# ROOFIO Platform Specification
## Complete Data-Linked AI Assistant System for Roofing Contractors
### Version 2.0 - Claude Code Ready - FINAL

---

## EXECUTIVE SUMMARY

This specification defines a **unified data platform** where all forms, documents, and AI functions share a **Single Source of Truth (SSOT)**. Every form auto-populates from the Unified Project Object. Every AI action logs to the project record. Every position (human or AI) works from the same synchronized data.

**Core Principle**: Data flows DOWN from Project → Job → Forms. Data flows UP from Forms → Job → Reports.

**Critical Rule**: Data entered ONCE (in Estimate) must propagate EVERYWHERE (PM, Safety, Accounting, QC).

---

## PART 1: DATA ARCHITECTURE - THE "SYNC" BACKBONE

### 1.1 Unified Project Object (UPO) - CRITICAL

**DO NOT BUILD SILOED FORMS.** Build a relational database where `Project_ID` links EVERY variable.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED PROJECT OBJECT (UPO)                              │
│                    ════════════════════════════                              │
│                                                                              │
│  EXAMPLE DATA FLOW:                                                          │
│  ─────────────────                                                          │
│                                                                              │
│  ESTIMATOR sets:                                                             │
│  ├── Material = "TPO 60mil White"                                           │
│  ├── Manufacturer = "Carlisle SynTec"                                       │
│  ├── Quantity = 45,000 SF                                                   │
│  └── Attachment = "Fully Adhered"                                           │
│                                                                              │
│  THIS DATA AUTO-PROPAGATES TO:                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  PM (Submittals)                                                    │    │
│  │  ├── Submittal #001: TPO 60mil White - Carlisle SynTec             │    │
│  │  └── Pre-filled product data sheet requirements                     │    │
│  │                                                                     │    │
│  │  SUPERINTENDENT (Material Orders)                                   │    │
│  │  ├── PO Draft: 45,000 SF TPO 60mil White                           │    │
│  │  └── Delivery schedule linked to project timeline                   │    │
│  │                                                                     │    │
│  │  QC (Inspection Checklists)                                         │    │
│  │  ├── Auto-generated: TPO Seam Probe Checklist                      │    │
│  │  ├── Auto-generated: Fully Adhered Substrate Checklist             │    │
│  │  └── Manufacturer-specific inspection requirements                  │    │
│  │                                                                     │    │
│  │  SAFETY (JHA)                                                       │    │
│  │  ├── Hazards auto-added: Adhesive fumes, MEK exposure              │    │
│  │  └── PPE requirements: Respirator, chemical gloves                  │    │
│  │                                                                     │    │
│  │  SPEC WRITER (Warranty App)                                         │    │
│  │  ├── Carlisle NDL warranty application pre-filled                  │    │
│  │  └── Required documentation checklist generated                     │    │
│  │                                                                     │    │
│  │  ACCOUNTS (Pay App)                                                 │    │
│  │  ├── SOV Line Item: TPO Membrane - 45,000 SF @ $X.XX               │    │
│  │  └── Retainage calculations per contract terms                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 The "Confidence Switch" - AI Safety Mechanism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI CONFIDENCE SWITCH                                  │
│                        ════════════════════                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  RULE: In "Full AI" mode, if confidence score drops below 90% on any        │
│        task, the system MUST:                                                │
│                                                                              │
│        1. AUTO-PAUSE the task                                               │
│        2. FLAG for human review                                             │
│        3. SWITCH to Assistant Mode for that task                            │
│        4. LOG the confidence score and reason                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONFIDENCE SCORING:                                                │    │
│  │                                                                     │    │
│  │  95-100%  ──► Full AI proceeds autonomously                        │    │
│  │  90-94%   ──► Full AI proceeds, flags for optional review          │    │
│  │  80-89%   ──► AUTO-PAUSE ⚠️ Human review required                  │    │
│  │  Below 80% ─► STOP ❌ Cannot proceed without human input           │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  CONFIDENCE FACTORS:                                                         │
│  ├── Data completeness (are all required fields populated?)                 │
│  ├── Data consistency (do values conflict with other records?)              │
│  ├── Historical accuracy (how often has similar AI output been edited?)     │
│  ├── Ambiguity detection (are there multiple valid interpretations?)        │
│  └── Risk level (financial/safety impact of error)                          │
│                                                                              │
│  EXAMPLE:                                                                    │
│  ─────────                                                                  │
│  AI Task: "Generate Change Order from RFI #007"                             │
│                                                                              │
│  ├── RFI response text is ambiguous      ──► -15% confidence               │
│  ├── Cost impact not explicitly stated   ──► -10% confidence               │
│  ├── Similar COs edited 40% of time      ──► -5% confidence                │
│  │                                                                          │
│  └── Final Score: 70% ──► ❌ AUTO-PAUSE                                     │
│                                                                              │
│      System Action:                                                          │
│      ┌────────────────────────────────────────────────────────────────┐     │
│      │  ⚠️ AI PAUSED - Human Review Required                         │     │
│      │                                                                │     │
│      │  Task: Generate Change Order from RFI #007                    │     │
│      │  Confidence: 70%                                              │     │
│      │                                                                │     │
│      │  Issues Detected:                                             │     │
│      │  • RFI response text is ambiguous                             │     │
│      │  • Cost impact not explicitly stated                          │     │
│      │                                                                │     │
│      │  [Review Draft]  [Take Over Manually]  [Provide More Info]   │     │
│      └────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Complete Entity Relationship Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROOFIO DATA MODEL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMPANY (root)                                                              │
│  ├── company_id, name, license_no, insurance_info, tax_id                   │
│  ├── default_markup, warranty_terms, payment_terms                          │
│  ├── labor_rates[], overhead_rate, profit_margin_target                     │
│  │                                                                          │
│  ├── CONTACTS (shared pool - enters ONCE, used EVERYWHERE)                  │
│  │   ├── contact_id, type (owner/gc/architect/sub/supplier/inspector/adj)  │
│  │   ├── name, company, email, phone, address                              │
│  │   └── relationship_history[], notes                                      │
│  │                                                                          │
│  ├── EMPLOYEES                                                              │
│  │   ├── employee_id, name, role, certifications[], hourly_rate            │
│  │   ├── emergency_contact, training_records[], OSHA_10_30                 │
│  │   └── assigned_projects[]                                                │
│  │                                                                          │
│  ├── PRODUCTS (material library - SSOT for all material data)              │
│  │   ├── product_id, manufacturer, name, sku, unit, unit_cost              │
│  │   ├── spec_section, fm_approval, ul_listing, warranty_years             │
│  │   ├── supplier_id, lead_time                                            │
│  │   ├── hazards[] (for auto-JHA generation)                               │
│  │   ├── inspection_requirements[] (for auto-QC checklist)                 │
│  │   └── warranty_form_template_id                                          │
│  │                                                                          │
│  └── PROJECTS (Unified Project Object - UPO)                                │
│      ├── project_id, name, address, type (commercial/residential)          │
│      ├── gc_contact_id, owner_contact_id, architect_contact_id             │
│      ├── adjuster_contact_id (for insurance work)                          │
│      ├── permit_number, permit_status, municipality_id                     │
│      ├── contract_amount, start_date, end_date, status                     │
│      ├── spec_sections[], insurance_requirements                           │
│      ├── is_insurance_claim, claim_number, policy_number                   │
│      │                                                                      │
│      ├── ESTIMATE (source data - propagates to all)                        │
│      │   ├── estimate_id, version, status, created_date                    │
│      │   ├── line_items[]                                                  │
│      │   │   ├── product_id, quantity, unit_cost, total                    │
│      │   │   ├── labor_hours, labor_rate, labor_total                      │
│      │   │   └── markup_percent, line_total                                │
│      │   ├── subtotal_materials, subtotal_labor                            │
│      │   ├── overhead_amount, profit_amount                                │
│      │   ├── total_estimate                                                │
│      │   └── margin_analysis{}  [NEW]                                      │
│      │                                                                      │
│      ├── JOBS (individual scopes within project)                           │
│      │   ├── job_id, scope_description, area_sqft                          │
│      │   ├── system_type, warranty_type, attachment_method                 │
│      │   │   └── (THESE DRIVE QC CHECKLISTS AUTOMATICALLY)                 │
│      │   ├── original_amount, change_orders_total, current_amount          │
│      │   ├── billed_to_date, retention_held, balance_due                   │
│      │   │                                                                  │
│      │   ├── SCHEDULE_OF_VALUES[] (SOV - Links to Pay Apps)                │
│      │   │   ├── line_item, description, spec_section                      │
│      │   │   ├── scheduled_value (from estimate)                           │
│      │   │   ├── work_completed_previous, work_completed_current           │
│      │   │   ├── materials_stored, total_completed, percent_complete       │
│      │   │   └── balance_to_finish, retainage                              │
│      │   │                                                                  │
│      │   ├── SUBMITTALS[]                                                  │
│      │   │   ├── (Auto-generated from estimate materials)                  │
│      │   │   ├── submittal_id, number, spec_section, description           │
│      │   │   ├── product_ids[] (linked to estimate)                        │
│      │   │   ├── submitted_date, required_date, status                     │
│      │   │   └── attachments[], revision_history[]                         │
│      │   │                                                                  │
│      │   ├── RFIs[]                                                        │
│      │   │   ├── rfi_id, number, subject, question, drawing_ref            │
│      │   │   ├── cost_impact, schedule_impact, confidence_score            │
│      │   │   └── linked_change_orders[]                                    │
│      │   │                                                                  │
│      │   ├── CHANGE_ORDERS[]                                               │
│      │   │   ├── co_id, number, description, reason                        │
│      │   │   ├── labor_cost, material_cost, markup, total                  │
│      │   │   ├── (Labor/material rates LINKED from estimate)               │
│      │   │   └── approval_signatures[], confidence_score                   │
│      │   │                                                                  │
│      │   ├── DAILY_REPORTS[]                                               │
│      │   │   ├── (Weather auto-fetched, crew auto-populated)               │
│      │   │   ├── percent_complete_update (feeds SOV)                       │
│      │   │   ├── materials_installed_today[] (links to products)           │
│      │   │   └── stored_materials_log[]  [NEW]                             │
│      │   │                                                                  │
│      │   ├── INSPECTIONS[]                                                 │
│      │   │   ├── (Checklist auto-generated from system_type)               │
│      │   │   ├── moisture_analysis_id  [NEW]                               │
│      │   │   └── penetration_log_id  [NEW]                                 │
│      │   │                                                                  │
│      │   ├── SAFETY_DOCS[]                                                 │
│      │   │   ├── JHA (hazards auto-populated from products)                │
│      │   │   ├── silica_control_plan_id  [NEW]                             │
│      │   │   ├── hot_work_permits[]                                        │
│      │   │   └── crane_lift_plans[]  [NEW]                                 │
│      │   │                                                                  │
│      │   ├── PAY_APPLICATIONS[]                                            │
│      │   │   ├── (Calculated from SOV + Daily Report progress)             │
│      │   │   ├── stored_materials_amount (from stored material log)        │
│      │   │   └── lien_waiver_ids[]                                         │
│      │   │                                                                  │
│      │   └── CLOSEOUT_DOCS[]                                               │
│      │       ├── warranty_applications[]  [NEW]                            │
│      │       ├── as_built_drawings[]  [NEW]                                │
│      │       └── manufacturer_warranty_ids[]                               │
│      │                                                                      │
│      ├── INSURANCE_SUPPLEMENTS[]  [NEW]                                    │
│      │   ├── supplement_id, original_estimate_id                           │
│      │   ├── missed_items[], code_upgrades[]                               │
│      │   ├── adjuster_contact_id                                           │
│      │   └── status, amount_requested, amount_approved                     │
│      │                                                                      │
│      ├── PERMITS[]  [NEW]                                                  │
│      │   ├── permit_id, municipality_id, permit_type                       │
│      │   ├── application_date, approval_date, expiration_date              │
│      │   ├── inspection_schedule[]                                         │
│      │   └── auto_filled_from: project + estimate data                     │
│      │                                                                      │
│      └── DRAWINGS[]                                                         │
│          ├── drawing_id, number, title, revision, is_as_built              │
│          ├── redlines[] (field changes)  [NEW]                             │
│          └── linked_rfis[], linked_submittals[]                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Data Propagation Rules (SSOT)

