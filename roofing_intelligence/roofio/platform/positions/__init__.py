"""
ROOFIO Position Automation System

Defines the 8 positions that can operate in Full AI or AI Assist mode.
Each position has defined functions, triggers, and confidence thresholds.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime
import uuid


class PositionMode(Enum):
    """Operation mode for each position"""
    OFF = "off"
    ASSIST = "assist"      # Human in role, AI provides one-click support
    FULL_AI = "full_ai"    # AI handles entire role autonomously


class PositionType(Enum):
    """The 8 positions in the roofing contractor workflow"""
    ESTIMATOR = "estimator"
    PROJECT_MANAGER = "project_manager"
    DETAILER = "detailer"
    SPEC_WRITER = "spec_writer"
    QC_INSPECTOR = "qc_inspector"
    SAFETY_OFFICER = "safety_officer"
    SUPERINTENDENT = "superintendent"
    ACCOUNTS = "accounts"


@dataclass
class ConfidenceScore:
    """Confidence scoring for AI actions"""
    score: int  # 0-100
    factors: Dict[str, int] = field(default_factory=dict)
    # Factors: data_completeness, data_consistency, historical_accuracy,
    #          ambiguity_level, risk_level

    @property
    def should_pause(self) -> bool:
        """Check if confidence is below threshold (90%)"""
        return self.score < 90

    @property
    def can_proceed_autonomously(self) -> bool:
        """Check if AI can proceed without human review"""
        return self.score >= 95

    @property
    def needs_optional_review(self) -> bool:
        """Check if flagging for optional review (90-94%)"""
        return 90 <= self.score < 95


@dataclass
class AIAction:
    """Represents an AI action that can be taken"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: PositionType = None
    action_type: str = ""
    description: str = ""
    trigger_event: str = ""

    # Execution
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)

    # Confidence
    confidence: ConfidenceScore = None

    # Status
    status: str = "pending"  # pending, completed, paused, human_review, failed
    paused_reason: str = ""

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime = None

    # Review
    reviewed_by: str = None
    review_action: str = None  # approved, edited, rejected


@dataclass
class PositionFunction:
    """A function that a position can perform"""
    function_id: str
    name: str
    description: str
    trigger: str  # What triggers this function
    available_in_modes: List[PositionMode]
    typical_confidence: int  # Expected confidence score
    output_forms: List[str]  # Forms this function generates


# =============================================================================
# POSITION DEFINITIONS WITH FUNCTIONS
# =============================================================================

