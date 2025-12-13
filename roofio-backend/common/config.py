"""
ROOFIO Configuration Module
============================

Centralized configuration for all environment variables and constants.
All values come from environment variables with sensible defaults for development.

CRITICAL: Never commit actual secrets to code!
Use environment variables or Modal secrets in production.
"""

import os
from typing import Optional
from dataclasses import dataclass

# =============================================================================
# ENVIRONMENT
# =============================================================================

ENV = os.environ.get("ROOFIO_ENV", "development")
DEBUG = ENV == "development"

# =============================================================================
# UPSTASH REDIS CONFIGURATION
# =============================================================================

UPSTASH_REDIS_REST_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "")
UPSTASH_REDIS_REST_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")

# =============================================================================
# UPSTASH VECTOR CONFIGURATION
# =============================================================================

UPSTASH_VECTOR_REST_URL = os.environ.get("UPSTASH_VECTOR_REST_URL", "")
UPSTASH_VECTOR_REST_TOKEN = os.environ.get("UPSTASH_VECTOR_REST_TOKEN", "")

# =============================================================================
# DATABASE CONFIGURATION (PostgreSQL)
# =============================================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Individual components (fallback if DATABASE_URL not set)
# NO DEFAULTS for user/password/database - must be explicitly set
PGHOST = os.environ.get("PGHOST", "localhost")
PGPORT = int(os.environ.get("PGPORT", "5432"))
PGUSER = os.environ.get("PGUSER", "")
PGPASSWORD = os.environ.get("PGPASSWORD", "")
PGDATABASE = os.environ.get("PGDATABASE", "")

def get_database_url() -> str:
    """Build database URL from components if not directly provided"""
    if DATABASE_URL:
        return DATABASE_URL

    # Validate required components if using fallback
    if not PGUSER or not PGPASSWORD or not PGDATABASE:
        raise ValueError(
            "DATABASE_URL not set and missing required components. "
            "Either set DATABASE_URL or set PGUSER, PGPASSWORD, PGHOST, PGDATABASE in .env file."
        )

    return f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

# =============================================================================
# JWT / AUTH CONFIGURATION
# =============================================================================

JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION_32_BYTES")
JWT_ALGORITHM = "HS256"

# Session timing
SESSION_TIMEOUT_SECONDS = int(os.environ.get("SESSION_TIMEOUT_SECONDS", "3600"))  # 1 hour
SESSION_REFRESH_THRESHOLD = 300  # Refresh if <5 min remaining
OAUTH_STATE_EXPIRATION = 600  # 10 minutes for OAuth flow

# =============================================================================
# ENCRYPTION
# =============================================================================

# Generate this with: from cryptography.fernet import Fernet; Fernet.generate_key()
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")

# =============================================================================
# AI PROVIDER API KEYS
# =============================================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# =============================================================================
# AI MODEL CONFIGURATION
# =============================================================================

# Tier 2 - Fast AI (Groq)
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Tier 3 - Advanced (Claude)
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# Master Architect (most capable)
ARCHITECT_MODEL = os.environ.get("ARCHITECT_MODEL", "claude-sonnet-4-20250514")

# OpenAI (fallback)
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# =============================================================================
# RATE LIMITING DEFAULTS
# =============================================================================

API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))  # per minute
AI_RATE_LIMIT = int(os.environ.get("AI_RATE_LIMIT", "20"))  # per minute

# =============================================================================
# CIRCUIT BREAKER DEFAULTS
# =============================================================================

CIRCUIT_FAIL_MAX = int(os.environ.get("CIRCUIT_FAIL_MAX", "5"))
CIRCUIT_RESET_TIMEOUT = int(os.environ.get("CIRCUIT_RESET_TIMEOUT", "60"))
CIRCUIT_SUCCESS_THRESHOLD = int(os.environ.get("CIRCUIT_SUCCESS_THRESHOLD", "3"))

# =============================================================================
# OAUTH PROVIDER CONFIGURATION
# =============================================================================

# QuickBooks
QUICKBOOKS_CLIENT_ID = os.environ.get("QUICKBOOKS_CLIENT_ID", "")
QUICKBOOKS_CLIENT_SECRET = os.environ.get("QUICKBOOKS_CLIENT_SECRET", "")

