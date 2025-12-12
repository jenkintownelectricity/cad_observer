"""
ROOFIO Modal Deployment Configuration
======================================

This file defines all Modal services:
- Gateway (FastAPI API)
- Tier 1 Python (CRUD operations)
- Tier 2 Groq (Fast AI with RAG)
- Tier 3 Advanced (Claude/GPT with fallback)
- Master Architect (Scheduled watchdog)
- Workers (Background jobs)

Deploy with:
    modal deploy modal_app.py

Dev mode with hot reload:
    modal serve modal_app.py
"""

import os
import modal
from datetime import datetime

# =============================================================================
# MODAL APP & IMAGE CONFIGURATION
# =============================================================================

# Define the container image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    # Core web framework
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "pydantic>=2.5.0",
    
    # Redis (Upstash HTTP-based)
    "upstash-redis>=1.0.0",
    
    # Vector DB (Upstash)
    "upstash-vector>=0.5.0",
    
    # JWT & Security
    "python-jose[cryptography]>=3.3.0",
    "cryptography>=41.0.0",
    "passlib[bcrypt]>=1.7.0",
    
    # AI Providers
    "anthropic>=0.40.0",
    "openai>=1.12.0",
    "groq>=0.4.0",
    
    # Database
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "databases>=0.9.0",
    
    # HTTP Client
    "httpx>=0.26.0",
    
    # Utilities
    "python-multipart>=0.0.6",
    "python-dotenv>=1.0.0",
)

# Create the Modal app
app = modal.App(
    name="roofio-backend",
    image=image,
)

# =============================================================================
# SECRETS CONFIGURATION
# =============================================================================

# Define secret groups (create these in Modal dashboard or CLI)
# modal secret create roofio-database PGHOST=... PGPORT=5432 ...
# modal secret create roofio-upstash UPSTASH_REDIS_REST_URL=... UPSTASH_REDIS_REST_TOKEN=...
# modal secret create roofio-ai ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GROQ_API_KEY=...
# modal secret create roofio-auth JWT_SECRET=... ENCRYPTION_KEY=...

database_secret = modal.Secret.from_name("roofio-database")
upstash_secret = modal.Secret.from_name("roofio-upstash")
ai_secret = modal.Secret.from_name("roofio-ai")
auth_secret = modal.Secret.from_name("roofio-auth")

all_secrets = [database_secret, upstash_secret, ai_secret, auth_secret]

# =============================================================================
# VOLUMES
# =============================================================================

# Volume for Skills Docs (pre-built knowledge base)
skills_volume = modal.Volume.from_name("roofio-skills", create_if_missing=True)

# =============================================================================
# GATEWAY SERVICE (FastAPI)
# =============================================================================

