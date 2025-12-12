"""
ROOFIO API Schemas
==================

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# AGENCY SCHEMAS
# =============================================================================

class AgencyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Dict[str, Any]] = None
    license_no: Optional[str] = None
    tax_id: Optional[str] = None


class AgencyCreate(AgencyBase):
    pass


class AgencyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    license_no: Optional[str] = None
    tax_id: Optional[str] = None
    default_markup: Optional[float] = None
    overhead_rate: Optional[float] = None
    labor_rates: Optional[Dict[str, float]] = None


class AgencyResponse(AgencyBase):
    agency_id: UUID
    default_markup: Optional[float] = 15.0
    overhead_rate: Optional[float] = 10.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    role: str = Field(default="user", pattern="^(admin|manager|user|viewer)$")
    positions: Optional[List[str]] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|manager|user|viewer)$")
    positions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    certifications: Optional[List[str]] = None


class UserResponse(UserBase):
    user_id: UUID
    agency_id: UUID
    is_active: bool = True
    email_verified: bool = False
    certifications: Optional[List[str]] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =============================================================================
# PROJECT SCHEMAS
# =============================================================================

class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class ContactSchema(BaseModel):
    name: str
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    number: Optional[str] = None
    description: Optional[str] = None
    address: Dict[str, Any]
    municipality: Optional[str] = None
    project_type: Optional[str] = Field(
        None,
        pattern="^(commercial|residential|industrial|institutional)$"
    )
    status: str = Field(
        default="bidding",
        pattern="^(bidding|awarded|in_progress|punch_list|closeout|complete|warranty|cancelled)$"
    )


class ProjectCreate(ProjectBase):
    gc_contact: Optional[Dict[str, Any]] = None
    owner_contact: Optional[Dict[str, Any]] = None
    architect_contact: Optional[Dict[str, Any]] = None
    contract_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    spec_sections: Optional[List[str]] = None
    is_insurance_claim: bool = False
    claim_number: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    number: Optional[str] = None
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    municipality: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    gc_contact: Optional[Dict[str, Any]] = None
    owner_contact: Optional[Dict[str, Any]] = None
    architect_contact: Optional[Dict[str, Any]] = None
    contract_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    permit_number: Optional[str] = None
    permit_status: Optional[str] = None
    spec_sections: Optional[List[str]] = None


class ProjectResponse(ProjectBase):
    project_id: UUID
    agency_id: UUID
    gc_contact: Optional[Dict[str, Any]] = None
    owner_contact: Optional[Dict[str, Any]] = None
    architect_contact: Optional[Dict[str, Any]] = None
    contract_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    permit_number: Optional[str] = None
    permit_status: Optional[str] = None
    spec_sections: Optional[List[str]] = None
    is_insurance_claim: bool = False
    ai_confidence: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    limit: int
    offset: int


# =============================================================================
# POSITION CONFIG SCHEMAS
# =============================================================================

class PositionConfigUpdate(BaseModel):
    mode: str = Field(..., pattern="^(off|assist|full_ai)$")
    confidence_threshold: Optional[int] = Field(None, ge=0, le=100)


class PositionConfigResponse(BaseModel):
    config_id: UUID
    agency_id: UUID
    position: str
    mode: str
    confidence_threshold: int = 90
    total_actions: int = 0
    actions_auto_completed: int = 0
    actions_flagged: int = 0
    average_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# AI ACTION LOG SCHEMAS
# =============================================================================

class AIActionLogResponse(BaseModel):
    log_id: UUID
    agency_id: UUID
    project_id: Optional[UUID] = None
    position: str
    action_type: str
    confidence_score: int
    confidence_factors: Optional[Dict[str, Any]] = None
    status: str
    paused_reason: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    reviewed_by: Optional[UUID] = None
    review_date: Optional[datetime] = None
    review_action: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AIActionReview(BaseModel):
    review_action: str = Field(..., pattern="^(approved|edited|rejected)$")
    review_notes: Optional[str] = None


# =============================================================================
# GENERIC RESPONSES
# =============================================================================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    version: str = "1.0.0"


# =============================================================================
# FORM TEMPLATE SCHEMAS
# =============================================================================

class FormFieldSchema(BaseModel):
    """Individual field in a form template"""
    name: str
    label: str
    type: str = Field(default="text", pattern="^(text|number|date|time|datetime|checkbox|select|textarea|signature|photo|gps)$")
    required: bool = False
    default_value: Optional[str] = None
    options: Optional[List[str]] = None  # For select fields
    position: Optional[Dict[str, Any]] = None  # {x, y, width, height} for layout


class FormTemplateCreate(BaseModel):
    """Create a new form template"""
    name: str = Field(..., min_length=1, max_length=255)
    form_type: str = Field(..., min_length=1, max_length=100)  # daily_report, inspection, jha, etc.
    description: Optional[str] = None
    is_custom: bool = True  # True = user's format, False = ROOFIO format
    fields: Optional[List[FormFieldSchema]] = None
    layout: Optional[Dict[str, Any]] = None
    roofio_additions: Optional[Dict[str, bool]] = Field(
        default={"logo": True, "timestamp": True, "gps": True, "watermark": False}
    )


class FormTemplateUpdate(BaseModel):
    """Update form template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    fields: Optional[List[FormFieldSchema]] = None
    layout: Optional[Dict[str, Any]] = None
    roofio_additions: Optional[Dict[str, bool]] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|draft)$")


