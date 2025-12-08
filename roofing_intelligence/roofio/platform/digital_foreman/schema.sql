-- ============================================================================
-- ROOFIO DIGITAL FOREMAN - DATABASE SCHEMA
-- Risk Shield Edition - "The Field Commander"
-- Version 2.0 - December 2025
-- ============================================================================

-- ----------------------------------------------------------------------------
-- EXTENSION: UUID generation
-- ----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- TABLE: projects
-- Master project record with Risk Shield configuration
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,

    -- GPS bounds for geofencing
    gps_latitude DECIMAL(10, 8) NOT NULL,
    gps_longitude DECIMAL(11, 8) NOT NULL,
    geofence_radius_meters INTEGER DEFAULT 500,

    -- Weather API configuration
    weather_api_location_id VARCHAR(50),
    weather_check_times JSONB DEFAULT '["12:00", "16:00"]',

    -- Delay thresholds (configurable per project)
    wind_threshold_mph DECIMAL(5,2) DEFAULT 20.0,
    precip_threshold_inches DECIMAL(5,2) DEFAULT 0.5,
    temp_min_f DECIMAL(5,2) DEFAULT 32.0,
    temp_max_f DECIMAL(5,2) DEFAULT 95.0,

    -- Safety requirements (Risk Shield gates)
    jha_required BOOLEAN DEFAULT TRUE,
    silica_tracking_required BOOLEAN DEFAULT FALSE,
    hot_work_permit_required BOOLEAN DEFAULT FALSE,

    -- OCIP tracking (Owner Controlled Insurance Program)
    is_ocip_project BOOLEAN DEFAULT FALSE,
    insurance_admin_email VARCHAR(255),

    -- Spec references
    spec_sections JSONB DEFAULT '[]',

    -- Status
    status VARCHAR(20) DEFAULT 'active',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: jha_templates
-- Pre-built JHA templates based on work type (Division 07)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_jha_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    work_type VARCHAR(100) NOT NULL, -- 'tpo_install', 'tear_off', 'flashing', etc.

    -- Hazards auto-populated based on work type
    hazards JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {"hazard": "Fall from height", "control": "Harness + tie-off", "ppe": ["harness", "hard_hat"]},
    --   {"hazard": "Chemical fumes", "control": "Ventilation", "ppe": ["respirator"]}
    -- ]

    required_ppe JSONB NOT NULL DEFAULT '[]',
    -- Example: ["hard_hat", "safety_glasses", "gloves", "harness"]

    checklist_items JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {"item": "Fall protection anchor points verified", "required": true},
    --   {"item": "Ladder secured at top and bottom", "required": true}
    -- ]

    spec_section VARCHAR(20), -- e.g., "07 54 00"

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default Division 07 JHA templates
INSERT INTO df_jha_templates (name, work_type, hazards, required_ppe, checklist_items, spec_section) VALUES
('TPO Membrane Installation', 'tpo_install',
 '[{"hazard": "Fall from height (>6ft)", "control": "100% tie-off, warning line system", "ppe": ["harness", "hard_hat"]},
   {"hazard": "Chemical fumes (adhesive/primer)", "control": "Ventilation, work upwind", "ppe": ["respirator", "safety_glasses"]},
   {"hazard": "Hot surface (heat welding)", "control": "Proper training, hot work permit", "ppe": ["gloves", "long_sleeves"]},
   {"hazard": "Heavy lifting", "control": "Team lift for rolls >50lbs", "ppe": ["back_brace"]}]',
 '["hard_hat", "safety_glasses", "gloves", "harness", "safety_boots"]',
 '[{"item": "Fall protection anchor points verified", "required": true},
   {"item": "Hot work permit obtained (if welding)", "required": false},
   {"item": "First aid kit on roof", "required": true},
   {"item": "Fire extinguisher within 25ft", "required": true},
   {"item": "Ladder secured at top and bottom", "required": true}]',
 '07 54 00'),

