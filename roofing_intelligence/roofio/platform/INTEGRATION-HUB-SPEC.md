# ROOFIO Integration Hub
## The "Trojan Horse" Super-Plugin Strategy

**Version:** 1.0
**Date:** December 2025
**Philosophy:** "We play nice with your current tools."

---

## THE CORE INSIGHT

> "People don't like change."

**The Wrong Approach:** "Throw away your current system and use ours."
**The Right Approach:** "Keep your current messy system—we just fix the one part you hate."

ROOFIO is NOT a replacement platform. It's a **Super-Plugin** that cleans up their existing mess.

---

## THE "LAND AND EXPAND" PSYCHOLOGY

### Phase 1: LAND (Single Pain Point)

A contractor discovers ROOFIO because they need ONE thing:

| Pain Point | What They Buy | The Hook |
|------------|---------------|----------|
| Weather delay disputes | Weather Truth Agent | "Never lose another weather claim" |
| OSHA crackdowns | JHA Gatekeeper | "Prove safety compliance instantly" |
| Insurance claims | Photo Chain of Custody | "GPS-stamped, hash-verified photos" |
| Silica regulations | Silica Tracker | "OSHA compliance documentation" |
| Scattered files | Magic Folder Sync | "Your photos, organized automatically" |

**Critical:** It works immediately because it connects to what they already use.

### Phase 2: EXPAND (Natural Discovery)

As they use that one feature, they discover more:
- "Oh, this syncs to my Dropbox? Nice."
- "Wait, it can also track my materials?"
- "My QuickBooks already has these job codes?"
- "The AI flagged a safety issue in my photo?"

**The platform grows WITH them—not against them.**

### Marketing Language

❌ DON'T SAY: "Integration" / "Platform Migration" / "Replace your tools"
✅ DO SAY: "We play nice with your current tools"

- "Keep your Dropbox."
- "Keep your QuickBooks."
- "We just connect the field to the office so you don't have to chase paperwork."

---

## THE FOUR KILLER INTEGRATIONS

These are the "Trojan Horses" that get ROOFIO into every contractor's workflow.

---

### 🗂️ 1. THE "MAGIC FOLDER" (Dropbox / Google Drive / OneDrive)

**The Problem:** Contractors have files scattered everywhere. They hate uploading things manually.

**The ROOFIO Solution:** Automatic folder structure + one-way sync.

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAGIC FOLDER SYNC                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  USER ACTION:                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Foreman takes photo in Digital Foreman app             │    │
│  │  📸 → [CAPTURE] → GPS tagged, timestamped               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ROOFIO AUTO-MAGIC:                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Photo uploaded to THEIR existing cloud storage:        │    │
│  │                                                          │    │
│  │  📁 Dropbox/                                             │    │
│  │  └── 📁 Projects/                                        │    │
│  │      └── 📁 2025/                                        │    │
│  │          └── 📁 UMass-Waterproofing/                     │    │
│  │              └── 📁 Photos/                              │    │
│  │                  └── 📁 Daily-Logs/                      │    │
│  │                      └── 📸 2025-12-07_1423_roof-deck.jpg│    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  PSYCHOLOGICAL BENEFIT:                                          │
│  Owner feels SAFE because they "own" their data on THEIR drive │
│  But they USE your app because it ORGANIZES it for them         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Folder Structure Auto-Created

When user connects ROOFIO to their cloud storage, we create:

```
📁 {Company}/Projects/{Year}/{Job-Number}/
├── 📁 Photos/
│   ├── 📁 Daily-Logs/
│   ├── 📁 Safety/
│   ├── 📁 Progress/
│   └── 📁 Issues/
├── 📁 Documents/
│   ├── 📁 Submittals/
│   ├── 📁 RFIs/
│   ├── 📁 Change-Orders/
│   └── 📁 Contracts/
├── 📁 Reports/
│   ├── 📁 Daily-Logs/
│   ├── 📁 Weather/
│   └── 📁 Safety-JHAs/
└── 📁 Correspondence/
    └── 📁 Emails/
```

#### Technical Implementation

