-- =============================================================================
-- ROOFIO Form Templates - Real Roofing Industry Forms
-- Run this in Supabase SQL Editor to create production-ready form templates
-- =============================================================================

-- Your Agency ID
DO $$
DECLARE
    agency UUID := '3cfd5441-d5fc-4857-8fb9-3dc7be7a37d5';
BEGIN

-- -----------------------------------------------------------------------------
-- 1. DAILY REPORT / DAILY LOG (Field Documentation)
-- -----------------------------------------------------------------------------
INSERT INTO form_templates (
    template_id, agency_id, name, form_type, description, is_custom, status, is_default,
    fields, roofio_additions, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    agency,
    'Daily Report / Log',
    'daily_report',
    'Comprehensive daily field report documenting weather, manpower, equipment, and work performed',
    false,
    'active',
    true,
    '[
        {
            "id": "projectId",
            "name": "project",
            "label": "Project",
            "type": "lookup",
            "required": true,
            "section": "Project Context"
        },
        {
            "id": "reportDate",
            "name": "report_date",
            "label": "Report Date",
            "type": "date",
            "required": true,
            "section": "Project Context"
        },
        {
            "id": "conditions",
            "name": "weather_conditions",
            "label": "Weather Conditions",
            "type": "select",
            "options": ["Clear", "Cloudy", "Rain", "Snow", "Fog", "Windy", "Hot (>90°F)", "Cold (<32°F)"],
            "required": true,
            "section": "Weather Conditions"
        },
        {
            "id": "tempHigh",
            "name": "temp_high",
            "label": "High Temp (°F)",
            "type": "number",
            "section": "Weather Conditions"
        },
        {
            "id": "tempLow",
            "name": "temp_low",
            "label": "Low Temp (°F)",
            "type": "number",
            "section": "Weather Conditions"
        },
        {
            "id": "precipitation",
            "name": "precipitation",
            "label": "Precipitation",
            "type": "text",
            "placeholder": "e.g., 0.5 inches rain, none",
            "section": "Weather Conditions"
        },
        {
            "id": "windSpeed",
            "name": "wind_speed",
            "label": "Wind Speed (MPH)",
            "type": "number",
            "section": "Weather Conditions"
        },
        {
            "id": "crewCount",
            "name": "crew_count",
            "label": "Total Crew on Site",
            "type": "number",
            "required": true,
            "section": "Manpower & Equipment"
        },
        {
            "id": "crewDetails",
            "name": "crew_details",
            "label": "Crew Breakdown",
            "type": "textarea",
            "placeholder": "Foreman: 1, Journeymen: 4, Apprentices: 2",
            "section": "Manpower & Equipment"
        },
        {
            "id": "equipmentUsed",
            "name": "equipment_used",
            "label": "Equipment Used",
            "type": "textarea",
            "placeholder": "Kettle (8 hrs), Crane (4 hrs), Forklift (2 hrs)",
            "section": "Manpower & Equipment"
        },
        {
            "id": "hoursWorked",
            "name": "hours_worked",
            "label": "Total Man-Hours",
            "type": "number",
            "section": "Manpower & Equipment"
        },
        {
            "id": "workNarrative",
            "name": "work_narrative",
            "label": "Work Performed Today",
            "type": "textarea",
            "required": true,
            "placeholder": "Detailed description of work completed. Include areas, quantities, and progress.",
            "section": "Work Log"
        },
        {
            "id": "squaresCompleted",
            "name": "squares_completed",
            "label": "Squares Completed",
            "type": "number",
            "section": "Work Log"
        },
        {
            "id": "materialsReceived",
            "name": "materials_received",
            "label": "Materials Received",
            "type": "textarea",
            "placeholder": "List deliveries received today",
            "section": "Work Log"
        },
        {
            "id": "delays",
            "name": "delays",
            "label": "Delays / Issues",
            "type": "textarea",
            "placeholder": "Document any delays, weather stoppages, or issues",
            "section": "Work Log"
        },
        {
            "id": "safetyIncidents",
            "name": "safety_incidents",
            "label": "Safety Incidents",
            "type": "select",
            "options": ["None", "Near Miss", "First Aid", "Recordable"],
            "required": true,
            "section": "Safety"
        },
        {
            "id": "safetyNotes",
            "name": "safety_notes",
            "label": "Safety Notes",
            "type": "textarea",
            "section": "Safety"
        },
        {
            "id": "photos",
            "name": "photos",
            "label": "Progress Photos",
            "type": "photo",
            "section": "Documentation"
        },
        {
            "id": "foremanSignature",
            "name": "foreman_signature",
            "label": "Foreman Signature",
            "type": "signature",
            "required": true,
            "section": "Approval"
        }
    ]'::jsonb,
    '{"logo": true, "timestamp": true, "gps": true, "weather_auto": true}'::jsonb,
    NOW(),
    NOW()
);

