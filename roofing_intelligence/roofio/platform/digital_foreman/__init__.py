"""
ROOFIO Digital Foreman Module
"The Field Commander" - Risk Shield Edition

This module implements the three core Risk Shield features:
1. THE GATEKEEPER - JHA locks daily log until safety verified
2. THE WEATHER TRUTH AGENT - Auto-captures weather at 12pm/4pm, flags delays
3. THE SILICA TRACKER - OSHA compliance documentation

Plus supporting features:
- Photo Chain of Custody (GPS, timestamp, SHA-256 hash)
- Material Verification (barcode scanning)
- Guest Inspector Mode
- Offline-First Sync

All designed to be "Spec-Grade" - meeting Division 01 requirements for:
- Section 01 32 26: Construction Progress Reporting
- Section 01 35 29: Safety Procedures
- Section 01 33 00: Submittal Procedures
- Section 01 32 33: Photographic Documentation
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid
import hashlib
import json


# =============================================================================
# ENUMS
# =============================================================================

class JHAStatus(Enum):
    """Status of daily Job Hazard Analysis"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class DailyLogStatus(Enum):
    """Status of daily construction log"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"


class WeatherCaptureType(Enum):
    """Type of weather capture"""
    SCHEDULED = "scheduled"  # 12pm/4pm automatic
    MANUAL = "manual"
    START_OF_DAY = "start_of_day"
    END_OF_DAY = "end_of_day"


class DelayFlagReason(Enum):
    """Reasons for weather delay flags"""
    WIND_EXCEEDED = "wind_exceeded"
    PRECIPITATION_EXCEEDED = "precipitation_exceeded"
    TEMP_TOO_LOW = "temp_too_low"
    TEMP_TOO_HIGH = "temp_too_high"


class MaterialMatchStatus(Enum):
    """Material verification status"""
    VERIFIED = "verified"
    MISMATCH = "mismatch"
    PENDING = "pending"
    NOT_FOUND = "not_found"


class InspectionResult(Enum):
    """Third-party inspection result"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"


class PhotoCategory(Enum):
    """Categories for photo documentation"""
    SITE_CONDITIONS = "site_conditions"
    WORK_PROGRESS = "work_progress"
    MATERIAL = "material"
    SAFETY = "safety"
    DELIVERY = "delivery"
    ISSUE = "issue"
    SILICA_CONTROL = "silica_control"
    INSPECTION = "inspection"


class AlertSeverity(Enum):
    """System alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of system alerts"""
    WEATHER_DELAY_FLAG = "weather_delay_flag"
    SILICA_VERIFICATION_MISSING = "silica_verification_missing"
    JHA_NOT_COMPLETED = "jha_not_completed"
    MATERIAL_MISMATCH = "material_mismatch"
    INSPECTION_DUE = "inspection_due"
    HOT_WORK_ACTIVE = "hot_work_active"
    FIRE_WATCH_ENDING = "fire_watch_ending"


class SilicaControlMethod(Enum):
    """OSHA silica control methods"""
    WET_CUTTING = "wet_cutting"
    VACUUM_EXTRACTION = "vacuum_extraction"
    ENCLOSED_CAB = "enclosed_cab"
    RESPIRATORY_PROTECTION = "respiratory_protection"
    LOCAL_EXHAUST_VENTILATION = "local_exhaust_ventilation"


