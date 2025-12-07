# Division 07 Web Scraper & Database

## ROOFIO - Division 07 Expert System

### Mission
Build and maintain the world's most comprehensive Division 07 (Thermal & Moisture Protection) database through systematic web scraping, API integration, and data organization.

---

## TARGET DATA SOURCES

### Tier 1: Standards Organizations (Priority)

| Source | URL | Data Type | Update Freq |
|--------|-----|-----------|-------------|
| NRCA | nrca.net | Guidelines, best practices | Quarterly |
| SPRI | spri.org | Standards, wind data | Quarterly |
| FM Global | fmglobal.com | Data sheets, approvals | Monthly |
| IIBEC | iibec.org | Technical papers | Monthly |
| ASTM | astm.org | Standards (metadata) | Annual |
| ICC | iccsafe.org | Code updates | 3-year cycle |
| ASCE | asce.org | ASCE 7 updates | 6-year cycle |

### Tier 2: Manufacturer Technical Libraries

**Big 3 (Immediate):**
| Manufacturer | Technical Portal | Data Types |
|--------------|------------------|------------|
| Carlisle | carlislesyntec.com/resources | TDS, SDS, details, specs |
| Firestone | firestonebpco.com/resources | TDS, SDS, details, specs |
| GAF | gaf.com/commercial | TDS, SDS, details, specs |

**Week 2-4 Expansion:**
| Manufacturer | Portal | Priority |
|--------------|--------|----------|
| Johns Manville | jm.com | High |
| Sika Sarnafil | usa.sarnafil.sika.com | High |
| Tremco | tremcoinc.com | High |
| Versico | versico.com | Medium |
| Soprema | soprema.us | Medium |
| IKO | iko.com | Medium |
| Duro-Last | duro-last.com | Medium |

**Week 5+ Expansion:**
- Insulation manufacturers
- Fastener manufacturers
- Edge metal manufacturers
- Adhesive/sealant manufacturers
- Accessory manufacturers

### Tier 3: Government & Code Resources

| Source | URL | Data |
|--------|-----|------|
| OSHA | osha.gov | Safety regulations |
| EPA | epa.gov | Environmental regs |
| DOE | energy.gov | Energy codes |
| FEMA | fema.gov | Flood/wind maps |
| NOAA | noaa.gov | Weather data |
| USGS | usgs.gov | Seismic data |

### Tier 4: Industry Publications

| Source | Type | Frequency |
|--------|------|-----------|
| Roofing Contractor | Trade publication | Monthly |
| Professional Roofing | NRCA magazine | Monthly |
| Building Enclosure | IIBEC journal | Quarterly |
| RSI (Roofing Siding Insulation) | Trade pub | Monthly |

### Tier 5: Research & Academic

| Source | Data Type |
|--------|-----------|
| Oak Ridge National Lab | Building science |
| NIST | Standards research |
| University building science programs | Research papers |
| DOE Building Technologies | Energy research |

---

## DATA SCHEMA

### Master Product Database

