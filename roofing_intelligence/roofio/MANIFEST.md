# ROOFIO - Division 07 AI Expert

```
██████╗  ██████╗  ██████╗ ███████╗██╗ ██████╗
██╔══██╗██╔═══██╗██╔═══██╗██╔════╝██║██╔═══██╗
██████╔╝██║   ██║██║   ██║█████╗  ██║██║   ██║
██╔══██╗██║   ██║██║   ██║██╔══╝  ██║██║   ██║
██║  ██║╚██████╔╝╚██████╔╝██║     ██║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝ ╚═════╝
        THE WORLD'S SMARTEST ROOFER
```

## Identity

**Roofio** is an expert AI assistant specializing in commercial roofing, waterproofing, and Division 07 specifications. Built on 20+ years of field experience combined with comprehensive industry standards knowledge.

### Personality
- **Bold** and confident in technical knowledge
- **Practical** - always considers field installation reality
- **Direct** - gives straight answers with spec citations
- **Safety-first** - never compromises on code compliance

### Expertise Areas
- All roofing systems (TPO, EPDM, PVC, Mod-Bit, BUR, Metal, Shingles)
- Waterproofing and air barriers
- Wind uplift calculations and ASCE 7 requirements
- Building codes (IBC, IRC, ICC)
- Industry standards (NRCA, FM Global, SPRI, IIBEC)
- Manufacturer specifications (Big 3 + expanding)
- Shop drawings and detail development
- Inspections and testing protocols

---

## Skill Registry

### Status Legend
- ✅ Complete
- 🔄 In Progress
- 📋 Planned
- ⬜ Not Started

### Codes & Standards

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `codes/asce-7` | ASCE 7 Wind & Hazard | ✅ | Wind uplift, seismic, climate zones |
| `codes/ibc` | International Building Code | ✅ | IBC roofing sections |
| `codes/irc` | International Residential Code | ✅ | IRC roofing requirements |
| `codes/icc` | ICC Standards | ✅ | ICC evaluation reports |
| `codes/nfpa` | NFPA Fire Codes | 📋 | Fire ratings, assemblies |
| `standards/hierarchy` | Standards Hierarchy | ✅ | Layered system: Code→Test→Enforce→Method→Money |

### Industry Standards

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `standards/nrca` | NRCA Manual | ✅ | Roofing manual, best practices |
| `standards/fm-global` | FM Global | ✅ | FM approvals, loss prevention |
| `standards/spri` | SPRI | ✅ | Single-ply industry standards |
| `standards/iibec` | IIBEC | ✅ | Building enclosure standards |
| `standards/astm` | ASTM Testing | 📋 | Test methods, specifications |

### Roofing Systems

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `systems/roofing-systems` | All Roofing Systems | ✅ | Comprehensive overview |
| `systems/tpo` | TPO Membrane | ✅ | Thermoplastic polyolefin expert |
| `systems/epdm` | EPDM Membrane | ✅ | Rubber membrane expert |
| `systems/pvc` | PVC Membrane | ✅ | Vinyl membrane expert |
| `systems/mod-bit` | Modified Bitumen | ✅ | SBS/APP systems |
| `systems/bur` | Built-Up Roofing | ✅ | Traditional BUR systems |
| `systems/metal` | Metal Roofing | 📋 | Standing seam, panels |
| `systems/shingles` | Asphalt Shingles | 📋 | Residential shingles |
| `systems/coatings` | Roof Coatings | 📋 | Restoration, maintenance |
| `systems/green` | Vegetative Roofs | 📋 | Green roof systems |

### Manufacturers (Big 3 + Expansion)

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `manufacturers/general` | Manufacturer Overview | ✅ | Product data, comparison |
| `manufacturers/carlisle` | Carlisle SynTec | 🔄 | Technical library |
| `manufacturers/firestone` | Firestone BP | 🔄 | Technical library |
| `manufacturers/gaf` | GAF | 🔄 | Technical library |
| `manufacturers/johns-manville` | Johns Manville | ⬜ | Week 1 expansion |
| `manufacturers/sika-sarnafil` | Sika Sarnafil | ⬜ | Week 2 expansion |
| `manufacturers/tremco` | Tremco | ⬜ | Week 3 expansion |
| `manufacturers/versico` | Versico | ⬜ | Week 4 expansion |

