"""
Add Form Tables Migration
=========================

Creates the form_templates and form_submissions tables.
Run this after the initial database is set up.

Usage:
    python add_form_tables.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def add_form_tables():
    """Create form_templates and form_submissions tables"""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False

    # Convert to async URL if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        # Create form_templates table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS form_templates (
                template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agency_id UUID NOT NULL REFERENCES agencies(agency_id),

                -- Template info
                name VARCHAR(255) NOT NULL,
                form_type VARCHAR(100) NOT NULL,
                description TEXT,

                -- Format preference
                is_custom BOOLEAN DEFAULT TRUE,
                is_default BOOLEAN DEFAULT FALSE,

                -- Source document
                source_file_url VARCHAR(500),
                source_file_type VARCHAR(50),

                -- Extracted/defined fields
                fields JSONB DEFAULT '[]'::jsonb,

                -- Layout info
                layout JSONB,

                -- ROOFIO additions
                roofio_additions JSONB DEFAULT '{"logo": true, "timestamp": true, "gps": true}'::jsonb,

                -- Preview
                preview_url VARCHAR(500),

                -- Stats
                times_used INTEGER DEFAULT 0,

                -- Status
                status VARCHAR(50) DEFAULT 'active',

                -- Created by
                created_by UUID REFERENCES users(user_id),

                -- Timestamps
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """))
        print("Created form_templates table")

        # Create indexes for form_templates
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_template_agency ON form_templates(agency_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_template_type ON form_templates(form_type);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_template_default ON form_templates(agency_id, form_type, is_default);
        """))
        print("Created form_templates indexes")

        # Create form_submissions table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS form_submissions (
                submission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agency_id UUID NOT NULL REFERENCES agencies(agency_id),
                project_id UUID REFERENCES projects(project_id),
                template_id UUID REFERENCES form_templates(template_id),

                -- Form type
                form_type VARCHAR(100) NOT NULL,

                -- Filled data
                data JSONB NOT NULL,

                -- Attachments
                attachments JSONB DEFAULT '[]'::jsonb,

                -- Signature
                signature_url VARCHAR(500),
                signed_by VARCHAR(255),
                signed_at TIMESTAMPTZ,

                -- GPS & metadata
                gps_latitude NUMERIC(10, 8),
                gps_longitude NUMERIC(11, 8),
                device_info JSONB,

                -- Status
                status VARCHAR(50) DEFAULT 'draft',

                -- Submitted by
                submitted_by UUID REFERENCES users(user_id),

                -- Timestamps
                created_at TIMESTAMPTZ DEFAULT NOW(),
                submitted_at TIMESTAMPTZ
            );
        """))
        print("Created form_submissions table")

        # Create indexes for form_submissions
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_sub_agency ON form_submissions(agency_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_sub_project ON form_submissions(project_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_form_sub_type ON form_submissions(form_type);
        """))
        print("Created form_submissions indexes")

    await engine.dispose()
    print("\n✅ Form tables created successfully!")
    return True


if __name__ == "__main__":
    asyncio.run(add_form_tables())