```python
class Product:
    """Single roofing/waterproofing product"""
    
    # Identity
    id: str                    # Unique identifier
    manufacturer: str          # Manufacturer name
    product_name: str          # Official product name
    product_family: str        # Product line/family
    
    # Classification
    category: str              # membrane, insulation, flashing, etc.
    subcategory: str           # tpo, epdm, polyiso, etc.
    spec_section: str          # 07 54 00, 07 22 00, etc.
    
    # Technical Data
    thickness: List[str]       # Available thicknesses
    width: List[str]           # Available widths
    length: List[str]          # Available lengths
    color: List[str]           # Available colors
    
    # Performance
    r_value: float             # Per inch (insulation)
    wind_rating: str           # FM rating
    fire_rating: str           # Class A, B, C
    hail_rating: str           # SH, MH, VH
    
    # Compliance
    fm_approval: str           # FM approval number
    ul_listing: str            # UL file number
    miami_dade_noa: str        # NOA number
    florida_approval: str      # FL product approval
    
    # Documents
    tds_url: str               # Technical data sheet
    sds_url: str               # Safety data sheet
    install_guide_url: str     # Installation guide
    warranty_url: str          # Warranty document
    cad_details_url: str       # CAD details
    
    # Metadata
    last_updated: datetime
    source_url: str
    scrape_date: datetime


class Assembly:
    """Complete roof assembly"""
    
    id: str
    name: str
    manufacturer: str
    
    # Components (ordered bottom to top)
    components: List[AssemblyComponent]
    
    # Ratings
    fm_rating_field: str       # Zone 1
    fm_rating_perimeter: str   # Zone 2
    fm_rating_corner: str      # Zone 3
    fire_class: str
    hail_rating: str
    
    # Application
    deck_types: List[str]
    slope_range: str
    attachment_method: str
    
    # Source
    roofnav_id: str
    source_url: str
    last_updated: datetime


class AssemblyComponent:
    """Single layer in assembly"""
    
    layer_number: int
    product_id: str            # Reference to Product
    thickness: str
    attachment: str            # adhered, mechanical, loose
    fastener_pattern: str      # If mechanical
    adhesive_rate: str         # If adhered


class Detail:
    """CAD detail/drawing"""
    
    id: str
    name: str
    manufacturer: str
    
    # Classification
    detail_type: str           # flashing, drain, penetration, etc.
    condition: str             # wall, curb, edge, etc.
    
    # Systems
    applicable_systems: List[str]  # TPO, EPDM, etc.
    
    # Files
    dwg_url: str
    pdf_url: str
    
    # Metadata
    version: str
    last_updated: datetime


class Specification:
    """Specification section"""
    
    id: str
    section_number: str        # 07 54 00
    section_title: str
    manufacturer: str
    
    # Content
    part1_general: str
    part2_products: str
    part3_execution: str
    
    # Versions
    format: str                # CSI 3-part, MasterSpec, etc.
    version: str
    last_updated: datetime
    
    # Files
    doc_url: str
    pdf_url: str


class Standard:
    """Industry standard (ASTM, FM, etc.)"""
    
    id: str
    standard_number: str       # ASTM D6878
    title: str
    organization: str          # ASTM, FM, UL, etc.
    
    # Content
    scope: str
    key_requirements: List[str]
    test_methods: List[str]
    
    # Applicability
    product_types: List[str]
    spec_sections: List[str]
    
    # Metadata
    current_version: str
    effective_date: date
    supersedes: str
    last_updated: datetime
```

### Relational Structure

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Product   │────▶│  Assembly   │────▶│   Detail    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Standard   │     │    Spec     │     │  Document   │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## SCRAPING IMPLEMENTATION

### Core Scraper Framework

