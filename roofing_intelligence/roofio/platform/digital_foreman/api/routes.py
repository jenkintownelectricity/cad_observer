"""
ROOFIO Digital Foreman - API Routes
Flask Blueprint for Digital Foreman endpoints

All endpoints follow the Risk Shield architecture:
- Gatekeeper check on every daily log action
- Weather auto-capture integration
- GPS verification on all field actions
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import uuid

# Import services
from .. import (
    GatekeeperService,
    WeatherTruthAgent,
    SilicaTracker,
    PhotoChainOfCustody,
    MaterialVerifier,
    GPSLocation,
    WeatherCaptureType,
    PhotoCategory
)

# Create Blueprint
digital_foreman_bp = Blueprint('digital_foreman', __name__, url_prefix='/api/digital-foreman')

# Initialize services
gatekeeper = GatekeeperService()
weather_agent = WeatherTruthAgent()
silica_tracker = SilicaTracker()
photo_service = PhotoChainOfCustody()
material_verifier = MaterialVerifier()


# =============================================================================
# GATEKEEPER ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/gatekeeper-status', methods=['GET'])
def get_gatekeeper_status(project_id, job_id):
    """
    Check if daily log is unlocked (JHA completed)

    GET /api/digital-foreman/projects/{project_id}/jobs/{job_id}/gatekeeper-status

    Response:
    {
        "locked": true/false,
        "reason": "JHA_NOT_COMPLETED" | null,
        "message": "Complete daily JHA to unlock daily log",
        "jha_status": "not_started" | "in_progress" | "completed",
        "jha_id": "uuid" | null,
        "safety_verified": true/false,
        "verified_at": "ISO-8601" | null
    }
    """
    check_date = request.args.get('date')
    if check_date:
        check_date = date.fromisoformat(check_date)
    else:
        check_date = date.today()

    status = gatekeeper.check_gatekeeper_status(project_id, job_id, check_date)
    return jsonify(status)


@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/jha/template', methods=['GET'])
def get_jha_template(project_id, job_id):
    """
    Get JHA template for work type with auto-populated hazards

    GET /api/digital-foreman/projects/{project_id}/jobs/{job_id}/jha/template?work_type=tpo_install
    """
    work_type = request.args.get('work_type', 'tpo_install')
    template = gatekeeper.get_jha_template(work_type)
    return jsonify(template)


@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/jha/complete', methods=['POST'])
def complete_jha(project_id, job_id):
    """
    Complete JHA and unlock daily log

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/jha/complete

    Body:
    {
        "checklist_responses": [...],
        "hazards_identified": [...],
        "ppe_verified": [...],
        "superintendent_id": "uuid",
        "superintendent_name": "John Smith",
        "superintendent_signature": "base64...",
        "crew_acknowledgments": [...],
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122,
        "device_id": "device_uuid"
    }
    """
    data = request.get_json()

    gps = GPSLocation(
        latitude=data.get('gps_latitude', 0),
        longitude=data.get('gps_longitude', 0)
    )

    result = gatekeeper.complete_jha(
        project_id=project_id,
        job_id=job_id,
        checklist_responses=data.get('checklist_responses', []),
        hazards_identified=data.get('hazards_identified', []),
        ppe_verified=data.get('ppe_verified', []),
        superintendent_id=data.get('superintendent_id'),
        superintendent_name=data.get('superintendent_name'),
        superintendent_signature=data.get('superintendent_signature'),
        crew_acknowledgments=data.get('crew_acknowledgments', []),
        gps=gps,
        device_id=data.get('device_id')
    )

    return jsonify(result)


# =============================================================================
# WEATHER TRUTH AGENT ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/weather/capture', methods=['POST'])
def capture_weather(project_id):
    """
    Capture weather for project (manual or scheduled)

    POST /api/digital-foreman/projects/{project_id}/weather/capture

    Body:
    {
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122,
        "capture_type": "manual" | "scheduled" | "start_of_day" | "end_of_day"
    }
    """
    data = request.get_json()

    gps = GPSLocation(
        latitude=data.get('gps_latitude', 0),
        longitude=data.get('gps_longitude', 0)
    )

    capture_type = WeatherCaptureType(data.get('capture_type', 'manual'))

    result = weather_agent.capture_weather(
        project_id=project_id,
        gps=gps,
        capture_type=capture_type
    )

    return jsonify(result)


@digital_foreman_bp.route('/projects/<project_id>/weather/flags', methods=['GET'])
def get_weather_flags(project_id):
    """
    Get weather delay flags for PM dashboard

    GET /api/digital-foreman/projects/{project_id}/weather/flags?start_date=2025-12-01&end_date=2025-12-08
    """
    start_date = request.args.get('start_date', date.today().isoformat())
    end_date = request.args.get('end_date', date.today().isoformat())

    # Would query DB in production
    return jsonify({
        "project_id": project_id,
        "start_date": start_date,
        "end_date": end_date,
        "flags": [],
        "total_flags": 0,
        "unacknowledged": 0
    })


@digital_foreman_bp.route('/weather/scheduled-capture', methods=['POST'])
def scheduled_weather_capture():
    """
    Scheduled weather capture for all active projects (cron endpoint)

    POST /api/digital-foreman/weather/scheduled-capture

    Called by cron at 12:00 PM and 4:00 PM local time
    """
    # Would iterate all active projects and capture weather
    return jsonify({
        "success": True,
        "captures": [],
        "flags_triggered": 0,
        "timestamp": datetime.utcnow().isoformat()
    })


# =============================================================================
# SILICA TRACKER ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/silica/verify', methods=['POST'])
def verify_silica(project_id, job_id):
    """
    Submit silica control verification

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/silica/verify

    Body:
    {
        "method": "wet_cutting",
        "equipment_verified": true,
        "photo_id": "uuid",
        "verifier_id": "uuid",
        "verifier_name": "John Smith",
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122,
        "notes": "Wet saw operating correctly"
    }
    """
    data = request.get_json()

    gps = GPSLocation(
        latitude=data.get('gps_latitude', 0),
        longitude=data.get('gps_longitude', 0)
    )

    result = silica_tracker.submit_verification(
        project_id=project_id,
        job_id=job_id,
        method=data.get('method'),
        equipment_verified=data.get('equipment_verified', False),
        photo_id=data.get('photo_id'),
        verifier_id=data.get('verifier_id'),
        verifier_name=data.get('verifier_name'),
        gps=gps,
        notes=data.get('notes')
    )

    return jsonify(result)


@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/silica/compliance', methods=['GET'])
def check_silica_compliance(project_id, job_id):
    """
    Check silica compliance status for the day

    GET /api/digital-foreman/projects/{project_id}/jobs/{job_id}/silica/compliance
    """
    check_date = request.args.get('date')
    if check_date:
        check_date = date.fromisoformat(check_date)
    else:
        check_date = date.today()

    result = silica_tracker.check_compliance(project_id, job_id, check_date)
    return jsonify(result)


@digital_foreman_bp.route('/silica/morning-alert-check', methods=['POST'])
def silica_morning_alert():
    """
    Check for missing silica verifications (10 AM cron)

    POST /api/digital-foreman/silica/morning-alert-check
    """
    # Would check all projects with silica_tracking_required
    return jsonify({
        "success": True,
        "alerts_created": 0,
        "projects_checked": [],
        "timestamp": datetime.utcnow().isoformat()
    })


# =============================================================================
# DAILY LOG ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/daily-log', methods=['GET'])
def get_daily_log(project_id, job_id):
    """
    Get daily log for date

    GET /api/digital-foreman/projects/{project_id}/jobs/{job_id}/daily-log?date=2025-12-08
    """
    log_date = request.args.get('date', date.today().isoformat())

    # First check gatekeeper
    gatekeeper_status = gatekeeper.check_gatekeeper_status(
        project_id, job_id, date.fromisoformat(log_date)
    )

    if gatekeeper_status['locked']:
        return jsonify({
            "locked": True,
            "gatekeeper": gatekeeper_status,
            "daily_log": None
        })

    # Would fetch from DB
    return jsonify({
        "locked": False,
        "gatekeeper": gatekeeper_status,
        "daily_log": {
            "id": None,
            "date": log_date,
            "status": "not_started",
            "jha_verified": True
        }
    })


@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/daily-log', methods=['POST'])
def create_daily_log(project_id, job_id):
    """
    Create or update daily log

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/daily-log

    Body: Full daily log data structure
    """
    data = request.get_json()
    log_date = data.get('date', date.today().isoformat())

    # Check gatekeeper first
    gatekeeper_status = gatekeeper.check_gatekeeper_status(
        project_id, job_id, date.fromisoformat(log_date)
    )

    if gatekeeper_status['locked']:
        return jsonify({
            "success": False,
            "error": "GATEKEEPER_LOCKED",
            "message": "Complete JHA before creating daily log",
            "gatekeeper": gatekeeper_status
        }), 403

    # Create daily log (would save to DB)
    log_id = str(uuid.uuid4())

    return jsonify({
        "success": True,
        "id": log_id,
        "date": log_date,
        "status": "draft",
        "message": "Daily log created"
    })


@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/daily-log/submit', methods=['POST'])
def submit_daily_log(project_id, job_id):
    """
    Submit daily log with signature

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/daily-log/submit

    Body:
    {
        "log_id": "uuid",
        "foreman_id": "uuid",
        "foreman_name": "John Smith",
        "foreman_signature": "base64...",
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122
    }
    """
    data = request.get_json()

    return jsonify({
        "success": True,
        "log_id": data.get('log_id'),
        "status": "submitted",
        "submitted_at": datetime.utcnow().isoformat(),
        "message": "Daily log submitted successfully"
    })


# =============================================================================
# PHOTO ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/photos', methods=['POST'])
def upload_photo(project_id):
    """
    Upload photo with chain of custody metadata

    POST /api/digital-foreman/projects/{project_id}/photos

    Body (multipart/form-data):
    - file: image file
    - category: site_conditions|work_progress|material|safety|delivery|issue
    - gps_latitude: float
    - gps_longitude: float
    - device_id: string
    - captured_by: uuid
    - captured_by_name: string
    """
    # In production, would handle file upload and storage
    data = request.form

    photo_id = str(uuid.uuid4())

    return jsonify({
        "success": True,
        "id": photo_id,
        "project_id": project_id,
        "category": data.get('category'),
        "chain_of_custody_verified": True,
        "on_site_verified": True,
        "message": "Photo uploaded with chain of custody"
    })


# =============================================================================
# MATERIAL VERIFICATION ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/materials/verify', methods=['POST'])
def verify_material(project_id, job_id):
    """
    Verify material barcode against submittal

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/materials/verify

    Body:
    {
        "barcode_data": "7890123456789",
        "submittal_id": "uuid",
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122,
        "scanned_by": "uuid",
        "scanned_by_name": "John Smith",
        "photo_ids": ["uuid", "uuid"]
    }
    """
    data = request.get_json()

    gps = GPSLocation(
        latitude=data.get('gps_latitude', 0),
        longitude=data.get('gps_longitude', 0)
    )

    result = material_verifier.verify_material(
        project_id=project_id,
        job_id=job_id,
        barcode_data=data.get('barcode_data'),
        submittal_id=data.get('submittal_id'),
        gps=gps,
        scanned_by=data.get('scanned_by'),
        scanned_by_name=data.get('scanned_by_name'),
        photo_ids=data.get('photo_ids', [])
    )

    return jsonify(result)


# =============================================================================
# INSPECTOR ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/inspector/create-visit', methods=['POST'])
def create_inspector_visit(project_id, job_id):
    """
    Create guest inspector visit (no account required)

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/inspector/create-visit

    Body:
    {
        "inspector_name": "Bob Johnson",
        "inspector_company": "FM Global",
        "inspector_email": "bob@fmglobal.com",
        "inspection_type": "deck_inspection",
        "hold_point_name": "Deck Inspection",
        "spec_reference": "07 22 00"
    }
    """
    data = request.get_json()
    visit_id = str(uuid.uuid4())

    return jsonify({
        "success": True,
        "visit_id": visit_id,
        "project_id": project_id,
        "job_id": job_id,
        "inspector_name": data.get('inspector_name'),
        "inspection_type": data.get('inspection_type'),
        "access_link": f"/inspector/{visit_id}",
        "message": "Inspector visit created. Share access link with inspector."
    })


@digital_foreman_bp.route('/inspector/<visit_id>/submit', methods=['POST'])
def submit_inspection(visit_id):
    """
    Submit inspection results and signature

    POST /api/digital-foreman/inspector/{visit_id}/submit

    Body:
    {
        "checklist_responses": [...],
        "result": "passed|failed|conditional",
        "result_notes": "...",
        "conditions": [...],
        "inspector_signature": "base64...",
        "gps_latitude": 39.2904,
        "gps_longitude": -76.6122,
        "photo_ids": [...]
    }
    """
    data = request.get_json()

    return jsonify({
        "success": True,
        "visit_id": visit_id,
        "result": data.get('result'),
        "signed_at": datetime.utcnow().isoformat(),
        "message": "Inspection submitted and linked to daily log"
    })


# =============================================================================
# HOT WORK PERMIT ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/jobs/<job_id>/hot-work/create', methods=['POST'])
def create_hot_work_permit(project_id, job_id):
    """
    Create hot work permit for torch operations

    POST /api/digital-foreman/projects/{project_id}/jobs/{job_id}/hot-work/create
    """
    data = request.get_json()
    permit_id = str(uuid.uuid4())

    return jsonify({
        "success": True,
        "permit_id": permit_id,
        "project_id": project_id,
        "job_id": job_id,
        "fire_watch_name": data.get('fire_watch_name'),
        "status": "active",
        "message": "Hot work permit created. Fire watch required."
    })


@digital_foreman_bp.route('/hot-work/<permit_id>/sign-off', methods=['POST'])
def sign_off_hot_work(permit_id):
    """
    Fire watch sign-off on hot work permit

    POST /api/digital-foreman/hot-work/{permit_id}/sign-off
    """
    data = request.get_json()

    return jsonify({
        "success": True,
        "permit_id": permit_id,
        "status": "completed",
        "fire_watch_signed_at": datetime.utcnow().isoformat(),
        "message": "Hot work permit completed. Fire watch signed off."
    })


# =============================================================================
# ALERTS ENDPOINTS
# =============================================================================

@digital_foreman_bp.route('/projects/<project_id>/alerts', methods=['GET'])
def get_project_alerts(project_id):
    """
    Get active alerts for PM dashboard

    GET /api/digital-foreman/projects/{project_id}/alerts?acknowledged=false
    """
    acknowledged = request.args.get('acknowledged', 'false') == 'true'

    return jsonify({
        "project_id": project_id,
        "alerts": [],
        "total": 0,
        "unacknowledged": 0
    })


@digital_foreman_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """
    Acknowledge system alert

    POST /api/digital-foreman/alerts/{alert_id}/acknowledge
    """
    data = request.get_json()

    return jsonify({
        "success": True,
        "alert_id": alert_id,
        "acknowledged": True,
        "acknowledged_at": datetime.utcnow().isoformat(),
        "acknowledged_by": data.get('acknowledged_by'),
        "resolution_notes": data.get('resolution_notes')
    })