```
DATA ENTERED ONCE ──► PROPAGATES EVERYWHERE
═══════════════════════════════════════════

TRIGGER                              AUTOMATIC PROPAGATION
─────────────────────────────────────────────────────────────────────────────

Estimate created with materials  ──► • Submittal log auto-generated
                                     • SOV line items created
                                     • Material order drafts created
                                     • QC checklists selected
                                     • JHA hazards identified
                                     • Warranty forms queued

Contact added to project         ──► • Available in all form dropdowns
                                     • Email/phone pre-filled everywhere
                                     • Transmittal routing auto-configured

System type selected             ──► • Inspection checklists loaded
(e.g., "TPO Fully Adhered")          • Seam testing requirements set
                                     • Manufacturer requirements loaded
                                     • Warranty application selected

Daily report logged              ──► • SOV percent complete updated
                                     • Weather delay auto-documented
                                     • Safety meeting attendance logged
                                     • Pay app progress calculated

Change order approved            ──► • Contract sum updated
                                     • SOV adjusted
                                     • Pay app recalculated
                                     • Estimate profitability updated

Inspection failed                ──► • Punch list auto-created
                                     • Closeout blocked
                                     • Daily report flagged
                                     • Warranty application held

All closeout docs received       ──► • Job status → COMPLETE
                                     • Final pay app unlocked
                                     • Warranty letter generated
                                     • As-built package compiled
```

