-- ============================================================================
-- ROOFIO DATABASE SCHEMA
-- PostgreSQL + Supabase Real-time Architecture
-- Version: 1.0.0
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gist";  -- For range queries

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Organizations (Companies using ROOFIO)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'starter', -- starter, professional, enterprise
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMPTZ,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    role VARCHAR(50) DEFAULT 'user', -- admin, manager, user, field
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- PROJECT MANAGEMENT TABLES
-- ============================================================================

-- Clients / General Contractors
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    company_type VARCHAR(50), -- gc, owner, architect, consultant
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(255),
    payment_terms INTEGER DEFAULT 30, -- days
    payment_history_score DECIMAL(3,2) DEFAULT 5.00, -- 1-5 rating
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_clients_org ON clients(organization_id);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    number VARCHAR(50), -- Project number
    description TEXT,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Project Details
    project_type VARCHAR(50), -- new_construction, reroof, repair, waterproofing
    building_type VARCHAR(50), -- commercial, industrial, institutional, residential
    roof_type VARCHAR(50), -- tpo, epdm, bur, modified, metal, shingle
    total_sf INTEGER,

    -- Financial
    contract_value DECIMAL(12, 2),
    estimated_cost DECIMAL(12, 2),
    actual_cost DECIMAL(12, 2) DEFAULT 0,
    profit_margin DECIMAL(5, 2),

    -- Schedule
    bid_date DATE,
    award_date DATE,
    start_date DATE,
    estimated_completion DATE,
    actual_completion DATE,
    schedule_variance_days INTEGER DEFAULT 0,

    -- Status
    phase VARCHAR(50) DEFAULT 'bidding', -- bidding, awarded, mobilization, in_progress, punch_list, complete, closed
    health_score DECIMAL(3, 2) DEFAULT 5.00, -- 1-5 rating
    status_color VARCHAR(20) DEFAULT 'green', -- green, yellow, red

    -- Assignments
    project_manager_id UUID REFERENCES users(id),
    superintendent_id UUID REFERENCES users(id),
    estimator_id UUID REFERENCES users(id),

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_org ON projects(organization_id);
CREATE INDEX idx_projects_client ON projects(client_id);
CREATE INDEX idx_projects_phase ON projects(phase);
CREATE INDEX idx_projects_status ON projects(status_color);

-- ============================================================================
-- ESTIMATOR MODULE TABLES
-- ============================================================================

-- Estimates
CREATE TABLE estimates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Basic Info
    estimate_number VARCHAR(50),
    name VARCHAR(255),
    description TEXT,
    version INTEGER DEFAULT 1,

    -- Measurement Data
    total_sf INTEGER,
    roof_perimeter_lf INTEGER,
    measurement_source VARCHAR(50), -- manual, eagleview, roofsnap, hover
    measurement_data JSONB, -- Raw measurement data

    -- Pricing
    material_cost DECIMAL(12, 2) DEFAULT 0,
    labor_cost DECIMAL(12, 2) DEFAULT 0,
    equipment_cost DECIMAL(12, 2) DEFAULT 0,
    overhead_cost DECIMAL(12, 2) DEFAULT 0,
    profit_amount DECIMAL(12, 2) DEFAULT 0,
    contingency_amount DECIMAL(12, 2) DEFAULT 0,
    total_price DECIMAL(12, 2) DEFAULT 0,

    -- Bid Details
    bid_due_date DATE,
    validity_days INTEGER DEFAULT 30,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, pending_review, submitted, won, lost
    win_probability DECIMAL(3, 2), -- AI-calculated 0-1

    -- Outcome (for learning)
    outcome VARCHAR(50), -- won, lost, no_bid, cancelled
    outcome_reason TEXT,
    winning_amount DECIMAL(12, 2), -- If lost, what was winning bid

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ
);

CREATE INDEX idx_estimates_org ON estimates(organization_id);
CREATE INDEX idx_estimates_project ON estimates(project_id);
CREATE INDEX idx_estimates_status ON estimates(status);

-- Estimate Line Items
CREATE TABLE estimate_line_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estimate_id UUID REFERENCES estimates(id) ON DELETE CASCADE,

    -- Item Details
    cost_code VARCHAR(50),
    description TEXT NOT NULL,
    category VARCHAR(100), -- material, labor, equipment, subcontractor, other

    -- Quantities
    quantity DECIMAL(12, 2),
    unit VARCHAR(50), -- sf, lf, ea, sq, hr, day

    -- Pricing
    unit_cost DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    total_cost DECIMAL(12, 2),
    total_price DECIMAL(12, 2),

    -- Labor
    labor_hours DECIMAL(8, 2),
    labor_rate DECIMAL(8, 2),
    productivity_factor DECIMAL(4, 2) DEFAULT 1.00, -- Adjustment for conditions

    -- Metadata
    sort_order INTEGER DEFAULT 0,
    is_alternate BOOLEAN DEFAULT FALSE,
    alternate_group VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_estimate_items_estimate ON estimate_line_items(estimate_id);

