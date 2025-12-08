# ROOFIO Backend Master Plan - Next Session Implementation Guide

**Created:** December 2025
**Purpose:** Implementation roadmap for the tiered intelligence architecture on Modal
**Status:** Ready for Phase 1 Implementation

---

## QUICK START FOR NEXT SESSION

Tell Claude: *"Let's implement Phase 1 of the Backend Master Plan - start with security.py foundation"*

---

## THE ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE COST-PERFORMANCE PYRAMID                     │
├─────────────────────────────────────────────────────────────────────┤
│                         ▲ Claude/GPT (Tier 3)                       │
│                        ╱ ╲ $15-75/1M tokens                         │
│                       ╱ 1%╲ Complex reasoning                       │
│                      ╱─────╲                                        │
│                     ╱ Groq  ╲ $0.64/1M tokens (Tier 2)              │
│                    ╱   4%    ╲ 300+ tok/sec                         │
│                   ╱───────────╲                                     │
│                  ╱  Python     ╲ ~$0.00 (Tier 1)                    │
│                 ╱     95%       ╲ CRUD, retrieval, logic            │
│                ╱─────────────────╲                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: FOUNDATION (Priority: CRITICAL)

### Files to Create

```
/roofio-backend/
├── /common/
│   ├── __init__.py
│   ├── security.py          # JWT, OAuth, RBAC, encryption
│   ├── session.py           # Redis-backed sessions (Upstash)
│   ├── database.py          # SQLAlchemy + Neon/Supabase
│   └── config.py            # Environment configuration
```

### security.py - The Foundation

```python
"""
Security Foundation for ROOFIO
- Redis-backed sessions (survives serverless spin-down)
- JWT token handling
- 3-legged OAuth flow
- RBAC permission system
- Encryption for stored tokens
"""

from upstash_redis import Redis
from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import uuid
from datetime import datetime, timedelta
import os

# Initialize Upstash Redis (HTTP-based, serverless-friendly)
redis = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
)

# Configuration
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token encryption for OAuth tokens
fernet = Fernet(ENCRYPTION_KEY)


class SessionManager:
    """Redis-backed session management for serverless"""

    @staticmethod
    async def create_session(user_id: str, agency_id: str, role: str) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "agency_id": agency_id,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
        }
        redis.hset(f"session:{session_id}", values=session_data)
        redis.expire(f"session:{session_id}", SESSION_TIMEOUT_SECONDS)

        token = jwt.encode(
            {"session_id": session_id, "exp": datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT_SECONDS)},
            JWT_SECRET, algorithm=JWT_ALGORITHM
        )
        return token

    @staticmethod
    async def validate_session(token: str) -> dict:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            session_id = payload.get("session_id")
            session_data = redis.hgetall(f"session:{session_id}")
            if not session_data:
                raise HTTPException(status_code=401, detail="Session expired")
            redis.expire(f"session:{session_id}", SESSION_TIMEOUT_SECONDS)
            return session_data
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


class RBAC:
    """Role-Based Access Control"""

    PERMISSIONS = {
        "super_admin": ["*"],
        "agency_admin": ["projects:*", "users:*", "forms:*", "integrations:*", "ai:*"],
        "project_manager": ["projects:read", "projects:write", "daily_logs:*", "forms:*", "ai:basic"],
        "foreman": ["projects:read", "daily_logs:write", "forms:submit", "photos:upload"],
        "apprentice": ["projects:read", "daily_logs:read", "forms:read"],
    }

    @staticmethod
    def check_permission(role: str, permission: str) -> bool:
        user_perms = RBAC.PERMISSIONS.get(role, [])
        if "*" in user_perms:
            return True
        if permission in user_perms:
            return True
        resource = permission.split(":")[0]
        if f"{resource}:*" in user_perms:
            return True
        return False


class OAuthManager:
    """3-Legged OAuth for external integrations"""

    STATE_EXPIRATION = 600  # 10 minutes

    @staticmethod
    async def start_oauth_flow(user_id: str, agency_id: str, provider: str) -> str:
        import secrets
        state = secrets.token_urlsafe(32)
        redis.hset(f"oauth_state:{state}", values={
            "user_id": user_id,
            "agency_id": agency_id,
            "provider": provider,
        })
        redis.expire(f"oauth_state:{state}", OAuthManager.STATE_EXPIRATION)
        return OAuthManager._get_auth_url(provider, state)

    @staticmethod
    async def handle_callback(state: str, code: str) -> dict:
        state_data = redis.hgetall(f"oauth_state:{state}")
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        redis.delete(f"oauth_state:{state}")
        # Exchange code for tokens, encrypt, store in DB
        return {"success": True, "provider": state_data.get("provider")}


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return fernet.decrypt(encrypted.encode()).decode()
```

---

## PHASE 2: TIER 1 PYTHON LAYER

### Files to Create

```
/roofio-backend/
├── /modules/
│   ├── /upo/               # User & Project Organization
│   │   ├── routes.py
│   │   └── services.py
│   ├── /foreman/           # Digital Foreman
│   │   ├── routes.py
│   │   └── risk_shield.py
│   ├── /control/           # Control Center
│   │   └── routes.py
│   └── /integrations/      # 28+ connectors
│       ├── routes.py
│       └── oauth.py
```