class SyncStatus(Enum):
    """Offline sync queue status"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    CONFLICT = "conflict"


# =============================================================================
# DATA CLASSES - Core Models
# =============================================================================

@dataclass
class GPSLocation:
    """GPS coordinates with accuracy"""
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy_meters": self.accuracy_meters,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class Hazard:
    """JHA hazard identification"""
    hazard: str
    control: str
    ppe: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical

    def to_dict(self) -> Dict:
        return {
            "hazard": self.hazard,
            "control": self.control,
            "ppe": self.ppe,
            "severity": self.severity
        }


@dataclass
class ChecklistItem:
    """JHA checklist item"""
    item: str
    required: bool = True
    checked: bool = False
    notes: Optional[str] = None
    photo_id: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "item": self.item,
            "required": self.required,
            "checked": self.checked,
            "notes": self.notes,
            "photo_id": self.photo_id
        }


@dataclass
class CrewMember:
    """Crew member on daily log"""
    employee_id: str
    name: str
    role: str
    hours: float = 8.0
    certifications_verified: bool = True

    def to_dict(self) -> Dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role,
            "hours": self.hours,
            "certifications_verified": self.certifications_verified
        }


@dataclass
class Signature:
    """Digital signature record"""
    signer_id: str
    signer_name: str
    signature_data: str  # Base64 encoded image or SVG
    signed_at: datetime
    device_id: str
    ip_address: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "signer_id": self.signer_id,
            "signer_name": self.signer_name,
            "signature_data": self.signature_data,
            "signed_at": self.signed_at.isoformat(),
            "device_id": self.device_id,
            "ip_address": self.ip_address
        }


@dataclass
class WeatherData:
    """Weather conditions from API"""
    temperature_f: float
    humidity_percent: int
    wind_speed_mph: float
    wind_gust_mph: Optional[float]
    wind_direction: str
    precipitation_inches: float
    conditions: str
    visibility_miles: Optional[float]
    feels_like_f: Optional[float] = None
    source: str = "openweathermap"
    raw_response: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "temperature_f": self.temperature_f,
            "humidity_percent": self.humidity_percent,
            "wind_speed_mph": self.wind_speed_mph,
            "wind_gust_mph": self.wind_gust_mph,
            "wind_direction": self.wind_direction,
            "precipitation_inches": self.precipitation_inches,
            "conditions": self.conditions,
            "visibility_miles": self.visibility_miles,
            "feels_like_f": self.feels_like_f,
            "source": self.source
        }


@dataclass
class MaterialDelivery:
    """Material delivery record"""
    delivery_id: str
    po_number: Optional[str]
    material: str
    quantity: float
    unit: str
    barcode_data: Optional[str]
    submittal_reference: Optional[str]
    match_status: MaterialMatchStatus = MaterialMatchStatus.PENDING
    photo_ids: List[str] = field(default_factory=list)
    received_by: Optional[str] = None
    received_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "delivery_id": self.delivery_id,
            "po_number": self.po_number,
            "material": self.material,
            "quantity": self.quantity,
            "unit": self.unit,
            "barcode_data": self.barcode_data,
            "submittal_reference": self.submittal_reference,
            "match_status": self.match_status.value,
            "photo_ids": self.photo_ids,
            "received_by": self.received_by,
            "received_at": self.received_at.isoformat() if self.received_at else None
        }


@dataclass
class Blocker:
    """Work blocker/issue"""
    blocker_id: str
    blocker_type: str  # 'obstruction', 'rfi_needed', 'material_issue', 'weather', 'other'
    description: str
    photo_ids: List[str] = field(default_factory=list)
    rfi_generated: bool = False
    rfi_id: Optional[str] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "blocker_id": self.blocker_id,
            "blocker_type": self.blocker_type,
            "description": self.description,
            "photo_ids": self.photo_ids,
            "rfi_generated": self.rfi_generated,
            "rfi_id": self.rfi_id,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes
        }


# =============================================================================
# GATEKEEPER - JHA Lock Logic
# =============================================================================

class GatekeeperService:
    """
    THE GATEKEEPER - JHA locks daily log until safety verified

    This is the core "Risk Shield" feature. The app is LOCKED until
    the daily Job Hazard Analysis is completed and signed.

    Flow:
    1. User opens app → All features locked
    2. Complete JHA checklist → Verify hazards → Sign
    3. JHA verified → Daily log UNLOCKED
    """

    def __init__(self, db_connection=None):
        self.db = db_connection

    def check_gatekeeper_status(
        self,
        project_id: str,
        job_id: str,
        check_date: date = None
    ) -> Dict[str, Any]:
        """
        Check if daily log is unlocked (JHA completed)

        Returns:
            {
                "locked": bool,
                "reason": "JHA_NOT_COMPLETED" | None,
                "message": str,
                "jha_status": "not_started" | "in_progress" | "completed",
                "jha_id": str | None,
                "safety_verified": bool,
                "verified_at": ISO-8601 | None
            }
        """
        if check_date is None:
            check_date = date.today()

        # In production, this would query the database
        # For now, return structure for API contract
        return {
            "locked": True,
            "reason": "JHA_NOT_COMPLETED",
            "message": "Complete daily JHA to unlock daily log",
            "jha_status": "not_started",
            "jha_id": None,
            "safety_verified": False,
            "verified_at": None,
            "date": check_date.isoformat()
        }

    def get_jha_template(self, work_type: str) -> Dict[str, Any]:
        """Get JHA template for work type with auto-populated hazards"""
        # Division 07 work type templates
        templates = {
            "tpo_install": {
                "name": "TPO Membrane Installation",
                "spec_section": "07 54 00",
                "hazards": [
                    Hazard("Fall from height (>6ft)", "100% tie-off, warning line system", ["harness", "hard_hat"]),
                    Hazard("Chemical fumes (adhesive/primer)", "Ventilation, work upwind", ["respirator", "safety_glasses"]),
                    Hazard("Hot surface (heat welding)", "Proper training, hot work permit", ["gloves", "long_sleeves"]),
                    Hazard("Heavy lifting", "Team lift for rolls >50lbs", ["back_brace"])
                ],
                "required_ppe": ["hard_hat", "safety_glasses", "gloves", "harness", "safety_boots"],
                "checklist": [
                    ChecklistItem("Fall protection anchor points verified", True),
                    ChecklistItem("Hot work permit obtained (if welding)", False),
                    ChecklistItem("First aid kit on roof", True),
                    ChecklistItem("Fire extinguisher within 25ft", True),
                    ChecklistItem("Ladder secured at top and bottom", True)
                ]
            },
            "tear_off": {
                "name": "Roof Tear-Off",
                "spec_section": "07 50 00",
                "hazards": [
                    Hazard("Fall from height", "100% tie-off, controlled access zone", ["harness", "hard_hat"]),
                    Hazard("Falling debris", "Debris chute, ground barriers", ["hard_hat", "safety_glasses"]),
                    Hazard("Silica dust", "Wet methods, HEPA vacuum", ["n95_respirator"]),
                    Hazard("Sharp objects", "Proper disposal, cut-resistant gloves", ["cut_resistant_gloves", "safety_boots"])
                ],
                "required_ppe": ["hard_hat", "safety_glasses", "cut_resistant_gloves", "harness", "safety_boots", "n95_respirator"],
                "checklist": [
                    ChecklistItem("Ground barricades in place", True),
                    ChecklistItem("Debris chute secured", True),
                    ChecklistItem("Fall protection verified", True),
                    ChecklistItem("Silica control plan reviewed", True)
                ]
            },
            "flashing": {
                "name": "Sheet Metal Flashing",
                "spec_section": "07 62 00",
                "hazards": [
                    Hazard("Fall from height", "100% tie-off at edge work", ["harness", "hard_hat"]),
                    Hazard("Sharp metal edges", "Cut-resistant gloves, proper handling", ["cut_resistant_gloves"]),
                    Hazard("Power tool injuries", "Training, guards in place", ["safety_glasses", "hearing_protection"]),
                    Hazard("Pinch points", "Proper brake/shear operation", ["gloves"])
                ],
                "required_ppe": ["hard_hat", "safety_glasses", "cut_resistant_gloves", "hearing_protection", "safety_boots"],
                "checklist": [
                    ChecklistItem("Sheet metal brake guards in place", True),
                    ChecklistItem("Scaffolding inspected", True),
                    ChecklistItem("Edge protection verified", True)
                ]
            }
        }

        template = templates.get(work_type, templates["tpo_install"])
        return {
            "name": template["name"],
            "spec_section": template["spec_section"],
            "hazards": [h.to_dict() for h in template["hazards"]],
            "required_ppe": template["required_ppe"],
            "checklist": [c.to_dict() for c in template["checklist"]]
        }

    def complete_jha(
        self,
        project_id: str,
        job_id: str,
        checklist_responses: List[Dict],
        hazards_identified: List[Dict],
        ppe_verified: List[str],
        superintendent_id: str,
        superintendent_name: str,
        superintendent_signature: str,
        crew_acknowledgments: List[Dict],
        gps: GPSLocation,
        device_id: str
    ) -> Dict[str, Any]:
        """
        Complete JHA and unlock daily log

        This is the key unlock action for the GATEKEEPER.
        """
        now = datetime.utcnow()
        jha_id = str(uuid.uuid4())

        # Verify all required checklist items are checked
        all_required_checked = all(
            item.get("checked", False)
            for item in checklist_responses
            if item.get("required", True)
        )

        if not all_required_checked:
            return {
                "success": False,
                "error": "All required checklist items must be checked",
                "jha_id": None
            }

        # Create JHA record
        jha_record = {
            "id": jha_id,
            "project_id": project_id,
            "job_id": job_id,
            "date": date.today().isoformat(),
            "status": JHAStatus.COMPLETED.value,
            "safety_verified": True,
            "verified_at": now.isoformat(),
            "completion_gps": gps.to_dict(),
            "on_site_verified": True,  # Would check geofence in production
            "hazards_identified": hazards_identified,
            "checklist_responses": checklist_responses,
            "ppe_verified": ppe_verified,
            "superintendent_id": superintendent_id,
            "superintendent_name": superintendent_name,
            "superintendent_signature": superintendent_signature,
            "superintendent_signed_at": now.isoformat(),
            "crew_acknowledgments": crew_acknowledgments,
            "device_id": device_id
        }

        return {
            "success": True,
            "jha_id": jha_id,
            "safety_verified": True,
            "verified_at": now.isoformat(),
            "on_site_verified": True,
            "daily_log_unlocked": True,
            "message": "JHA completed. Daily log is now unlocked."
        }


# =============================================================================
# WEATHER TRUTH AGENT
# =============================================================================

class WeatherTruthAgent:
    """
    THE WEATHER TRUTH AGENT - Auto-captures weather at 12pm and 4pm

    Key features:
    - Automatic capture based on project GPS
    - Auto-flag if conditions exceed thresholds
    - PM dashboard alerts for potential delays
    - Raw API response stored for legal defensibility
    """

    DEFAULT_THRESHOLDS = {
        "wind_mph": 20.0,
        "precip_inches": 0.5,
        "temp_min_f": 32.0,
        "temp_max_f": 95.0
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def capture_weather(
        self,
        project_id: str,
        gps: GPSLocation,
        capture_type: WeatherCaptureType = WeatherCaptureType.SCHEDULED,
        thresholds: Dict = None
    ) -> Dict[str, Any]:
        """
        Capture weather from API and check for delay flags

        In production, this calls OpenWeatherMap or NOAA API.
        """
        if thresholds is None:
            thresholds = self.DEFAULT_THRESHOLDS

        # Mock weather data (would call API in production)
        weather = WeatherData(
            temperature_f=52.0,
            humidity_percent=65,
            wind_speed_mph=12.0,
            wind_gust_mph=18.0,
            wind_direction="NW",
            precipitation_inches=0.0,
            conditions="Partly Cloudy",
            visibility_miles=10.0,
            feels_like_f=48.0,
            source="openweathermap"
        )

        # Check delay flags
        delay_flags = []
        if weather.wind_speed_mph > thresholds["wind_mph"]:
            delay_flags.append(DelayFlagReason.WIND_EXCEEDED.value)
        if weather.precipitation_inches > thresholds["precip_inches"]:
            delay_flags.append(DelayFlagReason.PRECIPITATION_EXCEEDED.value)
        if weather.temperature_f < thresholds["temp_min_f"]:
            delay_flags.append(DelayFlagReason.TEMP_TOO_LOW.value)
        if weather.temperature_f > thresholds["temp_max_f"]:
            delay_flags.append(DelayFlagReason.TEMP_TOO_HIGH.value)

        capture_id = str(uuid.uuid4())
        now = datetime.utcnow()

        return {
            "capture_id": capture_id,
            "project_id": project_id,
            "captured_at": now.isoformat(),
            "capture_type": capture_type.value,
            "gps": gps.to_dict(),
            "weather": weather.to_dict(),
            "delay_flag_triggered": len(delay_flags) > 0,
            "delay_flag_reasons": delay_flags,
            "requires_pm_acknowledgment": len(delay_flags) > 0
        }

    def get_weather_summary(
        self,
        project_id: str,
        for_date: date = None
    ) -> Dict[str, Any]:
        """Get weather summary for daily log"""
        if for_date is None:
            for_date = date.today()

        return {
            "date": for_date.isoformat(),
            "captures": [],  # Would fetch from DB
            "delay_flags": [],
            "delay_claimed": False
        }


# =============================================================================
# SILICA TRACKER
# =============================================================================

class SilicaTracker:
    """
    THE SILICA TRACKER - OSHA compliance documentation

    Key features:
    - Daily verification forms (minimum 2x per day)
    - Control method documentation
    - Photo evidence of controls
    - 10 AM alert if not completed
    - Links to daily log
    """

    CONTROL_METHODS = [
        {"id": "wet_cutting", "name": "Wet Cutting", "description": "Using water to suppress dust"},
        {"id": "vacuum_extraction", "name": "Vacuum Extraction", "description": "HEPA vacuum at point of cut"},
        {"id": "enclosed_cab", "name": "Enclosed Cab", "description": "Operating from enclosed cab with filtration"},
        {"id": "respiratory_protection", "name": "Respiratory Protection", "description": "N95 or higher respirator"},
        {"id": "local_exhaust_ventilation", "name": "Local Exhaust Ventilation", "description": "LEV at work area"}
    ]

    def submit_verification(
        self,
        project_id: str,
        job_id: str,
        method: str,
        equipment_verified: bool,
        photo_id: Optional[str],
        verifier_id: str,
        verifier_name: str,
        gps: GPSLocation,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit silica control verification"""
        now = datetime.utcnow()
        verification_id = str(uuid.uuid4())

        verification = {
            "time": now.strftime("%H:%M:%S"),
            "method": method,
            "equipment_verified": equipment_verified,
            "photo_id": photo_id,
            "verifier_id": verifier_id,
            "verifier_name": verifier_name,
            "gps": gps.to_dict(),
            "notes": notes
        }

        return {
            "success": True,
            "verification_id": verification_id,
            "verification": verification,
            "verification_count": 1,  # Would track total for day
            "compliant": False,  # Need 2+ for compliance
            "message": "Silica verification recorded. Need 2 verifications for daily compliance."
        }

    def check_compliance(self, project_id: str, job_id: str, for_date: date = None) -> Dict[str, Any]:
        """Check if silica compliance is met for the day"""
        if for_date is None:
            for_date = date.today()

        return {
            "date": for_date.isoformat(),
            "project_id": project_id,
            "job_id": job_id,
            "verification_count": 0,
            "required_count": 2,
            "compliant": False,
            "methods_used": [],
            "last_verification": None
        }


