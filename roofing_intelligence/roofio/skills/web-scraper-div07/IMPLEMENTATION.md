# Division 07 Web Scraper - Implementation

## Quick Start Code

### Installation

```bash
# Create project directory
mkdir div07_scraper
cd div07_scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install aiohttp beautifulsoup4 lxml sqlite-utils rich

# Create directory structure
mkdir -p data/scraped/{carlisle,firestone,gaf,nrca,fm_global,spri}
```

### Project Structure

```
div07_scraper/
├── __init__.py
├── core.py              # Base scraper class
├── database.py          # SQLite management
├── runner.py            # Orchestration
├── scheduler.py         # Update scheduling
├── schema.sql           # Database schema
├── config.py            # Configuration
│
├── manufacturers/
│   ├── __init__.py
│   ├── carlisle.py
│   ├── firestone.py
│   └── gaf.py
│
├── standards/
│   ├── __init__.py
│   ├── nrca.py
│   ├── fm_global.py
│   └── spri.py
│
└── data/
    ├── div07.db         # SQLite database
    └── scraped/         # Raw scraped data
```

---

## Complete Implementation Files

### config.py

```python
"""
Configuration for Division 07 scraper
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SCRAPED_DIR = DATA_DIR / "scraped"
DB_PATH = DATA_DIR / "div07.db"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
SCRAPED_DIR.mkdir(exist_ok=True)

# Rate limits (requests per second)
RATE_LIMITS = {
    "default": 1.0,
    "carlisle": 0.5,
    "firestone": 0.5,
    "gaf": 0.5,
    "nrca": 0.5,
    "fm_global": 0.3,
    "spri": 0.5,
}

# User agent
USER_AGENT = "Roofio-Div07-Indexer/1.0 (Building industry research)"

# Manufacturer URLs
MANUFACTURERS = {
    "carlisle": {
        "name": "Carlisle SynTec",
        "base_url": "https://www.carlislesyntec.com",
        "resources_url": "https://www.carlislesyntec.com/resources",
        "products_url": "https://www.carlislesyntec.com/products",
    },
    "firestone": {
        "name": "Firestone Building Products",
        "base_url": "https://www.firestonebpco.com",
        "resources_url": "https://www.firestonebpco.com/resources",
        "products_url": "https://www.firestonebpco.com/products",
    },
    "gaf": {
        "name": "GAF",
        "base_url": "https://www.gaf.com",
        "resources_url": "https://www.gaf.com/en-us/for-professionals/commercial-roofing",
        "products_url": "https://www.gaf.com/en-us/roofing-products/commercial-roofing-products",
    },
}

# Standards organizations
STANDARDS_ORGS = {
    "nrca": {
        "name": "National Roofing Contractors Association",
        "base_url": "https://www.nrca.net",
    },
    "fm_global": {
        "name": "FM Global",
        "base_url": "https://www.fmglobal.com",
    },
    "spri": {
        "name": "Single Ply Roofing Industry",
        "base_url": "https://www.spri.org",
    },
}
```

### core.py

