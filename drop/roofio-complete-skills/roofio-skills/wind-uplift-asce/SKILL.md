# Wind Uplift & ASCE Requirements Skill

## ROOFIO - Division 07 Expert System

### Overview
Wind uplift design is critical for roof system performance. This skill covers ASCE 7 wind load calculations, climate zone requirements, and attachment specifications for all roof assemblies.

---

## ASCE 7 Wind Design Fundamentals

### Basic Wind Speed (V)
ASCE 7-22 uses ultimate wind speeds (Vult) based on Risk Category:

| Risk Category | Description | Map Reference |
|---------------|-------------|---------------|
| I | Low hazard (ag buildings, minor storage) | Figure 26.5-1A |
| II | Standard occupancy (most commercial) | Figure 26.5-1B |
| III | Substantial hazard (schools, theaters) | Figure 26.5-1C |
| IV | Essential facilities (hospitals, EOC) | Figure 26.5-1D |

**Key Wind Speed Zones (Risk Category II):**
```
Gulf Coast (TX to FL):     150-180 mph
Atlantic Coast (FL-NC):    140-170 mph
Atlantic Coast (NC-ME):    110-140 mph
Central US:                105-115 mph
West Coast:                95-110 mph
Interior Mountain:         95-105 mph
Alaska:                    Varies widely
Hawaii:                    105-130 mph
```

### Wind Pressure Calculation

**Basic Formula:**
```
p = qh × [(GCp) - (GCpi)]

Where:
qh = Velocity pressure at mean roof height
GCp = External pressure coefficient
GCpi = Internal pressure coefficient
```

**Velocity Pressure:**
```
qh = 0.00256 × Kz × Kzt × Kd × Ke × V²

Where:
Kz = Velocity pressure exposure coefficient
Kzt = Topographic factor
Kd = Wind directionality factor (0.85 for roofs)
Ke = Ground elevation factor
V = Basic wind speed (mph)
```

### Exposure Categories

| Category | Description | Kz Range |
|----------|-------------|----------|
| B | Urban, suburban, wooded | 0.57-1.27 |
| C | Open terrain, scattered obstructions | 0.85-1.43 |
| D | Flat, unobstructed coastal | 1.03-1.56 |

**Exposure B:** Buildings in urban/suburban areas where surface roughness condition B prevails in upwind direction for at least 2,600 ft or 20× building height.

**Exposure C:** Default when B or D don't apply. Open terrain with scattered obstructions <30 ft.

**Exposure D:** Flat, unobstructed areas exposed to wind over open water for at least 1 mile.

---

## Roof Zones (ASCE 7 Figure 30.3-2)

### Low-Rise Buildings (h ≤ 60 ft)

```
┌─────────────────────────────────────────┐
│  CORNER (3)     │      EDGE (2)         │
│   10% width     │    10% width          │
├─────────────────┼───────────────────────┤
│                 │                       │
│   EDGE (2)      │      FIELD (1)        │
│                 │                       │
│                 │                       │
│                 │                       │
└─────────────────┴───────────────────────┘

Zone dimensions (a = 10% of least dimension or 0.4h, min 3 ft):
- Zone 1 (Field): Interior area
- Zone 2 (Perimeter): Width = a from edge
- Zone 3 (Corner): a × a at corners
```

### Component & Cladding Pressures (psf)

**Example: Risk Cat II, Exposure C, V=115 mph, h=20 ft**

| Zone | Positive | Negative |
|------|----------|----------|
| 1 (Field) | +8.5 | -15.2 |
| 2 (Perimeter) | +8.5 | -25.8 |
| 3 (Corner) | +8.5 | -38.4 |

*Note: Negative = uplift (critical for roofing)*

---

## Climate Zones & Regional Requirements

### IECC Climate Zones

