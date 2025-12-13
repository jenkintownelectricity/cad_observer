"""
Form AI Genie - Intelligent Form Analysis and Suggestions
=========================================================

Uses Groq (Tier 2 AI) to analyze project data and proactively suggest:
- Change Orders based on RFI + Daily Log correlations
- Risk flags from safety forms
- Cost impact predictions

This runs as a periodic batch process or on-demand analysis.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from common.config import GROQ_API_KEY, GROQ_MODEL


async def get_groq_client():
    """Get Groq client - lazy import to avoid issues if not installed"""
    try:
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        return Groq(api_key=GROQ_API_KEY)
    except ImportError:
        raise ImportError("groq package not installed. Run: pip install groq")


# =============================================================================
# CHANGE ORDER SUGGESTION GENERATOR
# =============================================================================

async def generate_change_order_suggestions(
    project_id: UUID,
    recent_rfis: List[Dict[str, Any]],
    recent_daily_logs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes project data for patterns indicating a scope change requiring a Change Order.

    Args:
        project_id: UUID of the project to analyze
        recent_rfis: List of RFI submissions from last 14 days
        recent_daily_logs: List of daily log submissions from last 7 days

    Returns:
        Dict with 'suggestions' list containing potential Change Orders
    """
    client = await get_groq_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are the 'Form AI Genie' specializing in construction finance and risk management.
Your job is to analyze project data and proactively identify situations that require
a formal Change Order (CO) to protect the contractor's margin and schedule.

Analyze the provided RFIs and Daily Logs for strong correlations between:
1. Questions/Clarifications (RFI) that reveal scope gaps
2. Delays/Issues (Daily Log) that indicate unforeseen conditions
3. Cost or Schedule Impact estimates that exceed thresholds

If a correlation is found, generate a highly confident suggestion for a new Change Order.

Output MUST be a single JSON object with this structure:
{
    "suggestions": [
        {
            "confidence": "HIGH" | "MEDIUM",
            "title": "Brief CO title",
            "description": "Detailed description of the scope change",
            "estimated_cost": 0.00,
            "schedule_impact_days": 0,
            "supporting_rfis": ["RFI-001"],
            "supporting_logs": ["2024-01-15"],
            "justification": "Why this qualifies as a Change Order",
            "recommended_action": "Submit CO to GC within 48 hours"
        }
    ],
    "analysis_summary": "Brief summary of patterns found",
    "risk_level": "LOW" | "MEDIUM" | "HIGH"
}"""
            },
            {
                "role": "user",
                "content": f"""
Analyze data for Project ID: {project_id}

--- RECENT RFIs (Last 14 days) ---
{json.dumps(recent_rfis, indent=2, default=str)}

--- RECENT DAILY LOG ISSUES (Last 7 days) ---
{json.dumps(recent_daily_logs, indent=2, default=str)}

Rules for Suggestion Confidence:
- HIGH: RFI explicitly states Cost Impact > $500 AND architect/engineer has responded
- HIGH: Daily Log documents unforeseen condition (hidden damage, code violation discovered)
- MEDIUM: Daily Log mentions "Owner delay" or "design change" AND subsequent RFI was filed
- MEDIUM: Multiple RFIs on same specification section within 7 days
- LOW: Generic issue logged with no stated cost/schedule impact (EXCLUDE from suggestions)

Suggest ONLY Change Orders with HIGH or MEDIUM confidence.
If no qualifying patterns found, return empty suggestions array with explanation in analysis_summary.
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=2000
    )

    result = json.loads(response.choices[0].message.content)

    # Add metadata
    result["project_id"] = str(project_id)
    result["analyzed_at"] = datetime.utcnow().isoformat()
    result["rfi_count"] = len(recent_rfis)
    result["daily_log_count"] = len(recent_daily_logs)

    return result


# =============================================================================
# SAFETY RISK ANALYZER
# =============================================================================