---

## PART 2: FORM LIBRARY - FINAL COMPLETE LIST

### 2.1 Forms by Position with All Additions

#### ESTIMATOR (10 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Bid Proposal | Formal bid submission | Contact, Project, Quantities | AI/Assist |
| ✅ Scope of Work | Detailed work description | Project, System type | AI/Assist |
| ✅ Material Takeoff & BOM | Bill of Materials | Takeoff, Product library | Full AI |
| ✅ Unit Price Schedule | Line item pricing | Products, Labor rates | AI/Assist |
| ✅ Exclusions/Clarifications | What's NOT included | Template + Project | AI/Assist |
| ✅ Bid Bond Request | Surety request | Project value, Company | Assist |
| ✅ Bid Comparison Sheet | Compare competitor bids | Manual entry | Assist |
| ✅ Subcontractor Quote Request | Get sub pricing | Project, Scope | AI/Assist |
| 🆕 **Insurance Supplement Request** | Document missed items for adjusters | Original estimate, Claim | Full AI |
| 🆕 **Profit/Margin Analyzer** | Live labor/material/overhead breakdown | Estimate, Actuals | Full AI |

#### PROJECT MANAGER (11 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Submittal Cover Sheet | Track product approvals | Project, Spec, Products | Full AI |
| ✅ Submittal Log | Track all submittals | Auto-generated from estimate | Full AI |
| ✅ RFI Form | Request clarification | Project, Drawing, Contact | AI/Assist |
| ✅ RFI Log | Track all RFIs | Auto-generated | Full AI |
| ✅ Change Order Request | Document scope changes | Job, RFI, Pricing | AI/Assist |
| ✅ Change Order Log | Track all COs | Auto-generated | Full AI |
| ✅ Meeting Minutes | Record decisions | Project, Attendees | AI/Assist |
| ✅ Transmittal | Cover sheet for docs sent | Project, Recipient | AI/Assist |
| ✅ Schedule Update Notice | Communicate delays | Project, Schedule | AI/Assist |
| ✅ Delay Notification | Formal delay claim | Project, Weather/RFI data | AI/Assist |
| 🆕 **Permit Application Packet** | Apply for building permit | Project, Estimate, Municipality | Full AI |

#### SHOP DRAWING DETAILER (7 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Shop Drawing Transmittal | Submit drawings for review | Project, Drawing list | Assist |
| ✅ Drawing Register/Log | Track all drawings | Project, Auto-generated | Assist |
| ✅ Revision History Sheet | Log changes | Drawing, Previous revisions | Assist |
| ✅ Detail Index | Catalog of details | Drawing set | Assist |
| ✅ Keynote Legend | Define symbols | Project standards | Assist |
| ✅ Drawing Review Response | Address reviewer comments | Submittal response | Assist |
| 🆕 **As-Built Drawing Overlay** | Redline field changes over originals | Original drawings, Field notes | Assist |

#### SPECIFICATION WRITER (6 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Specification Section | CSI 3-part format | Template, Products | Full AI |
| ✅ Product Data Sheet Compilation | Organize manufacturer data | Products, Submittals | Full AI |
| ✅ Substitution Request | Request product swap | Original spec, Alt product | AI/Assist |
| ✅ Basis of Design Summary | Document BOD products | Spec sections | Full AI |
| ✅ Spec Compliance Checklist | Verify installation matches spec | Spec, Inspection | Assist |
| 🆕 **Manufacturer Warranty Application** | Pre-fill NDL/warranty forms | Project, Products, Manufacturer | Full AI |

#### QC / INSPECTOR (10 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Pre-Installation Checklist | Verify readiness | Job, Manufacturer requirements | Assist |
| ✅ Progress Inspection Report | Document ongoing work | Job, System-specific checklist | Assist |
| ✅ Final Inspection Report | Sign-off inspection | Job, All prior inspections | Assist |
| ✅ Punch List | Deficiency tracking | Inspection findings | Assist |
| ✅ Test Report (flood/ELD/core) | Document test results | Job, Test type template | Assist |
| ✅ Non-Conformance Report | Document defects | Inspection, Spec reference | Assist |
| ✅ Warranty Inspection Checklist | Pre-warranty check | Manufacturer requirements | Assist |
| ✅ Photo Documentation Log | Organize progress photos | Job, Date, Location | Assist |
| 🆕 **Moisture Analysis Report** | Nuclear/Infrared scan logging | Job, Equipment readings | Assist |
| 🆕 **Roof Penetration Log** | Track flashings/curbs | Job, Drawing refs | Assist |

