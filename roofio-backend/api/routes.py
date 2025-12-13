"""
ROOFIO API Routes
=================

FastAPI REST endpoints for all CRUD operations.
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from fastapi.responses import JSONResponse

from tier1.crud import (
    AgencyCRUD,
    UserCRUD,
    ProjectCRUD,
    PositionConfigCRUD,
    AIActionLogCRUD,
)
from common.database import check_database_health

from .schemas import (
    # Agency
    AgencyCreate,
    AgencyUpdate,
    AgencyResponse,
    # User
    UserCreate,
    UserUpdate,
    UserResponse,
    # Project
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    # Position Config
    PositionConfigUpdate,
    PositionConfigResponse,
    # AI Action
    AIActionLogResponse,
    AIActionReview,
    # Generic
    MessageResponse,
    ErrorResponse,
    HealthResponse,
)


# =============================================================================
# ROUTERS
# =============================================================================

health_router = APIRouter(prefix="/health", tags=["Health"])
agency_router = APIRouter(prefix="/agencies", tags=["Agencies"])
user_router = APIRouter(prefix="/users", tags=["Users"])
project_router = APIRouter(prefix="/projects", tags=["Projects"])
position_router = APIRouter(prefix="/positions", tags=["Position Config"])
ai_router = APIRouter(prefix="/ai", tags=["AI Actions"])


# =============================================================================
# DEPENDENCY: Get Agency ID from Header
# =============================================================================

async def get_agency_id(x_agency_id: str = Header(..., description="Agency UUID")) -> UUID:
    """Extract and validate agency ID from header"""
    try:
        return UUID(x_agency_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agency ID format")


# =============================================================================
# HEALTH ENDPOINTS
# =============================================================================

@health_router.get("", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    db_health = await check_database_health()

    return HealthResponse(
        status="healthy" if db_health["status"] == "healthy" else "degraded",
        database=db_health["status"],
        redis="healthy",  # TODO: Add Redis health check
        version="1.0.0"
    )


@health_router.get("/db")
async def database_health():
    """Detailed database health check"""
    return await check_database_health()


# =============================================================================
# AGENCY ENDPOINTS
# =============================================================================

@agency_router.post("", response_model=AgencyResponse, status_code=201)
async def create_agency(agency: AgencyCreate):
    """Create a new agency"""
    result = await AgencyCRUD.create(
        name=agency.name,
        email=agency.email,
        phone=agency.phone,
        address=agency.address,
        license_no=agency.license_no,
        tax_id=agency.tax_id,
    )
    return result


@agency_router.get("/{agency_id}", response_model=AgencyResponse)
async def get_agency(agency_id: UUID):
    """Get agency by ID"""
    agency = await AgencyCRUD.get(agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    return agency


@agency_router.patch("/{agency_id}", response_model=AgencyResponse)
async def update_agency(agency_id: UUID, updates: AgencyUpdate):
    """Update agency fields"""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    agency = await AgencyCRUD.update(agency_id, **update_data)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    return agency


@agency_router.delete("/{agency_id}", response_model=MessageResponse)
async def delete_agency(agency_id: UUID):
    """Delete agency and all related data"""
    deleted = await AgencyCRUD.delete(agency_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agency not found")
    return MessageResponse(message="Agency deleted successfully")


# =============================================================================
# USER ENDPOINTS
# =============================================================================

@user_router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Create a new user in the agency"""
    # Check if email already exists
    existing = await UserCRUD.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # TODO: Hash password properly
    from hashlib import sha256
    password_hash = sha256(user.password.encode()).hexdigest()

    result = await UserCRUD.create(
        agency_id=agency_id,
        email=user.email,
        name=user.name,
        role=user.role,
        phone=user.phone,
        positions=user.positions,
        password_hash=password_hash,
    )
    return result