```python
"""
div07_scraper/core.py
Core scraping framework for Division 07 data
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import hashlib
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Result from a scrape operation"""
    url: str
    status: str  # success, error, skipped
    data: Dict[str, Any]
    timestamp: datetime
    checksum: str  # For change detection


class RateLimiter:
    """Respectful rate limiting"""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.delay = 1.0 / requests_per_second
        self.last_request = 0
    
    async def wait(self):
        now = asyncio.get_event_loop().time()
        wait_time = self.delay - (now - self.last_request)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self.last_request = asyncio.get_event_loop().time()


class Div07Scraper:
    """Base scraper class for Division 07 sources"""
    
    def __init__(
        self,
        source_name: str,
        base_url: str,
        output_dir: str = "./data/scraped",
        rate_limit: float = 1.0  # requests per second
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.output_dir = Path(output_dir) / source_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limiter = RateLimiter(rate_limit)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Tracking
        self.scraped_urls = set()
        self.results: List[ScrapeResult] = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Roofio-Div07-Indexer/1.0 (Building industry research)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL with rate limiting"""
        
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def fetch_binary(self, url: str) -> Optional[bytes]:
        """Fetch binary content (PDFs, etc.)"""
        
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url, timeout=60) as response:
                if response.status == 200:
                    return await response.read()
                return None
        except Exception as e:
            logger.error(f"Error fetching binary {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_links(self, soup: BeautifulSoup, pattern: str = None) -> List[str]:
        """Extract links matching optional pattern"""
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(self.base_url, href)
            
            if pattern and not re.search(pattern, full_url):
                continue
            
            links.append(full_url)
        
        return list(set(links))
    
    def save_result(self, result: ScrapeResult):
        """Save scrape result to disk"""
        
        # Generate filename from URL
        url_hash = hashlib.md5(result.url.encode()).hexdigest()[:12]
        filename = f"{url_hash}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump({
                "url": result.url,
                "status": result.status,
                "data": result.data,
                "timestamp": result.timestamp.isoformat(),
                "checksum": result.checksum
            }, f, indent=2)
        
        self.results.append(result)
    
    def compute_checksum(self, data: Dict) -> str:
        """Compute checksum for change detection"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def scrape(self):
        """Override in subclasses"""
        raise NotImplementedError
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            "source": self.source_name,
            "urls_scraped": len(self.scraped_urls),
            "successful": len([r for r in self.results if r.status == "success"]),
            "errors": len([r for r in self.results if r.status == "error"]),
        }
```

### Manufacturer Scraper (Carlisle Example)

