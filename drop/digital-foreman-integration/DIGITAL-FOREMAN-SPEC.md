# ROOFIO Digital Foreman Module
## "The Field Commander" - Specification-Ready Implementation Guide
### Version 2.0 - December 2025

---

## EXECUTIVE SUMMARY

The Digital Foreman is not just an app—it's a **Risk Shield for Building Owners**. It reduces insurance premiums, eliminates weather delay disputes, and creates legally defensible documentation.

**Critical Insight**: Architects hate specifying brand names (creates liability). They prefer **Performance Specs**—describing what the software MUST DO rather than what it's called.

**The Strategy**: You don't ask them to specify "ROOFIO." You ask them to specify:
> *"A cloud-based system capable of automated NOAA weather logging and metadata-tagged photo verification."*

Which, coincidentally, only ROOFIO does well.

---

## THE GOLDEN TICKET: OCIP (Owner Controlled Insurance Programs)

### What is OCIP?
On large commercial projects ($10M+), the **Building Owner pays for the insurance**, not the contractor. This is called an Owner Controlled Insurance Program (OCIP) or "Wrap-Up" insurance.

### Why This Matters for ROOFIO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE OCIP SALES STRATEGY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PROBLEM: Owner pays insurance premiums based on RISK PROFILE               │
│                                                                              │
│  RISK FACTORS:                                                               │
│  ├── Safety incidents on site                                               │
│  ├── Disputed delay claims (weather, materials)                             │
│  ├── Silica/asbestos exposure lawsuits                                      │
│  └── Undocumented work conditions                                           │
│                                                                              │
│  ROOFIO DIGITAL FOREMAN REDUCES ALL OF THESE:                               │
│  ├── JHA-gated daily logs = documented safety compliance                    │
│  ├── Auto-weather capture = undisputable delay claims                       │
│  ├── Silica control logs = OSHA compliance proof                            │
│  └── GPS-stamped photos = chain of custody evidence                         │
│                                                                              │
│  RESULT: Lower premiums for the Owner                                        │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  SALES PITCH TO OWNER/DEVELOPER:                                            │
│  "This platform pays for itself by reducing your OCIP premiums.             │
│   Every JHA logged, every weather capture, every silica verification        │
│   is documentation that protects you from claims."                          │
│                                                                              │
│  OWNER'S ACTION:                                                            │
│  They tell the Architect: "Write this into the specs."                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Target OCIP Projects
- University construction ($20M+)
- Hospital expansions
- Government facilities
- Corporate headquarters
- Multi-family residential (5+ stories)

---

## PART 0: THE "TROJAN HORSE" - PERFORMANCE-BASED SPEC LANGUAGE

**Core Value Propositions:**
| Stakeholder | Pain Point | Digital Foreman Solution |
|-------------|-----------|--------------------------|
| **Owner** | Arguing about rain days | Auto-documented weather with GPS/timestamp |
| **Architect** | Verifying field compliance | JHA gated daily logs, immutable photos |
| **GC** | Material theft/substitution | Barcode verification against submittals |
| **Insurance** | Disputed claims | Chain-of-custody photo documentation |
| **Contractor** | Getting paid | Progress photos linked to pay apps |

---

## PART 1: THE SPECIFICATION STRATEGY

### 1.1 Target Spec Sections

```
DIVISION 01 - GENERAL REQUIREMENTS
═══════════════════════════════════

PRIMARY TARGETS:
├── 01 26 20 - Weather Delays (Weather documentation)
├── 01 31 00 - Project Management and Coordination (Digital PM platform)
├── 01 32 26 - Construction Progress Reporting (Daily logs)
├── 01 33 00 - Submittal Procedures (Material verification)
├── 01 35 00 - Special Procedures (Safety/JHA)
├── 01 35 29 - Safety Procedures (JHA before work)
└── 01 60 00 - Product Requirements (Material verification)

SECONDARY TARGETS:
├── 07 00 00 - Thermal and Moisture Protection (Roofing-specific)
├── 07 50 00 - Membrane Roofing (System-specific checklists)
└── 07 62 00 - Sheet Metal Flashing (Detail documentation)
```

### 1.2 Spec Language Templates

#### SECTION 01 32 26 – CONSTRUCTION PROGRESS REPORTING
##### (The "Trojan Horse" that mandates your software)

```
PART 2 - PRODUCTS

2.1 DIGITAL FIELD DOCUMENTATION PLATFORM

A. General: Contractor shall provide a cloud-based digital platform 
   for daily field reporting, accessible via mobile devices (iOS/Android) 
   and web browsers.

B. Performance Requirements: The platform must provide the following 
   "Single Source of Truth" capabilities to ensure data integrity:

   1. Automated Weather Logging:
      a. System must automatically record local weather conditions 
         (Temperature, Precipitation, Wind Speed) at minimum 4-hour 
         intervals using GPS geolocation.
      b. Weather data source shall be NOAA, National Weather Service, 
         or equivalent certified meteorological service.
      c. Manual entry of weather data is NOT PERMITTED for delay claims.
      d. System shall automatically flag days where:
         - Wind speed exceeds 20 mph, OR
         - Precipitation exceeds 0.5 inches
         as "Potential Weather Delay" requiring Project Manager review.

   2. Immutable Photo Documentation:
      a. All progress photos must be natively stamped with:
         - GPS Coordinates (Latitude/Longitude)
         - User ID of the photographer
         - Date/Time (Server-side timestamp, not device time)
         - Device identifier (unique to assigned personnel)
      b. Photos must be uploaded directly from capture device to 
         cloud storage. File transfers via email, messaging, or 
         external storage are not permitted.
      c. Original EXIF metadata shall be preserved and uneditable.
      d. System shall generate SHA-256 hash of each photo at capture 
         to verify authenticity.

   3. Safety Gating ("Hard Hat" Feature):
      a. System must PREVENT the creation of a "Daily Construction 
         Report" until the daily "Job Hazard Analysis" (JHA) has been 
         digitally signed by the site superintendent.
      b. JHA form shall include, at minimum:
         - Fall protection verification
         - PPE compliance check
         - Ladder/scaffold inspection
         - Chemical hazard identification
         - Emergency contact verification
      c. JHA completion shall be timestamped with GPS location 
         to verify on-site completion.

   4. Material Chain of Custody:
      a. System must support barcode/QR scanning of delivered materials 
         to verify against approved Submittals (Section 01 33 00).
      b. Mismatched materials shall automatically generate hold status 
         and RFI to Architect.
      c. Material verification records shall include:
         - Barcode/QR data
         - Submittal reference number
         - Verification timestamp
         - Verifier ID
         - Photo documentation of material labels

   5. Offline Capability:
      a. System must operate fully offline with automatic 
         synchronization when connectivity is restored.
      b. All data created offline shall retain original timestamps 
         and be flagged as "Offline Created" in sync log.

C. Quality Assurance:
   1. Platform shall maintain immutable audit trail of all 
      document modifications.
   2. All exported reports shall include digital signature 
      verification capability.
```

#### SECTION 01 35 29 – HEALTH, SAFETY, AND EMERGENCY RESPONSE
##### (The "Risk Mitigation" Hook)