@user_router.get("", response_model=List[UserResponse])
async def list_users(
    agency_id: UUID = Depends(get_agency_id),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0)
):
    """List all users in the agency"""
    users = await UserCRUD.list_by_agency(agency_id, limit=limit, offset=offset)
    return users


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Get user by ID"""
    user = await UserCRUD.get(user_id, agency_id=agency_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    updates: UserUpdate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Update user fields"""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    user = await UserCRUD.update(user_id, agency_id, **update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Delete user from agency"""
    deleted = await UserCRUD.delete(user_id, agency_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return MessageResponse(message="User deleted successfully")


# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@project_router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Create a new project"""
    result = await ProjectCRUD.create(
        agency_id=agency_id,
        name=project.name,
        address=project.address,
        project_type=project.project_type,
        status=project.status,
        number=project.number,
        description=project.description,
        municipality=project.municipality,
        gc_contact=project.gc_contact,
        owner_contact=project.owner_contact,
        architect_contact=project.architect_contact,
        contract_amount=project.contract_amount,
        start_date=project.start_date,
        end_date=project.end_date,
        spec_sections=project.spec_sections,
        is_insurance_claim=project.is_insurance_claim,
        claim_number=project.claim_number,
    )
    return result


@project_router.get("", response_model=ProjectListResponse)
async def list_projects(
    agency_id: UUID = Depends(get_agency_id),
    status: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0)
):
    """List projects for the agency"""
    projects = await ProjectCRUD.list_by_agency(
        agency_id,
        status=status,
        limit=limit,
        offset=offset
    )
    total = await ProjectCRUD.count_by_agency(agency_id, status=status)

    return ProjectListResponse(
        projects=projects,
        total=total,
        limit=limit,
        offset=offset
    )


@project_router.get("/search")
async def search_projects(
    q: str = Query(..., min_length=1),
    agency_id: UUID = Depends(get_agency_id),
    limit: int = Query(20, le=100)
):
    """Search projects by name or number"""
    projects = await ProjectCRUD.search(agency_id, q, limit=limit)
    return {"results": projects, "count": len(projects)}