async def analyze_safety_risks(
    project_id: UUID,
    recent_jhas: List[Dict[str, Any]],
    recent_incidents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes JHA forms and incident reports to identify safety risk patterns.

    Returns risk assessment and recommended interventions.
    """
    client = await get_groq_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are a construction safety analyst. Analyze JHA (Job Hazard Analysis)
forms and incident reports to identify:
1. Recurring hazards that need additional controls
2. Tasks with inadequate PPE specifications
3. Near-miss patterns that predict future incidents
4. Training gaps based on crew acknowledgments

Output JSON with:
{
    "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "findings": [
        {
            "category": "fall_protection" | "hot_work" | "material_handling" | "weather" | "ppe" | "training",
            "severity": 1-5,
            "description": "What was found",
            "recommendation": "Specific action to take",
            "affected_tasks": ["Task names"]
        }
    ],
    "immediate_actions": ["Actions needed within 24 hours"],
    "weekly_focus": "Safety topic for next toolbox talk"
}"""
            },
            {
                "role": "user",
                "content": f"""
Analyze safety data for Project ID: {project_id}

--- RECENT JHAs (Last 7 days) ---
{json.dumps(recent_jhas, indent=2, default=str)}

--- INCIDENT REPORTS (Last 30 days) ---
{json.dumps(recent_incidents, indent=2, default=str)}

Focus on patterns, not individual events. What systemic issues exist?
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=1500
    )

    result = json.loads(response.choices[0].message.content)
    result["project_id"] = str(project_id)
    result["analyzed_at"] = datetime.utcnow().isoformat()

    return result


# =============================================================================
# DAILY LOG SUMMARIZER
# =============================================================================

async def summarize_daily_logs(
    project_id: UUID,
    daily_logs: List[Dict[str, Any]],
    period_days: int = 7
) -> Dict[str, Any]:
    """
    Generates a weekly summary from daily logs for PM reporting.
    """
    client = await get_groq_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are a construction project manager assistant.
Summarize daily field reports into a concise weekly progress report.

Output JSON with:
{
    "period": "Dec 9-13, 2025",
    "weather_summary": "Brief weather impact statement",
    "manpower_summary": {
        "total_manhours": 0,
        "average_crew_size": 0,
        "peak_day": "Day with most workers"
    },
    "work_completed": [
        "Bullet points of completed work"
    ],
    "squares_completed": 0,
    "delays_encountered": [
        {"date": "2025-01-15", "reason": "Description", "hours_lost": 0}
    ],
    "materials_received": ["List of deliveries"],
    "issues_outstanding": ["Unresolved items needing attention"],
    "next_week_focus": "Key priorities for upcoming week"
}"""
            },
            {
                "role": "user",
                "content": f"""
Summarize the last {period_days} days of daily logs for Project ID: {project_id}

--- DAILY LOGS ---
{json.dumps(daily_logs, indent=2, default=str)}

Create a professional summary suitable for owner/GC reporting.
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=1500
    )

    result = json.loads(response.choices[0].message.content)
    result["project_id"] = str(project_id)
    result["generated_at"] = datetime.utcnow().isoformat()

    return result


# =============================================================================
# FORM PRE-FILL SUGGESTIONS
# =============================================================================

async def suggest_form_prefill(
    form_type: str,
    project_context: Dict[str, Any],
    recent_submissions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Suggests field values for a new form based on project context and history.

    Uses patterns from recent submissions to pre-populate common fields.
    """
    client = await get_groq_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""You are helping pre-fill a {form_type} form for a roofing project.
Based on the project context and recent form submissions, suggest values for common fields.

Output JSON with field suggestions:
{{
    "suggestions": {{
        "field_name": {{
            "value": "suggested value",
            "confidence": 0.0-1.0,
            "source": "Why you suggest this"
        }}
    }},
    "warnings": ["Any fields that need special attention"]
}}

Only suggest values you're confident about (>0.7). Leave others empty."""
            },
            {
                "role": "user",
                "content": f"""
Form Type: {form_type}

--- PROJECT CONTEXT ---
{json.dumps(project_context, indent=2, default=str)}

--- RECENT SIMILAR SUBMISSIONS ---
{json.dumps(recent_submissions[-5:], indent=2, default=str)}

What fields can be pre-filled?
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=1000
    )

    return json.loads(response.choices[0].message.content)


# =============================================================================
# BATCH ANALYSIS RUNNER
# =============================================================================

async def run_project_analysis(
    agency_id: UUID,
    project_id: UUID
) -> Dict[str, Any]:
    """
    Runs all AI analysis for a project. Call this from a scheduled job.

    Returns combined results from all analyzers.
    """
    from common.database import get_session
    from common.models import FormSubmission
    from sqlalchemy import select
    from datetime import datetime, timedelta

    results = {
        "project_id": str(project_id),
        "agency_id": str(agency_id),
        "analyzed_at": datetime.utcnow().isoformat(),
        "change_orders": None,
        "safety_risks": None,
        "weekly_summary": None,
        "errors": []
    }

    async with get_session() as session:
        # Fetch recent RFIs
        rfi_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "rfi",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=14)
        )
        rfi_result = await session.execute(rfi_query)
        rfis = [{"id": str(r.submission_id), "data": r.data, "created_at": r.created_at}
                for r in rfi_result.scalars()]

        # Fetch recent daily logs
        log_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "daily_report",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
        )
        log_result = await session.execute(log_query)
        logs = [{"id": str(r.submission_id), "data": r.data, "created_at": r.created_at}
                for r in log_result.scalars()]

        # Fetch JHAs
        jha_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "jha",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
        )
        jha_result = await session.execute(jha_query)
        jhas = [{"id": str(r.submission_id), "data": r.data, "created_at": r.created_at}
                for r in jha_result.scalars()]

    # Run analyzers
    try:
        if rfis or logs:
            results["change_orders"] = await generate_change_order_suggestions(
                project_id, rfis, logs
            )
    except Exception as e:
        results["errors"].append(f"Change order analysis failed: {str(e)}")

    try:
        if jhas:
            results["safety_risks"] = await analyze_safety_risks(
                project_id, jhas, []
            )
    except Exception as e:
        results["errors"].append(f"Safety analysis failed: {str(e)}")

    try:
        if logs:
            results["weekly_summary"] = await summarize_daily_logs(
                project_id, logs
            )
    except Exception as e:
        results["errors"].append(f"Weekly summary failed: {str(e)}")

    return results


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "generate_change_order_suggestions",
    "analyze_safety_risks",
    "summarize_daily_logs",
    "suggest_form_prefill",
    "run_project_analysis",
]