```
PART 1 - GENERAL

1.4 SUBMITTALS

A. Silica Exposure Control Plan (Digital Log):
   1. Contractor must maintain a daily digital log of engineering 
      controls used for crystalline silica containment.
   2. Log entries shall include:
      a. Control method used (Wet cutting, Vacuum extraction, 
         Enclosed cab, Respiratory protection)
      b. Time of verification (minimum: start of shift, mid-day)
      c. Verifier name and signature
      d. Photo documentation of control equipment in use
      e. Air monitoring results (if applicable)
   3. Log entries shall be GPS-stamped to verify on-site completion.
   4. System shall alert Safety Officer if daily silica verification 
      is not completed by 10:00 AM local time.

B. Job Hazard Analysis (JHA) Requirements:
   1. Daily JHA completion is PREREQUISITE to commencing work.
   2. JHA shall be generated based on:
      a. Scheduled work activities for the day
      b. Materials to be installed (from approved submittals)
      c. Weather conditions (from automated weather capture)
      d. Site-specific hazards identified in Safety Plan
   3. JHA shall be digitally signed by:
      a. Site Superintendent (required)
      b. All crew members (acknowledgment)
   4. JHA data shall feed directly into Daily Construction Report.

C. Hot Work Permit (Digital):
   1. For torch-applied roofing, hot work permits shall be 
      generated through the digital platform.
   2. Permit shall include:
      a. Fire watch assignment and duration
      b. Extinguisher verification (location, inspection date)
      c. Combustible material clearance confirmation
      d. Post-work monitoring schedule
   3. Fire watch sign-off shall be captured digitally with 
      timestamp at completion.

PART 3 - EXECUTION

3.1 DOCUMENTATION REQUIREMENTS

A. All safety documentation shall be maintained in the approved 
   digital platform and available for Owner/Architect review 
   within 24 hours of request.

B. Weekly safety summary reports shall be auto-generated and 
   distributed to:
   1. Owner's Representative
   2. Architect
   3. General Contractor Safety Director
   4. Insurance Administrator (for OCIP projects)
```

#### SECTION 01 60 00 – PRODUCT REQUIREMENTS
##### (Material Verification)

```
PART 1 - GENERAL

1.5 FIELD VERIFICATION

A. Material Delivery Verification:
   1. All materials delivered to site shall be scanned using 
      the approved digital platform within 4 hours of delivery.
   2. Scanning shall verify:
      a. Material matches approved Submittal
      b. Quantity matches delivery ticket
      c. Manufacturer and product line are correct
      d. Lot/batch numbers are recorded

B. Non-Compliant Material Protocol:
   1. Materials that do not match approved Submittals shall be:
      a. Automatically flagged in system
      b. Placed on installation hold
      c. Documented with photo evidence
   2. RFI shall be auto-generated to Architect for:
      a. Substitution approval, or
      b. Rejection and replacement instructions
   3. Non-compliant materials shall not be installed until 
      written approval is received and logged in system.
```

#### Section 01 31 00 - Project Management and Coordination
```
PART 1 - GENERAL

1.1 PROJECT COORDINATION REQUIREMENTS

A. Project collaboration and documentation shall be managed via a 
   centralized, cloud-based platform capable of real-time field data 
   synchronization (e.g., ROOFIO or approved equal).

B. Platform Requirements:
   1. Offline-first capability with automatic synchronization
   2. GPS-tagged photographic documentation
   3. Weather data integration from certified sources
   4. Digital signature capability for field reports
   5. Role-based access control
   6. Audit trail for all document modifications

C. Daily Field Reports shall be generated through the approved platform
   and include, at minimum:
   1. Automatic weather capture at 12:00 PM and 4:00 PM local time
   2. GPS coordinates confirming job site location
   3. Crew count and work performed
   4. Material deliveries received
   5. Digital foreman signature
```

#### Section 01 32 26 - Construction Progress Reporting
```
PART 1 - GENERAL

1.1 DAILY CONSTRUCTION REPORTS

A. Contractor shall utilize a digital platform to record daily site 
   conditions. System must automatically capture local weather data 
   (temperature, precipitation, wind speed) at 12:00 PM and 4:00 PM 
   to substantiate weather delay claims.

B. Weather Data Requirements:
   1. Source: NOAA, NWS, or equivalent certified weather service
   2. Capture: Automatic, GPS-based location
   3. Storage: Immutable record with timestamp
   4. Format: PDF export capability for official documentation

C. Progress Photography:
   1. Minimum 5 photos per work day
   2. GPS coordinates embedded in metadata
   3. Timestamp embedded and non-editable
   4. Direct upload from capture device (no file transfers)
```

#### Section 01 35 29 - Safety Procedures
```
PART 1 - GENERAL

1.1 JOB HAZARD ANALYSIS (JHA) REQUIREMENTS

A. Daily safety inspection checklists must be digitally completed and 
   time-stamped prior to the commencement of work activities each 
   morning.

B. JHA Completion shall be prerequisite to unlocking Daily Field Report
   functionality.

C. JHA shall be automatically generated based on:
   1. Specified roofing system type
   2. Materials listed in approved submittals
   3. Site-specific hazards identified in contract documents

D. Documentation shall include:
   1. Hazard identification with photo documentation
   2. Control measures implemented
   3. PPE requirements by task
   4. Worker acknowledgment signatures
```

#### Section 01 33 00 - Submittal Procedures (Material Verification)
```
PART 2 - PRODUCTS

2.1 MATERIAL VERIFICATION

A. Field verification of delivered materials shall be digitally logged 
   against the approved Bill of Materials to ensure compliance with 
   Specification Section 07 (Thermal and Moisture Protection).

B. Verification Method:
   1. Barcode/QR code scanning of manufacturer packaging
   2. Cross-reference to approved submittal number
   3. Quantity verification against delivery ticket
   4. Photo documentation of material labels
   5. GPS-tagged receipt location

C. Non-Compliant Material Protocol:
   1. Automatic flag in system
   2. Hold on material installation
   3. RFI generation to Architect
   4. Resolution documentation required before use
```

#### Section 01 32 33 - Photographic Documentation
```
PART 1 - GENERAL

1.1 PHOTOGRAPHIC DOCUMENTATION REQUIREMENTS

A. Photographic documentation shall be metadata-tagged with geolocations 
   and timestamps. Photos must be uploaded directly from the capture 
   device to the cloud server to ensure chain of custody.

B. Required Metadata:
   1. GPS coordinates (latitude, longitude)
   2. Timestamp (date, time, timezone)
   3. Device identifier (unique to assigned personnel)
   4. User ID of photographer
   5. Project identifier

C. Chain of Custody:
   1. Photos shall not be transferred via email, messaging, or file sharing
   2. Direct capture-to-cloud upload required
   3. No post-capture editing or cropping permitted
   4. Original EXIF metadata shall be preserved

D. Photo Categories (minimum required daily):
   1. Site conditions at start of day (2)
   2. Work in progress (3)
   3. Material deliveries (as needed)
   4. Safety compliance (1)
   5. End of day conditions (2)
```

---

## PART 2: DATABASE SCHEMA - THE "RISK SHIELD" CORE

### 2.0 The Three Risk Shield Features

These are the core features that make ROOFIO "Spec-Grade":

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE RISK SHIELD ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. THE GATEKEEPER (JHA Lock)                                               │
│     ├── Trigger: User opens app at start of day                             │
│     ├── Action: ALL features LOCKED                                         │
│     ├── Unlock: Complete and sign daily JHA                                 │
│     └── Output: { "safety_verified": true, "timestamp": "ISO-8601" }        │
│                                                                              │
│  2. THE WEATHER TRUTH AGENT                                                 │
│     ├── Trigger: 12:00 PM and 4:00 PM daily (automatic)                     │
│     ├── Action: Fetch weather from API based on project GPS                 │
│     ├── Logic: If wind > 20mph OR precip > 0.5in → FLAG                     │
│     └── Output: "Potential Weather Delay" on PM dashboard                   │
│                                                                              │
│  3. THE SILICA TRACKER                                                      │
│     ├── Trigger: Daily (when scope includes cutting)                        │
│     ├── Action: Require silica control verification form                    │
│     ├── Logic: Links to daily log, alerts if not completed by 10 AM        │
│     └── Output: OSHA-compliant silica exposure documentation                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Database Schema - Core Tables