```typescript
// services/integrations/magic-folder.ts

interface MagicFolderConfig {
  provider: 'dropbox' | 'google_drive' | 'onedrive' | 'box';
  rootPath: string;
  projectId: string;
  syncRules: SyncRule[];
}

interface SyncRule {
  roofioPath: string;      // e.g., "/photos/daily"
  cloudPath: string;       // e.g., "/Photos/Daily-Logs"
  direction: 'push' | 'pull' | 'bidirectional';
  fileTypes: string[];     // e.g., ["jpg", "png", "pdf"]
  preserveMetadata: boolean;
}

// Event-driven sync
class MagicFolderService {

  async onPhotoUploaded(event: PhotoUploadedEvent) {
    const config = await this.getUserConfig(event.userId);

    if (!config.syncEnabled) return;

    // Build cloud path
    const cloudPath = this.buildPath(config, {
      year: event.timestamp.getFullYear(),
      jobNumber: event.project.jobNumber,
      category: this.categorizePhoto(event.photo),
      filename: this.buildFilename(event)
    });

    // Queue for async upload (never block the app)
    await this.syncQueue.add('upload', {
      provider: config.provider,
      localFile: event.photo.path,
      remotePath: cloudPath,
      metadata: {
        gps: event.photo.gps,
        timestamp: event.timestamp,
        capturedBy: event.userId,
        hash: event.photo.sha256
      }
    });
  }

  buildFilename(event: PhotoUploadedEvent): string {
    // 2025-12-07_1423_roof-deck_johndoe.jpg
    const date = format(event.timestamp, 'yyyy-MM-dd');
    const time = format(event.timestamp, 'HHmm');
    const desc = slugify(event.photo.description || 'photo');
    const user = event.user.lastName.toLowerCase();
    return `${date}_${time}_${desc}_${user}.jpg`;
  }
}
```

#### Supported Providers

| Provider | API | Auth | Real-time Sync |
|----------|-----|------|----------------|
| Dropbox | Dropbox API v2 | OAuth 2.0 | Webhooks ✓ |
| Google Drive | Drive API v3 | OAuth 2.0 | Push Notifications ✓ |
| OneDrive | Microsoft Graph | OAuth 2.0 | Webhooks ✓ |
| Box | Box Platform | OAuth 2.0 | Webhooks ✓ |
| SharePoint | Microsoft Graph | OAuth 2.0 | Webhooks ✓ |

---

### 📧 2. THE EMAIL "SIDECAR" (Outlook / Gmail Plugin)

**The Problem:** 80% of construction management happens in messy email threads. Important approvals get lost.

**The ROOFIO Solution:** A browser extension / Outlook Add-in with one magic button.

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL SIDECAR                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  OUTLOOK / GMAIL                                         │    │
│  │  ─────────────────────────────────────────────────────   │    │
│  │  From: john@acmeroofing.com                              │    │
│  │  Subject: RE: UMass Change Order #7 - APPROVED           │    │
│  │                                                          │    │
│  │  "Yes, approved. Go ahead with the additional           │    │
│  │   flashing at $4,200. See attached signed CO."          │    │
│  │                                                          │    │
│  │   📎 CO-007-signed.pdf                                   │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────┐                │    │
│  │  │  🔵 ROOFIO  │ [Save to Job ▼]        │  ← MAGIC BUTTON│    │
│  │  │             │ UMass Waterproofing    │                │    │
│  │  │             │ └── Change Orders      │                │    │
│  │  └──────────────────────────────────────┘                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  AI EXTRACTION:                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • Detected: Change Order Approval                       │    │
│  │  • Amount: $4,200                                        │    │
│  │  • Approved by: John Smith                               │    │
│  │  • Attachment: CO-007-signed.pdf                         │    │
│  │                                                          │    │
│  │  → Filed to: UMass Waterproofing > Approvals > CO-007   │    │
│  │  → Linked to: Change Event #7 in Project Manager        │    │
│  │  → Status updated: APPROVED                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### AI Email Intelligence

