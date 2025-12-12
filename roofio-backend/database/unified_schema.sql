-- ============================================================================
-- ROOFIO UNIFIED DATABASE SCHEMA
-- PostgreSQL + Supabase Architecture
-- Version: 2.0.0
--
-- NAMING CONVENTION: agency_id (standardized across all tables)
-- This is the authoritative schema - all models must match this
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- For fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gist";    -- For range queries

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Agencies (Roofing Companies using ROOFIO)
CREATE TABLE IF NOT EXISTS agencies (
    agency_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,

    -- Contact Info
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- Business Info
    license_number VARCHAR(100),
    insurance_info JSONB,

    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',  -- free, pro, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active',
    trial_ends_at TIMESTAMPTZ,

    -- Settings
    settings JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,

    -- Auth
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),

    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    avatar_url TEXT,

    -- Role & Permissions
    role VARCHAR(50) DEFAULT 'field_worker',  -- owner, admin, project_manager, field_worker
    permissions JSONB DEFAULT '[]',

    -- Auth Tokens (encrypted)
    oauth_provider VARCHAR(50),
    oauth_token_encrypted TEXT,
    refresh_token_encrypted TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PROJECT MANAGEMENT
-- ============================================================================

-- Clients (End customers of roofing companies)
CREATE TABLE IF NOT EXISTS clients (
    client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,

    -- Info
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),

    -- Notes
    notes TEXT,
    tags JSONB DEFAULT '[]',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(client_id),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_number VARCHAR(100),

    -- Location
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Status
    status VARCHAR(50) DEFAULT 'planning',  -- planning, active, on_hold, completed, cancelled
    priority VARCHAR(20) DEFAULT 'medium',

    -- Dates
    start_date DATE,
    end_date DATE,
    estimated_completion DATE,

    -- Financial
    estimated_value DECIMAL(12, 2),
    actual_value DECIMAL(12, 2),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id)
);

-- ============================================================================
-- DIGITAL FOREMAN (Forms & Inspections)
-- ============================================================================

-- Form Templates
CREATE TABLE IF NOT EXISTS form_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,

    -- Template Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),  -- inspection, checklist, report, safety

    -- Schema
    schema JSONB NOT NULL,  -- Form field definitions
    version INTEGER DEFAULT 1,

    -- Settings
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,  -- System templates can't be deleted

    -- Metadata
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

    -- Data
    data JSONB NOT NULL,  -- Submitted form data

    -- Status
    status VARCHAR(50) DEFAULT 'draft',  -- draft, submitted, approved, rejected

    -- Location (where form was filled)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Signatures
    signatures JSONB DEFAULT '[]',

    -- Metadata
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_by UUID REFERENCES users(user_id)
);

-- ============================================================================
-- AI & AUDIT LOGGING
-- ============================================================================

-- AI Action Log
CREATE TABLE IF NOT EXISTS ai_action_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id),

    -- Request
    tier INTEGER NOT NULL,  -- 1, 2, or 3
    endpoint VARCHAR(255),
    request_summary TEXT,

    -- Response
    response_summary TEXT,
    tokens_used INTEGER,
    latency_ms INTEGER,

    -- Escalation
    was_escalated BOOLEAN DEFAULT FALSE,
    escalated_to INTEGER,
    escalation_reason TEXT,

    -- Feedback
    user_rating INTEGER,  -- 1-5
    user_feedback TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID REFERENCES agencies(agency_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id),

    -- Action
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,

    -- Details
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_agency ON users(agency_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Projects
CREATE INDEX IF NOT EXISTS idx_projects_agency ON projects(agency_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_id);

-- Form Submissions
CREATE INDEX IF NOT EXISTS idx_submissions_template ON form_submissions(template_id);
CREATE INDEX IF NOT EXISTS idx_submissions_project ON form_submissions(project_id);
CREATE INDEX IF NOT EXISTS idx_submissions_agency ON form_submissions(agency_id);

-- AI Logs
CREATE INDEX IF NOT EXISTS idx_ai_logs_agency ON ai_action_logs(agency_id);
CREATE INDEX IF NOT EXISTS idx_ai_logs_created ON ai_action_logs(created_at);

-- Audit Logs
CREATE INDEX IF NOT EXISTS idx_audit_agency ON audit_logs(agency_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE agencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE form_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE form_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_action_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE agencies IS 'Roofing companies using ROOFIO platform';
COMMENT ON TABLE users IS 'Users belonging to agencies';
COMMENT ON TABLE clients IS 'End customers of roofing companies';
COMMENT ON TABLE projects IS 'Roofing projects';
COMMENT ON TABLE form_templates IS 'Digital Foreman form templates';
COMMENT ON TABLE form_submissions IS 'Submitted forms and inspections';
COMMENT ON TABLE ai_action_logs IS 'AI tier action logging for analytics';
COMMENT ON TABLE audit_logs IS 'General audit trail';
