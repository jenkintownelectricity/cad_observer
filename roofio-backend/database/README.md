# ROOFIO Database

## Unified Schema

The `unified_schema.sql` file is the **authoritative reference** for the ROOFIO database structure.

### Naming Conventions

| Convention | Standard | Notes |
|------------|----------|-------|
| Multi-tenant ID | `agency_id` | Previously: organization_id, company_id |
| Primary Keys | `{table}_id` | e.g., `user_id`, `project_id` |
| Foreign Keys | `{referenced_table}_id` | e.g., `agency_id` in users table |
| Timestamps | `created_at`, `updated_at` | All tables include these |

### Table Categories

1. **Core Tables**: `agencies`, `users`
2. **Project Management**: `projects`, `clients`
3. **Digital Foreman**: `form_templates`, `form_submissions`
4. **AI & Audit**: `ai_action_logs`, `audit_logs`

### Usage

```bash
# Apply schema to Supabase
psql $DATABASE_URL -f unified_schema.sql
```

### Migration from Old Schemas

If migrating from older schemas that used `organization_id` or `company_id`:

```sql
ALTER TABLE users RENAME COLUMN organization_id TO agency_id;
```