```typescript
// services/integrations/email-sidecar.ts

interface EmailAnalysis {
  documentType: 'approval' | 'rfi' | 'submittal' | 'change_order' |
                'meeting_notes' | 'general';
  extractedData: {
    amounts?: number[];
    dates?: Date[];
    approver?: string;
    status?: 'approved' | 'rejected' | 'pending';
    references?: string[];  // "CO-007", "RFI-23", etc.
  };
  suggestedProject: Project | null;
  suggestedFolder: string;
  confidence: number;
}

class EmailSidecarService {

  async analyzeEmail(email: Email): Promise<EmailAnalysis> {
    // Extract structured data using AI
    const analysis = await this.ai.analyze({
      subject: email.subject,
      body: email.body,
      attachments: email.attachments.map(a => a.filename),
      from: email.from,
      thread: email.threadHistory
    });

    // Match to existing project
    const project = await this.matchProject(email, analysis);

    return {
      documentType: analysis.type,
      extractedData: analysis.extracted,
      suggestedProject: project,
      suggestedFolder: this.suggestFolder(analysis.type),
      confidence: analysis.confidence
    };
  }

  async saveToProject(email: Email, projectId: string, folder: string) {
    // 1. Save email content as record
    const record = await this.createEmailRecord(email, projectId);

    // 2. Upload attachments to Magic Folder
    for (const attachment of email.attachments) {
      await this.magicFolder.upload(attachment, {
        project: projectId,
        folder: folder,
        source: 'email',
        emailId: record.id
      });
    }

    // 3. Update related records (if change order, RFI, etc.)
    if (record.extractedData.references) {
      await this.linkToExistingRecords(record);
    }

    // 4. Notify team if needed
    await this.notifyTeam(record);
  }
}
```

#### Browser Extension Manifest

```json
// chrome-extension/manifest.json
{
  "manifest_version": 3,
  "name": "ROOFIO Email Sidecar",
  "version": "1.0.0",
  "description": "Save construction emails to your ROOFIO projects",
  "permissions": ["activeTab", "storage"],
  "host_permissions": [
    "https://mail.google.com/*",
    "https://outlook.office.com/*",
    "https://outlook.live.com/*"
  ],
  "content_scripts": [
    {
      "matches": [
        "https://mail.google.com/*",
        "https://outlook.office.com/*"
      ],
      "js": ["content.js"],
      "css": ["sidecar.css"]
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icons/roofio-48.png"
  }
}
```

---

### 💰 3. THE "GET PAID FASTER" LINK (QuickBooks / Xero / Sage)

**The Problem:** Field crew does work, but the office doesn't bill until weeks later because paperwork is slow.

**The ROOFIO Solution:** Live "Percent Complete" sync → Ready to Bill triggers.

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                GET PAID FASTER FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FIELD (Digital Foreman App):                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  📋 Phase: Roof Tear-Off                                 │    │
│  │                                                          │    │
│  │  Progress: ████████████████████░░░░ 85%                  │    │
│  │           ─────────────────────────►                     │    │
│  │           [Slide to update]                              │    │
│  │                                                          │    │
│  │  📸 Progress photos attached: 4                          │    │
│  │  ✅ Daily log complete                                   │    │
│  │                                                          │    │
│  │  [Mark 100% Complete]                                    │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼ Foreman slides to 100%               │
│                                                                  │
│  ROOFIO TRIGGERS:                                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  1. Update project phase status                          │    │
│  │  2. Compile progress photos as documentation             │    │
│  │  3. Push to QuickBooks: "Ready to Bill" flag             │    │
│  │  4. Draft AIA G702/G703 pay app                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  OFFICE (QuickBooks):                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  🔔 READY TO BILL                                        │    │
│  │                                                          │    │
│  │  Job: UMass Waterproofing                                │    │
│  │  Phase: Roof Tear-Off                                    │    │
│  │  Amount: $45,000                                         │    │
│  │  Status: 100% Complete (field verified)                  │    │
│  │                                                          │    │
│  │  📎 Documentation attached:                              │    │
│  │     • 4 progress photos (GPS verified)                   │    │
│  │     • Daily log excerpt                                  │    │
│  │     • Foreman signature                                  │    │
│  │                                                          │    │
│  │  [Create Invoice] [View Details]                         │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  WHY THEY BUY IT: Improves cash flow IMMEDIATELY                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### QuickBooks Integration

