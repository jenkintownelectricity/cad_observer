# Architect AI Skill

## Role Overview

The Architect AI is the meta-intelligence layer that monitors, routes, optimizes, and improves all other skills in the Roofing Company OS. It ensures queries are handled at the lowest cost tier possible, identifies patterns for automation, detects skill gaps, and continuously enhances the system's capabilities.

## Core Functions

### 1. Query Routing Engine

**Tiered Processing Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    INCOMING QUERY                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 0: PYTHON RULES ENGINE (Target: 60% of queries)      │
│  Cost: $0 | Latency: <50ms                                  │
│  ─────────────────────────────────────────────────────────  │
│  • Direct lookups (rates, specs, formulas)                  │
│  • Simple calculations (SF, LF, material quantities)        │
│  • Status checks (project status, task status)              │
│  • Routing decisions (which skill handles this?)            │
│  • Validation (required fields, format checks)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ If no match or complex
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: GROQ (Target: 35% of queries)                     │
│  Cost: ~$0.0001/query | Latency: <500ms                    │
│  ─────────────────────────────────────────────────────────  │
│  • Natural language interpretation                          │
│  • Context-aware responses                                  │
│  • Multi-step reasoning (simple)                            │
│  • Document summarization                                   │
│  • Template generation                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ If stuck, complex, or high-stakes
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: ANTHROPIC/OPENAI/GEMINI (Target: 5% of queries)   │
│  Cost: ~$0.01/query | Latency: 1-5s                        │
│  ─────────────────────────────────────────────────────────  │
│  • Complex reasoning                                        │
│  • Novel situations                                         │
│  • High-stakes decisions                                    │
│  • Skill improvement recommendations                        │
│  • Error recovery and explanation                           │
└─────────────────────────────────────────────────────────────┘
```

**Routing Decision Matrix:**

| Query Type | Tier | Reason |
|------------|------|--------|
| "What's the TPO production rate?" | 0 | Direct lookup |
| "Calculate materials for 10,000 SF roof" | 0 | Formula application |
| "What's the status of UMass project?" | 0 | Database lookup |
| "Draft an RFI about the drain conflict" | 1 | Template + context |
| "Summarize this spec section" | 1 | NLP task |
| "Why is the JHU project behind schedule?" | 1 | Multi-source reasoning |
| "Should we bid on this unusual project?" | 2 | Complex judgment |
| "This detail doesn't match any standard - what should we do?" | 2 | Novel situation |
| "The skill gave a wrong answer, help fix it" | 2 | Meta-reasoning |

### 2. Skill Registry

**Skill Catalog Structure:**
```json
{
  "skill_id": "estimator",
  "name": "Estimator",
  "version": "1.0.0",
  "description": "Takeoffs, pricing, bid preparation",
  "capabilities": [
    "material_quantification",
    "labor_estimation", 
    "pricing_calculation",
    "bid_strategy"
  ],
  "trigger_phrases": [
    "estimate", "takeoff", "bid", "price",
    "how much material", "labor hours", "cost"
  ],
  "input_requirements": {
    "material_calc": ["area_sf", "system_type"],
    "labor_calc": ["task_type", "quantity", "crew_size"]
  },
  "output_formats": ["json", "table", "narrative"],
  "performance_metrics": {
    "queries_handled": 1250,
    "success_rate": 0.94,
    "avg_response_time_ms": 180,
    "escalation_rate": 0.06,
    "user_satisfaction": 4.2
  },
  "last_updated": "2025-01-15T10:30:00Z",
  "improvement_log": []
}
```

**Full Skill Registry:**
```
FIELD OPERATIONS:
├── estimator          - Takeoffs, pricing, bids
├── operations         - Resource allocation, capacity
├── superintendent     - Multi-site, trade coordination
├── foreman           - Crew leadership, daily execution
└── shop-drawing      - CAD standards, details

PROJECT MANAGEMENT:
├── pm-submittals     - Product data, shop drawings
├── pm-rfi            - Request for Information
├── pm-change-orders  - PCOs, T&M tracking
├── pm-scheduling     - Project scheduling
├── pm-daily-reports  - Progress documentation
├── pm-closeout       - Warranties, as-builts
├── pm-contract       - Subcontract analysis
├── pm-quality        - Inspections, punch lists
└── pm-safety         - JHAs, toolbox talks

