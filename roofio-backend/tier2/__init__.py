"""
ROOFIO Tier 2 Module
====================

Fast AI with Groq + RAG from Skills Docs.

Cost: ~$0.001 per request
Latency: <500ms

Modules:
- form_ai_genie.py: Intelligent form analysis (Change Orders, Safety, Summaries)
- groq_ai.py: Groq integration with RAG (future)
- summarize.py: Text summarization (future)
- classify.py: Text classification (future)
- extract.py: Entity extraction (future)
"""

from .form_ai_genie import (
    generate_change_order_suggestions,
    analyze_safety_risks,
    summarize_daily_logs,
    suggest_form_prefill,
    run_project_analysis,
)

__all__ = [
    "generate_change_order_suggestions",
    "analyze_safety_risks",
    "summarize_daily_logs",
    "suggest_form_prefill",
    "run_project_analysis",
]
