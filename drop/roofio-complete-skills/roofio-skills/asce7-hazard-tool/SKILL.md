# ASCE 7 Hazard Tool Skill

## ROOFIO - Division 07 Expert System

### Overview
The ASCE 7 Hazard Tool is the authoritative online resource for determining site-specific design loads including wind, seismic, snow, rain, ice, and flood hazards per ASCE 7-22.

**Official Tool:** https://asce7hazardtool.online/

---

## TOOL ACCESS

### Getting Started

**URL:** asce7hazardtool.online

**Requirements:**
- Subscription or pay-per-report
- Project location (address or coordinates)
- Building parameters

**Output:**
- PDF report with all hazard data
- Site-specific design values
- Mapped hazard data
- Code-compliant values

---

## WIND HAZARD DATA

### What the Tool Provides

**Basic Wind Speed (V):**
```
Risk Category I:   Vult (Figure 26.5-1A)
Risk Category II:  Vult (Figure 26.5-1B)
Risk Category III: Vult (Figure 26.5-1C)
Risk Category IV:  Vult (Figure 26.5-1D)
```

**Exposure Category:**
- Based on site conditions
- User input with guidance
- B, C, or D classification

**Design Parameters:**
- Kz values (velocity pressure coefficient)
- Kzt (topographic factor)
- Kd (directionality factor)
- Ke (ground elevation factor)

### Using Wind Data for Roofing

**Step 1: Get Basic Wind Speed**
- Enter project address
- Select Risk Category (usually II for commercial)
- Record Vult value

**Step 2: Determine Exposure**
- B: Urban/suburban
- C: Open terrain (default)
- D: Coastal/water exposure

**Step 3: Calculate Design Pressure**
```
qh = 0.00256 × Kz × Kzt × Kd × Ke × V²

Where tool provides:
- Kz (from tables by height)
- Kzt (topographic factor, usually 1.0)
- Kd = 0.85 for roofs
- Ke (elevation factor)
- V = basic wind speed
```

**Step 4: Apply to Roof Zones**
```
Zone 1 (Field): qh × GCp1
Zone 2 (Perimeter): qh × GCp2
Zone 3 (Corner): qh × GCp3

GCp values from ASCE 7 tables based on:
- Building height
- Roof slope
- Tributary area
```

---

## SEISMIC HAZARD DATA

### Parameters Provided

**Site Coefficients:**
```
Ss = Short period spectral acceleration (0.2 sec)
S1 = 1-second spectral acceleration
SMS = Site-adjusted short period
SM1 = Site-adjusted 1-second
SDS = Design short period
SD1 = Design 1-second
```

**Seismic Design Category:**
- A through F
- Based on spectral accelerations
- Risk Category considered

### Application to Roofing

**Seismic Design Category Impacts:**
| SDC | Roofing Impact |
|-----|----------------|
| A-B | Minimal requirements |
| C | Enhanced anchorage |
| D-F | Drift accommodation, special details |

**Parapet Requirements:**
- Bracing requirements
- Height limitations
- Connection details

---

## SNOW HAZARD DATA

### Parameters Provided

**Ground Snow Load (pg):**
- Site-specific value (psf)
- From ASCE 7 maps
- Can be zero in some locations

**Flat Roof Snow Load (pf):**
```
pf = 0.7 × Ce × Ct × Is × pg

Where:
Ce = Exposure factor
Ct = Thermal factor
Is = Importance factor
```

### Application to Roofing

**Structural Considerations:**
- Drift loads at parapets
- Drift loads at higher roofs
- Sliding snow loads
- Rain-on-snow surcharge

**Drainage Design:**
- Size drains for snowmelt
- Consider overflow during melt
- Ice dam prevention

---

## RAIN HAZARD DATA

### Parameters Provided

**Design Rain Intensity:**
- 1-hour duration
- Based on location
- In inches per hour

**Rainfall Accumulation:**
```
R = 5.2(ds + dh)

Where:
ds = Depth of water at drain inlet
dh = Additional depth at secondary inlet
```

### Drainage Design

**Primary Drainage:**
- Sized for design storm
- Per local requirements
- Based on roof area

**Secondary (Overflow) Drainage:**
- Required by IBC
- Capacity equals primary
- 2" above primary inlet

**Scupper Sizing:**
Based on:
- Contributory area
- Head height
- Rainfall intensity

---

## ICE/ICING DATA

### Parameters Provided (Ice-prone areas)

**Ice Thickness:**
- Nominal ice thickness
- For structural considerations

