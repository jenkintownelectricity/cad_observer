"""
ROOFIO Database Models
======================

SQLAlchemy ORM models for core entities.

These models align with the security/session module's multi-tenancy
using agency_id for data isolation.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer,
    ForeignKey, Numeric, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from .database import Base


# =============================================================================
# CORE ENTITIES
# =============================================================================

class Agency(Base):
    """
    Agency/Company - Top-level tenant for multi-tenancy.
    All other entities are scoped to an agency.
    """
    __tablename__ = "agencies"

    agency_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    license_no = Column(String(100))
    tax_id = Column(String(50))
    insurance_info = Column(JSON)

    # Financial defaults
    default_markup = Column(Numeric(5, 2), default=15.00)
    overhead_rate = Column(Numeric(5, 2), default=10.00)
    profit_margin_target = Column(Numeric(5, 2), default=15.00)
    labor_rates = Column(JSON)  # {"journeyman": 85, "foreman": 95, ...}

    # Contact info
    address = Column(JSON)
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))

    # Settings
    warranty_terms = Column(Text)
    payment_terms = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="agency")
    projects = relationship("Project", back_populates="agency")


class User(Base):
    """
    User account - linked to an agency.
    Supports multiple roles per agency.
    """
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)

    # Auth
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255))  # Null for OAuth-only users

    # Profile
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    avatar_url = Column(String(500))

    # Role & Permissions
    role = Column(String(50), nullable=False, default="user")  # admin, manager, user, viewer
    positions = Column(ARRAY(String))  # ["estimator", "project_manager", ...]

    # Certifications & Training
    certifications = Column(JSON, default=list)  # ["OSHA 30", "Carlisle Certified"]
    osha_10_date = Column(DateTime)
    osha_30_date = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)

    # OAuth
    oauth_provider = Column(String(50))  # google, microsoft, etc
    oauth_id = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agency = relationship("Agency", back_populates="users")

    # Indexes
    __table_args__ = (
        Index("idx_users_agency", "agency_id"),
        Index("idx_users_email", "email"),
    )


class Project(Base):
    """
    Project - The Unified Project Object (UPO).
    Central entity that links all project data.
    """
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)

    # Basic Info
    name = Column(String(255), nullable=False)
    number = Column(String(50))  # Project number/code
    description = Column(Text)

    # Location
    address = Column(JSON, nullable=False)  # {street, city, state, zip, lat, lng}
    municipality = Column(String(100))

    # Type & Status
    project_type = Column(String(50))  # commercial, residential, industrial, institutional
    status = Column(String(50), default="bidding")  # bidding, awarded, in_progress, complete, etc

    # Contacts (stored as JSON for flexibility)
    gc_contact = Column(JSON)
    owner_contact = Column(JSON)
    architect_contact = Column(JSON)

    # Contract
    contract_amount = Column(Numeric(12, 2))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Permit
    permit_number = Column(String(100))
    permit_status = Column(String(50))

    # Specs
    spec_sections = Column(ARRAY(String))  # ["07 54 00", "07 62 00", ...]

    # Insurance Claim Fields
    is_insurance_claim = Column(Boolean, default=False)
    claim_number = Column(String(100))
    policy_number = Column(String(100))

    # Documents & Files
    documents = Column(JSON, default=list)  # [{name, url, type, uploaded_at}]

    # AI Tracking
    ai_confidence = Column(Integer)
    last_ai_action = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agency = relationship("Agency", back_populates="projects")

    # Indexes
    __table_args__ = (
        Index("idx_projects_agency", "agency_id"),
        Index("idx_projects_status", "status"),
    )


class AuditLog(Base):
    """
    Audit log for tracking all changes.
    Required for compliance and debugging.
    """
    __tablename__ = "audit_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Action details
    action = Column(String(50), nullable=False)  # create, update, delete, login, etc
    entity_type = Column(String(100))  # projects, users, etc
    entity_id = Column(UUID(as_uuid=True))

    # Change data
    old_values = Column(JSON)
    new_values = Column(JSON)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_audit_agency", "agency_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_created", "created_at"),
    )


class AIActionLog(Base):
    """
    AI action log for tracking AI operations.
    Used for confidence scoring and human review.
    """
    __tablename__ = "ai_action_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Position & Action
    position = Column(String(50), nullable=False)  # estimator, pm, qc, etc
    action_type = Column(String(100), nullable=False)  # generate_estimate, create_rfi, etc

    # Confidence
    confidence_score = Column(Integer, nullable=False)
    confidence_factors = Column(JSON)  # {data_completeness: 95, consistency: 90}

    # Status
    status = Column(String(50), nullable=False)  # completed, paused, human_review, failed
    paused_reason = Column(Text)

    # Data
    input_data = Column(JSON)
    output_data = Column(JSON)

    # Review
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    review_date = Column(DateTime)
    review_action = Column(String(50))  # approved, edited, rejected
    review_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_ai_log_agency", "agency_id"),
        Index("idx_ai_log_status", "status"),
        Index("idx_ai_log_position", "position"),
    )


# =============================================================================
# POSITION CONFIGURATION
# =============================================================================

class PositionConfig(Base):
    """
    Per-agency AI position configuration.
    Controls how each AI position behaves.
    """
    __tablename__ = "position_configs"

    config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)

    # Position
    position = Column(String(50), nullable=False)  # estimator, project_manager, etc

    # Mode: off, assist, full_ai
    mode = Column(String(20), nullable=False, default="assist")

    # Confidence threshold (pause below this)
    confidence_threshold = Column(Integer, default=90)

    # Assigned human for assist mode
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Statistics
    total_actions = Column(Integer, default=0)
    actions_auto_completed = Column(Integer, default=0)
    actions_flagged = Column(Integer, default=0)
    average_confidence = Column(Numeric(5, 2))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint
    __table_args__ = (
        Index("idx_position_agency", "agency_id", "position", unique=True),
    )


# =============================================================================
# CUSTOM FORM TEMPLATES
# =============================================================================

class FormTemplate(Base):
    """
    Custom form templates - allows users to use their own form formats.
    Can be created by:
    1. Scanning/photographing an existing paper form
    2. Uploading a PDF/image of their template
    3. AI extraction of fields from scanned document
    """
    __tablename__ = "form_templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)

    # Template info
    name = Column(String(255), nullable=False)
    form_type = Column(String(100), nullable=False)  # daily_report, inspection, jha, etc.
    description = Column(Text)

    # Format preference
    is_custom = Column(Boolean, default=True)  # True = user's format, False = ROOFIO format
    is_default = Column(Boolean, default=False)  # Default template for this form_type

    # Source document (scanned/uploaded)
    source_file_url = Column(String(500))  # URL to original uploaded file
    source_file_type = Column(String(50))  # pdf, jpg, png, heic

    # Extracted/defined fields
    fields = Column(JSON, default=list)  # [{name, type, position, required, default_value}]

    # Layout info (for rendering)
    layout = Column(JSON)  # {columns, rows, field_positions, styles}

    # Our flavor additions (always present even on custom forms)
    roofio_additions = Column(JSON, default=dict)  # {logo: true, timestamp: true, gps: true}

    # Preview image
    preview_url = Column(String(500))

    # Usage stats
    times_used = Column(Integer, default=0)

    # Status
    status = Column(String(50), default="active")  # active, archived, draft

    # Created by
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_form_template_agency", "agency_id"),
        Index("idx_form_template_type", "form_type"),
        Index("idx_form_template_default", "agency_id", "form_type", "is_default"),
    )


class FormSubmission(Base):
    """
    Submitted form instances - actual filled-out forms.
    Links to either custom or ROOFIO template.
    """
    __tablename__ = "form_submissions"

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agencies.agency_id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    template_id = Column(UUID(as_uuid=True), ForeignKey("form_templates.template_id"))

    # Form type (in case template is deleted)
    form_type = Column(String(100), nullable=False)

    # Filled data
    data = Column(JSON, nullable=False)  # {field_name: value, ...}

    # Attachments (photos, signatures)
    attachments = Column(JSON, default=list)  # [{name, url, type}]

    # Signature
    signature_url = Column(String(500))
    signed_by = Column(String(255))
    signed_at = Column(DateTime)

    # GPS & metadata
    gps_latitude = Column(Numeric(10, 8))
    gps_longitude = Column(Numeric(11, 8))
    device_info = Column(JSON)

    # Status
    status = Column(String(50), default="draft")  # draft, submitted, approved, rejected

    # Submitted by
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)

    # Indexes
    __table_args__ = (
        Index("idx_form_sub_agency", "agency_id"),
        Index("idx_form_sub_project", "project_id"),
        Index("idx_form_sub_type", "form_type"),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Agency",
    "User",
    "Project",
    "AuditLog",
    "AIActionLog",
    "PositionConfig",
    "FormTemplate",
    "FormSubmission",
]
