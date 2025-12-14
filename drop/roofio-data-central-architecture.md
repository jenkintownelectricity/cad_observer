# Roofio Data Central: Complete Architecture

## The Core Insight

**Documents ARE the data.**

Instead of 13 separate data entry points (one per AI role), you have ONE source of truth:
- **Parsed documents** that feed the entire system
- **Event-driven propagation** that instantly updates all roles
- **Version control** with AI-powered diff detection
- **Role-based views** showing relevant data per user

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DATA CENTRAL ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DOCUMENTS                    AI PARSER                   EVENT STREAM     │
│   (Source of Truth)            (Extraction)                (Propagation)    │
│                                                                              │
│   ┌─────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│   │ Contract    │         │                 │         │                 │  │
│   │ Scope       │────────▶│   AI Document   │────────▶│  Event Bus      │  │
│   │ Drawings    │         │   Parser        │         │  (Kafka/Redis)  │  │
│   │ Specs       │         │                 │         │                 │  │
│   │ Assembly    │         │  • OCR          │         │  • Doc_Uploaded │  │
│   │ Submittals  │         │  • NLP Extract  │         │  • Data_Parsed  │  │
│   └─────────────┘         │  • Schema Map   │         │  • SOV_Updated  │  │
│                           │  • Validation   │         │  • CO_Approved  │  │
│                           └─────────────────┘         └────────┬────────┘  │
│                                                                 │           │
│                                                                 ▼           │
│                         ┌───────────────────────────────────────────────┐  │
│                         │           INTEGRATED PROJECT DATABASE          │  │
│                         │                                               │  │
│                         │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │  │
│                         │  │ Project │ │  Scope  │ │  Crew   │        │  │
│                         │  │ Record  │ │ Record  │ │ Record  │        │  │
│                         │  └─────────┘ └─────────┘ └─────────┘        │  │
│                         │                                               │  │
│                         │  Contract Sum: $1,247,500                     │  │
│                         │  Total SF: 32,450                             │  │
│                         │  SOV Line Items: 12                           │  │
│                         │  Active COs: 2                                │  │
│                         │                                               │  │
│                         └───────────────────────────────────────────────┘  │
│                                          │                                  │
│                                          │ Role-Based Views                │
│                                          ▼                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        13 AI ROLE CONSUMERS                          │  │
│  │                                                                      │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │  │
│  │  │Estimator│ │  PM   │ │Detailer│ │ Super  │ │ Safety │ │Accounts│ │  │
│  │  │        │ │        │ │        │ │        │ │        │ │        │ │  │
│  │  │$1.24M  │ │ Rev 2  │ │32,450SF│ │  R-30  │ │ TPO    │ │  SOV   │ │  │
│  │  │Budget  │ │Changes │ │Details │ │ Spec   │ │ MSDS   │ │12 items│ │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │  │
│  │                                                                      │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │  │
│  │  │  QC    │ │Foreman │ │HR/Work │ │ Sales  │ │ Mktg   │ │Warranty│ │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │  │
│  │                                                                      │  │
│  │                            ┌────────┐                               │  │
│  │                            │ Owner  │                               │  │
│  │                            │Dashboard│                               │  │
│  │                            └────────┘                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Document Types & What They Feed

| Document Type | AI Extracts | Feeds These Roles |
|--------------|-------------|-------------------|
| **Contract / Scope of Work** | Contract sum, milestones, retainage %, exclusions | Estimator, PM, Accounts, Owner |
| **Architectural Drawings** | Square footage, penetrations, slopes, details | Estimator, Detailer, Super, QC |
| **Specifications (Div 07)** | Material specs, warranty reqs, installation methods | QC, Safety, Detailer, PM |
| **Assembly Letters** | Approved components, installation sequence, warranty conditions | PM (submittals), Super (install), QC (verify) |
| **Submittals** | Product data, approval status, substitutions | PM, Procurement, Detailer |
| **Change Orders** | Cost impact, scope changes, schedule impact | Estimator, PM, Accounts, Super |
| **Daily Logs** | Crew counts, weather, work performed | Super, Foreman, Safety, HR |
| **Pay Applications** | Billed amounts, stored materials, retainage | Accounts, PM, Owner |

