"""
Architect AI - Python Rules Engine
Tier 0: Direct lookups and calculations (Target: 60% of queries)
Cost: $0 | Latency: <50ms
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
# LOOKUP TABLES - Roofing Industry Data
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
    "07 54 00": "Thermoplastic Membrane Roofing (TPO/PVC)",
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
    import time

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
        # Return common rates if no specific match
        common_rates = ["tpo_adhered", "epdm_adhered", "mod_bit_2ply", "tearoff_single"]
        results = {k: {"rate": PRODUCTION_RATES[k], "unit": "SF/day", "crew_size": 5}
                   for k in common_rates}

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
            "waste_factor": f"{waste*100:.0f}%",
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
        return {"error": f"Unknown task: {task}", "available_tasks": list(PRODUCTION_RATES.keys())[:10]}

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
# MAIN QUERY PROCESSOR
# ============================================================

def process_query(query: str, context: Dict = None) -> QueryResult:
    """
    Main entry point for processing queries through tiered architecture
    """
    context = context or {}

    # Route the query
    tier, handler, params = route_query(query, context)

    # Execute at appropriate tier
    if tier == Tier.PYTHON:
        return handle_tier_0(handler, params)

    # For Tier 1 and 2, return routing info (actual LLM calls handled elsewhere)
    return QueryResult(
        tier=tier,
        response={"route_to": tier.name, "handler": handler, "params": params},
        cost=0,
        latency_ms=0,
        skill_used=handler,
        confidence=0.5
    )


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


# Global metrics collector
metrics = MetricsCollector()