# Dropbox
DROPBOX_CLIENT_ID = os.environ.get("DROPBOX_CLIENT_ID", "")
DROPBOX_CLIENT_SECRET = os.environ.get("DROPBOX_CLIENT_SECRET", "")

# Google Drive
GOOGLE_DRIVE_CLIENT_ID = os.environ.get("GOOGLE_DRIVE_CLIENT_ID", "")
GOOGLE_DRIVE_CLIENT_SECRET = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET", "")

# EagleView
EAGLEVIEW_CLIENT_ID = os.environ.get("EAGLEVIEW_CLIENT_ID", "")
EAGLEVIEW_CLIENT_SECRET = os.environ.get("EAGLEVIEW_CLIENT_SECRET", "")

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "https://roofio.app,http://localhost:3000,http://127.0.0.1:5000"
).split(",")

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = os.environ.get(
    "LOG_FORMAT",
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# =============================================================================
# VALIDATION HELPER
# =============================================================================

@dataclass
class ConfigValidation:
    """Validation results for configuration"""
    valid: bool
    missing: list
    warnings: list


def validate_config() -> ConfigValidation:
    """
    Validate that required configuration is present.
    Call this on startup to fail fast if misconfigured.
    """
    missing = []
    warnings = []

    # Critical - must have
    if not UPSTASH_REDIS_REST_URL:
        missing.append("UPSTASH_REDIS_REST_URL")
    if not UPSTASH_REDIS_REST_TOKEN:
        missing.append("UPSTASH_REDIS_REST_TOKEN")
    if JWT_SECRET == "CHANGE_ME_IN_PRODUCTION_32_BYTES" and not DEBUG:
        missing.append("JWT_SECRET (must be changed in production)")

    # Important - warn if missing
    if not DATABASE_URL and not PGPASSWORD:
        warnings.append("DATABASE_URL or PGPASSWORD not set - database operations will fail")
    if not ANTHROPIC_API_KEY:
        warnings.append("ANTHROPIC_API_KEY not set - Tier 3 AI will use fallback only")
    if not GROQ_API_KEY:
        warnings.append("GROQ_API_KEY not set - Tier 2 AI will not function")
    if not ENCRYPTION_KEY:
        warnings.append("ENCRYPTION_KEY not set - using auto-generated key (not persistent)")

    return ConfigValidation(
        valid=len(missing) == 0,
        missing=missing,
        warnings=warnings,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Environment
    "ENV",
    "DEBUG",

    # Redis
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN",

    # Vector DB
    "UPSTASH_VECTOR_REST_URL",
    "UPSTASH_VECTOR_REST_TOKEN",

    # Database
    "DATABASE_URL",
    "get_database_url",
    "PGHOST",
    "PGPORT",
    "PGUSER",
    "PGPASSWORD",
    "PGDATABASE",

    # Auth
    "JWT_SECRET",
    "JWT_ALGORITHM",
    "SESSION_TIMEOUT_SECONDS",
    "SESSION_REFRESH_THRESHOLD",
    "OAUTH_STATE_EXPIRATION",
    "ENCRYPTION_KEY",

    # AI Keys
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GROQ_API_KEY",

    # AI Models
    "GROQ_MODEL",
    "CLAUDE_MODEL",
    "ARCHITECT_MODEL",
    "OPENAI_MODEL",

    # Rate Limiting
    "API_RATE_LIMIT",
    "AI_RATE_LIMIT",

    # Circuit Breaker
    "CIRCUIT_FAIL_MAX",
    "CIRCUIT_RESET_TIMEOUT",
    "CIRCUIT_SUCCESS_THRESHOLD",

    # OAuth
    "QUICKBOOKS_CLIENT_ID",
    "QUICKBOOKS_CLIENT_SECRET",
    "DROPBOX_CLIENT_ID",
    "DROPBOX_CLIENT_SECRET",
    "GOOGLE_DRIVE_CLIENT_ID",
    "GOOGLE_DRIVE_CLIENT_SECRET",
    "EAGLEVIEW_CLIENT_ID",
    "EAGLEVIEW_CLIENT_SECRET",

    # CORS
    "CORS_ORIGINS",

    # Logging
    "LOG_LEVEL",
    "LOG_FORMAT",

    # Validation
    "validate_config",
    "ConfigValidation",
]