```python
"""
div07_scraper/manufacturers/carlisle.py
Scraper for Carlisle SynTec technical resources
"""

from ..core import Div07Scraper, ScrapeResult
from datetime import datetime
import re


class CarlisleScraper(Div07Scraper):
    """Scraper for Carlisle SynTec Systems"""
    
    def __init__(self):
        super().__init__(
            source_name="carlisle",
            base_url="https://www.carlislesyntec.com",
            rate_limit=0.5  # Be respectful
        )
        
        # Known resource URLs
        self.resource_sections = [
            "/resources/documents",
            "/resources/technical-data-sheets",
            "/resources/safety-data-sheets",
            "/resources/cad-details",
            "/resources/specifications",
        ]
    
    async def scrape(self):
        """Main scraping routine"""
        
        logger.info(f"Starting Carlisle scrape")
        
        # 1. Scrape product catalog
        await self.scrape_products()
        
        # 2. Scrape technical documents
        await self.scrape_technical_docs()
        
        # 3. Scrape CAD details
        await self.scrape_cad_details()
        
        # 4. Scrape specifications
        await self.scrape_specifications()
        
        logger.info(f"Carlisle scrape complete: {self.get_stats()}")
    
    async def scrape_products(self):
        """Scrape product information"""
        
        # Product category pages
        categories = [
            "/products/tpo-roofing",
            "/products/epdm-roofing",
            "/products/pvc-roofing",
            "/products/insulation",
            "/products/accessories",
        ]
        
        for category_path in categories:
            url = f"{self.base_url}{category_path}"
            html = await self.fetch(url)
            
            if not html:
                continue
            
            soup = self.parse_html(html)
            products = self.extract_products(soup, category_path)
            
            for product in products:
                result = ScrapeResult(
                    url=product.get("url", url),
                    status="success",
                    data=product,
                    timestamp=datetime.now(),
                    checksum=self.compute_checksum(product)
                )
                self.save_result(result)
    
    def extract_products(self, soup, category: str) -> list:
        """Extract product data from category page"""
        
        products = []
        
        # Look for product cards/listings
        product_elements = soup.select('.product-card, .product-item, [data-product]')
        
        for elem in product_elements:
            product = {
                "manufacturer": "Carlisle",
                "category": category.split("/")[-1],
                "name": "",
                "description": "",
                "url": "",
                "specs": {}
            }
            
            # Extract name
            name_elem = elem.select_one('h2, h3, .product-name, .title')
            if name_elem:
                product["name"] = name_elem.get_text(strip=True)
            
            # Extract link
            link = elem.select_one('a')
            if link and link.get('href'):
                product["url"] = urljoin(self.base_url, link['href'])
            
            # Extract description
            desc = elem.select_one('.description, .product-desc, p')
            if desc:
                product["description"] = desc.get_text(strip=True)
            
            if product["name"]:
                products.append(product)
        
        return products
    
    async def scrape_technical_docs(self):
        """Scrape technical data sheets"""
        
        url = f"{self.base_url}/resources/technical-data-sheets"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse_html(html)
        
        # Find PDF links
        pdf_links = soup.select('a[href*=".pdf"]')
        
        for link in pdf_links:
            href = link.get('href')
            full_url = urljoin(self.base_url, href)
            
            doc_data = {
                "type": "technical_data_sheet",
                "manufacturer": "Carlisle",
                "title": link.get_text(strip=True),
                "url": full_url,
                "format": "pdf"
            }
            
            result = ScrapeResult(
                url=full_url,
                status="success",
                data=doc_data,
                timestamp=datetime.now(),
                checksum=self.compute_checksum(doc_data)
            )
            self.save_result(result)
    
    async def scrape_cad_details(self):
        """Scrape CAD detail library"""
        
        url = f"{self.base_url}/resources/cad-details"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse_html(html)
        
        # Look for DWG/DXF downloads
        cad_links = soup.select('a[href*=".dwg"], a[href*=".dxf"], a[href*=".zip"]')
        
        for link in cad_links:
            href = link.get('href')
            full_url = urljoin(self.base_url, href)
            
            detail_data = {
                "type": "cad_detail",
                "manufacturer": "Carlisle",
                "title": link.get_text(strip=True),
                "url": full_url,
                "format": href.split('.')[-1]
            }
            
            result = ScrapeResult(
                url=full_url,
                status="success",
                data=detail_data,
                timestamp=datetime.now(),
                checksum=self.compute_checksum(detail_data)
            )
            self.save_result(result)
    
    async def scrape_specifications(self):
        """Scrape specification documents"""
        
        url = f"{self.base_url}/resources/specifications"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse_html(html)
        
        # Find spec documents
        spec_links = soup.select('a[href*="spec"], a[href*=".doc"], a[href*=".docx"]')
        
        for link in spec_links:
            href = link.get('href')
            full_url = urljoin(self.base_url, href)
            
            spec_data = {
                "type": "specification",
                "manufacturer": "Carlisle",
                "title": link.get_text(strip=True),
                "url": full_url,
            }
            
            result = ScrapeResult(
                url=full_url,
                status="success",
                data=spec_data,
                timestamp=datetime.now(),
                checksum=self.compute_checksum(spec_data)
            )
            self.save_result(result)
```

### NRCA Scraper

```python
"""
div07_scraper/standards/nrca.py
Scraper for NRCA resources
"""

from ..core import Div07Scraper, ScrapeResult
from datetime import datetime


class NRCAScraper(Div07Scraper):
    """Scraper for NRCA technical resources"""
    
    def __init__(self):
        super().__init__(
            source_name="nrca",
            base_url="https://www.nrca.net",
            rate_limit=0.5
        )
    
    async def scrape(self):
        """Scrape NRCA resources"""
        
        # Technical publications
        await self.scrape_publications()
        
        # Technical bulletins
        await self.scrape_bulletins()
        
        # Guidelines
        await self.scrape_guidelines()
    
    async def scrape_publications(self):
        """Scrape NRCA publication listings"""
        
        url = f"{self.base_url}/technical/publications"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse_html(html)
        
        # Extract publication information
        # (Structure depends on actual site)
        publications = soup.select('.publication, .resource-item')
        
        for pub in publications:
            pub_data = {
                "type": "publication",
                "source": "NRCA",
                "title": "",
                "description": "",
                "url": ""
            }
            
            title = pub.select_one('h3, .title')
            if title:
                pub_data["title"] = title.get_text(strip=True)
            
            link = pub.select_one('a')
            if link:
                pub_data["url"] = urljoin(self.base_url, link.get('href', ''))
            
            if pub_data["title"]:
                result = ScrapeResult(
                    url=pub_data["url"],
                    status="success",
                    data=pub_data,
                    timestamp=datetime.now(),
                    checksum=self.compute_checksum(pub_data)
                )
                self.save_result(result)
    
    async def scrape_bulletins(self):
        """Scrape technical bulletins"""
        pass  # Similar implementation
    
    async def scrape_guidelines(self):
        """Scrape guideline documents"""
        pass  # Similar implementation
```