```
Zone 1: Very Hot-Humid (Miami, Hawaii)
Zone 2: Hot-Humid (Houston, Phoenix, New Orleans)
Zone 3: Warm (LA, Dallas, Atlanta, Charlotte)
Zone 4: Mixed (NYC, DC, St. Louis, Seattle)
Zone 5: Cool (Chicago, Boston, Denver)
Zone 6: Cold (Minneapolis, Milwaukee)
Zone 7: Very Cold (Duluth, Fargo)
Zone 8: Subarctic (Fairbanks)
```

### Regional Wind Considerations

**Hurricane-Prone Regions:**
- Atlantic coast south of CT
- Gulf coast
- Hawaii
- Puerto Rico, US Virgin Islands
- Special requirements: Impact-resistant, enhanced fastening

**High-Wind Zones (>130 mph):**
- Florida Building Code requirements
- Miami-Dade NOA required (South FL)
- TAS 100/101/102/103 testing
- Enhanced edge securement

**Tornado Alley:**
- Central US (TX to SD)
- Consider enhanced attachment
- Safe room requirements (FEMA P-320, P-361)

### Temperature Considerations by Zone

| Zone | Winter Design | Summer Design | Thermal Movement |
|------|---------------|---------------|------------------|
| 1-2 | 35-50°F | 95-105°F | Moderate |
| 3-4 | 10-30°F | 85-95°F | Significant |
| 5-6 | -10 to 10°F | 80-90°F | High |
| 7-8 | -30 to -10°F | 70-85°F | Very High |

---

## Attachment Requirements

### Fastener Patterns by Wind Zone

**Field (Zone 1):**
```
Standard: 1 fastener per 1 SF (12" × 12" grid)
Enhanced: 1 fastener per 0.75 SF
High-wind: 1 fastener per 0.5 SF (6" × 12" pattern)
```

**Perimeter (Zone 2):**
```
Standard: 1 fastener per 0.75 SF
Enhanced: 1 fastener per 0.5 SF
High-wind: 1 fastener per 0.33 SF
```

**Corner (Zone 3):**
```
Standard: 1 fastener per 0.5 SF
Enhanced: 1 fastener per 0.33 SF
High-wind: 1 fastener per 0.25 SF (6" × 6" pattern)
```

### Fastener Pullout Requirements

