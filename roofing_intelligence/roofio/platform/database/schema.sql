-- ROOFIO UNIFIED PROJECT OBJECT (UPO) DATABASE SCHEMA
-- Version 2.0 - Single Source of Truth Architecture
-- All data linked via project_id - NO SILOED FORMS

-- ============================================================================
-- CORE ENTITIES (Company Level)
-- ============================================================================

CREATE TABLE IF NOT EXISTS companies (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    license_no TEXT,
    tax_id TEXT,
    insurance_info JSONB,
    default_markup DECIMAL(5,2) DEFAULT 15.00,
    warranty_terms TEXT,
    payment_terms TEXT,
    labor_rates JSONB,  -- {"journeyman": 85, "foreman": 95, "apprentice": 55}
    overhead_rate DECIMAL(5,2) DEFAULT 10.00,
    profit_margin_target DECIMAL(5,2) DEFAULT 15.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    contact_type TEXT NOT NULL CHECK (contact_type IN (
        'owner', 'gc', 'architect', 'subcontractor', 'supplier',
        'inspector', 'adjuster', 'manufacturer_rep', 'other'
    )),
    name TEXT NOT NULL,
    company_name TEXT,
    email TEXT,
    phone TEXT,
    address JSONB,
    relationship_history JSONB DEFAULT '[]'::JSONB,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN (
        'estimator', 'project_manager', 'detailer', 'spec_writer',
        'qc_inspector', 'safety_officer', 'superintendent', 'foreman',
        'journeyman', 'apprentice', 'admin', 'accounts'
    )),
    certifications JSONB DEFAULT '[]'::JSONB,  -- ["OSHA 30", "Carlisle Certified", etc]
    hourly_rate DECIMAL(10,2),
    emergency_contact JSONB,
    training_records JSONB DEFAULT '[]'::JSONB,
    osha_10_date DATE,
    osha_30_date DATE,
    assigned_projects UUID[] DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PRODUCT LIBRARY - SSOT for all material data
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    manufacturer TEXT NOT NULL,
    name TEXT NOT NULL,
    sku TEXT,
    unit TEXT NOT NULL,  -- SF, LF, EA, GAL, etc
    unit_cost DECIMAL(10,2),
    spec_section TEXT,  -- 07 54 00, etc
    fm_approval TEXT,
    ul_listing TEXT,
    warranty_years INTEGER,
    supplier_id UUID REFERENCES contacts(contact_id),
    lead_time_days INTEGER,
    hazards JSONB DEFAULT '[]'::JSONB,  -- Auto-generates JHA entries
    inspection_requirements JSONB DEFAULT '[]'::JSONB,  -- Auto-generates QC checklists
    warranty_form_template TEXT,  -- Which manufacturer warranty form to use
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- UNIFIED PROJECT OBJECT (UPO) - THE CORE
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    address JSONB NOT NULL,
    project_type TEXT CHECK (project_type IN ('commercial', 'residential', 'industrial', 'institutional')),

    -- LINKED CONTACTS (entered once, used everywhere)
    gc_contact_id UUID REFERENCES contacts(contact_id),
    owner_contact_id UUID REFERENCES contacts(contact_id),
    architect_contact_id UUID REFERENCES contacts(contact_id),
    adjuster_contact_id UUID REFERENCES contacts(contact_id),

    -- PROJECT DATA
    permit_number TEXT,
    permit_status TEXT CHECK (permit_status IN ('not_applied', 'pending', 'approved', 'expired')),
    municipality TEXT,
    contract_amount DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'bidding' CHECK (status IN (
        'bidding', 'awarded', 'in_progress', 'punch_list',
        'closeout', 'complete', 'warranty', 'cancelled'
    )),
    spec_sections TEXT[],
    insurance_requirements JSONB,

    -- INSURANCE CLAIM FIELDS
    is_insurance_claim BOOLEAN DEFAULT FALSE,
    claim_number TEXT,
    policy_number TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- ESTIMATES - SOURCE DATA (Propagates to ALL other entities)
-- ============================================================================