---

## Event Types & Propagation

When a document is uploaded or changed, events propagate to all affected roles:

```typescript
// Event Types
interface RoofioEvent {
  type: EventType;
  timestamp: Date;
  documentId: string;
  projectId: string;
  userId: string;
  data: Record<string, any>;
  affectedRoles: RoleId[];
}

enum EventType {
  // Document Events
  DOCUMENT_UPLOADED = 'document.uploaded',
  DOCUMENT_PARSED = 'document.parsed',
  DOCUMENT_VERSION_CHANGED = 'document.version_changed',
  DOCUMENT_MISSING = 'document.missing',
  
  // Data Events
  SOV_UPDATED = 'sov.updated',
  CONTRACT_SUM_CHANGED = 'contract_sum.changed',
  CHANGE_ORDER_APPROVED = 'change_order.approved',
  SUBMITTAL_STATUS_CHANGED = 'submittal.status_changed',
  
  // Workflow Events
  PAY_APP_SUBMITTED = 'pay_app.submitted',
  DAILY_LOG_SUBMITTED = 'daily_log.submitted',
  INSPECTION_COMPLETED = 'inspection.completed',
  
  // Alert Events
  CONFIDENCE_LOW = 'confidence.low',
  DATA_MISMATCH = 'data.mismatch',
  DOCUMENT_REQUIRED = 'document.required',
}
```

### Event Propagation Matrix

| Event | Estimator | PM | Detailer | Super | Safety | QC | Accounts | HR | Owner |
|-------|-----------|-----|---------|-------|--------|-----|----------|-----|-------|
| Scope Rev Changed | ✓ | ✓ | ✓ | ✓ | | | ✓ | | ✓ |
| Drawing Uploaded | ✓ | ✓ | ✓ | ✓ | | ✓ | | | |
| CO Approved | ✓ | ✓ | ✓ | ✓ | | | ✓ | | ✓ |
| Submittal Approved | | ✓ | ✓ | ✓ | | ✓ | | | |
| Daily Log Submitted | | ✓ | | ✓ | ✓ | | | ✓ | |
| Pay App Submitted | | ✓ | | | | | ✓ | | ✓ |
| Safety Issue Detected | | ✓ | | ✓ | ✓ | ✓ | | | |

---

## Role-Based Data Views

Each role sees ONLY the data relevant to their function:

### Project Manager View
```json
{
  "priority_documents": ["Scope of Work", "Assembly Letters", "Submittals"],
  "key_metrics": {
    "contract_sum": 1247500,
    "approved_cos": 2,
    "pending_submittals": 3,
    "active_rfis": 5,
    "schedule_variance": -2
  },
  "alerts": [
    "Scope Rev 2 has 3 changes from Rev 1",
    "Bond document missing - blocking Pay App",
    "Submittal #4 pending architect review"
  ]
}
```

### Accounts View
```json
{
  "priority_documents": ["Scope of Work", "SOV", "Pay Applications"],
  "key_metrics": {
    "contract_sum": 1247500,
    "billed_to_date": 0,
    "retainage_held": 0,
    "next_billing": "2025-12-31"
  },
  "sov_summary": {
    "total_lines": 12,
    "original_value": 1247500,
    "approved_cos": 57500,
    "current_contract": 1305000
  },
  "blockers": [
    "Bond document required before Pay App #1"
  ]
}
```

### Detailer View
```json
{
  "priority_documents": ["Drawings", "Assembly Letters", "Specs"],
  "key_metrics": {
    "total_sf": 32450,
    "penetrations": 24,
    "drains": 10,
    "curb_details": 8
  },
  "extracted_dimensions": {
    "building_length": 245,
    "building_width": 132,
    "parapet_height": 24,
    "slope": "1/4 per ft"
  },
  "version_changes": [
    "R-30 insulation (was R-25)",
    "4 additional drains in Alternate 2"
  ]
}
```

### Safety Officer View
```json
{
  "priority_documents": ["Specs", "Assembly Letters", "MSDS"],
  "safety_data": {
    "membrane_type": "TPO 60mil",
    "fire_rating": "Class A",
    "msds_required": ["TPO Adhesive", "Primer", "Sealant"],
    "fall_protection": "Required - 15ft height"
  },
  "certifications_needed": [
    "OSHA 30 for superintendent",
    "Fall protection for all crew",
    "Hot work permit if welding"
  ]
}
```