('Roof Tear-Off', 'tear_off',
 '[{"hazard": "Fall from height", "control": "100% tie-off, controlled access zone", "ppe": ["harness", "hard_hat"]},
   {"hazard": "Falling debris", "control": "Debris chute, ground barriers", "ppe": ["hard_hat", "safety_glasses"]},
   {"hazard": "Silica dust (concrete/masonry)", "control": "Wet methods, HEPA vacuum", "ppe": ["n95_respirator"]},
   {"hazard": "Sharp objects (fasteners, metal)", "control": "Proper disposal, cut-resistant gloves", "ppe": ["cut_resistant_gloves", "safety_boots"]}]',
 '["hard_hat", "safety_glasses", "cut_resistant_gloves", "harness", "safety_boots", "n95_respirator"]',
 '[{"item": "Ground barricades in place", "required": true},
   {"item": "Debris chute secured", "required": true},
   {"item": "Fall protection verified", "required": true},
   {"item": "Silica control plan reviewed", "required": true}]',
 '07 50 00'),

('Sheet Metal Flashing', 'flashing',
 '[{"hazard": "Fall from height", "control": "100% tie-off at edge work", "ppe": ["harness", "hard_hat"]},
   {"hazard": "Sharp metal edges", "control": "Cut-resistant gloves, proper handling", "ppe": ["cut_resistant_gloves"]},
   {"hazard": "Power tool injuries", "control": "Training, guards in place", "ppe": ["safety_glasses", "hearing_protection"]},
   {"hazard": "Pinch points", "control": "Proper brake/shear operation", "ppe": ["gloves"]}]',
 '["hard_hat", "safety_glasses", "cut_resistant_gloves", "hearing_protection", "safety_boots"]',
 '[{"item": "Sheet metal brake guards in place", "required": true},
   {"item": "Scaffolding inspected", "required": true},
   {"item": "Edge protection verified", "required": true}]',
 '07 62 00'),

('Modified Bitumen Application', 'mod_bit',
 '[{"hazard": "Fall from height", "control": "100% tie-off", "ppe": ["harness", "hard_hat"]},
   {"hazard": "Burns from torch", "control": "Hot work permit, fire watch", "ppe": ["flame_resistant_clothing", "leather_gloves"]},
   {"hazard": "Fire/explosion", "control": "Fire extinguisher, propane handling training", "ppe": []},
   {"hazard": "Fumes/smoke", "control": "Work upwind, breaks in fresh air", "ppe": ["respirator"]}]',
 '["hard_hat", "safety_glasses", "leather_gloves", "flame_resistant_clothing", "safety_boots"]',
 '[{"item": "Hot work permit obtained", "required": true},
   {"item": "Fire watch assigned (during + 30min after)", "required": true},
   {"item": "Propane cylinders secured upright", "required": true},
   {"item": "Fire extinguisher within 10ft of torch", "required": true},
   {"item": "Combustibles cleared 35ft radius", "required": true}]',
 '07 52 00'),

('Waterproofing Application', 'waterproofing',
 '[{"hazard": "Fall into excavation", "control": "Barricades, warning line", "ppe": ["hard_hat"]},
   {"hazard": "Chemical exposure", "control": "Proper PPE, ventilation", "ppe": ["chemical_resistant_gloves", "respirator", "tyvek_suit"]},
   {"hazard": "Confined space", "control": "Permit required, air monitoring", "ppe": ["respirator"]},
   {"hazard": "Spray equipment injury", "control": "Training, proper pressure settings", "ppe": ["face_shield"]}]',
 '["hard_hat", "safety_glasses", "chemical_resistant_gloves", "respirator", "tyvek_suit", "safety_boots"]',
 '[{"item": "Confined space permit (if applicable)", "required": false},
   {"item": "Ventilation verified", "required": true},
   {"item": "Chemical SDS reviewed", "required": true},
   {"item": "Emergency eyewash available", "required": true}]',
 '07 10 00')

ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- TABLE: daily_jha
-- THE GATEKEEPER - must be completed before daily log unlocks
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_daily_jha (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,
    date DATE NOT NULL,

    -- Template used
    template_id UUID REFERENCES df_jha_templates(id),

    -- Completion status (THIS IS THE GATEKEEPER)
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Values: 'pending', 'in_progress', 'completed', 'expired'

    -- Safety verification output
    safety_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,

    -- GPS verification (must be on-site)
    completion_gps_latitude DECIMAL(10, 8),
    completion_gps_longitude DECIMAL(11, 8),
    on_site_verified BOOLEAN DEFAULT FALSE,

    -- Hazards identified (can add custom beyond template)
    hazards_identified JSONB NOT NULL DEFAULT '[]',

    -- Checklist responses
    checklist_responses JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {"item": "Fall protection verified", "checked": true, "notes": null},
    --   {"item": "Ladder secured", "checked": true, "notes": "North side ladder"}
    -- ]

    -- PPE verification
    ppe_verified JSONB NOT NULL DEFAULT '[]',

    -- Superintendent signature (REQUIRED)
    superintendent_id UUID NOT NULL,
    superintendent_name VARCHAR(255),
    superintendent_signature TEXT, -- Base64 or URL
    superintendent_signed_at TIMESTAMPTZ,

    -- Crew acknowledgments
    crew_acknowledgments JSONB DEFAULT '[]',
    -- Example: [
    --   {"employee_id": "uuid", "name": "John Smith", "signed_at": "ISO-8601", "signature": "base64"}
    -- ]

    -- Weather conditions at time of JHA
    weather_at_completion JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint: one JHA per project per day
    UNIQUE(project_id, job_id, date)
);