---

## PHASE 3: TIER 2 GROQ + RAG

### Key Implementation

```python
from groq import Groq
from upstash_vector import Index

class GroqWithRAG:
    def __init__(self):
        self.groq = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.vector = Index(
            url=os.environ["UPSTASH_VECTOR_REST_URL"],
            token=os.environ["UPSTASH_VECTOR_REST_TOKEN"]
        )

    async def process(self, query: str, task_type: str) -> dict:
        # 1. Query Skills Docs for context
        relevant_docs = self.vector.query(data=query, top_k=3)

        # 2. Build prompt with knowledge
        context = "\n".join([doc.data for doc in relevant_docs])

        # 3. Call Groq
        response = self.groq.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": f"Context:\n{context}"},
                {"role": "user", "content": query}
            ]
        )
        return {"response": response.choices[0].message.content}
```

---

## PHASE 4: TIER 3 ADVANCED LLM

### Multi-Provider with Failover

```python
class AdvancedLLM:
    providers = ["claude", "gpt4", "gemini"]

    async def think_deep(self, prompt: str) -> dict:
        for provider in self.providers:
            if self._check_circuit(provider):
                try:
                    return await self._call_provider(provider, prompt)
                except Exception:
                    self._record_failure(provider)
        raise Exception("All providers failed")
```

---

## PHASE 5: MASTER ARCHITECT

### Knowledge Updater (NOT Code Modifier)

```python
class MasterArchitect:
    """
    DOES NOT modify code. ONLY updates knowledge in Vector DB.
    """

    async def learn_from_failures(self):
        failures = await self._get_recent_failures()
        for failure in failures:
            if self._is_knowledge_gap(failure):
                await self.vector.upsert([
                    (str(uuid.uuid4()), failure["fix"], {"category": "error_fix"})
                ])
            else:
                await self._alert_humans(failure)
```

---

## REQUIRED EXTERNAL SERVICES

| Service | Purpose | Setup |
|---------|---------|-------|
| **Modal** | Serverless compute | modal.com |
| **Upstash Redis** | Sessions, state | upstash.com |
| **Upstash Vector** | Skills Docs RAG | upstash.com |
| **Neon/Supabase** | PostgreSQL | neon.tech or supabase.com |
| **Groq** | Fast AI (Tier 2) | groq.com |
| **Anthropic** | Claude (Tier 3) | anthropic.com |

---

## ENVIRONMENT VARIABLES NEEDED

```bash
# Modal
MODAL_TOKEN_ID=...
MODAL_TOKEN_SECRET=...

# Upstash
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
UPSTASH_VECTOR_REST_URL=...
UPSTASH_VECTOR_REST_TOKEN=...

# Database
DATABASE_URL=postgresql://...

# AI Providers
GROQ_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Security
JWT_SECRET=...
ENCRYPTION_KEY=...

# OAuth (per provider)
QUICKBOOKS_CLIENT_ID=...
QUICKBOOKS_CLIENT_SECRET=...
DROPBOX_CLIENT_ID=...
# etc.
```

---

## DIRECTORY STRUCTURE (Final)

```
/roofio-backend/
├── /common/                    # Shared utilities
│   ├── security.py
│   ├── session.py
│   ├── database.py
│   └── config.py
├── /models/                    # SQLAlchemy models
├── /modules/                   # Business logic
│   ├── /upo/
│   ├── /foreman/
│   ├── /control/
│   └── /integrations/
├── /brain/                     # AI Tiers
│   ├── tier1_python.py
│   ├── tier2_groq.py
│   ├── tier3_advanced.py
│   └── knowledge.py
├── /architect/                 # Master Architect
├── /skills_docs/               # Seed knowledge
├── app.py
├── modal_gateway.py
├── modal_tier1.py
├── modal_tier2.py
├── modal_tier3.py
└── modal_architect.py
```

---

## IMPLEMENTATION ORDER

1. **security.py** - Sessions, JWT, OAuth, RBAC
2. **database.py** - PostgreSQL connection
3. **modal_gateway.py** - API Gateway
4. **modal_tier1.py** - Python functions
5. **Seed Skills Docs** - Load knowledge into Vector DB
6. **modal_tier2.py** - Groq + RAG
7. **modal_tier3.py** - Claude/GPT
8. **modal_architect.py** - Self-healing

---

## COST ESTIMATE (Monthly)

| Component | Cost |
|-----------|------|
| Modal | $50-100 |
| Neon/Supabase | $25 |
| Upstash Redis | $10 |
| Upstash Vector | $20 |
| Groq | $20-50 |
| Claude/GPT | $50-100 |
| **Total** | **$175-305** |

---

## NEXT SESSION PROMPT

```
"I want to implement Phase 1 of the Backend Master Plan.
Start with security.py - I need:
1. Redis-backed session management (Upstash)
2. JWT token handling
3. RBAC permission system
4. 3-legged OAuth flow for integrations
5. Token encryption utilities

Reference: NEXT-SESSION-BACKEND-MASTERPLAN.md"
```