-- Material Price History (for tracking volatility)
CREATE TABLE material_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    material_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    sku VARCHAR(100),

    unit VARCHAR(50),
    price DECIMAL(10, 2),
    vendor_id UUID,

    effective_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_material_prices_org ON material_prices(organization_id);
CREATE INDEX idx_material_prices_name ON material_prices(material_name);
CREATE INDEX idx_material_prices_date ON material_prices(effective_date);

-- ============================================================================
-- SUPERINTENDENT / DAILY LOGS MODULE
-- ============================================================================

-- Daily Logs
CREATE TABLE daily_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Basic Info
    log_date DATE NOT NULL,
    weather_conditions JSONB, -- temp, conditions, wind, humidity

    -- Work Summary
    work_performed TEXT,
    areas_worked TEXT[],
    sf_completed INTEGER DEFAULT 0,

    -- Crew Info
    crew_count INTEGER DEFAULT 0,
    total_man_hours DECIMAL(8, 2) DEFAULT 0,

    -- Delays
    has_delay BOOLEAN DEFAULT FALSE,
    delay_type VARCHAR(50), -- weather, gc, material, owner, other
    delay_hours DECIMAL(4, 2),
    delay_days INTEGER,
    delay_reason TEXT,

    -- Materials
    materials_received TEXT[],
    materials_needed TEXT[],

    -- Equipment
    equipment_on_site TEXT[],

    -- Visitors
    visitors JSONB[], -- [{name, company, time_in, time_out}]

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, approved

    -- Metadata
    created_by UUID REFERENCES users(id),
    submitted_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_daily_logs_org ON daily_logs(organization_id);
CREATE INDEX idx_daily_logs_project ON daily_logs(project_id);
CREATE INDEX idx_daily_logs_date ON daily_logs(log_date);
CREATE UNIQUE INDEX idx_daily_logs_unique ON daily_logs(project_id, log_date);