-- Index for the GATEKEEPER check
CREATE INDEX IF NOT EXISTS idx_jha_gatekeeper ON df_daily_jha(project_id, job_id, date, safety_verified);

-- ----------------------------------------------------------------------------
-- TABLE: weather_captures
-- THE WEATHER TRUTH AGENT - automatic captures at 12pm and 4pm
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_weather_captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,

    -- Capture metadata
    captured_at TIMESTAMPTZ NOT NULL,
    capture_type VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    -- Values: 'scheduled' (12pm/4pm), 'manual', 'start_of_day', 'end_of_day'

    -- GPS of capture (project location)
    gps_latitude DECIMAL(10, 8) NOT NULL,
    gps_longitude DECIMAL(11, 8) NOT NULL,

    -- Weather data from API
    source VARCHAR(50) NOT NULL, -- 'openweathermap', 'noaa', 'weatherapi'
    source_station_id VARCHAR(100),

    temperature_f DECIMAL(5,2),
    feels_like_f DECIMAL(5,2),
    humidity_percent INTEGER,
    wind_speed_mph DECIMAL(5,2),
    wind_gust_mph DECIMAL(5,2),
    wind_direction VARCHAR(10),
    precipitation_inches DECIMAL(5,3),
    conditions VARCHAR(100), -- 'Clear', 'Partly Cloudy', 'Rain', etc.
    visibility_miles DECIMAL(5,2),

    -- RAW API response (for legal defensibility)
    raw_api_response JSONB NOT NULL,

    -- AUTO-FLAG LOGIC (Weather Truth Agent)
    delay_flag_triggered BOOLEAN DEFAULT FALSE,
    delay_flag_reasons JSONB DEFAULT '[]',
    -- Example: ["wind_exceeded", "precipitation_exceeded"]

    -- PM acknowledgment (if flagged)
    pm_acknowledged BOOLEAN DEFAULT FALSE,
    pm_acknowledged_at TIMESTAMPTZ,
    pm_acknowledged_by UUID,
    pm_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for delay flag queries
CREATE INDEX IF NOT EXISTS idx_weather_delay_flags ON df_weather_captures(project_id, delay_flag_triggered, captured_at);

-- Trigger function for auto-flagging weather delays
CREATE OR REPLACE FUNCTION check_weather_delay_trigger()
RETURNS TRIGGER AS $$
DECLARE
    project_wind_threshold DECIMAL(5,2);
    project_precip_threshold DECIMAL(5,2);
    project_temp_min DECIMAL(5,2);
    project_temp_max DECIMAL(5,2);
    flag_reasons JSONB := '[]'::jsonb;