### Inspections & Testing

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `inspections/div07-inspections` | Div 07 Inspections | ✅ | Full inspection protocols |
| `inspections/div07-testing` | Div 07 Testing | ✅ | Test methods, standards |
| `inspections/leak-detection` | Leak Detection | ✅ | ELD, flood testing, IR |
| `inspections/visual` | Visual Inspection | ✅ | Visual protocols |
| `inspections/core-cuts` | Core Cut Analysis | 📋 | Core sampling procedures |
| `inspections/wind-uplift` | Wind Uplift Testing | ✅ | FM, UL testing |
| `inspections/moisture` | Moisture Survey | 📋 | IR, nuclear, capacitance |

### Tools & Calculations

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `tools/asce-hazard` | ASCE 7 Hazard Tool | ✅ | Wind speed, seismic lookup |
| `tools/uplift-calc` | Uplift Calculator | ✅ | Wind uplift calculations |
| `tools/r-value` | R-Value Calculator | 📋 | Insulation thermal calc |
| `tools/drainage` | Drainage Calculator | 📋 | Drain sizing, slope |
| `tools/estimating` | Estimating Tools | 📋 | Takeoff, pricing |
| `tools/web-scraper` | Div 07 Web Scraper | ✅ | Database building tool |

### Drafting & Details

| Skill ID | Name | Status | Description |
|----------|------|--------|-------------|
| `drafting/standard-details` | Standard Details | 📋 | Common detail library |
| `drafting/innovations` | Detail Innovations | ✅ | Armand's innovations |
| `drafting/cad-standards` | CAD Standards | 📋 | Layer, linetype standards |

---

## Skill File Format

Each skill is a markdown file with this structure:

```markdown
# Skill Name

## Metadata
- skill_id: codes/asce-7
- version: 1.0
- last_updated: 2024-12-07
- sources: [URLs, documents]

## Quick Reference
[Most frequently needed info - instant lookup]

## Knowledge Base
[Detailed information organized by topic]

## Decision Trees
[If X condition, then Y recommendation]

## Code Citations
[Exact spec section references]

## Common Questions
[FAQ with vetted answers]

## Related Skills
[Links to related skill files]
```

---

## Integration Points

### Web Scraping Targets (Database Building)
```python
SCRAPE_SOURCES = {
    "nrca": "https://www.nrca.net/",
    "spri": "https://www.spri.org/",
    "iibec": "https://iibec.org/",
    "fm_global": "https://www.fmglobal.com/",
    "icc": "https://www.iccsafe.org/",

    # Manufacturer tech docs
    "carlisle": "https://www.carlislesyntec.com/",
    "firestone": "https://www.firestonebpco.com/",
    "gaf": "https://www.gaf.com/",

    # Code lookup
    "asce_hazard": "https://asce7hazardtool.online/",
}
```

### ASCE 7 Hazard Tool Integration
```python
def get_wind_speed(latitude: float, longitude: float, risk_category: str):
    """
    Query ASCE 7 Hazard Tool for wind speed
    Returns: Ultimate wind speed (Vult) for location
    """
    pass

def get_climate_zone(zip_code: str):
    """
    Get IECC climate zone for energy code compliance
    """
    pass
```

---

## Roofio Response Style

### Example Interaction

**User**: What's the FM wind uplift requirement for a 40-foot tall building in Miami?

**Roofio**:
> 🏗️ **Miami Wind Uplift - 40' Building**
>
> **Quick Answer**: You're in a **1-165** wind zone (HVHZ).
>
> **FM Requirements**:
> - Corner Zone: **-315 psf** (FM 1-165)
> - Perimeter Zone: **-195 psf**
> - Field Zone: **-120 psf**
>
> **Code Citations**:
> - ASCE 7-22, Section 30.4 - Components & Cladding
> - FBC 2023, High-Velocity Hurricane Zone
> - FM Global DS 1-29 - Roof Deck Securement
>
> **Recommendation**: Use FM-approved assembly with **minimum I-120** rating. For Miami-Dade, you'll also need NOA (Notice of Acceptance).
>
> *Want me to pull the specific FM assembly for your membrane type?*

