"""
Roof Page Filter
Pre-filters PDF pages to identify roof/waterproofing-related sheets.
Only sends relevant pages to AI vision (cost optimization).
"""
import re
from typing import List, Dict, Tuple
import PyPDF2


# ============================================================================
# KEYWORD SCORING
# ============================================================================

# ============================================================================
# DIVISION 07 - THERMAL AND MOISTURE PROTECTION (CSI MasterFormat)
# ============================================================================

# CSI Section numbers (Level 2 and 3) - regex patterns
DIVISION_07_SECTIONS = [
    # 07 10 00 - Dampproofing and Waterproofing
    r'\b07\s*1[0-9]\s*[0-9]{2}\b',
    r'\b07\s*11\s*00\b',  # Dampproofing
    r'\b07\s*13\s*00\b',  # Sheet Waterproofing
    r'\b07\s*14\s*00\b',  # Fluid-Applied Waterproofing
    r'\b07\s*16\s*00\b',  # Cementitious Waterproofing
    r'\b07\s*17\s*00\b',  # Bentonite Waterproofing
    r'\b07\s*18\s*00\b',  # Traffic Coatings
    r'\b07\s*19\s*00\b',  # Water Repellents

    # 07 20 00 - Thermal Protection
    r'\b07\s*2[0-9]\s*[0-9]{2}\b',
    r'\b07\s*21\s*00\b',  # Thermal Insulation
    r'\b07\s*22\s*00\b',  # Roof and Deck Insulation
    r'\b07\s*24\s*00\b',  # EIFS
    r'\b07\s*25\s*00\b',  # Weather Barriers
    r'\b07\s*26\s*00\b',  # Vapor Retarders
    r'\b07\s*27\s*00\b',  # Air Barriers

    # 07 30 00 - Steep Slope Roofing
    r'\b07\s*3[0-9]\s*[0-9]{2}\b',
    r'\b07\s*31\s*00\b',  # Shingles and Shakes
    r'\b07\s*32\s*00\b',  # Roof Tiles
    r'\b07\s*33\s*00\b',  # Natural Roof Coverings

    # 07 40 00 - Roofing and Siding Panels
    r'\b07\s*4[0-9]\s*[0-9]{2}\b',
    r'\b07\s*41\s*00\b',  # Roof Panels
    r'\b07\s*42\s*00\b',  # Wall Panels
    r'\b07\s*44\s*00\b',  # Faced Panels
    r'\b07\s*46\s*00\b',  # Siding

    # 07 50 00 - Membrane Roofing
    r'\b07\s*5[0-9]\s*[0-9]{2}\b',
    r'\b07\s*51\s*00\b',  # Built-Up Bituminous Roofing
    r'\b07\s*52\s*00\b',  # Modified Bituminous Membrane Roofing
    r'\b07\s*53\s*00\b',  # Elastomeric Membrane Roofing (EPDM)
    r'\b07\s*54\s*00\b',  # Thermoplastic Membrane Roofing (TPO/PVC)
    r'\b07\s*55\s*00\b',  # Protected Membrane Roofing
    r'\b07\s*56\s*00\b',  # Fluid-Applied Roofing
    r'\b07\s*57\s*00\b',  # Coated Foamed Roofing
    r'\b07\s*58\s*00\b',  # Roll Roofing

    # 07 60 00 - Flashing and Sheet Metal
    r'\b07\s*6[0-9]\s*[0-9]{2}\b',
    r'\b07\s*61\s*00\b',  # Sheet Metal Roofing
    r'\b07\s*62\s*00\b',  # Sheet Metal Flashing and Trim
    r'\b07\s*63\s*00\b',  # Sheet Metal Roofing Specialties
    r'\b07\s*65\s*00\b',  # Flexible Flashing

    # 07 70 00 - Roof and Wall Specialties
    r'\b07\s*7[0-9]\s*[0-9]{2}\b',
    r'\b07\s*71\s*00\b',  # Roof Specialties
    r'\b07\s*72\s*00\b',  # Roof Accessories
    r'\b07\s*76\s*00\b',  # Roof Pavers
    r'\b07\s*77\s*00\b',  # Wall Specialties

    # 07 90 00 - Joint Protection
    r'\b07\s*9[0-9]\s*[0-9]{2}\b',
    r'\b07\s*91\s*00\b',  # Preformed Joint Seals
    r'\b07\s*92\s*00\b',  # Joint Sealants
    r'\b07\s*95\s*00\b',  # Expansion Control
]