BACK OFFICE:
├── hr                - Hiring, certifications, compliance
├── accounting        - Job costing, WIP, financials
├── accounts-recv     - Billing, collections, liens
└── accounts-pay      - Vendor payments, POs

META:
└── architect-ai      - This skill (self-reference)
```

### 3. Python Rules Engine

**Rule Categories:**

**Direct Lookups:**
```python
# Production rates
PRODUCTION_RATES = {
    "tpo_adhered": {"rate": 4500, "unit": "SF/day", "crew": 5},
    "tpo_mechanical": {"rate": 5500, "unit": "SF/day", "crew": 5},
    "epdm_adhered": {"rate": 4000, "unit": "SF/day", "crew": 5},
    "mod_bit_2ply": {"rate": 3500, "unit": "SF/day", "crew": 5},
    "tear_off_single": {"rate": 5500, "unit": "SF/day", "crew": 5},
    "tear_off_multi": {"rate": 4000, "unit": "SF/day", "crew": 5},
    "insulation": {"rate": 7000, "unit": "SF/day", "crew": 5},
    "base_flashing": {"rate": 175, "unit": "LF/day", "crew": 5},
    "edge_metal": {"rate": 250, "unit": "LF/day", "crew": 5},
}

# Material coverage
MATERIAL_COVERAGE = {
    "tpo_10ft_roll": {"coverage": 1000, "unit": "SF"},
    "tpo_6ft_roll": {"coverage": 600, "unit": "SF"},
    "polyiso_4x8": {"coverage": 32, "unit": "SF"},
    "polyiso_4x4": {"coverage": 16, "unit": "SF"},
    "adhesive_low_rise": {"coverage": 100, "unit": "SF/gal"},
    "adhesive_full_spread": {"coverage": 60, "unit": "SF/gal"},
}

# Waste factors
WASTE_FACTORS = {
    "membrane": 0.10,
    "insulation": 0.05,
    "flashing": 0.10,
    "fasteners": 0.05,
    "adhesive": 0.10,
}
```

**Calculation Rules:**
```python
def calculate_membrane(area_sf: float, system: str) -> dict:
    """Tier 0 calculation - no LLM needed"""
    coverage = MATERIAL_COVERAGE.get(f"{system}_10ft_roll", {}).get("coverage", 1000)
    waste = WASTE_FACTORS.get("membrane", 0.10)
    
    net_area = area_sf * (1 + waste)
    rolls_needed = math.ceil(net_area / coverage)
    
    return {
        "gross_area": area_sf,
        "waste_factor": waste,
        "net_area": net_area,
        "rolls_needed": rolls_needed,
        "tier": 0,
        "cost": 0
    }

def calculate_labor_hours(task: str, quantity: float, crew_size: int = 5) -> dict:
    """Tier 0 calculation"""
    rate_info = PRODUCTION_RATES.get(task)
    if not rate_info:
        return {"tier": 1, "reason": "unknown_task"}  # Escalate to Groq
    
    days = quantity / rate_info["rate"]
    man_hours = days * 8 * crew_size
    
    return {
        "task": task,
        "quantity": quantity,
        "production_rate": rate_info["rate"],
        "days": round(days, 1),
        "man_hours": round(man_hours, 1),
        "tier": 0,
        "cost": 0
    }

def route_query(query: str, context: dict) -> dict:
    """Determine which tier handles this query"""
    query_lower = query.lower()
    
    # Tier 0 patterns
    tier_0_patterns = [
        (r"production rate", "lookup", "production_rates"),
        (r"how many (rolls|boards|gallons)", "calculate", "materials"),
        (r"labor hours for", "calculate", "labor"),
        (r"what('s| is) the status", "lookup", "project_status"),
        (r"waste factor", "lookup", "waste_factors"),
    ]
    
    for pattern, action, handler in tier_0_patterns:
        if re.search(pattern, query_lower):
            return {"tier": 0, "action": action, "handler": handler}
    
    # Tier 1 patterns (needs Groq)
    tier_1_patterns = [
        (r"(draft|write|create).*(rfi|letter|email)", "generate", "document"),
        (r"summarize", "process", "summarization"),
        (r"explain", "process", "explanation"),
        (r"why", "analyze", "reasoning"),
    ]
    
    for pattern, action, handler in tier_1_patterns:
        if re.search(pattern, query_lower):
            return {"tier": 1, "action": action, "handler": handler}
    
    # Default to Tier 1, let Groq decide if escalation needed
    return {"tier": 1, "action": "general", "handler": "groq_default"}