```sql
-- ============================================================================
-- ROOFIO DIGITAL FOREMAN - DATABASE SCHEMA
-- Risk Shield Edition
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLE: projects
-- Master project record
-- ----------------------------------------------------------------------------
CREATE TABLE projects (
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
    
    -- Safety requirements
    jha_required BOOLEAN DEFAULT TRUE,
    silica_tracking_required BOOLEAN DEFAULT FALSE,
    hot_work_permit_required BOOLEAN DEFAULT FALSE,
    
    -- OCIP tracking
    is_ocip_project BOOLEAN DEFAULT FALSE,
    insurance_admin_email VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: jha_templates
-- Pre-built JHA templates based on work type
-- ----------------------------------------------------------------------------
CREATE TABLE jha_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    work_type VARCHAR(100) NOT NULL, -- 'tpo_install', 'tear_off', 'flashing', etc.
    
    -- Hazards auto-populated based on work type
    hazards JSONB NOT NULL,
    -- Example: [
    --   {"hazard": "Fall from height", "control": "Harness + tie-off", "ppe": ["harness", "hard_hat"]},
    --   {"hazard": "Chemical fumes", "control": "Ventilation", "ppe": ["respirator"]}
    -- ]
    
    required_ppe JSONB NOT NULL,
    -- Example: ["hard_hat", "safety_glasses", "gloves", "harness"]
    
    checklist_items JSONB NOT NULL,
    -- Example: [
    --   {"item": "Fall protection anchor points verified", "required": true},
    --   {"item": "Ladder secured at top and bottom", "required": true}
    -- ]
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- TABLE: daily_jha
-- The GATEKEEPER - must be completed before daily log unlocks
-- ----------------------------------------------------------------------------
CREATE TABLE daily_jha (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    job_id UUID NOT NULL,
    date DATE NOT NULL,
    
    -- Template used
    template_id UUID REFERENCES jha_templates(id),
    
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
    
    -- Hazards identified
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
    superintendent_signature TEXT, -- Base64 or URL
    superintendent_signed_at TIMESTAMPTZ,
    
    -- Crew acknowledgments
    crew_acknowledgments JSONB DEFAULT '[]',
    -- Example: [
    --   {"employee_id": "uuid", "signed_at": "ISO-8601", "signature": "base64"}
    -- ]
    
    -- Weather conditions at time of JHA
    weather_at_completion JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint: one JHA per project per day
    UNIQUE(project_id, job_id, date)
);

-- Index for the GATEKEEPER check
CREATE INDEX idx_jha_gatekeeper ON daily_jha(project_id, job_id, date, safety_verified);

-- ----------------------------------------------------------------------------
-- TABLE: weather_captures
-- THE WEATHER TRUTH AGENT - automatic captures
-- ----------------------------------------------------------------------------
CREATE TABLE weather_captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
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
CREATE INDEX idx_weather_delay_flags ON weather_captures(project_id, delay_flag_triggered, captured_at);

-- Trigger function for auto-flagging
CREATE OR REPLACE FUNCTION check_weather_delay_trigger()
RETURNS TRIGGER AS $$
DECLARE
    project_wind_threshold DECIMAL(5,2);
    project_precip_threshold DECIMAL(5,2);
    project_temp_min DECIMAL(5,2);
    project_temp_max DECIMAL(5,2);
    flag_reasons JSONB := '[]';
BEGIN
    -- Get project thresholds
    SELECT wind_threshold_mph, precip_threshold_inches, temp_min_f, temp_max_f
    INTO project_wind_threshold, project_precip_threshold, project_temp_min, project_temp_max
    FROM projects WHERE id = NEW.project_id;
    
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

CREATE TRIGGER weather_delay_auto_flag
    BEFORE INSERT ON weather_captures
    FOR EACH ROW
    EXECUTE FUNCTION check_weather_delay_trigger();

-- ----------------------------------------------------------------------------
-- TABLE: silica_verifications
-- THE SILICA TRACKER - OSHA compliance
-- ----------------------------------------------------------------------------
CREATE TABLE silica_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    job_id UUID NOT NULL,
    date DATE NOT NULL,
    
    -- Link to daily log
    daily_log_id UUID,
    
    -- Verification times (minimum 2 per day)
    verifications JSONB NOT NULL DEFAULT '[]',
    -- Example: [
    --   {
    --     "time": "08:00:00",
    --     "method": "wet_cutting",
    --     "equipment_verified": true,
    --     "photo_id": "uuid",
    --     "verifier_id": "uuid",
    --     "notes": "Wet saw operating correctly"
    --   },
    --   {
    --     "time": "13:00:00", 
    --     "method": "vacuum_extraction",
    --     "equipment_verified": true,
    --     "photo_id": "uuid",
    --     "verifier_id": "uuid",
    --     "notes": "HEPA filter checked"
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
    verifier_signature TEXT,
    signed_at TIMESTAMPTZ,
    
    -- GPS verification
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(project_id, job_id, date)
);

-- Alert trigger for silica not completed by 10 AM
CREATE OR REPLACE FUNCTION check_silica_morning_alert()
RETURNS void AS $$
DECLARE
    project_record RECORD;
BEGIN
    -- Find projects requiring silica tracking without verification by 10 AM
    FOR project_record IN 
        SELECT p.id, p.name
        FROM projects p
        WHERE p.silica_tracking_required = TRUE
        AND NOT EXISTS (
            SELECT 1 FROM silica_verifications sv
            WHERE sv.project_id = p.id
            AND sv.date = CURRENT_DATE
            AND jsonb_array_length(sv.verifications) > 0
        )
    LOOP
        -- Insert alert (would trigger notification in app)
        INSERT INTO system_alerts (project_id, alert_type, message, created_at)
        VALUES (
            project_record.id,
            'silica_verification_missing',
            'Silica control verification not completed by 10:00 AM',
            NOW()
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- TABLE: daily_logs
-- The main daily log (GATED by JHA)
-- ----------------------------------------------------------------------------
CREATE TABLE daily_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    job_id UUID NOT NULL,
    date DATE NOT NULL,
    
    -- GATEKEEPER CHECK
    jha_id UUID REFERENCES daily_jha(id),
    jha_verified BOOLEAN DEFAULT FALSE,
    -- If jha_verified = FALSE, this record cannot be created
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Values: 'draft', 'submitted', 'approved', 'revision_requested'
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID NOT NULL,
    device_id VARCHAR(100),
    offline_created BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMPTZ,
    
    -- GPS verification
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    on_site_verified BOOLEAN DEFAULT FALSE,
    
    -- Weather (linked from weather_captures)
    weather_captures JSONB DEFAULT '[]',
    -- Array of weather_capture IDs for this date
    
    weather_delay_claimed BOOLEAN DEFAULT FALSE,
    weather_delay_reason TEXT,
    
    -- Manpower
    crew_count INTEGER,
    crew_members JSONB DEFAULT '[]',
    
    -- Work performed
    work_description TEXT,
    percent_complete_update DECIMAL(5,2),
    areas_worked JSONB DEFAULT '[]',
    
    -- Materials
    deliveries_received JSONB DEFAULT '[]',
    materials_installed JSONB DEFAULT '[]',
    materials_stored JSONB DEFAULT '[]',
    
    -- Equipment
    equipment_on_site JSONB DEFAULT '[]',
    
    -- Issues/Blockers
    blockers JSONB DEFAULT '[]',
    
    -- Photos
    photos JSONB DEFAULT '[]',
    
    -- Safety links
    silica_verification_id UUID REFERENCES silica_verifications(id),
    hot_work_permits JSONB DEFAULT '[]',
    
    -- Signatures
    foreman_signature TEXT,
    foreman_signed_at TIMESTAMPTZ,
    
    -- Guest inspector (if applicable)
    inspector_access JSONB,
    
    -- Notes
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
BEGIN
    -- Check if JHA exists and is verified
    SELECT * INTO jha_record
    FROM daily_jha
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

CREATE TRIGGER daily_log_jha_gatekeeper
    BEFORE INSERT ON daily_logs
    FOR EACH ROW
    EXECUTE FUNCTION enforce_jha_gatekeeper();

-- ----------------------------------------------------------------------------
-- TABLE: photos
-- Immutable photo records with chain of custody
-- ----------------------------------------------------------------------------
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Chain of custody
    captured_at TIMESTAMPTZ NOT NULL,
    captured_by UUID NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    
    -- GPS (from EXIF, verified)
    gps_latitude DECIMAL(10, 8) NOT NULL,
    gps_longitude DECIMAL(11, 8) NOT NULL,
    gps_accuracy_meters DECIMAL(10,2),
    
    -- Geofence verification
    on_site_verified BOOLEAN DEFAULT FALSE,
    
    -- File integrity
    file_hash_sha256 VARCHAR(64) NOT NULL,
    original_exif JSONB NOT NULL,
    
    -- Storage
    storage_url TEXT NOT NULL,
    thumbnail_url TEXT,
    
    -- Categorization
    category VARCHAR(50) NOT NULL,
    -- Values: 'site_conditions', 'work_progress', 'material', 'safety', 
    --         'delivery', 'issue', 'silica_control', 'inspection'
    
    caption TEXT,
    
    -- Links
    linked_to_type VARCHAR(50),
    linked_to_id UUID,
    
    -- Flags
    flags JSONB DEFAULT '[]',
    -- Example: ['OUTSIDE_GEOFENCE', 'TIMESTAMP_MISMATCH']
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for chain of custody queries
CREATE INDEX idx_photos_chain ON photos(project_id, captured_at, captured_by);

-- ----------------------------------------------------------------------------
-- TABLE: system_alerts
-- Alerts for PM dashboard
-- ----------------------------------------------------------------------------
CREATE TABLE system_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    alert_type VARCHAR(50) NOT NULL,
    -- Values: 'weather_delay_flag', 'silica_verification_missing', 
    --         'jha_not_completed', 'material_mismatch', 'inspection_due'
    
    severity VARCHAR(20) DEFAULT 'warning',
    -- Values: 'info', 'warning', 'critical'
    
    message TEXT NOT NULL,
    
    -- Related records
    related_type VARCHAR(50),
    related_id UUID,
    
    -- Status
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for PM dashboard
CREATE INDEX idx_alerts_dashboard ON system_alerts(project_id, acknowledged, created_at DESC);
```

