"""
ROOFIO Forms Registry

74 forms across 8 positions, all linked via Project_ID through SSOT.

CRITICAL: No siloed forms. Every form pre-fills from the Unified Project Object.
Data entered ONCE propagates EVERYWHERE.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class FormMode(Enum):
    """Which modes can generate this form"""
    FULL_AI = "full_ai"      # AI generates autonomously
    ASSIST = "assist"        # AI assists human with pre-fill
    BOTH = "both"            # Available in both modes


@dataclass
class SSOTMapping:
    """How a form field maps to SSOT data"""
    field_name: str
    source_table: str
    source_field: str
    origin_description: str
    editable: bool = True


@dataclass
class FormDefinition:
    """Definition of a form in the system"""
    form_id: str
    name: str
    description: str
    position: str  # Which position owns this form
    mode: FormMode

    # SSOT Mappings
    ssot_chain: List[str]  # e.g., ["estimate", "sov", "pay_app"]
    prefill_fields: List[SSOTMapping] = field(default_factory=list)

    # Triggers
    auto_trigger: Optional[str] = None  # What triggers auto-generation
    manual_trigger: str = ""  # Button/action for manual creation

    # Output
    output_format: str = "pdf"  # pdf, json, email, etc.
    template_name: Optional[str] = None


# =============================================================================
# ESTIMATOR FORMS (10)
# =============================================================================

ESTIMATOR_FORMS = [
    FormDefinition(
        form_id="bid_proposal",
        name="Bid Proposal",
        description="Formal bid submission document",
        position="estimator",
        mode=FormMode.BOTH,
        ssot_chain=["company", "project", "estimate"],
        prefill_fields=[
            SSOTMapping("company_name", "companies", "name", "Company info"),
            SSOTMapping("project_address", "projects", "address", "Project location"),
            SSOTMapping("total_bid", "estimates", "total_estimate", "Calculated total"),
        ],
        manual_trigger="Create Bid Proposal",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="scope_of_work",
        name="Scope of Work",
        description="Detailed work description",
        position="estimator",
        mode=FormMode.BOTH,
        ssot_chain=["project", "jobs"],
        prefill_fields=[
            SSOTMapping("system_type", "jobs", "system_type", "Roofing system"),
            SSOTMapping("area_sqft", "jobs", "area_sqft", "Square footage"),
        ],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="material_takeoff",
        name="Material Takeoff & BOM",
        description="Bill of Materials from takeoff",
        position="estimator",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "estimate_line_items", "products"],
        auto_trigger="takeoff_complete",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="unit_price_schedule",
        name="Unit Price Schedule",
        description="Line item pricing breakdown",
        position="estimator",
        mode=FormMode.BOTH,
        ssot_chain=["products", "company.labor_rates"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="exclusions",
        name="Exclusions/Clarifications",
        description="What's NOT included in bid",
        position="estimator",
        mode=FormMode.BOTH,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="bid_bond_request",
        name="Bid Bond Request",
        description="Surety bond request",
        position="estimator",
        mode=FormMode.ASSIST,
        ssot_chain=["company", "estimate"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="bid_comparison",
        name="Bid Comparison Sheet",
        description="Compare competitor bids",
        position="estimator",
        mode=FormMode.ASSIST,
        ssot_chain=[],  # Manual entry
        output_format="pdf",
    ),
    FormDefinition(
        form_id="sub_quote_request",
        name="Subcontractor Quote Request",
        description="Request pricing from subs",
        position="estimator",
        mode=FormMode.BOTH,
        ssot_chain=["project", "contacts"],
        output_format="email",
    ),
    FormDefinition(
        form_id="insurance_supplement",
        name="Insurance Supplement Request",
        description="Document missed items for adjusters",
        position="estimator",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "insurance_supplements"],
        auto_trigger="insurance_claim_identified",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="margin_analyzer",
        name="Profit/Margin Analyzer",
        description="Live labor/material/overhead breakdown",
        position="estimator",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "daily_reports", "change_orders"],
        auto_trigger="estimate_finalized",
        output_format="dashboard",
    ),
]

# =============================================================================
# PROJECT MANAGER FORMS (11)
# =============================================================================

PROJECT_MANAGER_FORMS = [
    FormDefinition(
        form_id="submittal_cover",
        name="Submittal Cover Sheet",
        description="Track product approvals",
        position="project_manager",
        mode=FormMode.FULL_AI,
        ssot_chain=["project", "submittals", "products"],
        auto_trigger="submittal_created",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="submittal_log",
        name="Submittal Log",
        description="Track all submittals",
        position="project_manager",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "submittals"],
        auto_trigger="estimate_approved",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="rfi",
        name="RFI Form",
        description="Request for Information",
        position="project_manager",
        mode=FormMode.BOTH,
        ssot_chain=["project", "contacts", "drawings"],
        prefill_fields=[
            SSOTMapping("project_name", "projects", "name", "Project"),
            SSOTMapping("architect_email", "contacts", "email", "Architect contact"),
        ],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="rfi_log",
        name="RFI Log",
        description="Track all RFIs",
        position="project_manager",
        mode=FormMode.FULL_AI,
        ssot_chain=["rfis"],
        auto_trigger="rfi_created",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="change_order",
        name="Change Order Request",
        description="Document scope changes",
        position="project_manager",
        mode=FormMode.ASSIST,  # Usually needs human judgment
        ssot_chain=["jobs", "rfis", "estimate.labor_rates"],
        prefill_fields=[
            SSOTMapping("labor_rate", "companies", "labor_rates", "From company rates"),
            SSOTMapping("markup", "companies", "default_markup", "Default markup"),
        ],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="change_order_log",
        name="Change Order Log",
        description="Track all change orders",
        position="project_manager",
        mode=FormMode.FULL_AI,
        ssot_chain=["change_orders"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="meeting_minutes",
        name="Meeting Minutes",
        description="Record meeting decisions",
        position="project_manager",
        mode=FormMode.BOTH,
        ssot_chain=["project", "contacts"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="transmittal",
        name="Transmittal",
        description="Cover sheet for documents sent",
        position="project_manager",
        mode=FormMode.BOTH,
        ssot_chain=["project", "contacts"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="schedule_update",
        name="Schedule Update Notice",
        description="Communicate schedule changes",
        position="project_manager",
        mode=FormMode.BOTH,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="delay_notice",
        name="Delay Notification",
        description="Formal delay claim",
        position="project_manager",
        mode=FormMode.BOTH,
        ssot_chain=["project", "daily_reports", "rfis"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="permit_application",
        name="Permit Application Packet",
        description="Building permit application",
        position="project_manager",
        mode=FormMode.FULL_AI,
        ssot_chain=["project", "estimate", "permits"],
        auto_trigger="municipality_selected",
        output_format="pdf",
    ),
]

# =============================================================================
# SHOP DRAWING DETAILER FORMS (7)
# =============================================================================

DETAILER_FORMS = [
    FormDefinition(
        form_id="shop_drawing_transmittal",
        name="Shop Drawing Transmittal",
        description="Submit drawings for review",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["project", "drawings"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="drawing_register",
        name="Drawing Register/Log",
        description="Track all drawings",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["drawings"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="revision_history",
        name="Revision History Sheet",
        description="Log drawing changes",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["drawings"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="detail_index",
        name="Detail Index",
        description="Catalog of details",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["drawings"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="keynote_legend",
        name="Keynote Legend",
        description="Define drawing symbols",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="drawing_review_response",
        name="Drawing Review Response",
        description="Address reviewer comments",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["submittals"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="as_built_overlay",
        name="As-Built Drawing Overlay",
        description="Redline field changes",
        position="detailer",
        mode=FormMode.ASSIST,
        ssot_chain=["drawings", "daily_reports"],
        output_format="dwg",
    ),
]

# =============================================================================
# SPECIFICATION WRITER FORMS (6)
# =============================================================================

SPEC_WRITER_FORMS = [
    FormDefinition(
        form_id="spec_section",
        name="Specification Section",
        description="CSI 3-part format spec",
        position="spec_writer",
        mode=FormMode.FULL_AI,
        ssot_chain=["products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="product_data_compilation",
        name="Product Data Sheet Compilation",
        description="Organize manufacturer data",
        position="spec_writer",
        mode=FormMode.FULL_AI,
        ssot_chain=["products", "submittals"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="substitution_request",
        name="Substitution Request",
        description="Request product swap",
        position="spec_writer",
        mode=FormMode.BOTH,
        ssot_chain=["products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="basis_of_design",
        name="Basis of Design Summary",
        description="Document BOD products",
        position="spec_writer",
        mode=FormMode.FULL_AI,
        ssot_chain=["products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="spec_compliance_checklist",
        name="Spec Compliance Checklist",
        description="Verify installation matches spec",
        position="spec_writer",
        mode=FormMode.ASSIST,
        ssot_chain=["inspections"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="warranty_application",
        name="Manufacturer Warranty Application",
        description="Pre-fill NDL/warranty forms",
        position="spec_writer",
        mode=FormMode.FULL_AI,
        ssot_chain=["project", "products", "inspections", "daily_reports", "employees"],
        auto_trigger="closeout_begins",
        output_format="pdf",
    ),
]

# =============================================================================
# QC / INSPECTOR FORMS (10)
# =============================================================================

QC_INSPECTOR_FORMS = [
    FormDefinition(
        form_id="pre_install_checklist",
        name="Pre-Installation Checklist",
        description="Verify readiness",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="progress_inspection",
        name="Progress Inspection Report",
        description="Document ongoing work",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "inspections"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="final_inspection",
        name="Final Inspection Report",
        description="Sign-off inspection",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "inspections"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="punch_list",
        name="Punch List",
        description="Deficiency tracking",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["inspections", "punch_list_items"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="test_report",
        name="Test Report (flood/ELD/core)",
        description="Document test results",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="non_conformance",
        name="Non-Conformance Report",
        description="Document defects",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["inspections"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="warranty_inspection",
        name="Warranty Inspection Checklist",
        description="Pre-warranty check",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="photo_log",
        name="Photo Documentation Log",
        description="Organize progress photos",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="moisture_analysis",
        name="Moisture Analysis Report",
        description="Nuclear/IR scan logging",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="penetration_log",
        name="Roof Penetration Log",
        description="Track flashings/curbs",
        position="qc_inspector",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "drawings"],
        output_format="pdf",
    ),
]

# =============================================================================
# SAFETY OFFICER FORMS (10)
# =============================================================================

SAFETY_OFFICER_FORMS = [
    FormDefinition(
        form_id="jha",
        name="Job Hazard Analysis (JHA)",
        description="Identify hazards",
        position="safety_officer",
        mode=FormMode.FULL_AI,
        ssot_chain=["jobs", "products.hazards"],
        auto_trigger="job_created_with_materials",
        prefill_fields=[
            SSOTMapping("hazards", "products", "hazards", "Auto from products"),
        ],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="toolbox_talk",
        name="Toolbox Talk Sign-In",
        description="Document safety meetings",
        position="safety_officer",
        mode=FormMode.FULL_AI,
        ssot_chain=["project", "employees"],
        auto_trigger="weekly_schedule",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="incident_report",
        name="Incident/Accident Report",
        description="Document injuries",
        position="safety_officer",
        mode=FormMode.ASSIST,
        ssot_chain=["project", "employees"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="safety_inspection",
        name="Safety Inspection Checklist",
        description="Site safety audit",
        position="safety_officer",
        mode=FormMode.BOTH,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="hot_work_permit",
        name="Hot Work Permit",
        description="Authorize torch work",
        position="safety_officer",
        mode=FormMode.ASSIST,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="fall_protection_plan",
        name="Fall Protection Plan",
        description="Document fall prevention",
        position="safety_officer",
        mode=FormMode.FULL_AI,
        ssot_chain=["jobs"],
        auto_trigger="job_height_over_6ft",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="equipment_inspection",
        name="Equipment Inspection Log",
        description="Track equipment safety",
        position="safety_officer",
        mode=FormMode.ASSIST,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="osha_300",
        name="OSHA 300 Log Entry",
        description="Recordable incident log",
        position="safety_officer",
        mode=FormMode.ASSIST,
        ssot_chain=["safety_documents"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="silica_control_plan",
        name="Silica Exposure Control Plan",
        description="OSHA mandatory for cutting",
        position="safety_officer",
        mode=FormMode.FULL_AI,
        ssot_chain=["jobs", "products"],
        auto_trigger="scope_includes_cutting",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="crane_lift_plan",
        name="Crane/Hoist Lift Plan",
        description="Critical for roof loading",
        position="safety_officer",
        mode=FormMode.ASSIST,  # Requires human judgment
        ssot_chain=["jobs"],
        output_format="pdf",
    ),
]

# =============================================================================
# SUPERINTENDENT / FOREMAN FORMS (9)
# =============================================================================

SUPERINTENDENT_FORMS = [
    FormDefinition(
        form_id="daily_field_report",
        name="Daily Field Report",
        description="Document daily activities",
        position="superintendent",
        mode=FormMode.BOTH,
        ssot_chain=["project", "employees", "weather_api"],
        prefill_fields=[
            SSOTMapping("weather", "weather_api", "forecast", "Auto from API"),
            SSOTMapping("crew", "employees", "assigned", "Yesterday's crew"),
        ],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="tm_ticket",
        name="T&M (Time & Materials) Ticket",
        description="Track extra work",
        position="superintendent",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "employees", "products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="material_receiving",
        name="Material Receiving Log",
        description="Document deliveries",
        position="superintendent",
        mode=FormMode.ASSIST,
        ssot_chain=["products"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="delivery_schedule",
        name="Delivery Schedule",
        description="Plan material drops",
        position="superintendent",
        mode=FormMode.BOTH,
        ssot_chain=["jobs", "contacts"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="two_week_lookahead",
        name="2-Week Lookahead",
        description="Short-term schedule",
        position="superintendent",
        mode=FormMode.FULL_AI,
        ssot_chain=["project"],
        auto_trigger="weekly_schedule",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="extra_work_auth",
        name="Extra Work Authorization",
        description="Approve additional work",
        position="superintendent",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "change_orders"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="weather_delay_log",
        name="Weather Delay Log",
        description="Document weather impacts",
        position="superintendent",
        mode=FormMode.FULL_AI,
        ssot_chain=["daily_reports", "weather_api"],
        auto_trigger="weather_forecast_rain",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="crew_assignment",
        name="Crew Assignment Sheet",
        description="Daily crew deployment",
        position="superintendent",
        mode=FormMode.BOTH,
        ssot_chain=["employees", "jobs"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="stored_material_log",
        name="Stored Material Log",
        description="Track material on roof vs ground",
        position="superintendent",
        mode=FormMode.ASSIST,
        ssot_chain=["stored_materials", "schedule_of_values"],
        output_format="pdf",
    ),
]

# =============================================================================
# ACCOUNTS / ADMINISTRATION FORMS (11)
# =============================================================================

ACCOUNTS_FORMS = [
    FormDefinition(
        form_id="g702",
        name="Progress Invoice (G702)",
        description="AIA payment application",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["schedule_of_values", "pay_applications"],
        auto_trigger="billing_period_ends",
        prefill_fields=[
            SSOTMapping("original_contract_sum", "jobs", "original_amount", "From job"),
            SSOTMapping("change_orders_approved", "change_orders", "sum(total)", "Sum of approved COs"),
            SSOTMapping("total_completed_stored", "schedule_of_values", "sum(total_completed + materials_stored)", "From SOV"),
        ],
        output_format="pdf",
        template_name="aia_g702",
    ),
    FormDefinition(
        form_id="g703",
        name="Continuation Sheet (G703)",
        description="SOV continuation sheet",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["schedule_of_values"],
        auto_trigger="pay_app_created",
        output_format="pdf",
        template_name="aia_g703",
    ),
    FormDefinition(
        form_id="lien_waiver_conditional",
        name="Lien Waiver (Conditional)",
        description="Conditional release of lien rights",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["pay_applications"],
        auto_trigger="pay_app_approved",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="lien_waiver_unconditional",
        name="Lien Waiver (Unconditional)",
        description="Final lien release",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["pay_applications"],
        auto_trigger="payment_received",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="coi_request",
        name="Certificate of Insurance Request",
        description="Request updated COI",
        position="accounts",
        mode=FormMode.BOTH,
        ssot_chain=["contacts"],
        output_format="email",
    ),
    FormDefinition(
        form_id="contract_checklist",
        name="Contract Exhibit Checklist",
        description="Track contract documents",
        position="accounts",
        mode=FormMode.ASSIST,
        ssot_chain=["project"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="closeout_checklist",
        name="Closeout Document Checklist",
        description="Track closeout docs",
        position="accounts",
        mode=FormMode.ASSIST,
        ssot_chain=["jobs", "closeout_documents"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="warranty_letter",
        name="Warranty Letter",
        description="Issue workmanship warranty",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["jobs", "company"],
        auto_trigger="job_complete",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="sub_pay_request",
        name="Subcontractor Pay Request",
        description="Sub payment processing",
        position="accounts",
        mode=FormMode.BOTH,
        ssot_chain=["contacts"],
        output_format="pdf",
    ),
    FormDefinition(
        form_id="notice_of_completion",
        name="Notice of Completion",
        description="Formal project completion",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["project", "inspections"],
        auto_trigger="project_complete",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="schedule_of_values",
        name="Schedule of Values (SOV)",
        description="Contract breakdown",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "estimate_line_items"],
        auto_trigger="estimate_approved",
        output_format="pdf",
    ),
    FormDefinition(
        form_id="job_cost_report",
        name="Job Cost Report",
        description="Actual vs Estimated",
        position="accounts",
        mode=FormMode.FULL_AI,
        ssot_chain=["estimate", "daily_reports", "change_orders", "stored_materials"],
        auto_trigger="daily_data_updated",
        output_format="dashboard",
    ),
]

# =============================================================================
# COMPLETE FORM REGISTRY
# =============================================================================

ALL_FORMS = (
    ESTIMATOR_FORMS +
    PROJECT_MANAGER_FORMS +
    DETAILER_FORMS +
    SPEC_WRITER_FORMS +
    QC_INSPECTOR_FORMS +
    SAFETY_OFFICER_FORMS +
    SUPERINTENDENT_FORMS +
    ACCOUNTS_FORMS
)

FORMS_BY_ID = {f.form_id: f for f in ALL_FORMS}

FORMS_BY_POSITION = {
    "estimator": ESTIMATOR_FORMS,
    "project_manager": PROJECT_MANAGER_FORMS,
    "detailer": DETAILER_FORMS,
    "spec_writer": SPEC_WRITER_FORMS,
    "qc_inspector": QC_INSPECTOR_FORMS,
    "safety_officer": SAFETY_OFFICER_FORMS,
    "superintendent": SUPERINTENDENT_FORMS,
    "accounts": ACCOUNTS_FORMS,
}


def get_form(form_id: str) -> Optional[FormDefinition]:
    """Get a form by ID"""
    return FORMS_BY_ID.get(form_id)


def get_forms_for_position(position: str) -> List[FormDefinition]:
    """Get all forms for a position"""
    return FORMS_BY_POSITION.get(position, [])


def get_auto_trigger_forms() -> List[FormDefinition]:
    """Get all forms that have auto-triggers"""
    return [f for f in ALL_FORMS if f.auto_trigger]


def get_form_count_summary() -> Dict[str, int]:
    """Get form count by position"""
    return {pos: len(forms) for pos, forms in FORMS_BY_POSITION.items()}


# Print summary
if __name__ == "__main__":
    print("ROOFIO FORMS REGISTRY")
    print("=" * 50)
    for pos, forms in FORMS_BY_POSITION.items():
        print(f"{pos.upper()}: {len(forms)} forms")
    print("-" * 50)
    print(f"TOTAL: {len(ALL_FORMS)} forms")