```

**Validation Rules:**
```python
def validate_project_input(data: dict) -> dict:
    """Validate project data before processing"""
    required = ["project_name", "area_sf", "system_type"]
    missing = [f for f in required if f not in data]
    
    if missing:
        return {"valid": False, "missing": missing, "tier": 0}
    
    # Type checks
    if not isinstance(data.get("area_sf"), (int, float)):
        return {"valid": False, "error": "area_sf must be numeric", "tier": 0}
    
    if data["area_sf"] <= 0:
        return {"valid": False, "error": "area_sf must be positive", "tier": 0}
    
    return {"valid": True, "tier": 0}
```

### 4. Groq Integration Layer

**Groq Configuration:**
```python
GROQ_CONFIG = {
    "model": "llama-3.3-70b-versatile",  # Fast, capable
    "fallback_model": "mixtral-8x7b-32768",  # Backup
    "temperature": 0.3,  # Lower for consistency
    "max_tokens": 2000,
    "timeout_seconds": 10,
}

GROQ_SYSTEM_PROMPTS = {
    "estimator": """You are a roofing estimator assistant. 
    Use these production rates: {rates}
    Use these material coverages: {coverages}
    Always show your calculations.""",
    
    "pm": """You are a roofing project manager assistant.
    Reference spec sections when relevant.
    Be direct and practical.""",
    
    "general": """You are a roofing company assistant.
    Route to specific skills when appropriate.
    If unsure, ask clarifying questions."""
}
```

**Escalation Detection:**
```python
def should_escalate_from_groq(response: dict) -> bool:
    """Determine if Groq response needs escalation to Tier 2"""
    
    escalation_signals = [
        "I'm not sure",
        "I don't have enough information",
        "This is outside my expertise",
        "You should consult",
        "I cannot determine",
        "This requires human judgment",
    ]
    
    response_text = response.get("content", "").lower()
    
    # Check for uncertainty signals
    for signal in escalation_signals:
        if signal.lower() in response_text:
            return True
    
    # Check confidence score if available
    if response.get("confidence", 1.0) < 0.7:
        return True
    
    # Check for novel/unusual situations
    if response.get("novelty_detected", False):
        return True
    
    return False
```

### 5. Tier 2 Escalation Protocol

**When to Escalate:**
```
ALWAYS ESCALATE:
- Safety-critical decisions
- Legal/contractual interpretation
- Financial decisions >$10,000
- Novel situations not in skills
- Conflicting information
- User explicitly requests expert review