**Minimum Pullout Values:**
| Deck Type | Min Pullout | Test Standard |
|-----------|-------------|---------------|
| Steel (22 ga) | 500 lbf | FM 4470 |
| Steel (20 ga) | 650 lbf | FM 4470 |
| Plywood (5/8") | 400 lbf | ASTM D1761 |
| Wood plank | 350 lbf | ASTM D1761 |
| Concrete | 800 lbf | ASTM E488 |
| Gypsum | 300 lbf | FM 4470 |

### Adhesive Wind Uplift

**Full Adhesion Required When:**
- Wind uplift exceeds 60 psf
- Re-roofing over smooth surfaces
- Manufacturer requires for warranty

**Adhesive Coverage:**
```
Standard: Ribbon pattern (12" OC)
Enhanced: 6" ribbon pattern
Full spread: 100% coverage (high wind)
```

---

## FM Global Wind Ratings

### FM 1-60 through 1-435 System

**Rating = Design Pressure (psf) × 1.5 Safety Factor**

| FM Rating | Design Pressure | Typical Application |
|-----------|-----------------|---------------------|
| 1-60 | 40 psf | Interior, low buildings |
| 1-90 | 60 psf | Standard commercial |
| 1-120 | 80 psf | Coastal, taller buildings |
| 1-150 | 100 psf | High-wind coastal |
| 1-180 | 120 psf | Hurricane zones |
| 1-240 | 160 psf | Extreme exposure |
| 1-435 | 290 psf | Miami-Dade, critical |

### FM RoofNav

**Required Information:**
1. Building location (address or coordinates)
2. Building height
3. Roof dimensions
4. Exposure category
5. Risk category
6. Roof slope

**Output:**
- Required FM rating by zone
- Assembly options meeting requirements
- Securement schedules

---

## Seismic Considerations

### ASCE 7 Seismic Design Categories

| SDC | Description | Roof Impact |
|-----|-------------|-------------|
| A | Very low seismicity | No special requirements |
| B | Low seismicity | Basic anchorage |
| C | Moderate seismicity | Enhanced connections |
| D | High seismicity | Drift accommodation |
| E | Near-fault, high | Special detailing |
| F | Near-fault, essential | Critical detailing |

### Seismic Roof Details

**Expansion Joints:**
- Locate at structural separations
- Accommodate building drift
- Typical movement: ±2" to ±6"

**Parapet Bracing:**
- Required SDC C and above
- Spacing per structural requirements
- Connection to roof structure

---

## Regional Code Supplements

### Florida Building Code (FBC)
- HVHZ (High-Velocity Hurricane Zone): Miami-Dade, Broward
- Product approval required (FL#, NOA)
- TAS 100-95 testing for adhesion
- Enhanced edge securement

### Texas Department of Insurance (TDI)
- Windstorm certification required (coastal)
- WPI-8 form for compliance
- Approved product list

### California Building Code
- Title 24 energy requirements
- Cool roof requirements
- Fire ratings (WUI zones)

### New York City Building Code
- High-rise wind requirements
- Periodic inspection requirements
- Special inspection for roofing

---

## Design Checklist

### Project Information
- [ ] Location (address, coordinates)
- [ ] Building dimensions (L×W×H)
- [ ] Mean roof height
- [ ] Roof slope
- [ ] Occupancy/Risk Category
- [ ] Essential facility?

### Wind Analysis
- [ ] Basic wind speed (V)
- [ ] Exposure category (B, C, D)
- [ ] Topographic factor (Kzt)
- [ ] Velocity pressure (qh)
- [ ] Zone pressures calculated
- [ ] FM rating determined

### Assembly Selection
- [ ] Meets Zone 1 (Field) requirements
- [ ] Meets Zone 2 (Perimeter) requirements
- [ ] Meets Zone 3 (Corner) requirements
- [ ] Manufacturer approved assembly
- [ ] FM/UL listed (if required)

### Attachment Schedule
- [ ] Field fastener pattern
- [ ] Perimeter fastener pattern
- [ ] Corner fastener pattern
- [ ] Edge securement details
- [ ] Fastener type and length
- [ ] Pullout verification

---

## Quick Reference Tables

### Wind Speed to Pressure (Exposure C, h=30')

| Wind Speed | Zone 1 | Zone 2 | Zone 3 |
|------------|--------|--------|--------|
| 95 mph | -12 psf | -20 psf | -30 psf |
| 110 mph | -16 psf | -27 psf | -40 psf |
| 120 mph | -19 psf | -32 psf | -48 psf |
| 130 mph | -22 psf | -38 psf | -56 psf |
| 150 mph | -30 psf | -50 psf | -75 psf |
| 170 mph | -38 psf | -64 psf | -96 psf |

### FM Rating Quick Selection

| Wind Speed | Exposure B | Exposure C | Exposure D |
|------------|------------|------------|------------|
| 95 mph | 1-60 | 1-75 | 1-90 |
| 110 mph | 1-75 | 1-90 | 1-120 |
| 120 mph | 1-90 | 1-120 | 1-150 |
| 130 mph | 1-120 | 1-150 | 1-180 |
| 150 mph | 1-150 | 1-180 | 1-240 |

---

## Resources

- ASCE 7-22: Minimum Design Loads
- FM Global Data Sheet 1-29: Roof Deck Securement
- FM Global Data Sheet 1-28: Wind Design
- NRCA Roofing Manual: Architectural Metal Flashing
- SPRI Wind Design Guide
- ASCE 7 Hazard Tool: https://asce7hazardtool.online/