-- -----------------------------------------------------------------------------
-- 2. REQUEST FOR INFORMATION (RFI) (Project Administration)
-- -----------------------------------------------------------------------------
INSERT INTO form_templates (
    template_id, agency_id, name, form_type, description, is_custom, status, is_default,
    fields, roofio_additions, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    agency,
    'Request for Information (RFI)',
    'rfi',
    'Formal request for clarification on project documents, specifications, or design intent',
    false,
    'active',
    true,
    '[
        {
            "id": "rfiNumber",
            "name": "rfi_number",
            "label": "RFI Number",
            "type": "text",
            "required": true,
            "placeholder": "Auto-generated or enter manually",
            "section": "RFI Details"
        },
        {
            "id": "projectLookup",
            "name": "project",
            "label": "Project",
            "type": "lookup",
            "required": true,
            "section": "RFI Details"
        },
        {
            "id": "dateIssued",
            "name": "date_issued",
            "label": "Date Issued",
            "type": "date",
            "required": true,
            "section": "RFI Details"
        },
        {
            "id": "responseDeadline",
            "name": "response_deadline",
            "label": "Response Due Date",
            "type": "date",
            "required": true,
            "section": "RFI Details"
        },
        {
            "id": "priority",
            "name": "priority",
            "label": "Priority",
            "type": "select",
            "options": ["Low", "Medium", "High", "Critical"],
            "required": true,
            "section": "RFI Details"
        },
        {
            "id": "addressedTo",
            "name": "addressed_to",
            "label": "Addressed To",
            "type": "select",
            "options": ["Architect", "Engineer", "Owner", "General Contractor", "Consultant"],
            "required": true,
            "section": "RFI Details"
        },
        {
            "id": "specSection",
            "name": "spec_section",
            "label": "Specification Section",
            "type": "text",
            "placeholder": "e.g., 07 54 13 (TPO Roofing)",
            "section": "Question & Reference"
        },
        {
            "id": "drawingReference",
            "name": "drawing_reference",
            "label": "Drawing Reference",
            "type": "text",
            "placeholder": "e.g., A-501, Detail 3",
            "section": "Question & Reference"
        },
        {
            "id": "subject",
            "name": "subject",
            "label": "Subject",
            "type": "text",
            "required": true,
            "placeholder": "Brief description of the question",
            "section": "Question & Reference"
        },
        {
            "id": "questionDetail",
            "name": "question_detail",
            "label": "Detailed Question",
            "type": "textarea",
            "required": true,
            "placeholder": "Provide complete description of the information needed and why",
            "section": "Question & Reference"
        },
        {
            "id": "suggestedAnswer",
            "name": "suggested_answer",
            "label": "Suggested Solution",
            "type": "textarea",
            "placeholder": "Optional: Propose a solution for consideration",
            "section": "Question & Reference"
        },
        {
            "id": "attachments",
            "name": "attachments",
            "label": "Attachments (Photos/Sketches)",
            "type": "photo",
            "section": "Question & Reference"
        },
        {
            "id": "scheduleImpact",
            "name": "schedule_impact",
            "label": "Schedule Impact (Days)",
            "type": "number",
            "placeholder": "0 if no impact",
            "section": "Impact Assessment"
        },
        {
            "id": "costImpact",
            "name": "cost_impact",
            "label": "Potential Cost Impact ($)",
            "type": "number",
            "placeholder": "Estimate for potential Change Order",
            "section": "Impact Assessment"
        },
        {
            "id": "impactNotes",
            "name": "impact_notes",
            "label": "Impact Description",
            "type": "textarea",
            "placeholder": "Describe how delay affects schedule or cost",
            "section": "Impact Assessment"
        },
        {
            "id": "submittedBy",
            "name": "submitted_by",
            "label": "Submitted By",
            "type": "text",
            "required": true,
            "section": "Submission"
        },
        {
            "id": "signature",
            "name": "signature",
            "label": "Signature",
            "type": "signature",
            "required": true,
            "section": "Submission"
        }
    ]'::jsonb,
    '{"logo": true, "timestamp": true, "tracking_number": true}'::jsonb,
    NOW(),
    NOW()
);