#### SAFETY OFFICER (10 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Job Hazard Analysis (JHA) | Identify hazards | Job type, Products (auto-hazards) | Full AI |
| ✅ Toolbox Talk Sign-In | Document safety meetings | Project, Crew, Topic library | Full AI |
| ✅ Incident/Accident Report | Document injuries | Project, Employee, Date | Assist |
| ✅ Safety Inspection Checklist | Site safety audit | OSHA requirements | AI/Assist |
| ✅ Hot Work Permit | Authorize torch work | Project, Location, Date | Assist |
| ✅ Fall Protection Plan | Document fall prevention | Job, Height, Equipment | Full AI |
| ✅ Equipment Inspection Log | Track equipment safety | Equipment list | Assist |
| ✅ OSHA 300 Log Entry | Recordable incident log | Incident report | Assist |
| 🆕 **Silica Exposure Control Plan** | OSHA mandatory for cutting | Job scope, Materials | Full AI |
| 🆕 **Crane/Hoist Lift Plan** | Critical for roof loading | Job, Equipment, Loads | Assist |

#### SUPERINTENDENT / FOREMAN (9 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Daily Field Report | Document daily activities | Project, Weather API, Crew | AI/Assist |
| ✅ T&M (Time & Materials) Ticket | Track extra work | Job, Employee, Materials | Assist |
| ✅ Material Receiving Log | Document deliveries | PO, Supplier, Products | Assist |
| ✅ Delivery Schedule | Plan material drops | Job, Supplier calendar | AI/Assist |
| ✅ 2-Week Lookahead | Short-term schedule | Master schedule | Full AI |
| ✅ Extra Work Authorization | Approve additional work | Job, CO pending | Assist |
| ✅ Weather Delay Log | Document weather impacts | Daily report, Weather API | Full AI |
| ✅ Crew Assignment Sheet | Daily crew deployment | Employees, Jobs | AI/Assist |
| 🆕 **Stored Material Log** | Track material on roof vs ground | Deliveries, Location | Assist |

#### ACCOUNTS / ADMINISTRATION (11 Forms)
| Form | Purpose | Pre-fill Source | Mode |
|------|---------|-----------------|------|
| ✅ Progress Invoice (G702/G703) | Request payment | SOV, Previous payments | Full AI |
| ✅ Lien Waiver (Conditional) | Release lien rights | Pay app, Amount | Full AI |
| ✅ Lien Waiver (Unconditional) | Final lien release | Pay app, Amount | Full AI |
| ✅ Certificate of Insurance Request | Request updated COI | Vendor, Project | AI/Assist |
| ✅ Contract Exhibit Checklist | Track contract docs | Project, Template | Assist |
| ✅ Closeout Document Checklist | Track closeout | Job, Required docs | Assist |
| ✅ Warranty Letter | Issue workmanship warranty | Job, Company terms | Full AI |
| ✅ Subcontractor Pay Request | Sub payment processing | Sub contract, SOV | AI/Assist |
| ✅ Notice of Completion | Formal project completion | Project, Final inspection | Full AI |
| 🆕 **Schedule of Values (SOV)** | Contract breakdown | Estimate, Contract | Full AI |
| 🆕 **Job Cost Report** | Actual vs Estimated | Estimate, Daily reports, POs | Full AI |

### 2.2 Form Count Summary - FINAL

| Position | Original | Your Additions | Final |
|----------|----------|----------------|-------|
| Estimator | 8 | +2 | **10** |
| Project Manager | 9 | +1 | **11** (includes logs) |
| Shop Drawing Detailer | 6 | +1 | **7** |
| Specification Writer | 5 | +1 | **6** |
| QC/Inspector | 8 | +2 | **10** |
| Safety Officer | 8 | +2 | **10** |
| Superintendent | 8 | +1 | **9** |
| Accounts | 9 | +2 | **11** |
| **TOTAL** | **61** | **+12** | **74** |

---

## PART 3: UI/UX SPECIFICATION

### 3.1 Mode Toggle System with Confidence Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROOFIO CONTROL CENTER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ COMPANY SETTINGS ──────────────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │  POSITION CONFIGURATION                    [Toggle All AI] [Reset]  │    │
│  │  ═══════════════════════════════════════════════════════════════    │    │
│  │                                                                      │    │
│  │  ESTIMATOR          ○ OFF   ○ ASSIST   ◉ FULL AI    [98% avg]      │    │
│  │  PROJECT MANAGER    ○ OFF   ○ ASSIST   ◉ FULL AI    [94% avg]      │    │
│  │  SHOP DETAILER      ○ OFF   ◉ ASSIST   ○ FULL AI    [n/a]          │    │
│  │  SPEC WRITER        ○ OFF   ○ ASSIST   ◉ FULL AI    [96% avg]      │    │
│  │  QC / INSPECTOR     ○ OFF   ◉ ASSIST   ○ FULL AI    [n/a]          │    │
│  │  SAFETY OFFICER     ○ OFF   ○ ASSIST   ◉ FULL AI    [97% avg]      │    │
│  │  SUPERINTENDENT     ○ OFF   ◉ ASSIST   ○ FULL AI    [n/a]          │    │
│  │  ACCOUNTS           ○ OFF   ○ ASSIST   ◉ FULL AI    [99% avg]      │    │
│  │                                                                      │    │
│  │  ⚠️ CONFIDENCE THRESHOLD: [90%] (AI pauses below this)             │    │
│  │                                                                      │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─ AI ACTIVITY SUMMARY ───────────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │  TODAY:  Actions: 47  |  Auto-Completed: 45  |  Flagged: 2          │    │
│  │                                                                      │    │
│  │  ⚠️ PENDING REVIEW (2)                                              │    │
│  │  ├── CO #003 from RFI #007 - Confidence: 72% - [Review Now]         │    │
│  │  └── JHA for Job #12 - Missing hazard data - [Provide Info]         │    │
│  │                                                                      │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─ FORM SETS (Toggle Groups) ─────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │  ☑ Core Project Management (RFI, Submittal, CO, Pay App)  REQUIRED  │    │
│  │  ☑ Daily Operations (Daily Report, T&M, Delivery)         ENABLED   │    │
│  │  ☑ Safety & Compliance (JHA, Toolbox, Incident)           ENABLED   │    │
│  │  ☑ Closeout (Warranty, Punch, Lien Waiver)                ENABLED   │    │
│  │  ☑ Insurance Claims (Supplement, Adjuster Docs)           ENABLED   │    │
│  │  ☐ Estimating (Bid, SOW, Unit Pricing)                    DISABLED  │    │
│  │  ☐ Advanced Specs (CSI Sections)                          DISABLED  │    │
│  │                                                                      │    │
│  │  [Expand to Configure Individual Forms ▼]                           │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Visual Badge System with Confidence