CREATE TABLE IF NOT EXISTS estimates (
    estimate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'revised')),
    created_date TIMESTAMPTZ DEFAULT NOW(),

    -- CALCULATED FIELDS (auto-updated by triggers)
    subtotal_materials DECIMAL(12,2) DEFAULT 0,
    subtotal_labor DECIMAL(12,2) DEFAULT 0,
    overhead_amount DECIMAL(12,2) DEFAULT 0,
    profit_amount DECIMAL(12,2) DEFAULT 0,
    total_estimate DECIMAL(12,2) DEFAULT 0,

    -- MARGIN ANALYSIS
    margin_analysis JSONB DEFAULT '{}'::JSONB,

    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estimate_line_items (
    line_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estimate_id UUID REFERENCES estimates(estimate_id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(product_id),
    description TEXT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    unit TEXT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    material_total DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    labor_hours DECIMAL(10,2),
    labor_rate DECIMAL(10,2),
    labor_total DECIMAL(12,2) GENERATED ALWAYS AS (labor_hours * labor_rate) STORED,
    markup_percent DECIMAL(5,2) DEFAULT 0,
    line_total DECIMAL(12,2),  -- Calculated with markup
    sort_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- JOBS (Scopes within Project) - Links Estimate to Execution
-- ============================================================================

CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    estimate_id UUID REFERENCES estimates(estimate_id),
    scope_description TEXT NOT NULL,
    area_sqft DECIMAL(12,2),

    -- SYSTEM TYPE (Drives QC checklists, JHA hazards, warranty forms)
    system_type TEXT CHECK (system_type IN (
        'tpo_mechanically_attached', 'tpo_fully_adhered', 'tpo_ballasted',
        'epdm_mechanically_attached', 'epdm_fully_adhered', 'epdm_ballasted',
        'pvc_mechanically_attached', 'pvc_fully_adhered',
        'mod_bit_torch', 'mod_bit_cold', 'mod_bit_self_adhered',
        'bur_hot', 'bur_cold',
        'metal_standing_seam', 'metal_exposed_fastener',
        'shingles_architectural', 'shingles_3_tab',
        'coating_acrylic', 'coating_silicone',
        'waterproofing_fluid', 'waterproofing_sheet',
        'air_barrier', 'other'
    )),
    warranty_type TEXT CHECK (warranty_type IN (
        'material_only', 'system', 'ndl', 'platinum', 'gold', 'standard', 'none'
    )),
    attachment_method TEXT,

    -- FINANCIAL (SSOT - Updated by triggers from estimates/change_orders)
    original_amount DECIMAL(12,2),
    change_orders_total DECIMAL(12,2) DEFAULT 0,
    current_amount DECIMAL(12,2) GENERATED ALWAYS AS (original_amount + change_orders_total) STORED,
    billed_to_date DECIMAL(12,2) DEFAULT 0,
    retention_held DECIMAL(12,2) DEFAULT 0,
    balance_due DECIMAL(12,2),

    status TEXT DEFAULT 'not_started' CHECK (status IN (
        'not_started', 'mobilizing', 'in_progress', 'punch_list',
        'final_inspection', 'closeout', 'complete', 'warranty'
    )),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SCHEDULE OF VALUES (SOV) - Auto-generated from Estimate, Updated by Daily Reports
-- ============================================================================

CREATE TABLE IF NOT EXISTS schedule_of_values (
    sov_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    spec_section TEXT,

    -- VALUES (Initial from estimate)
    scheduled_value DECIMAL(12,2) NOT NULL,

    -- PROGRESS (Updated by daily reports)
    work_completed_previous DECIMAL(12,2) DEFAULT 0,
    work_completed_current DECIMAL(12,2) DEFAULT 0,
    materials_stored DECIMAL(12,2) DEFAULT 0,

    -- CALCULATED
    total_completed DECIMAL(12,2) GENERATED ALWAYS AS (work_completed_previous + work_completed_current) STORED,
    percent_complete DECIMAL(5,2),  -- Updated by trigger
    balance_to_finish DECIMAL(12,2),  -- Updated by trigger
    retainage DECIMAL(12,2),  -- Calculated based on contract terms

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SUBMITTALS - Auto-generated from Estimate products
-- ============================================================================

CREATE TABLE IF NOT EXISTS submittals (
    submittal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    number TEXT NOT NULL,
    spec_section TEXT,
    description TEXT NOT NULL,
    product_ids UUID[] DEFAULT '{}',  -- Linked to estimate products

    submitted_date DATE,
    required_date DATE,
    approved_date DATE,
    status TEXT DEFAULT 'not_submitted' CHECK (status IN (
        'not_submitted', 'submitted', 'under_review', 'approved',
        'approved_as_noted', 'revise_resubmit', 'rejected'
    )),

    attachments JSONB DEFAULT '[]'::JSONB,
    revision_history JSONB DEFAULT '[]'::JSONB,
    reviewer_comments TEXT,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- RFIs - Request for Information
-- ============================================================================

CREATE TABLE IF NOT EXISTS rfis (
    rfi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    number TEXT NOT NULL,
    subject TEXT NOT NULL,
    question TEXT NOT NULL,
    drawing_ref TEXT,
    spec_ref TEXT,

    cost_impact BOOLEAN DEFAULT FALSE,
    cost_impact_amount DECIMAL(12,2),
    schedule_impact BOOLEAN DEFAULT FALSE,
    schedule_impact_days INTEGER,

    submitted_date DATE,
    required_date DATE,
    response_date DATE,
    response TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft', 'submitted', 'under_review', 'answered', 'closed'
    )),

    linked_change_orders UUID[] DEFAULT '{}',
    attachments JSONB DEFAULT '[]'::JSONB,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CHANGE ORDERS
-- ============================================================================

CREATE TABLE IF NOT EXISTS change_orders (
    co_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    number TEXT NOT NULL,
    description TEXT NOT NULL,
    reason TEXT CHECK (reason IN (
        'owner_request', 'design_change', 'unforeseen_condition',
        'code_requirement', 'value_engineering', 'rfi_response', 'other'
    )),

    -- COSTS (Linked from estimate rates)
    labor_cost DECIMAL(12,2) DEFAULT 0,
    material_cost DECIMAL(12,2) DEFAULT 0,
    equipment_cost DECIMAL(12,2) DEFAULT 0,
    subcontractor_cost DECIMAL(12,2) DEFAULT 0,
    markup_percent DECIMAL(5,2),
    markup_amount DECIMAL(12,2),
    total DECIMAL(12,2),

    submitted_date DATE,
    approved_date DATE,
    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft', 'submitted', 'under_review', 'approved', 'rejected', 'void'
    )),

    linked_rfi_id UUID REFERENCES rfis(rfi_id),
    approval_signatures JSONB DEFAULT '[]'::JSONB,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DAILY REPORTS - Updates SOV progress
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    report_date DATE NOT NULL,

    -- WEATHER (Auto-fetched from API)
    weather JSONB,  -- {temp_high, temp_low, conditions, wind_speed, precipitation}
    weather_delay BOOLEAN DEFAULT FALSE,
    weather_delay_hours DECIMAL(4,2),

    -- CREW
    crew_members JSONB DEFAULT '[]'::JSONB,  -- [{employee_id, hours, task}]
    total_man_hours DECIMAL(10,2),

    -- WORK PERFORMED
    work_description TEXT,
    areas_worked TEXT[],
    percent_complete_update DECIMAL(5,2),  -- Feeds SOV

    -- MATERIALS (Links to products)
    materials_installed JSONB DEFAULT '[]'::JSONB,  -- [{product_id, quantity, location}]

    -- EQUIPMENT
    equipment_used JSONB DEFAULT '[]'::JSONB,

    -- VISITORS/INSPECTIONS
    visitors JSONB DEFAULT '[]'::JSONB,

    -- ISSUES
    safety_incidents BOOLEAN DEFAULT FALSE,
    quality_issues TEXT,
    delays TEXT,

    photos JSONB DEFAULT '[]'::JSONB,
    notes TEXT,

    submitted_by UUID REFERENCES employees(employee_id),

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- STORED MATERIALS LOG - Links to SOV materials_stored
-- ============================================================================

CREATE TABLE IF NOT EXISTS stored_materials (
    stored_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    date_received DATE NOT NULL,
    product_id UUID REFERENCES products(product_id),
    description TEXT,
    quantity DECIMAL(12,2) NOT NULL,
    unit TEXT NOT NULL,
    unit_cost DECIMAL(10,2),
    total_value DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    location TEXT CHECK (location IN ('ground', 'roof', 'staging', 'installed', 'returned')),
    po_reference TEXT,
    photos JSONB DEFAULT '[]'::JSONB,
    status TEXT DEFAULT 'stored' CHECK (status IN ('stored', 'installed', 'returned', 'damaged')),

    -- When installed, updates SOV
    installed_date DATE,
    installed_daily_report_id UUID REFERENCES daily_reports(report_id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INSPECTIONS (Checklists auto-generated from system_type)
-- ============================================================================

CREATE TABLE IF NOT EXISTS inspections (
    inspection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    inspection_type TEXT NOT NULL CHECK (inspection_type IN (
        'pre_installation', 'progress', 'final', 'warranty', 'punch_list'
    )),
    inspection_date DATE NOT NULL,
    inspector_id UUID REFERENCES employees(employee_id),

    -- CHECKLIST (Auto-loaded based on job.system_type)
    checklist JSONB NOT NULL,  -- [{item, passed, notes, photo}]

    overall_result TEXT CHECK (overall_result IN ('pass', 'fail', 'conditional')),
    deficiencies_found INTEGER DEFAULT 0,

    photos JSONB DEFAULT '[]'::JSONB,
    notes TEXT,

    -- LINKS
    moisture_analysis_id UUID,
    penetration_log JSONB DEFAULT '[]'::JSONB,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PUNCH LIST (Auto-created from inspection deficiencies)
-- ============================================================================

CREATE TABLE IF NOT EXISTS punch_list_items (
    punch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES inspections(inspection_id),
    item_number INTEGER,
    description TEXT NOT NULL,
    location TEXT,
    spec_reference TEXT,
    assigned_to UUID REFERENCES employees(employee_id),
    priority TEXT CHECK (priority IN ('critical', 'high', 'medium', 'low')),

    due_date DATE,
    completed_date DATE,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'verified')),

    photos_before JSONB DEFAULT '[]'::JSONB,
    photos_after JSONB DEFAULT '[]'::JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SAFETY DOCUMENTS (JHA auto-generated from products.hazards)
-- ============================================================================

CREATE TABLE IF NOT EXISTS safety_documents (
    safety_doc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    doc_type TEXT NOT NULL CHECK (doc_type IN (
        'jha', 'toolbox_talk', 'incident_report', 'hot_work_permit',
        'fall_protection_plan', 'silica_control_plan', 'crane_lift_plan',
        'equipment_inspection'
    )),

    title TEXT NOT NULL,
    content JSONB NOT NULL,  -- Structured content based on doc_type

    date_created DATE DEFAULT CURRENT_DATE,
    date_effective DATE,
    date_expires DATE,

    -- SIGNATURES
    prepared_by UUID REFERENCES employees(employee_id),
    approved_by UUID REFERENCES employees(employee_id),
    attendees JSONB DEFAULT '[]'::JSONB,  -- For toolbox talks

    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'void')),

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,
    auto_populated_hazards JSONB DEFAULT '[]'::JSONB,  -- From products

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PAY APPLICATIONS (Auto-calculated from SOV + Daily Reports)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pay_applications (
    pay_app_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    application_number INTEGER NOT NULL,
    period_from DATE NOT NULL,
    period_to DATE NOT NULL,

    -- G702 FIELDS (All calculated from SSOT)
    original_contract_sum DECIMAL(12,2),
    change_orders_approved DECIMAL(12,2),
    contract_sum_to_date DECIMAL(12,2),
    total_completed_stored DECIMAL(12,2),  -- From SOV
    retainage_percent DECIMAL(5,2),
    retainage_amount DECIMAL(12,2),
    total_earned_less_retainage DECIMAL(12,2),
    less_previous_payments DECIMAL(12,2),
    current_payment_due DECIMAL(12,2),

    -- STATUS
    submitted_date DATE,
    approved_date DATE,
    paid_date DATE,
    paid_amount DECIMAL(12,2),
    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft', 'submitted', 'under_review', 'approved', 'paid', 'disputed'
    )),

    -- LINKED LIEN WAIVERS
    conditional_waiver_id UUID,
    unconditional_waiver_id UUID,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- LIEN WAIVERS
-- ============================================================================

CREATE TABLE IF NOT EXISTS lien_waivers (
    waiver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    pay_app_id UUID REFERENCES pay_applications(pay_app_id),
    waiver_type TEXT NOT NULL CHECK (waiver_type IN (
        'conditional_progress', 'unconditional_progress',
        'conditional_final', 'unconditional_final'
    )),

    amount DECIMAL(12,2) NOT NULL,
    through_date DATE NOT NULL,

    signed_date DATE,
    signed_by TEXT,
    notarized BOOLEAN DEFAULT FALSE,
    notary_date DATE,

    pdf_url TEXT,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CLOSEOUT DOCUMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS closeout_documents (
    closeout_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    doc_type TEXT NOT NULL CHECK (doc_type IN (
        'warranty_application', 'warranty_letter', 'as_built_drawings',
        'operations_manual', 'maintenance_schedule', 'test_reports',
        'certificate_of_completion', 'final_lien_waiver', 'other'
    )),

    title TEXT NOT NULL,
    description TEXT,

    -- MANUFACTURER WARRANTY
    manufacturer TEXT,
    warranty_number TEXT,
    warranty_years INTEGER,
    warranty_start_date DATE,
    warranty_end_date DATE,

    file_url TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'submitted', 'received', 'filed'
    )),

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INSURANCE SUPPLEMENTS (For Insurance Claims)
-- ============================================================================

CREATE TABLE IF NOT EXISTS insurance_supplements (
    supplement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    original_estimate_id UUID REFERENCES estimates(estimate_id),

    missed_items JSONB DEFAULT '[]'::JSONB,  -- Items not in original scope
    code_upgrades JSONB DEFAULT '[]'::JSONB,  -- Required by current code

    adjuster_contact_id UUID REFERENCES contacts(contact_id),

    amount_requested DECIMAL(12,2),
    amount_approved DECIMAL(12,2),

    documentation JSONB DEFAULT '[]'::JSONB,  -- Photos, code refs
    adjuster_notes TEXT,

    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft', 'submitted', 'under_review', 'approved', 'denied', 'appealed'
    )),

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PERMITS
-- ============================================================================

CREATE TABLE IF NOT EXISTS permits (
    permit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    permit_type TEXT NOT NULL CHECK (permit_type IN (
        'building', 'roofing', 'mechanical', 'electrical', 'demolition', 'other'
    )),

    municipality TEXT NOT NULL,
    permit_number TEXT,

    application_date DATE,
    approval_date DATE,
    expiration_date DATE,

    fee_amount DECIMAL(10,2),
    fee_paid BOOLEAN DEFAULT FALSE,

    inspection_schedule JSONB DEFAULT '[]'::JSONB,

    status TEXT DEFAULT 'not_applied' CHECK (status IN (
        'not_applied', 'application_submitted', 'approved', 'expired', 'closed'
    )),

    -- AUTO-FILLED FROM PROJECT + ESTIMATE
    auto_filled_data JSONB,

    -- AI TRACKING
    ai_generated BOOLEAN DEFAULT FALSE,
    confidence_score INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DRAWINGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS drawings (
    drawing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    number TEXT NOT NULL,
    title TEXT NOT NULL,
    revision TEXT DEFAULT 'A',
    revision_date DATE,

    is_as_built BOOLEAN DEFAULT FALSE,

    file_url TEXT,
    file_type TEXT CHECK (file_type IN ('dwg', 'dxf', 'pdf', 'other')),

    redlines JSONB DEFAULT '[]'::JSONB,  -- Field changes

    linked_rfis UUID[] DEFAULT '{}',
    linked_submittals UUID[] DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- AI POSITION CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS position_config (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    position TEXT NOT NULL CHECK (position IN (
        'estimator', 'project_manager', 'detailer', 'spec_writer',
        'qc_inspector', 'safety_officer', 'superintendent', 'accounts'
    )),

    mode TEXT NOT NULL CHECK (mode IN ('off', 'assist', 'full_ai')),

    -- CONFIDENCE SETTINGS
    confidence_threshold INTEGER DEFAULT 90,  -- Auto-pause below this

    -- ASSIGNED HUMAN (for assist mode)
    assigned_employee_id UUID REFERENCES employees(employee_id),

    -- STATISTICS
    total_actions INTEGER DEFAULT 0,
    actions_auto_completed INTEGER DEFAULT 0,
    actions_flagged INTEGER DEFAULT 0,
    average_confidence DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(company_id, position)
);

-- ============================================================================
-- AI ACTION LOG
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_action_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(project_id),
    job_id UUID REFERENCES jobs(job_id),

    position TEXT NOT NULL,
    action_type TEXT NOT NULL,  -- 'create_rfi', 'generate_pay_app', etc

    trigger_event TEXT,  -- What caused this action

    confidence_score INTEGER NOT NULL,
    confidence_factors JSONB,  -- {data_completeness: 95, consistency: 90, ...}

    status TEXT NOT NULL CHECK (status IN (
        'completed', 'paused', 'human_review', 'failed'
    )),

    input_data JSONB,
    output_data JSONB,

    paused_reason TEXT,
    reviewed_by UUID REFERENCES employees(employee_id),
    review_date TIMESTAMPTZ,
    review_action TEXT,  -- 'approved', 'edited', 'rejected'

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_projects_company ON projects(company_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_estimates_project ON estimates(project_id);
CREATE INDEX idx_jobs_project ON jobs(project_id);
CREATE INDEX idx_sov_job ON schedule_of_values(job_id);
CREATE INDEX idx_submittals_job ON submittals(job_id);
CREATE INDEX idx_submittals_status ON submittals(status);
CREATE INDEX idx_rfis_job ON rfis(job_id);
CREATE INDEX idx_change_orders_job ON change_orders(job_id);
CREATE INDEX idx_daily_reports_job ON daily_reports(job_id);
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
CREATE INDEX idx_inspections_job ON inspections(job_id);
CREATE INDEX idx_pay_apps_job ON pay_applications(job_id);
CREATE INDEX idx_ai_log_company ON ai_action_log(company_id);
CREATE INDEX idx_ai_log_status ON ai_action_log(status);

-- ============================================================================
-- TRIGGERS FOR SSOT PROPAGATION
-- ============================================================================

-- Trigger: Update estimate totals when line items change
CREATE OR REPLACE FUNCTION update_estimate_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE estimates SET
        subtotal_materials = (SELECT COALESCE(SUM(material_total), 0) FROM estimate_line_items WHERE estimate_id = NEW.estimate_id),
        subtotal_labor = (SELECT COALESCE(SUM(labor_total), 0) FROM estimate_line_items WHERE estimate_id = NEW.estimate_id),
        updated_at = NOW()
    WHERE estimate_id = NEW.estimate_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_estimate_line_items
AFTER INSERT OR UPDATE OR DELETE ON estimate_line_items
FOR EACH ROW EXECUTE FUNCTION update_estimate_totals();

-- Trigger: Update SOV when daily reports update progress
CREATE OR REPLACE FUNCTION update_sov_from_daily_report()
RETURNS TRIGGER AS $$
BEGIN
    -- Update SOV percent complete based on daily report
    -- This is a simplified version - actual implementation would be more complex
    IF NEW.percent_complete_update IS NOT NULL THEN
        UPDATE schedule_of_values SET
            percent_complete = NEW.percent_complete_update,
            updated_at = NOW()
        WHERE job_id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_daily_report_sov
AFTER INSERT OR UPDATE ON daily_reports
FOR EACH ROW EXECUTE FUNCTION update_sov_from_daily_report();

-- Trigger: Update job change_orders_total when COs approved
CREATE OR REPLACE FUNCTION update_job_co_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE jobs SET
        change_orders_total = (
            SELECT COALESCE(SUM(total), 0)
            FROM change_orders
            WHERE job_id = NEW.job_id AND status = 'approved'
        ),
        updated_at = NOW()
    WHERE job_id = NEW.job_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_change_order_approved
AFTER INSERT OR UPDATE ON change_orders
FOR EACH ROW EXECUTE FUNCTION update_job_co_total();
