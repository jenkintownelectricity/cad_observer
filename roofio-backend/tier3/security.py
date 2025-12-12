"""
ROOFIO Security Module - The Foundation
========================================

This module handles everything that needs to survive container restarts:
- Redis-backed session management
- JWT token handling with sliding expiration
- 3-legged OAuth flow with state persistence
- RBAC permission system
- Encryption utilities for stored tokens
- Circuit breaker pattern for external services

CRITICAL: All state lives in Redis/Upstash, NOT in local memory.
This is what makes the system foolproof on serverless (Modal).
"""

import os
import uuid
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable, TypeVar
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode

# External dependencies
from upstash_redis import Redis
from jose import jwt, JWTError
from cryptography.fernet import Fernet
from fastapi import Request, Response, HTTPException, Depends
from pydantic import BaseModel

# Initialize Upstash Redis (HTTP-based, connectionless)
# This survives container restarts because state lives externally
redis = Redis(
    url=os.environ.get("UPSTASH_REDIS_REST_URL", ""),
    token=os.environ.get("UPSTASH_REDIS_REST_TOKEN", ""),
)

# =============================================================================
# CONFIGURATION
# =============================================================================

JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour
SESSION_REFRESH_THRESHOLD = 300  # Refresh if <5 min remaining
OAUTH_STATE_EXPIRATION = 600  # 10 minutes for OAuth flow
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key())

# Initialize encryption cipher
cipher = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())


# =============================================================================
# DATA CLASSES
# =============================================================================

class Role(str, Enum):
    """The 5 ROOFIO roles in the permission hierarchy"""
    SUPER_ADMIN = "super_admin"
    AGENCY_ADMIN = "agency_admin"
    PROJECT_MANAGER = "project_manager"
    FOREMAN = "foreman"
    APPRENTICE = "apprentice"


@dataclass
class Permission:
    """A single permission definition"""
    resource: str
    action: str  # 'read', 'write', 'delete', '*'
    
    def __str__(self):
        return f"{self.resource}:{self.action}"