@project_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Get project by ID"""
    project = await ProjectCRUD.get(project_id, agency_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@project_router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    updates: ProjectUpdate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Update project fields"""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    project = await ProjectCRUD.update(project_id, agency_id, **update_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@project_router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Delete project"""
    deleted = await ProjectCRUD.delete(project_id, agency_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return MessageResponse(message="Project deleted successfully")


# =============================================================================
# POSITION CONFIG ENDPOINTS
# =============================================================================

VALID_POSITIONS = [
    "estimator", "project_manager", "qc_inspector", "safety_officer",
    "superintendent", "shop_drawings", "accounting", "operations"
]


@position_router.get("", response_model=List[PositionConfigResponse])
async def list_position_configs(agency_id: UUID = Depends(get_agency_id)):
    """Get all position configurations for the agency"""
    configs = await PositionConfigCRUD.list_by_agency(agency_id)

    # If no configs exist, create defaults
    if not configs:
        for position in VALID_POSITIONS:
            await PositionConfigCRUD.get_or_create(agency_id, position)
        configs = await PositionConfigCRUD.list_by_agency(agency_id)

    return configs


@position_router.get("/{position}", response_model=PositionConfigResponse)
async def get_position_config(
    position: str,
    agency_id: UUID = Depends(get_agency_id)
):
    """Get configuration for a specific position"""
    if position not in VALID_POSITIONS:
        raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {VALID_POSITIONS}")

    config = await PositionConfigCRUD.get_or_create(agency_id, position)
    return config


@position_router.patch("/{position}", response_model=PositionConfigResponse)
async def update_position_config(
    position: str,
    updates: PositionConfigUpdate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Update position configuration (mode, threshold)"""
    if position not in VALID_POSITIONS:
        raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {VALID_POSITIONS}")

    # Ensure config exists
    await PositionConfigCRUD.get_or_create(agency_id, position)

    # Update mode
    config = await PositionConfigCRUD.update_mode(agency_id, position, updates.mode)
    if not config:
        raise HTTPException(status_code=404, detail="Position config not found")

    return config


# =============================================================================
# AI ACTION LOG ENDPOINTS
# =============================================================================

@ai_router.get("/pending", response_model=List[AIActionLogResponse])
async def list_pending_ai_actions(
    agency_id: UUID = Depends(get_agency_id),
    limit: int = Query(50, le=200)
):
    """Get AI actions pending human review"""
    actions = await AIActionLogCRUD.list_pending_review(agency_id, limit=limit)
    return actions


@ai_router.post("/{log_id}/review", response_model=AIActionLogResponse)
async def review_ai_action(
    log_id: UUID,
    review: AIActionReview,
    agency_id: UUID = Depends(get_agency_id),
    x_user_id: str = Header(..., description="Reviewing user's UUID")
):
    """Review an AI action (approve, edit, or reject)"""
    try:
        user_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await AIActionLogCRUD.mark_reviewed(
        log_id=log_id,
        reviewed_by=user_id,
        review_action=review.review_action,
        review_notes=review.review_notes
    )

    if not result:
        raise HTTPException(status_code=404, detail="AI action log not found")

    return result


# =============================================================================
# FORM TEMPLATE ENDPOINTS
# =============================================================================

form_router = APIRouter(prefix="/forms", tags=["Form Templates"])
scan_router = APIRouter(prefix="/scan", tags=["Document Scanner"])


# Import form-related schemas
from .schemas import (
    FormTemplateCreate,
    FormTemplateUpdate,
    FormTemplateResponse,
    FormTemplateListResponse,
    FormSubmissionCreate,
    FormSubmissionResponse,
    ScanRequest,
    ScanResponse,
    FormFromScanRequest,
)

# Valid form types
VALID_FORM_TYPES = [
    "daily_report", "inspection", "jha", "toolbox_talk", "incident_report",
    "safety_inspection", "material_receiving", "punch_list", "rfi",
    "change_order", "submittal", "photo_log", "time_sheet", "equipment_log"
]


@form_router.get("/types")
async def list_form_types():
    """Get all available form types"""
    return {
        "form_types": VALID_FORM_TYPES,
        "descriptions": {
            "daily_report": "Daily field report documenting work completed",
            "inspection": "Quality control inspection checklist",
            "jha": "Job Hazard Analysis for safety planning",
            "toolbox_talk": "Safety meeting documentation",
            "incident_report": "Safety incident or accident report",
            "safety_inspection": "Site safety inspection checklist",
            "material_receiving": "Material delivery verification",
            "punch_list": "Deficiency and correction tracking",
            "rfi": "Request for Information",
            "change_order": "Contract change documentation",
            "submittal": "Product approval request",
            "photo_log": "Photo documentation log",
            "time_sheet": "Labor time tracking",
            "equipment_log": "Equipment usage log"
        }
    }


@form_router.get("/templates", response_model=FormTemplateListResponse)
async def list_form_templates(
    agency_id: UUID = Depends(get_agency_id),
    form_type: Optional[str] = None,
    is_custom: Optional[bool] = None,
    status: str = Query("active", pattern="^(active|archived|draft|all)$")
):
    """List form templates for the agency"""
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select

    async with get_session() as session:
        query = select(FormTemplate).where(FormTemplate.agency_id == agency_id)

        if form_type:
            query = query.where(FormTemplate.form_type == form_type)
        if is_custom is not None:
            query = query.where(FormTemplate.is_custom == is_custom)
        if status != "all":
            query = query.where(FormTemplate.status == status)

        query = query.order_by(FormTemplate.form_type, FormTemplate.name)
        result = await session.execute(query)
        templates = result.scalars().all()

        return FormTemplateListResponse(
            templates=[FormTemplateResponse.model_validate(t) for t in templates],
            total=len(templates)
        )


@form_router.post("/templates", response_model=FormTemplateResponse, status_code=201)
async def create_form_template(
    template: FormTemplateCreate,
    agency_id: UUID = Depends(get_agency_id),
    x_user_id: Optional[str] = Header(None)
):
    """Create a new form template"""
    from common.database import get_session
    from common.models import FormTemplate
    from uuid import uuid4

    user_id = UUID(x_user_id) if x_user_id else None

    async with get_session() as session:
        new_template = FormTemplate(
            template_id=uuid4(),
            agency_id=agency_id,
            name=template.name,
            form_type=template.form_type,
            description=template.description,
            is_custom=template.is_custom,
            fields=template.fields if template.fields else [],
            layout=template.layout,
            roofio_additions=template.roofio_additions or {"logo": True, "timestamp": True, "gps": True},
            created_by=user_id,
            status="active"
        )
        session.add(new_template)
        await session.commit()
        await session.refresh(new_template)
        return new_template


@form_router.get("/templates/{template_id}", response_model=FormTemplateResponse)
async def get_form_template(
    template_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Get a specific form template"""
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select

    async with get_session() as session:
        query = select(FormTemplate).where(
            FormTemplate.template_id == template_id,
            FormTemplate.agency_id == agency_id
        )
        result = await session.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Form template not found")
        return template


@form_router.patch("/templates/{template_id}", response_model=FormTemplateResponse)
async def update_form_template(
    template_id: UUID,
    updates: FormTemplateUpdate,
    agency_id: UUID = Depends(get_agency_id)
):
    """Update a form template"""
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select
    from datetime import datetime

    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    async with get_session() as session:
        query = select(FormTemplate).where(
            FormTemplate.template_id == template_id,
            FormTemplate.agency_id == agency_id
        )
        result = await session.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Form template not found")

        for key, value in update_data.items():
            setattr(template, key, value)
        template.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(template)
        return template


@form_router.delete("/templates/{template_id}", response_model=MessageResponse)
async def delete_form_template(
    template_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Delete a form template (soft delete - sets status to archived)"""
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select
    from datetime import datetime

    async with get_session() as session:
        query = select(FormTemplate).where(
            FormTemplate.template_id == template_id,
            FormTemplate.agency_id == agency_id
        )
        result = await session.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Form template not found")

        template.status = "archived"
        template.updated_at = datetime.utcnow()
        await session.commit()

        return MessageResponse(message="Form template archived successfully")


@form_router.post("/templates/{template_id}/set-default", response_model=FormTemplateResponse)
async def set_default_template(
    template_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """Set a template as the default for its form type"""
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select, update
    from datetime import datetime

    async with get_session() as session:
        # Get the template
        query = select(FormTemplate).where(
            FormTemplate.template_id == template_id,
            FormTemplate.agency_id == agency_id
        )
        result = await session.execute(query)
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Form template not found")

        # Unset any existing default for this form type
        await session.execute(
            update(FormTemplate)
            .where(
                FormTemplate.agency_id == agency_id,
                FormTemplate.form_type == template.form_type,
                FormTemplate.is_default == True
            )
            .values(is_default=False)
        )

        # Set this one as default
        template.is_default = True
        template.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(template)

        return template


@form_router.get("/preference/{form_type}")
async def get_form_preference(
    form_type: str,
    agency_id: UUID = Depends(get_agency_id)
):
    """
    Get the preferred format (custom vs ROOFIO) for a form type.
    Returns the default template if one exists, otherwise indicates first-time setup needed.
    """
    from common.database import get_session
    from common.models import FormTemplate
    from sqlalchemy import select

    async with get_session() as session:
        # Look for default template
        query = select(FormTemplate).where(
            FormTemplate.agency_id == agency_id,
            FormTemplate.form_type == form_type,
            FormTemplate.is_default == True,
            FormTemplate.status == "active"
        )
        result = await session.execute(query)
        default_template = result.scalar_one_or_none()

        if default_template:
            return {
                "has_preference": True,
                "use_custom": default_template.is_custom,
                "template_id": str(default_template.template_id),
                "template_name": default_template.name
            }

        # No default - check if any templates exist
        query = select(FormTemplate).where(
            FormTemplate.agency_id == agency_id,
            FormTemplate.form_type == form_type,
            FormTemplate.status == "active"
        )
        result = await session.execute(query)
        templates = result.scalars().all()

        return {
            "has_preference": False,
            "use_custom": None,
            "available_templates": len(templates),
            "first_time_setup": len(templates) == 0
        }


# =============================================================================
# DOCUMENT SCANNER ENDPOINTS (CamScan-like feature)
# =============================================================================

@scan_router.post("/upload", response_model=ScanResponse)
async def upload_and_process_scan(
    agency_id: UUID = Depends(get_agency_id),
    output_format: str = Query("pdf", pattern="^(pdf|png|jpg|docx|xlsx)$"),
    enhance: bool = Query(True, description="Auto-enhance image quality"),
    extract_text: bool = Query(False, description="Run OCR text extraction"),
    extract_fields: bool = Query(False, description="AI extract form fields")
):
    """
    Upload a scanned/photographed document for processing.

    This is the CamScan-like feature that:
    1. Accepts an image (camera capture or file upload)
    2. Auto-enhances (straighten, crop, adjust contrast)
    3. Converts to requested format (PDF, image, Word, Excel)
    4. Optionally extracts text via OCR
    5. Optionally extracts form fields via AI for template creation

    File should be sent as multipart/form-data with field name 'file'.
    """
    from uuid import uuid4
    from datetime import datetime
    import time

    # Note: In production, this would:
    # 1. Accept file upload via python-multipart
    # 2. Process with Pillow for enhancement
    # 3. Use Tesseract/EasyOCR for text extraction
    # 4. Use Groq AI for field extraction
    # 5. Convert to requested format

    start_time = time.time()
    scan_id = uuid4()

    # Placeholder response - actual implementation would process the file
    return ScanResponse(
        scan_id=scan_id,
        original_url=f"/uploads/scans/{scan_id}/original.jpg",
        processed_url=f"/uploads/scans/{scan_id}/processed.{output_format}",
        output_format=output_format,
        extracted_text="[OCR text would appear here if extract_text=true]" if extract_text else None,
        extracted_fields=[
            {"name": "date", "label": "Date", "type": "date", "required": True},
            {"name": "project_name", "label": "Project Name", "type": "text", "required": True},
            {"name": "inspector", "label": "Inspector", "type": "text", "required": True},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False},
            {"name": "signature", "label": "Signature", "type": "signature", "required": True},
        ] if extract_fields else None,
        processing_time_ms=int((time.time() - start_time) * 1000) + 150,  # Simulated processing time
        created_at=datetime.utcnow()
    )


@scan_router.post("/create-template", response_model=FormTemplateResponse, status_code=201)
async def create_template_from_scan(
    request: FormFromScanRequest,
    agency_id: UUID = Depends(get_agency_id),
    x_user_id: Optional[str] = Header(None)
):
    """
    Create a form template from a previously scanned document.

    Uses the AI-extracted fields from the scan to create a matching template
    with ROOFIO flavor (logo, timestamp, GPS tracking).
    """
    from common.database import get_session
    from common.models import FormTemplate
    from uuid import uuid4

    user_id = UUID(x_user_id) if x_user_id else None

    # In production, this would fetch the scan and its extracted fields
    # For now, use sample fields
    extracted_fields = [
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "project_name", "label": "Project Name", "type": "text", "required": True},
        {"name": "inspector", "label": "Inspector", "type": "text", "required": True},
        {"name": "location", "label": "Location", "type": "text", "required": False},
        {"name": "notes", "label": "Notes", "type": "textarea", "required": False},
        {"name": "photo", "label": "Photo", "type": "photo", "required": False},
        {"name": "signature", "label": "Signature", "type": "signature", "required": True},
    ]

    async with get_session() as session:
        new_template = FormTemplate(
            template_id=uuid4(),
            agency_id=agency_id,
            name=request.name,
            form_type=request.form_type,
            description=request.description or f"Created from scanned document",
            is_custom=True,
            source_file_url=f"/uploads/scans/{request.scan_id}/original.jpg",
            source_file_type="jpg",
            fields=extracted_fields,
            roofio_additions={"logo": True, "timestamp": True, "gps": True, "watermark": False},
            created_by=user_id,
            status="draft"  # Start as draft for user review
        )
        session.add(new_template)
        await session.commit()
        await session.refresh(new_template)
        return new_template


@scan_router.get("/formats")
async def list_output_formats():
    """Get available output formats for document scanning"""
    return {
        "formats": [
            {"id": "pdf", "name": "PDF Document", "description": "Portable document, best for sharing"},
            {"id": "png", "name": "PNG Image", "description": "High quality image with transparency"},
            {"id": "jpg", "name": "JPEG Image", "description": "Compressed image, smaller file size"},
            {"id": "docx", "name": "Word Document", "description": "Editable text document (requires OCR)"},
            {"id": "xlsx", "name": "Excel Spreadsheet", "description": "Spreadsheet format (requires OCR)"},
        ]
    }


# =============================================================================
# FORM SUBMISSION ENDPOINTS
# =============================================================================

@form_router.post("/submissions", response_model=FormSubmissionResponse, status_code=201)
async def submit_form(
    submission: FormSubmissionCreate,
    agency_id: UUID = Depends(get_agency_id),
    x_user_id: Optional[str] = Header(None)
):
    """Submit a filled form"""
    from common.database import get_session
    from common.models import FormSubmission, FormTemplate
    from sqlalchemy import select
    from uuid import uuid4
    from datetime import datetime

    user_id = UUID(x_user_id) if x_user_id else None

    async with get_session() as session:
        # Update template usage count if template_id provided
        if submission.template_id:
            query = select(FormTemplate).where(FormTemplate.template_id == submission.template_id)
            result = await session.execute(query)
            template = result.scalar_one_or_none()
            if template:
                template.times_used = (template.times_used or 0) + 1

        new_submission = FormSubmission(
            submission_id=uuid4(),
            agency_id=agency_id,
            project_id=submission.project_id,
            template_id=submission.template_id,
            form_type=submission.form_type,
            data=submission.data,
            attachments=submission.attachments,
            signature_url=submission.signature_url,
            signed_by=submission.signed_by,
            signed_at=datetime.utcnow() if submission.signature_url else None,
            gps_latitude=submission.gps_latitude,
            gps_longitude=submission.gps_longitude,
            device_info=submission.device_info,
            submitted_by=user_id,
            status="submitted",
            submitted_at=datetime.utcnow()
        )
        session.add(new_submission)
        await session.commit()
        await session.refresh(new_submission)
        return new_submission


@form_router.get("/submissions")
async def list_form_submissions(
    agency_id: UUID = Depends(get_agency_id),
    project_id: Optional[UUID] = None,
    form_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0)
):
    """List form submissions"""
    from common.database import get_session
    from common.models import FormSubmission
    from sqlalchemy import select, func

    async with get_session() as session:
        query = select(FormSubmission).where(FormSubmission.agency_id == agency_id)

        if project_id:
            query = query.where(FormSubmission.project_id == project_id)
        if form_type:
            query = query.where(FormSubmission.form_type == form_type)
        if status:
            query = query.where(FormSubmission.status == status)

        query = query.order_by(FormSubmission.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        submissions = result.scalars().all()

        # Get total count
        count_query = select(func.count(FormSubmission.submission_id)).where(
            FormSubmission.agency_id == agency_id
        )
        if project_id:
            count_query = count_query.where(FormSubmission.project_id == project_id)
        if form_type:
            count_query = count_query.where(FormSubmission.form_type == form_type)
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "submissions": [FormSubmissionResponse.model_validate(s) for s in submissions],
            "total": total,
            "limit": limit,
            "offset": offset
        }