-- Crew Time Entries
CREATE TABLE time_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    daily_log_id UUID REFERENCES daily_logs(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    employee_name VARCHAR(255) NOT NULL,
    employee_id VARCHAR(50),

    work_date DATE NOT NULL,
    clock_in TIMESTAMPTZ,
    clock_out TIMESTAMPTZ,
    regular_hours DECIMAL(4, 2) DEFAULT 0,
    overtime_hours DECIMAL(4, 2) DEFAULT 0,

    cost_code VARCHAR(50),
    work_description TEXT,

    -- GPS Data
    clock_in_location POINT,
    clock_out_location POINT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_time_entries_org ON time_entries(organization_id);
CREATE INDEX idx_time_entries_project ON time_entries(project_id);
CREATE INDEX idx_time_entries_date ON time_entries(work_date);

-- ============================================================================
-- QC MODULE TABLES
-- ============================================================================

-- Inspections
CREATE TABLE inspections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Basic Info
    inspection_type VARCHAR(100) NOT NULL, -- progress, quality, final, manufacturer
    inspection_date DATE NOT NULL,
    location_description TEXT,

    -- Checklist
    checklist_template_id UUID,
    checklist_items JSONB, -- [{item, passed, notes, photo_ids}]
    items_passed INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    items_na INTEGER DEFAULT 0,

    -- Results
    overall_result VARCHAR(50), -- pass, fail, conditional
    quality_score DECIMAL(3, 2), -- 1-5

    -- Follow-up
    defects_found INTEGER DEFAULT 0,
    corrective_actions_required TEXT,
    reinspection_date DATE,

    -- Metadata
    inspector_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_inspections_org ON inspections(organization_id);
CREATE INDEX idx_inspections_project ON inspections(project_id);

-- Punch List Items
CREATE TABLE punch_list_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES inspections(id),

    -- Item Details
    item_number INTEGER,
    description TEXT NOT NULL,
    location TEXT,
    category VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'normal', -- low, normal, high, critical

    -- Assignment
    assigned_to VARCHAR(255),
    assigned_crew VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, completed, verified
    due_date DATE,
    completed_date DATE,
    verified_by UUID REFERENCES users(id),
    verified_date DATE,

    -- Photos
    defect_photo_ids UUID[],
    completion_photo_ids UUID[],

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_punch_list_org ON punch_list_items(organization_id);
CREATE INDEX idx_punch_list_project ON punch_list_items(project_id);
CREATE INDEX idx_punch_list_status ON punch_list_items(status);

-- ============================================================================
-- SAFETY MODULE TABLES
-- ============================================================================

-- JHAs (Job Hazard Analysis)
CREATE TABLE jhas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    -- Basic Info
    jha_number VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    work_activity TEXT,
    location TEXT,

    -- Conditions
    date_created DATE DEFAULT CURRENT_DATE,
    weather_conditions JSONB,
    site_conditions JSONB, -- roof_pitch, access, hazards

    -- Analysis
    hazards JSONB[], -- [{hazard, risk_level, controls, ppe_required}]

    -- Sign-off
    supervisor_id UUID REFERENCES users(id),
    supervisor_signed_at TIMESTAMPTZ,
    crew_signatures JSONB[], -- [{name, signed_at}]

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, archived
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_jhas_org ON jhas(organization_id);
CREATE INDEX idx_jhas_project ON jhas(project_id);

-- Safety Incidents
CREATE TABLE safety_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    -- Incident Details
    incident_date DATE NOT NULL,
    incident_time TIME,
    incident_type VARCHAR(100), -- injury, near_miss, property_damage, environmental
    severity VARCHAR(50), -- first_aid, recordable, lost_time, fatality

    -- Description
    description TEXT NOT NULL,
    immediate_cause TEXT,
    root_cause TEXT,

    -- People Involved
    injured_party_name VARCHAR(255),
    injured_party_type VARCHAR(50), -- employee, subcontractor, visitor
    witnesses JSONB[],

    -- Treatment
    treatment_provided TEXT,
    medical_facility VARCHAR(255),
    days_away INTEGER DEFAULT 0,
    days_restricted INTEGER DEFAULT 0,

    -- Investigation
    investigation_status VARCHAR(50) DEFAULT 'pending',
    investigator_id UUID REFERENCES users(id),
    corrective_actions JSONB[],

    -- OSHA Reporting
    osha_recordable BOOLEAN DEFAULT FALSE,
    osha_reported BOOLEAN DEFAULT FALSE,
    osha_report_date DATE,

    -- Metadata
    reported_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_incidents_org ON safety_incidents(organization_id);
CREATE INDEX idx_incidents_project ON safety_incidents(project_id);
CREATE INDEX idx_incidents_date ON safety_incidents(incident_date);

-- Certifications
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),

    employee_name VARCHAR(255),
    certification_type VARCHAR(100) NOT NULL, -- osha_10, osha_30, fall_protection, first_aid, etc
    certification_number VARCHAR(100),

    issued_date DATE,
    expiration_date DATE,

    document_url TEXT,

    -- Alerts
    reminder_sent_30_days BOOLEAN DEFAULT FALSE,
    reminder_sent_60_days BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_certifications_org ON certifications(organization_id);
CREATE INDEX idx_certifications_expiry ON certifications(expiration_date);

-- ============================================================================
-- ACCOUNTING MODULE TABLES
-- ============================================================================

-- Schedule of Values
CREATE TABLE schedule_of_values (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    line_number INTEGER,
    description TEXT NOT NULL,
    scheduled_value DECIMAL(12, 2) NOT NULL,

    -- Progress
    previous_completed DECIMAL(12, 2) DEFAULT 0,
    this_period DECIMAL(12, 2) DEFAULT 0,
    materials_stored DECIMAL(12, 2) DEFAULT 0,
    total_completed DECIMAL(12, 2) DEFAULT 0,
    percent_complete DECIMAL(5, 2) DEFAULT 0,
    balance_to_finish DECIMAL(12, 2),

    -- Retainage
    retainage_percent DECIMAL(5, 2) DEFAULT 10.00,
    retainage_amount DECIMAL(12, 2) DEFAULT 0,

    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sov_project ON schedule_of_values(project_id);

-- Invoices / Pay Applications
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Invoice Details
    invoice_number VARCHAR(50) NOT NULL,
    invoice_type VARCHAR(50) DEFAULT 'progress', -- progress, final, retention, change_order
    application_number INTEGER, -- For AIA billing

    -- Period
    period_from DATE,
    period_to DATE,

    -- Amounts
    contract_amount DECIMAL(12, 2),
    change_orders_amount DECIMAL(12, 2) DEFAULT 0,
    revised_contract DECIMAL(12, 2),

    previous_billed DECIMAL(12, 2) DEFAULT 0,
    current_billed DECIMAL(12, 2),
    total_billed DECIMAL(12, 2),

    retainage_held DECIMAL(12, 2) DEFAULT 0,
    retainage_released DECIMAL(12, 2) DEFAULT 0,

    amount_due DECIMAL(12, 2),

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, approved, paid, disputed

    -- Dates
    submitted_date DATE,
    due_date DATE,
    paid_date DATE,
    paid_amount DECIMAL(12, 2),

    -- Documents
    pdf_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoices_org ON invoices(organization_id);
CREATE INDEX idx_invoices_project ON invoices(project_id);
CREATE INDEX idx_invoices_status ON invoices(status);

-- Change Orders
CREATE TABLE change_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- CO Details
    co_number INTEGER,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reason VARCHAR(100), -- owner_request, unforeseen, design_change, value_engineering

    -- Amounts
    material_cost DECIMAL(10, 2) DEFAULT 0,
    labor_cost DECIMAL(10, 2) DEFAULT 0,
    equipment_cost DECIMAL(10, 2) DEFAULT 0,
    markup_percent DECIMAL(5, 2) DEFAULT 15.00,
    markup_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2),

    -- Schedule Impact
    days_added INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, submitted, approved, rejected, incorporated

    -- Dates
    submitted_date DATE,
    approved_date DATE,
    approved_by VARCHAR(255),

    -- Supporting Docs
    supporting_documents JSONB[],

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_change_orders_org ON change_orders(organization_id);
CREATE INDEX idx_change_orders_project ON change_orders(project_id);