BEGIN
    -- Get project thresholds
    SELECT wind_threshold_mph, precip_threshold_inches, temp_min_f, temp_max_f
    INTO project_wind_threshold, project_precip_threshold, project_temp_min, project_temp_max
    FROM df_projects WHERE id = NEW.project_id;

    -- Check wind
    IF NEW.wind_speed_mph > project_wind_threshold THEN
        flag_reasons := flag_reasons || '"wind_exceeded"'::jsonb;
    END IF;

    -- Check precipitation
    IF NEW.precipitation_inches > project_precip_threshold THEN
        flag_reasons := flag_reasons || '"precipitation_exceeded"'::jsonb;
    END IF;

    -- Check temperature (too cold)
    IF NEW.temperature_f < project_temp_min THEN
        flag_reasons := flag_reasons || '"temp_too_low"'::jsonb;
    END IF;

    -- Check temperature (too hot)
    IF NEW.temperature_f > project_temp_max THEN
        flag_reasons := flag_reasons || '"temp_too_high"'::jsonb;
    END IF;

    -- Set flag if any reasons
    IF jsonb_array_length(flag_reasons) > 0 THEN
        NEW.delay_flag_triggered := TRUE;
        NEW.delay_flag_reasons := flag_reasons;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS weather_delay_auto_flag ON df_weather_captures;
CREATE TRIGGER weather_delay_auto_flag
    BEFORE INSERT ON df_weather_captures
    FOR EACH ROW
    EXECUTE FUNCTION check_weather_delay_trigger();

-- ----------------------------------------------------------------------------
-- TABLE: silica_verifications
-- THE SILICA TRACKER - OSHA compliance documentation
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_silica_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,
    date DATE NOT NULL,

    -- Link to daily log
    daily_log_id UUID,

    -- Verification times (minimum 2 per day for compliance)
    verifications JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {
    --     "time": "08:00:00",
    --     "method": "wet_cutting",
    --     "equipment_verified": true,
    --     "photo_id": "uuid",
    --     "verifier_id": "uuid",
    --     "verifier_name": "John Smith",
    --     "notes": "Wet saw operating correctly"
    --   }
    -- ]

    -- Control methods used today
    control_methods_used JSONB NOT NULL DEFAULT '[]',
    -- Values: 'wet_cutting', 'vacuum_extraction', 'enclosed_cab',
    --         'respiratory_protection', 'local_exhaust_ventilation'

    -- Air monitoring (if applicable)
    air_monitoring_conducted BOOLEAN DEFAULT FALSE,
    air_monitoring_results JSONB,

    -- Compliance status
    compliant BOOLEAN DEFAULT FALSE,
    compliance_notes TEXT,

    -- Alert tracking
    morning_alert_sent BOOLEAN DEFAULT FALSE,
    morning_alert_sent_at TIMESTAMPTZ,

    -- Verifier signature
    verifier_id UUID NOT NULL,
    verifier_name VARCHAR(255),
    verifier_signature TEXT,
    signed_at TIMESTAMPTZ,

    -- GPS verification
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(project_id, job_id, date)
);

-- ----------------------------------------------------------------------------
-- TABLE: daily_logs
-- The main daily log (GATED by JHA)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_daily_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,
    date DATE NOT NULL,

    -- GATEKEEPER CHECK
    jha_id UUID REFERENCES df_daily_jha(id),
    jha_verified BOOLEAN DEFAULT FALSE,
    -- If jha_verified = FALSE, this record cannot be created

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Values: 'draft', 'submitted', 'approved', 'revision_requested'

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID NOT NULL,
    created_by_name VARCHAR(255),
    device_id VARCHAR(100),
    offline_created BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMPTZ,

    -- GPS verification
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    on_site_verified BOOLEAN DEFAULT FALSE,

    -- Weather (linked from weather_captures)
    weather_capture_ids JSONB DEFAULT '[]',
    weather_summary JSONB,

    weather_delay_claimed BOOLEAN DEFAULT FALSE,
    weather_delay_reason TEXT,
    weather_delay_hours DECIMAL(4,2),

    -- Manpower
    crew_count INTEGER,
    crew_members JSONB DEFAULT '[]',
    -- Example: [{"employee_id": "uuid", "name": "John Smith", "role": "Foreman", "hours": 8}]

    -- Work performed
    work_description TEXT,
    work_areas JSONB DEFAULT '[]',
    percent_complete_update DECIMAL(5,2),
    sov_line_items_updated JSONB DEFAULT '[]',

    -- Materials
    deliveries_received JSONB DEFAULT '[]',
    materials_installed JSONB DEFAULT '[]',
    materials_stored JSONB DEFAULT '[]',

    -- Equipment
    equipment_on_site JSONB DEFAULT '[]',
    equipment_hours JSONB DEFAULT '{}',

    -- Issues/Blockers
    blockers JSONB DEFAULT '[]',
    rfis_generated JSONB DEFAULT '[]',

    -- Photo IDs
    photo_ids JSONB DEFAULT '[]',

    -- Safety links
    silica_verification_id UUID REFERENCES df_silica_verifications(id),
    hot_work_permit_ids JSONB DEFAULT '[]',

    -- Signatures
    foreman_id UUID,
    foreman_name VARCHAR(255),
    foreman_signature TEXT,
    foreman_signed_at TIMESTAMPTZ,

    -- Guest inspector (if applicable)
    inspector_access JSONB,

    -- Notes
    notes_internal TEXT,
    notes_for_tomorrow TEXT,

    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(project_id, job_id, date)
);