# RBAC Permission Matrix
ROLE_PERMISSIONS: Dict[Role, List[str]] = {
    Role.SUPER_ADMIN: ["*:*"],  # All permissions
    Role.AGENCY_ADMIN: [
        "projects:*",
        "users:*",
        "forms:*",
        "reports:*",
        "integrations:*",
        "billing:*",
        "ai:*",
    ],
    Role.PROJECT_MANAGER: [
        "projects:read",
        "projects:write",
        "daily_logs:*",
        "forms:*",
        "reports:read",
        "photos:*",
        "ai:basic",
    ],
    Role.FOREMAN: [
        "projects:read",
        "daily_logs:read",
        "daily_logs:write",
        "forms:read",
        "forms:submit",
        "photos:upload",
        "ai:basic",
    ],
    Role.APPRENTICE: [
        "projects:read",
        "daily_logs:read",
        "forms:read",
    ],
}


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
        return cls(
            user_id=data.get("user_id", ""),
            agency_id=data.get("agency_id", ""),
            role=Role(data.get("role", "apprentice")),
            email=data.get("email", ""),
            created_at=data.get("created_at", ""),
            last_activity=data.get("last_activity", ""),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
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
# SESSION MANAGEMENT (Redis-backed)
# =============================================================================

class SessionManager:
    """
    Redis-backed session management for serverless environments.
    
    This is the KEY to making auth work on Modal:
    - Sessions are stored in Upstash Redis (HTTP-based, no connection needed)
    - JWT tokens contain only session_id (not the full session)
    - Session data is fetched/updated on every request
    - Sliding expiration keeps active sessions alive
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
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            session_id = payload.get("session_id")
            user_id = payload.get("user_id")
            
            if session_id:
                redis.delete(f"session:{session_id}")
                
            if user_id:
                redis.srem(f"user_sessions:{user_id}", session_id)
                
            return True
        except JWTError:
            return False  # Token already invalid
    
    @staticmethod
    def destroy_all_user_sessions(user_id: str) -> int:
        """Logout all devices for a user"""
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


# =============================================================================
# OAUTH MANAGER (3-Legged Flow with Redis State)
# =============================================================================

# OAuth Provider Configurations
OAUTH_PROVIDERS = {
    "quickbooks": {
        "auth_url": "https://appcenter.intuit.com/connect/oauth2",
        "token_url": "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        "scope": "com.intuit.quickbooks.accounting",
    },
    "dropbox": {
        "auth_url": "https://www.dropbox.com/oauth2/authorize",
        "token_url": "https://api.dropbox.com/oauth2/token",
        "scope": "files.content.write files.content.read",
    },
    "google_drive": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/drive.file",
    },
    "eagleview": {
        "auth_url": "https://api.eagleview.com/oauth2/authorize",
        "token_url": "https://api.eagleview.com/oauth2/token",
        "scope": "reports.read orders.write",
    },
}


class OAuthManager:
    """
    Handle 3-legged OAuth for external integrations.
    
    The state token is stored in Redis to survive container restarts
    during the OAuth redirect flow.
    """
    
    @staticmethod
    def start_oauth_flow(
        user_id: str,
        agency_id: str,
        provider: str,
        redirect_uri: str,
    ) -> str:
        """
        Step 1: Generate secure state and return authorization URL.
        
        The state token is stored in Redis so it survives
        container restarts during the OAuth flow.
        """
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        
        # Generate cryptographically secure state token
        state = secrets.token_urlsafe(32)
        
        # Store state in Redis with metadata
        state_data = {
            "user_id": user_id,
            "agency_id": agency_id,
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        redis.hset(f"oauth_state:{state}", values=state_data)
        redis.expire(f"oauth_state:{state}", OAUTH_STATE_EXPIRATION)
        
        # Build authorization URL
        config = OAUTH_PROVIDERS[provider]
        client_id = os.environ.get(f"{provider.upper()}_CLIENT_ID", "")
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "state": state,
            "response_type": "code",
            "access_type": "offline",  # Get refresh token
        }
        
        # Provider-specific additions
        if provider == "google_drive":
            params["prompt"] = "consent"  # Force consent to get refresh token
        
        auth_url = f"{config['auth_url']}?{urlencode(params)}"
        return auth_url
    
    @staticmethod
    async def handle_callback(
        provider: str,
        state: str,
        code: str,
    ) -> dict:
        """
        Step 2: Handle OAuth callback.
        
        Validates state token from Redis, exchanges code for tokens.
        Returns tokens for storage.
        """
        # Validate state from Redis
        state_data = redis.hgetall(f"oauth_state:{state}")
        
        if not state_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OAuth state. Please try connecting again."
            )
        
        # Delete state immediately (one-time use prevents replay attacks)
        redis.delete(f"oauth_state:{state}")
        
        # Verify provider matches
        if state_data.get("provider") != provider:
            raise HTTPException(status_code=400, detail="Provider mismatch")
        
        # Exchange code for tokens
        import httpx
        
        config = OAUTH_PROVIDERS[provider]
        client_id = os.environ.get(f"{provider.upper()}_CLIENT_ID", "")
        client_secret = os.environ.get(f"{provider.upper()}_CLIENT_SECRET", "")
        
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": state_data.get("redirect_uri"),
            "client_id": client_id,
            "client_secret": client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Token exchange failed: {response.text}"
                )
            
            tokens = response.json()
        
        # Calculate expiration
        expires_at = None
        if "expires_in" in tokens:
            expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        
        return {
            "provider": provider,
            "agency_id": state_data.get("agency_id"),
            "user_id": state_data.get("user_id"),
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "scope": tokens.get("scope"),
        }
    
    @staticmethod
    async def refresh_tokens(provider: str, refresh_token: str) -> dict:
        """Refresh OAuth tokens using refresh token"""
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        
        import httpx
        
        config = OAUTH_PROVIDERS[provider]
        client_id = os.environ.get(f"{provider.upper()}_CLIENT_ID", "")
        client_secret = os.environ.get(f"{provider.upper()}_CLIENT_SECRET", "")
        
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Token refresh failed: {response.text}"
                )
            
            tokens = response.json()
        
        expires_at = None
        if "expires_in" in tokens:
            expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        
        return {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token", refresh_token),  # Some providers don't return new refresh
            "expires_at": expires_at.isoformat() if expires_at else None,
        }


# =============================================================================
# ENCRYPTION UTILITIES
# =============================================================================

def encrypt_token(plaintext: str) -> str:
    """Encrypt a token for database storage"""
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token from database storage"""
    return cipher.decrypt(ciphertext.encode()).decode()


def hash_api_key(api_key: str) -> str:
    """Create a secure hash of an API key"""
    return hashlib.sha256(api_key.encode()).hexdigest()


# =============================================================================
# RBAC (Role-Based Access Control)
# =============================================================================

def has_permission(role: Role, resource: str, action: str) -> bool:
    """Check if a role has a specific permission"""
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    # Check for wildcard permissions
    if "*:*" in permissions:
        return True
    if f"{resource}:*" in permissions:
        return True
    if f"{resource}:{action}" in permissions:
        return True
    
    return False


def require_permission(resource: str, action: str):
    """
    Decorator to require a specific permission for a route.
    
    Usage:
        @require_permission("projects", "write")
        async def create_project(current_user: CurrentUser = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by FastAPI)
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if not has_permission(current_user.role, resource, action):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {resource}:{action}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# FASTAPI DEPENDENCIES
# =============================================================================

async def get_current_user(request: Request) -> CurrentUser:
    """
    FastAPI dependency to extract and validate the current user.
    
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
            ...
    """
    # Get token from header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    session = SessionManager.validate_session(token)
    
    # Build current user with permissions
    permissions = ROLE_PERMISSIONS.get(session.role, [])
    
    # Extract session_id from token for reference
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    return CurrentUser(
        user_id=session.user_id,
        agency_id=session.agency_id,
        role=session.role,
        email=session.email,
        session_id=payload.get("session_id", ""),
        permissions=permissions,
    )


def require_agency_scope(func: Callable):
    """
    Decorator to ensure all database queries are scoped to user's agency.
    
    This is the MULTI-TENANCY enforcement layer.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Inject agency_id into kwargs for the handler to use
        kwargs["_agency_id"] = current_user.agency_id
        
        return await func(*args, **kwargs)
    return wrapper


# =============================================================================
# CIRCUIT BREAKER PATTERN
# =============================================================================

class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    fail_max: int = 5              # Failures before opening
    reset_timeout: int = 60         # Seconds before trying again
    success_threshold: int = 3      # Successes to close from half-open
    excluded_exceptions: tuple = field(default_factory=tuple)


class CircuitBreaker:
    """
    Redis-backed Circuit Breaker for external service calls.
    
    State is stored in Redis so it's shared across all containers.
    This prevents thundering herd when a service is down.
    
    Usage:
        claude_breaker = CircuitBreaker("claude_api")
        
        @claude_breaker
        async def call_claude(prompt: str):
            ...
    """
    
    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.key_prefix = f"circuit:{name}"
    
    def _get_state(self) -> dict:
        """Get circuit state from Redis"""
        state_data = redis.hgetall(self.key_prefix)
        
        if not state_data:
            return {
                "state": CircuitState.CLOSED.value,
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
            }
        
        return {
            "state": state_data.get("state", CircuitState.CLOSED.value),
            "failure_count": int(state_data.get("failure_count", 0)),
            "success_count": int(state_data.get("success_count", 0)),
            "last_failure_time": state_data.get("last_failure_time"),
        }
    
    def _set_state(self, state: CircuitState, failure_count: int = 0, success_count: int = 0):
        """Update circuit state in Redis"""
        data = {
            "state": state.value,
            "failure_count": str(failure_count),
            "success_count": str(success_count),
            "last_failure_time": datetime.utcnow().isoformat() if state == CircuitState.OPEN else "",
        }
        redis.hset(self.key_prefix, values=data)
        redis.expire(self.key_prefix, self.config.reset_timeout * 10)  # Keep state longer than timeout
    
    def _should_allow_request(self) -> bool:
        """Check if request should be allowed through"""
        state_data = self._get_state()
        state = CircuitState(state_data["state"])
        
        if state == CircuitState.CLOSED:
            return True
        
        if state == CircuitState.OPEN:
            # Check if timeout has passed
            last_failure = state_data.get("last_failure_time")
            if last_failure:
                last_failure_dt = datetime.fromisoformat(last_failure)
                if datetime.utcnow() - last_failure_dt > timedelta(seconds=self.config.reset_timeout):
                    # Transition to half-open
                    self._set_state(CircuitState.HALF_OPEN)
                    return True
            return False
        
        if state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self):
        """Record a successful call"""
        state_data = self._get_state()
        state = CircuitState(state_data["state"])
        
        if state == CircuitState.HALF_OPEN:
            success_count = state_data["success_count"] + 1
            if success_count >= self.config.success_threshold:
                # Transition to closed
                self._set_state(CircuitState.CLOSED)
            else:
                self._set_state(CircuitState.HALF_OPEN, success_count=success_count)
        else:
            # Reset failure count on success
            self._set_state(CircuitState.CLOSED)
    
    def _record_failure(self):
        """Record a failed call"""
        state_data = self._get_state()
        state = CircuitState(state_data["state"])
        
        if state == CircuitState.HALF_OPEN:
            # Go back to open
            self._set_state(CircuitState.OPEN)
        else:
            failure_count = state_data["failure_count"] + 1
            if failure_count >= self.config.fail_max:
                self._set_state(CircuitState.OPEN, failure_count=failure_count)
            else:
                self._set_state(CircuitState.CLOSED, failure_count=failure_count)
    
    def __call__(self, func: Callable):
        """Decorator to wrap a function with circuit breaker logic"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self._should_allow_request():
                raise CircuitBreakerOpen(
                    f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
                )
            
            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                # Check if exception should be excluded
                if isinstance(e, self.config.excluded_exceptions):
                    raise
                
                self._record_failure()
                raise
        
        return wrapper
    
    def get_status(self) -> dict:
        """Get current circuit breaker status (for monitoring)"""
        state_data = self._get_state()
        return {
            "name": self.name,
            "state": state_data["state"],
            "failure_count": state_data["failure_count"],
            "success_count": state_data["success_count"],
            "last_failure_time": state_data.get("last_failure_time"),
            "config": {
                "fail_max": self.config.fail_max,
                "reset_timeout": self.config.reset_timeout,
                "success_threshold": self.config.success_threshold,
            }
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# =============================================================================
# MULTI-PROVIDER LLM WITH FALLBACK
# =============================================================================

# Pre-configured circuit breakers for LLM providers
claude_breaker = CircuitBreaker("claude_api", CircuitBreakerConfig(fail_max=3, reset_timeout=60))
openai_breaker = CircuitBreaker("openai_api", CircuitBreakerConfig(fail_max=3, reset_timeout=60))
groq_breaker = CircuitBreaker("groq_api", CircuitBreakerConfig(fail_max=5, reset_timeout=30))


async def call_llm_with_fallback(
    prompt: str,
    system_prompt: str = "",
    providers: List[str] = None,
    max_tokens: int = 1000,
) -> dict:
    """
    Call LLM with automatic failover between providers.
    
    Order of fallback (customizable via providers param):
    1. Claude (primary)
    2. OpenAI GPT-4
    3. Groq (fastest, cheapest fallback)
    
    Returns:
        {
            "response": "...",
            "provider": "claude",
            "tokens": 150,
            "latency_ms": 1234,
        }
    """
    import time
    
    providers = providers or ["claude", "openai", "groq"]
    errors = []
    
    for provider in providers:
        start_time = time.time()
        
        try:
            if provider == "claude":
                result = await _call_claude(prompt, system_prompt, max_tokens)
            elif provider == "openai":
                result = await _call_openai(prompt, system_prompt, max_tokens)
            elif provider == "groq":
                result = await _call_groq(prompt, system_prompt, max_tokens)
            else:
                continue
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": result["response"],
                "provider": provider,
                "tokens": result.get("tokens", 0),
                "latency_ms": latency_ms,
            }
            
        except CircuitBreakerOpen as e:
            errors.append(f"{provider}: Circuit open")
            continue
        except Exception as e:
            errors.append(f"{provider}: {str(e)}")
            continue
    
    # All providers failed
    raise HTTPException(
        status_code=503,
        detail=f"All LLM providers failed: {'; '.join(errors)}"
    )


@claude_breaker
async def _call_claude(prompt: str, system_prompt: str, max_tokens: int) -> dict:
    """Call Claude API (protected by circuit breaker)"""
    import anthropic
    
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    messages = [{"role": "user", "content": prompt}]
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    
    return {
        "response": response.content[0].text,
        "tokens": response.usage.input_tokens + response.usage.output_tokens,
    }


@openai_breaker
async def _call_openai(prompt: str, system_prompt: str, max_tokens: int) -> dict:
    """Call OpenAI API (protected by circuit breaker)"""
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=max_tokens,
        messages=messages,
    )
    
    return {
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
    }


@groq_breaker
async def _call_groq(prompt: str, system_prompt: str, max_tokens: int) -> dict:
    """Call Groq API (protected by circuit breaker)"""
    from groq import AsyncGroq
    
    client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=messages,
        temperature=0.2,
    )
    
    return {
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
    }


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Redis-backed rate limiter using sliding window algorithm.
    
    Usage:
        limiter = RateLimiter("api_calls", max_requests=100, window_seconds=60)
        
        if not await limiter.is_allowed(user_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    """
    
    def __init__(self, name: str, max_requests: int, window_seconds: int):
        self.name = name
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier (user_id, ip, etc.)"""
        key = f"ratelimit:{self.name}:{identifier}"
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds
        
        # Remove old entries
        redis.zremrangebyscore(key, "-inf", window_start)
        
        # Count current requests
        current_count = redis.zcard(key) or 0
        
        if current_count >= self.max_requests:
            return False
        
        # Add new request
        redis.zadd(key, {str(now): now})
        redis.expire(key, self.window_seconds)
        
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        key = f"ratelimit:{self.name}:{identifier}"
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds
        
        redis.zremrangebyscore(key, "-inf", window_start)
        current_count = redis.zcard(key) or 0
        
        return max(0, self.max_requests - current_count)


# Default rate limiters
api_rate_limiter = RateLimiter("api", max_requests=100, window_seconds=60)
ai_rate_limiter = RateLimiter("ai", max_requests=20, window_seconds=60)


# =============================================================================
# AUDIT LOGGING
# =============================================================================

def log_security_event(
    event_type: str,
    user_id: str = None,
    agency_id: str = None,
    ip_address: str = None,
    details: dict = None,
    severity: str = "info",
):
    """
    Log a security event to Redis (for Master Architect to analyze).
    
    Events are stored in a time-series structure for easy querying.
    """
    event = {
        "event_type": event_type,
        "user_id": user_id or "",
        "agency_id": agency_id or "",
        "ip_address": ip_address or "",
        "details": json.dumps(details or {}),
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Store in Redis stream for time-series queries
    redis.xadd("security_events", event, maxlen=10000)
    
    # Also increment counters for quick stats
    today = datetime.utcnow().strftime("%Y-%m-%d")
    redis.hincrby(f"security_stats:{today}", event_type, 1)
    redis.expire(f"security_stats:{today}", 86400 * 30)  # Keep 30 days


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Session Management
    "SessionManager",
    "SessionData",
    "CurrentUser",
    
    # OAuth
    "OAuthManager",
    "OAUTH_PROVIDERS",
    
    # RBAC
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "has_permission",
    "require_permission",
    
    # FastAPI Dependencies
    "get_current_user",
    "require_agency_scope",
    
    # Encryption
    "encrypt_token",
    "decrypt_token",
    "hash_api_key",
    
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpen",
    "CircuitState",
    
    # LLM with Fallback
    "call_llm_with_fallback",
    "claude_breaker",
    "openai_breaker",
    "groq_breaker",
    
    # Rate Limiting
    "RateLimiter",
    "api_rate_limiter",
    "ai_rate_limiter",
    
    # Audit
    "log_security_event",
]
