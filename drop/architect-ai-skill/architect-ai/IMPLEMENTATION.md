# Architect AI - Implementation Reference

## Python Rules Engine Implementation

```python
"""
architect_ai/rules_engine.py
Core Python rules engine for Tier 0 query handling
"""

import re
import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Tier(Enum):
    PYTHON = 0
    GROQ = 1
    ANTHROPIC = 2

@dataclass
class QueryResult:
    tier: Tier
    response: Any
    cost: float
    latency_ms: float
    skill_used: str
    confidence: float

# ============================================================
# LOOKUP TABLES
# ============================================================

PRODUCTION_RATES = {
    # Membrane systems (SF/day, 5-man crew)
    "tpo_adhered": 4500,
    "tpo_mechanical": 5500,
    "epdm_adhered": 4000,
    "epdm_ballasted": 8000,
    "pvc_adhered": 4000,
    "pvc_mechanical": 5000,
    "mod_bit_2ply": 3500,
    "mod_bit_3ply": 2500,
    "bur_4ply": 2200,
    
    # Tear-off (SF/day, 5-man crew)
    "tearoff_single": 5500,
    "tearoff_multi": 4000,
    "tearoff_bur": 3000,
    
    # Insulation (SF/day, 5-man crew)
    "insulation_adhered": 7000,
    "insulation_mechanical": 8000,
    
    # Flashing (LF/day, 5-man crew)
    "base_flashing": 175,
    "edge_metal": 250,
    "coping": 175,
    "counter_flashing": 200,
    
    # Details (each/day, 5-man crew)
    "curb_small": 8,
    "curb_large": 3,
    "penetration_small": 15,
    "penetration_large": 6,
    "drain": 8,
}

MATERIAL_COVERAGE = {
    # Membrane rolls
    "tpo_10ft": 1000,  # SF per roll
    "tpo_6ft": 600,
    "epdm_10ft": 1000,
    "epdm_20ft": 2000,
    "pvc_10ft": 1000,
    
    # Insulation boards
    "polyiso_4x8": 32,  # SF per board
    "polyiso_4x4": 16,
    "eps_4x8": 32,
    "xps_4x8": 32,
    
    # Adhesives
    "adhesive_ribbon": 100,  # SF per gallon
    "adhesive_full": 60,
    "bonding_adhesive": 80,
    
    # Fasteners
    "fastener_field": 1,  # per SF at 12" OC
    "fastener_perimeter": 2,  # per LF at 6" OC
    "fastener_corner": 4,  # per LF at 6" OC both ways
}

WASTE_FACTORS = {
    "membrane": 0.10,
    "insulation": 0.05,
    "flashing": 0.10,
    "fasteners": 0.05,
    "adhesive": 0.10,
    "sheet_metal": 0.15,
}

SPEC_SECTIONS = {
    "07 10 00": "Dampproofing and Waterproofing",
    "07 20 00": "Thermal Protection",
    "07 27 00": "Air Barriers",
    "07 50 00": "Membrane Roofing",
    "07 52 00": "Modified Bituminous Membrane Roofing",
    "07 54 00": "Thermoplastic Membrane Roofing",
    "07 55 00": "EPDM Membrane Roofing",
    "07 60 00": "Flashing and Sheet Metal",
    "07 62 00": "Sheet Metal Flashing and Trim",
    "07 70 00": "Roof Specialties",
    "07 72 00": "Roof Accessories",
    "07 90 00": "Joint Protection",
    "07 92 00": "Joint Sealants",
}

# ============================================================
# PATTERN MATCHERS
# ============================================================

TIER_0_PATTERNS = [
    # Direct lookups
    (r"production rate.*(tpo|epdm|pvc|mod.?bit|bur)", "lookup_production_rate"),
    (r"(coverage|how much).*(roll|board|gallon)", "lookup_coverage"),
    (r"waste factor", "lookup_waste"),
    (r"spec section.*(07|roofing|flashing|membrane)", "lookup_spec"),
    
    # Calculations
    (r"(calculate|how many).*(rolls?|boards?|gallons?)", "calculate_materials"),
    (r"(calculate|how many).*(hours?|days?|labor)", "calculate_labor"),
    (r"(man.?hours?|labor hours?) for", "calculate_labor"),
    
    # Status checks
    (r"status of.*(project|job)", "lookup_status"),
    (r"what('s| is) (the )?(current )?status", "lookup_status"),
]

TIER_1_PATTERNS = [
    # Document generation
    (r"(draft|write|create|generate).*(rfi|letter|email|memo)", "generate_document"),
    (r"(draft|write|create|generate).*(submittal|schedule)", "generate_document"),
    
    # Summarization
    (r"summarize|summary of", "summarize"),
    
    # Explanation
    (r"explain|what (is|are)|how (do|does)", "explain"),
    
    # Analysis
    (r"(analyze|compare|review)", "analyze"),
    (r"why (is|did|was)", "analyze"),
]

# ============================================================
# CORE FUNCTIONS
# ============================================================

def route_query(query: str, context: Dict = None) -> Tuple[Tier, str, Dict]:
    """
    Route incoming query to appropriate tier
    Returns: (tier, handler_function, extracted_params)
    """
    query_lower = query.lower().strip()
    context = context or {}
    
    # Check Tier 0 patterns first
    for pattern, handler in TIER_0_PATTERNS:
        match = re.search(pattern, query_lower)
        if match:
            params = extract_params(query_lower, handler)
            return (Tier.PYTHON, handler, params)
    
    # Check Tier 1 patterns
    for pattern, handler in TIER_1_PATTERNS:
        match = re.search(pattern, query_lower)
        if match:
            params = {"query": query, "context": context}
            return (Tier.GROQ, handler, params)
    
    # Default to Tier 1
    return (Tier.GROQ, "general", {"query": query, "context": context})


def extract_params(query: str, handler: str) -> Dict:
    """Extract relevant parameters from query for handler"""
    params = {}
    
    if handler == "lookup_production_rate":
        systems = re.findall(r"(tpo|epdm|pvc|mod.?bit|bur)", query)
        params["systems"] = systems
        
    elif handler == "calculate_materials":
        # Extract area
        area_match = re.search(r"(\d+[,\d]*)\s*(sf|square feet)", query)
        if area_match:
            params["area_sf"] = float(area_match.group(1).replace(",", ""))
        
        # Extract material type
        mat_match = re.search(r"(membrane|insulation|tpo|epdm|polyiso)", query)
        if mat_match:
            params["material"] = mat_match.group(1)
            
    elif handler == "calculate_labor":
        # Extract quantity
        qty_match = re.search(r"(\d+[,\d]*)\s*(sf|lf|square feet|linear feet)", query)
        if qty_match:
            params["quantity"] = float(qty_match.group(1).replace(",", ""))
            params["unit"] = qty_match.group(2)
        
        # Extract task
        task_match = re.search(r"(tear.?off|membrane|insulation|flashing)", query)
        if task_match:
            params["task"] = task_match.group(1)
    
    return params


def handle_tier_0(handler: str, params: Dict) -> QueryResult:
    """Execute Tier 0 (Python) handler"""
    
    handlers = {
        "lookup_production_rate": _lookup_production_rate,
        "lookup_coverage": _lookup_coverage,
        "lookup_waste": _lookup_waste,
        "lookup_spec": _lookup_spec,
        "calculate_materials": _calculate_materials,
        "calculate_labor": _calculate_labor,
        "lookup_status": _lookup_status,
    }
    
    if handler not in handlers:
        return QueryResult(
            tier=Tier.GROQ,
            response=None,
            cost=0,
            latency_ms=0,
            skill_used="architect",
            confidence=0
        )
    
    import time
    start = time.time()
    result = handlers[handler](params)
    latency = (time.time() - start) * 1000
    
    return QueryResult(
        tier=Tier.PYTHON,
        response=result,
        cost=0,
        latency_ms=latency,
        skill_used="architect",
        confidence=1.0
    )


# ============================================================
# TIER 0 HANDLERS
# ============================================================

def _lookup_production_rate(params: Dict) -> Dict:
    """Look up production rates"""
    systems = params.get("systems", [])
    results = {}
    
    for system in systems:
        # Normalize system name
        normalized = system.lower().replace(" ", "_").replace("-", "_")
        
        # Find matching rates
        for key, rate in PRODUCTION_RATES.items():
            if normalized in key or key in normalized:
                results[key] = {"rate": rate, "unit": "SF/day", "crew_size": 5}
    
    if not results:
        # Return all rates if no specific match
        results = {k: {"rate": v, "unit": "SF/day" if v > 100 else "each/day", "crew_size": 5} 
                   for k, v in PRODUCTION_RATES.items()}
    
    return {"production_rates": results}


def _lookup_coverage(params: Dict) -> Dict:
    """Look up material coverage rates"""
    return {"material_coverage": MATERIAL_COVERAGE}


def _lookup_waste(params: Dict) -> Dict:
    """Look up waste factors"""
    return {"waste_factors": WASTE_FACTORS}


def _lookup_spec(params: Dict) -> Dict:
    """Look up spec section information"""
    return {"spec_sections": SPEC_SECTIONS}


def _calculate_materials(params: Dict) -> Dict:
    """Calculate material quantities"""
    area = params.get("area_sf", 0)
    material = params.get("material", "membrane")
    
    if area <= 0:
        return {"error": "Invalid area", "need": "area_sf"}
    
    # Determine coverage and waste
    if "membrane" in material or "tpo" in material or "epdm" in material:
        coverage = MATERIAL_COVERAGE.get("tpo_10ft", 1000)
        waste = WASTE_FACTORS.get("membrane", 0.10)
        unit = "rolls"
    elif "insulation" in material or "polyiso" in material:
        coverage = MATERIAL_COVERAGE.get("polyiso_4x8", 32)
        waste = WASTE_FACTORS.get("insulation", 0.05)
        unit = "boards"
    else:
        coverage = 1000
        waste = 0.10
        unit = "units"
    
    net_area = area * (1 + waste)
    quantity = math.ceil(net_area / coverage)
    
    return {
        "calculation": {
            "gross_area_sf": area,
            "waste_factor": waste,
            "net_area_sf": net_area,
            "coverage_per_unit": coverage,
            "quantity_needed": quantity,
            "unit": unit
        }
    }


def _calculate_labor(params: Dict) -> Dict:
    """Calculate labor hours/days"""
    quantity = params.get("quantity", 0)
    task = params.get("task", "").lower().replace("-", "_").replace(" ", "_")
    unit = params.get("unit", "sf").lower()
    
    if quantity <= 0:
        return {"error": "Invalid quantity", "need": "quantity"}
    
    # Find matching production rate
    rate = None
    rate_key = None
    
    for key, value in PRODUCTION_RATES.items():
        if task in key or key in task:
            rate = value
            rate_key = key
            break
    
    if not rate:
        return {"error": f"Unknown task: {task}", "available_tasks": list(PRODUCTION_RATES.keys())}
    
    # Calculate
    crew_size = 5
    days = quantity / rate
    man_hours = days * 8 * crew_size
    
    return {
        "labor_calculation": {
            "task": rate_key,
            "quantity": quantity,
            "production_rate": rate,
            "days": round(days, 2),
            "man_hours": round(man_hours, 1),
            "crew_size": crew_size
        }
    }


def _lookup_status(params: Dict) -> Dict:
    """Look up project status - requires database integration"""
    return {
        "status": "requires_database",
        "note": "Connect to project database for real-time status"
    }


# ============================================================
# GROQ INTEGRATION
# ============================================================

GROQ_CONFIG = {
    "model": "llama-3.3-70b-versatile",
    "fallback_model": "mixtral-8x7b-32768", 
    "temperature": 0.3,
    "max_tokens": 2000,
}

async def handle_tier_1(handler: str, params: Dict, skills_context: Dict) -> QueryResult:
    """
    Execute Tier 1 (Groq) handler
    Requires: groq library installed
    """
    import groq
    import time
    
    client = groq.Groq()
    
    # Build system prompt based on handler
    system_prompt = build_system_prompt(handler, skills_context)
    
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=GROQ_CONFIG["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": params["query"]}
            ],
            temperature=GROQ_CONFIG["temperature"],
            max_tokens=GROQ_CONFIG["max_tokens"]
        )
        
        latency = (time.time() - start) * 1000
        content = response.choices[0].message.content
        
        # Check if escalation needed
        if should_escalate(content):
            return await handle_tier_2(params, skills_context, "groq_uncertainty")
        
        return QueryResult(
            tier=Tier.GROQ,
            response=content,
            cost=0.0001,  # Approximate Groq cost
            latency_ms=latency,
            skill_used=handler,
            confidence=0.85
        )
        
    except Exception as e:
        # Fallback to Tier 2 on Groq failure
        return await handle_tier_2(params, skills_context, f"groq_error: {e}")


def build_system_prompt(handler: str, skills_context: Dict) -> str:
    """Build appropriate system prompt for handler"""
    
    base_prompt = """You are a roofing company AI assistant. Be direct and practical.
    Use construction terminology correctly. Reference spec sections when relevant."""
    
    handler_prompts = {
        "generate_document": """Generate professional construction documents.
        Use industry-standard formats. Be clear and specific.""",
        
        "summarize": """Summarize the provided content concisely.
        Focus on key points relevant to roofing/construction.""",
        
        "explain": """Explain roofing concepts clearly.
        Use examples when helpful. Reference standards/codes when applicable.""",
        
        "analyze": """Analyze the situation using roofing industry knowledge.
        Consider practical field implications.""",
        
        "general": """Help with roofing company operations.
        Route to specific capabilities when appropriate."""
    }
    
    return base_prompt + "\n\n" + handler_prompts.get(handler, handler_prompts["general"])


def should_escalate(response: str) -> bool:
    """Check if Groq response indicates need for escalation"""
    
    escalation_signals = [
        "i'm not sure",
        "i don't have enough information",
        "this is outside my expertise",
        "you should consult",
        "i cannot determine",
        "this requires human judgment",
        "i'm uncertain",
        "beyond my capabilities"
    ]
    
    response_lower = response.lower()
    return any(signal in response_lower for signal in escalation_signals)


# ============================================================
# TIER 2 ESCALATION
# ============================================================

async def handle_tier_2(params: Dict, skills_context: Dict, reason: str) -> QueryResult:
    """
    Execute Tier 2 (Anthropic/OpenAI) handler
    Used for complex reasoning, novel situations, error recovery
    """
    import anthropic
    import time
    
    client = anthropic.Anthropic()
    
    system_prompt = """You are an expert roofing industry AI assistant handling 
    escalated queries that require advanced reasoning. You have access to comprehensive 
    roofing knowledge including specifications, codes, best practices, and business operations.
    
    This query was escalated because: """ + reason
    
    start = time.time()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": params["query"]}]
        )
        
        latency = (time.time() - start) * 1000
        content = response.content[0].text
        
        return QueryResult(
            tier=Tier.ANTHROPIC,
            response=content,
            cost=0.01,  # Approximate Anthropic cost
            latency_ms=latency,
            skill_used="tier2_anthropic",
            confidence=0.95
        )
        
    except Exception as e:
        return QueryResult(
            tier=Tier.ANTHROPIC,
            response=f"Error in Tier 2: {e}",
            cost=0,
            latency_ms=0,
            skill_used="error",
            confidence=0
        )


# ============================================================
# MAIN QUERY PROCESSOR
# ============================================================

async def process_query(query: str, context: Dict = None) -> QueryResult:
    """
    Main entry point for processing queries through tiered architecture
    """
    context = context or {}
    
    # Route the query
    tier, handler, params = route_query(query, context)
    
    # Execute at appropriate tier
    if tier == Tier.PYTHON:
        return handle_tier_0(handler, params)
    
    elif tier == Tier.GROQ:
        return await handle_tier_1(handler, params, context)
    
    else:
        return await handle_tier_2(params, context, "direct_escalation")


# ============================================================
# METRICS TRACKING
# ============================================================

class MetricsCollector:
    """Track query metrics for optimization"""
    
    def __init__(self):
        self.queries = []
        self.tier_counts = {Tier.PYTHON: 0, Tier.GROQ: 0, Tier.ANTHROPIC: 0}
        self.total_cost = 0
        self.total_latency = 0
    
    def record(self, result: QueryResult):
        self.queries.append({
            "tier": result.tier,
            "cost": result.cost,
            "latency": result.latency_ms,
            "skill": result.skill_used,
            "confidence": result.confidence
        })
        self.tier_counts[result.tier] += 1
        self.total_cost += result.cost
        self.total_latency += result.latency_ms
    
    def summary(self) -> Dict:
        total = len(self.queries)
        if total == 0:
            return {"error": "No queries recorded"}
        
        return {
            "total_queries": total,
            "tier_distribution": {
                "tier_0_python": f"{self.tier_counts[Tier.PYTHON]/total*100:.1f}%",
                "tier_1_groq": f"{self.tier_counts[Tier.GROQ]/total*100:.1f}%",
                "tier_2_anthropic": f"{self.tier_counts[Tier.ANTHROPIC]/total*100:.1f}%"
            },
            "total_cost": f"${self.total_cost:.4f}",
            "avg_latency_ms": f"{self.total_latency/total:.1f}",
            "cost_if_all_tier2": f"${total * 0.01:.2f}",
            "savings": f"${(total * 0.01) - self.total_cost:.2f}"
        }
```

## Usage Example

```python
# Initialize
metrics = MetricsCollector()

# Process queries
result1 = await process_query("What's the production rate for TPO?")
metrics.record(result1)
# Result: Tier 0, instant, $0

result2 = await process_query("Calculate materials for 15,000 SF TPO roof")
metrics.record(result2)
# Result: Tier 0, instant, $0

result3 = await process_query("Draft an RFI about the drain location conflict")
metrics.record(result3)
# Result: Tier 1 (Groq), ~500ms, $0.0001

result4 = await process_query("Should we take on this unusual project with asbestos?")
metrics.record(result4)
# Result: Tier 2 (Anthropic), ~2s, $0.01

# View metrics
print(metrics.summary())
```

## Integration Notes

**For Claude Code:**
- Import this module in your main application
- Connect `_lookup_status` to your project database
- Configure API keys for Groq and Anthropic
- Extend TIER_0_PATTERNS as you identify more automatable queries

**For Dashboard:**
- `process_query()` is your main API endpoint
- `metrics.summary()` feeds the Architect AI dashboard
- Real-time tier distribution shows cost optimization