### FM Global Scraper

```python
"""
div07_scraper/standards/fm_global.py
Scraper for FM Global Data Sheets
"""

from ..core import Div07Scraper, ScrapeResult
from datetime import datetime


class FMGlobalScraper(Div07Scraper):
    """Scraper for FM Global resources"""
    
    # Known roofing data sheets
    ROOFING_DATA_SHEETS = [
        ("1-28", "Wind Design"),
        ("1-29", "Roof Deck Securement"),
        ("1-31", "Metal Roof Systems"),
        ("1-32", "Vegetated Roof Systems"),
        ("1-34", "Hail Damage"),
        ("1-49", "Perimeter Flashing"),
        ("1-52", "Field Verification"),
        ("1-54", "Roof Loads"),
    ]
    
    def __init__(self):
        super().__init__(
            source_name="fm_global",
            base_url="https://www.fmglobal.com",
            rate_limit=0.3  # Very respectful
        )
    
    async def scrape(self):
        """Scrape FM Global resources"""
        
        # Data sheet index
        await self.scrape_data_sheets()
        
        # Approval guide
        await self.scrape_approvals()
    
    async def scrape_data_sheets(self):
        """Scrape data sheet listings"""
        
        url = f"{self.base_url}/research-and-resources/fm-global-data-sheets"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse_html(html)
        
        # Record known data sheets
        for ds_num, ds_title in self.ROOFING_DATA_SHEETS:
            ds_data = {
                "type": "data_sheet",
                "source": "FM Global",
                "number": ds_num,
                "title": ds_title,
                "category": "roofing",
                "url": f"{self.base_url}/research/datasteets/{ds_num}"
            }
            
            result = ScrapeResult(
                url=ds_data["url"],
                status="success",
                data=ds_data,
                timestamp=datetime.now(),
                checksum=self.compute_checksum(ds_data)
            )
            self.save_result(result)
    
    async def scrape_approvals(self):
        """Scrape approval guide product listings"""
        
        # FM Approvals has separate site
        url = "https://www.approvalguide.com"
        # Would need to handle their search/filter interface
        pass
```

---

## DATABASE STORAGE

### SQLite Schema (Local Development)