```typescript
// services/integrations/quickbooks.ts

interface QuickBooksConfig {
  realmId: string;          // QB company ID
  accessToken: string;
  refreshToken: string;
  syncSettings: {
    pullJobCodes: boolean;
    pullCustomers: boolean;
    pullVendors: boolean;
    pushTimeEntries: boolean;
    pushExpenses: boolean;
    pushReadyToBill: boolean;
  };
}

class QuickBooksService {

  // PULL: Import job codes from QuickBooks (so users don't re-enter)
  async importJobCodes(config: QuickBooksConfig): Promise<JobCode[]> {
    const response = await this.qb.query(
      `SELECT * FROM Item WHERE Type = 'Service'`,
      config
    );

    return response.Items.map(item => ({
      externalId: item.Id,
      code: item.Name,
      description: item.Description,
      rate: item.UnitPrice,
      source: 'quickbooks'
    }));
  }

  // PUSH: Send "Ready to Bill" when phase completes
  async pushReadyToBill(phase: ProjectPhase, photos: Photo[]) {
    const project = await this.getProject(phase.projectId);
    const qbJob = await this.getLinkedQBJob(project);

    // Create a "bill later" invoice or sales receipt
    const invoice = {
      CustomerRef: { value: qbJob.customerId },
      Line: [{
        Amount: phase.contractAmount,
        Description: `${phase.name} - 100% Complete`,
        DetailType: 'SalesItemLineDetail',
        SalesItemLineDetail: {
          ItemRef: { value: phase.jobCodeId },
          Qty: 1,
          UnitPrice: phase.contractAmount
        }
      }],
      CustomField: [{
        Name: 'ROOFIO Phase ID',
        StringValue: phase.id
      }],
      PrivateNote: `Auto-generated by ROOFIO. Photos: ${photos.length}`,
      // Attach documentation
      Attachments: await this.createAttachments(photos)
    };

    // Create as draft (not sent)
    const result = await this.qb.createInvoice(invoice, { draft: true });

    // Notify office
    await this.notifications.send({
      type: 'ready_to_bill',
      project: project,
      phase: phase,
      invoice: result,
      recipients: project.officeContacts
    });
  }

  // PUSH: Daily time entries to payroll
  async syncTimeEntries(dailyLog: DailyLog) {
    for (const labor of dailyLog.laborEntries) {
      await this.qb.createTimeActivity({
        EmployeeRef: { value: labor.employee.qbId },
        ItemRef: { value: labor.jobCode.qbId },
        Hours: labor.hours,
        Description: `${dailyLog.project.name} - ${dailyLog.date}`,
        TxnDate: dailyLog.date
      });
    }
  }
}
```

#### Data Flow Summary

| Direction | From | To | Data |
|-----------|------|-----|------|
| PULL | QuickBooks | ROOFIO | Jobs, Customers, Vendors, Cost Codes |
| PUSH | ROOFIO | QuickBooks | Time Entries, Expenses, Ready-to-Bill Flags |
| PUSH | ROOFIO | QuickBooks | Progress photos as invoice attachments |

---

### 📷 4. THE "VISUAL PROOF" HOOK (CompanyCam / EagleView)

**The Problem:** Roofers already love CompanyCam. You can't fight them—you must join them.

**The ROOFIO Solution:** Two-way sync + AI intelligence layer on top.

#### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│              VISUAL PROOF AI LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  They prefer taking photos in CompanyCam? LET THEM.             │
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────┐                 │
│  │   COMPANYCAM     │      │     ROOFIO       │                 │
│  │   (Photo App)    │ ───► │   (AI Brain)     │                 │
│  │                  │      │                  │                 │
│  │  📸 Dumb storage │      │  🧠 Smart analysis│                │
│  └──────────────────┘      └──────────────────┘                 │
│                                   │                              │
│                                   ▼                              │
│  AI ANALYSIS:                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  📸 Photo uploaded from CompanyCam sync                  │    │
│  │                                                          │    │
│  │  🤖 AI Detection:                                        │    │
│  │     ⚠️ SAFETY ISSUE DETECTED                             │    │
│  │     "Worker on roof without fall protection visible"     │    │
│  │     Confidence: 87%                                      │    │
│  │                                                          │    │
│  │     📍 PROGRESS TRACKING                                 │    │
│  │     "Membrane installation ~60% complete"                │    │
│  │     "3 rolls visible in staging area"                    │    │
│  │                                                          │    │
│  │     🔧 MATERIAL VERIFICATION                             │    │
│  │     "Detected: Carlisle TPO (matches submittal)"         │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  VALUE ADD: You add INTELLIGENCE on top of their DUMB STORAGE   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### CompanyCam Integration