```python
"""
Core scraper framework
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import hashlib
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse
import re

from .config import USER_AGENT, RATE_LIMITS, SCRAPED_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Result from a scrape operation"""
    url: str
    status: str
    data: Dict[str, Any]
    timestamp: datetime
    checksum: str
    source: str = ""


class RateLimiter:
    """Respectful rate limiting per domain"""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.delay = 1.0 / requests_per_second
        self.last_request: Dict[str, float] = {}
    
    async def wait(self, domain: str = "default"):
        now = asyncio.get_event_loop().time()
        last = self.last_request.get(domain, 0)
        wait_time = self.delay - (now - last)
        
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        
        self.last_request[domain] = asyncio.get_event_loop().time()


class Div07Scraper:
    """Base scraper class"""
    
    def __init__(
        self,
        source_name: str,
        base_url: str,
        rate_limit: float = None
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.output_dir = SCRAPED_DIR / source_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        rate = rate_limit or RATE_LIMITS.get(source_name, RATE_LIMITS["default"])
        self.rate_limiter = RateLimiter(rate)
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.scraped_urls: set = set()
        self.results: List[ScrapeResult] = []
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT},
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch URL with rate limiting"""
        
        domain = urlparse(url).netloc
        await self.rate_limiter.wait(domain)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.scraped_urls.add(url)
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status}: {url}")
                    return None
        except Exception as e:
            logger.error(f"Fetch error {url}: {e}")
            return None
    
    def parse(self, html: str) -> BeautifulSoup:
        """Parse HTML"""
        return BeautifulSoup(html, 'lxml')
    
    def extract_links(
        self,
        soup: BeautifulSoup,
        pattern: str = None,
        selector: str = "a[href]"
    ) -> List[str]:
        """Extract links matching pattern"""
        
        links = []
        for a in soup.select(selector):
            href = a.get('href', '')
            if not href or href.startswith('#'):
                continue
            
            full_url = urljoin(self.base_url, href)
            
            if pattern and not re.search(pattern, full_url, re.I):
                continue
            
            links.append(full_url)
        
        return list(set(links))
    
    def extract_pdfs(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract PDF links with metadata"""
        
        pdfs = []
        for a in soup.select('a[href*=".pdf"]'):
            href = a.get('href', '')
            full_url = urljoin(self.base_url, href)
            
            pdfs.append({
                "url": full_url,
                "title": a.get_text(strip=True) or Path(href).stem,
                "format": "pdf"
            })
        
        return pdfs
    
    def compute_checksum(self, data: Dict) -> str:
        """Compute checksum for change detection"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_result(self, result: ScrapeResult):
        """Save result to disk"""
        
        url_hash = hashlib.md5(result.url.encode()).hexdigest()[:12]
        filename = f"{url_hash}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                "url": result.url,
                "status": result.status,
                "source": self.source_name,
                "data": result.data,
                "timestamp": result.timestamp.isoformat(),
                "checksum": result.checksum
            }, f, indent=2)
        
        self.results.append(result)
        logger.info(f"Saved: {result.data.get('title', result.url)[:50]}")
    
    def create_result(self, url: str, data: Dict, status: str = "success") -> ScrapeResult:
        """Create a scrape result"""
        return ScrapeResult(
            url=url,
            status=status,
            data=data,
            timestamp=datetime.now(),
            checksum=self.compute_checksum(data),
            source=self.source_name
        )
    
    async def scrape(self):
        """Override in subclasses"""
        raise NotImplementedError("Subclasses must implement scrape()")
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            "source": self.source_name,
            "urls_scraped": len(self.scraped_urls),
            "results_saved": len(self.results),
            "successful": len([r for r in self.results if r.status == "success"]),
            "errors": len([r for r in self.results if r.status == "error"]),
        }
```

### manufacturers/carlisle.py

