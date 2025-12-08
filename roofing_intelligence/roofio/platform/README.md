# ROOFIO Platform Architecture

## Unified Project Object (UPO) System

**CRITICAL PRINCIPLE**: Data flows DOWN from Project → Job → Forms. Data flows UP from Forms → Job → Reports.

**RULE**: Data entered ONCE (in Estimate) propagates EVERYWHERE (PM, Safety, Accounting, QC).

---

## Directory Structure

```
platform/
├── README.md                     # This file
├── ROOFIO-PLATFORM-SPEC-v2.md   # Complete specification
│
├── database/
│   └── schema.sql               # PostgreSQL schema with UPO
│
├── positions/
│   └── __init__.py              # 8 positions with Full AI/Assist modes
│
├── forms/
│   └── __init__.py              # 74 forms with SSOT mappings
│
├── badges/
│   └── __init__.py              # Visual badge system
│
├── confidence/
│   └── __init__.py              # AI confidence scoring (90% threshold)
│
└── api/
    └── (planned)                # REST API endpoints
```

---

## Mode System

### Full AI Mode 🤖 `[ROOFIO AUTONOMOUS]`
- AI handles entire role autonomously
- No human in position
- Monitors confidence score
- Auto-pauses at <90% confidence

### AI Assist Mode 🧑‍💼 `[ROOFIO ASSIST]`
- Human in position
- AI provides one-click support
- Pre-fills forms from SSOT
- Suggests actions

### Confidence Thresholds
```
95-100%  → Full AI proceeds autonomously
90-94%   → Full AI proceeds, flags for optional review
80-89%   → AUTO-PAUSE ⚠️ Human review required
Below 80% → STOP ❌ Cannot proceed without human input
```

---

## The 8 Positions

| Position | Forms | Typical Mode |
|----------|-------|--------------|
| Estimator | 10 | Full AI / Assist |
| Project Manager | 11 | Full AI |
| Shop Drawing Detailer | 7 | Assist |
| Specification Writer | 6 | Full AI |
| QC Inspector | 10 | Assist |
| Safety Officer | 10 | Full AI |
| Superintendent | 9 | Assist |
| Accounts | 11 | Full AI |
| **TOTAL** | **74** | |

---

## SSOT Data Flow

```
ESTIMATOR sets:
├── Material = "TPO 60mil White"
├── Manufacturer = "Carlisle SynTec"
├── Quantity = 45,000 SF
└── Attachment = "Fully Adhered"

THIS DATA AUTO-PROPAGATES TO:
├── PM → Submittal #001: TPO 60mil White - Carlisle SynTec
├── SUPERINTENDENT → PO Draft: 45,000 SF TPO 60mil White
├── QC → Auto-generated: TPO Seam Probe Checklist
├── SAFETY → Hazards: Adhesive fumes, MEK exposure
├── SPEC WRITER → Carlisle NDL warranty application pre-filled
└── ACCOUNTS → SOV Line Item: TPO Membrane - 45,000 SF @ $X.XX
```

---

## Database Entity Relationships

```
COMPANY (root)
├── CONTACTS (shared pool)
├── EMPLOYEES
├── PRODUCTS (material library with hazards[], inspection_requirements[])
│
└── PROJECTS (Unified Project Object - UPO)
    ├── ESTIMATE (source data)
    │   └── LINE_ITEMS (links to products)
    │
    └── JOBS (scopes within project)
        ├── SCHEDULE_OF_VALUES (auto from estimate)
        ├── SUBMITTALS (auto from estimate products)
        ├── RFIs
        ├── CHANGE_ORDERS
        ├── DAILY_REPORTS (updates SOV progress)
        ├── STORED_MATERIALS (links to SOV)
        ├── INSPECTIONS (checklists from system_type)
        ├── SAFETY_DOCUMENTS (JHA from products.hazards)
        ├── PAY_APPLICATIONS (calculated from SOV)
        └── CLOSEOUT_DOCUMENTS
```

---

## Auto-Trigger Forms

These forms generate automatically when their trigger conditions are met:

| Form | Trigger | Position |
|------|---------|----------|
| Submittal Log | Estimate approved | PM |
| SOV | Estimate approved | Accounts |
| JHA | Job created with materials | Safety |
| Toolbox Talk | Weekly schedule | Safety |
| Fall Protection Plan | Job height > 6ft | Safety |
| Silica Control Plan | Scope includes cutting | Safety |
| Pay App (G702) | Billing period ends | Accounts |
| Lien Waiver (Cond) | Pay app approved | Accounts |
| Lien Waiver (Uncond) | Payment received | Accounts |
| Weather Delay Log | Rain forecast | Superintendent |
| 2-Week Lookahead | Weekly schedule | Superintendent |
| Permit Application | Municipality selected | PM |
| Warranty Application | Closeout begins | Spec Writer |

---

## Key Implementation Notes

1. **Never create siloed forms** - Every form links to Project_ID
2. **Products drive safety** - Product hazards auto-populate JHAs
3. **System type drives QC** - Job.system_type selects inspection checklists
4. **Estimate is the source** - All downstream forms pull from estimate data
5. **Daily reports update SOV** - Progress flows up to billing
6. **Confidence gates actions** - AI pauses when uncertain

---

## Tech Stack (Recommended)

- **Database**: PostgreSQL (Supabase)
- **Backend**: Python / Edge Functions
- **Frontend**: Next.js + Tailwind + shadcn/ui
- **AI**: Claude API (Anthropic)
- **PDF**: react-pdf/renderer
- **Weather**: OpenWeatherMap API

---

## Version

- **Spec Version**: 2.0 FINAL
- **Forms**: 74 total
- **Positions**: 8
- **Date**: December 2025