```typescript
// services/integrations/companycam.ts

class CompanyCamService {

  // Webhook receiver: CompanyCam sends us new photos
  async onPhotoCreated(webhook: CompanyCamWebhook) {
    const photo = webhook.photo;

    // 1. Match to ROOFIO project
    const project = await this.matchProject(photo.project_name);

    // 2. Download photo
    const imageData = await this.downloadPhoto(photo.urls.original);

    // 3. Preserve their metadata + add ours
    const enrichedPhoto = {
      externalId: photo.id,
      source: 'companycam',
      originalUrl: photo.urls.original,
      capturedAt: photo.captured_at,
      capturedBy: photo.creator.name,
      gps: {
        lat: photo.lat,
        lng: photo.lng
      },
      // Add ROOFIO chain of custody
      importedAt: new Date(),
      sha256: await this.hashImage(imageData)
    };

    // 4. Run AI analysis
    const analysis = await this.aiService.analyzePhoto(imageData, {
      projectContext: project,
      lookFor: ['safety_issues', 'progress', 'materials', 'defects']
    });

    // 5. Create alerts if issues found
    if (analysis.safetyIssues.length > 0) {
      await this.createSafetyAlert(project, photo, analysis.safetyIssues);
    }

    // 6. Update progress tracking if detected
    if (analysis.progressEstimate) {
      await this.updatePhaseProgress(project, analysis.progressEstimate);
    }

    // 7. Save to ROOFIO + sync to Magic Folder
    await this.savePhoto(enrichedPhoto, analysis);
  }
}
```

#### EagleView Integration

```typescript
// services/integrations/eagleview.ts

class EagleViewService {

  // Pull measurement reports
  async importMeasurementReport(orderId: string, projectId: string) {
    const report = await this.eagleview.getReport(orderId);

    // Extract key measurements
    const measurements = {
      totalRoofArea: report.roof_total_area,
      pitches: report.pitches,
      facets: report.facets,
      ridges: report.ridge_length,
      valleys: report.valley_length,
      eaves: report.eave_length,
      rakes: report.rake_length,
      hips: report.hip_length,
      flashings: report.flashing_length,
      // Waste factor calculation
      complexity: report.complexity_rating,
      suggestedWaste: this.calculateWaste(report.complexity_rating)
    };

    // Link to project
    await this.projects.addMeasurements(projectId, measurements);

    // Generate material takeoff
    const takeoff = await this.generateTakeoff(measurements, projectId);

    return { measurements, takeoff };
  }
}
```

---

## TECHNICAL ARCHITECTURE

### The Integration Hub (Middleware)

```
┌─────────────────────────────────────────────────────────────────┐
│                   ROOFIO INTEGRATION HUB                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 INTEGRATION MANAGER                      │    │
│  │                 (OAuth2 Orchestrator)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│           ┌───────────────┼───────────────┐                     │
│           ▼               ▼               ▼                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  CONNECTOR  │ │  CONNECTOR  │ │  CONNECTOR  │               │
│  │   SERVICE   │ │   SERVICE   │ │   SERVICE   │               │
│  │  (Storage)  │ │   (Email)   │ │ (Financial) │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SYNC AGENT                            │    │
│  │              (Redis/BullMQ Job Queue)                    │    │
│  │                                                          │    │
│  │   Event-Driven: Never blocks the app                     │    │
│  │   Retry Logic: Exponential backoff                       │    │
│  │   Offline Queue: Syncs when connected                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    DATA MAPPER                           │    │
│  │              (JSON Schema Translator)                    │    │
│  │                                                          │    │
│  │   ROOFIO Object ←→ External Format                       │    │
│  │   Daily_Log (JSON) → PDF → Email Attachment              │    │
│  │   Photo (ROOFIO) → EXIF preserved → Cloud Storage        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Services

```typescript
// services/integrations/integration-manager.ts

interface IntegrationProvider {
  id: string;
  name: string;
  category: 'storage' | 'email' | 'financial' | 'photo' | 'pm';
  authType: 'oauth2' | 'api_key' | 'webhook';
  status: 'active' | 'coming_soon' | 'beta';
}