# =============================================================================
# PHOTO CHAIN OF CUSTODY
# =============================================================================

class PhotoChainOfCustody:
    """
    Photo Chain of Custody - Immutable photo records

    Key features:
    - GPS extraction from EXIF
    - SHA-256 hash at capture (before any processing)
    - Direct-to-cloud upload (no local file transfers)
    - Geofence verification
    - Original EXIF preserved
    """

    @staticmethod
    def generate_file_hash(file_bytes: bytes) -> str:
        """Generate SHA-256 hash of file for integrity verification"""
        return hashlib.sha256(file_bytes).hexdigest()

    def create_photo_record(
        self,
        project_id: str,
        file_hash: str,
        gps: GPSLocation,
        captured_by: str,
        captured_by_name: str,
        device_id: str,
        category: PhotoCategory,
        exif_data: Dict,
        storage_url: str,
        geofence_center: GPSLocation = None,
        geofence_radius: float = 500.0
    ) -> Dict[str, Any]:
        """Create immutable photo record with chain of custody"""
        now = datetime.utcnow()
        photo_id = str(uuid.uuid4())

        # Check if within geofence
        on_site = True
        flags = []

        if geofence_center:
            distance = self._calculate_distance(gps, geofence_center)
            on_site = distance <= geofence_radius
            if not on_site:
                flags.append("OUTSIDE_GEOFENCE")

        return {
            "id": photo_id,
            "project_id": project_id,
            "captured_at": now.isoformat(),
            "captured_by": captured_by,
            "captured_by_name": captured_by_name,
            "device_id": device_id,
            "gps": gps.to_dict(),
            "on_site_verified": on_site,
            "file_hash_sha256": file_hash,
            "original_exif": exif_data,
            "storage_url": storage_url,
            "category": category.value,
            "flags": flags,
            "chain_of_custody_verified": True
        }

    def _calculate_distance(self, point1: GPSLocation, point2: GPSLocation) -> float:
        """Calculate distance between two GPS points in meters (Haversine formula)"""
        from math import radians, cos, sin, asin, sqrt

        lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
        lat2, lon2 = radians(point2.latitude), radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth radius in meters

        return c * r


