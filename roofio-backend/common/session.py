"""
ROOFIO Session Management
=========================

Redis-backed session management for serverless environments (Modal).

This is the KEY to making auth work on Modal:
- Sessions are stored in Upstash Redis (HTTP-based, no persistent connection needed)
- JWT tokens contain only session_id (not the full session)
- Session data is fetched/updated on every request
- Sliding expiration keeps active sessions alive

CRITICAL: All state lives in Redis, NOT in local memory.
This is what makes the system foolproof on serverless.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from upstash_redis import Redis
from jose import jwt, JWTError
from fastapi import HTTPException

from .config import (
    UPSTASH_REDIS_REST_URL,
    UPSTASH_REDIS_REST_TOKEN,
    JWT_SECRET,
    JWT_ALGORITHM,
    SESSION_TIMEOUT_SECONDS,
)

# =============================================================================
# REDIS CLIENT (Singleton)
# =============================================================================

_redis_client: Optional[Redis] = None


def get_redis() -> Redis:
    """Get or create Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            url=UPSTASH_REDIS_REST_URL,
            token=UPSTASH_REDIS_REST_TOKEN,
        )
    return _redis_client


# =============================================================================
# ROLE ENUM
# =============================================================================

class Role(str, Enum):
    """The 5 ROOFIO roles in the permission hierarchy"""
    SUPER_ADMIN = "super_admin"
    AGENCY_ADMIN = "agency_admin"
    PROJECT_MANAGER = "project_manager"
    FOREMAN = "foreman"
    APPRENTICE = "apprentice"


# =============================================================================
# SESSION DATA CLASS
# =============================================================================

@dataclass
class SessionData:
    """Session data stored in Redis"""
    user_id: str
    agency_id: str
    role: Role
    email: str
    created_at: str
    last_activity: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for Redis storage"""
        return {
            "user_id": self.user_id,
            "agency_id": self.agency_id,
            "role": self.role.value if isinstance(self.role, Role) else self.role,
            "email": self.email,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "ip_address": self.ip_address or "",
            "user_agent": self.user_agent or "",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        """Create from dictionary (Redis data)"""
        return cls(
            user_id=data.get("user_id", ""),
            agency_id=data.get("agency_id", ""),
            role=Role(data.get("role", "apprentice")),
            email=data.get("email", ""),
            created_at=data.get("created_at", ""),
            last_activity=data.get("last_activity", ""),
            ip_address=data.get("ip_address") or None,
            user_agent=data.get("user_agent") or None,
        )


@dataclass
class CurrentUser:
    """The authenticated user context passed to route handlers"""
    user_id: str
    agency_id: str
    role: Role
    email: str
    session_id: str
    permissions: List[str]


# =============================================================================
# SESSION MANAGER
# =============================================================================

class SessionManager:
    """
    Redis-backed session management for serverless environments.

    Key Features:
    - Stateless: All data lives in Redis
    - Sliding window: Sessions auto-extend on activity
    - Multi-device: Track all sessions per user
    - Secure: JWT only contains session_id reference
    """

    @staticmethod
    def create_session(
        user_id: str,
        agency_id: str,
        role: str,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Create a new session and return a JWT token.

        The session data lives in Redis.
        The JWT only contains the session_id for lookup.
        """
        redis = get_redis()
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Session data to store in Redis
        session_data = SessionData(
            user_id=user_id,
            agency_id=agency_id,
            role=Role(role) if isinstance(role, str) else role,
            email=email,
            created_at=now.isoformat(),
            last_activity=now.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Store session in Redis with hash map
        redis.hset(f"session:{session_id}", values=session_data.to_dict())
        redis.expire(f"session:{session_id}", SESSION_TIMEOUT_SECONDS)

        # Track active sessions per user (for "log out all devices")
        redis.sadd(f"user_sessions:{user_id}", session_id)
        redis.expire(f"user_sessions:{user_id}", SESSION_TIMEOUT_SECONDS * 2)

        # Create JWT token containing session_id
        token_expiry = now + timedelta(seconds=SESSION_TIMEOUT_SECONDS)
        token_data = {
            "session_id": session_id,
            "user_id": user_id,  # Included for quick access without Redis hit
            "agency_id": agency_id,
            "exp": token_expiry,
            "iat": now,
        }

        token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def validate_session(token: str) -> SessionData:
        """
        Validate JWT and return full session data from Redis.

        Raises HTTPException if invalid/expired.
        """
        redis = get_redis()

        try:
            # Decode JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            session_id = payload.get("session_id")

            if not session_id:
                raise HTTPException(status_code=401, detail="Invalid token structure")

            # Get full session from Redis
            session_dict = redis.hgetall(f"session:{session_id}")

            if not session_dict:
                raise HTTPException(status_code=401, detail="Session expired or invalid")

            # Refresh session expiration (sliding window)
            redis.expire(f"session:{session_id}", SESSION_TIMEOUT_SECONDS)

            # Update last activity
            now = datetime.utcnow().isoformat()
            redis.hset(f"session:{session_id}", "last_activity", now)

            return SessionData.from_dict(session_dict)

        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    @staticmethod
    def destroy_session(token: str) -> bool:
        """Logout - destroy session in Redis"""
        redis = get_redis()

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            session_id = payload.get("session_id")
            user_id = payload.get("user_id")

            if session_id:
                redis.delete(f"session:{session_id}")

            if user_id and session_id:
                redis.srem(f"user_sessions:{user_id}", session_id)

            return True
        except JWTError:
            return False  # Token already invalid

    @staticmethod
    def destroy_all_user_sessions(user_id: str) -> int:
        """Logout all devices for a user"""
        redis = get_redis()
        session_ids = redis.smembers(f"user_sessions:{user_id}")
        count = 0

        for session_id in session_ids or []:
            redis.delete(f"session:{session_id}")
            count += 1

        redis.delete(f"user_sessions:{user_id}")
        return count

    @staticmethod
    def get_active_sessions(user_id: str) -> List[dict]:
        """Get all active sessions for a user (for session management UI)"""
        redis = get_redis()
        session_ids = redis.smembers(f"user_sessions:{user_id}")
        sessions = []

        for session_id in session_ids or []:
            session_dict = redis.hgetall(f"session:{session_id}")
            if session_dict:
                sessions.append({
                    "session_id": session_id,
                    **session_dict,
                })

        return sessions

    @staticmethod
    def get_session_by_id(session_id: str) -> Optional[SessionData]:
        """Get session data by session ID (used internally)"""
        redis = get_redis()
        session_dict = redis.hgetall(f"session:{session_id}")

        if not session_dict:
            return None

        return SessionData.from_dict(session_dict)

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode a JWT token without validation (for extracting session_id).
        Use validate_session for full validation.
        """
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            return {}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Redis
    "get_redis",

    # Enums
    "Role",

    # Data classes
    "SessionData",
    "CurrentUser",

    # Session Manager
    "SessionManager",
]