const SUPPORTED_PROVIDERS: IntegrationProvider[] = [
  // STORAGE
  { id: 'dropbox', name: 'Dropbox', category: 'storage', authType: 'oauth2', status: 'active' },
  { id: 'google_drive', name: 'Google Drive', category: 'storage', authType: 'oauth2', status: 'active' },
  { id: 'onedrive', name: 'OneDrive', category: 'storage', authType: 'oauth2', status: 'active' },
  { id: 'box', name: 'Box', category: 'storage', authType: 'oauth2', status: 'active' },
  { id: 'sharepoint', name: 'SharePoint', category: 'storage', authType: 'oauth2', status: 'active' },

  // EMAIL
  { id: 'gmail', name: 'Gmail', category: 'email', authType: 'oauth2', status: 'active' },
  { id: 'outlook', name: 'Outlook', category: 'email', authType: 'oauth2', status: 'active' },

  // FINANCIAL
  { id: 'quickbooks_online', name: 'QuickBooks Online', category: 'financial', authType: 'oauth2', status: 'active' },
  { id: 'quickbooks_desktop', name: 'QuickBooks Desktop', category: 'financial', authType: 'api_key', status: 'active' },
  { id: 'xero', name: 'Xero', category: 'financial', authType: 'oauth2', status: 'active' },
  { id: 'sage', name: 'Sage', category: 'financial', authType: 'oauth2', status: 'coming_soon' },

  // PHOTO APPS
  { id: 'companycam', name: 'CompanyCam', category: 'photo', authType: 'oauth2', status: 'active' },
  { id: 'eagleview', name: 'EagleView', category: 'photo', authType: 'api_key', status: 'active' },

  // PROJECT MANAGEMENT
  { id: 'procore', name: 'Procore', category: 'pm', authType: 'oauth2', status: 'coming_soon' },
  { id: 'buildertrend', name: 'Buildertrend', category: 'pm', authType: 'oauth2', status: 'coming_soon' },

  // COMMUNICATION
  { id: 'slack', name: 'Slack', category: 'communication', authType: 'oauth2', status: 'active' },
  { id: 'teams', name: 'Microsoft Teams', category: 'communication', authType: 'oauth2', status: 'active' },

  // SIGNATURES
  { id: 'docusign', name: 'DocuSign', category: 'signatures', authType: 'oauth2', status: 'active' },

  // AUTOMATION
  { id: 'zapier', name: 'Zapier', category: 'automation', authType: 'webhook', status: 'active' },
  { id: 'make', name: 'Make (Integromat)', category: 'automation', authType: 'webhook', status: 'active' }
];
```

### Sync Queue Architecture

```typescript
// services/integrations/sync-queue.ts

import { Queue, Worker } from 'bullmq';

// Job types
type SyncJobType =
  | 'upload_photo'
  | 'sync_email'
  | 'push_time_entry'
  | 'push_ready_to_bill'
  | 'import_job_codes'
  | 'webhook_delivery';

interface SyncJob {
  type: SyncJobType;
  provider: string;
  userId: string;
  projectId?: string;
  payload: any;
  priority: 'high' | 'normal' | 'low';
  retryCount: number;
}

// Queue configuration
const syncQueue = new Queue('integration-sync', {
  defaultJobOptions: {
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 1000  // 1s, 2s, 4s, 8s, 16s
    },
    removeOnComplete: 100,
    removeOnFail: 1000
  }
});

// Worker processor
const worker = new Worker('integration-sync', async (job) => {
  const { type, provider, payload } = job.data;

  switch (type) {
    case 'upload_photo':
      return await storageService.uploadPhoto(provider, payload);
    case 'sync_email':
      return await emailService.saveEmail(provider, payload);
    case 'push_time_entry':
      return await financialService.pushTimeEntry(provider, payload);
    case 'push_ready_to_bill':
      return await financialService.pushReadyToBill(provider, payload);
    default:
      throw new Error(`Unknown job type: ${type}`);
  }
}, {
  concurrency: 10,
  limiter: {
    max: 100,
    duration: 60000  // 100 jobs per minute per provider
  }
});
```

### Database Schema (Integration Tables)

```sql
-- User integration connections
CREATE TABLE user_integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) NOT NULL,
  provider VARCHAR(50) NOT NULL,  -- 'dropbox', 'quickbooks', etc.
  status VARCHAR(20) DEFAULT 'active',

  -- OAuth tokens (encrypted)
  access_token_encrypted TEXT,
  refresh_token_encrypted TEXT,
  token_expires_at TIMESTAMPTZ,

  -- Provider-specific settings
  settings JSONB DEFAULT '{}',
  -- e.g., { "root_folder": "/Projects", "sync_photos": true }

  -- Sync state
  last_sync_at TIMESTAMPTZ,
  last_sync_status VARCHAR(20),
  sync_cursor TEXT,  -- For incremental sync

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(user_id, provider)
);