---

## Directory Structure

```
roofio/
├── MANIFEST.md              # This file
├── skills/
│   ├── codes/
│   │   ├── asce-7.md
│   │   ├── ibc.md
│   │   ├── irc.md
│   │   └── icc.md
│   ├── standards/
│   │   ├── nrca.md
│   │   ├── fm-global.md
│   │   ├── spri.md
│   │   └── iibec.md
│   ├── systems/
│   │   ├── tpo.md
│   │   ├── epdm.md
│   │   ├── pvc.md
│   │   ├── mod-bit.md
│   │   └── ...
│   ├── manufacturers/
│   │   ├── carlisle.md
│   │   ├── firestone.md
│   │   ├── gaf.md
│   │   └── ...
│   ├── inspections/
│   │   ├── leak-detection.md
│   │   ├── moisture-survey.md
│   │   └── ...
│   └── tools/
│       ├── asce-hazard.md
│       ├── uplift-calc.md
│       └── ...
├── data/
│   ├── wind_zones.json
│   ├── climate_zones.json
│   ├── fm_assemblies.json
│   └── manufacturer_specs/
└── scrapers/
    ├── nrca_scraper.py
    ├── manufacturer_scraper.py
    └── code_scraper.py
```

---

## Weekly Expansion Plan

| Week | Manufacturer | Focus |
|------|--------------|-------|
| 1 | Johns Manville | TPO, ISO |
| 2 | Sika Sarnafil | PVC systems |
| 3 | Tremco | Waterproofing |
| 4 | Versico | TPO, EPDM |
| 5 | Polyglass | Mod-bit |
| 6 | Soprema | Multi-system |
| 7 | IKO | Commercial |
| 8 | Mule-Hide | Single-ply |

---

## API Endpoints (Planned)

```
POST /api/roofio/ask          # Ask Roofio a question
GET  /api/roofio/skills       # List available skills
GET  /api/roofio/skill/{id}   # Get skill content
POST /api/roofio/lookup/wind  # ASCE 7 wind lookup
POST /api/roofio/lookup/climate # Climate zone lookup
POST /api/roofio/calculate/uplift # Wind uplift calc
GET  /api/roofio/manufacturers # List manufacturers
GET  /api/roofio/assemblies    # FM approved assemblies
```

---

## Site Generator

The Division 07 Specification Website generator is located at `site-generator/`:

```bash
# Generate the spec website
cd site-generator
python roofio_site_generator.py

# Output
build/index.html              # Master index with search
build/07-XX-XX-*.html        # Individual spec pages
```

**Data Source**: `div07_codes.csv` - Contains all Division 07 spec sections with metadata.

**Generated Pages**: 50+ specification pages covering all Division 07 sections.

---

## Partnership Package

See `PARTNERSHIP-PACKAGE.md` for:
- NRCA Partnership email template
- IIBEC Technical Advisory Committee abstract
- Manufacturer partnership request templates
- Barrett Roofing pilot pitch
- ICC Code Connect application
- Technical data specification requirements
- Platform integrations (Procore, PlanGrid, etc.)
- Execution timeline

**Pitch Materials**:
- `roofio-pitch.html` - Interactive presentation
- `roofio-spec-index.html` - Spec database demo

---

## Current Skill Count

| Category | Complete | In Progress | Planned |
|----------|----------|-------------|---------|
| Codes & Standards | 5 | 0 | 1 |
| Industry Standards | 4 | 0 | 1 |
| Roofing Systems | 6 | 0 | 4 |
| Manufacturers | 1 | 3 | 4 |
| Inspections | 5 | 0 | 2 |
| Tools | 3 | 0 | 2 |
| Drafting | 1 | 0 | 2 |
| **Total** | **25** | **3** | **16** |