# High-value keywords (strong indicators) - Drawing titles + spec terms
HIGH_VALUE_KEYWORDS = [
    # Drawing titles
    r'\bROOF\s+PLAN\b',
    r'\bROOF\s+DETAIL[S]?\b',
    r'\bROOFING\s+DETAIL[S]?\b',
    r'\bROOF\s+FRAMING\b',
    r'\bROOF\s+DRAIN\s+SCHEDULE\b',
    r'\bROOFING\s+SCHEDULE\b',
    r'\bWATERPROOFING\s+PLAN\b',
    r'\bWATERPROOFING\s+DETAIL[S]?\b',
    r'\bMEMBRANE\s+ROOFING\b',
    r'\bROOF\s+ASSEMBLY\b',
    r'\bROOF\s+SECTION\b',

    # Spec section titles
    r'\bTHERMAL\s+AND\s+MOISTURE\s+PROTECTION\b',
    r'\bMEMBRANE\s+ROOFING\b',
    r'\bSHEET\s+METAL\s+FLASHING\b',
    r'\bBUILT.?UP\s+ROOFING\b',
    r'\bMODIFIED\s+BITUMINOUS\b',
    r'\bELASTOMERIC\s+MEMBRANE\b',
    r'\bTHERMOPLASTIC\s+MEMBRANE\b',
    r'\bFLUID.?APPLIED\s+ROOFING\b',
    r'\bROOF\s+INSULATION\b',
    r'\bROOF\s+RECOVER\b',
    r'\bRE.?ROOFING\b',
    r'\bROOF\s+REPLACEMENT\b',

    # Add Division 07 section patterns
] + DIVISION_07_SECTIONS

# Medium-value keywords - Material/system types
MEDIUM_VALUE_KEYWORDS = [
    # General terms
    r'\bROOF\b',
    r'\bROOFING\b',
    r'\bWATERPROOFING\b',
    r'\bPARAPET\b',
    r'\bCOPING\b',
    r'\bFLASHING\b',
    r'\bMEMBRANE\b',

    # Drainage
    r'\bROOF\s+DRAIN\b',
    r'\bSCUPPER\b',
    r'\bOVERFLOW\s+DRAIN\b',
    r'\bR\.?D\.?\b',  # RD abbreviation

    # Membrane types
    r'\bTPO\b',
    r'\bEPDM\b',
    r'\bPVC\s+(ROOF|MEMBRANE)\b',
    r'\bMOD\s*BIT\b',
    r'\bAPP\s+MODIFIED\b',
    r'\bSBS\s+MODIFIED\b',
    r'\bBUILT.?UP\s+ROOF\b',
    r'\bBUR\b',
    r'\bKEE\s*SHIELD\b',
    r'\bSINGLE.?PLY\b',

    # Insulation types
    r'\bPOLYISO\b',
    r'\bISO\s+BOARD\b',
    r'\bEPS\s+INSULATION\b',
    r'\bXPS\s+INSULATION\b',
    r'\bTAPER\s+SYSTEM\b',
    r'\bCOVERBOARD\b',
    r'\bDENSDECK\b',
    r'\bSECURROCK\b',

    # Barriers
    r'\bVAPOR\s+(BARRIER|RETARDER)\b',
    r'\bAIR\s+BARRIER\b',
    r'\bWEATHER\s+BARRIER\b',

    # Manufacturers
    r'\bCARLISLE\b',
    r'\bFIRESTONE\b',
    r'\bGAF\b',
    r'\bJOHNS\s+MANVILLE\b',
    r'\bVERSICO\b',
    r'\bSIPLAST\b',
    r'\bSOPREMA\b',
    r'\bMULE.?HIDE\b',
    r'\bTREMCO\b',
    r'\bSIKA\b',
    r'\bBARRETT\b',
    r'\bHENRY\b',
    r'\bCETCO\b',
]