```python
"""
Carlisle SynTec scraper
"""

import re
from ..core import Div07Scraper, logger
from ..config import MANUFACTURERS


class CarlisleScraper(Div07Scraper):
    """Scraper for Carlisle SynTec Systems"""
    
    def __init__(self):
        config = MANUFACTURERS["carlisle"]
        super().__init__(
            source_name="carlisle",
            base_url=config["base_url"]
        )
        self.resources_url = config["resources_url"]
        self.products_url = config["products_url"]
    
    async def scrape(self):
        """Main scraping routine"""
        logger.info("Starting Carlisle scrape...")
        
        # Scrape main resource page for document links
        await self.scrape_resources_page()
        
        # Scrape product categories
        await self.scrape_products()
        
        logger.info(f"Carlisle complete: {self.get_stats()}")
    
    async def scrape_resources_page(self):
        """Scrape the main resources page"""
        
        html = await self.fetch(self.resources_url)
        if not html:
            return
        
        soup = self.parse(html)
        
        # Get all PDF links
        pdfs = self.extract_pdfs(soup)
        
        for pdf in pdfs:
            # Categorize by URL/title patterns
            doc_type = self.categorize_document(pdf["title"], pdf["url"])
            
            data = {
                "type": "document",
                "document_type": doc_type,
                "manufacturer": "Carlisle",
                "title": pdf["title"],
                "url": pdf["url"],
                "format": "pdf"
            }
            
            result = self.create_result(pdf["url"], data)
            self.save_result(result)
        
        # Get links to sub-pages
        resource_links = self.extract_links(
            soup,
            pattern=r"(technical|data-sheet|specification|detail|cad)",
        )
        
        for link in resource_links[:20]:  # Limit for initial scrape
            await self.scrape_resource_subpage(link)
    
    async def scrape_resource_subpage(self, url: str):
        """Scrape a resource sub-page"""
        
        html = await self.fetch(url)
        if not html:
            return
        
        soup = self.parse(html)
        pdfs = self.extract_pdfs(soup)
        
        for pdf in pdfs:
            doc_type = self.categorize_document(pdf["title"], pdf["url"])
            
            data = {
                "type": "document",
                "document_type": doc_type,
                "manufacturer": "Carlisle",
                "title": pdf["title"],
                "url": pdf["url"],
                "format": "pdf",
                "source_page": url
            }
            
            result = self.create_result(pdf["url"], data)
            self.save_result(result)
    
    async def scrape_products(self):
        """Scrape product listings"""
        
        categories = [
            "/products/tpo",
            "/products/epdm", 
            "/products/pvc",
            "/products/insulation",
        ]
        
        for cat_path in categories:
            url = f"{self.base_url}{cat_path}"
            html = await self.fetch(url)
            
            if not html:
                continue
            
            soup = self.parse(html)
            category = cat_path.split("/")[-1].upper()
            
            # Look for product elements
            products = soup.select('.product-item, .product-card, [class*="product"]')
            
            for prod in products:
                name_elem = prod.select_one('h2, h3, h4, .title, .name')
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                
                link_elem = prod.select_one('a[href]')
                prod_url = ""
                if link_elem:
                    prod_url = urljoin(self.base_url, link_elem['href'])
                
                desc_elem = prod.select_one('p, .description, .desc')
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                data = {
                    "type": "product",
                    "manufacturer": "Carlisle",
                    "name": name,
                    "category": category,
                    "description": description,
                    "url": prod_url,
                    "spec_section": self.get_spec_section(category)
                }
                
                result = self.create_result(prod_url or url, data)
                self.save_result(result)
    
    def categorize_document(self, title: str, url: str) -> str:
        """Categorize document by title/URL patterns"""
        
        text = f"{title} {url}".lower()
        
        if any(x in text for x in ["tds", "technical data", "data sheet"]):
            return "technical_data_sheet"
        elif any(x in text for x in ["sds", "safety data", "msds"]):
            return "safety_data_sheet"
        elif any(x in text for x in ["install", "application", "guide"]):
            return "installation_guide"
        elif any(x in text for x in ["spec", "csi", "masterspec"]):
            return "specification"
        elif any(x in text for x in ["cad", "dwg", "detail"]):
            return "cad_detail"
        elif any(x in text for x in ["warranty"]):
            return "warranty"
        else:
            return "document"
    
    def get_spec_section(self, category: str) -> str:
        """Map category to spec section"""
        
        mapping = {
            "TPO": "07 54 00",
            "EPDM": "07 55 00",
            "PVC": "07 54 00",
            "INSULATION": "07 22 00",
            "MODIFIED": "07 52 00",
        }
        return mapping.get(category.upper(), "07 00 00")
```

### manufacturers/firestone.py

```python
"""
Firestone Building Products scraper
"""

from ..core import Div07Scraper, logger
from ..config import MANUFACTURERS


class FirestoneScraper(Div07Scraper):
    """Scraper for Firestone Building Products"""
    
    def __init__(self):
        config = MANUFACTURERS["firestone"]
        super().__init__(
            source_name="firestone",
            base_url=config["base_url"]
        )
    
    async def scrape(self):
        """Main scraping routine"""
        logger.info("Starting Firestone scrape...")
        
        # Similar structure to Carlisle
        await self.scrape_resources()
        await self.scrape_products()
        
        logger.info(f"Firestone complete: {self.get_stats()}")
    
    async def scrape_resources(self):
        """Scrape resources section"""
        
        url = f"{self.base_url}/resources"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse(html)
        pdfs = self.extract_pdfs(soup)
        
        for pdf in pdfs:
            data = {
                "type": "document",
                "manufacturer": "Firestone",
                "title": pdf["title"],
                "url": pdf["url"],
                "format": "pdf"
            }
            result = self.create_result(pdf["url"], data)
            self.save_result(result)
    
    async def scrape_products(self):
        """Scrape product information"""
        
        url = f"{self.base_url}/products"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse(html)
        
        # Extract product links
        product_links = self.extract_links(soup, pattern=r"/products/")
        
        for link in product_links[:15]:
            await self.scrape_product_page(link)
    
    async def scrape_product_page(self, url: str):
        """Scrape individual product page"""
        
        html = await self.fetch(url)
        if not html:
            return
        
        soup = self.parse(html)
        
        title = soup.select_one('h1')
        title_text = title.get_text(strip=True) if title else "Unknown"
        
        data = {
            "type": "product",
            "manufacturer": "Firestone",
            "name": title_text,
            "url": url,
        }
        
        # Get associated documents
        pdfs = self.extract_pdfs(soup)
        if pdfs:
            data["documents"] = pdfs
        
        result = self.create_result(url, data)
        self.save_result(result)
```

