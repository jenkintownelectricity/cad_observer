# Drafting Details & Innovations

## ROOFIO - Division 07 Expert System

### Overview
This skill covers shop drawing standards, detail development, and innovative solutions for roofing and waterproofing details. Based on 20+ years of field experience from Armand Lefebvre.

---

## DRAFTING STANDARDS

### Layer Conventions

**Standard Layer Structure:**
```
ROOF-DECK        - Structural deck outline
ROOF-SLOPE       - Slope arrows, drainage
ROOF-MEMB        - Field membrane (Cyan)
ROOF-FLASH-BASE  - Base flashing (Yellow)
ROOF-FLASH-CAP   - Counter/cap flashing (Red)
ROOF-EDGE        - Edge metal (Magenta)
ROOF-INSUL       - Insulation (Green)
ROOF-DRAIN       - Drains, scuppers (Blue)
ROOF-PENE        - Penetrations (White)
ROOF-CURB        - Equipment curbs
ROOF-NOTES       - Notes, dimensions
ROOF-HATCH       - Hatch patterns
```

**Layer Colors:**
| Layer | Color | Number |
|-------|-------|--------|
| ROOF-MEMB | Cyan | 4 |
| ROOF-FLASH-BASE | Yellow | 2 |
| ROOF-FLASH-CAP | Red | 1 |
| ROOF-EDGE | Magenta | 6 |
| ROOF-INSUL | Green | 3 |
| ROOF-DRAIN | Blue | 5 |

### Scale Standards

| Drawing Type | Scale |
|--------------|-------|
| Roof plan | 1/8" = 1'-0" |
| Enlarged plan | 1/4" = 1'-0" |
| Details | 3/4" = 1'-0" or 1-1/2" = 1'-0" |
| Large details | 3" = 1'-0" |

### Sheet Organization

```
SD-701  Roof Plan
SD-702  Enlarged Plans
SD-703  Flashing Details (1 of X)
SD-704  Flashing Details (2 of X)
SD-705  Drain Details
SD-706  Penetration Details
SD-707  Edge Metal Details
SD-708  Equipment Curb Details
SD-709  Schedules
```

---

## STANDARD DETAILS

### Base Flashing Series (FL)

**FL-01: Masonry Wall**
```
Components:
1. Membrane field
2. Membrane base flash (stripped-in)
3. Termination bar (stainless)
4. Counter flash into reglet
5. Sealant at top
6. Insulation tapered to wall

Key dimensions:
- Base flash height: 8" minimum
- Counter flash overlap: 4" minimum
- Reglet depth: 1" minimum
- Termination bar: 1" from top of base
```

**FL-02: Metal Stud/Sheathing**
```
Components:
1. Membrane field
2. Membrane base flash
3. Surface termination bar
4. Sheet metal counter flash
5. Sealant at all metal joints
6. Air barrier integration

Key dimensions:
- Base flash: 8" min above roof
- Counter flash: 4" overlap
- Metal joint spacing: 10' OC
```

**FL-03: Concrete Wall**
```
Components:
1. Membrane field
2. Membrane base flash
3. Termination bar with expansion anchors
4. Reglet or surface counter flash
5. Backer rod and sealant

Key dimensions:
- Anchor spacing: 6" OC
- Base flash: 8" minimum
```

### Edge Metal Series (EM)

**EM-01: Gravel Stop**
```
Components:
1. Membrane field
2. Strip-in ply under edge
3. Edge metal with water dam
4. Continuous cleat
5. Face fascia

Key dimensions:
- Face height: 4" minimum
- Water dam: 1" minimum
- Cleat: 3" minimum
- Joint spacing: 4' OC (with splice)
```

**EM-02: Drip Edge**
```
Components:
1. Membrane over metal flange
2. Drip edge hemmed at outer
3. Continuous cleat or direct nail
4. Gutter below (if applicable)

Key dimensions:
- Roof flange: 4" minimum
- Drip leg: 2" minimum
- Hem: 1/4" minimum
```