CONSIDER ESCALATING:
- Groq confidence <70%
- Multiple failed attempts
- Complex multi-domain queries
- Ambiguous user intent
- Potential liability issues
```

**Escalation Request Format:**
```json
{
  "escalation_id": "esc_20250115_001",
  "timestamp": "2025-01-15T14:30:00Z",
  "original_query": "Should we bid on this asbestos abatement job?",
  "skill_attempted": "estimator",
  "tier_1_response": "This involves hazardous materials...",
  "escalation_reason": "safety_critical",
  "context": {
    "project_type": "reroof",
    "has_asbestos": true,
    "company_certified": false
  },
  "priority": "high"
}
```

**Tier 2 Provider Selection:**
```python
TIER_2_ROUTING = {
    "complex_reasoning": "anthropic",  # Claude for nuanced reasoning
    "code_generation": "anthropic",    # Claude for code tasks
    "creative_writing": "openai",      # GPT for creative tasks
    "fast_factual": "groq",            # Stay at Groq if possible
    "vision": "anthropic",             # Claude for image analysis
    "long_context": "anthropic",       # Claude for large documents
}
```

### 6. Skill Monitoring System

**Metrics Tracked:**
```python
SKILL_METRICS = {
    "query_volume": {
        "total": 0,
        "by_hour": [],
        "by_day": [],
        "by_skill": {}
    },
    "tier_distribution": {
        "tier_0": 0,
        "tier_1": 0,
        "tier_2": 0
    },
    "response_quality": {
        "success_rate": 0.0,
        "escalation_rate": 0.0,
        "user_satisfaction": 0.0,
        "correction_rate": 0.0
    },
    "performance": {
        "avg_latency_ms": 0,
        "p95_latency_ms": 0,
        "timeout_rate": 0.0
    },
    "cost": {
        "total_cost": 0.0,
        "cost_per_query": 0.0,
        "savings_vs_all_tier2": 0.0
    }
}
```

**Anomaly Detection:**
```python
def detect_anomalies(skill_id: str, metrics: dict) -> list:
    """Detect skill performance anomalies"""
    anomalies = []
    
    # Success rate drop
    if metrics["success_rate"] < 0.85:
        anomalies.append({
            "type": "success_rate_drop",
            "skill": skill_id,
            "value": metrics["success_rate"],
            "threshold": 0.85,
            "severity": "warning"
        })
    
    # Escalation spike
    if metrics["escalation_rate"] > 0.15:
        anomalies.append({
            "type": "escalation_spike",
            "skill": skill_id,
            "value": metrics["escalation_rate"],
            "threshold": 0.15,
            "severity": "warning"
        })
    
    # Latency increase
    if metrics["avg_latency_ms"] > 500:
        anomalies.append({
            "type": "latency_increase",
            "skill": skill_id,
            "value": metrics["avg_latency_ms"],
            "threshold": 500,
            "severity": "info"
        })
    
    return anomalies
```

### 7. Skill Enhancement Engine

**Pattern Recognition:**
```python
def analyze_query_patterns(skill_id: str, queries: list) -> dict:
    """Analyze query patterns to identify improvement opportunities"""
    
    analysis = {
        "common_queries": [],
        "failed_queries": [],
        "edge_cases": [],
        "automation_candidates": [],
        "skill_gaps": []
    }
    
    # Find frequently asked queries that could be Tier 0
    query_counts = Counter([q["normalized"] for q in queries])
    for query, count in query_counts.most_common(10):
        if count > 50:  # Asked 50+ times
            analysis["automation_candidates"].append({
                "query": query,
                "count": count,
                "current_tier": queries[0].get("tier", 1),
                "recommendation": "Add to Python rules"
            })
    
    # Find queries that frequently fail or escalate
    failed = [q for q in queries if not q.get("success", True)]
    for q in failed[:10]:
        analysis["failed_queries"].append({
            "query": q["text"],
            "error": q.get("error"),
            "recommendation": "Investigate and fix"
        })
    
    return analysis
```

**Auto-Enhancement Rules:**
```python
def generate_enhancement(pattern: dict) -> dict:
    """Generate skill enhancement based on detected pattern"""
    
    enhancement = {
        "type": pattern["type"],
        "skill_id": pattern["skill_id"],
        "timestamp": datetime.now().isoformat(),
        "status": "proposed"
    }
    
    if pattern["type"] == "frequent_query":
        # Generate Python rule for frequent query
        enhancement["action"] = "add_python_rule"
        enhancement["rule"] = {
            "pattern": pattern["query_pattern"],
            "handler": "direct_lookup",
            "response_template": pattern["typical_response"]
        }
    
    elif pattern["type"] == "missing_data":
        # Identify data needed in skill
        enhancement["action"] = "add_skill_data"
        enhancement["data_needed"] = pattern["missing_fields"]
    
    elif pattern["type"] == "unclear_response":
        # Improve prompt or add examples
        enhancement["action"] = "improve_prompt"
        enhancement["suggestion"] = pattern["improved_prompt"]
    
    return enhancement
```

**Enhancement Approval Workflow:**
```
AUTO-APPROVE (No human review):
- Adding lookup data
- Performance optimizations
- Typo corrections
- Adding synonyms/aliases