-- Project-level integration mappings
CREATE TABLE project_integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  integration_id UUID REFERENCES user_integrations(id) NOT NULL,

  -- External IDs
  external_folder_id TEXT,    -- Cloud storage folder ID
  external_project_id TEXT,   -- QuickBooks job ID, Procore project ID
  external_customer_id TEXT,  -- QuickBooks customer ID

  -- Mapping configuration
  folder_mapping JSONB DEFAULT '{}',
  -- e.g., { "photos": "/Photos", "daily_logs": "/Reports/Daily" }

  sync_enabled BOOLEAN DEFAULT true,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync job history (for debugging)
CREATE TABLE integration_sync_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID REFERENCES user_integrations(id),
  job_type VARCHAR(50),
  status VARCHAR(20),  -- 'pending', 'processing', 'completed', 'failed'

  payload JSONB,
  result JSONB,
  error_message TEXT,

  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook subscriptions (for receiving data from providers)
CREATE TABLE webhook_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID REFERENCES user_integrations(id),
  provider VARCHAR(50),
  event_type VARCHAR(100),  -- 'photo.created', 'file.changed'

  webhook_url TEXT,
  webhook_secret TEXT,

  status VARCHAR(20) DEFAULT 'active',
  last_received_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## UI: THE APP STORE EXPERIENCE

### Integration Settings Page

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Settings > Integrations                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  "We play nice with your current tools."                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🔍 Search integrations...                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  📁 FILE STORAGE                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │ 📦      │ │ 📁      │ │ ☁️      │ │ 📤      │               │
│  │ Dropbox │ │ Google  │ │ OneDrive│ │ Box     │               │
│  │         │ │ Drive   │ │         │ │         │               │
│  │ ✅ ON   │ │ [Connect]│ │ [Connect]│ │ [Connect]│              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
│                                                                  │
│  📧 EMAIL                                                        │
│  ┌─────────┐ ┌─────────┐                                        │
│  │ ✉️      │ │ 📬      │                                        │
│  │ Gmail   │ │ Outlook │                                        │
│  │         │ │         │                                        │
│  │ [Connect]│ │ ✅ ON   │                                        │
│  └─────────┘ └─────────┘                                        │
│                                                                  │
│  💰 ACCOUNTING                                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│  │ 📊      │ │ 📈      │ │ 🧮      │                            │
│  │ Quick-  │ │ Xero    │ │ Sage    │                            │
│  │ Books   │ │         │ │         │                            │
│  │ ✅ ON   │ │ [Connect]│ │ Coming  │                            │
│  └─────────┘ └─────────┘ └─────────┘                            │
│                                                                  │
│  📷 PHOTO APPS                                                   │
│  ┌─────────┐ ┌─────────┐                                        │
│  │ 📸      │ │ 🛰️      │                                        │
│  │ Company │ │ Eagle   │                                        │
│  │ Cam     │ │ View    │                                        │
│  │ [Connect]│ │ [Connect]│                                       │
│  └─────────┘ └─────────┘                                        │
│                                                                  │
│  🔗 AUTOMATION                                                   │
│  ┌─────────┐ ┌─────────┐                                        │
│  │ ⚡      │ │ 🔄      │                                        │
│  │ Zapier  │ │ Make    │                                        │
│  │         │ │         │                                        │
│  │ [Connect]│ │ [Connect]│                                       │
│  └─────────┘ └─────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Connected Integration Detail View

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back    📦 Dropbox                           [Disconnect]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ Connected as: john@lefebvredesign.com                       │
│  Last synced: 2 minutes ago                                      │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  📁 ROOT FOLDER                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  /Lefebvre Design/Projects                              │    │
│  │  [Change Folder]                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  🔄 SYNC SETTINGS                                                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  📸 Photos                               [✓] Auto-sync   │    │
│  │     Uploads field photos to /Photos/Daily-Logs          │    │
│  │                                                          │    │
│  │  📄 Documents                            [✓] Auto-sync   │    │
│  │     Syncs submittals, RFIs, change orders               │    │
│  │                                                          │    │
│  │  📋 Reports                              [✓] Auto-sync   │    │
│  │     Daily logs saved as PDFs to /Reports                │    │
│  │                                                          │    │
│  │  📧 Emails                               [ ] Auto-sync   │    │
│  │     Saved correspondence (optional)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  📊 SYNC HISTORY                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ✓ 2 min ago   Photo uploaded (roof-deck-progress.jpg) │    │
│  │  ✓ 15 min ago  Daily log PDF saved                      │    │
│  │  ✓ 1 hr ago    4 photos synced                          │    │
│  │  ⚠️ 2 hrs ago   Retry: connection timeout               │    │
│  │  ✓ 3 hrs ago   Submittal document synced                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ZAPIER / MAKE INTEGRATION (NO-CODE AUTOMATION)