**EM-03: Coping**
```
Components:
1. Membrane base flash both sides
2. Coping cap
3. Splice plates at joints
4. Continuous cleat each side
5. Sealant at joints

Key dimensions:
- Overhang: 2" minimum each side
- Slope: 2:12 to interior
- Joint spacing: 10' max (steel)
- Splice plates: 6" wide
```

### Drain Series (DR)

**DR-01: Standard Roof Drain**
```
Components:
1. Sump framing (4" min depth)
2. Membrane into sump
3. Clamping ring
4. Drain body
5. Strainer/dome
6. Leader pipe below

Key dimensions:
- Sump depth: 4" minimum
- Membrane extension into sump: Full
- Drain diameter: 4" minimum (6" typical)
```

**DR-02: Overflow Drain**
```
Components:
1. Drain body set 2" above primary
2. Membrane flashing
3. Clamping ring
4. Open strainer

Key dimensions:
- Set height: 2" above primary
- Capacity: Equal to primary
- Location: Within 10' of primary
```

**DR-03: Scupper**
```
Components:
1. Metal scupper box
2. Membrane into box
3. Conductor head (exterior)
4. Overflow line marked

Key dimensions:
- Minimum size: 4" × 4" (depends on area)
- Overflow: 2" above roof surface
- Conductor: Below scupper
```

### Penetration Series (PN)