```
MODE INDICATORS (Always Visible)
════════════════════════════════

🤖 FULL AI MODE (Agent)
┌──────────────────────────────────────────────────────────────┐
│  🤖 [ROOFIO AUTONOMOUS]            Confidence: ████████ 96%  │
│  ▸ Handling: Submittals, Schedule, RFIs, Pay Apps            │
│  ▸ Actions Today: 12 completed, 0 flagged                    │
│  ▸ [View Activity Log]  [Pause All AI]                       │
└──────────────────────────────────────────────────────────────┘

⚠️ FULL AI MODE - PAUSED (Confidence Drop)
┌──────────────────────────────────────────────────────────────┐
│  ⚠️ [ROOFIO PAUSED]                Confidence: ████░░ 72%    │
│  ▸ Reason: Ambiguous RFI response                            │
│  ▸ Task: Generate CO from RFI #007                           │
│  ▸ [Review Draft]  [Take Over]  [Provide More Info]          │
└──────────────────────────────────────────────────────────────┘

🧑‍💼 ASSIST MODE (Copilot)
┌──────────────────────────────────────────────────────────────┐
│  🧑‍💼 [ROOFIO ASSIST] Armand                                   │
│  ▸ Available: [New RFI] [New CO] [Daily Report] [+ More]     │
│  ▸ Suggestions: 2 items ready for review                     │
│  ▸ [Voice Input 🎤]  [Quick Actions ▼]                        │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 Job Dashboard with SSOT Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  JOB: JHU Homewood Library - Roof Replacement                    [Edit Job] │
│  Status: IN PROGRESS   |   Phase: Installation   |   System: TPO 60mil FA  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ FINANCIAL SNAPSHOT (Live from SSOT) ────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Original Contract    Change Orders    Current Contract    Billed    │   │
│  │  $847,500            +$23,400 (2)      $870,900           $435,450   │   │
│  │                                                                      │   │
│  │  ┌─ MARGIN ANALYZER ────────────────────────────────────────────┐   │   │
│  │  │  Estimated Margin: 18.5%  │  Current Margin: 17.2%  │  ▼1.3% │   │   │
│  │  │  Labor Variance: -$4,200  │  Material Variance: +$1,800      │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ SSOT DATA (Set Once, Used Everywhere) ──────────────────────────────┐   │
│  │                                                                      │   │
│  │  MATERIALS (from Estimate):                                         │   │
│  │  ├── TPO 60mil White - Carlisle SynTec - 45,000 SF                  │   │
│  │  │   └── Drives: Submittal #001, PO #234, QC Checklist #TPO-FA     │   │
│  │  ├── 2.6" Polyiso - Johns Manville - 45,000 SF                      │   │
│  │  │   └── Drives: Submittal #002, PO #235, QC Checklist #ISO        │   │
│  │  └── [View All 23 Line Items]                                       │   │
│  │                                                                      │   │
│  │  CONTACTS:                                                          │   │
│  │  ├── Owner: JHU Facilities (John Smith) - john@jhu.edu             │   │
│  │  ├── GC: Turner Construction (Sarah Lee) - slee@turner.com         │   │
│  │  ├── Architect: Ayers Saint Gross (Mike Chen) - mchen@asg.com      │   │
│  │  └── [+ Add Contact]                                                │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ ACTIVE ITEMS ─────────────────────────┬─ AI STATUS ─────────────────┐   │
│  │                                        │                              │   │
│  │  ⚠️  RFI #007 - Response unclear       │  🤖 PM: 94% confidence       │   │
│  │  📋 Submittal #012 - Under Review      │  🤖 Safety: 97% confidence   │   │
│  │  💰 Pay App #5 - Ready to Submit       │  🤖 Accounts: 99% confidence │   │
│  │  📸 Final Inspection Due in 3 Days     │                              │   │
│  │                                        │  ⚠️ 1 task paused            │   │
│  └────────────────────────────────────────┴──────────────────────────────┘   │
│                                                                              │
│  ┌─ QUICK ACTIONS ──────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  [+ Daily Report]  [+ RFI]  [+ CO]  [+ T&M]  [+ Photo]  [🎤 Voice]  │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ROOFIO SSOT DATA FLOW                                  │
│                       ════════════════════                                  │
│                                                                              │
│                         ┌────────────────┐                                  │
│                         │    ESTIMATE    │  ◄── Data enters ONCE            │
│                         │  (Source Data) │                                  │
│                         └───────┬────────┘                                  │
│                                 │                                           │
│        ┌────────────────────────┼────────────────────────┐                  │
│        │                        │                        │                  │
│        ▼                        ▼                        ▼                  │
│  ┌───────────┐           ┌───────────┐           ┌───────────┐             │
│  │    SOV    │           │SUBMITTALS │           │    JHA    │             │
│  │(Accounts) │           │   (PM)    │           │ (Safety)  │             │
│  └─────┬─────┘           └─────┬─────┘           └─────┬─────┘             │
│        │                       │                       │                   │
│        │    ┌──────────────────┼──────────────────┐    │                   │
│        │    │                  │                  │    │                   │
│        ▼    ▼                  ▼                  ▼    ▼                   │
│  ┌───────────┐           ┌───────────┐           ┌───────────┐             │
│  │  PAY APP  │           │    QC     │           │  ORDERS   │             │
│  │ (G702/703)│           │CHECKLISTS │           │  (Supt)   │             │
│  └─────┬─────┘           └─────┬─────┘           └───────────┘             │
│        │                       │                                           │
│        │                       │                                           │
│        ▼                       ▼                                           │
│  ┌───────────┐           ┌───────────┐                                     │
│  │   LIEN    │           │  WARRANTY │                                     │
│  │  WAIVER   │           │   APPS    │                                     │
│  └───────────┘           └───────────┘                                     │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│  KEY: Data flows automatically. Change in source = update in all children.  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PART 4: AI MODE SPECIFICATIONS

### 4.1 Full AI Mode (Agent) - Complete Function Map

```
POSITION: ESTIMATOR - FULL AI 🤖
═════════════════════════════════