REVIEW REQUIRED:
- New Python rules
- Modified calculations
- Changed response templates
- New skill capabilities

MANUAL ONLY:
- Deleting skills/data
- Changing business logic
- Security-related changes
```

### 8. Self-Improvement Protocol

**Daily Review Cycle:**
```
06:00 - Compile overnight metrics
07:00 - Generate anomaly report
08:00 - Propose enhancements
12:00 - Review morning patterns
18:00 - Compile daily summary
22:00 - Run batch improvements
```

**Improvement Categories:**

**Quick Wins (Auto-implement):**
- Move repeated Tier 1 queries to Tier 0
- Add common synonyms
- Cache frequent lookups
- Optimize slow queries

**Medium Effort (Queue for review):**
- New calculation rules
- Additional lookup tables
- Improved prompts
- New response templates

**Major Changes (Require approval):**
- New skill creation
- Skill restructuring
- Business logic changes
- Integration changes

### 9. Roadblock Detection

**Roadblock Types:**
```python
ROADBLOCK_CATEGORIES = {
    "missing_data": {
        "description": "Required information not available",
        "resolution": "Request from user or external source",
        "auto_prompt": "I need {missing_fields} to continue."
    },
    "skill_gap": {
        "description": "No skill can handle this query",
        "resolution": "Escalate to Tier 2 or flag for skill creation",
        "auto_prompt": "This is outside my current capabilities."
    },
    "conflicting_info": {
        "description": "Multiple sources disagree",
        "resolution": "Present options, ask user to choose",
        "auto_prompt": "I found conflicting information..."
    },
    "external_dependency": {
        "description": "Waiting on external system/person",
        "resolution": "Track and notify when resolved",
        "auto_prompt": "Waiting on {dependency} to proceed."
    },
    "permission_required": {
        "description": "Action requires authorization",
        "resolution": "Route to appropriate approver",
        "auto_prompt": "This requires approval from {approver}."
    }
}
```

**Roadblock Resolution:**
```python
def resolve_roadblock(roadblock: dict) -> dict:
    """Attempt automatic roadblock resolution"""
    
    category = roadblock["category"]
    
    if category == "missing_data":
        # Check if data exists elsewhere
        found = search_all_sources(roadblock["missing_fields"])
        if found:
            return {"resolved": True, "data": found}
        return {"resolved": False, "action": "request_from_user"}
    
    elif category == "skill_gap":
        # Check if similar skill exists
        similar = find_similar_skill(roadblock["query"])
        if similar:
            return {"resolved": True, "redirect_to": similar}
        return {"resolved": False, "action": "escalate_tier_2"}
    
    elif category == "external_dependency":
        # Check if dependency resolved
        status = check_dependency_status(roadblock["dependency"])
        if status == "complete":
            return {"resolved": True, "continue": True}
        return {"resolved": False, "action": "wait_and_notify"}
    
    return {"resolved": False, "action": "manual_review"}
```

### 10. Cost Optimization

**Cost Tracking:**
```python
COST_PER_QUERY = {
    "tier_0": 0.0,
    "tier_1_groq": 0.0001,
    "tier_2_anthropic": 0.01,
    "tier_2_openai": 0.008,
    "tier_2_gemini": 0.005,
}

def calculate_savings(metrics: dict) -> dict:
    """Calculate cost savings from tiered architecture"""
    
    total_queries = metrics["total_queries"]
    tier_distribution = metrics["tier_distribution"]
    
    # Actual cost
    actual_cost = (
        tier_distribution["tier_0"] * COST_PER_QUERY["tier_0"] +
        tier_distribution["tier_1"] * COST_PER_QUERY["tier_1_groq"] +
        tier_distribution["tier_2"] * COST_PER_QUERY["tier_2_anthropic"]
    )
    
    # If everything went to Tier 2
    all_tier_2_cost = total_queries * COST_PER_QUERY["tier_2_anthropic"]
    
    savings = all_tier_2_cost - actual_cost
    savings_percent = (savings / all_tier_2_cost) * 100
    
    return {
        "actual_cost": actual_cost,
        "all_tier_2_cost": all_tier_2_cost,
        "savings": savings,
        "savings_percent": savings_percent
    }