### manufacturers/gaf.py

```python
"""
GAF Commercial scraper
"""

from ..core import Div07Scraper, logger
from ..config import MANUFACTURERS


class GAFScraper(Div07Scraper):
    """Scraper for GAF Commercial"""
    
    def __init__(self):
        config = MANUFACTURERS["gaf"]
        super().__init__(
            source_name="gaf",
            base_url=config["base_url"]
        )
    
    async def scrape(self):
        """Main scraping routine"""
        logger.info("Starting GAF scrape...")
        
        await self.scrape_commercial_products()
        
        logger.info(f"GAF complete: {self.get_stats()}")
    
    async def scrape_commercial_products(self):
        """Scrape commercial product section"""
        
        url = f"{self.base_url}/en-us/roofing-products/commercial-roofing-products"
        html = await self.fetch(url)
        
        if not html:
            return
        
        soup = self.parse(html)
        
        # Get PDFs
        pdfs = self.extract_pdfs(soup)
        for pdf in pdfs:
            data = {
                "type": "document",
                "manufacturer": "GAF",
                "title": pdf["title"],
                "url": pdf["url"],
                "format": "pdf"
            }
            result = self.create_result(pdf["url"], data)
            self.save_result(result)
        
        # Get product links
        product_links = self.extract_links(
            soup,
            pattern=r"commercial.*product|everguard"
        )
        
        for link in product_links[:15]:
            await self.scrape_product_page(link)
    
    async def scrape_product_page(self, url: str):
        """Scrape product page"""
        
        html = await self.fetch(url)
        if not html:
            return
        
        soup = self.parse(html)
        
        title = soup.select_one('h1')
        
        data = {
            "type": "product",
            "manufacturer": "GAF",
            "name": title.get_text(strip=True) if title else "Unknown",
            "url": url,
        }
        
        pdfs = self.extract_pdfs(soup)
        if pdfs:
            data["documents"] = pdfs
        
        result = self.create_result(url, data)
        self.save_result(result)
```

### runner.py

```python
"""
Main runner for Division 07 scraper
"""

import asyncio
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table

from .manufacturers.carlisle import CarlisleScraper
from .manufacturers.firestone import FirestoneScraper
from .manufacturers.gaf import GAFScraper
from .database import Div07Database

console = Console()


class ScraperOrchestrator:
    """Orchestrates all scraping operations"""
    
    def __init__(self):
        self.db = Div07Database()
        
        self.scrapers = {
            "carlisle": CarlisleScraper,
            "firestone": FirestoneScraper,
            "gaf": GAFScraper,
        }
        
        self.results = {}
    
    async def run_scraper(self, name: str):
        """Run a single scraper"""
        
        console.print(f"[blue]Starting {name} scraper...[/blue]")
        
        scraper_class = self.scrapers.get(name)
        if not scraper_class:
            console.print(f"[red]Unknown scraper: {name}[/red]")
            return
        
        async with scraper_class() as scraper:
            await scraper.scrape()
            stats = scraper.get_stats()
            self.results[name] = stats
            
            # Import to database
            for result in scraper.results:
                if result.status == "success":
                    self.db.add_scraped_item(result.data)
            
            console.print(f"[green]✓ {name}: {stats['results_saved']} items[/green]")
    
    async def run_all(self):
        """Run all scrapers sequentially"""
        
        for name in self.scrapers:
            await self.run_scraper(name)
    
    async def run_manufacturers(self):
        """Run manufacturer scrapers"""
        
        for name in ["carlisle", "firestone", "gaf"]:
            await self.run_scraper(name)
    
    def print_summary(self):
        """Print summary table"""
        
        table = Table(title="Scraping Summary")
        table.add_column("Source")
        table.add_column("URLs Scraped")
        table.add_column("Items Saved")
        table.add_column("Errors")
        
        for name, stats in self.results.items():
            table.add_row(
                name,
                str(stats["urls_scraped"]),
                str(stats["results_saved"]),
                str(stats["errors"])
            )
        
        console.print(table)
        
        # Database stats
        db_stats = self.db.get_stats()
        console.print(f"\n[bold]Database totals:[/bold]")
        for key, value in db_stats.items():
            console.print(f"  {key}: {value}")


async def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Division 07 Web Scraper - Build the world's largest roofing database"
    )
    parser.add_argument(
        "--source",
        choices=["carlisle", "firestone", "gaf", "all"],
        default="all",
        help="Source to scrape"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scrapers"
    )
    
    args = parser.parse_args()
    
    orchestrator = ScraperOrchestrator()
    
    if args.list:
        console.print("[bold]Available scrapers:[/bold]")
        for name in orchestrator.scrapers:
            console.print(f"  - {name}")
        return
    
    console.print("[bold cyan]═══ ROOFIO Division 07 Scraper ═══[/bold cyan]\n")
    
    start_time = datetime.now()
    
    if args.source == "all":
        await orchestrator.run_all()
    else:
        await orchestrator.run_scraper(args.source)
    
    elapsed = datetime.now() - start_time
    
    console.print(f"\n[bold]Completed in {elapsed.total_seconds():.1f} seconds[/bold]")
    orchestrator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
```