AUTOMATED FUNCTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER                          │  AI ACTION                   │ CONF.   │
├───────────────────────────────────┼──────────────────────────────┼─────────┤
│  Plans uploaded                   │  Auto-takeoff measurements   │  95%+   │
│  Takeoff complete                 │  Generate BOM from products  │  98%    │
│  BOM generated                    │  Calculate labor hours       │  90%    │
│  All costs calculated             │  Apply margin, generate bid  │  95%    │
│  Insurance claim identified       │  Generate supplement request │  85%*   │
│  Estimate finalized               │  Update margin analyzer      │  99%    │
└─────────────────────────────────────────────────────────────────────────────┘
* May require human review - insurance claims often have ambiguity

OUTPUT: Complete bid package ready for review/send


POSITION: PROJECT MANAGER - FULL AI 🤖
══════════════════════════════════════

AUTOMATED FUNCTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER                          │  AI ACTION                   │ CONF.   │
├───────────────────────────────────┼──────────────────────────────┼─────────┤
│  Estimate approved                │  Generate submittal log      │  99%    │
│  Submittal due in 7 days          │  Draft reminder email        │  98%    │
│  Submittal overdue                │  Escalate, log delay         │  95%    │
│  RFI response received            │  Log, check for cost impact  │  90%    │
│  RFI has cost impact              │  Draft change order          │  75%*   │
│  Municipality selected            │  Generate permit application │  92%    │
│  Meeting scheduled                │  Prepare agenda, attendees   │  95%    │
│  Monthly billing period ends      │  Generate pay app draft      │  97%    │
└─────────────────────────────────────────────────────────────────────────────┘
* RFI cost impacts often ambiguous - likely to pause for human review


POSITION: SAFETY OFFICER - FULL AI 🤖
═════════════════════════════════════

AUTOMATED FUNCTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER                          │  AI ACTION                   │ CONF.   │
├───────────────────────────────────┼──────────────────────────────┼─────────┤
│  Job created with materials       │  Generate JHA from products  │  95%    │
│  Materials include adhesives      │  Add chemical hazards to JHA │  98%    │
│  Scope includes tile cutting      │  Generate Silica Control Plan│  97%    │
│  Scope includes torch work        │  Queue Hot Work Permit       │  95%    │
│  Scope includes roof loading      │  Queue Crane Lift Plan       │  80%*   │
│  Weekly schedule                  │  Generate Toolbox Talk topic │  99%    │
│  Crew assigned                    │  Verify certifications       │  95%    │
│  Incident reported                │  Draft OSHA 300 entry        │  70%*   │
└─────────────────────────────────────────────────────────────────────────────┘
* Lift plans and incidents require human judgment


POSITION: ACCOUNTS - FULL AI 🤖
═══════════════════════════════

AUTOMATED FUNCTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER                          │  AI ACTION                   │ CONF.   │
├───────────────────────────────────┼──────────────────────────────┼─────────┤
│  Estimate approved                │  Create SOV from line items  │  99%    │
│  Daily reports logged             │  Update SOV percentages      │  95%    │
│  Stored materials received        │  Add to SOV stored column    │  98%    │
│  Monthly billing period ends      │  Generate G702/G703          │  97%    │
│  Pay app approved                 │  Generate Conditional Waiver │  99%    │
│  Payment received                 │  Generate Unconditional Wvr  │  99%    │
│  Sub invoice received             │  Match to PO, queue payment  │  90%    │
│  Project complete                 │  Generate closeout package   │  95%    │
│  Daily + estimate data            │  Update job cost report      │  98%    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Assist Mode (Copilot) - One-Click Actions