-- -----------------------------------------------------------------------------
-- 3. JOB HAZARD ANALYSIS (JHA) (Safety)
-- -----------------------------------------------------------------------------
INSERT INTO form_templates (
    template_id, agency_id, name, form_type, description, is_custom, status, is_default,
    fields, roofio_additions, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    agency,
    'Job Hazard Analysis (JHA)',
    'jha',
    'Pre-task safety analysis identifying hazards and control measures for roofing operations',
    false,
    'active',
    true,
    '[
        {
            "id": "projectLookup",
            "name": "project",
            "label": "Project",
            "type": "lookup",
            "required": true,
            "section": "Task Identification"
        },
        {
            "id": "date",
            "name": "date",
            "label": "Date",
            "type": "date",
            "required": true,
            "section": "Task Identification"
        },
        {
            "id": "taskName",
            "name": "task_name",
            "label": "Task Being Analyzed",
            "type": "select",
            "options": [
                "Hot Asphalt Application",
                "Tear-off Operations",
                "TPO/PVC Membrane Installation",
                "EPDM Installation",
                "Modified Bitumen Torch Application",
                "Metal Roof Installation",
                "Fall Protection Setup",
                "Material Handling/Hoisting",
                "Kettle Operations",
                "Roof Penetration Work",
                "Flashing Installation",
                "Gutter/Downspout Work",
                "Spray Foam Application",
                "Coating Application"
            ],
            "required": true,
            "section": "Task Identification"
        },
        {
            "id": "workArea",
            "name": "work_area",
            "label": "Work Area/Location",
            "type": "text",
            "required": true,
            "placeholder": "e.g., Section A - East Wing, Roof Level 3",
            "section": "Task Identification"
        },
        {
            "id": "crewLead",
            "name": "crew_lead",
            "label": "Crew Lead/Foreman",
            "type": "text",
            "required": true,
            "section": "Task Identification"
        },
        {
            "id": "hazard1Step",
            "name": "hazard_1_step",
            "label": "Step 1: Job Step",
            "type": "text",
            "placeholder": "e.g., Set up fall protection",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard1Risk",
            "name": "hazard_1_risk",
            "label": "Step 1: Hazards",
            "type": "textarea",
            "placeholder": "e.g., Falls from height, anchor point failure",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard1Control",
            "name": "hazard_1_control",
            "label": "Step 1: Control Measures",
            "type": "textarea",
            "placeholder": "e.g., Inspect anchors, use 6ft shock lanyard, 100% tie-off",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard2Step",
            "name": "hazard_2_step",
            "label": "Step 2: Job Step",
            "type": "text",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard2Risk",
            "name": "hazard_2_risk",
            "label": "Step 2: Hazards",
            "type": "textarea",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard2Control",
            "name": "hazard_2_control",
            "label": "Step 2: Control Measures",
            "type": "textarea",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard3Step",
            "name": "hazard_3_step",
            "label": "Step 3: Job Step",
            "type": "text",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard3Risk",
            "name": "hazard_3_risk",
            "label": "Step 3: Hazards",
            "type": "textarea",
            "section": "Hazard Analysis"
        },
        {
            "id": "hazard3Control",
            "name": "hazard_3_control",
            "label": "Step 3: Control Measures",
            "type": "textarea",
            "section": "Hazard Analysis"
        },
        {
            "id": "ppeRequired",
            "name": "ppe_required",
            "label": "Required PPE",
            "type": "multiselect",
            "options": [
                "Hard Hat",
                "Safety Glasses",
                "High-Vis Vest",
                "Gloves (Leather)",
                "Gloves (Chemical)",
                "Steel Toe Boots",
                "Fall Harness",
                "Hearing Protection",
                "Respirator",
                "Face Shield",
                "Knee Pads",
                "Sun Protection"
            ],
            "required": true,
            "section": "PPE Requirements"
        },
        {
            "id": "emergencyProcedure",
            "name": "emergency_procedure",
            "label": "Emergency Procedure",
            "type": "textarea",
            "placeholder": "Location of first aid kit, emergency contact, evacuation route",
            "section": "Emergency Information"
        },
        {
            "id": "crewBriefed",
            "name": "crew_briefed",
            "label": "Crew Briefed?",
            "type": "select",
            "options": ["Yes - All crew members briefed", "Partial - Some absent", "No - Training needed"],
            "required": true,
            "section": "Acknowledgment"
        },
        {
            "id": "crewCount",
            "name": "crew_count",
            "label": "Number of Crew Present",
            "type": "number",
            "required": true,
            "section": "Acknowledgment"
        },
        {
            "id": "foremanSignature",
            "name": "foreman_signature",
            "label": "Foreman Signature",
            "type": "signature",
            "required": true,
            "section": "Acknowledgment"
        },
        {
            "id": "safetyOfficerSignature",
            "name": "safety_officer_signature",
            "label": "Safety Officer Signature (if applicable)",
            "type": "signature",
            "section": "Acknowledgment"
        }
    ]'::jsonb,
    '{"logo": true, "timestamp": true, "gps": true, "safety_header": true}'::jsonb,
    NOW(),
    NOW()
);