### 2.2 API Endpoints - Risk Shield Features

```javascript
// ============================================================================
// GATEKEEPER API - JHA Lock Logic
// ============================================================================

// Check if daily log is unlocked (JHA completed)
app.get('/api/projects/:projectId/jobs/:jobId/gatekeeper-status', async (req, res) => {
  const { projectId, jobId } = req.params;
  const today = new Date().toISOString().split('T')[0];
  
  const jha = await db.query(`
    SELECT id, safety_verified, verified_at, superintendent_signed_at
    FROM daily_jha
    WHERE project_id = $1 AND job_id = $2 AND date = $3
  `, [projectId, jobId, today]);
  
  if (!jha.rows.length || !jha.rows[0].safety_verified) {
    return res.json({
      locked: true,
      reason: 'JHA_NOT_COMPLETED',
      message: 'Complete daily JHA to unlock daily log',
      jha_status: jha.rows.length ? 'in_progress' : 'not_started'
    });
  }
  
  return res.json({
    locked: false,
    jha_id: jha.rows[0].id,
    safety_verified: true,
    timestamp: jha.rows[0].verified_at
  });
});

// Complete JHA and unlock daily log
app.post('/api/projects/:projectId/jobs/:jobId/jha/complete', async (req, res) => {
  const { projectId, jobId } = req.params;
  const { 
    checklist_responses, 
    hazards_identified,
    ppe_verified,
    superintendent_signature,
    crew_acknowledgments,
    gps_latitude,
    gps_longitude
  } = req.body;
  
  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toISOString();
  
  // Verify on-site (within geofence)
  const project = await db.query(`
    SELECT gps_latitude, gps_longitude, geofence_radius_meters
    FROM projects WHERE id = $1
  `, [projectId]);
  
  const onSite = isWithinGeofence(
    { lat: gps_latitude, lng: gps_longitude },
    { 
      lat: project.rows[0].gps_latitude, 
      lng: project.rows[0].gps_longitude,
      radius: project.rows[0].geofence_radius_meters
    }
  );
  
  // Insert or update JHA
  const result = await db.query(`
    INSERT INTO daily_jha (
      project_id, job_id, date, status,
      safety_verified, verified_at,
      completion_gps_latitude, completion_gps_longitude, on_site_verified,
      hazards_identified, checklist_responses, ppe_verified,
      superintendent_id, superintendent_signature, superintendent_signed_at,
      crew_acknowledgments
    ) VALUES ($1, $2, $3, 'completed', true, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
    ON CONFLICT (project_id, job_id, date) 
    DO UPDATE SET
      status = 'completed',
      safety_verified = true,
      verified_at = $4,
      completion_gps_latitude = $5,
      completion_gps_longitude = $6,
      on_site_verified = $7,
      hazards_identified = $8,
      checklist_responses = $9,
      ppe_verified = $10,
      superintendent_signature = $12,
      superintendent_signed_at = $13,
      crew_acknowledgments = $14,
      updated_at = NOW()
    RETURNING id, safety_verified, verified_at
  `, [
    projectId, jobId, today, now,
    gps_latitude, gps_longitude, onSite,
    JSON.stringify(hazards_identified),
    JSON.stringify(checklist_responses),
    JSON.stringify(ppe_verified),
    req.user.id,
    superintendent_signature,
    now,
    JSON.stringify(crew_acknowledgments)
  ]);
  
  return res.json({
    success: true,
    jha_id: result.rows[0].id,
    safety_verified: true,
    timestamp: result.rows[0].verified_at,
    on_site_verified: onSite,
    daily_log_unlocked: true
  });
});

// ============================================================================
// WEATHER TRUTH AGENT API
// ============================================================================

// Scheduled weather capture (called by cron job at 12pm and 4pm)
app.post('/api/weather/scheduled-capture', async (req, res) => {
  // Get all active projects
  const projects = await db.query(`
    SELECT id, gps_latitude, gps_longitude, weather_api_location_id,
           wind_threshold_mph, precip_threshold_inches
    FROM projects
    WHERE status = 'active'
  `);
  
  const results = [];
  
  for (const project of projects.rows) {
    // Fetch weather from API
    const weather = await fetchWeatherFromAPI(
      project.gps_latitude,
      project.gps_longitude
    );
    
    // Insert weather capture (trigger will auto-flag)
    const capture = await db.query(`
      INSERT INTO weather_captures (
        project_id, captured_at, capture_type,
        gps_latitude, gps_longitude,
        source, temperature_f, humidity_percent,
        wind_speed_mph, wind_gust_mph, wind_direction,
        precipitation_inches, conditions, visibility_miles,
        raw_api_response
      ) VALUES ($1, NOW(), 'scheduled', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
      RETURNING id, delay_flag_triggered, delay_flag_reasons
    `, [
      project.id,
      project.gps_latitude, project.gps_longitude,
      'openweathermap',
      weather.temp_f, weather.humidity,
      weather.wind_mph, weather.wind_gust_mph, weather.wind_dir,
      weather.precip_inches, weather.conditions, weather.visibility,
      JSON.stringify(weather.raw)
    ]);
    
    // If flagged, create alert for PM dashboard
    if (capture.rows[0].delay_flag_triggered) {
      await db.query(`
        INSERT INTO system_alerts (
          project_id, alert_type, severity, message,
          related_type, related_id
        ) VALUES ($1, 'weather_delay_flag', 'warning', $2, 'weather_capture', $3)
      `, [
        project.id,
        `Weather conditions may cause delay: ${capture.rows[0].delay_flag_reasons.join(', ')}`,
        capture.rows[0].id
      ]);
    }
    
    results.push({
      project_id: project.id,
      flagged: capture.rows[0].delay_flag_triggered,
      reasons: capture.rows[0].delay_flag_reasons
    });
  }
  
  return res.json({ captures: results });
});

// PM dashboard - get weather flags
app.get('/api/projects/:projectId/weather-flags', async (req, res) => {
  const { projectId } = req.params;
  const { startDate, endDate } = req.query;
  
  const flags = await db.query(`
    SELECT wc.*, 
           sa.acknowledged, sa.acknowledged_at, sa.resolution_notes
    FROM weather_captures wc
    LEFT JOIN system_alerts sa ON sa.related_id = wc.id
    WHERE wc.project_id = $1
    AND wc.delay_flag_triggered = true
    AND wc.captured_at BETWEEN $2 AND $3
    ORDER BY wc.captured_at DESC
  `, [projectId, startDate, endDate]);
  
  return res.json({ weather_flags: flags.rows });
});

// ============================================================================
// SILICA TRACKER API
// ============================================================================

// Submit silica verification
app.post('/api/projects/:projectId/jobs/:jobId/silica-verification', async (req, res) => {
  const { projectId, jobId } = req.params;
  const { 
    method, 
    equipment_verified, 
    photo_id, 
    notes,
    gps_latitude,
    gps_longitude
  } = req.body;
  
  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toISOString();
  const currentTime = new Date().toTimeString().split(' ')[0];
  
  // Get or create today's silica record
  let silicaRecord = await db.query(`
    SELECT * FROM silica_verifications
    WHERE project_id = $1 AND job_id = $2 AND date = $3
  `, [projectId, jobId, today]);
  
  const verification = {
    time: currentTime,
    method: method,
    equipment_verified: equipment_verified,
    photo_id: photo_id,
    verifier_id: req.user.id,
    notes: notes
  };
  
  if (!silicaRecord.rows.length) {
    // Create new record
    silicaRecord = await db.query(`
      INSERT INTO silica_verifications (
        project_id, job_id, date,
        verifications, control_methods_used,
        verifier_id, gps_latitude, gps_longitude
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *
    `, [
      projectId, jobId, today,
      JSON.stringify([verification]),
      JSON.stringify([method]),
      req.user.id,
      gps_latitude, gps_longitude
    ]);
  } else {
    // Append to existing
    const verifications = silicaRecord.rows[0].verifications;
    verifications.push(verification);
    
    const methods = new Set(silicaRecord.rows[0].control_methods_used);
    methods.add(method);
    
    silicaRecord = await db.query(`
      UPDATE silica_verifications
      SET verifications = $1,
          control_methods_used = $2,
          updated_at = NOW()
      WHERE id = $3
      RETURNING *
    `, [
      JSON.stringify(verifications),
      JSON.stringify([...methods]),
      silicaRecord.rows[0].id
    ]);
  }
  
  // Check compliance (minimum 2 verifications per day)
  const isCompliant = silicaRecord.rows[0].verifications.length >= 2;
  
  await db.query(`
    UPDATE silica_verifications
    SET compliant = $1
    WHERE id = $2
  `, [isCompliant, silicaRecord.rows[0].id]);
  
  return res.json({
    success: true,
    verification_count: silicaRecord.rows[0].verifications.length,
    compliant: isCompliant,
    silica_id: silicaRecord.rows[0].id
  });
});

// Silica compliance alert (called at 10 AM by cron)
app.post('/api/silica/morning-alert-check', async (req, res) => {
  const today = new Date().toISOString().split('T')[0];
  
  const missingProjects = await db.query(`
    SELECT p.id, p.name
    FROM projects p
    WHERE p.silica_tracking_required = TRUE
    AND p.status = 'active'
    AND NOT EXISTS (
      SELECT 1 FROM silica_verifications sv
      WHERE sv.project_id = p.id
      AND sv.date = $1
      AND jsonb_array_length(sv.verifications) > 0
    )
  `, [today]);
  
  const alerts = [];
  for (const project of missingProjects.rows) {
    await db.query(`
      INSERT INTO system_alerts (
        project_id, alert_type, severity, message
      ) VALUES ($1, 'silica_verification_missing', 'critical', $2)
    `, [
      project.id,
      'ALERT: Silica control verification not completed by 10:00 AM'
    ]);
    alerts.push(project.id);
  }
  
  return res.json({ alerts_created: alerts.length, projects: alerts });
});
```

### 2.3 Frontend - Gatekeeper Lock Screen

```jsx
// GatekeeperScreen.jsx - The Lock Screen
import React, { useState, useEffect } from 'react';

const GatekeeperScreen = ({ projectId, jobId, onUnlock }) => {
  const [gatekeeperStatus, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    checkGatekeeperStatus();
  }, []);
  
  const checkGatekeeperStatus = async () => {
    const response = await fetch(
      `/api/projects/${projectId}/jobs/${jobId}/gatekeeper-status`
    );
    const data = await response.json();
    setStatus(data);
    setLoading(false);
    
    if (!data.locked) {
      onUnlock(data);
    }
  };
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (!gatekeeperStatus.locked) {
    return null; // Unlocked, show main app
  }
  
  return (
    <div className="gatekeeper-lock-screen">
      <div className="lock-icon">🔒</div>
      
      <h1>Daily Log Locked</h1>
      
      <div className="lock-message">
        <p>Complete the Daily Job Hazard Analysis (JHA) to unlock all features.</p>
        
        <div className="safety-badge">
          ⚠️ Safety First
        </div>
      </div>
      
      <div className="jha-status">
        {gatekeeperStatus.jha_status === 'not_started' ? (
          <p>No JHA started for today</p>
        ) : (
          <p>JHA in progress - complete all items</p>
        )}
      </div>
      
      <button 
        className="unlock-button"
        onClick={() => navigateToJHAForm()}
      >
        🔓 Complete JHA to Unlock
      </button>
      
      <div className="locked-features">
        <h3>Features locked until JHA complete:</h3>
        <ul>
          <li>📸 Photo capture</li>
          <li>📝 Daily log</li>
          <li>📦 Material verification</li>
          <li>⚠️ Issue reporting</li>
        </ul>
      </div>
    </div>
  );
};
```

---

## PART 3: DAILY LOG DATA STRUCTURE (SSOT INTEGRATION)

```json
{
  "daily_log": {
    "id": "uuid",
    "job_id": "job_uuid (SSOT link)",
    "date": "2025-12-07",
    "status": "draft|submitted|approved",
    
    "metadata": {
      "created_at": "ISO-8601",
      "created_by": "employee_id",
      "device_id": "unique_device_identifier",
      "gps_location": {
        "latitude": 39.2904,
        "longitude": -76.6122,
        "accuracy_meters": 5
      },
      "offline_created": false,
      "synced_at": "ISO-8601 or null"
    },
    
    "jha_completed": {
      "required": true,
      "completed_at": "ISO-8601 or null",
      "jha_id": "jha_uuid",
      "blocks_daily_log": true
    },
    
    "weather": {
      "source": "NOAA|OpenWeatherMap|Apple Weather",
      "captures": [
        {
          "time": "12:00:00",
          "temperature_f": 45,
          "precipitation_in": 0.0,
          "wind_speed_mph": 12,
          "conditions": "Partly Cloudy",
          "auto_captured": true
        },
        {
          "time": "16:00:00",
          "temperature_f": 52,
          "precipitation_in": 0.0,
          "wind_speed_mph": 8,
          "conditions": "Clear",
          "auto_captured": true
        }
      ],
      "delay_claimed": false,
      "delay_reason": null
    },
    
    "manpower": {
      "crew_count": 6,
      "crew_members": [
        {
          "employee_id": "emp_uuid",
          "name": "John Smith",
          "role": "Foreman",
          "hours": 8,
          "certifications_verified": true
        }
      ],
      "subcontractors": [],
      "visitors": []
    },
    
    "work_performed": {
      "description": "Installed TPO membrane on roof area A, zones 1-3",
      "percent_complete_update": 35,
      "sov_line_items_updated": ["sov_001", "sov_002"],
      "areas_worked": ["Roof Area A - Zones 1-3"]
    },
    
    "materials": {
      "deliveries_received": [
        {
          "delivery_id": "del_uuid",
          "po_number": "PO-2025-0042",
          "material": "TPO 60mil White",
          "quantity": 5000,
          "unit": "SF",
          "verified_against_submittal": "SUB-001",
          "verification_method": "barcode_scan",
          "barcode_data": "7890123456789",
          "match_status": "verified|mismatch|pending",
          "photo_ids": ["photo_uuid_1", "photo_uuid_2"],
          "received_by": "employee_id",
          "received_at": "ISO-8601"
        }
      ],
      "materials_installed": [
        {
          "material": "TPO 60mil White",
          "quantity": 2500,
          "unit": "SF",
          "from_delivery_id": "del_uuid"
        }
      ],
      "stored_materials": [
        {
          "material": "TPO 60mil White",
          "quantity": 2500,
          "unit": "SF",
          "location": "Roof - Staging Area B",
          "photo_id": "photo_uuid_3"
        }
      ]
    },
    
    "equipment": {
      "on_site": ["Crane #42", "Kettle #7"],
      "hours_used": {
        "Crane #42": 4,
        "Kettle #7": 0
      }
    },
    
    "issues": {
      "blockers": [
        {
          "id": "blocker_uuid",
          "type": "obstruction|rfi_needed|material_issue|weather|other",
          "description": "HVAC unit not moved - blocking roof area B",
          "photo_ids": ["photo_uuid_4"],
          "rfi_generated": true,
          "rfi_id": "rfi_uuid",
          "resolved": false,
          "resolution_notes": null
        }
      ],
      "safety_incidents": [],
      "quality_issues": []
    },
    
    "photos": [
      {
        "id": "photo_uuid",
        "category": "site_conditions|work_progress|material|safety|delivery|issue",
        "timestamp": "ISO-8601",
        "gps": {
          "latitude": 39.2904,
          "longitude": -76.6122
        },
        "device_id": "device_uuid",
        "user_id": "employee_id",
        "file_hash": "sha256_hash",
        "exif_preserved": true,
        "storage_url": "s3://bucket/path",
        "caption": "TPO installation zone 2 complete",
        "linked_to": {
          "type": "work_item|delivery|issue",
          "id": "related_uuid"
        }
      }
    ],
    
    "signatures": {
      "foreman": {
        "employee_id": "emp_uuid",
        "signed_at": "ISO-8601",
        "signature_image": "base64 or url",
        "ip_address": "192.168.1.100",
        "device_id": "device_uuid"
      },
      "guest_inspector": {
        "name": "Bob Johnson",
        "company": "FM Global",
        "signed_at": "ISO-8601",
        "inspection_type": "deck_inspection",
        "result": "passed|failed|conditional",
        "notes": "Deck inspection passed - clear to proceed with insulation"
      }
    },
    
    "notes_for_tomorrow": "Continue TPO installation in zone 4. Crane scheduled for 7 AM."
  }
}
```

### 2.2 SSOT Cascade Rules

```
DAILY LOG DATA FLOWS:
═════════════════════

Daily Log Submitted ──►
│
├──► SOV Updates
│    └── percent_complete_update → SOV line items
│    └── materials_installed → SOV work completed
│    └── stored_materials → SOV materials stored
│
├──► Weather Delay Log
│    └── If delay_claimed = true → Weather Delay Record created
│    └── Auto-links weather data as documentation
│
├──► Pay Application
│    └── Progress updates feed G702 calculations
│    └── Stored materials feed G702 materials column
│
├──► RFI Queue (if blocker)
│    └── blocker → Draft RFI for PM review
│
├──► Labor Tracking
│    └── crew_members.hours → Labor budget vs actual
│
├──► Safety Log
│    └── jha_completed → Safety compliance record
│    └── safety_incidents → Incident report workflow
│
└──► Material Verification
     └── deliveries_received → Delivery log
     └── Submittal verification status
```

### 2.3 Photo Chain of Custody Implementation

```javascript
// Photo Capture Flow (React Native / PWA)

const capturePhoto = async (category) => {
  // 1. Capture image with native camera
  const photo = await Camera.takePicture({
    quality: 0.8,
    exifData: true  // Preserve original EXIF
  });
  
  // 2. Immediately extract and verify EXIF
  const exif = await extractEXIF(photo);
  const gps = {
    latitude: exif.GPSLatitude,
    longitude: exif.GPSLongitude,
    timestamp: exif.DateTimeOriginal
  };
  
  // 3. Verify GPS is within job site bounds
  const jobSite = await getJobSiteGeofence(currentJobId);
  const onSite = isWithinGeofence(gps, jobSite);
  
  if (!onSite) {
    // Flag photo but still allow capture
    photo.flags = ['OUTSIDE_GEOFENCE'];
  }
  
  // 4. Generate file hash BEFORE any processing
  const fileHash = await sha256(photo.base64);
  
  // 5. Create immutable metadata record
  const photoRecord = {
    id: uuid(),
    timestamp: new Date().toISOString(),
    gps: gps,
    device_id: await getDeviceId(),
    user_id: currentUser.id,
    file_hash: fileHash,
    exif_original: exif,
    category: category,
    job_id: currentJobId,
    flags: photo.flags || []
  };
  
  // 6. Upload directly to secure storage
  // NO local file save, NO file transfer
  const storageUrl = await uploadToSecureStorage(photo, photoRecord);
  
  // 7. Log to blockchain/immutable log (optional)
  await logToAuditTrail({
    action: 'PHOTO_CAPTURED',
    photo_id: photoRecord.id,
    hash: fileHash,
    timestamp: photoRecord.timestamp
  });
  
  return { photoRecord, storageUrl };
};
```

---

## PART 3: UI/UX SPECIFICATION

### 3.1 "Big Button" Mode Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ROOFIO DIGITAL FOREMAN                          📍 JHU Library - Roof A   │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │     ⚠️  JHA REQUIRED BEFORE STARTING DAILY LOG                     │   │
│  │                                                                     │   │
│  │     ┌───────────────────────────────────────────────────────┐      │   │
│  │     │                                                       │      │   │
│  │     │        [  🔒 COMPLETE JHA TO UNLOCK  ]               │      │   │
│  │     │                                                       │      │   │
│  │     └───────────────────────────────────────────────────────┘      │   │
│  │                                                                     │   │
│  │     Today's JHA: TPO Membrane Installation                         │   │
│  │     Hazards Auto-Detected: 4                                       │   │
│  │     └── Chemical fumes (adhesive)                                  │   │
│  │     └── Fall hazard (>6ft)                                         │   │
│  │     └── Hot surface (heat welding)                                 │   │
│  │     └── Heavy lifting                                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ▼ AFTER JHA COMPLETED ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  ROOFIO DIGITAL FOREMAN                          📍 JHU Library - Roof A   │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  Weather: 52°F | Wind: 8mph | Clear              Auto-captured: 12:00 PM  │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │             │  │             │  │             │  │             │       │
│  │   📸        │  │   👷        │  │   📦        │  │   ⚠️        │       │
│  │   PHOTO     │  │   CREW      │  │  MATERIAL   │  │   BLOCKER   │       │
│  │             │  │   (6)       │  │  RECEIVED   │  │             │       │
│  │             │  │             │  │             │  │             │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  PROGRESS: ████████████████░░░░░░░░░░░░░░░░░░░  35%                │   │
│  │                                                                     │   │
│  │  [  ◄  ]  Slide to update progress  [  ►  ]                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  🎤 VOICE NOTE: "Installed 2500 square feet of TPO on zones..."    │   │
│  │                                                                     │   │
│  │  [  HOLD TO RECORD  ]                                               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  [        ✅ SUBMIT DAILY LOG & SIGN        ]                      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Material Verification Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MATERIAL VERIFICATION                                      📍 Staging Area │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  SCAN MATERIAL BARCODE                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │                    [  📷 SCAN BARCODE  ]                           │   │
│  │                                                                     │   │
│  │                    ─── OR ENTER MANUALLY ───                       │   │
│  │                                                                     │   │
│  │                    [___________________]                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                              ▼ AFTER SCAN ▼                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ✅ MATERIAL VERIFIED                                              │   │
│  │                                                                     │   │
│  │  SCANNED:                                                          │   │
│  │  └── Carlisle TPO 60mil White                                      │   │
│  │  └── Lot #: 2025-1207-A                                            │   │
│  │  └── Mfg Date: 2025-10-15                                          │   │
│  │                                                                     │   │
│  │  MATCHES SUBMITTAL:                                                │   │
│  │  └── Submittal #001 - TPO Membrane                                 │   │
│  │  └── Approved: 2025-11-01                                          │   │
│  │  └── Spec Section: 07 54 00                                        │   │
│  │                                                                     │   │
│  │  QUANTITY:                                                         │   │
│  │  └── Delivery Ticket: 5,000 SF                                     │   │
│  │  └── [  VERIFY QUANTITY  ] or [  REPORT DISCREPANCY  ]            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [  📸 PHOTO LABEL  ]    [  📸 PHOTO PALLET  ]    [  ✅ CONFIRM  ]         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ▼ IF MISMATCH ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️ MATERIAL MISMATCH DETECTED                                              │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  SCANNED:                                                                   │
│  └── GAF EverGuard TPO 60mil                                               │
│                                                                             │
│  APPROVED SUBMITTAL REQUIRES:                                               │
│  └── Carlisle TPO 60mil White                                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ❌ THIS MATERIAL CANNOT BE INSTALLED                              │   │
│  │                                                                     │   │
│  │  Options:                                                          │   │
│  │  └── [  REJECT DELIVERY  ]                                         │   │
│  │  └── [  GENERATE RFI FOR SUBSTITUTION  ]                           │   │
│  │  └── [  CONTACT PROJECT MANAGER  ]                                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Guest Inspector Mode

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ROOFIO - INSPECTOR ACCESS                              📍 JHU Library     │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  HOLD POINT INSPECTION                                                      │
│                                                                             │
│  Inspection Type: DECK INSPECTION                                           │
│  Required Before: Insulation Installation                                   │
│  Spec Reference: 07 22 00 - Roof Deck Insulation                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  INSPECTOR INFORMATION                                             │   │
│  │                                                                     │   │
│  │  Name:     [_______________________]                               │   │
│  │  Company:  [_______________________]                               │   │
│  │  License#: [_______________________] (optional)                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  INSPECTION CHECKLIST                                              │   │
│  │                                                                     │   │
│  │  ☑ Deck surface clean and dry                                      │   │
│  │  ☑ No ponding water observed                                       │   │
│  │  ☑ Deck fasteners properly installed                               │   │
│  │  ☐ Penetrations properly flashed                                   │   │
│  │  ☑ Slope verified per drawings                                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  RESULT:  ○ PASSED   ○ CONDITIONAL   ○ FAILED                      │   │
│  │                                                                     │   │
│  │  NOTES:                                                            │   │
│  │  [_______________________________________________]                  │   │
│  │  [_______________________________________________]                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [  📸 ATTACH PHOTOS  ]              [  ✍️ SIGN & SUBMIT  ]                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PART 4: OFFLINE-FIRST ARCHITECTURE

### 4.1 Sync Strategy

```
OFFLINE-FIRST DATA FLOW
═══════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  LOCAL DEVICE                          │           CLOUD                    │
│  ═════════════                         │           ═════                    │
│                                        │                                    │
│  ┌──────────────┐                      │    ┌──────────────────────────┐   │
│  │   SQLite     │                      │    │     Supabase             │   │
│  │   Database   │◄────── SYNC ────────►│    │     PostgreSQL           │   │
│  │              │                      │    │                          │   │
│  │  - Daily Logs│                      │    │  - All project data      │   │
│  │  - Photos    │                      │    │  - Photo storage         │   │
│  │  - JHAs      │                      │    │  - Audit logs            │   │
│  │  - Crew      │                      │    │                          │   │
│  └──────────────┘                      │    └──────────────────────────┘   │
│         │                              │              │                    │
│         ▼                              │              ▼                    │
│  ┌──────────────┐                      │    ┌──────────────────────────┐   │
│  │   Pending    │                      │    │     Sync Queue           │   │
│  │   Queue      │─────► ON CONNECT ───►│    │     Processor            │   │
│  │              │                      │    │                          │   │
│  │  - Unsent    │                      │    │  - Conflict resolution   │   │
│  │    records   │                      │    │  - Deduplication         │   │
│  │  - Unuploaded│                      │    │  - Validation            │   │
│  │    photos    │                      │    │                          │   │
│  └──────────────┘                      │    └──────────────────────────┘   │
│                                        │                                    │
└─────────────────────────────────────────────────────────────────────────────┘

SYNC RULES:
1. All writes go to local DB first
2. Queue tracks pending sync items
3. On connectivity, push queue to cloud
4. Conflict resolution: Last-write-wins with audit trail
5. Photos: Upload in background, low priority
6. Critical data (signatures, JHA): High priority sync
```

### 4.2 Data Integrity

```javascript
// Offline-capable data write
const saveDailyLog = async (dailyLog) => {
  // 1. Generate ID locally if new
  if (!dailyLog.id) {
    dailyLog.id = uuid();
    dailyLog.created_at = new Date().toISOString();
  }
  
  // 2. Save to local SQLite
  await localDB.dailyLogs.put(dailyLog);
  
  // 3. Add to sync queue
  await syncQueue.add({
    type: 'DAILY_LOG',
    id: dailyLog.id,
    action: 'UPSERT',
    data: dailyLog,
    created_at: new Date().toISOString(),
    priority: dailyLog.status === 'submitted' ? 'HIGH' : 'NORMAL'
  });
  
  // 4. Trigger sync if online
  if (navigator.onLine) {
    syncManager.triggerSync();
  }
  
  // 5. Return immediately (optimistic)
  return dailyLog;
};
```

---

## PART 5: IMPLEMENTATION PRIORITY

### Phase 1: Core Legal Shield (Weeks 1-2)
```
□ Daily Log with auto-weather capture
□ Photo capture with GPS/timestamp
□ Digital signature capability
□ PDF export for daily report
□ Offline-first local storage
```

### Phase 2: Safety Gate (Week 3)
```
□ JHA form with hazard library
□ JHA-gates-daily-log logic
□ Crew acknowledgment signatures
□ Safety checklist templates
```

### Phase 3: Material Verification (Week 4)
```
□ Barcode/QR scanner
□ Submittal cross-reference
□ Mismatch flagging
□ RFI auto-generation
```

### Phase 4: Inspector Mode (Week 5)
```
□ Guest access without account
□ Hold point checklists
□ Inspector signature
□ Result feeds to daily log
```

### Phase 5: Spec Integration (Week 6)
```
□ Weather delay claim generator
□ Progress → SOV linkage
□ Pay App integration
□ Spec-compliant PDF reports
```

---

## PART 6: SPECIFICATION ADOPTION STRATEGY

### 6.1 Target Firms for Pilot Specs

```
TIER 1: INSTITUTIONAL OWNERS (Risk-Averse)
├── Universities (JHU, UMass)
├── Hospitals
├── Government facilities
└── Why: Legal liability drives spec requirements

TIER 2: INSURANCE-DRIVEN
├── FM Global insured properties
├── Self-insured corporations
└── Why: Claims documentation requirements

TIER 3: PROGRESSIVE ARCHITECTS
├── Gensler, HOK, Perkins&Will
├── Spec writers who embrace digital
└── Why: Efficiency in administration
```

### 6.2 Value Proposition by Stakeholder

```
FOR OWNERS (OCIP):
"This platform pays for itself by reducing your OCIP premiums.
Every JHA logged, every weather capture, every silica verification
is documentation that protects you from claims and lawsuits."

FOR OWNERS (NON-OCIP):
"Eliminate weather delay disputes with automated, 
GPS-verified documentation that meets AIA A201 15.1.6.2 
requirements for weather delay claims."

FOR ARCHITECTS:
"Verify field compliance without site visits. 
JHA-gated daily logs ensure safety protocols are 
followed before work begins. Performance-based specs
protect you from brand-name liability."

FOR GCs:
"Get paid faster with progress photos that link 
directly to pay applications. Material verification 
prevents costly substitution mistakes."

FOR INSURANCE:
"Chain-of-custody photo documentation reduces 
disputed claims. Every photo includes immutable 
GPS, timestamp, and user identification.
Silica tracking creates OSHA compliance proof."
```

---

## APPENDIX A: SPEC LANGUAGE - COPY/PASTE READY

### Option 1: Performance-Based (Recommended)
*Insert into Section 01 32 26:*

```
2.1 DIGITAL FIELD DOCUMENTATION PLATFORM

A. General: Contractor shall provide a cloud-based digital platform 
   for daily field reporting, accessible via mobile devices (iOS/Android) 
   and web browsers.

B. Performance Requirements: The platform must provide the following 
   capabilities to ensure data integrity:

   1. Automated Weather Logging: System must automatically record local 
      weather conditions (Temperature, Precipitation, Wind Speed) at 
      minimum 4-hour intervals using GPS geolocation. Manual entry of 
      weather data is not permitted for delay claims.

   2. Immutable Photo Documentation: All progress photos must be natively 
      stamped with GPS Coordinates, User ID, and Server-side timestamp.

   3. Safety Gating: System must prevent the creation of a "Daily 
      Construction Report" until the daily "Job Hazard Analysis" (JHA) 
      has been digitally signed by the site superintendent.

   4. Material Chain of Custody: System must support barcode/QR scanning 
      of delivered materials to verify against approved Submittals.

C. Platforms meeting these requirements: ROOFIO or approved equal.
```

### Option 2: Direct Specification
*Insert into Section 01 31 00:*

```
1.5 DIGITAL PROJECT MANAGEMENT PLATFORM

A. Contractor shall utilize ROOFIO (www.roofio.com) or approved equal 
   cloud-based field documentation platform with the following minimum 
   capabilities:
   
   1. Offline-first operation with automatic synchronization
   2. GPS-geotagged photographic documentation
   3. Automatic weather data capture from NOAA or equivalent
   4. Digital signature capability for daily reports
   5. Material verification via barcode scanning
   6. Job Hazard Analysis (JHA) workflow
   7. Third-party inspector guest access
   8. Immutable audit trail for all documentation
   
B. All daily field reports shall be generated through the approved 
   platform and submitted within 24 hours of work completion.

C. Photographic documentation shall be captured exclusively through 
   the approved platform to maintain chain of custody.
```

---

## APPENDIX B: OCIP SALES SCRIPT

### For Owners/Developers

```
"I'd like to show you how our Digital Foreman module can reduce 
your OCIP premiums on [Project Name].

Your current risk profile includes:
- Weather delay disputes (we eliminate with auto-capture)
- Safety incident exposure (we document with JHA gating)
- Silica lawsuit liability (we track with OSHA-compliant logs)
- Material fraud/substitution (we verify with barcode scanning)

Every piece of documentation we generate is legally defensible:
- GPS-stamped photos with chain of custody
- Server-side timestamps (not device time)
- SHA-256 file hashes for authenticity
- Immutable audit trails

Insurance companies LOVE this. It's not just convenience—it's 
risk reduction that translates directly to premium savings.

Would you like me to connect you with our team to discuss 
implementation, or would you prefer to have your Architect 
include the performance specs in Division 01?"
```

### For Architects

```
"I'm not asking you to specify a brand name—I know that creates 
liability for you. Instead, I'm asking you to specify the 
PERFORMANCE requirements that protect your client.

Consider adding to Section 01 32 26:

'System must automatically record local weather conditions at 
minimum 4-hour intervals using GPS geolocation. Manual entry 
of weather data is not permitted for delay claims.'

This language protects the Owner from fraudulent delay claims 
without naming any specific software. If a contractor wants 
to use a different system, they just need to meet the same 
performance standards.

The Owner's insurance administrator will appreciate this too—
especially on OCIP projects."
```

---

## APPENDIX C: IMPLEMENTATION CHECKLIST

### Phase 1: Risk Shield Core (Weeks 1-2)
```
□ Database schema (PostgreSQL/Supabase)
□ Gatekeeper logic (JHA locks daily log)
□ JHA form with hazard library
□ Digital signature capture
□ GPS verification (geofencing)
```

### Phase 2: Weather Truth Agent (Week 3)
```
□ Weather API integration (OpenWeatherMap)
□ Scheduled captures (12pm, 4pm cron)
□ Auto-flag logic (wind/precip thresholds)
□ PM dashboard alerts
□ Weather delay claim generator
```

### Phase 3: Photo Chain of Custody (Week 4)
```
□ Camera capture with EXIF preservation
□ GPS extraction and verification
□ SHA-256 hash at capture
□ Direct-to-cloud upload
□ Chain of custody report generator
```

### Phase 4: Silica Tracker (Week 5)
```
□ Silica verification form
□ Control method selection
□ Photo documentation requirement
□ 10 AM alert system
□ OSHA compliance report generator
```

### Phase 5: Material Verification (Week 6)
```
□ Barcode/QR scanner
□ Submittal cross-reference
□ Mismatch flagging
□ Auto-RFI generation
□ Delivery log with photos
```

---

## APPENDIX D: TECHNOLOGY NOTES

### Cron Jobs Required
```
# Weather capture - 12 PM and 4 PM local time
0 12,16 * * * curl -X POST https://api.roofio.com/weather/scheduled-capture

# Silica verification alert - 10 AM local time
0 10 * * 1-5 curl -X POST https://api.roofio.com/silica/morning-alert-check

# JHA expiration check - midnight
0 0 * * * curl -X POST https://api.roofio.com/jha/expire-previous-day
```

### Weather API Configuration
```javascript
// OpenWeatherMap One Call API 3.0
const WEATHER_API_BASE = 'https://api.openweathermap.org/data/3.0/onecall';

const fetchWeatherFromAPI = async (lat, lng) => {
  const response = await fetch(
    `${WEATHER_API_BASE}?lat=${lat}&lon=${lng}&appid=${API_KEY}&units=imperial`
  );
  const data = await response.json();
  
  return {
    temp_f: data.current.temp,
    humidity: data.current.humidity,
    wind_mph: data.current.wind_speed,
    wind_gust_mph: data.current.wind_gust || null,
    wind_dir: degreesToCardinal(data.current.wind_deg),
    precip_inches: (data.current.rain?.['1h'] || 0) / 25.4, // mm to inches
    conditions: data.current.weather[0].description,
    visibility: data.current.visibility / 1609.34, // meters to miles
    raw: data
  };
};
```

---

**END OF SPECIFICATION**

*Document prepared for: Lefebvre Design Solutions / ROOFIO*
*Version 2.0 - December 2025*
*Ready for Claude Code implementation*

---

## QUICK REFERENCE: THE THREE RISK SHIELD FEATURES

| Feature | Trigger | Action | Output |
|---------|---------|--------|--------|
| **GATEKEEPER** | User opens app | Lock all features | `{ "safety_verified": true, "timestamp": "ISO-8601" }` |
| **WEATHER TRUTH** | 12pm/4pm auto | Fetch weather, check thresholds | PM dashboard alert if flagged |
| **SILICA TRACKER** | Daily (if scope includes cutting) | Require verification form | OSHA-compliant documentation |

**The Risk Shield angle makes ROOFIO an insurance policy, not just a convenience app.**