### database.py

```python
"""
SQLite database for Division 07 data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from .config import DB_PATH


class Div07Database:
    """Database manager"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                item_type TEXT NOT NULL,
                title TEXT,
                url TEXT UNIQUE,
                data JSON,
                checksum TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_items_source ON items(source);
            CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
        """)
        self.conn.commit()
    
    def add_scraped_item(self, data: Dict) -> int:
        """Add a scraped item"""
        
        cursor = self.conn.execute("""
            INSERT OR REPLACE INTO items (source, item_type, title, url, data, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("manufacturer", data.get("source", "unknown")),
            data.get("type", "unknown"),
            data.get("title", data.get("name", "")),
            data.get("url", ""),
            json.dumps(data),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search items"""
        
        cursor = self.conn.execute("""
            SELECT * FROM items
            WHERE title LIKE ? OR data LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_source(self, source: str) -> List[Dict]:
        """Get items by source"""
        
        cursor = self.conn.execute(
            "SELECT * FROM items WHERE source = ?",
            (source,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_type(self, item_type: str) -> List[Dict]:
        """Get items by type"""
        
        cursor = self.conn.execute(
            "SELECT * FROM items WHERE item_type = ?",
            (item_type,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        
        stats = {}
        
        # Total items
        cursor = self.conn.execute("SELECT COUNT(*) FROM items")
        stats["total_items"] = cursor.fetchone()[0]
        
        # By source
        cursor = self.conn.execute("""
            SELECT source, COUNT(*) as count
            FROM items GROUP BY source
        """)
        stats["by_source"] = {row["source"]: row["count"] for row in cursor.fetchall()}
        
        # By type
        cursor = self.conn.execute("""
            SELECT item_type, COUNT(*) as count
            FROM items GROUP BY item_type
        """)
        stats["by_type"] = {row["item_type"]: row["count"] for row in cursor.fetchall()}
        
        return stats
    
    def close(self):
        self.conn.close()
```

---

## Running the Scraper

```bash
# Run all scrapers
python -m div07_scraper.runner

# Run specific manufacturer
python -m div07_scraper.runner --source carlisle

# List available scrapers
python -m div07_scraper.runner --list
```

---

## Expected Output

```
═══ ROOFIO Division 07 Scraper ═══

Starting carlisle scraper...
Saved: Sure-Weld TPO Technical Data Sheet
Saved: Sure-Seal EPDM Installation Guide
Saved: 60 mil TPO Membrane
...
✓ carlisle: 47 items

Starting firestone scraper...
...
✓ firestone: 38 items

Starting gaf scraper...
...
✓ gaf: 42 items

Completed in 45.3 seconds

┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Source     ┃ URLs Scraped  ┃ Items Saved ┃ Errors ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
│ carlisle   │ 23            │ 47          │ 0      │
│ firestone  │ 18            │ 38          │ 0      │
│ gaf        │ 15            │ 42          │ 0      │
└────────────┴───────────────┴─────────────┴────────┘

Database totals:
  total_items: 127
  by_source: {'carlisle': 47, 'firestone': 38, 'gaf': 42}
  by_type: {'document': 89, 'product': 38}
```