```sql
-- products.sql

CREATE TABLE manufacturers (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    website TEXT,
    technical_portal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    name TEXT NOT NULL,
    product_family TEXT,
    category TEXT,
    subcategory TEXT,
    spec_section TEXT,
    
    -- Technical specs (JSON for flexibility)
    specifications JSON,
    
    -- Ratings
    fm_approval TEXT,
    ul_listing TEXT,
    miami_dade_noa TEXT,
    
    -- Documents
    tds_url TEXT,
    sds_url TEXT,
    install_guide_url TEXT,
    
    -- Metadata
    source_url TEXT,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(manufacturer_id, name)
);

CREATE TABLE assemblies (
    id INTEGER PRIMARY KEY,
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    name TEXT NOT NULL,
    
    -- Components (JSON array)
    components JSON,
    
    -- Ratings
    fm_rating_field TEXT,
    fm_rating_perimeter TEXT,
    fm_rating_corner TEXT,
    fire_class TEXT,
    hail_rating TEXT,
    
    -- Application
    deck_types JSON,
    slope_range TEXT,
    attachment_method TEXT,
    
    -- Source
    roofnav_id TEXT,
    source_url TEXT,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE details (
    id INTEGER PRIMARY KEY,
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    name TEXT NOT NULL,
    detail_type TEXT,
    condition TEXT,
    
    applicable_systems JSON,
    
    dwg_url TEXT,
    pdf_url TEXT,
    
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE standards (
    id INTEGER PRIMARY KEY,
    organization TEXT NOT NULL,
    standard_number TEXT NOT NULL,
    title TEXT,
    scope TEXT,
    
    key_requirements JSON,
    test_methods JSON,
    
    product_types JSON,
    spec_sections JSON,
    
    current_version TEXT,
    effective_date DATE,
    
    source_url TEXT,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization, standard_number)
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    document_type TEXT,
    title TEXT,
    url TEXT UNIQUE,
    
    file_format TEXT,
    file_size INTEGER,
    
    -- Content extraction
    extracted_text TEXT,
    keywords JSON,
    
    scraped_at TIMESTAMP,
    last_checked TIMESTAMP,
    checksum TEXT
);

-- Indexes for fast queries
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_spec_section ON products(spec_section);
CREATE INDEX idx_assemblies_fm_rating ON assemblies(fm_rating_field);
CREATE INDEX idx_standards_org ON standards(organization);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Full-text search
CREATE VIRTUAL TABLE products_fts USING fts5(
    name, product_family, category, subcategory,
    content=products
);

CREATE VIRTUAL TABLE documents_fts USING fts5(
    title, extracted_text,
    content=documents
);
```

### Database Manager

```python
"""
div07_scraper/database.py
Database management for Division 07 data
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class Div07Database:
    """Database manager for Division 07 scraped data"""
    
    def __init__(self, db_path: str = "./data/div07.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path) as f:
                self.conn.executescript(f.read())
        self.conn.commit()
    
    # Manufacturers
    def add_manufacturer(self, name: str, website: str = None) -> int:
        cursor = self.conn.execute(
            "INSERT OR IGNORE INTO manufacturers (name, website) VALUES (?, ?)",
            (name, website)
        )
        self.conn.commit()
        
        # Get ID
        cursor = self.conn.execute(
            "SELECT id FROM manufacturers WHERE name = ?", (name,)
        )
        return cursor.fetchone()["id"]
    
    # Products
    def add_product(self, product: Dict) -> int:
        """Add or update a product"""
        
        manufacturer_id = self.add_manufacturer(product["manufacturer"])
        
        cursor = self.conn.execute("""
            INSERT INTO products (
                manufacturer_id, name, product_family, category,
                subcategory, spec_section, specifications,
                fm_approval, ul_listing, miami_dade_noa,
                tds_url, sds_url, install_guide_url,
                source_url, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(manufacturer_id, name) DO UPDATE SET
                specifications = excluded.specifications,
                last_updated = excluded.last_updated
        """, (
            manufacturer_id,
            product.get("name"),
            product.get("product_family"),
            product.get("category"),
            product.get("subcategory"),
            product.get("spec_section"),
            json.dumps(product.get("specifications", {})),
            product.get("fm_approval"),
            product.get("ul_listing"),
            product.get("miami_dade_noa"),
            product.get("tds_url"),
            product.get("sds_url"),
            product.get("install_guide_url"),
            product.get("source_url"),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    # Search
    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search for products"""
        
        cursor = self.conn.execute("""
            SELECT p.*, m.name as manufacturer_name
            FROM products_fts
            JOIN products p ON products_fts.rowid = p.id
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE products_fts MATCH ?
            LIMIT ?
        """, (query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        
        cursor = self.conn.execute("""
            SELECT p.*, m.name as manufacturer_name
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE p.category = ?
            ORDER BY m.name, p.name
        """, (category,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_products_by_spec_section(self, section: str) -> List[Dict]:
        """Get products by spec section"""
        
        cursor = self.conn.execute("""
            SELECT p.*, m.name as manufacturer_name
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE p.spec_section LIKE ?
            ORDER BY m.name, p.name
        """, (f"{section}%",))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Statistics
    def get_stats(self) -> Dict:
        """Get database statistics"""
        
        stats = {}
        
        for table in ["manufacturers", "products", "assemblies", "details", "standards", "documents"]:
            cursor = self.conn.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = cursor.fetchone()["count"]
        
        return stats
    
    def close(self):
        self.conn.close()
```