-- GATEKEEPER CONSTRAINT
-- Prevent daily log creation without verified JHA
CREATE OR REPLACE FUNCTION enforce_jha_gatekeeper()
RETURNS TRIGGER AS $$
DECLARE
    jha_record RECORD;
    project_jha_required BOOLEAN;
BEGIN
    -- Check if project requires JHA
    SELECT jha_required INTO project_jha_required
    FROM df_projects WHERE id = NEW.project_id;

    -- If JHA not required, allow creation
    IF NOT project_jha_required THEN
        RETURN NEW;
    END IF;

    -- Check if JHA exists and is verified
    SELECT * INTO jha_record
    FROM df_daily_jha
    WHERE project_id = NEW.project_id
    AND job_id = NEW.job_id
    AND date = NEW.date
    AND safety_verified = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'GATEKEEPER BLOCK: Daily JHA must be completed and verified before creating daily log. Project: %, Job: %, Date: %',
            NEW.project_id, NEW.job_id, NEW.date;
    END IF;

    -- Set the JHA reference
    NEW.jha_id := jha_record.id;
    NEW.jha_verified := TRUE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS daily_log_jha_gatekeeper ON df_daily_logs;
CREATE TRIGGER daily_log_jha_gatekeeper
    BEFORE INSERT ON df_daily_logs
    FOR EACH ROW
    EXECUTE FUNCTION enforce_jha_gatekeeper();

-- ----------------------------------------------------------------------------
-- TABLE: photos
-- Immutable photo records with chain of custody
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,

    -- Chain of custody
    captured_at TIMESTAMPTZ NOT NULL,
    captured_by UUID NOT NULL,
    captured_by_name VARCHAR(255),
    device_id VARCHAR(100) NOT NULL,

    -- GPS (from EXIF, verified)
    gps_latitude DECIMAL(10, 8) NOT NULL,
    gps_longitude DECIMAL(11, 8) NOT NULL,
    gps_accuracy_meters DECIMAL(10,2),

    -- Geofence verification
    on_site_verified BOOLEAN DEFAULT FALSE,

    -- File integrity (SHA-256 hash at capture)
    file_hash_sha256 VARCHAR(64) NOT NULL,
    original_exif JSONB NOT NULL,

    -- Storage
    storage_url TEXT NOT NULL,
    thumbnail_url TEXT,
    file_size_bytes BIGINT,

    -- Categorization
    category VARCHAR(50) NOT NULL,
    -- Values: 'site_conditions', 'work_progress', 'material', 'safety',
    --         'delivery', 'issue', 'silica_control', 'inspection'

    caption TEXT,
    tags JSONB DEFAULT '[]',

    -- Links
    linked_to_type VARCHAR(50),
    linked_to_id UUID,

    -- Flags
    flags JSONB DEFAULT '[]',
    -- Example: ['OUTSIDE_GEOFENCE', 'TIMESTAMP_MISMATCH']

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for chain of custody queries
CREATE INDEX IF NOT EXISTS idx_photos_chain ON df_photos(project_id, captured_at, captured_by);
CREATE INDEX IF NOT EXISTS idx_photos_category ON df_photos(project_id, category, captured_at);

