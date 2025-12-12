"""
ROOFIO Tier 1 CRUD Operations
=============================

Pure Python database operations for core entities.
All operations are async and tenant-scoped.

Cost: Near zero (just compute)
Latency: <50ms
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import Agency, User, Project, AuditLog, AIActionLog, PositionConfig
from common.database import get_db_session, get_tenant_session


# =============================================================================
# AGENCY CRUD
# =============================================================================

class AgencyCRUD:
    """CRUD operations for agencies"""

    @staticmethod
    async def create(
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Dict] = None,
        **kwargs
    ) -> Agency:
        """Create a new agency"""
        async with get_db_session() as session:
            agency = Agency(
                name=name,
                email=email,
                phone=phone,
                address=address,
                **kwargs
            )
            session.add(agency)
            await session.commit()
            await session.refresh(agency)
            return agency

    @staticmethod
    async def get(agency_id: UUID) -> Optional[Agency]:
        """Get agency by ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Agency).where(Agency.agency_id == agency_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(agency_id: UUID, **kwargs) -> Optional[Agency]:
        """Update agency fields"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Agency).where(Agency.agency_id == agency_id)
            )
            agency = result.scalar_one_or_none()
            if agency:
                for key, value in kwargs.items():
                    if hasattr(agency, key):
                        setattr(agency, key, value)
                agency.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(agency)
            return agency

    @staticmethod
    async def delete(agency_id: UUID) -> bool:
        """Delete agency (cascades to all related data)"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(Agency).where(Agency.agency_id == agency_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def list_all(limit: int = 100, offset: int = 0) -> List[Agency]:
        """List all agencies (admin only)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Agency)
                .order_by(Agency.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()


# =============================================================================
# USER CRUD
# =============================================================================

class UserCRUD:
    """CRUD operations for users (tenant-scoped)"""

    @staticmethod
    async def create(
        agency_id: UUID,
        email: str,
        name: str,
        role: str = "user",
        password_hash: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create a new user"""
        async with get_db_session() as session:
            user = User(
                agency_id=agency_id,
                email=email,
                name=name,
                role=role,
                password_hash=password_hash,
                **kwargs
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def get(user_id: UUID, agency_id: Optional[UUID] = None) -> Optional[User]:
        """Get user by ID (optionally verify agency)"""
        async with get_db_session() as session:
            query = select(User).where(User.user_id == user_id)
            if agency_id:
                query = query.where(User.agency_id == agency_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(user_id: UUID, agency_id: UUID, **kwargs) -> Optional[User]:
        """Update user fields (tenant-scoped)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(
                    User.user_id == user_id,
                    User.agency_id == agency_id
                )
            )
            user = result.scalar_one_or_none()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key) and key not in ['user_id', 'agency_id']:
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(user)
            return user

    @staticmethod
    async def delete(user_id: UUID, agency_id: UUID) -> bool:
        """Delete user (tenant-scoped)"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(User).where(
                    User.user_id == user_id,
                    User.agency_id == agency_id
                )
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def list_by_agency(agency_id: UUID, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users for an agency"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User)
                .where(User.agency_id == agency_id)
                .order_by(User.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()

    @staticmethod
    async def update_last_login(user_id: UUID) -> None:
        """Update user's last login timestamp"""
        async with get_db_session() as session:
            await session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await session.commit()


# =============================================================================
# PROJECT CRUD
# =============================================================================

class ProjectCRUD:
    """CRUD operations for projects (tenant-scoped)"""

    @staticmethod
    async def create(
        agency_id: UUID,
        name: str,
        address: Dict,
        project_type: Optional[str] = None,
        status: str = "bidding",
        **kwargs
    ) -> Project:
        """Create a new project"""
        async with get_db_session() as session:
            project = Project(
                agency_id=agency_id,
                name=name,
                address=address,
                project_type=project_type,
                status=status,
                **kwargs
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project

    @staticmethod
    async def get(project_id: UUID, agency_id: UUID) -> Optional[Project]:
        """Get project by ID (tenant-scoped)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Project).where(
                    Project.project_id == project_id,
                    Project.agency_id == agency_id
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(project_id: UUID, agency_id: UUID, **kwargs) -> Optional[Project]:
        """Update project fields (tenant-scoped)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Project).where(
                    Project.project_id == project_id,
                    Project.agency_id == agency_id
                )
            )
            project = result.scalar_one_or_none()
            if project:
                for key, value in kwargs.items():
                    if hasattr(project, key) and key not in ['project_id', 'agency_id']:
                        setattr(project, key, value)
                project.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(project)
            return project

    @staticmethod
    async def delete(project_id: UUID, agency_id: UUID) -> bool:
        """Delete project (tenant-scoped)"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(Project).where(
                    Project.project_id == project_id,
                    Project.agency_id == agency_id
                )
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def list_by_agency(
        agency_id: UUID,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Project]:
        """List projects for an agency (with optional status filter)"""
        async with get_db_session() as session:
            query = select(Project).where(Project.agency_id == agency_id)
            if status:
                query = query.where(Project.status == status)
            query = query.order_by(Project.updated_at.desc()).limit(limit).offset(offset)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def count_by_agency(agency_id: UUID, status: Optional[str] = None) -> int:
        """Count projects for an agency"""
        async with get_db_session() as session:
            query = select(func.count(Project.project_id)).where(Project.agency_id == agency_id)
            if status:
                query = query.where(Project.status == status)
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def search(
        agency_id: UUID,
        query: str,
        limit: int = 20
    ) -> List[Project]:
        """Search projects by name or number"""
        async with get_db_session() as session:
            search_pattern = f"%{query}%"
            result = await session.execute(
                select(Project)
                .where(
                    Project.agency_id == agency_id,
                    (Project.name.ilike(search_pattern) | Project.number.ilike(search_pattern))
                )
                .order_by(Project.updated_at.desc())
                .limit(limit)
            )
            return result.scalars().all()


# =============================================================================
# AUDIT LOG
# =============================================================================

class AuditLogCRUD:
    """CRUD operations for audit logs"""

    @staticmethod
    async def log(
        action: str,
        agency_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry"""
        async with get_db_session() as session:
            log = AuditLog(
                action=action,
                agency_id=agency_id,
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(log)
            await session.commit()
            return log

    @staticmethod
    async def list_by_entity(
        entity_type: str,
        entity_id: UUID,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AuditLog)
                .where(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id
                )
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()


# =============================================================================
# AI ACTION LOG
# =============================================================================

class AIActionLogCRUD:
    """CRUD operations for AI action logs"""

    @staticmethod
    async def log(
        agency_id: UUID,
        position: str,
        action_type: str,
        confidence_score: int,
        status: str,
        project_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        confidence_factors: Optional[Dict] = None,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        paused_reason: Optional[str] = None,
    ) -> AIActionLog:
        """Create an AI action log entry"""
        async with get_db_session() as session:
            log = AIActionLog(
                agency_id=agency_id,
                position=position,
                action_type=action_type,
                confidence_score=confidence_score,
                status=status,
                project_id=project_id,
                user_id=user_id,
                confidence_factors=confidence_factors,
                input_data=input_data,
                output_data=output_data,
                paused_reason=paused_reason,
            )
            session.add(log)
            await session.commit()
            return log

    @staticmethod
    async def list_pending_review(agency_id: UUID, limit: int = 50) -> List[AIActionLog]:
        """Get AI actions pending human review"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AIActionLog)
                .where(
                    AIActionLog.agency_id == agency_id,
                    AIActionLog.status.in_(["paused", "human_review"])
                )
                .order_by(AIActionLog.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def mark_reviewed(
        log_id: UUID,
        reviewed_by: UUID,
        review_action: str,
        review_notes: Optional[str] = None
    ) -> Optional[AIActionLog]:
        """Mark an AI action as reviewed"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AIActionLog).where(AIActionLog.log_id == log_id)
            )
            log = result.scalar_one_or_none()
            if log:
                log.reviewed_by = reviewed_by
                log.review_date = datetime.utcnow()
                log.review_action = review_action
                log.review_notes = review_notes
                log.status = "completed" if review_action == "approved" else "failed"
                await session.commit()
                await session.refresh(log)
            return log


# =============================================================================
# POSITION CONFIG
# =============================================================================

class PositionConfigCRUD:
    """CRUD operations for position configuration"""

    @staticmethod
    async def get_or_create(agency_id: UUID, position: str) -> PositionConfig:
        """Get or create position config"""
        async with get_db_session() as session:
            result = await session.execute(
                select(PositionConfig).where(
                    PositionConfig.agency_id == agency_id,
                    PositionConfig.position == position
                )
            )
            config = result.scalar_one_or_none()

            if not config:
                config = PositionConfig(
                    agency_id=agency_id,
                    position=position,
                    mode="assist",
                    confidence_threshold=90
                )
                session.add(config)
                await session.commit()
                await session.refresh(config)

            return config

    @staticmethod
    async def update_mode(agency_id: UUID, position: str, mode: str) -> Optional[PositionConfig]:
        """Update position mode (off, assist, full_ai)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(PositionConfig).where(
                    PositionConfig.agency_id == agency_id,
                    PositionConfig.position == position
                )
            )
            config = result.scalar_one_or_none()
            if config:
                config.mode = mode
                config.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(config)
            return config

    @staticmethod
    async def list_by_agency(agency_id: UUID) -> List[PositionConfig]:
        """Get all position configs for an agency"""
        async with get_db_session() as session:
            result = await session.execute(
                select(PositionConfig)
                .where(PositionConfig.agency_id == agency_id)
                .order_by(PositionConfig.position)
            )
            return result.scalars().all()

    @staticmethod
    async def increment_stats(
        agency_id: UUID,
        position: str,
        auto_completed: bool = False,
        flagged: bool = False
    ) -> None:
        """Increment position statistics"""
        async with get_db_session() as session:
            result = await session.execute(
                select(PositionConfig).where(
                    PositionConfig.agency_id == agency_id,
                    PositionConfig.position == position
                )
            )
            config = result.scalar_one_or_none()
            if config:
                config.total_actions = (config.total_actions or 0) + 1
                if auto_completed:
                    config.actions_auto_completed = (config.actions_auto_completed or 0) + 1
                if flagged:
                    config.actions_flagged = (config.actions_flagged or 0) + 1
                await session.commit()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgencyCRUD",
    "UserCRUD",
    "ProjectCRUD",
    "AuditLogCRUD",
    "AIActionLogCRUD",
    "PositionConfigCRUD",
]
