"""
ROOFIO API Client
=================

HTTP client for Flask frontend to call the FastAPI backend.
Handles all communication with the ROOFIO Backend API.
"""

import os
import httpx
from typing import Optional, Dict, List, Any
from functools import lru_cache

# Configuration
API_BASE_URL = os.getenv("ROOFIO_API_URL", "http://localhost:8000")
API_TIMEOUT = 30.0

# Store the current agency ID (would come from session in production)
_current_agency_id: Optional[str] = None


def set_agency_id(agency_id: str):
    """Set the current agency ID for API calls"""
    global _current_agency_id
    _current_agency_id = agency_id


def get_agency_id() -> Optional[str]:
    """Get the current agency ID"""
    return _current_agency_id


def _get_headers() -> Dict[str, str]:
    """Get headers for API calls"""
    headers = {"Content-Type": "application/json"}
    if _current_agency_id:
        headers["X-Agency-Id"] = _current_agency_id
    return headers


class APIError(Exception):
    """API call error"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# =============================================================================
# AGENCY API
# =============================================================================

def create_agency(name: str, email: str = None, phone: str = None, **kwargs) -> Dict:
    """Create a new agency"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/agencies",
            json={"name": name, "email": email, "phone": phone, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_agency(agency_id: str) -> Optional[Dict]:
    """Get agency by ID"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/agencies/{agency_id}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return None
        raise APIError(response.text, response.status_code)


def update_agency(agency_id: str, **kwargs) -> Dict:
    """Update agency"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.patch(
            f"{API_BASE_URL}/agencies/{agency_id}",
            json=kwargs,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


# =============================================================================
# USER API
# =============================================================================

def create_user(email: str, name: str, password: str, role: str = "user", **kwargs) -> Dict:
    """Create a new user"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/users",
            json={"email": email, "name": name, "password": password, "role": role, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


def list_users(limit: int = 100, offset: int = 0) -> List[Dict]:
    """List all users for the agency"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/users",
            params={"limit": limit, "offset": offset},
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_user(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/users/{user_id}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return None
        raise APIError(response.text, response.status_code)


# =============================================================================
# PROJECT API
# =============================================================================

def create_project(name: str, address: Dict, **kwargs) -> Dict:
    """Create a new project"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/projects",
            json={"name": name, "address": address, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


def list_projects(status: str = None, limit: int = 100, offset: int = 0) -> Dict:
    """List projects for the agency"""
    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status

    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/projects",
            params=params,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_project(project_id: str) -> Optional[Dict]:
    """Get project by ID"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/projects/{project_id}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return None
        raise APIError(response.text, response.status_code)


def update_project(project_id: str, **kwargs) -> Dict:
    """Update project"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.patch(
            f"{API_BASE_URL}/projects/{project_id}",
            json=kwargs,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def delete_project(project_id: str) -> bool:
    """Delete project"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.delete(
            f"{API_BASE_URL}/projects/{project_id}",
            headers=_get_headers()
        )
        return response.status_code == 200


def search_projects(query: str, limit: int = 20) -> List[Dict]:
    """Search projects by name or number"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/projects/search",
            params={"q": query, "limit": limit},
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json().get("results", [])
        raise APIError(response.text, response.status_code)


# =============================================================================
# POSITION CONFIG API
# =============================================================================

def list_position_configs() -> List[Dict]:
    """Get all position configurations"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/positions",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_position_config(position: str) -> Dict:
    """Get configuration for a specific position"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/positions/{position}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def update_position_mode(position: str, mode: str) -> Dict:
    """Update position mode (off, assist, full_ai)"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.patch(
            f"{API_BASE_URL}/positions/{position}",
            json={"mode": mode},
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


# =============================================================================
# AI ACTIONS API
# =============================================================================

def list_pending_ai_actions(limit: int = 50) -> List[Dict]:
    """Get AI actions pending human review"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/ai/pending",
            params={"limit": limit},
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def review_ai_action(log_id: str, user_id: str, action: str, notes: str = None) -> Dict:
    """Review an AI action"""
    headers = _get_headers()
    headers["X-User-Id"] = user_id

    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/ai/{log_id}/review",
            json={"review_action": action, "review_notes": notes},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


# =============================================================================
# HEALTH API
# =============================================================================

def check_api_health() -> Dict:
    """Check if API is healthy"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                return response.json()
            return {"status": "unhealthy", "error": response.text}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


def is_api_available() -> bool:
    """Quick check if API is available"""
    health = check_api_health()
    return health.get("status") == "healthy"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def ensure_agency_exists(agency_id: str = None) -> str:
    """Ensure an agency exists, create default if needed"""
    global _current_agency_id

    if agency_id:
        agency = get_agency(agency_id)
        if agency:
            set_agency_id(agency_id)
            return agency_id

    # Check if we already have one set
    if _current_agency_id:
        return _current_agency_id

    # Create a default agency
    try:
        agency = create_agency(
            name="My Roofing Company",
            email="admin@company.com"
        )
        set_agency_id(agency["agency_id"])
        return agency["agency_id"]
    except APIError:
        return None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Config
    "set_agency_id",
    "get_agency_id",
    "API_BASE_URL",
    "APIError",

    # Agency
    "create_agency",
    "get_agency",
    "update_agency",

    # User
    "create_user",
    "list_users",
    "get_user",

    # Project
    "create_project",
    "list_projects",
    "get_project",
    "update_project",
    "delete_project",
    "search_projects",

    # Position Config
    "list_position_configs",
    "get_position_config",
    "update_position_mode",

    # AI Actions
    "list_pending_ai_actions",
    "review_ai_action",

    # Health
    "check_api_health",
    "is_api_available",

    # Convenience
    "ensure_agency_exists",
]