---

## ORCHESTRATION

### Main Scraper Runner

```python
"""
div07_scraper/runner.py
Orchestrates all scraping operations
"""

import asyncio
from datetime import datetime
from typing import List

from .core import Div07Scraper
from .manufacturers.carlisle import CarlisleScraper
from .manufacturers.firestone import FirestoneScraper
from .manufacturers.gaf import GAFScraper
from .standards.nrca import NRCAScraper
from .standards.fm_global import FMGlobalScraper
from .standards.spri import SPRIScraper
from .database import Div07Database


class ScraperOrchestrator:
    """Orchestrates all Division 07 scraping"""
    
    def __init__(self, db_path: str = "./data/div07.db"):
        self.db = Div07Database(db_path)
        
        # Register all scrapers
        self.scrapers = {
            # Tier 1: Priority manufacturers
            "carlisle": CarlisleScraper,
            "firestone": FirestoneScraper,
            "gaf": GAFScraper,
            
            # Tier 2: Standards organizations
            "nrca": NRCAScraper,
            "fm_global": FMGlobalScraper,
            "spri": SPRIScraper,
        }
        
        self.results = {}
    
    async def run_scraper(self, name: str):
        """Run a single scraper"""
        
        if name not in self.scrapers:
            raise ValueError(f"Unknown scraper: {name}")
        
        scraper_class = self.scrapers[name]
        
        async with scraper_class() as scraper:
            await scraper.scrape()
            self.results[name] = scraper.get_stats()
            
            # Import to database
            for result in scraper.results:
                if result.status == "success":
                    self.import_result(result)
    
    async def run_all(self, parallel: int = 2):
        """Run all scrapers with limited parallelism"""
        
        names = list(self.scrapers.keys())
        
        for i in range(0, len(names), parallel):
            batch = names[i:i + parallel]
            await asyncio.gather(*[
                self.run_scraper(name) for name in batch
            ])
    
    async def run_manufacturers(self):
        """Run only manufacturer scrapers"""
        
        manufacturer_scrapers = ["carlisle", "firestone", "gaf"]
        await asyncio.gather(*[
            self.run_scraper(name) for name in manufacturer_scrapers
        ])
    
    async def run_standards(self):
        """Run only standards organization scrapers"""
        
        standards_scrapers = ["nrca", "fm_global", "spri"]
        await asyncio.gather(*[
            self.run_scraper(name) for name in standards_scrapers
        ])
    
    def import_result(self, result):
        """Import scrape result to database"""
        
        data = result.data
        data_type = data.get("type", "unknown")
        
        if data_type == "product":
            self.db.add_product(data)
        # ... handle other types
    
    def get_summary(self) -> Dict:
        """Get summary of all scraping"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "scrapers": self.results,
            "database": self.db.get_stats()
        }


# CLI Interface
async def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Division 07 Web Scraper")
    parser.add_argument("--source", help="Specific source to scrape")
    parser.add_argument("--manufacturers", action="store_true", help="Scrape manufacturers only")
    parser.add_argument("--standards", action="store_true", help="Scrape standards only")
    parser.add_argument("--all", action="store_true", help="Scrape all sources")
    
    args = parser.parse_args()
    
    orchestrator = ScraperOrchestrator()
    
    if args.source:
        await orchestrator.run_scraper(args.source)
    elif args.manufacturers:
        await orchestrator.run_manufacturers()
    elif args.standards:
        await orchestrator.run_standards()
    elif args.all:
        await orchestrator.run_all()
    else:
        # Default: run all
        await orchestrator.run_all()
    
    print(orchestrator.get_summary())


if __name__ == "__main__":
    asyncio.run(main())
```