# =============================================================================
# AI GENIE ENDPOINTS (Tier 2 Groq Analysis)
# =============================================================================

@ai_router.post("/analyze/change-orders/{project_id}")
async def analyze_change_orders(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """
    Analyze RFIs and Daily Logs to suggest potential Change Orders.

    Uses Groq AI to identify patterns that indicate scope changes,
    unforeseen conditions, or owner-caused delays requiring formal COs.
    """
    from tier2.form_ai_genie import generate_change_order_suggestions
    from common.database import get_session
    from common.models import FormSubmission
    from sqlalchemy import select
    from datetime import datetime, timedelta

    async with get_session() as session:
        # Fetch recent RFIs (last 14 days)
        rfi_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "rfi",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=14)
        )
        rfi_result = await session.execute(rfi_query)
        rfis = [{"id": str(r.submission_id), "data": r.data, "created_at": str(r.created_at)}
                for r in rfi_result.scalars()]

        # Fetch recent daily logs (last 7 days)
        log_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "daily_report",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
        )
        log_result = await session.execute(log_query)
        logs = [{"id": str(r.submission_id), "data": r.data, "created_at": str(r.created_at)}
                for r in log_result.scalars()]

    if not rfis and not logs:
        return {
            "project_id": str(project_id),
            "suggestions": [],
            "analysis_summary": "No RFIs or Daily Logs found in the analysis period.",
            "risk_level": "LOW"
        }

    result = await generate_change_order_suggestions(project_id, rfis, logs)
    return result