**PN-01: Small Pipe (<4")**
```
Components:
1. Membrane field
2. Pipe boot/cone
3. Compression clamp
4. Sealant
5. Pitch pan option

Key dimensions:
- Boot height: 8" minimum
- Overlap on membrane: 4" minimum
```

**PN-02: Large Pipe (>4")**
```
Components:
1. Field membrane
2. Metal sleeve/pitch pan
3. Membrane flashing
4. Umbrella cap
5. Pourable sealer

Key dimensions:
- Pan depth: 4" minimum
- Clearance: 1" around pipe
- Dam height: 2" above fill
```

**PN-03: Conduit Cluster**
```
Components:
1. Metal curb/trough
2. Membrane flashing
3. Umbrella cover
4. Individual seals
5. Support framing

Design approach:
- Group conduits when possible
- Provide maintenance access
- Plan for future additions
```

### Curb Series (CB)

**CB-01: Equipment Curb**
```
Components:
1. Curb framing (steel or wood)
2. Membrane flashing to top of curb
3. Metal counterflash
4. Equipment base flashing
5. Vibration isolation (if needed)

Key dimensions:
- Curb height: 8" min (12" near drains)
- Flashing up curb: Full height
- Counterflash overlap: 4" minimum
- Equipment overhang: 2" max
```

**CB-02: Skylight Curb**
```
Components:
1. Factory curb or site-built
2. Membrane flashing
3. Metal counterflash
4. Skylight frame
5. Condensation gutter

Key dimensions:
- Curb height: 8" minimum
- Flashing: To underside of frame
- Weep holes in curb
```

---

## INNOVATIVE DETAILS

### Problem: Multiple Penetrations in Tight Space
**Solution: Consolidated Penetration Curb**
```
Instead of individual flashings:
1. Build continuous metal curb
2. Route all penetrations through curb
3. Single membrane flashing
4. Common hood/cover
5. Simplified maintenance

Benefits:
- Fewer potential leak points
- Easier waterproofing
- Better aesthetics
- Future-proofed for additions
```

### Problem: Parapet Too Low for Base Flashing
**Solution: Extended Metal System**
```
When parapet < 8":
1. Metal cap extends over wall
2. Membrane terminates at deck edge
3. Metal counter over membrane
4. Drip edge at exterior
5. Full integration with wall

Benefits:
- Meets code intent
- Protects membrane
- Aesthetically clean
```

### Problem: Deck Deflection at Drains
**Solution: Reinforced Sump Detail**
```
1. Sump receiver welded to deck
2. Reinforced membrane at sump
3. Additional insulation support
4. Oversized clamping ring
5. Inspection port option

Benefits:
- Accommodates movement
- Prevents ponding away from drain
- Easier maintenance
```

### Problem: High Foot Traffic Areas
**Solution: Walkway System Integration**
```
1. Reinforced membrane (80 mil)
2. Protection mat
3. Paver system or walkway pads
4. Edge restraints
5. Drainage consideration

Details:
- Route traffic patterns
- Protect penetration flashings
- Service access paths
- Maintenance considerations
```

### Problem: Green Roof Transition
**Solution: Vegetated to Membrane Detail**
```
1. Membrane continuous under green roof
2. Transition curb (6" minimum)
3. Drainage mat extends beyond green
4. Filter fabric termination
5. Inspection zone at perimeter

Key points:
- Maintain drainage path
- Allow membrane inspection
- Prevent growing media migration
```

---

## CAD PRODUCTIVITY

### Block Library Essentials

**Standard Blocks:**
```
DRAIN-4       4" drain with sump
DRAIN-6       6" drain with sump
PENE-SM       Small penetration (<4")
PENE-LG       Large penetration (>4")
CURB-STD      Standard equipment curb
SLOPE-ARW     Slope arrow with text
SECTION-MK    Section marker
DETAIL-MK     Detail marker
NORTH-ARW     North arrow
```

### Productivity Commands

```
LAYMCH   - Match layer properties
LAYCUR   - Set current layer
LAYISO   - Isolate layers
LAYFRZ   - Freeze layers
QSELECT  - Quick select by property
MATCHPROP - Match all properties
BURST    - Explode with attributes
```

### Hatch Patterns

| Pattern | Use |
|---------|-----|
| INSUL | Insulation in section |
| AR-CONC | Concrete |
| STEEL | Steel deck |
| SOLID | Membrane (color varies) |
| ANSI31 | General section hatch |

---

## DETAIL DEVELOPMENT PROCESS

### Step 1: Understand the Condition
```
□ What are the components meeting?
□ What materials are involved?
□ What movement is expected?
□ What's the exposure?
□ What maintenance access is needed?
```

### Step 2: Reference Standards
```
□ Check manufacturer details
□ Review NRCA guidelines
□ Verify code requirements
□ Consider FM/UL requirements
□ Review similar successful details
```

### Step 3: Draft Initial Detail
```
□ Show all components
□ Include proper dimensions
□ Note materials clearly
□ Show sequence (numbered)
□ Include critical dimensions
```

### Step 4: Review and Refine
```
□ Constructability review
□ Material compatibility
□ Movement accommodation
□ Water management
□ Maintenance access
```

### Step 5: Coordinate
```
□ Coordinate with architect
□ Coordinate with structure
□ Coordinate with MEP
□ Confirm with contractor
□ Verify with manufacturer
```

---

## DETAIL NOTES

### Standard Note Sets

**General Notes:**
```
1. Contractor to verify all dimensions in field
2. Slope membrane to drains minimum 1/4" per foot
3. Flash all penetrations per manufacturer requirements
4. Minimum 8" base flash height unless noted
5. Install per manufacturer specifications and details
```

**Membrane Notes:**
```
1. Seam overlap: 2.5" minimum (TPO/PVC)
2. Probe test 100% of seams
3. Clean and prime surfaces per manufacturer
4. Ambient temperature limits per spec
5. Do not install over wet surfaces
```

**Flashing Notes:**
```
1. Turn up termination bar 6" on ends
2. Sealant per manufacturer recommendations
3. Counter flash to extend 4" below top of base
4. Stainless steel fasteners in coastal areas
5. Expansion joints per manufacturer
```

---

## ARMAND'S INNOVATIONS

### [To Be Populated Through Conversation]

*This section will be filled with specific innovations and details developed through working with Armand. Each addition will include:*

- Problem description
- Solution approach
- CAD detail reference
- Field-proven results
- Lessons learned

**Ask Armand:**
- "Tell me about a detail you're particularly proud of"
- "What's a common problem you've solved uniquely?"
- "What detail do you wish architects understood better?"
- "What innovation have you developed that saves time/money?"