-- Lien Waivers
CREATE TABLE lien_waivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id),

    waiver_type VARCHAR(50), -- conditional_progress, unconditional_progress, conditional_final, unconditional_final

    through_date DATE,
    amount DECIMAL(12, 2),

    status VARCHAR(50) DEFAULT 'pending', -- pending, signed, received

    signed_date DATE,
    document_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lien_waivers_project ON lien_waivers(project_id);

-- ============================================================================
-- OPERATIONS MODULE TABLES
-- ============================================================================

-- Vendors / Suppliers
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(50), -- distributor, manufacturer, subcontractor, rental

    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),

    contact_name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),

    -- Performance
    on_time_delivery_rate DECIMAL(5, 2),
    quality_score DECIMAL(3, 2),
    price_competitiveness_score DECIMAL(3, 2),
    overall_score DECIMAL(3, 2),

    payment_terms INTEGER DEFAULT 30,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vendors_org ON vendors(organization_id);

-- Purchase Orders
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),
    vendor_id UUID REFERENCES vendors(id),

    po_number VARCHAR(50) NOT NULL,

    -- Order Details
    order_date DATE DEFAULT CURRENT_DATE,
    required_date DATE,

    -- Amounts
    subtotal DECIMAL(12, 2) DEFAULT 0,
    tax DECIMAL(10, 2) DEFAULT 0,
    shipping DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(12, 2) DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, confirmed, shipped, received, cancelled

    -- Delivery
    delivery_address TEXT,
    delivery_instructions TEXT,

    -- Tracking
    shipped_date DATE,
    tracking_number VARCHAR(100),
    received_date DATE,
    received_by UUID REFERENCES users(id),

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_purchase_orders_org ON purchase_orders(organization_id);
CREATE INDEX idx_purchase_orders_project ON purchase_orders(project_id);
CREATE INDEX idx_purchase_orders_vendor ON purchase_orders(vendor_id);

-- Purchase Order Line Items
CREATE TABLE po_line_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_order_id UUID REFERENCES purchase_orders(id) ON DELETE CASCADE,

    description TEXT NOT NULL,
    sku VARCHAR(100),
    quantity DECIMAL(10, 2),
    unit VARCHAR(50),
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(12, 2),

    quantity_received DECIMAL(10, 2) DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_po_items_po ON po_line_items(purchase_order_id);

-- Inventory
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    item_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    category VARCHAR(100),

    quantity_on_hand DECIMAL(10, 2) DEFAULT 0,
    unit VARCHAR(50),

    reorder_point DECIMAL(10, 2),
    reorder_quantity DECIMAL(10, 2),

    location VARCHAR(255), -- warehouse, yard, etc

    last_count_date DATE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inventory_org ON inventory(organization_id);

-- ============================================================================
-- SHOP DRAWINGS MODULE TABLES
-- ============================================================================

-- Shop Drawings
CREATE TABLE shop_drawings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Drawing Info
    drawing_number VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    drawing_type VARCHAR(100), -- detail, assembly, layout, section
    category VARCHAR(100), -- flashing, membrane, penetration, edge, drain

    -- Version Control
    current_version INTEGER DEFAULT 1,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, internal_review, submitted, approved, rejected, revised

    -- Submittal Info
    submittal_number VARCHAR(50),
    submitted_date DATE,
    required_date DATE,
    approved_date DATE,
    approved_by VARCHAR(255),
    approval_comments TEXT,

    -- File
    file_url TEXT,
    file_type VARCHAR(50), -- pdf, dwg, dxf
    thumbnail_url TEXT,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_shop_drawings_org ON shop_drawings(organization_id);