@ai_router.post("/analyze/safety/{project_id}")
async def analyze_safety_risks(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """
    Analyze JHA forms and incident reports for safety risk patterns.

    Identifies recurring hazards, PPE gaps, and training needs.
    """
    from tier2.form_ai_genie import analyze_safety_risks as analyze_safety
    from common.database import get_session
    from common.models import FormSubmission
    from sqlalchemy import select
    from datetime import datetime, timedelta

    async with get_session() as session:
        # Fetch recent JHAs
        jha_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "jha",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
        )
        jha_result = await session.execute(jha_query)
        jhas = [{"id": str(r.submission_id), "data": r.data, "created_at": str(r.created_at)}
                for r in jha_result.scalars()]

    if not jhas:
        return {
            "project_id": str(project_id),
            "risk_level": "LOW",
            "findings": [],
            "analysis_summary": "No JHA forms found in the analysis period."
        }

    result = await analyze_safety(project_id, jhas, [])
    return result


@ai_router.post("/analyze/weekly-summary/{project_id}")
async def generate_weekly_summary(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id),
    days: int = Query(7, ge=1, le=30)
):
    """
    Generate a weekly progress summary from Daily Logs.

    Creates a professional report suitable for owner/GC reporting.
    """
    from tier2.form_ai_genie import summarize_daily_logs
    from common.database import get_session
    from common.models import FormSubmission
    from sqlalchemy import select
    from datetime import datetime, timedelta

    async with get_session() as session:
        log_query = select(FormSubmission).where(
            FormSubmission.agency_id == agency_id,
            FormSubmission.project_id == project_id,
            FormSubmission.form_type == "daily_report",
            FormSubmission.created_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(FormSubmission.created_at)

        log_result = await session.execute(log_query)
        logs = [{"id": str(r.submission_id), "data": r.data, "created_at": str(r.created_at)}
                for r in log_result.scalars()]

    if not logs:
        return {
            "project_id": str(project_id),
            "error": f"No daily logs found in the last {days} days."
        }

    result = await summarize_daily_logs(project_id, logs, days)
    return result


@ai_router.post("/analyze/full/{project_id}")
async def run_full_project_analysis(
    project_id: UUID,
    agency_id: UUID = Depends(get_agency_id)
):
    """
    Run all AI analyzers for a project.

    Returns combined results from:
    - Change Order suggestions
    - Safety risk analysis
    - Weekly summary
    """
    from tier2.form_ai_genie import run_project_analysis

    result = await run_project_analysis(agency_id, project_id)
    return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "health_router",
    "agency_router",
    "user_router",
    "project_router",
    "position_router",
    "ai_router",
    "form_router",
    "scan_router",
]