```
POSITION: SUPERINTENDENT - ASSIST MODE 🧑‍💼
════════════════════════════════════════════

ONE-CLICK ACTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  USER ACTION                      │  AI RESPONSE                            │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Tap [+ Daily Report]             │  Pre-fill: project, date, weather API, │
│                                   │  yesterday's crew + equipment.          │
│                                   │  User adds: work description, notes.    │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Tap [+ Stored Material]          │  Show expected deliveries, match to PO, │
│                                   │  log location (roof/ground), quantity.  │
│                                   │  Auto-updates SOV stored materials.     │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Tap [🎤 Voice Note]              │  Transcribe, detect form type:          │
│                                   │  "Sounds like a T&M ticket. Create?"    │
│                                   │  Pre-fill detected info, user confirms. │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Tap [2-Week Lookahead]           │  Auto-generate from master schedule,    │
│                                   │  flag conflicts, suggest crew assign.   │
│                                   │  User adjusts and approves.             │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Upload Photo                     │  Auto-tag: date, location, uploader.    │
│                                   │  "Add to Daily Report?" "Tag defect?"   │
└─────────────────────────────────────────────────────────────────────────────┘

SMART SUGGESTIONS (Proactive, Not Auto-Executed):
• "Rain forecast tomorrow. Draft weather delay notice?"
• "Yesterday's T&M ticket wasn't submitted. Reminder?"
• "Material delivery due today. Update receiving log?"


POSITION: QC / INSPECTOR - ASSIST MODE 🧑‍💼
═══════════════════════════════════════════

ONE-CLICK ACTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  USER ACTION                      │  AI RESPONSE                            │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Start Inspection                 │  Load checklist for THIS system type.   │
│                                   │  (TPO FA → Seam probes, substrate, etc) │
│                                   │  Photo prompts at each checkpoint.      │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Log Moisture Reading             │  Pre-fill: location, equipment type,    │
│                                   │  reading scale. Map to roof zones.      │
│                                   │  Auto-generate moisture analysis report.│
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Mark Deficiency                  │  Photo required. Spec reference lookup. │
│                                   │  Auto-add to punch list.                │
│                                   │  Assign to crew member dropdown.        │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  Log Penetration                  │  Drawing reference, type (curb/pipe/    │
│                                   │  HVAC), flashing detail used.           │
│                                   │  Auto-populates penetration log.        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PART 5: IMPLEMENTATION ROADMAP

### Phase 1: SSOT Foundation (Weeks 1-2)
```
□ Database schema (PostgreSQL/Supabase)
□ Core entities: Company, Project, Estimate, Job, Contact, Employee, Product
□ SSOT propagation engine (data flows from estimate to all children)
□ Authentication & multi-tenancy
□ Basic CRUD APIs with cascade updates
```

### Phase 2: Core Forms + Pre-fill (Weeks 3-4)
```
□ Form engine with SSOT pre-fill logic
□ RFI form + auto-routing
□ Submittal form + log (auto-generated from estimate)
□ Change Order form + margin impact
□ SOV auto-generation from estimate
□ Pay Application (G702/G703) calculator
□ PDF export for all forms
```

### Phase 3: AI Confidence System (Week 5)
```
□ Confidence scoring algorithm
□ Auto-pause triggers at 90% threshold
□ Human review queue
□ Activity logging for all AI actions
□ Confidence analytics dashboard
```

### Phase 4: Daily Operations + Voice (Weeks 6-7)
```
□ Daily Report form + photo integration + weather API
□ T&M Ticket form with voice-to-text
□ Stored Material Log (links to SOV)
□ 2-Week Lookahead generator
□ Crew Assignment with certification check
```

### Phase 5: Safety Compliance (Week 8)
```
□ JHA auto-generation from products/hazards
□ Toolbox Talk topic library + generator
□ Silica Exposure Control Plan (auto from scope)
□ Hot Work Permit form
□ Crane/Hoist Lift Plan form
□ Incident Report + OSHA 300 entry
```

### Phase 6: Insurance & Specialty (Week 9)
```
□ Insurance Supplement Request form
□ Permit Application auto-fill (municipality data)
□ Manufacturer Warranty Application (Carlisle, Firestone, GAF templates)
□ Moisture Analysis Report
□ Roof Penetration Log
□ As-Built Drawing Overlay system
```

### Phase 7: Accounts & Closeout (Week 10)
```
□ Profit/Margin Analyzer (live estimate vs actual)
□ Job Cost Report
□ Lien Waiver generator (conditional/unconditional)
□ Closeout document tracker
□ Notice of Completion
□ Warranty letter generator
```

### Phase 8: Polish & Mobile (Weeks 11-12)
```
□ Mobile-responsive all forms
□ Offline capability for field use
□ Voice-to-text integration (Whisper API)
□ Photo annotation tools
□ Push notifications
□ Mode toggle UI refinement
□ Confidence threshold configuration
```

---

## PART 6: TECH STACK RECOMMENDATION

```
RECOMMENDED STACK
═════════════════

FRONTEND:
├─ Next.js 14 (App Router)
├─ Tailwind CSS + shadcn/ui
├─ React Hook Form (form state with SSOT pre-fill)
├─ TanStack Query (data fetching + cache invalidation)
└─ Zustand (global state for mode toggles)

BACKEND:
├─ Supabase (PostgreSQL + Auth + Storage + Realtime)
│   └─ Row Level Security for multi-tenancy
├─ Edge Functions (serverless logic)
├─ Database triggers for SSOT cascade updates
└─ Anthropic API (Claude for AI features)

CONFIDENCE SYSTEM:
├─ Custom scoring algorithm (TypeScript)
├─ Factors: data completeness, consistency, historical accuracy
├─ Threshold configurable per company (default 90%)
└─ Pause/resume queue with human review workflow

MOBILE:
├─ React Native + Expo
├─ Or: Progressive Web App (PWA) with offline-first
├─ Camera integration for photos
└─ Voice: Whisper API or native speech-to-text

PDF GENERATION:
├─ react-pdf/renderer (client-side)
├─ AIA G702/G703 templates
├─ Manufacturer warranty form templates
└─ Company branding customization