**Wind on Ice:**
- Combined ice/wind loading

### Roofing Application

**Ice Dam Regions:**
- Ice barrier requirements
- Extended to 24" inside exterior wall
- Climate zones 5-8 and ice dam areas

---

## USING THE TOOL - STEP BY STEP

### For a Roofing Project

**Step 1: Access Tool**
1. Go to asce7hazardtool.online
2. Log in or purchase report
3. Enter project address

**Step 2: Input Parameters**
```
Required:
- Site address or coordinates
- Risk Category (I, II, III, IV)
- Exposure Category (B, C, D)
- Mean roof height
- Building dimensions (optional for some)
```

**Step 3: Generate Report**
1. Review input parameters
2. Generate PDF report
3. Download for records

**Step 4: Extract Roofing Data**
```
For FM/wind design:
□ Basic wind speed (V)
□ Exposure category
□ Calculate design pressures
□ Select FM rating

For drainage:
□ Rainfall intensity
□ Size primary drains
□ Size overflow

For seismic:
□ SDC category
□ Special requirements (if SDC C+)
```

---

## REPORT INTERPRETATION

### Wind Section

**Key Values to Extract:**
| Parameter | Use |
|-----------|-----|
| Vult (mph) | Wind design speed |
| Exposure | Pressure coefficients |
| Kz | Velocity pressure factor |
| Kzt | Topographic factor |

**Example Output:**
```
Basic Wind Speed (Risk Cat II): 115 mph
Exposure Category: C
Kz at 30': 0.98
Kzt: 1.0
Kd: 0.85
Ke: 1.0
```

### Calculating Roof Pressures

**From Tool Data:**
```
qh = 0.00256 × 0.98 × 1.0 × 0.85 × 1.0 × 115²
qh = 0.00256 × 0.98 × 0.85 × 13,225
qh = 28.2 psf (velocity pressure)
```

**Apply GCp (from ASCE 7):**
```
Zone 1: 28.2 × (-1.0) = -28.2 psf
Zone 2: 28.2 × (-1.8) = -50.8 psf
Zone 3: 28.2 × (-2.8) = -79.0 psf
```

**Select FM Rating:**
```
Zone 1: 28.2 psf × 1.5 SF = 42.3 → FM 1-60
Zone 2: 50.8 psf × 1.5 SF = 76.2 → FM 1-90
Zone 3: 79.0 psf × 1.5 SF = 118.5 → FM 1-120
```

---

## ALTERNATIVE RESOURCES

### When ASCE 7 Tool Unavailable

**Wind:**
- FM Global wind maps
- RoofNav (requires subscription)
- Local AHJ resources

**Seismic:**
- USGS seismic hazard maps
- Local building department

**Snow:**
- Local building codes
- Historical data

**Rain:**
- NOAA precipitation data
- Local drainage codes

---

## INTEGRATION WITH FM ROOFNAV

### Workflow

1. **ASCE 7 Tool:** Get wind speed, exposure
2. **RoofNav:** Enter parameters
3. **RoofNav:** Get FM ratings by zone
4. **RoofNav:** Select assembly
5. **Specification:** Document requirements

### RoofNav Inputs from ASCE 7

| ASCE 7 Tool | RoofNav Input |
|-------------|---------------|
| Basic wind speed | Wind speed |
| Exposure category | Exposure |
| Building height | Mean roof height |
| - | Building dimensions |
| - | Roof slope |

---

## QUICK REFERENCE

### Risk Categories (ASCE 7)

| Category | Examples |
|----------|----------|
| I | Agriculture, temporary |
| II | Most commercial (default) |
| III | Schools, theaters, >300 people |
| IV | Hospitals, emergency, essential |

### Exposure Categories

| Category | Description |
|----------|-------------|
| B | Urban, suburban, wooded |
| C | Open terrain (default) |
| D | Flat coastal, water |

### Common Design Values

| Location | Typical Wind (Cat II) |
|----------|----------------------|
| Interior US | 95-115 mph |
| Atlantic coast | 110-150 mph |
| Gulf coast | 130-180 mph |
| Pacific coast | 95-115 mph |

---

## DOCUMENTATION

### What to Save

**For Project Files:**
- Full ASCE 7 Hazard Tool report (PDF)
- Date report generated
- Input parameters used
- Calculated design values

**For Submittals:**
- Design wind speed
- Exposure category
- FM rating selected
- Assembly specification

**For Records:**
- Report confirms code compliance
- Supports warranty applications
- Documents design basis