CREATE INDEX idx_shop_drawings_project ON shop_drawings(project_id);

-- Drawing Revisions
CREATE TABLE drawing_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_drawing_id UUID REFERENCES shop_drawings(id) ON DELETE CASCADE,

    version INTEGER NOT NULL,
    revision_reason TEXT,
    changes_description TEXT,

    file_url TEXT,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_revisions_drawing ON drawing_revisions(shop_drawing_id);

-- RFIs
CREATE TABLE rfis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    rfi_number INTEGER,
    subject VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,

    -- Spec Reference
    spec_section VARCHAR(50),
    drawing_reference VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, answered, closed
    priority VARCHAR(50) DEFAULT 'normal', -- low, normal, high, critical

    -- Dates
    submitted_date DATE,
    due_date DATE,
    answered_date DATE,

    -- Response
    response TEXT,
    responded_by VARCHAR(255),

    -- Impact
    cost_impact DECIMAL(10, 2),
    schedule_impact_days INTEGER,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rfis_org ON rfis(organization_id);
CREATE INDEX idx_rfis_project ON rfis(project_id);

-- ============================================================================
-- DOCUMENTS & PHOTOS
-- ============================================================================

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    -- File Info
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_url TEXT NOT NULL,

    -- Classification
    document_type VARCHAR(100), -- contract, spec, drawing, photo, submittal, correspondence
    category VARCHAR(100),

    -- Metadata
    description TEXT,
    tags TEXT[],

    -- Related Records
    related_type VARCHAR(50), -- daily_log, inspection, change_order, etc
    related_id UUID,

    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_org ON documents(organization_id);
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Photos (specialized for construction)
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id),

    -- File Info
    file_url TEXT NOT NULL,
    thumbnail_url TEXT,

    -- Photo Details
    taken_at TIMESTAMPTZ DEFAULT NOW(),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Classification
    photo_type VARCHAR(100), -- progress, defect, safety, before_after, closeout
    location_on_roof TEXT,

    -- Annotations
    annotations JSONB, -- Drawing annotations

    -- AI Analysis
    ai_analysis JSONB, -- Defect detection results

    -- Metadata
    description TEXT,
    tags TEXT[],

    -- Related Records
    daily_log_id UUID REFERENCES daily_logs(id),
    inspection_id UUID REFERENCES inspections(id),
    punch_list_item_id UUID REFERENCES punch_list_items(id),

    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_photos_org ON photos(organization_id);
CREATE INDEX idx_photos_project ON photos(project_id);
CREATE INDEX idx_photos_type ON photos(photo_type);

-- ============================================================================
-- CROSS-MODULE EVENT SYSTEM
-- ============================================================================

-- Event Log (for cross-module triggers and audit)
CREATE TABLE event_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    event_type VARCHAR(100) NOT NULL, -- weather_delay, defect_found, invoice_overdue, etc
    event_source VARCHAR(100), -- Which module generated

    -- Related Records
    project_id UUID REFERENCES projects(id),
    source_table VARCHAR(100),
    source_id UUID,

    -- Event Data
    payload JSONB NOT NULL,

    -- Cascade Actions Taken
    actions_triggered JSONB[], -- [{action, target, result}]

    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_event_log_org ON event_log(organization_id);
CREATE INDEX idx_event_log_type ON event_log(event_type);
CREATE INDEX idx_event_log_project ON event_log(project_id);
CREATE INDEX idx_event_log_processed ON event_log(processed);

-- Notification Queue
CREATE TABLE notification_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    notification_type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'normal', -- low, normal, high, urgent

    -- Recipients
    recipients UUID[], -- User IDs

    -- Content
    title VARCHAR(255),
    message TEXT,
    payload JSONB,

    -- Related
    project_id UUID REFERENCES projects(id),

    -- Delivery
    channels VARCHAR(50)[] DEFAULT ARRAY['in_app'], -- in_app, email, sms, push

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    sent_at TIMESTAMPTZ,
    error_message TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_org ON notification_queue(organization_id);
CREATE INDEX idx_notifications_status ON notification_queue(status);

-- Delay Claims Log (for documentation)
CREATE TABLE delay_claims_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    delay_type VARCHAR(50) NOT NULL, -- weather, gc_caused, owner_directed, unforeseen
    delay_days INTEGER NOT NULL,
    cause TEXT,

    -- Supporting Data
    weather_data JSONB,
    daily_log_ids UUID[],
    photo_ids UUID[],
    document_ids UUID[],

    -- Status
    claim_status VARCHAR(50) DEFAULT 'documented', -- documented, submitted, approved, denied

    logged_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_delay_claims_project ON delay_claims_log(project_id);

-- ============================================================================
-- CROSS-MODULE INTELLIGENCE TRIGGERS
-- ============================================================================