INTEGRATIONS:
├─ Weather: OpenWeatherMap API (auto-fetch for daily reports)
├─ Accounting: QuickBooks API (invoices, payments)
├─ Measurements: EagleView API (aerial takeoffs)
├─ Municipality: Manual database or API where available
└─ Manufacturers: Carlisle, Firestone, GAF warranty portals
```

---

## PART 7: FORM FIELD MAPPINGS (SSOT Pre-fill)

### Example: Pay Application G702 (Full SSOT Chain)

```json
{
  "form": "G702_Pay_Application",
  "ssot_chain": [
    "estimate → sov → daily_reports → pay_app"
  ],
  "fields": [
    {
      "name": "original_contract_sum",
      "source": "job.original_amount",
      "origin": "estimate.total (when estimate approved)",
      "editable": false
    },
    {
      "name": "change_orders_approved",
      "source": "sum(job.change_orders where status=approved)",
      "origin": "change_orders created from RFIs or manual",
      "editable": false
    },
    {
      "name": "total_completed_stored",
      "source": "sum(sov.total_completed + sov.materials_stored)",
      "origin": "daily_reports.percent_complete + stored_material_log",
      "editable": false
    },
    {
      "name": "materials_stored",
      "source": "sum(stored_material_log where location != 'installed')",
      "origin": "superintendent.stored_material_log entries",
      "editable": false
    },
    {
      "name": "retainage",
      "source": "calculated: total_completed * job.retainage_rate",
      "origin": "retainage_rate from contract",
      "editable": false
    },
    {
      "name": "less_previous_payments",
      "source": "sum(previous_pay_apps.amount_paid)",
      "origin": "prior pay apps marked as paid",
      "editable": false
    },
    {
      "name": "current_payment_due",
      "source": "calculated: (total_earned - retainage) - less_previous",
      "editable": false
    }
  ]
}
```

### Example: JHA Auto-Generation from Products

```json
{
  "form": "JHA_Job_Hazard_Analysis",
  "ssot_chain": [
    "estimate.products → products.hazards → jha"
  ],
  "auto_populate": {
    "trigger": "job created with estimate",
    "logic": [
      {
        "if": "products contain adhesives",
        "add_hazard": {
          "hazard": "Chemical exposure - adhesive fumes",
          "control": "Adequate ventilation, respirator with organic vapor cartridge",
          "ppe": ["Respirator", "Chemical resistant gloves", "Safety glasses"]
        }
      },
      {
        "if": "products contain hot-applied materials",
        "add_hazard": {
          "hazard": "Burn hazard - hot asphalt/modified bitumen",
          "control": "Kettle safety procedures, fire extinguisher on-site",
          "ppe": ["Heat-resistant gloves", "Face shield", "Long sleeves"]
        }
      },
      {
        "if": "scope includes tile cutting",
        "add_hazard": {
          "hazard": "Silica dust exposure",
          "control": "Wet cutting methods, dust collection, Silica Control Plan",
          "ppe": ["N95 or P100 respirator", "Safety glasses"]
        },
        "also_generate": "Silica_Exposure_Control_Plan"
      },
      {
        "if": "job.height > 6ft",
        "add_hazard": {
          "hazard": "Fall hazard",
          "control": "Fall protection plan, warning lines, personal fall arrest",
          "ppe": ["Full body harness", "Lanyard", "Anchor point"]
        }
      }
    ]
  }
}
```

---

## APPENDIX A: NEW FORM SPECIFICATIONS

### Insurance Supplement Request [NEW]
```
PURPOSE: Document missed items/code upgrades for insurance adjusters
TRIGGERS: When project.is_insurance_claim = true AND missed items identified

PRE-FILL FROM:
├── Original estimate data
├── Claim number, policy number
├── Adjuster contact
└── Code requirements for jurisdiction

FIELDS:
├── original_estimate_total
├── missed_items[] (line items not in original scope)
├── code_upgrades[] (required by current code, not original)
├── documentation (photos, code references)
├── supplement_amount_requested
└── adjuster_notes

OUTPUT: PDF formatted for insurance company submission
```

### Profit/Margin Analyzer [NEW]
```
PURPOSE: Live breakdown of labor/material/overhead vs actual
TRIGGERS: Auto-updates on any cost entry

DATA SOURCES (SSOT):
├── Estimated: estimate.labor_total, estimate.material_total
├── Actual labor: sum(daily_reports.hours * employee.rate)
├── Actual materials: sum(material_receiving_log.amount)
└── Change orders: sum(change_orders.labor + materials)

CALCULATIONS:
├── estimated_margin = (contract - costs) / contract
├── current_margin = (billed - actual_costs) / billed
├── labor_variance = actual_labor - estimated_labor
├── material_variance = actual_material - estimated_material
└── projected_final_margin (based on percent complete)

DISPLAY: Dashboard widget + exportable report
```

### Manufacturer Warranty Application [NEW]
```
PURPOSE: Pre-fill NDL/warranty forms for Carlisle, Firestone, GAF, etc.
TRIGGERS: When job.warranty_type is set and closeout begins

PRE-FILL FROM (SSOT):
├── Project info (address, owner, size)
├── Products installed (from estimate)
├── Installation dates (from daily reports)
├── Installer certifications (from employees)
├── Inspection records (from QC)
└── Photo documentation

MANUFACTURER TEMPLATES:
├── Carlisle SynTec - NDL/Platinum warranty
├── Firestone - Red Shield/Diamond Shield
├── GAF - Golden Pledge/System Plus
├── Johns Manville - Peak Advantage
└── Custom template builder

OUTPUT: Completed PDF ready for manufacturer submission
```

### Stored Material Log [NEW]
```
PURPOSE: Track material on roof vs ground for accurate billing
LINKS TO: SOV.materials_stored, Pay Application

FIELDS:
├── date_received
├── material (from products)
├── quantity
├── location (ground, roof area A, roof area B, etc.)
├── po_reference
├── photo_documentation
└── status (stored, installed, returned)

SSOT UPDATES:
├── When added: SOV.materials_stored increases
├── When installed: SOV.work_completed increases, stored decreases
└── Pay App reflects current stored value
```

---

**END OF SPECIFICATION**

*This document is ready for Claude Code implementation.*
*Version 2.0 FINAL - December 2025*
*Prepared for: Lefebvre Design Solutions / Roofio*

---

## SUMMARY OF CHANGES FROM V1

| Category | Change |
|----------|--------|
| Data Architecture | Added Unified Project Object (UPO) concept |
| Data Architecture | Added Confidence Switch (90% threshold) |
| Forms | +12 new forms (74 total, up from 61) |
| Estimator | +Insurance Supplement, +Margin Analyzer |
| PM | +Permit Application Packet |
| Detailer | +As-Built Drawing Overlay |
| Spec Writer | +Manufacturer Warranty Application |
| QC | +Moisture Analysis, +Penetration Log |
| Safety | +Silica Control, +Crane Lift Plan |
| Superintendent | +Stored Material Log |
| Accounts | +SOV form, +Job Cost Report |
| AI System | Added confidence scoring algorithm |
| AI System | Added auto-pause mechanism |
| UI | Added confidence display in badges |
| UI | Added AI activity summary |
