-- ============================================================================
-- MIGRATION: Add missing columns to form_templates table
-- Run this in Supabase SQL Editor to update the table schema
-- ============================================================================

-- Add form_type column (replaces category for more specific typing)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS form_type VARCHAR(100);

-- Add is_custom flag (whether user-created or system template)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS is_custom BOOLEAN DEFAULT false;

-- Add status column (active, archived, draft)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- Add is_default flag (default template for a form type)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT false;

-- Add fields column (form field definitions - more descriptive than 'schema')
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS fields JSONB DEFAULT '[]'::jsonb;

-- Add roofio_additions column (ROOFIO-specific features: logo, GPS, etc.)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS roofio_additions JSONB DEFAULT '{}'::jsonb;

-- Add layout column (optional layout configuration)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS layout JSONB;

-- Add source_file columns (for scanned/uploaded templates)
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS source_file_url TEXT;

ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS source_file_type VARCHAR(50);

-- Add times_used counter
ALTER TABLE form_templates
ADD COLUMN IF NOT EXISTS times_used INTEGER DEFAULT 0;

-- Migrate existing data: copy category to form_type, schema to fields
UPDATE form_templates
SET form_type = category
WHERE form_type IS NULL AND category IS NOT NULL;

UPDATE form_templates
SET fields = schema
WHERE fields = '[]'::jsonb AND schema IS NOT NULL AND schema != '{}'::jsonb;

-- Set is_system templates as not custom
UPDATE form_templates
SET is_custom = NOT COALESCE(is_system, false);

-- Create index on form_type for faster lookups
CREATE INDEX IF NOT EXISTS idx_form_templates_type ON form_templates(form_type);
CREATE INDEX IF NOT EXISTS idx_form_templates_status ON form_templates(status);

-- ============================================================================
-- VERIFY THE CHANGES
-- ============================================================================
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'form_templates'
ORDER BY ordinal_position;