-- ----------------------------------------------------------------------------
-- TABLE: hot_work_permits
-- Digital hot work permits for torch applications
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_hot_work_permits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,
    date DATE NOT NULL,

    -- Location
    work_location TEXT NOT NULL,
    work_description TEXT NOT NULL,

    -- Fire watch assignment
    fire_watch_name VARCHAR(255) NOT NULL,
    fire_watch_id UUID,
    fire_watch_start TIMESTAMPTZ NOT NULL,
    fire_watch_end TIMESTAMPTZ,
    fire_watch_duration_minutes INTEGER DEFAULT 30,

    -- Safety checks
    extinguisher_location TEXT NOT NULL,
    extinguisher_last_inspection DATE,
    combustibles_cleared BOOLEAN DEFAULT FALSE,
    combustibles_clearance_feet INTEGER DEFAULT 35,

    -- Approvals
    issued_by UUID NOT NULL,
    issued_by_name VARCHAR(255),
    issued_at TIMESTAMPTZ DEFAULT NOW(),

    -- Completion
    work_completed_at TIMESTAMPTZ,
    fire_watch_signed_off BOOLEAN DEFAULT FALSE,
    fire_watch_signed_at TIMESTAMPTZ,
    fire_watch_signature TEXT,

    -- Photos
    photo_ids JSONB DEFAULT '[]',

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    -- Values: 'active', 'completed', 'cancelled'

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: material_verifications
-- Barcode/QR scanning for material chain of custody
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_material_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,

    -- Scan data
    scanned_at TIMESTAMPTZ NOT NULL,
    scanned_by UUID NOT NULL,
    scanned_by_name VARCHAR(255),
    barcode_data VARCHAR(255) NOT NULL,
    barcode_type VARCHAR(50), -- 'QR', 'EAN13', 'CODE128', etc.

    -- GPS
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),

    -- Material info (from scan or manual)
    manufacturer VARCHAR(255),
    product_name VARCHAR(255),
    product_code VARCHAR(100),
    lot_number VARCHAR(100),
    manufacture_date DATE,

    -- Delivery info
    delivery_ticket_number VARCHAR(100),
    quantity DECIMAL(10,2),
    unit VARCHAR(20),

    -- Submittal cross-reference
    submittal_id UUID,
    submittal_number VARCHAR(50),
    spec_section VARCHAR(20),

    -- Verification result
    match_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Values: 'verified', 'mismatch', 'pending', 'not_found'
    mismatch_details TEXT,

    -- RFI generated (if mismatch)
    rfi_generated BOOLEAN DEFAULT FALSE,
    rfi_id UUID,

    -- Photos
    photo_ids JSONB DEFAULT '[]',

    -- Resolution (for mismatches)
    resolution_status VARCHAR(20),
    -- Values: 'approved', 'rejected', 'substitution_approved', 'pending'
    resolution_notes TEXT,
    resolved_by UUID,
    resolved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: inspector_visits
-- Guest inspector mode for third-party inspections
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_inspector_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,

    -- Inspector info (no account required)
    inspector_name VARCHAR(255) NOT NULL,
    inspector_company VARCHAR(255),
    inspector_email VARCHAR(255),
    inspector_phone VARCHAR(50),
    inspector_license VARCHAR(100),

    -- Visit details
    visit_date DATE NOT NULL,
    arrival_time TIMESTAMPTZ,
    departure_time TIMESTAMPTZ,

    -- Inspection type
    inspection_type VARCHAR(100) NOT NULL,
    -- Examples: 'deck_inspection', 'insulation_inspection', 'final_inspection', 'warranty_inspection'

    hold_point_name VARCHAR(255),
    spec_reference VARCHAR(50),

    -- Checklist
    checklist_items JSONB DEFAULT '[]',
    -- Example: [
    --   {"item": "Deck surface clean and dry", "checked": true, "notes": null},
    --   {"item": "No ponding water", "checked": true, "notes": null}
    -- ]

    -- Result
    result VARCHAR(20),
    -- Values: 'passed', 'failed', 'conditional'
    result_notes TEXT,
    conditions JSONB DEFAULT '[]',

    -- Signature
    inspector_signature TEXT,
    signed_at TIMESTAMPTZ,

    -- GPS
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),

    -- Photos
    photo_ids JSONB DEFAULT '[]',

    -- Link to daily log
    daily_log_id UUID REFERENCES df_daily_logs(id),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: system_alerts