ESTIMATOR_FUNCTIONS = [
    PositionFunction(
        function_id="est_takeoff",
        name="Quantity Takeoffs",
        description="Auto-generate measurements from PDF/DWG plans",
        trigger="plans_uploaded",
        available_in_modes=[PositionMode.FULL_AI, PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["material_takeoff"]
    ),
    PositionFunction(
        function_id="est_bom",
        name="Bill of Materials",
        description="Generate BOM from takeoff using product library",
        trigger="takeoff_complete",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=98,
        output_forms=["bom"]
    ),
    PositionFunction(
        function_id="est_labor",
        name="Labor Hour Calculation",
        description="Calculate labor hours from historical data",
        trigger="bom_generated",
        available_in_modes=[PositionMode.FULL_AI, PositionMode.ASSIST],
        typical_confidence=90,
        output_forms=["labor_estimate"]
    ),
    PositionFunction(
        function_id="est_bid",
        name="Bid Generation",
        description="Apply margins and generate complete bid package",
        trigger="all_costs_calculated",
        available_in_modes=[PositionMode.FULL_AI, PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["bid_proposal", "scope_of_work", "exclusions"]
    ),
    PositionFunction(
        function_id="est_supplement",
        name="Insurance Supplement",
        description="Generate supplement request for insurance claims",
        trigger="insurance_claim_identified",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=85,  # Often requires human review
        output_forms=["insurance_supplement_request"]
    ),
    PositionFunction(
        function_id="est_margin",
        name="Margin Analysis",
        description="Live profit/margin tracking vs actual costs",
        trigger="estimate_finalized",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["margin_analyzer"]
    ),
]

PROJECT_MANAGER_FUNCTIONS = [
    PositionFunction(
        function_id="pm_submittal_log",
        name="Submittal Log Generation",
        description="Auto-generate submittal log from estimate materials",
        trigger="estimate_approved",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["submittal_log"]
    ),
    PositionFunction(
        function_id="pm_submittal_reminder",
        name="Submittal Reminders",
        description="Draft reminder emails for upcoming submittals",
        trigger="submittal_due_7_days",
        available_in_modes=[PositionMode.FULL_AI, PositionMode.ASSIST],
        typical_confidence=98,
        output_forms=["email_draft"]
    ),
    PositionFunction(
        function_id="pm_rfi_draft",
        name="RFI Drafting",
        description="Draft RFI from spec conflict or field question",
        trigger="spec_conflict_detected",
        available_in_modes=[PositionMode.FULL_AI, PositionMode.ASSIST],
        typical_confidence=90,
        output_forms=["rfi"]
    ),
    PositionFunction(
        function_id="pm_co_draft",
        name="Change Order Draft",
        description="Draft change order from RFI with cost impact",
        trigger="rfi_has_cost_impact",
        available_in_modes=[PositionMode.ASSIST],  # Usually needs human
        typical_confidence=75,  # Often pauses
        output_forms=["change_order"]
    ),
    PositionFunction(
        function_id="pm_permit",
        name="Permit Application",
        description="Generate permit application from project/estimate data",
        trigger="municipality_selected",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=92,
        output_forms=["permit_application"]
    ),
    PositionFunction(
        function_id="pm_pay_app",
        name="Pay Application Draft",
        description="Generate G702/G703 from SOV progress",
        trigger="billing_period_ends",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=97,
        output_forms=["g702", "g703"]
    ),
]

SAFETY_OFFICER_FUNCTIONS = [
    PositionFunction(
        function_id="safety_jha",
        name="JHA Generation",
        description="Auto-generate JHA from products/hazards",
        trigger="job_created_with_materials",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["jha"]
    ),
    PositionFunction(
        function_id="safety_toolbox",
        name="Toolbox Talk Generation",
        description="Generate weekly toolbox talk topics",
        trigger="weekly_schedule",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["toolbox_talk"]
    ),
    PositionFunction(
        function_id="safety_silica",
        name="Silica Control Plan",
        description="Generate silica exposure control plan",
        trigger="scope_includes_cutting",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=97,
        output_forms=["silica_control_plan"]
    ),
    PositionFunction(
        function_id="safety_fall",
        name="Fall Protection Plan",
        description="Generate fall protection plan",
        trigger="job_height_over_6ft",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["fall_protection_plan"]
    ),
    PositionFunction(
        function_id="safety_lift",
        name="Crane Lift Plan",
        description="Generate crane/hoist lift plan",
        trigger="scope_includes_roof_loading",
        available_in_modes=[PositionMode.ASSIST],  # Requires human judgment
        typical_confidence=80,
        output_forms=["crane_lift_plan"]
    ),
    PositionFunction(
        function_id="safety_incident",
        name="Incident Report Draft",
        description="Draft OSHA 300 entry from incident report",
        trigger="incident_reported",
        available_in_modes=[PositionMode.ASSIST],  # Sensitive, needs human
        typical_confidence=70,
        output_forms=["incident_report", "osha_300_entry"]
    ),
]

ACCOUNTS_FUNCTIONS = [
    PositionFunction(
        function_id="acct_sov",
        name="SOV Generation",
        description="Create schedule of values from estimate",
        trigger="estimate_approved",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["schedule_of_values"]
    ),
    PositionFunction(
        function_id="acct_sov_update",
        name="SOV Progress Update",
        description="Update SOV percentages from daily reports",
        trigger="daily_reports_logged",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["schedule_of_values"]
    ),
    PositionFunction(
        function_id="acct_pay_app",
        name="Pay Application",
        description="Generate G702/G703 from SOV",
        trigger="billing_period_ends",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=97,
        output_forms=["g702", "g703"]
    ),
    PositionFunction(
        function_id="acct_waiver_cond",
        name="Conditional Lien Waiver",
        description="Generate conditional waiver with pay app",
        trigger="pay_app_approved",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["lien_waiver_conditional"]
    ),
    PositionFunction(
        function_id="acct_waiver_uncond",
        name="Unconditional Lien Waiver",
        description="Generate unconditional waiver when paid",
        trigger="payment_received",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=99,
        output_forms=["lien_waiver_unconditional"]
    ),
    PositionFunction(
        function_id="acct_job_cost",
        name="Job Cost Report",
        description="Generate job cost report (estimated vs actual)",
        trigger="daily_estimate_data_updated",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=98,
        output_forms=["job_cost_report"]
    ),
    PositionFunction(
        function_id="acct_closeout",
        name="Closeout Package",
        description="Compile closeout document package",
        trigger="project_complete",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["closeout_checklist"]
    ),
]

QC_INSPECTOR_FUNCTIONS = [
    PositionFunction(
        function_id="qc_checklist",
        name="Inspection Checklist",
        description="Load system-specific inspection checklist",
        trigger="inspection_started",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["inspection_checklist"]
    ),
    PositionFunction(
        function_id="qc_moisture",
        name="Moisture Analysis Report",
        description="Generate moisture analysis from readings",
        trigger="moisture_readings_logged",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=90,
        output_forms=["moisture_analysis_report"]
    ),
    PositionFunction(
        function_id="qc_punch",
        name="Punch List Generation",
        description="Auto-create punch list from deficiencies",
        trigger="deficiency_marked",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["punch_list"]
    ),
    PositionFunction(
        function_id="qc_penetration",
        name="Penetration Log",
        description="Track roof penetrations with drawing refs",
        trigger="penetration_logged",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=90,
        output_forms=["penetration_log"]
    ),
]

SUPERINTENDENT_FUNCTIONS = [
    PositionFunction(
        function_id="super_daily",
        name="Daily Report",
        description="Pre-fill daily report with project/weather/crew",
        trigger="daily_report_started",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=90,
        output_forms=["daily_field_report"]
    ),
    PositionFunction(
        function_id="super_stored",
        name="Stored Material Log",
        description="Track stored materials for SOV billing",
        trigger="delivery_received",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["stored_material_log"]
    ),
    PositionFunction(
        function_id="super_lookahead",
        name="2-Week Lookahead",
        description="Generate 2-week schedule from master",
        trigger="weekly_schedule",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=90,
        output_forms=["two_week_lookahead"]
    ),
    PositionFunction(
        function_id="super_weather",
        name="Weather Delay Log",
        description="Auto-document weather delays",
        trigger="weather_forecast_rain",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["weather_delay_log"]
    ),
]

DETAILER_FUNCTIONS = [
    PositionFunction(
        function_id="detail_transmittal",
        name="Shop Drawing Transmittal",
        description="Generate transmittal for drawing submission",
        trigger="drawings_ready_for_review",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=95,
        output_forms=["shop_drawing_transmittal"]
    ),
    PositionFunction(
        function_id="detail_compliance",
        name="Spec Compliance Check",
        description="Check details against spec requirements",
        trigger="detail_completed",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=85,
        output_forms=["compliance_report"]
    ),
    PositionFunction(
        function_id="detail_asbuilt",
        name="As-Built Overlay",
        description="Redline field changes on originals",
        trigger="field_changes_reported",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=80,
        output_forms=["as_built_drawing"]
    ),
]

SPEC_WRITER_FUNCTIONS = [
    PositionFunction(
        function_id="spec_section",
        name="Specification Section",
        description="Generate CSI 3-part spec section",
        trigger="spec_section_requested",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=95,
        output_forms=["specification_section"]
    ),
    PositionFunction(
        function_id="spec_warranty",
        name="Warranty Application",
        description="Pre-fill manufacturer warranty forms",
        trigger="closeout_begins",
        available_in_modes=[PositionMode.FULL_AI],
        typical_confidence=92,
        output_forms=["warranty_application"]
    ),
    PositionFunction(
        function_id="spec_substitution",
        name="Substitution Review",
        description="Analyze product substitution requests",
        trigger="substitution_requested",
        available_in_modes=[PositionMode.ASSIST],
        typical_confidence=85,
        output_forms=["substitution_review"]
    ),
]


# =============================================================================
# POSITION REGISTRY
# =============================================================================

POSITION_FUNCTIONS = {
    PositionType.ESTIMATOR: ESTIMATOR_FUNCTIONS,
    PositionType.PROJECT_MANAGER: PROJECT_MANAGER_FUNCTIONS,
    PositionType.SAFETY_OFFICER: SAFETY_OFFICER_FUNCTIONS,
    PositionType.ACCOUNTS: ACCOUNTS_FUNCTIONS,
    PositionType.QC_INSPECTOR: QC_INSPECTOR_FUNCTIONS,
    PositionType.SUPERINTENDENT: SUPERINTENDENT_FUNCTIONS,
    PositionType.DETAILER: DETAILER_FUNCTIONS,
    PositionType.SPEC_WRITER: SPEC_WRITER_FUNCTIONS,
}


@dataclass
class PositionConfig:
    """Configuration for a position"""
    position: PositionType
    mode: PositionMode
    confidence_threshold: int = 90
    assigned_employee_id: Optional[str] = None

    # Statistics
    total_actions: int = 0
    actions_auto_completed: int = 0
    actions_flagged: int = 0
    average_confidence: float = 0.0

    @property
    def functions(self) -> List[PositionFunction]:
        """Get available functions for this position"""
        return POSITION_FUNCTIONS.get(self.position, [])

    @property
    def badge_text(self) -> str:
        """Get badge display text"""
        if self.mode == PositionMode.FULL_AI:
            return "ROOFIO AUTONOMOUS"
        elif self.mode == PositionMode.ASSIST:
            return "ROOFIO ASSIST"
        else:
            return "DISABLED"

    @property
    def badge_emoji(self) -> str:
        """Get badge emoji"""
        if self.mode == PositionMode.FULL_AI:
            return "\U0001F916"  # Robot
        elif self.mode == PositionMode.ASSIST:
            return "\U0001F9D1\u200D\U0001F4BC"  # Office worker
        else:
            return "\u26D4"  # No entry