---

## Version Diff Engine

The AI compares document versions and highlights changes:

```typescript
interface VersionDiff {
  documentId: string;
  oldVersion: string;
  newVersion: string;
  changes: Change[];
  summary: string;
  affectedRoles: RoleId[];
  confidence: number;
}

interface Change {
  type: 'added' | 'removed' | 'modified';
  field: string;
  oldValue: any;
  newValue: any;
  impact: 'high' | 'medium' | 'low';
  affectedData: string[];
}

// Example: Scope Rev 1 → Rev 2 Diff
const scopeDiff: VersionDiff = {
  documentId: 'scope-001',
  oldVersion: 'Rev 1',
  newVersion: 'Rev 2',
  changes: [
    {
      type: 'modified',
      field: 'contract_sum',
      oldValue: 1185000,
      newValue: 1247500,
      impact: 'high',
      affectedData: ['sov.total', 'estimates.budget', 'pay_apps.contract']
    },
    {
      type: 'added',
      field: 'alternate_2',
      oldValue: null,
      newValue: { description: 'Additional Drains', amount: 12500 },
      impact: 'medium',
      affectedData: ['sov.alternates', 'detailer.drains']
    },
    {
      type: 'modified',
      field: 'insulation_r_value',
      oldValue: 'R-25',
      newValue: 'R-30',
      impact: 'medium',
      affectedData: ['specs.insulation', 'procurement.materials', 'qc.checklist']
    }
  ],
  summary: 'Rev 2 increases contract sum by 5.3% due to R-30 insulation upgrade. New Alternate 2 adds 4 drains.',
  affectedRoles: ['estimator', 'pm', 'accounts', 'detailer', 'qc'],
  confidence: 0.98
};
```

---

## Missing Document Detection

The system knows which documents are required and blocks workflows when missing:

```typescript
interface DocumentRequirement {
  documentType: string;
  requiredFor: WorkflowStep[];
  blockedRoles: RoleId[];
  alertLevel: 'critical' | 'warning' | 'info';
}

const documentRequirements: DocumentRequirement[] = [
  {
    documentType: 'Bond',
    requiredFor: ['pay_app_1', 'contract_execution'],
    blockedRoles: ['accounts'],
    alertLevel: 'critical'
  },
  {
    documentType: 'Insurance Certificate',
    requiredFor: ['mobilization', 'site_access'],
    blockedRoles: ['superintendent', 'foreman'],
    alertLevel: 'critical'
  },
  {
    documentType: 'Assembly Letter',
    requiredFor: ['submittal_package', 'procurement'],
    blockedRoles: ['pm', 'procurement'],
    alertLevel: 'warning'
  },
  {
    documentType: 'Approved Submittals',
    requiredFor: ['material_order', 'shop_drawings'],
    blockedRoles: ['detailer', 'procurement'],
    alertLevel: 'warning'
  }
];
```

---

## Database Schema (Integrated Project Database)