-- Alerts for PM dashboard (weather flags, missing silica, etc.)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_system_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES df_projects(id) ON DELETE CASCADE,

    alert_type VARCHAR(50) NOT NULL,
    -- Values: 'weather_delay_flag', 'silica_verification_missing',
    --         'jha_not_completed', 'material_mismatch', 'inspection_due',
    --         'hot_work_active', 'fire_watch_ending'

    severity VARCHAR(20) DEFAULT 'warning',
    -- Values: 'info', 'warning', 'critical'

    message TEXT NOT NULL,

    -- Related records
    related_type VARCHAR(50),
    related_id UUID,

    -- Status
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID,
    acknowledged_by_name VARCHAR(255),
    acknowledged_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Auto-dismiss
    expires_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for PM dashboard
CREATE INDEX IF NOT EXISTS idx_alerts_dashboard ON df_system_alerts(project_id, acknowledged, created_at DESC);

-- ----------------------------------------------------------------------------
-- TABLE: sync_queue
-- Offline-first sync tracking
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_sync_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Record info
    record_type VARCHAR(50) NOT NULL,
    -- Values: 'daily_log', 'jha', 'photo', 'material_verification', etc.
    record_id UUID NOT NULL,

    -- Action
    action VARCHAR(20) NOT NULL,
    -- Values: 'create', 'update', 'delete'

    -- Data
    data JSONB NOT NULL,

    -- Device info
    device_id VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,

    -- Sync status
    status VARCHAR(20) DEFAULT 'pending',
    -- Values: 'pending', 'syncing', 'synced', 'failed', 'conflict'

    -- Timing
    created_offline_at TIMESTAMPTZ NOT NULL,
    synced_at TIMESTAMPTZ,

    -- Priority
    priority VARCHAR(20) DEFAULT 'normal',
    -- Values: 'high' (signatures, JHA), 'normal', 'low' (photos)

    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for sync processing
CREATE INDEX IF NOT EXISTS idx_sync_queue_pending ON df_sync_queue(status, priority, created_at);

-- ----------------------------------------------------------------------------
-- TABLE: audit_log
-- Immutable audit trail for all changes
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS df_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Record info
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,

    -- Action
    action VARCHAR(20) NOT NULL,
    -- Values: 'INSERT', 'UPDATE', 'DELETE'

    -- Change data
    old_data JSONB,
    new_data JSONB,

    -- Who/When/Where
    performed_by UUID,
    performed_by_name VARCHAR(255),
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    device_id VARCHAR(100),
    ip_address INET,

    -- Notes
    reason TEXT
);

-- Index for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_log_record ON df_audit_log(table_name, record_id, performed_at);

-- ============================================================================
-- VIEWS for common queries
-- ============================================================================

-- Active projects with today's status
CREATE OR REPLACE VIEW df_project_daily_status AS
SELECT
    p.id as project_id,
    p.name as project_name,
    p.gps_latitude,
    p.gps_longitude,
    CURRENT_DATE as today,

    -- JHA status
    CASE
        WHEN jha.safety_verified = TRUE THEN 'completed'
        WHEN jha.id IS NOT NULL THEN 'in_progress'
        ELSE 'not_started'
    END as jha_status,
    jha.verified_at as jha_verified_at,

    -- Daily log status
    dl.status as daily_log_status,

    -- Weather flags today
    (SELECT COUNT(*) FROM df_weather_captures wc
     WHERE wc.project_id = p.id
     AND wc.captured_at::date = CURRENT_DATE
     AND wc.delay_flag_triggered = TRUE) as weather_flags_today,

    -- Silica compliance
    CASE
        WHEN p.silica_tracking_required = FALSE THEN 'not_required'
        WHEN sv.compliant = TRUE THEN 'compliant'
        WHEN sv.id IS NOT NULL THEN 'in_progress'
        ELSE 'missing'
    END as silica_status,

    -- Active alerts
    (SELECT COUNT(*) FROM df_system_alerts sa
     WHERE sa.project_id = p.id
     AND sa.acknowledged = FALSE) as unacknowledged_alerts

FROM df_projects p
LEFT JOIN df_daily_jha jha ON jha.project_id = p.id AND jha.date = CURRENT_DATE
LEFT JOIN df_daily_logs dl ON dl.project_id = p.id AND dl.date = CURRENT_DATE
LEFT JOIN df_silica_verifications sv ON sv.project_id = p.id AND sv.date = CURRENT_DATE
WHERE p.status = 'active';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