# Lower-value but relevant keywords - Components/details
LOW_VALUE_KEYWORDS = [
    # Penetrations and curbs
    r'\bCURB\b',
    r'\bRTU\b',
    r'\bROOF\s*TOP\s*UNIT\b',
    r'\bPENETRATION\b',
    r'\bPIPE\s+BOOT\b',
    r'\bPITCH\s+(PAN|POCKET)\b',
    r'\bSKYLIGHT\b',
    r'\bHATCH\b',
    r'\bEQUIPMENT\s+SUPPORT\b',
    r'\bPIPE\s+SUPPORT\b',
    r'\bDUNNAGE\b',

    # Flashing components
    r'\bREGLET\b',
    r'\bCOUNTER\s*FLASHING\b',
    r'\bBASE\s+FLASHING\b',
    r'\bSTEP\s+FLASHING\b',
    r'\bVALLEY\s+FLASHING\b',
    r'\bDRIP\s+EDGE\b',
    r'\bGRAVEL\s+STOP\b',
    r'\bEDGE\s+METAL\b',
    r'\bFASCIA\b',

    # Accessories
    r'\bCANT\s+STRIP\b',
    r'\bTAPER\s+INSULATION\b',
    r'\bCRICKET\b',
    r'\bSADDLE\b',
    r'\bOVERFLOW\b',
    r'\bDRAINAGE\b',
    r'\bWALKWAY\s+PAD\b',
    r'\bROOF\s+PAVER\b',
    r'\bPROTECTION\s+MAT\b',
    r'\bSLIP\s+SHEET\b',

    # Fastening
    r'\bFASTENER\b',
    r'\bPLATE\b',
    r'\bMECHANICAL\s+ATTACHMENT\b',
    r'\bADHESIVE\b',
    r'\bFULLY\s+ADHERED\b',
    r'\bBALLAST\b',

    # Sealants
    r'\bSEALANT\b',
    r'\bCAULK\b',
    r'\bJOINT\s+SEALANT\b',
    r'\bURETHANE\s+SEALANT\b',
    r'\bSILICONE\b',

    # FM/UL/approvals
    r'\bFM\s+APPROVED\b',
    r'\bFM\s+GLOBAL\b',
    r'\bUL\s+LISTED\b',
    r'\bROOFNAV\b',
    r'\bI-?\s*90\b',  # Wind rating
    r'\bI-?\s*120\b',
]

# Sheet number patterns that suggest roof sheets
ROOF_SHEET_PATTERNS = [
    r'\bA-?[0-9]*\.?[45][0-9]{0,2}\b',  # A-401, A5.01, A-501, etc (often roof)
    r'\bAR-?[0-9]+\b',  # AR-1, AR-2 (Architectural Roof)
    r'\bR-?[0-9]+\b',   # R-1, R-2 (Roof sheets)
]

# Negative indicators (pages to potentially skip)
NEGATIVE_KEYWORDS = [
    r'\bFOUNDATION\s+PLAN\b',
    r'\bBASEMENT\s+PLAN\b',
    r'\bFLOOR\s+PLAN\b(?!.*ROOF)',  # Floor plan without "roof" context
    r'\bELECTRICAL\s+PLAN\b',
    r'\bPLUMBING\s+PLAN\b(?!.*ROOF)',
    r'\bMECHANICAL\s+PLAN\b(?!.*ROOF)',
    r'\bFIRE\s+PROTECTION\b',
    r'\bSPRINKLER\b',
]


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_page(text: str) -> Dict:
    """
    Score a page for roof/waterproofing relevance.
    Returns score and matched keywords.
    """
    text_upper = text.upper()

    score = 0
    matches = {
        'high': [],
        'medium': [],
        'low': [],
        'sheet_patterns': [],
        'negative': []
    }

    # Check high-value keywords (+10 points each)
    for pattern in HIGH_VALUE_KEYWORDS:
        found = re.findall(pattern, text_upper, re.IGNORECASE)
        if found:
            score += 10 * len(found)
            matches['high'].extend(found)

    # Check medium-value keywords (+5 points each)
    for pattern in MEDIUM_VALUE_KEYWORDS:
        found = re.findall(pattern, text_upper, re.IGNORECASE)
        if found:
            score += 5 * len(found)
            matches['medium'].extend(found)

    # Check low-value keywords (+2 points each)
    for pattern in LOW_VALUE_KEYWORDS:
        found = re.findall(pattern, text_upper, re.IGNORECASE)
        if found:
            score += 2 * len(found)
            matches['low'].extend(found)

    # Check sheet patterns (+8 points)
    for pattern in ROOF_SHEET_PATTERNS:
        found = re.findall(pattern, text_upper)
        if found:
            score += 8
            matches['sheet_patterns'].extend(found)

    # Check negative indicators (-15 points each)
    for pattern in NEGATIVE_KEYWORDS:
        found = re.findall(pattern, text_upper, re.IGNORECASE)
        if found:
            score -= 15 * len(found)
            matches['negative'].extend(found)

    return {
        'score': max(0, score),  # Don't go negative
        'matches': matches,
        'is_roof_page': score >= 10  # Threshold
    }