For contractors who want custom workflows without code:

### ROOFIO Zapier Triggers

| Trigger | Description |
|---------|-------------|
| New Photo Uploaded | When a photo is captured in Digital Foreman |
| Daily Log Completed | When a foreman submits their daily log |
| JHA Signed | When safety JHA is signed and verified |
| Phase Completed | When a project phase hits 100% |
| Weather Flag Triggered | When auto-weather detects delay conditions |
| Safety Issue Detected | When AI detects safety concern in photo |
| Material Scanned | When barcode/QR verified against submittal |

### ROOFIO Zapier Actions

| Action | Description |
|--------|-------------|
| Create Project | Set up new project with details |
| Add Photo to Project | Upload photo with metadata |
| Create Daily Log Entry | Add labor, equipment, notes |
| Update Phase Progress | Set percentage complete |
| Send Notification | Alert team members |
| Generate Report | Create PDF daily log or progress report |

### Example Zaps

1. **Photo → Slack Alert**
   - Trigger: New Photo Uploaded (with safety issue)
   - Action: Send Slack message to #safety channel with photo

2. **Daily Log → Google Sheets**
   - Trigger: Daily Log Completed
   - Action: Add row to project tracking spreadsheet

3. **Phase Complete → QuickBooks Invoice**
   - Trigger: Phase Completed (100%)
   - Action: Create draft invoice in QuickBooks

4. **Weather Flag → Email Alert**
   - Trigger: Weather Flag Triggered
   - Action: Email project manager and owner

---

## IMPLEMENTATION PRIORITY

### Phase 1: Foundation (Weeks 1-2)
1. Integration Manager service (OAuth2 flows)
2. Sync Queue (BullMQ + Redis)
3. Database schema for integrations
4. Settings UI (App Store style)

### Phase 2: Magic Folder (Weeks 3-4)
1. Dropbox connector
2. Google Drive connector
3. OneDrive connector
4. Auto-folder structure creation
5. Photo sync (ROOFIO → Cloud)

### Phase 3: Get Paid Faster (Weeks 5-6)
1. QuickBooks Online connector
2. Job code import
3. Time entry push
4. Ready-to-Bill triggers

### Phase 4: Email Sidecar (Weeks 7-8)
1. Gmail browser extension
2. Outlook Add-in
3. AI email analysis
4. One-click save to project

### Phase 5: Visual Proof (Weeks 9-10)
1. CompanyCam webhook receiver
2. Photo import + AI analysis
3. EagleView measurement import
4. Safety issue detection

### Phase 6: Automation (Week 11-12)
1. Zapier integration
2. Make integration
3. Webhook delivery system
4. Custom workflow builder

---

## SUCCESS METRICS

### Adoption Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Integration Connection Rate | 70% connect ≥1 | Validates "Super-Plugin" positioning |
| Magic Folder Usage | 60% of photos synced | Core value prop working |
| Email Sidecar Installs | 40% of users | Email is where work happens |
| QuickBooks Connection | 50% of paying users | Billing acceleration = retention |

### Expansion Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Features Used (Start) | 1.2 avg | Land with single feature |
| Features Used (90 days) | 3.5 avg | Expand into platform |
| Cross-feature Discovery | 25% /month | Natural expansion working |
| Upgrade from Free | 35% in 60 days | Integration hook converts |

### Net Revenue Retention

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| NDR | >120% | Expansion > Churn |
| Upsell Rate | 30% /year | Integration users buy more |
| Churn Rate | <5% /year | Integrations create stickiness |

---

## THE BOTTOM LINE

**Old Pitch:** "Replace everything with ROOFIO"
**Result:** 😠 "No thanks, I already have tools"

**New Pitch:** "Keep your Dropbox, your QuickBooks, your email. ROOFIO just fixes the one thing you hate."
**Result:** 🤔 "Okay, I'll try the weather documentation..."
**30 days later:** 😍 "Wait, this also does safety tracking? And it syncs to my Drive?"

**That's the Trojan Horse.**

---

*"We play nice with your current tools."*