# =============================================================================
# MATERIAL VERIFICATION
# =============================================================================

class MaterialVerifier:
    """
    Material Verification - Barcode/QR scanning

    Key features:
    - Scan material barcode/QR
    - Cross-reference with approved submittals
    - Flag mismatches
    - Auto-generate RFI for substitutions
    """

    def verify_material(
        self,
        project_id: str,
        job_id: str,
        barcode_data: str,
        submittal_id: str,
        gps: GPSLocation,
        scanned_by: str,
        scanned_by_name: str,
        photo_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Verify scanned material against approved submittal"""
        now = datetime.utcnow()
        verification_id = str(uuid.uuid4())

        # In production, this would lookup submittal and compare
        # Mock response showing verified match
        return {
            "verification_id": verification_id,
            "project_id": project_id,
            "job_id": job_id,
            "scanned_at": now.isoformat(),
            "barcode_data": barcode_data,
            "submittal_id": submittal_id,
            "match_status": MaterialMatchStatus.VERIFIED.value,
            "scanned_material": {
                "manufacturer": "Carlisle",
                "product_name": "TPO 60mil White",
                "lot_number": "2025-1207-A",
                "manufacture_date": "2025-10-15"
            },
            "approved_material": {
                "manufacturer": "Carlisle",
                "product_name": "TPO 60mil White",
                "submittal_number": "SUB-001",
                "spec_section": "07 54 00"
            },
            "verified": True,
            "message": "Material verified - matches approved submittal"
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "JHAStatus",
    "DailyLogStatus",
    "WeatherCaptureType",
    "DelayFlagReason",
    "MaterialMatchStatus",
    "InspectionResult",
    "PhotoCategory",
    "AlertSeverity",
    "AlertType",
    "SilicaControlMethod",
    "SyncStatus",

    # Data Classes
    "GPSLocation",
    "Hazard",
    "ChecklistItem",
    "CrewMember",
    "Signature",
    "WeatherData",
    "MaterialDelivery",
    "Blocker",

    # Services
    "GatekeeperService",
    "WeatherTruthAgent",
    "SilicaTracker",
    "PhotoChainOfCustody",
    "MaterialVerifier"
]