---

## SCHEDULING

### Update Schedule

```python
"""
div07_scraper/scheduler.py
Scheduling for regular updates
"""

from datetime import datetime, timedelta
from typing import Dict

# Update frequencies by source type
UPDATE_SCHEDULE = {
    # Manufacturers - monthly (product data changes)
    "carlisle": timedelta(days=30),
    "firestone": timedelta(days=30),
    "gaf": timedelta(days=30),
    
    # Standards - quarterly (less frequent changes)
    "nrca": timedelta(days=90),
    "fm_global": timedelta(days=90),
    "spri": timedelta(days=90),
    
    # Codes - annually (update cycles)
    "icc": timedelta(days=365),
    
    # Weather/hazard data - weekly
    "noaa": timedelta(days=7),
}

def get_due_scrapers(last_runs: Dict[str, datetime]) -> list:
    """Get list of scrapers due for update"""
    
    now = datetime.now()
    due = []
    
    for source, interval in UPDATE_SCHEDULE.items():
        last_run = last_runs.get(source)
        
        if last_run is None or (now - last_run) > interval:
            due.append(source)
    
    return due
```

---

## LEGAL & ETHICAL

### Compliance Rules

```yaml
# robots.txt compliance
respect_robots_txt: true

# Rate limiting (requests per second)
rate_limits:
  default: 1.0
  manufacturer_sites: 0.5
  government_sites: 0.3
  
# User agent identification
user_agent: "Roofio-Div07-Indexer/1.0 (Building industry research; contact@example.com)"

# Data usage
permitted_uses:
  - Internal reference
  - Product comparison
  - Specification assistance
  - Training data (with attribution)
  
prohibited_uses:
  - Republishing copyrighted content verbatim
  - Commercial redistribution
  - Competitive intelligence scraping
  
# Attribution requirements
always_attribute:
  - Source URL
  - Scrape date
  - Original author/organization
```

### Terms of Service Compliance

**Before scraping any site:**
1. Check robots.txt
2. Review Terms of Service
3. Respect rate limits
4. Identify crawler appropriately
5. Cache aggressively (don't re-fetch)
6. Store metadata, link to originals

---

## QUICK START

```bash
# Install dependencies
pip install aiohttp beautifulsoup4 lxml

# Run initial scrape (Big 3 manufacturers)
python -m div07_scraper.runner --manufacturers

# Run standards organizations
python -m div07_scraper.runner --standards

# Run everything
python -m div07_scraper.runner --all

# Check database stats
python -c "from div07_scraper.database import Div07Database; print(Div07Database().get_stats())"
```

---

## EXPANSION ROADMAP

### Phase 1 (Weeks 1-2): Foundation
- [x] Core scraper framework
- [x] Database schema
- [ ] Big 3 manufacturers (Carlisle, Firestone, GAF)
- [ ] NRCA, FM Global, SPRI

### Phase 2 (Weeks 3-4): Expansion
- [ ] Johns Manville, Sika, Tremco
- [ ] IIBEC, ASTM metadata
- [ ] Code resources (ICC, IRC)

### Phase 3 (Weeks 5-8): Depth
- [ ] All major manufacturers
- [ ] PDF text extraction
- [ ] CAD detail parsing
- [ ] Full-text search optimization

### Phase 4 (Ongoing): Maintenance
- [ ] Automated update scheduling
- [ ] Change detection
- [ ] Quality monitoring
- [ ] API for Roofio queries
