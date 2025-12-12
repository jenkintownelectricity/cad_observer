"""
Schedule of Values Parser - Extracts billing breakdown

Parses SOV/AIA G703 documents to extract:
- Line items and descriptions
- Scheduled values
- Completed work percentages
- Retainage amounts
"""

import re
from .base_parser import BaseParser, ParserResult, ConfidenceLevel


class ScheduleOfValuesParser(BaseParser):
    """Parser for Schedule of Values and AIA G703 documents"""

    def __init__(self):
        super().__init__()
        self.doc_type = "sov"
        self.version = "1.0.0"

    def _extract_data(self, content: str, result: ParserResult):
        """Extract SOV data"""

        # -----------------------------------------------------------------
        # TOTAL CONTRACT VALUE
        # -----------------------------------------------------------------
        total_patterns = [
            r'(?:total|contract)\s*(?:sum|value|amount)[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:total|contract)',
            r'original\s*contract[:\s]+\$?([\d,]+(?:\.\d{2})?)',
        ]

        for pattern in total_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                result.add_suggestion(
                    'total_contract_value',
                    f"${float(value):,.2f}",
                    ConfidenceLevel.HIGH,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # CHANGE ORDER TOTAL
        # -----------------------------------------------------------------
        co_match = re.search(
            r'change\s*orders?[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            content, re.IGNORECASE
        )
        if co_match:
            value = co_match.group(1).replace(',', '')
            result.add_suggestion(
                'change_orders_total',
                f"${float(value):,.2f}",
                ConfidenceLevel.MEDIUM,
                source_text=co_match.group(0)
            )

        # -----------------------------------------------------------------
        # WORK COMPLETED
        # -----------------------------------------------------------------
        completed_patterns = [
            r'(?:total|work)\s*completed[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            r'completed\s*to\s*date[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            r'billed\s*to\s*date[:\s]+\$?([\d,]+(?:\.\d{2})?)',
        ]

        for pattern in completed_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                result.add_suggestion(
                    'work_completed_value',
                    f"${float(value):,.2f}",
                    ConfidenceLevel.MEDIUM,
                    source_text=match.group(0)
                )
                break

        # -----------------------------------------------------------------
        # PERCENT COMPLETE
        # -----------------------------------------------------------------
        pct_match = re.search(
            r'(\d+(?:\.\d+)?)\s*%\s*(?:complete|finished)',
            content, re.IGNORECASE
        )
        if pct_match:
            result.add_suggestion(
                'percent_complete',
                f"{pct_match.group(1)}%",
                ConfidenceLevel.HIGH,
                source_text=pct_match.group(0)
            )

        # -----------------------------------------------------------------
        # RETAINAGE
        # -----------------------------------------------------------------
        ret_patterns = [
            r'retainage[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            r'retainage\s*(?:held|withheld)[:\s]+\$?([\d,]+(?:\.\d{2})?)',
        ]

        for pattern in ret_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                result.add_suggestion(
                    'retainage_held',
                    f"${float(value):,.2f}",
                    ConfidenceLevel.HIGH,
                    source_text=match.group(0)
                )
                break

        # Retainage percentage
        ret_pct = re.search(r'retainage[:\s]+(\d+(?:\.\d+)?)\s*%', content, re.IGNORECASE)
        if ret_pct:
            result.add_suggestion(
                'retainage_percent',
                f"{ret_pct.group(1)}%",
                ConfidenceLevel.HIGH,
                source_text=ret_pct.group(0)
            )

        # -----------------------------------------------------------------
        # BALANCE TO FINISH
        # -----------------------------------------------------------------
        balance_match = re.search(
            r'balance\s*(?:to finish|remaining)[:\s]+\$?([\d,]+(?:\.\d{2})?)',
            content, re.IGNORECASE
        )
        if balance_match:
            value = balance_match.group(1).replace(',', '')
            result.add_suggestion(
                'balance_to_finish',
                f"${float(value):,.2f}",
                ConfidenceLevel.MEDIUM,
                source_text=balance_match.group(0)
            )

        # -----------------------------------------------------------------
        # LINE ITEMS (extract common roofing categories)
        # -----------------------------------------------------------------
        line_item_patterns = [
            (r'mobilization[:\s]+\$?([\d,]+)', 'mobilization'),
            (r'tear[- ]?off[:\s]+\$?([\d,]+)', 'tear_off'),
            (r'insulation[:\s]+\$?([\d,]+)', 'insulation'),
            (r'membrane[:\s]+\$?([\d,]+)', 'membrane'),
            (r'sheet\s*metal[:\s]+\$?([\d,]+)', 'sheet_metal'),
            (r'flashings?[:\s]+\$?([\d,]+)', 'flashing'),
            (r'closeout[:\s]+\$?([\d,]+)', 'closeout'),
        ]

        for pattern, field_name in line_item_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                result.add_suggestion(
                    f'line_item_{field_name}',
                    f"${float(value):,.2f}",
                    ConfidenceLevel.LOW,
                    source_text=match.group(0)
                )

        # -----------------------------------------------------------------
        # APPLICATION NUMBER
        # -----------------------------------------------------------------
        app_match = re.search(
            r'application\s*(?:no\.?|number|#)[:\s]*(\d+)',
            content, re.IGNORECASE
        )
        if app_match:
            result.add_suggestion(
                'application_number',
                f"#{app_match.group(1)}",
                ConfidenceLevel.HIGH,
                source_text=app_match.group(0)
            )

        # -----------------------------------------------------------------
        # PERIOD COVERED
        # -----------------------------------------------------------------
        period_match = re.search(
            r'period[:\s]+(?:from\s*)?([^\n]+?to[^\n]+)',
            content, re.IGNORECASE
        )
        if period_match:
            result.add_suggestion(
                'billing_period',
                period_match.group(1).strip(),
                ConfidenceLevel.MEDIUM,
                source_text=period_match.group(0)
            )

        # -----------------------------------------------------------------
        # FLAGS
        # -----------------------------------------------------------------

        # Flag if retainage over standard 10%
        if ret_pct:
            pct = float(ret_pct.group(1))
            if pct > 10:
                result.add_flag(
                    'warning',
                    f'Retainage at {pct}% is higher than standard 10%',
                    severity=2
                )

        # Flag if materials stored
        if re.search(r'materials?\s*(?:stored|on\s*site)', content, re.IGNORECASE):
            result.add_flag(
                'info',
                'Materials stored - ensure lien waivers from suppliers',
                severity=1
            )