@app.function(
    secrets=all_secrets,
    cpu=0.5,
    memory=512,
    container_idle_timeout=300,
    allow_concurrent_inputs=100,
)
@modal.asgi_app()
def gateway():
    """
    Main API Gateway
    
    Handles:
    - Authentication
    - Rate limiting
    - Request routing to appropriate tier
    - CORS and security headers
    """
    from fastapi import FastAPI, Request, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import time
    
    api = FastAPI(
        title="ROOFIO API",
        description="Construction Intelligence Platform",
        version="1.0.0",
    )
    
    # CORS
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["https://roofio.app", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import security module
    from common.security import (
        get_current_user,
        CurrentUser,
        api_rate_limiter,
        log_security_event,
    )
    
    # Request timing middleware
    @api.middleware("http")
    async def add_timing(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Health check
    @api.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "roofio-gateway",
        }
    
    # Auth endpoints
    @api.post("/api/v1/auth/login")
    async def login(request: Request):
        """Login endpoint - returns JWT token"""
        # This would validate credentials against database
        # For now, placeholder
        from common.security import SessionManager
        
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        # TODO: Validate against database
        # user = await validate_user(email, password)
        
        # For demo, create session
        # token = SessionManager.create_session(
        #     user_id=user.id,
        #     agency_id=user.agency_id,
        #     role=user.role,
        #     email=user.email,
        # )
        
        return {"message": "Login endpoint - implement with database"}
    
    @api.post("/api/v1/auth/logout")
    async def logout(request: Request):
        """Logout endpoint"""
        from common.security import SessionManager
        
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            SessionManager.destroy_session(token)
        
        return {"message": "Logged out"}
    
    # Protected route example
    @api.get("/api/v1/me")
    async def get_me(current_user: CurrentUser = Depends(get_current_user)):
        return {
            "user_id": current_user.user_id,
            "agency_id": current_user.agency_id,
            "role": current_user.role.value,
            "email": current_user.email,
            "permissions": current_user.permissions,
        }
    
    # Tier routing would happen here...
    # /api/v1/projects/* -> Tier 1
    # /api/v1/ai/summarize -> Tier 2
    # /api/v1/ai/analyze -> Tier 3
    
    return api


# =============================================================================
# TIER 1: PYTHON CRUD LAYER
# =============================================================================

@app.cls(
    secrets=all_secrets,
    cpu=0.5,
    memory=512,
    container_idle_timeout=300,
    allow_concurrent_inputs=100,
)
class Tier1Python:
    """
    Pure Python operations - CRUD, business logic, integrations.
    
    Cost: Near zero (just compute)
    Latency: <50ms
    """
    
    def __enter__(self):
        """Initialize database connection"""
        # In production, initialize SQLAlchemy/databases connection
        pass
    
    @modal.method()
    async def get_projects(self, agency_id: str, limit: int = 100) -> list:
        """Get projects for an agency"""
        # TODO: Implement with database
        return [{"id": "demo", "name": "Demo Project", "agency_id": agency_id}]
    
    @modal.method()
    async def create_daily_log(self, agency_id: str, data: dict) -> dict:
        """Create a daily log entry"""
        # TODO: Implement with database
        return {"id": "new-log", "status": "created", **data}
    
    @modal.method()
    async def validate_submittal(self, data: dict) -> dict:
        """Validate submittal data against specs"""
        # Pure Python validation logic
        errors = []
        
        if not data.get("spec_section"):
            errors.append("Spec section required")
        if not data.get("product_data"):
            errors.append("Product data required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }


# =============================================================================
# TIER 2: GROQ FAST AI
# =============================================================================

@app.cls(
    secrets=all_secrets,
    cpu=0.5,
    memory=512,
    container_idle_timeout=600,
    allow_concurrent_inputs=20,
    volumes={"/skills": skills_volume},
)
class Tier2Groq:
    """
    Fast AI with RAG from Skills Docs.
    
    Cost: ~$0.001 per request
    Latency: <500ms
    """
    
    def __enter__(self):
        """Initialize Groq client and knowledge base"""
        from brain.knowledge import GroqWithRAG
        self.ai = GroqWithRAG()
    
    @modal.method()
    async def summarize(self, text: str, max_length: int = 200) -> dict:
        """Summarize text"""
        return await self.ai.process(
            user_input=f"Summarize this in {max_length} words or less:\n\n{text}",
            task_type="summarize",
            system_prompt="You are a construction document summarizer. Be precise and technical.",
        )
    
    @modal.method()
    async def classify(self, text: str, categories: list) -> dict:
        """Classify text into categories"""
        return await self.ai.process(
            user_input=f"Classify this text into one of these categories: {categories}\n\nText: {text}",
            task_type="classify",
            system_prompt="Respond with just the category name, nothing else.",
        )
    
    @modal.method()
    async def extract_entities(self, text: str, entity_types: list) -> dict:
        """Extract entities from text"""
        return await self.ai.process(
            user_input=f"Extract these entities from the text: {entity_types}\n\nText: {text}\n\nRespond with JSON.",
            task_type="extract",
            system_prompt="Extract entities and return valid JSON only.",
        )
    
    @modal.method()
    async def answer_from_knowledge(self, question: str) -> dict:
        """Answer a question using Skills Docs"""
        return await self.ai.process(
            user_input=question,
            task_type="answer",
            system_prompt="Answer based on the knowledge provided. If the knowledge doesn't contain the answer, say so.",
        )


# =============================================================================
# TIER 3: ADVANCED LLM
# =============================================================================

@app.cls(
    secrets=all_secrets,
    cpu=1,
    memory=2048,
    container_idle_timeout=300,
    timeout=300,
    allow_concurrent_inputs=10,
)
class Tier3Advanced:
    """
    Complex reasoning with multi-provider failover.
    
    Cost: ~$0.05 per request
    Latency: 5-30 seconds
    """
    
    def __enter__(self):
        """Initialize providers"""
        from common.security import call_llm_with_fallback
        self.call_llm = call_llm_with_fallback
    
    @modal.method()
    async def analyze_project_risks(self, project_data: dict) -> dict:
        """Deep analysis of project risks"""
        
        prompt = f"""Analyze this roofing/waterproofing project for risks:

Project Data:
{project_data}

Provide:
1. Weather-related risks
2. Safety concerns (OSHA compliance)
3. Material compatibility issues
4. Schedule risks
5. Cost exposure areas

Be specific to commercial roofing/waterproofing."""

        result = await self.call_llm(
            prompt=prompt,
            system_prompt="You are an expert construction risk analyst specializing in Division 07 (roofing, waterproofing, flashing).",
            max_tokens=2000,
        )
        
        return result
    
    @modal.method()
    async def generate_schedule(self, project_data: dict, constraints: dict) -> dict:
        """Generate construction schedule"""
        
        prompt = f"""Create a construction schedule for this project:

Project: {project_data}
Constraints: {constraints}

Include:
1. Phase breakdown
2. Critical path items
3. Weather contingencies
4. Inspection points

Format as a structured schedule with dates."""

        return await self.call_llm(
            prompt=prompt,
            system_prompt="You are a construction scheduler. Be realistic with durations.",
            max_tokens=3000,
        )
    
    @modal.method()
    async def complex_document_analysis(self, document_text: str, questions: list) -> dict:
        """Analyze complex documents (specs, contracts, etc.)"""
        
        prompt = f"""Analyze this document and answer the questions:

Document:
{document_text[:10000]}  # Limit for context window

Questions:
{questions}

Provide detailed answers with citations to specific sections."""

        return await self.call_llm(
            prompt=prompt,
            system_prompt="You are a construction document analyst. Be thorough and cite specific sections.",
            max_tokens=4000,
        )


# =============================================================================
# MASTER ARCHITECT (Scheduled Watchdog)
# =============================================================================

@app.cls(
    secrets=all_secrets,
    cpu=1,
    memory=2048,
    timeout=600,
)
class MasterArchitectService:
    """
    The watchdog that learns and teaches.
    Modifies knowledge, not code.
    """
    
    def __enter__(self):
        from architect.master import MasterArchitect
        self.architect = MasterArchitect()
    
    @modal.method()
    async def analyze_and_learn(self, hours: int = 1):
        """Main learning cycle"""
        return await self.architect.analyze_and_learn(hours)
    
    @modal.method()
    async def security_audit(self):
        """Security scan"""
        return await self.architect.security_audit()
    
    @modal.method()
    async def generate_training_data(self, hours: int = 6):
        """Generate fine-tuning examples"""
        return await self.architect.generate_training_data(hours)
    
    @modal.method()
    async def comprehensive_analysis(self):
        """Daily deep analysis"""
        return await self.architect.comprehensive_analysis()
    
    @modal.method()
    async def get_dashboard(self):
        """Get monitoring dashboard data"""
        return await self.architect.get_dashboard_data()


# =============================================================================
# SCHEDULED FUNCTIONS
# =============================================================================

@app.function(
    secrets=all_secrets,
    schedule=modal.Period(minutes=15),
    timeout=300,
)
async def scheduled_security_audit():
    """Run security audit every 15 minutes"""
    service = MasterArchitectService()
    return await service.security_audit.remote()


@app.function(
    secrets=all_secrets,
    schedule=modal.Period(hours=1),
    timeout=600,
)
async def scheduled_hourly_analysis():
    """Run analysis every hour"""
    service = MasterArchitectService()
    return await service.analyze_and_learn.remote(hours=1)


@app.function(
    secrets=all_secrets,
    schedule=modal.Period(hours=6),
    timeout=900,
)
async def scheduled_training_generation():
    """Generate training data every 6 hours"""
    service = MasterArchitectService()
    return await service.generate_training_data.remote(hours=6)


@app.function(
    secrets=all_secrets,
    schedule=modal.Cron("0 3 * * *"),  # Daily at 3 AM UTC
    timeout=1800,
)
async def scheduled_daily_analysis():
    """Deep analysis daily at 3 AM UTC"""
    service = MasterArchitectService()
    return await service.comprehensive_analysis.remote()


# =============================================================================
# BACKGROUND WORKERS
# =============================================================================

@app.cls(
    secrets=all_secrets,
    cpu=0.5,
    memory=1024,
    container_idle_timeout=300,
)
class BackgroundWorker:
    """
    Background job processing using Redis Streams.
    """
    
    @modal.method()
    async def process_pdf(self, file_url: str, options: dict) -> dict:
        """Process PDF document"""
        # TODO: Implement PDF processing
        return {"status": "processed", "url": file_url}
    
    @modal.method()
    async def send_notification(self, notification_type: str, data: dict) -> dict:
        """Send email/SMS notification"""
        # TODO: Implement notifications
        return {"status": "sent", "type": notification_type}
    
    @modal.method()
    async def sync_integration(self, provider: str, agency_id: str) -> dict:
        """Sync data with external integration"""
        # TODO: Implement integration sync
        return {"status": "synced", "provider": provider}


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

@app.local_entrypoint()
def main():
    """Local testing entrypoint"""
    print("ROOFIO Backend - Modal Deployment")
    print("=" * 40)
    print()
    print("Deploy with: modal deploy modal_app.py")
    print("Dev mode:    modal serve modal_app.py")
    print()
    print("Services:")
    print("  - Gateway (FastAPI)")
    print("  - Tier 1 Python (CRUD)")
    print("  - Tier 2 Groq (Fast AI)")
    print("  - Tier 3 Advanced (Claude/GPT)")
    print("  - Master Architect (Watchdog)")
    print("  - Background Workers")
    print()
    print("Scheduled Jobs:")
    print("  - Security audit: Every 15 min")
    print("  - Hourly analysis: Every hour")
    print("  - Training generation: Every 6 hours")
    print("  - Daily analysis: 3 AM UTC")


# =============================================================================
# EXPORTS
# =============================================================================

# Make services available for remote calls
tier1 = Tier1Python()
tier2 = Tier2Groq()
tier3 = Tier3Advanced()
architect = MasterArchitectService()
worker = BackgroundWorker()