-- Function to recalculate project health score
CREATE OR REPLACE FUNCTION recalculate_project_health(p_project_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_schedule_score DECIMAL;
    v_budget_score DECIMAL;
    v_quality_score DECIMAL;
    v_safety_score DECIMAL;
    v_health_score DECIMAL;
BEGIN
    -- Schedule Score (based on variance)
    SELECT CASE
        WHEN schedule_variance_days <= 0 THEN 5.0
        WHEN schedule_variance_days <= 5 THEN 4.0
        WHEN schedule_variance_days <= 10 THEN 3.0
        WHEN schedule_variance_days <= 20 THEN 2.0
        ELSE 1.0
    END INTO v_schedule_score
    FROM projects WHERE id = p_project_id;

    -- Budget Score (based on cost vs estimate)
    SELECT CASE
        WHEN actual_cost <= estimated_cost THEN 5.0
        WHEN actual_cost <= estimated_cost * 1.05 THEN 4.0
        WHEN actual_cost <= estimated_cost * 1.10 THEN 3.0
        WHEN actual_cost <= estimated_cost * 1.20 THEN 2.0
        ELSE 1.0
    END INTO v_budget_score
    FROM projects WHERE id = p_project_id;

    -- Quality Score (based on recent inspections)
    SELECT COALESCE(AVG(quality_score), 4.0) INTO v_quality_score
    FROM inspections
    WHERE project_id = p_project_id
    AND completed_at > NOW() - INTERVAL '30 days';

    -- Safety Score (based on incidents)
    SELECT CASE
        WHEN COUNT(*) = 0 THEN 5.0
        WHEN COUNT(*) = 1 THEN 3.0
        ELSE 1.0
    END INTO v_safety_score
    FROM safety_incidents
    WHERE project_id = p_project_id
    AND incident_date > NOW() - INTERVAL '90 days';

    -- Calculate weighted average
    v_health_score := (v_schedule_score * 0.3 + v_budget_score * 0.3 + v_quality_score * 0.25 + v_safety_score * 0.15);

    -- Update project
    UPDATE projects
    SET
        health_score = v_health_score,
        status_color = CASE
            WHEN v_health_score >= 4.0 THEN 'green'
            WHEN v_health_score >= 3.0 THEN 'yellow'
            ELSE 'red'
        END,
        updated_at = NOW()
    WHERE id = p_project_id;

    RETURN v_health_score;
END;
$$ LANGUAGE plpgsql;

-- Weather Delay Cascade Trigger
CREATE OR REPLACE FUNCTION propagate_weather_delay()
RETURNS TRIGGER AS $$
DECLARE
    v_project_id UUID;
    v_delay_days INTEGER;
    v_new_completion DATE;
BEGIN
    IF NEW.has_delay = TRUE AND NEW.delay_type = 'weather' THEN
        v_project_id := NEW.project_id;
        v_delay_days := COALESCE(NEW.delay_days, 1);

        -- 1. UPDATE PROJECT SCHEDULE
        UPDATE projects
        SET
            estimated_completion = estimated_completion + (v_delay_days || ' days')::INTERVAL,
            schedule_variance_days = schedule_variance_days + v_delay_days,
            updated_at = NOW()
        WHERE id = v_project_id
        RETURNING estimated_completion INTO v_new_completion;

        -- 2. UPDATE BILLING SCHEDULE
        UPDATE invoices
        SET due_date = due_date + (v_delay_days || ' days')::INTERVAL
        WHERE project_id = v_project_id
        AND status IN ('draft', 'submitted');

        -- 3. LOG FOR CLAIMS
        INSERT INTO delay_claims_log (
            organization_id,
            project_id,
            delay_type,
            delay_days,
            cause,
            weather_data,
            daily_log_ids,
            logged_by
        ) VALUES (
            NEW.organization_id,
            v_project_id,
            'weather',
            v_delay_days,
            NEW.delay_reason,
            NEW.weather_conditions,
            ARRAY[NEW.id],
            NEW.created_by
        );

        -- 4. UPDATE PROJECT HEALTH
        PERFORM recalculate_project_health(v_project_id);

        -- 5. CREATE EVENT LOG
        INSERT INTO event_log (
            organization_id,
            event_type,
            event_source,
            project_id,
            source_table,
            source_id,
            payload
        ) VALUES (
            NEW.organization_id,
            'weather_delay',
            'daily_log',
            v_project_id,
            'daily_logs',
            NEW.id,
            jsonb_build_object(
                'delay_days', v_delay_days,
                'new_completion', v_new_completion,
                'weather', NEW.weather_conditions
            )
        );

        -- 6. QUEUE NOTIFICATIONS
        INSERT INTO notification_queue (
            organization_id,
            notification_type,
            priority,
            recipients,
            title,
            message,
            project_id,
            channels
        )
        SELECT
            NEW.organization_id,
            'schedule_change',
            'high',
            ARRAY[p.project_manager_id, p.superintendent_id],
            'Weather Delay - ' || p.name,
            'Project delayed ' || v_delay_days || ' day(s). New completion: ' || v_new_completion,
            v_project_id,
            ARRAY['in_app', 'email']
        FROM projects p
        WHERE p.id = v_project_id;

        -- 7. SEND REAL-TIME NOTIFICATION
        PERFORM pg_notify('project_updates',
            jsonb_build_object(
                'type', 'weather_delay',
                'project_id', v_project_id,
                'delay_days', v_delay_days,
                'new_completion', v_new_completion
            )::text
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_delay_logged
    AFTER INSERT ON daily_logs
    FOR EACH ROW
    EXECUTE FUNCTION propagate_weather_delay();

-- QC Defect Found Cascade Trigger
CREATE OR REPLACE FUNCTION propagate_defect_found()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'open' THEN
        -- 1. Update project health
        PERFORM recalculate_project_health(NEW.project_id);

        -- 2. Log event
        INSERT INTO event_log (
            organization_id,
            event_type,
            event_source,
            project_id,
            source_table,
            source_id,
            payload
        ) VALUES (
            NEW.organization_id,
            'defect_found',
            'qc',
            NEW.project_id,
            'punch_list_items',
            NEW.id,
            jsonb_build_object(
                'description', NEW.description,
                'priority', NEW.priority,
                'location', NEW.location
            )
        );

        -- 3. Notify superintendent
        INSERT INTO notification_queue (
            organization_id,
            notification_type,
            priority,
            recipients,
            title,
            message,
            project_id
        )
        SELECT
            NEW.organization_id,
            'defect_found',
            CASE NEW.priority
                WHEN 'critical' THEN 'urgent'
                WHEN 'high' THEN 'high'
                ELSE 'normal'
            END,
            ARRAY[p.superintendent_id],
            'Defect Found - ' || p.name,
            NEW.description,
            NEW.project_id
        FROM projects p
        WHERE p.id = NEW.project_id;

        -- 4. Real-time notification
        PERFORM pg_notify('project_updates',
            jsonb_build_object(
                'type', 'defect_found',
                'project_id', NEW.project_id,
                'punch_list_id', NEW.id,
                'priority', NEW.priority
            )::text
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_punch_list_created
    AFTER INSERT ON punch_list_items
    FOR EACH ROW
    EXECUTE FUNCTION propagate_defect_found();

-- Invoice Overdue Cascade Trigger
CREATE OR REPLACE FUNCTION check_invoice_overdue()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'submitted' AND NEW.due_date < CURRENT_DATE THEN
        -- 1. Log event
        INSERT INTO event_log (
            organization_id,
            event_type,
            event_source,
            project_id,
            source_table,
            source_id,
            payload
        ) VALUES (
            NEW.organization_id,
            'invoice_overdue',
            'accounting',
            NEW.project_id,
            'invoices',
            NEW.id,
            jsonb_build_object(
                'invoice_number', NEW.invoice_number,
                'amount_due', NEW.amount_due,
                'days_overdue', CURRENT_DATE - NEW.due_date
            )
        );

        -- 2. Notify owner
        INSERT INTO notification_queue (
            organization_id,
            notification_type,
            priority,
            title,
            message,
            project_id
        )
        SELECT
            NEW.organization_id,
            'invoice_overdue',
            'high',
            'Invoice Overdue - ' || NEW.invoice_number,
            'Invoice for $' || NEW.amount_due || ' is ' || (CURRENT_DATE - NEW.due_date) || ' days overdue',
            NEW.project_id;

        PERFORM pg_notify('accounting_updates',
            jsonb_build_object(
                'type', 'invoice_overdue',
                'invoice_id', NEW.id,
                'amount_due', NEW.amount_due,
                'days_overdue', CURRENT_DATE - NEW.due_date
            )::text
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_invoice_update
    AFTER UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION check_invoice_overdue();

-- Safety Incident Cascade Trigger
CREATE OR REPLACE FUNCTION propagate_safety_incident()
RETURNS TRIGGER AS $$
BEGIN
    -- 1. Update project health
    IF NEW.project_id IS NOT NULL THEN
        PERFORM recalculate_project_health(NEW.project_id);
    END IF;

    -- 2. Log event
    INSERT INTO event_log (
        organization_id,
        event_type,
        event_source,
        project_id,
        source_table,
        source_id,
        payload
    ) VALUES (
        NEW.organization_id,
        'safety_incident',
        'safety',
        NEW.project_id,
        'safety_incidents',
        NEW.id,
        jsonb_build_object(
            'incident_type', NEW.incident_type,
            'severity', NEW.severity,
            'description', NEW.description
        )
    );

    -- 3. High-priority notification for recordable incidents
    IF NEW.osha_recordable = TRUE THEN
        INSERT INTO notification_queue (
            organization_id,
            notification_type,
            priority,
            title,
            message,
            project_id,
            channels
        ) VALUES (
            NEW.organization_id,
            'safety_incident',
            'urgent',
            'OSHA Recordable Incident',
            'A recordable safety incident has been reported. Immediate review required.',
            NEW.project_id,
            ARRAY['in_app', 'email', 'sms']
        );
    END IF;

    PERFORM pg_notify('safety_updates',
        jsonb_build_object(
            'type', 'incident_reported',
            'incident_id', NEW.id,
            'severity', NEW.severity,
            'project_id', NEW.project_id
        )::text
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_incident_created
    AFTER INSERT ON safety_incidents
    FOR EACH ROW
    EXECUTE FUNCTION propagate_safety_incident();

-- Submittal Approved Cascade Trigger
CREATE OR REPLACE FUNCTION propagate_submittal_approved()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status != 'approved' AND NEW.status = 'approved' THEN
        -- Log event
        INSERT INTO event_log (
            organization_id,
            event_type,
            event_source,
            project_id,
            source_table,
            source_id,
            payload
        ) VALUES (
            NEW.organization_id,
            'submittal_approved',
            'shop_drawings',
            NEW.project_id,
            'shop_drawings',
            NEW.id,
            jsonb_build_object(
                'drawing_number', NEW.drawing_number,
                'title', NEW.title,
                'approved_by', NEW.approved_by
            )
        );

        -- Notify operations to release material order
        INSERT INTO notification_queue (
            organization_id,
            notification_type,
            priority,
            title,
            message,
            project_id
        )
        SELECT
            NEW.organization_id,
            'submittal_approved',
            'normal',
            'Submittal Approved - ' || NEW.drawing_number,
            'Drawing ' || NEW.title || ' approved. Ready to order materials.',
            NEW.project_id;

        PERFORM pg_notify('operations_updates',
            jsonb_build_object(
                'type', 'submittal_approved',
                'project_id', NEW.project_id,
                'drawing_id', NEW.id
            )::text
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_drawing_status_change
    AFTER UPDATE ON shop_drawings
    FOR EACH ROW
    EXECUTE FUNCTION propagate_submittal_approved();

-- ============================================================================
-- VIEWS FOR DASHBOARD
-- ============================================================================

-- Project Summary View
CREATE OR REPLACE VIEW v_project_summary AS
SELECT
    p.id,
    p.organization_id,
    p.name,
    p.number,
    p.phase,
    p.status_color,
    p.health_score,
    p.contract_value,
    p.estimated_completion,
    p.schedule_variance_days,
    c.name as client_name,
    pm.first_name || ' ' || pm.last_name as pm_name,
    (SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = p.id AND dl.log_date = CURRENT_DATE) as has_daily_log,
    (SELECT COUNT(*) FROM punch_list_items pli WHERE pli.project_id = p.id AND pli.status = 'open') as open_punch_items,
    (SELECT SUM(amount_due) FROM invoices i WHERE i.project_id = p.id AND i.status = 'submitted' AND i.due_date < CURRENT_DATE) as overdue_ar
FROM projects p
LEFT JOIN clients c ON p.client_id = c.id
LEFT JOIN users pm ON p.project_manager_id = pm.id
WHERE p.is_active = TRUE;

-- Cash Position View
CREATE OR REPLACE VIEW v_cash_position AS
SELECT
    organization_id,
    SUM(CASE WHEN status = 'submitted' THEN amount_due ELSE 0 END) as pending_ar,
    SUM(CASE WHEN status = 'submitted' AND due_date < CURRENT_DATE THEN amount_due ELSE 0 END) as overdue_ar,
    SUM(retainage_held - retainage_released) as retention_held
FROM invoices
GROUP BY organization_id;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Full-text search on projects
CREATE INDEX idx_projects_search ON projects USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Full-text search on daily logs
CREATE INDEX idx_daily_logs_search ON daily_logs USING gin(to_tsvector('english', COALESCE(work_performed, '')));

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE estimates ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their organization's data
CREATE POLICY org_isolation_users ON users
    FOR ALL USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY org_isolation_projects ON projects
    FOR ALL USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY org_isolation_daily_logs ON daily_logs
    FOR ALL USING (organization_id = current_setting('app.current_organization_id')::UUID);

-- ============================================================================
-- SEED DATA FOR DEMO
-- ============================================================================

-- This will be populated via the application