```sql
-- Core Tables

CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT,
  owner_id UUID REFERENCES contacts(id),
  architect_id UUID REFERENCES contacts(id),
  contract_sum DECIMAL(12,2),
  original_contract_sum DECIMAL(12,2),
  retainage_pct DECIMAL(5,2) DEFAULT 10,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents as Source of Truth
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  type TEXT NOT NULL, -- 'contract', 'scope', 'drawing', 'spec', 'assembly', 'submittal'
  filename TEXT NOT NULL,
  version TEXT DEFAULT '1',
  file_path TEXT NOT NULL,
  file_size INTEGER,
  uploaded_by UUID REFERENCES users(id),
  parsed_at TIMESTAMPTZ,
  parse_confidence DECIMAL(5,4),
  is_current BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Extracted Data (linked to source document)
CREATE TABLE extracted_data (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  field_name TEXT NOT NULL,
  field_value JSONB,
  confidence DECIMAL(5,4),
  source_page INTEGER,
  source_location TEXT, -- bounding box or text snippet
  validated_by UUID REFERENCES users(id),
  validated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Version Diffs
CREATE TABLE document_diffs (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  old_document_id UUID REFERENCES documents(id),
  new_document_id UUID REFERENCES documents(id),
  changes JSONB NOT NULL, -- array of Change objects
  summary TEXT,
  affected_roles TEXT[],
  confidence DECIMAL(5,4),
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event Log (Audit Trail)
CREATE TABLE events (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  event_type TEXT NOT NULL,
  document_id UUID REFERENCES documents(id),
  user_id UUID REFERENCES users(id),
  data JSONB,
  affected_roles TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role-Specific Views
CREATE VIEW pm_project_view AS
SELECT 
  p.*,
  (SELECT COUNT(*) FROM submittals s WHERE s.project_id = p.id AND s.status = 'pending') as pending_submittals,
  (SELECT COUNT(*) FROM rfis r WHERE r.project_id = p.id AND r.status = 'open') as open_rfis,
  (SELECT COUNT(*) FROM change_orders co WHERE co.project_id = p.id AND co.status = 'pending') as pending_cos,
  (SELECT json_agg(d.*) FROM documents d WHERE d.project_id = p.id AND d.type IN ('scope', 'assembly', 'submittal') AND d.is_current = TRUE) as priority_docs
FROM projects p;

CREATE VIEW accounts_project_view AS
SELECT 
  p.*,
  (SELECT COALESCE(SUM(pa.current_payment_due), 0) FROM pay_applications pa WHERE pa.project_id = p.id AND pa.status = 'approved') as billed_to_date,
  (SELECT COALESCE(SUM(pa.retainage), 0) FROM pay_applications pa WHERE pa.project_id = p.id) as retainage_held,
  (SELECT json_agg(sov.*) FROM schedule_of_values sov WHERE sov.project_id = p.id ORDER BY sov.line_number) as sov_lines,
  (SELECT NOT EXISTS(SELECT 1 FROM documents d WHERE d.project_id = p.id AND d.type = 'bond')) as bond_missing
FROM projects p;
```

---

## Implementation Phases

### Phase 1: Document Parser (Weeks 1-2)
- [ ] PDF text extraction (pdfjs, Textract)
- [ ] Image OCR for scanned docs (Tesseract)
- [ ] AI field extraction (Claude/Groq)
- [ ] Confidence scoring
- [ ] Schema mapping to database

### Phase 2: Data Central UI (Weeks 3-4)
- [ ] Document upload with drag-drop
- [ ] Virtual document preview
- [ ] Extracted data display below document
- [ ] Missing document alerts
- [ ] Role-based filtering

### Phase 3: Version Diff Engine (Weeks 5-6)
- [ ] Version tracking per document
- [ ] AI-powered comparison
- [ ] Change visualization
- [ ] Affected roles notification
- [ ] Version history timeline

### Phase 4: Event-Driven Architecture (Weeks 7-8)
- [ ] Event stream (Redis pub/sub or Kafka)
- [ ] Event handlers for each role
- [ ] Real-time UI updates
- [ ] Event history/audit log
- [ ] Webhook integrations

### Phase 5: Role-Based Views (Weeks 9-10)
- [ ] PM Mission Control
- [ ] Accounts Dashboard
- [ ] Superintendent Field View
- [ ] Safety Officer Compliance View
- [ ] Owner Executive Summary

---

## Key Competitive Advantages

1. **Documents ARE the Database**
   - No duplicate data entry
   - Source always traceable
   - Version history built-in

2. **AI-Powered Extraction**
   - 95%+ accuracy on structured docs
   - Continuous learning from corrections
   - Multi-format support (PDF, Excel, Images)

3. **Instant Propagation**
   - Change a contract sum → ALL roles updated instantly
   - No stale data anywhere in the system
   - Real-time dashboards

4. **Version Intelligence**
   - AI detects what changed between revisions
   - Saves hours of manual red-lining
   - Alerts affected roles automatically

5. **Role-Based Simplicity**
   - Each user sees only what they need
   - No information overload
   - Faster workflows

This is the architecture that makes Roofio the "World's Smartest Roofer" - because the intelligence starts at the SOURCE of truth: the documents.
