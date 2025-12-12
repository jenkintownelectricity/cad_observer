"""
ROOFIO Common Module
====================

Core functionality for the ROOFIO backend:
- config: Environment configuration
- session: Redis-backed session management
- security: RBAC, OAuth, encryption, circuit breakers
- database: PostgreSQL connection management
"""

from .config import (
    ENV,
    DEBUG,
    validate_config,
)

from .session import (
    get_redis,
    Role,
    SessionData,
    CurrentUser,
    SessionManager,
)

from .security import (
    # RBAC
    ROLE_PERMISSIONS,
    has_permission,
    require_permission,

    # FastAPI Dependencies
    get_current_user,
    require_agency_scope,

    # OAuth
    OAuthManager,
    OAUTH_PROVIDERS,

    # Encryption
    encrypt_token,
    decrypt_token,
    hash_api_key,

    # Circuit Breaker
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpen,
    CircuitState,
    claude_breaker,
    openai_breaker,
    groq_breaker,

    # LLM with Fallback
    call_llm_with_fallback,

    # Rate Limiting
    RateLimiter,
    api_rate_limiter,
    ai_rate_limiter,

    # Audit
    log_security_event,
)

from .database import (
    Base,
    get_engine,
    get_db_session,
    get_db,
    get_tenant_session,
    TenantScopedSession,
    check_database_health,
    init_database,
    close_database,
)

from .models import (
    Agency,
    User,
    Project,
    AuditLog,
    AIActionLog,
    PositionConfig,
)

__all__ = [
    # Config
    "ENV",
    "DEBUG",
    "validate_config",

    # Session
    "get_redis",
    "Role",
    "SessionData",
    "CurrentUser",
    "SessionManager",

    # RBAC
    "ROLE_PERMISSIONS",
    "has_permission",
    "require_permission",

    # FastAPI Dependencies
    "get_current_user",
    "require_agency_scope",

    # OAuth
    "OAuthManager",
    "OAUTH_PROVIDERS",

    # Encryption
    "encrypt_token",
    "decrypt_token",
    "hash_api_key",

    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpen",
    "CircuitState",
    "claude_breaker",
    "openai_breaker",
    "groq_breaker",

    # LLM with Fallback
    "call_llm_with_fallback",

    # Rate Limiting
    "RateLimiter",
    "api_rate_limiter",
    "ai_rate_limiter",

    # Audit
    "log_security_event",

    # Database
    "Base",
    "get_engine",
    "get_db_session",
    "get_db",
    "get_tenant_session",
    "TenantScopedSession",
    "check_database_health",
    "init_database",
    "close_database",

    # Models
    "Agency",
    "User",
    "Project",
    "AuditLog",
    "AIActionLog",
    "PositionConfig",
]
