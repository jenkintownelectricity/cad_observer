# ROOFIO Digital Foreman

## "The Field Commander" - Risk Shield Edition

The Digital Foreman module is a **spec-grade field documentation system** designed to be written into Division 01 specifications. It provides legally defensible documentation that reduces insurance premiums and eliminates weather delay disputes.

## Core Features: The Risk Shield Architecture

### 1. THE GATEKEEPER (JHA Lock)

**The app is LOCKED until the daily Job Hazard Analysis is completed.**

```
User Opens App → All Features LOCKED → Complete JHA → Sign → UNLOCKED
```

- JHA templates auto-populated based on work type (TPO, tear-off, flashing, etc.)
- Hazards pre-identified based on Division 07 work
- Required PPE checklist
- Superintendent digital signature required
- Crew acknowledgment signatures
- GPS verification (must be on-site)

**Spec Section**: 01 35 29 - Safety Procedures

### 2. THE WEATHER TRUTH AGENT

**Automatic weather capture at 12:00 PM and 4:00 PM daily.**

- Weather data from NOAA/OpenWeatherMap API
- GPS-based location for project site
- Auto-flag if conditions exceed thresholds:
  - Wind > 20 mph
  - Precipitation > 0.5 inches
  - Temperature < 32°F or > 95°F
- PM dashboard alerts for potential delays
- Raw API response stored for legal defensibility
- **No manual entry permitted for delay claims**

**Spec Section**: 01 32 26 - Construction Progress Reporting

### 3. THE SILICA TRACKER

**OSHA compliance documentation for silica exposure control.**

- Daily verification forms (minimum 2x per day)
- Control method documentation:
  - Wet cutting
  - Vacuum extraction
  - Enclosed cab
  - Respiratory protection
  - Local exhaust ventilation
- Photo evidence of controls
- 10 AM alert if not completed
- Links to daily log

**Spec Section**: 01 35 29 - Health, Safety, and Emergency Response

## Additional Features

### Photo Chain of Custody

- GPS extraction from EXIF
- SHA-256 hash at capture (before any processing)
- Direct-to-cloud upload (no local file transfers)
- Server-side timestamp (not device time)
- Geofence verification
- Original EXIF preserved

**Spec Section**: 01 32 33 - Photographic Documentation

### Material Verification

- Barcode/QR code scanning
- Cross-reference with approved submittals
- Automatic mismatch flagging
- Auto-generate RFI for substitutions
- Photo documentation of labels

**Spec Section**: 01 33 00 - Submittal Procedures

### Guest Inspector Mode

- No account required for third-party inspectors
- Hold point checklists
- Inspector signature capture
- Result links to daily log
- Available to Owner/Architect within 24 hours

### Hot Work Permits

- Digital hot work permits for torch operations
- Fire watch assignment and duration
- Extinguisher verification
- Combustibles clearance confirmation
- Post-work monitoring schedule

## Database Schema

See `schema.sql` for complete PostgreSQL schema including:

- `df_projects` - Project configuration with Risk Shield settings
- `df_jha_templates` - Pre-built Division 07 JHA templates
- `df_daily_jha` - Daily JHA records (THE GATEKEEPER)
- `df_weather_captures` - Weather Truth Agent captures
- `df_silica_verifications` - Silica Tracker records
- `df_daily_logs` - Daily construction logs (GATED by JHA)
- `df_photos` - Photo chain of custody records
- `df_hot_work_permits` - Hot work permit records
- `df_material_verifications` - Material scan records
- `df_inspector_visits` - Guest inspector records
- `df_system_alerts` - PM dashboard alerts
- `df_sync_queue` - Offline-first sync queue
- `df_audit_log` - Immutable audit trail

## API Endpoints

### Gatekeeper

```
GET  /api/digital-foreman/projects/{id}/jobs/{id}/gatekeeper-status
GET  /api/digital-foreman/projects/{id}/jobs/{id}/jha/template
POST /api/digital-foreman/projects/{id}/jobs/{id}/jha/complete
```

### Weather

```
POST /api/digital-foreman/projects/{id}/weather/capture
GET  /api/digital-foreman/projects/{id}/weather/flags
POST /api/digital-foreman/weather/scheduled-capture  (cron)
```

### Silica

```
POST /api/digital-foreman/projects/{id}/jobs/{id}/silica/verify
GET  /api/digital-foreman/projects/{id}/jobs/{id}/silica/compliance
POST /api/digital-foreman/silica/morning-alert-check  (cron)
```

### Daily Log

```
GET  /api/digital-foreman/projects/{id}/jobs/{id}/daily-log
POST /api/digital-foreman/projects/{id}/jobs/{id}/daily-log
POST /api/digital-foreman/projects/{id}/jobs/{id}/daily-log/submit
```

### Photos

```
POST /api/digital-foreman/projects/{id}/photos
```

### Materials

```
POST /api/digital-foreman/projects/{id}/jobs/{id}/materials/verify
```

### Inspector

```
POST /api/digital-foreman/projects/{id}/jobs/{id}/inspector/create-visit
POST /api/digital-foreman/inspector/{visit_id}/submit
```

## UI Routes

- `/digital-foreman` - Main Digital Foreman interface
- `/inspector/{visit_id}` - Guest inspector access

## Specification Language

### Performance-Based (Recommended)

```
2.1 DIGITAL FIELD DOCUMENTATION PLATFORM

A. General: Contractor shall provide a cloud-based digital platform
   for daily field reporting, accessible via mobile devices (iOS/Android)
   and web browsers.

B. Performance Requirements: The platform must provide the following
   capabilities to ensure data integrity:

   1. Automated Weather Logging: System must automatically record local
      weather conditions (Temperature, Precipitation, Wind Speed) at
      minimum 4-hour intervals using GPS geolocation. Manual entry of
      weather data is not permitted for delay claims.

   2. Immutable Photo Documentation: All progress photos must be natively
      stamped with GPS Coordinates, User ID, and Server-side timestamp.

   3. Safety Gating: System must prevent the creation of a "Daily
      Construction Report" until the daily "Job Hazard Analysis" (JHA)
      has been digitally signed by the site superintendent.

   4. Material Chain of Custody: System must support barcode/QR scanning
      of delivered materials to verify against approved Submittals.

C. Platforms meeting these requirements: ROOFIO or approved equal.
```

## OCIP Sales Strategy

For Owner Controlled Insurance Programs (OCIP):

> "This platform pays for itself by reducing your OCIP premiums.
> Every JHA logged, every weather capture, every silica verification
> is documentation that protects you from claims and lawsuits."

Target projects:
- Universities ($20M+)
- Hospitals
- Government facilities
- Corporate headquarters
- Multi-family residential (5+ stories)

## Cron Jobs Required

```bash
# Weather capture - 12 PM and 4 PM local time
0 12,16 * * * curl -X POST https://api.roofio.com/digital-foreman/weather/scheduled-capture

# Silica verification alert - 10 AM local time
0 10 * * 1-5 curl -X POST https://api.roofio.com/digital-foreman/silica/morning-alert-check
```

---

**The Risk Shield angle makes ROOFIO an insurance policy, not just a convenience app.**