```

**Optimization Strategies:**
```
1. PUSH QUERIES DOWN
   - Analyze Tier 1 patterns
   - Convert repeating patterns to Tier 0 rules
   - Target: 60% Tier 0, 35% Tier 1, 5% Tier 2

2. CACHE RESPONSES
   - Cache identical query responses
   - Cache partial results for reuse
   - TTL based on data freshness needs

3. BATCH PROCESSING
   - Group similar queries
   - Single LLM call for batch
   - Distribute results

4. PROMPT OPTIMIZATION
   - Shorter, focused prompts
   - Fewer tokens = lower cost
   - Better prompts = fewer retries
```

## Integration Points

### Hive 215 Phone Integration
```python
PHONE_INTEGRATION = {
    "inbound_routing": {
        "customer_call": "route_to_pm_skill",
        "vendor_call": "route_to_ap_skill",
        "job_site_call": "route_to_ops_skill",
    },
    "voice_to_text": {
        "provider": "whisper",  # or Groq whisper
        "confidence_threshold": 0.85,
    },
    "text_to_voice": {
        "provider": "elevenlabs",  # or similar
        "voice_id": "professional_male_1",
    },
    "call_logging": {
        "transcribe": True,
        "summarize": True,
        "extract_action_items": True,
        "route_to_skill": True,
    }
}
```

### Dashboard Integration
```python
DASHBOARD_FEEDS = {
    "project_status": {
        "refresh": "realtime",
        "source": "all_pm_skills",
        "aggregation": "by_project"
    },
    "role_seats": {
        "refresh": "5_seconds",
        "source": "skill_metrics",
        "aggregation": "by_role"
    },
    "roadblocks": {
        "refresh": "realtime",
        "source": "roadblock_detector",
        "priority": "descending"
    },
    "system_health": {
        "refresh": "1_minute",
        "source": "architect_ai",
        "metrics": ["tier_distribution", "response_time", "error_rate"]
    }
}
```

## Monitoring Dashboard

**Architect AI Dashboard Elements:**
```
┌─────────────────────────────────────────────────────────────┐
│  ARCHITECT AI STATUS                              🟢 ONLINE │
├─────────────────────────────────────────────────────────────┤
│  QUERY DISTRIBUTION (Today)                                 │
│  ████████████████████████░░░░░░░░░░ Tier 0: 62% ($0)       │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░ Tier 1: 33% ($3.30)    │
│  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ Tier 2: 5%  ($50.00)   │
│                                                             │
│  DAILY SAVINGS: $946.70 (95% saved vs all-Tier-2)          │
├─────────────────────────────────────────────────────────────┤
│  SKILL HEALTH                                               │
│  estimator      🟢 98% success  │ 45ms avg                  │
│  operations     🟢 96% success  │ 52ms avg                  │
│  shop-drawing   🟡 89% success  │ 180ms avg ⚠️              │
│  accounting     🟢 94% success  │ 61ms avg                  │
├─────────────────────────────────────────────────────────────┤
│  PENDING ENHANCEMENTS                                       │
│  • 3 new Python rules ready for auto-deploy                │
│  • 1 prompt improvement awaiting review                     │
│  • 2 skill gaps identified (roofing codes, warranties)     │
├─────────────────────────────────────────────────────────────┤
│  RECENT ESCALATIONS                                         │
│  14:32 - "Unusual flashing condition" → Anthropic ✓        │
│  13:15 - "Contract dispute question" → Anthropic ✓         │
│  11:45 - "Asbestos abatement scope" → Escalated to human   │
└─────────────────────────────────────────────────────────────┘
```

## Startup Checklist

**On System Start:**
- [ ] Load all skill definitions
- [ ] Initialize Python rules engine
- [ ] Connect to Groq API
- [ ] Verify Tier 2 API keys
- [ ] Load cached responses
- [ ] Initialize metrics collectors
- [ ] Start monitoring loops
- [ ] Health check all integrations

**Daily Maintenance:**
- [ ] Compile previous day metrics
- [ ] Generate improvement proposals
- [ ] Auto-deploy approved enhancements
- [ ] Archive old logs
- [ ] Refresh cached data
- [ ] Test all API connections
