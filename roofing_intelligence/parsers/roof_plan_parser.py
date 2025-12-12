"""
Roof Plan Parser - Extracts quantities from roof drawings

Parses roof plans/drawings to extract:
- Total roof area (SF)
- Drains (primary and overflow)
- Coping/edge metal (LF)
- Penetrations (RTUs, VTRs, pipes)
- Skylights
"""

import re
from .base_parser import BaseParser, ParserResult, ConfidenceLevel


class RoofPlanParser(BaseParser):
    """Parser for roof plan drawings and area takeoffs"""

    def __init__(self):
        super().__init__()
        self.doc_type = "roof-plan"
        self.version = "1.0.0"

    def _extract_data(self, content: str, result: ParserResult):
        """Extract roof plan quantities"""

        # -----------------------------------------------------------------
        # ROOF AREA
        # -----------------------------------------------------------------
        area_patterns = [
            r'(?:total|roof)\s*area[:\s]+(\d[\d,]+)\s*(?:SF|sq\.?\s*ft)',
            r'(\d[\d,]+)\s*(?:SF|square feet)\s*(?:total|roof)',
            r'(\d[\d,]+)\s*SF',
        ]

        for pattern in area_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                area = match.group(1).replace(',', '')
                result.add_suggestion(
                    'total_roof_area',
                    f"{int(area):,} SF",
                    ConfidenceLevel.MEDIUM,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # DRAINS
        # -----------------------------------------------------------------

        # Primary drains
        drain_patterns = [
            r'(\d+)\s*(?:roof\s*)?drains?',
            r'drains?[:\s]+(\d+)',
            r'RD[:\s]*(\d+)',
        ]

        for pattern in drain_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result.add_suggestion(
                    'roof_drains',
                    f"{match.group(1)} drains",
                    ConfidenceLevel.MEDIUM,
                    source_text=match.group(0)
                )
                break

        # Overflow drains
        overflow_match = re.search(
            r'(\d+)\s*(?:overflow|secondary)\s*drains?',
            content, re.IGNORECASE
        )
        if overflow_match:
            result.add_suggestion(
                'overflow_drains',
                f"{overflow_match.group(1)} overflow",
                ConfidenceLevel.MEDIUM,
                source_text=overflow_match.group(0)
            )

        # -----------------------------------------------------------------
        # COPING / EDGE METAL
        # -----------------------------------------------------------------
        coping_patterns = [
            r'coping[:\s]+(\d[\d,]*)\s*(?:LF|linear)',
            r'(\d[\d,]*)\s*(?:LF|linear).*?coping',
            r'edge\s*metal[:\s]+(\d[\d,]*)\s*(?:LF|linear)',
        ]

        for pattern in coping_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                lf = match.group(1).replace(',', '')
                result.add_suggestion(
                    'coping_lf',
                    f"{int(lf):,} LF coping",
                    ConfidenceLevel.MEDIUM,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # RTUs (Rooftop Units)
        # -----------------------------------------------------------------
        rtu_match = re.search(r'(\d+)\s*RTUs?', content, re.IGNORECASE)
        if rtu_match:
            result.add_suggestion(
                'rtus',
                f"{rtu_match.group(1)} RTUs",
                ConfidenceLevel.HIGH,
                source_text=rtu_match.group(0)
            )

        # -----------------------------------------------------------------
        # VTRs (Vent Through Roof)
        # -----------------------------------------------------------------
        vtr_match = re.search(r'(\d+)\s*VTRs?', content, re.IGNORECASE)
        if vtr_match:
            result.add_suggestion(
                'vtrs',
                f"{vtr_match.group(1)} VTRs",
                ConfidenceLevel.HIGH,
                source_text=vtr_match.group(0)
            )

        # -----------------------------------------------------------------
        # SKYLIGHTS
        # -----------------------------------------------------------------
        skylight_match = re.search(r'(\d+)\s*skylights?', content, re.IGNORECASE)
        if skylight_match:
            result.add_suggestion(
                'skylights',
                f"{skylight_match.group(1)} skylights",
                ConfidenceLevel.HIGH,
                source_text=skylight_match.group(0)
            )

        # -----------------------------------------------------------------
        # PENETRATIONS (generic)
        # -----------------------------------------------------------------
        pen_match = re.search(
            r'(\d+)\s*(?:total\s*)?penetrations?',
            content, re.IGNORECASE
        )
        if pen_match:
            result.add_suggestion(
                'penetrations',
                f"{pen_match.group(1)} penetrations",
                ConfidenceLevel.LOW,
                source_text=pen_match.group(0)
            )

        # -----------------------------------------------------------------
        # ROOF SLOPE
        # -----------------------------------------------------------------
        slope_patterns = [
            r'slope[:\s]+(\d+/\d+)[:\s]*(?:per foot|/ft)',
            r'(\d+/\d+)[:\s]*(?:per foot|/ft)',
            r'(\d+)\s*%\s*slope',
        ]

        for pattern in slope_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result.add_suggestion(
                    'roof_slope',
                    match.group(1),
                    ConfidenceLevel.MEDIUM,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # FLAGS
        # -----------------------------------------------------------------

        # Flag if multiple roof areas detected
        if re.search(r'(?:area|roof)\s*[A-Z]', content, re.IGNORECASE):
            result.add_flag(
                'info',
                'Multiple roof areas detected - verify totals',
                severity=1
            )

        # Flag if crickets mentioned
        if re.search(r'\bcrickets?\b', content, re.IGNORECASE):
            result.add_flag(
                'info',
                'Crickets/saddles indicated - include in drainage plan',
                severity=1
            )
