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
# EXPORTS
# =============================================================================

__all__ = [
    "health_router",
    "agency_router",
    "user_router",
    "project_router",
    "position_router",
    "ai_router",
]
