"""
ROOFIO Database Initialization
==============================

Creates all tables in Supabase PostgreSQL using the unified schema.

Usage:
    python init_db.py
"""

import asyncio
import os

# Load .env file BEFORE anything else
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")
else:
    print(f"WARNING: No .env file found at {env_path}")
    print("Make sure environment variables are set!")

import asyncpg

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")


async def init_database():
    """Create all tables using raw SQL"""
    print("=" * 50)
    print("ROOFIO Database Initialization")
    print("=" * 50)

    # Parse the DATABASE_URL to show host (hide password)
    if '@' in DATABASE_URL:
        host_part = DATABASE_URL.split('@')[1].split('/')[0]
        print(f"\nConnecting to: {host_part}...")

    # Connect using asyncpg directly
    conn = await asyncpg.connect(DATABASE_URL)

    print("Connected!")
    print("\nCreating tables...")

    # SQL for creating tables
    create_tables_sql = """
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Agencies (Roofing Companies using ROOFIO)
    CREATE TABLE IF NOT EXISTS agencies (
        agency_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255),
        phone VARCHAR(50),
        address TEXT,
        city VARCHAR(100),
        state VARCHAR(50),
        zip_code VARCHAR(20),
        country VARCHAR(100) DEFAULT 'USA',
        license_number VARCHAR(100),
        insurance_info JSONB,
        subscription_tier VARCHAR(50) DEFAULT 'free',
        subscription_status VARCHAR(50) DEFAULT 'active',
        trial_ends_at TIMESTAMPTZ,
        settings JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE
    );

    -- Users
    CREATE TABLE IF NOT EXISTS users (
        user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(50),
        avatar_url TEXT,
        role VARCHAR(50) DEFAULT 'field_worker',
        permissions JSONB DEFAULT '[]',
        oauth_provider VARCHAR(50),
        oauth_token_encrypted TEXT,
        refresh_token_encrypted TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        email_verified BOOLEAN DEFAULT FALSE,
        last_login TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Clients
    CREATE TABLE IF NOT EXISTS clients (
        client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        company_name VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(50),
        address TEXT,
        city VARCHAR(100),
        state VARCHAR(50),
        zip_code VARCHAR(20),
        notes TEXT,
        tags JSONB DEFAULT '[]',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Projects
    CREATE TABLE IF NOT EXISTS projects (
        project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        client_id UUID REFERENCES clients(client_id),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        project_number VARCHAR(100),
        address TEXT,
        city VARCHAR(100),
        state VARCHAR(50),
        zip_code VARCHAR(20),
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        status VARCHAR(50) DEFAULT 'planning',
        priority VARCHAR(20) DEFAULT 'medium',
        start_date DATE,
        end_date DATE,
        estimated_completion DATE,
        estimated_value DECIMAL(12, 2),
        actual_value DECIMAL(12, 2),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        created_by UUID REFERENCES users(user_id)
    );

    -- Form Templates (Digital Foreman)
    CREATE TABLE IF NOT EXISTS form_templates (
        template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        category VARCHAR(100),
        schema JSONB NOT NULL,
        version INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT TRUE,
        is_system BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        created_by UUID REFERENCES users(user_id)
    );

    -- Form Submissions
    CREATE TABLE IF NOT EXISTS form_submissions (
        submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        template_id UUID REFERENCES form_templates(template_id),
        project_id UUID REFERENCES projects(project_id),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        data JSONB NOT NULL,
        status VARCHAR(50) DEFAULT 'draft',
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        signatures JSONB DEFAULT '[]',
        submitted_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        submitted_by UUID REFERENCES users(user_id)
    );

    -- AI Action Logs
    CREATE TABLE IF NOT EXISTS ai_action_logs (
        log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        user_id UUID REFERENCES users(user_id),
        tier INTEGER NOT NULL,
        endpoint VARCHAR(255),
        request_summary TEXT,
        response_summary TEXT,
        tokens_used INTEGER,
        latency_ms INTEGER,
        was_escalated BOOLEAN DEFAULT FALSE,
        escalated_to INTEGER,
        escalation_reason TEXT,
        user_rating INTEGER,
        user_feedback TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Audit Logs
    CREATE TABLE IF NOT EXISTS audit_logs (
        audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        user_id UUID REFERENCES users(user_id),
        action VARCHAR(100) NOT NULL,
        resource_type VARCHAR(100),
        resource_id UUID,
        old_values JSONB,
        new_values JSONB,
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Position Config (for Digital Foreman)
    CREATE TABLE IF NOT EXISTS position_configs (
        config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        permissions JSONB DEFAULT '[]',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    # Execute the SQL
    await conn.execute(create_tables_sql)

    # Get list of tables
    tables = await conn.fetch("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)

    print("\nTables in database:")
    for table in tables:
        print(f"  ✓ {table['tablename']}")

    await conn.close()

    print("\n" + "=" * 50)
    print("SUCCESS! Database initialized.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(init_database())