class FormTemplateResponse(BaseModel):
    """Form template response"""
    template_id: UUID
    agency_id: UUID
    name: str
    form_type: str
    description: Optional[str] = None
    is_custom: bool = True
    is_default: bool = False
    source_file_url: Optional[str] = None
    source_file_type: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None
    layout: Optional[Dict[str, Any]] = None
    roofio_additions: Optional[Dict[str, bool]] = None
    preview_url: Optional[str] = None
    times_used: int = 0
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormTemplateListResponse(BaseModel):
    """List of form templates"""
    templates: List[FormTemplateResponse]
    total: int


# =============================================================================
# FORM SUBMISSION SCHEMAS
# =============================================================================

class FormSubmissionCreate(BaseModel):
    """Submit a filled form"""
    template_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    form_type: str
    data: Dict[str, Any]
    attachments: Optional[List[Dict[str, str]]] = None  # [{name, url, type}]
    signature_url: Optional[str] = None
    signed_by: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    device_info: Optional[Dict[str, Any]] = None


class FormSubmissionResponse(BaseModel):
    """Form submission response"""
    submission_id: UUID
    agency_id: UUID
    project_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    form_type: str
    data: Dict[str, Any]
    attachments: Optional[List[Dict[str, str]]] = None
    signature_url: Optional[str] = None
    signed_by: Optional[str] = None
    signed_at: Optional[datetime] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    status: str = "draft"
    created_at: datetime
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =============================================================================
# DOCUMENT SCAN / CAMERA SCHEMAS
# =============================================================================

class ScanRequest(BaseModel):
    """Request to process a scanned/photographed document"""
    output_format: str = Field(
        default="pdf",
        pattern="^(pdf|png|jpg|docx|xlsx|json)$"
    )
    enhance: bool = True  # Auto-enhance (contrast, straighten, crop)
    extract_text: bool = False  # OCR text extraction
    extract_fields: bool = False  # AI field extraction for form creation


class ScanResponse(BaseModel):
    """Response from document scan processing"""
    scan_id: UUID
    original_url: str
    processed_url: str
    output_format: str
    extracted_text: Optional[str] = None
    extracted_fields: Optional[List[FormFieldSchema]] = None
    processing_time_ms: int
    created_at: datetime


class FormFromScanRequest(BaseModel):
    """Create a form template from a scanned document"""
    scan_id: UUID
    name: str
    form_type: str
    description: Optional[str] = None
    confirm_fields: bool = False  # If true, use AI-extracted fields as-is
