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
# FORM TEMPLATE API
# =============================================================================

def list_form_types() -> Dict:
    """Get available form types"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/forms/types",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def list_form_templates(form_type: str = None, status: str = "active") -> Dict:
    """List form templates for the agency"""
    params = {"status": status}
    if form_type:
        params["form_type"] = form_type

    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/forms/templates",
            params=params,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def create_form_template(name: str, form_type: str, is_custom: bool = True, **kwargs) -> Dict:
    """Create a new form template"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/forms/templates",
            json={"name": name, "form_type": form_type, "is_custom": is_custom, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_form_template(template_id: str) -> Optional[Dict]:
    """Get a specific form template"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/forms/templates/{template_id}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return None
        raise APIError(response.text, response.status_code)


def update_form_template(template_id: str, **kwargs) -> Dict:
    """Update a form template"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.patch(
            f"{API_BASE_URL}/forms/templates/{template_id}",
            json=kwargs,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def set_default_template(template_id: str) -> Dict:
    """Set a template as default for its form type"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/forms/templates/{template_id}/set-default",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def get_form_preference(form_type: str) -> Dict:
    """Get user's preferred format for a form type"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/forms/preference/{form_type}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def submit_form(form_type: str, data: Dict, **kwargs) -> Dict:
    """Submit a filled form"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/forms/submissions",
            json={"form_type": form_type, "data": data, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


def list_form_submissions(form_type: str = None, project_id: str = None, limit: int = 50) -> Dict:
    """List form submissions"""
    params = {"limit": limit}
    if form_type:
        params["form_type"] = form_type
    if project_id:
        params["project_id"] = project_id

    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/forms/submissions",
            params=params,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


# =============================================================================
# DOCUMENT SCANNER API
# =============================================================================

def get_scan_formats() -> Dict:
    """Get available scan output formats"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.get(
            f"{API_BASE_URL}/scan/formats",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def process_scan(output_format: str = "pdf", enhance: bool = True, extract_text: bool = False, extract_fields: bool = False) -> Dict:
    """Process an uploaded scan"""
    params = {
        "output_format": output_format,
        "enhance": enhance,
        "extract_text": extract_text,
        "extract_fields": extract_fields
    }
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/scan/upload",
            params=params,
            headers=_get_headers()
        )
        if response.status_code == 200:
            return response.json()
        raise APIError(response.text, response.status_code)


def create_template_from_scan(scan_id: str, name: str, form_type: str, **kwargs) -> Dict:
    """Create a form template from a scanned document"""
    with httpx.Client(timeout=API_TIMEOUT) as client:
        response = client.post(
            f"{API_BASE_URL}/scan/create-template",
            json={"scan_id": scan_id, "name": name, "form_type": form_type, **kwargs},
            headers=_get_headers()
        )
        if response.status_code == 201:
            return response.json()
        raise APIError(response.text, response.status_code)


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

    # Form Templates
    "list_form_types",
    "list_form_templates",
    "create_form_template",
    "get_form_template",
    "update_form_template",
    "set_default_template",
    "get_form_preference",
    "submit_form",
    "list_form_submissions",

    # Document Scanner
    "get_scan_formats",
    "process_scan",
    "create_template_from_scan",
]