def extract_sheet_info(text: str) -> Dict:
    """
    Extract sheet number and title from page text.
    """
    info = {
        'sheet_number': None,
        'sheet_title': None
    }

    # Common sheet number patterns
    sheet_patterns = [
        r'\b([A-Z]{1,2}-?\d{1,3}\.?\d{0,2})\b',  # A-101, AR-1, A1.01
        r'SHEET\s*[:#]?\s*([A-Z0-9\-\.]+)',
        r'DWG\s*[:#]?\s*([A-Z0-9\-\.]+)',
    ]

    for pattern in sheet_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['sheet_number'] = match.group(1)
            break

    # Try to find sheet title
    title_patterns = [
        r'(ROOF\s+PLAN[S]?)',
        r'(ROOF\s+DETAIL[S]?)',
        r'(ROOFING\s+DETAIL[S]?)',
        r'(WATERPROOFING\s+PLAN)',
        r'(WATERPROOFING\s+DETAIL[S]?)',
        r'(ROOF\s+FRAMING\s+PLAN)',
        r'(ROOF\s+DRAIN\s+SCHEDULE)',
    ]

    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['sheet_title'] = match.group(1).upper()
            break

    return info


# ============================================================================
# MAIN FILTER FUNCTION
# ============================================================================

def filter_roof_pages(pdf_path: str, threshold: int = 10, verbose: bool = True) -> Dict:
    """
    Filter a PDF to find roof/waterproofing-related pages.

    Args:
        pdf_path: Path to PDF file
        threshold: Minimum score to consider a page relevant (default 10)
        verbose: Print progress and results

    Returns:
        Dict with:
            - roof_pages: List of (page_num, score, sheet_info) tuples
            - total_pages: Total pages in PDF
            - pages_to_process: Number of roof-related pages
            - savings_percent: Percentage of pages filtered out
    """
    result = {
        'roof_pages': [],
        'all_scores': [],
        'total_pages': 0,
        'pages_to_process': 0,
        'savings_percent': 0
    }

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            result['total_pages'] = total_pages

            if verbose:
                print(f"\n{'='*60}")
                print(f"🔍 SCANNING {total_pages} PAGES FOR ROOF CONTENT")
                print(f"{'='*60}\n")

            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text() or ""

                # Score the page
                page_score = score_page(text)
                sheet_info = extract_sheet_info(text)

                page_data = {
                    'page_num': page_num + 1,  # 1-indexed for display
                    'score': page_score['score'],
                    'is_roof_page': page_score['is_roof_page'],
                    'sheet_number': sheet_info['sheet_number'],
                    'sheet_title': sheet_info['sheet_title'],
                    'matches': page_score['matches']
                }

                result['all_scores'].append(page_data)

                if page_score['is_roof_page']:
                    result['roof_pages'].append(page_data)

                    if verbose:
                        sheet = sheet_info['sheet_number'] or f"Page {page_num + 1}"
                        title = sheet_info['sheet_title'] or "Roof-related content"
                        print(f"  ✓ {sheet}: {title} (score: {page_score['score']})")

                        # Show top matches
                        if page_score['matches']['high']:
                            print(f"      High: {', '.join(page_score['matches']['high'][:3])}")

            # Calculate stats
            result['pages_to_process'] = len(result['roof_pages'])
            if total_pages > 0:
                result['savings_percent'] = round(
                    (1 - result['pages_to_process'] / total_pages) * 100, 1
                )

            if verbose:
                print(f"\n{'='*60}")
                print(f"📊 RESULTS:")
                print(f"   Total pages: {total_pages}")
                print(f"   Roof pages found: {result['pages_to_process']}")
                print(f"   Pages filtered out: {total_pages - result['pages_to_process']}")
                print(f"   Cost savings: {result['savings_percent']}%")
                print(f"{'='*60}\n")

    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        result['error'] = str(e)

    return result


def get_roof_page_numbers(pdf_path: str, threshold: int = 10) -> List[int]:
    """
    Simple helper - returns just the page numbers (1-indexed) of roof pages.
    """
    result = filter_roof_pages(pdf_path, threshold, verbose=False)
    return [p['page_num'] for p in result['roof_pages']]


# ============================================================================
# CLI USAGE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python roof_page_filter.py <pdf_path> [threshold]")
        print("  pdf_path: Path to PDF file")
        print("  threshold: Minimum score (default 10)")
        sys.exit(1)

    pdf_path = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    result = filter_roof_pages(pdf_path, threshold)

    if result['roof_pages']:
        print("\n📋 ROOF PAGE NUMBERS TO PROCESS:")
        page_nums = [str(p['page_num']) for p in result['roof_pages']]
        print(f"   {', '.join(page_nums)}")
