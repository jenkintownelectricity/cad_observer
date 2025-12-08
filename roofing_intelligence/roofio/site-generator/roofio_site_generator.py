#!/usr/bin/env python3
"""
ROOFIO Division 07 Specification Database Generator
Generates a complete static website for all Division 07 spec sections.

Usage:
    python roofio_site_generator.py

Output:
    /build/index.html - Master index with search
    /build/07-XX-XX-*.html - Individual spec pages
"""

import csv
import os
from datetime import datetime

# CONFIGURATION
DATA_FILE = 'div07_codes.csv'
OUTPUT_DIR = 'build'

# ---------------------------------------------------------
# TEMPLATE 1: THE SPEC PAGE (Roofio Authority Style)
# ---------------------------------------------------------
spec_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spec {code}: {name} | ROOFIO Division 07 Database</title>
    <meta name="description" content="Official Division 07 specification for {code} {name}. Technical standards, testing requirements, and installation guidelines from ROOFIO.">
    
    <meta property="og:title" content="Spec {code}: {name} | ROOFIO">
    <meta property="og:description" content="Division 07 Technical Standard for {name}. NRCA, FM Global, and ASTM compliant.">
    <meta property="og:type" content="article">
    
    <style>
        :root {{ 
            --primary: #0f172a; 
            --accent: #f97316; 
            --accent-dark: #ea580c;
            --bg: #f1f5f9; 
            --paper: #ffffff; 
            --border: #e2e8f0;
            --success: #10b981;
            --info: #3b82f6;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background: var(--bg); 
            color: #333; 
            margin: 0; 
            line-height: 1.6; 
        }}
        
        .navbar {{ 
            background: var(--primary); 
            padding: 15px 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }}
        
        .nav-logo {{ 
            font-weight: 900; 
            font-size: 1.4rem; 
            letter-spacing: -1px; 
            text-decoration: none; 
            color: white; 
        }}
        
        .nav-logo span {{ color: var(--accent); }}
        
        .nav-badge {{
            background: var(--accent);
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .container {{ 
            max-width: 1100px; 
            margin: 40px auto; 
            padding: 0 20px; 
            display: grid; 
            grid-template-columns: 1fr 320px; 
            gap: 40px; 
        }}
        
        /* THE OFFICIAL DOC LOOK */
        .doc-viewer {{ 
            background: var(--paper); 
            border: 1px solid #cbd5e0; 
            padding: 50px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            font-family: "Courier New", Courier, monospace;
            font-size: 14px;
            white-space: pre-wrap;
            position: relative;
            border-radius: 8px;
        }}
        
        .highlight {{ 
            background-color: #fff7ed; 
            border-left: 3px solid var(--accent); 
            padding-left: 8px; 
            display: block; 
            width: 100%; 
            margin: 2px 0;
        }}
        
        .highlight-info {{
            background-color: #eff6ff;
            border-left: 3px solid var(--info);
            padding-left: 8px;
            display: block;
            width: 100%;
            margin: 2px 0;
        }}
        
        .highlight-success {{
            background-color: #ecfdf5;
            border-left: 3px solid var(--success);
            padding-left: 8px;
            display: block;
            width: 100%;
            margin: 2px 0;
        }}
        
        .sidebar-box {{ 
            background: white; 
            border: 1px solid var(--border); 
            border-radius: 12px; 
            padding: 25px; 
            position: sticky; 
            top: 20px; 
        }}
        
        .btn {{ 
            display: block; 
            width: 100%; 
            padding: 14px; 
            background: var(--primary); 
            color: white; 
            text-align: center; 
            text-decoration: none; 
            font-weight: bold; 
            border-radius: 8px; 
            margin-bottom: 10px; 
            transition: all 0.2s;
        }}
        
        .btn:hover {{ 
            background: #1e293b; 
            transform: translateY(-1px);
        }}
        
        .btn-accent {{
            background: var(--accent);
        }}
        
        .btn-accent:hover {{
            background: var(--accent-dark);
        }}
        
        .breadcrumb {{ 
            color: #64748b; 
            font-size: 0.9rem; 
            margin-bottom: 20px; 
        }}
        
        .breadcrumb a {{ 
            color: var(--accent); 
            text-decoration: none; 
        }}
        
        .breadcrumb a:hover {{ text-decoration: underline; }}
        
        h1 {{
            color: var(--primary);
            margin-top: 0;
            font-size: 1.8rem;
        }}
        
        .spec-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        
        .meta-tag {{
            background: #f1f5f9;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #475569;
        }}
        
        .meta-tag.category {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .related-list {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        
        .related-list h4 {{
            margin: 0 0 15px 0;
            font-size: 0.9rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .related-link {{
            display: block;
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
            color: #334155;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        
        .related-link:hover {{
            color: var(--accent);
        }}
        
        .related-link:last-child {{
            border-bottom: none;
        }}

        @media(max-width: 900px) {{ 
            .container {{ grid-template-columns: 1fr; }} 
            .sidebar-box {{ position: static; }}
        }}
    </style>
</head>
<body>

    <nav class="navbar">
        <a href="index.html" class="nav-logo">ROOF<span>IO</span></a>
        <span class="nav-badge">Division 07 Database</span>
    </nav>

    <div class="container">
        <main>
            <div class="breadcrumb">
                <a href="index.html">&larr; Back to Index</a> / Division 07 / {code}
            </div>
            
            <h1>{code} - {name}</h1>
            
            <div class="spec-meta">
                <span class="meta-tag category">{category}</span>
                <span class="meta-tag">CSI MasterFormat</span>
                <span class="meta-tag">Updated: {date}</span>
            </div>
            
            <p style="color: #475569; font-size: 1.05rem; margin-bottom: 30px;">{description}</p>

            <div class="doc-viewer">
SECTION {code} - {name_upper}
═══════════════════════════════════════════════════════════════
ROOFIO DIVISION 07 TECHNICAL STANDARD
Date: {date}
Status: CURRENT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PART 1 - GENERAL

1.1 SUMMARY
    A. Section Includes:
       1. {name}.
       2. Related accessories and components.
       3. Quality assurance and testing requirements.

1.2 RELATED SECTIONS
{related_sections}

1.3 REFERENCES
<span class="highlight-info">    A. NRCA Roofing Manual - Current Edition</span>
<span class="highlight-info">    B. FM Global Property Loss Prevention Data Sheets</span>
    C. ASTM Standards as specified herein.
    D. Local building codes and amendments (AHJ).

1.4 SUBMITTALS
    A. Product Data: Manufacturer's technical data sheets.
    B. Shop Drawings: Layout, details, and flashing conditions.
    C. Samples: Physical samples upon request.
    D. Certifications: FM Approval, UL Listing as applicable.

1.5 QUALITY ASSURANCE
<span class="highlight">    A. Manufacturer Qualifications:</span>
<span class="highlight">       1. Minimum 5 years experience in {name_lower}.</span>
<span class="highlight">       2. FM Approved or UL Listed products where required.</span>
    
    B. Installer Qualifications:
       1. Manufacturer-certified installer.
       2. Minimum 3 years documented experience.

1.6 DELIVERY, STORAGE, AND HANDLING
    A. Deliver materials in original packaging.
    B. Store in dry location, protected from weather.
    C. Handle to prevent damage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PART 2 - PRODUCTS

2.1 MANUFACTURERS
    A. Acceptable Manufacturers:
<span class="highlight-success">       1. {manufacturer_hook}</span>
       2. Or approved equal meeting specifications.

2.2 MATERIALS
    A. Refer to ROOFIO {code} Technical Skill for:
       - Material specifications
       - ASTM test requirements
       - Performance criteria
       - FM/UL ratings

2.3 ACCESSORIES
    A. Fasteners, adhesives, and accessories as recommended
       by primary material manufacturer.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PART 3 - EXECUTION

3.1 EXAMINATION
    A. Verify substrate conditions meet requirements.
    B. Report unsatisfactory conditions in writing.
    C. Do not proceed until conditions are corrected.

3.2 PREPARATION
    A. Clean surfaces of debris, moisture, and contaminants.
    B. Prime surfaces as required by manufacturer.

3.3 INSTALLATION
    A. Install in accordance with:
       1. Manufacturer's written instructions.
       2. NRCA Roofing Manual guidelines.
       3. FM Global requirements where applicable.
    
    B. Coordinate with adjacent work.

3.4 PROTECTION
    A. Protect installed work from damage.
    B. Repair or replace damaged materials.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

END OF SECTION {code}

ROOFIO - The Division 07 Digital Journeyman
            </div>
        </main>

        <aside>
            <div class="sidebar-box">
                <h3 style="margin-top:0; color: var(--primary);">Download Spec</h3>
                <p style="font-size:0.9rem; color:#64748b">Get the editable Word and PDF versions of this specification.</p>
                <a href="#" class="btn btn-accent">Download Package</a>
                <div style="font-size: 0.8rem; color: #94a3b8; text-align: center; margin-top: 10px;">
                    Format: .DOCX / .PDF<br>
                    CSI 3-Part Format
                </div>
                
                <div class="related-list">
                    <h4>Related Standards</h4>
                    <a href="#" class="related-link">NRCA Manual Reference</a>
                    <a href="#" class="related-link">FM Data Sheets</a>
                    <a href="#" class="related-link">ASTM Standards</a>
                    <a href="#" class="related-link">Installation Details</a>
                </div>
            </div>
            
            <div class="sidebar-box" style="margin-top: 20px; border-color: #fed7aa; background: #fff7ed;">
                <h4 style="margin-top:0; color: #9a3412;">🔧 Ask Roofio</h4>
                <p style="font-size:0.85rem; color:#78350f">Get instant answers about {name} specifications, installation, and compliance.</p>
                <a href="#" class="btn" style="background: var(--accent);">Open Roofio Chat &rarr;</a>
            </div>
        </aside>
    </div>

</body>
</html>
"""

# ---------------------------------------------------------
# TEMPLATE 2: THE MASTER INDEX (Roofio Library)
# ---------------------------------------------------------
index_template_start = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOFIO | Division 07 Specification Database</title>
    <meta name="description" content="The world's most comprehensive Division 07 specification database. Thermal and Moisture Protection standards from NRCA, FM Global, and industry leaders.">
    
    <style>
        :root {
            --primary: #0f172a;
            --accent: #f97316;
            --accent-dark: #ea580c;
            --bg: #f1f5f9;
            --border: #e2e8f0;
            --success: #10b981;
        }
        
        * { box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: var(--bg); 
            color: #1a202c; 
            margin: 0; 
        }
        
        .hero { 
            background: linear-gradient(135deg, var(--primary) 0%, #1e293b 100%);
            color: white; 
            padding: 80px 20px; 
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f97316' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .hero h1 { 
            margin: 0; 
            font-size: 3.5rem; 
            letter-spacing: -2px;
            font-weight: 900;
        }
        
        .hero h1 span { color: var(--accent); }
        
        .hero p { 
            color: #94a3b8; 
            font-size: 1.3rem; 
            max-width: 700px; 
            margin: 20px auto 0;
            line-height: 1.6;
        }
        
        .hero-stats {
            display: flex;
            justify-content: center;
            gap: 50px;
            margin-top: 40px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--accent);
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .container { 
            max-width: 1200px; 
            margin: -50px auto 60px; 
            padding: 0 20px; 
            position: relative;
            z-index: 2;
        }
        
        .search-box { 
            background: white; 
            padding: 25px; 
            border-radius: 16px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
            display: flex; 
            gap: 15px; 
            margin-bottom: 40px;
            align-items: center;
        }
        
        .search-input { 
            flex: 1; 
            padding: 18px 20px; 
            border: 2px solid var(--border); 
            border-radius: 10px; 
            font-size: 1.1rem;
            transition: border-color 0.2s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        .filter-btn {
            padding: 18px 25px;
            background: var(--bg);
            border: 2px solid var(--border);
            border-radius: 10px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .filter-btn:hover {
            background: white;
            border-color: var(--accent);
        }
        
        .filter-btn.active {
            background: var(--accent);
            border-color: var(--accent);
            color: white;
        }
        
        .category-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .cat-tab {
            padding: 10px 20px;
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .cat-tab:hover {
            border-color: var(--accent);
        }
        
        .cat-tab.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }
        
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); 
            gap: 25px; 
        }
        
        .card { 
            background: white; 
            border: 1px solid var(--border); 
            border-radius: 12px; 
            padding: 25px; 
            transition: all 0.2s; 
            text-decoration: none; 
            color: inherit; 
            display: block;
            position: relative;
        }
        
        .card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 12px 30px rgba(0,0,0,0.08); 
            border-color: var(--accent); 
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .code-badge { 
            background: var(--primary); 
            color: white; 
            padding: 6px 12px; 
            border-radius: 6px; 
            font-weight: bold; 
            font-family: monospace; 
            font-size: 0.9rem; 
        }
        
        .category-badge { 
            color: var(--accent); 
            font-size: 0.75rem; 
            font-weight: bold; 
            text-transform: uppercase;
            letter-spacing: 1px;
            background: #fff7ed;
            padding: 4px 10px;
            border-radius: 4px;
        }
        
        .card h3 { 
            margin: 0 0 10px; 
            font-size: 1.15rem;
            color: var(--primary);
        }
        
        .card p { 
            color: #64748b; 
            font-size: 0.9rem; 
            margin: 0; 
            line-height: 1.6; 
        }
        
        .card-footer {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .card-tag {
            font-size: 0.75rem;
            padding: 4px 8px;
            background: var(--bg);
            border-radius: 4px;
            color: #64748b;
        }
        
        footer {
            background: var(--primary);
            color: #64748b;
            padding: 40px 20px;
            text-align: center;
        }
        
        footer a {
            color: var(--accent);
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 2.5rem; }
            .hero-stats { flex-direction: column; gap: 20px; }
            .search-box { flex-direction: column; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div class="hero">
    <div class="hero-content">
        <h1>ROOF<span>IO</span></h1>
        <p>The world's most comprehensive Division 07 specification database. Thermal and Moisture Protection standards built by a 20-year journeyman, verified by industry leaders.</p>
        
        <div class="hero-stats">
            <div class="stat">
                <div class="stat-number" id="specCount">0</div>
                <div class="stat-label">Specifications</div>
            </div>
            <div class="stat">
                <div class="stat-number">14</div>
                <div class="stat-label">Technical Skills</div>
            </div>
            <div class="stat">
                <div class="stat-number">3</div>
                <div class="stat-label">Manufacturer Partners</div>
            </div>
        </div>
    </div>
</div>

<div class="container">
    <div class="search-box">
        <input type="text" class="search-input" placeholder="Search specs (e.g., '07 54 00', 'TPO', 'flashing')..." onkeyup="filterList()" id="searchInput">
    </div>
    
    <div class="category-tabs">
        <button class="cat-tab active" onclick="filterCategory('all')">All Specs</button>
        <button class="cat-tab" onclick="filterCategory('Membranes')">Membranes</button>
        <button class="cat-tab" onclick="filterCategory('Flashings')">Flashings</button>
        <button class="cat-tab" onclick="filterCategory('Insulation')">Insulation</button>
        <button class="cat-tab" onclick="filterCategory('Coatings')">Coatings</button>
        <button class="cat-tab" onclick="filterCategory('Sealants')">Sealants</button>
        <button class="cat-tab" onclick="filterCategory('Accessories')">Accessories</button>
    </div>

    <div class="grid" id="specGrid">
"""

index_template_end = """
    </div>
</div>

<footer>
    <p>&copy; 2025 <a href="#">Lefebvre Design Solutions</a>. ROOFIO - The Division 07 Digital Journeyman.</p>
    <p style="margin-top: 10px; font-size: 0.85rem;">Built with 20+ years of roofing expertise. Union proud.</p>
</footer>

<script>
// Count specs
document.addEventListener('DOMContentLoaded', function() {
    var cards = document.getElementsByClassName('card');
    document.getElementById('specCount').textContent = cards.length;
});

// Search filter
function filterList() {
    var input = document.getElementById('searchInput');
    var filter = input.value.toUpperCase();
    var grid = document.getElementById("specGrid");
    var cards = grid.getElementsByClassName('card');

    for (var i = 0; i < cards.length; i++) {
        var txtValue = cards[i].textContent || cards[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
}

// Category filter
function filterCategory(category) {
    var tabs = document.getElementsByClassName('cat-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    event.target.classList.add('active');
    
    var grid = document.getElementById("specGrid");
    var cards = grid.getElementsByClassName('card');
    
    for (var i = 0; i < cards.length; i++) {
        if (category === 'all') {
            cards[i].style.display = "";
        } else {
            var cardCategory = cards[i].getAttribute('data-category');
            if (cardCategory === category) {
                cards[i].style.display = "";
            } else {
                cards[i].style.display = "none";
            }
        }
    }
}
</script>

</body>
</html>
"""

# ---------------------------------------------------------
# THE ENGINE LOGIC
# ---------------------------------------------------------
def build_site():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✓ Created output directory: /{OUTPUT_DIR}")

    index_html_content = ""
    current_date = datetime.now().strftime("%B %Y")
    
    print("\n═══ ROOFIO Site Generator ═══\n")
    print("Reading specification data...")
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        print(f"Found {len(rows)} specifications\n")
        
        # 1. BUILD INDIVIDUAL PAGES
        for row in rows:
            safe_name = row['name'].lower().replace(' ', '-').replace(',', '').replace('/', '-').replace('(', '').replace(')', '')
            safe_code = row['code'].replace(' ', '-')
            filename = f"{safe_code}-{safe_name}.html"
            
            # Build related sections string
            related = row.get('related_sections', '')
            if related:
                related_lines = "\n".join([f"    {r.strip()}" for r in related.split(';')])
            else:
                related_lines = "    A. Related Division 07 sections as applicable."
            
            # Generate Page
            html = spec_template.format(
                code=row['code'],
                name=row['name'],
                name_upper=row['name'].upper(),
                name_lower=row['name'].lower(),
                description=row['description'],
                category=row['category'],
                manufacturer_hook=row.get('manufacturer_hook', 'Approved manufacturers'),
                related_sections=related_lines,
                date=current_date
            )
            
            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as out:
                out.write(html)
                
            print(f"  ✓ {row['code']} - {row['name'][:40]}...")
            
            # Get tags for card
            tags = row.get('tags', '').split(',') if row.get('tags') else []
            tags_html = ''.join([f'<span class="card-tag">{t.strip()}</span>' for t in tags[:3]])
            
            # Add to Index Content
            index_html_content += f"""
            <a href="{filename}" class="card" data-category="{row['category']}">
                <div class="card-header">
                    <span class="code-badge">{row['code']}</span>
                    <span class="category-badge">{row['category']}</span>
                </div>
                <h3>{row['name']}</h3>
                <p>{row['description'][:150]}{'...' if len(row['description']) > 150 else ''}</p>
                <div class="card-footer">
                    {tags_html}
                </div>
            </a>
            """

    # 2. BUILD MASTER INDEX
    final_index = index_template_start + index_html_content + index_template_end
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as idx:
        idx.write(final_index)
    
    print(f"\n✓ Generated index.html")
    print(f"\n═══ BUILD COMPLETE ═══")
    print(f"Open: {OUTPUT_DIR}/index.html")

if __name__ == "__main__":
    build_site()
