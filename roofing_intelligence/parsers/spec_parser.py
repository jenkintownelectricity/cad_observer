"""
Specification Parser - Extracts roofing system requirements from specs

Focuses on Division 07 specifications:
- 07 50 00 Membrane Roofing
- 07 62 00 Sheet Metal Flashing
- 07 27 00 Air Barriers
- 07 92 00 Joint Sealants
"""

import re
from .base_parser import BaseParser, ParserResult, ConfidenceLevel


class SpecificationParser(BaseParser):
    """Parser for construction specifications, focused on roofing/waterproofing"""

    def __init__(self):
        super().__init__()
        self.doc_type = "specs"
        self.version = "1.0.0"

        # Known manufacturers and systems
        self.manufacturers = [
            'Carlisle', 'Firestone', 'Johns Manville', 'JM',
            'GAF', 'Sika Sarnafil', 'Sarnafil', 'Tremco',
            'Versico', 'GenFlex', 'Duro-Last', 'IKO',
            'CertainTeed', 'Soprema', 'Henry', 'Polyglass'
        ]

        self.membrane_types = [
            'TPO', 'EPDM', 'PVC', 'KEE', 'modified bitumen',
            'mod bit', 'BUR', 'built-up', 'single-ply',
            'hot-applied', 'cold-applied', 'torch-applied'
        ]

        self.insulation_types = [
            'polyiso', 'polyisocyanurate', 'EPS', 'XPS',
            'mineral wool', 'perlite', 'wood fiber',
            'lightweight insulating concrete', 'LWIC'
        ]

    def _extract_data(self, content: str, result: ParserResult):
        """Extract specification data"""

        # -----------------------------------------------------------------
        # MEMBRANE SYSTEM
        # -----------------------------------------------------------------

        # Find membrane type and thickness
        for membrane in self.membrane_types:
            pattern = rf'{membrane}.*?(\d+)\s*(?:mil|mm)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result.add_suggestion(
                    'membrane_type',
                    f"{membrane} {match.group(1)} mil",
                    ConfidenceLevel.HIGH,
                    source_text=match.group(0)
                )
                break

        # Find manufacturer
        for mfr in self.manufacturers:
            if re.search(rf'\b{mfr}\b', content, re.IGNORECASE):
                result.add_suggestion(
                    'membrane_manufacturer',
                    mfr,
                    ConfidenceLevel.HIGH,
                    source_text=f"Found: {mfr}"
                )
                break

        # Attachment method
        attachment_patterns = {
            'fully adhered': r'fully\s*adhered',
            'mechanically attached': r'mechanic(?:ally)?\s*(?:attached|fastened)',
            'ballasted': r'ballast(?:ed)?',
            'induction welded': r'induction\s*weld',
        }
        for method, pattern in attachment_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                result.add_suggestion(
                    'attachment_method',
                    method,
                    ConfidenceLevel.HIGH,
                    source_text=method
                )
                break

        # -----------------------------------------------------------------
        # INSULATION
        # -----------------------------------------------------------------

        # R-value requirement
        r_match = re.search(r'R-?(\d+(?:\.\d+)?)', content)
        if r_match:
            result.add_suggestion(
                'r_value_required',
                f"R-{r_match.group(1)}",
                ConfidenceLevel.HIGH,
                source_text=r_match.group(0)
            )

        # Insulation type
        for insul in self.insulation_types:
            if re.search(rf'\b{insul}\b', content, re.IGNORECASE):
                result.add_suggestion(
                    'insulation_type',
                    insul,
                    ConfidenceLevel.MEDIUM,
                    source_text=f"Found: {insul}"
                )
                break

        # -----------------------------------------------------------------
        # WARRANTY REQUIREMENTS
        # -----------------------------------------------------------------

        warranty_patterns = [
            (r'(\d+)\s*year.*?(?:NDL|no dollar limit)', 'NDL'),
            (r'(\d+)\s*year.*?warranty', 'standard'),
            (r'(?:NDL|no dollar limit).*?(\d+)\s*year', 'NDL'),
        ]

        for pattern, warranty_type in warranty_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                years = match.group(1)
                result.add_suggestion(
                    'warranty_required',
                    f"{years}-year {warranty_type}",
                    ConfidenceLevel.HIGH,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # WIND UPLIFT
        # -----------------------------------------------------------------

        fm_match = re.search(r'FM\s*(\d-\d+)', content)
        if fm_match:
            result.add_suggestion(
                'wind_uplift_rating',
                f"FM {fm_match.group(1)}",
                ConfidenceLevel.HIGH,
                source_text=fm_match.group(0)
            )

        # -----------------------------------------------------------------
        # FLAGS
        # -----------------------------------------------------------------

        # Flag if specific manufacturer is REQUIRED
        if re.search(r'(?:shall be|must be|required).*?(?:Carlisle|Firestone|GAF)', content, re.IGNORECASE):
            result.add_flag(
                'info',
                'Specific manufacturer appears to be required (not "or equal")',
                severity=2
            )

        # Flag high wind uplift requirements
        if re.search(r'FM\s*1-(?:120|150|180)', content):
            result.add_flag(
                'info',
                'High wind uplift requirement - verify fastening pattern',
                severity=2
            )
