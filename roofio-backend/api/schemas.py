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