-- -----------------------------------------------------------------------------
-- 4. MOISTURE SURVEY REPORT (Quality Control)
-- -----------------------------------------------------------------------------
INSERT INTO form_templates (
    template_id, agency_id, name, form_type, description, is_custom, status, is_default,
    fields, roofio_additions, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    agency,
    'Moisture Survey Report',
    'inspection',
    'Infrared or nuclear moisture detection survey documenting wet areas and repair recommendations',
    false,
    'active',
    false,
    '[
        {
            "id": "projectLookup",
            "name": "project",
            "label": "Project",
            "type": "lookup",
            "required": true,
            "section": "Survey Parameters"
        },
        {
            "id": "surveyDate",
            "name": "survey_date",
            "label": "Survey Date",
            "type": "date",
            "required": true,
            "section": "Survey Parameters"
        },
        {
            "id": "surveyMethod",
            "name": "survey_method",
            "label": "Survey Method",
            "type": "select",
            "options": ["Infrared Thermography", "Nuclear Gauge", "Capacitance Meter", "Core Cut Verification", "Combined Methods"],
            "required": true,
            "section": "Survey Parameters"
        },
        {
            "id": "equipmentUsed",
            "name": "equipment_used",
            "label": "Equipment Used",
            "type": "text",
            "placeholder": "e.g., FLIR E75 Infrared Camera, Tramex Dec Scanner",
            "section": "Survey Parameters"
        },
        {
            "id": "roofSection",
            "name": "roof_section",
            "label": "Roof Section Surveyed",
            "type": "text",
            "required": true,
            "placeholder": "e.g., Building A - Main Roof, Section 1",
            "section": "Survey Parameters"
        },
        {
            "id": "roofSystem",
            "name": "roof_system",
            "label": "Existing Roof System",
            "type": "select",
            "options": ["TPO", "EPDM", "PVC", "Modified Bitumen", "Built-Up Roof (BUR)", "Metal", "Spray Foam", "Shingle", "Unknown"],
            "required": true,
            "section": "Survey Parameters"
        },
        {
            "id": "roofAge",
            "name": "roof_age",
            "label": "Approximate Roof Age (Years)",
            "type": "number",
            "section": "Survey Parameters"
        },
        {
            "id": "totalAreaSurveyed",
            "name": "total_area_surveyed",
            "label": "Total Area Surveyed (SF)",
            "type": "number",
            "required": true,
            "section": "Survey Parameters"
        },
        {
            "id": "weatherConditions",
            "name": "weather_conditions",
            "label": "Weather Conditions During Survey",
            "type": "text",
            "placeholder": "e.g., Clear, 45°F, no precipitation in 48 hrs",
            "section": "Survey Parameters"
        },
        {
            "id": "wetArea1Location",
            "name": "wet_area_1_location",
            "label": "Wet Area #1: Location",
            "type": "text",
            "placeholder": "e.g., NW corner near RTU-3",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea1Size",
            "name": "wet_area_1_size",
            "label": "Wet Area #1: Size (SF)",
            "type": "number",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea1Reading",
            "name": "wet_area_1_reading",
            "label": "Wet Area #1: Moisture Reading",
            "type": "text",
            "placeholder": "e.g., 28% moisture content",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea2Location",
            "name": "wet_area_2_location",
            "label": "Wet Area #2: Location",
            "type": "text",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea2Size",
            "name": "wet_area_2_size",
            "label": "Wet Area #2: Size (SF)",
            "type": "number",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea2Reading",
            "name": "wet_area_2_reading",
            "label": "Wet Area #2: Moisture Reading",
            "type": "text",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea3Location",
            "name": "wet_area_3_location",
            "label": "Wet Area #3: Location",
            "type": "text",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea3Size",
            "name": "wet_area_3_size",
            "label": "Wet Area #3: Size (SF)",
            "type": "number",
            "section": "Moisture Findings"
        },
        {
            "id": "wetArea3Reading",
            "name": "wet_area_3_reading",
            "label": "Wet Area #3: Moisture Reading",
            "type": "text",
            "section": "Moisture Findings"
        },
        {
            "id": "totalWetArea",
            "name": "total_wet_area",
            "label": "Total Estimated Wet Area (SF)",
            "type": "number",
            "required": true,
            "section": "Moisture Findings"
        },
        {
            "id": "percentageWet",
            "name": "percentage_wet",
            "label": "Percentage of Roof Wet (%)",
            "type": "number",
            "section": "Moisture Findings"
        },
        {
            "id": "thermalImages",
            "name": "thermal_images",
            "label": "Thermal/IR Images",
            "type": "photo",
            "section": "Visual Evidence"
        },
        {
            "id": "visualPhotos",
            "name": "visual_photos",
            "label": "Visual Photographs",
            "type": "photo",
            "section": "Visual Evidence"
        },
        {
            "id": "roofPlan",
            "name": "roof_plan",
            "label": "Marked-Up Roof Plan",
            "type": "photo",
            "section": "Visual Evidence"
        },
        {
            "id": "overallCondition",
            "name": "overall_condition",
            "label": "Overall Roof Condition",
            "type": "select",
            "options": ["Good - Minor repairs needed", "Fair - Moderate repairs needed", "Poor - Major repairs needed", "Failed - Replacement recommended"],
            "required": true,
            "section": "Recommendations"
        },
        {
            "id": "recommendations",
            "name": "recommendations",
            "label": "Repair Recommendations",
            "type": "textarea",
            "required": true,
            "placeholder": "Detail recommended repairs: remove and replace wet insulation, repair membrane, etc.",
            "section": "Recommendations"
        },
        {
            "id": "estimatedRepairCost",
            "name": "estimated_repair_cost",
            "label": "Estimated Repair Cost ($)",
            "type": "number",
            "section": "Recommendations"
        },
        {
            "id": "urgency",
            "name": "urgency",
            "label": "Repair Urgency",
            "type": "select",
            "options": ["Immediate - Active leak", "Urgent - Within 30 days", "Scheduled - Within 90 days", "Monitor - Annual re-survey"],
            "required": true,
            "section": "Recommendations"
        },
        {
            "id": "inspectorName",
            "name": "inspector_name",
            "label": "Inspector Name",
            "type": "text",
            "required": true,
            "section": "Certification"
        },
        {
            "id": "certifications",
            "name": "certifications",
            "label": "Inspector Certifications",
            "type": "text",
            "placeholder": "e.g., Level II Thermographer, RRC",
            "section": "Certification"
        },
        {
            "id": "inspectorSignature",
            "name": "inspector_signature",
            "label": "Inspector Signature",
            "type": "signature",
            "required": true,
            "section": "Certification"
        }
    ]'::jsonb,
    '{"logo": true, "timestamp": true, "gps": true, "qc_watermark": true}'::jsonb,
    NOW(),
    NOW()
);

RAISE NOTICE 'Successfully created 4 form templates for agency %', agency;

END $$;

-- Verify the inserts
SELECT template_id, name, form_type, status, is_default
FROM form_templates
WHERE agency_id = '3cfd5441-d5fc-4857-8fb9-3dc7be7a37d5'
ORDER BY created_at DESC;
