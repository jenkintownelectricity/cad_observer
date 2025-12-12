"""
Contract Parser - Extracts key terms and flags tricky/risky clauses

This parser is designed to:
1. Extract standard contract data (value, duration, retainage, etc.)
2. FLAG dangerous clauses (liquidated damages, indemnification, etc.)
3. Identify misleading or tricky language that could hurt the subcontractor
"""

import re
from .base_parser import (
    BaseParser, ParserResult, ConfidenceLevel, Flag
)


class ContractParser(BaseParser):
    """
    Parser for construction contracts and subcontracts.
    Specialized in identifying roofing/waterproofing contract risks.
    """

    def __init__(self):
        super().__init__()
        self.doc_type = "contract"
        self.version = "1.0.0"

        # =====================================================================
        # RED FLAG PATTERNS - Clauses that should trigger warnings
        # =====================================================================
        self.red_flag_patterns = {
            # Liquidated Damages
            'liquidated_damages': {
                'patterns': [
                    r'liquidated damages.*?\$[\d,]+',
                    r'\$[\d,]+.*?per.*?(?:calendar |working )?day',
                    r'delay damages.*?\$[\d,]+',
                ],
                'severity': 5,
                'message': 'Liquidated damages clause detected'
            },

            # Indemnification
            'indemnification': {
                'patterns': [
                    r'indemnify.*?hold harmless',
                    r'defend.*?indemnify',
                    r'sole negligence',
                    r'broadly worded indemnification',
                ],
                'severity': 4,
                'message': 'Broad indemnification clause - review carefully'
            },

            # Pay-if-Paid vs Pay-when-Paid
            'pay_if_paid': {
                'patterns': [
                    r'pay.*?if.*?paid',
                    r'payment.*?contingent.*?upon.*?receipt',
                    r'condition precedent.*?payment',
                ],
                'severity': 5,
                'message': 'PAY-IF-PAID clause - you may not get paid if GC doesn\'t'
            },

            # Waiver of Lien Rights
            'lien_waiver': {
                'patterns': [
                    r'waive.*?lien rights',
                    r'waiver of mechanic.?s lien',
                    r'release.*?all lien rights',
                ],
                'severity': 4,
                'message': 'Lien rights waiver clause detected'
            },

            # No Damage for Delay
            'no_damage_delay': {
                'patterns': [
                    r'no damage.*?for delay',
                    r'time extension.*?sole remedy',
                    r'exclusive remedy.*?time extension',
                ],
                'severity': 4,
                'message': 'No-damage-for-delay clause - delays won\'t be compensated'
            },

            # Flow-Down Provisions
            'flow_down': {
                'patterns': [
                    r'flow.?down',
                    r'terms.*?prime contract.*?apply',
                    r'incorporated.*?reference.*?prime',
                    r'bound.*?terms.*?owner',
                ],
                'severity': 3,
                'message': 'Flow-down clause - prime contract terms may apply'
            },

            # Warranty Extensions
            'extended_warranty': {
                'patterns': [
                    r'warranty.*?(?:2|3|4|5|10|15|20)\s*years?',
                    r'(?:2|3|4|5|10|15|20)\s*year.*?warranty',
                    r'warrant.*?workmanship.*?(?:2|3|4|5)\s*years?',
                ],
                'severity': 3,
                'message': 'Extended warranty period detected - verify coverage'
            },

            # Change Order Limitations
            'co_limitations': {
                'patterns': [
                    r'change.*?order.*?markup.*?(?:10|15)%',
                    r'overhead.*?profit.*?limited.*?(?:10|15)%',
                    r'no.*?change.*?without.*?written.*?approval',
                ],
                'severity': 2,
                'message': 'Change order markup limitations'
            },

            # Termination for Convenience
            'termination_convenience': {
                'patterns': [
                    r'terminat.*?convenience',
                    r'terminat.*?without cause',
                    r'owner.*?right.*?terminat.*?any time',
                ],
                'severity': 3,
                'message': 'Termination for convenience clause'
            },

            # Insurance Requirements
            'insurance_requirements': {
                'patterns': [
                    r'insurance.*?\$[\d,]+.*?(?:million|M)',
                    r'additional insured',
                    r'waiver of subrogation',
                ],
                'severity': 2,
                'message': 'Special insurance requirements'
            },

            # Dispute Resolution
            'arbitration': {
                'patterns': [
                    r'binding arbitration',
                    r'waive.*?jury trial',
                    r'disputes.*?resolved.*?arbitration',
                ],
                'severity': 2,
                'message': 'Mandatory arbitration clause'
            },
        }

        # =====================================================================
        # TRICKY LANGUAGE PATTERNS - Subtle wording that could be problematic
        # =====================================================================
        self.tricky_patterns = {
            'all_costs': {
                'patterns': [
                    r'all costs.*?included',
                    r'complete.*?scope.*?included',
                    r'no additional compensation',
                ],
                'message': 'Broad scope inclusion language'
            },
            'schedule_responsibility': {
                'patterns': [
                    r'maintain.*?schedule',
                    r'responsible.*?delays',
                    r'contractor.*?responsible.*?coordination',
                ],
                'message': 'Schedule responsibility clause'
            },
            'weather_risk': {
                'patterns': [
                    r'weather.*?not.*?excuse',
                    r'anticipate.*?weather',
                    r'account for.*?weather',
                ],
                'message': 'Weather may not excuse delays'
            },
            'site_conditions': {
                'patterns': [
                    r'accept.*?site.*?as.?is',
                    r'examined.*?site',
                    r'familiar.*?conditions',
                ],
                'message': 'Site condition acceptance language'
            },
        }

    def _extract_data(self, content: str, result: ParserResult):
        """Extract contract data and check for red flags"""

        # -----------------------------------------------------------------
        # EXTRACT STANDARD CONTRACT DATA
        # -----------------------------------------------------------------

        # Contract Value
        money_values = self.find_money(content)
        if money_values:
            # Find the largest value (likely contract amount)
            values = []
            for v in money_values:
                try:
                    num = float(v.replace('$', '').replace(',', ''))
                    values.append((num, v))
                except:
                    pass
            if values:
                values.sort(reverse=True)
                contract_value = values[0][1]
                result.add_suggestion(
                    'contract_value',
                    contract_value,
                    ConfidenceLevel.MEDIUM,
                    source_text=f"Found: {contract_value}"
                )

        # Retainage
        retainage_match = re.search(
            r'retainage.*?(\d+(?:\.\d+)?)\s*%',
            content, re.IGNORECASE
        )
        if retainage_match:
            result.add_suggestion(
                'retainage_percent',
                f"{retainage_match.group(1)}%",
                ConfidenceLevel.HIGH,
                source_text=retainage_match.group(0)
            )

        # Contract Duration
        durations = self.find_durations(content)
        if durations:
            result.add_suggestion(
                'duration',
                durations[0],
                ConfidenceLevel.MEDIUM,
                source_text=f"Found: {durations[0]}"
            )

        # Start Date
        dates = self.find_dates(content)
        if dates:
            result.add_suggestion(
                'start_date',
                dates[0],
                ConfidenceLevel.LOW,
                source_text=f"Found date: {dates[0]}"
            )

        # Payment Terms
        payment_match = re.search(
            r'(?:net|payment).*?(\d+)\s*(?:days?|calendar)',
            content, re.IGNORECASE
        )
        if payment_match:
            result.add_suggestion(
                'payment_terms',
                f"Net {payment_match.group(1)} days",
                ConfidenceLevel.MEDIUM,
                source_text=payment_match.group(0)
            )

        # -----------------------------------------------------------------
        # CHECK FOR RED FLAGS
        # -----------------------------------------------------------------
        for flag_name, flag_config in self.red_flag_patterns.items():
            for pattern in flag_config['patterns']:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result.add_flag(
                        'warning',
                        flag_config['message'],
                        source_text=matches[0] if matches else "",
                        severity=flag_config['severity']
                    )
                    break  # Only flag once per category

        # -----------------------------------------------------------------
        # CHECK FOR TRICKY LANGUAGE
        # -----------------------------------------------------------------
        for trick_name, trick_config in self.tricky_patterns.items():
            for pattern in trick_config['patterns']:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result.add_flag(
                        'info',
                        trick_config['message'],
                        source_text=matches[0] if matches else "",
                        severity=1
                    )
                    break

        # -----------------------------------------------------------------
        # SPECIFIC EXTRACTIONS
        # -----------------------------------------------------------------

        # Liquidated Damages Amount
        ld_match = re.search(
            r'liquidated damages.*?\$?([\d,]+)',
            content, re.IGNORECASE
        )
        if not ld_match:
            ld_match = re.search(
                r'\$?([\d,]+).*?per.*?(?:calendar |working )?day.*?(?:delay|liquidated)',
                content, re.IGNORECASE
            )
        if ld_match:
            result.add_suggestion(
                'liquidated_damages_amount',
                f"${ld_match.group(1)}/day",
                ConfidenceLevel.HIGH,
                source_text=ld_match.group(0)
            )
            result.add_flag(
                'danger',
                f"LIQUIDATED DAMAGES: ${ld_match.group(1)} per day",
                source_text=ld_match.group(0),
                severity=5
            )

        # Insurance Requirements
        insurance_match = re.search(
            r'(?:general liability|GL).*?\$?([\d,]+).*?(?:million|M|000,000)',
            content, re.IGNORECASE
        )
        if insurance_match:
            result.add_suggestion(
                'insurance_gl_required',
                f"${insurance_match.group(1)}M",
                ConfidenceLevel.MEDIUM,
                source_text=insurance_match.group(0)
            )

        # Warranty Period
        warranty_match = re.search(
            r'warrant.*?(?:period|term).*?(\d+)\s*(?:year|month)',
            content, re.IGNORECASE
        )
        if warranty_match:
            result.add_suggestion(
                'warranty_period',
                f"{warranty_match.group(1)} years",
                ConfidenceLevel.MEDIUM,
                source_text=warranty_match.group(0)
            )

        # Change Order Markup Limit
        co_match = re.search(
            r'(?:change|extra).*?(?:markup|overhead|profit).*?(\d+)\s*%',
            content, re.IGNORECASE
        )
        if co_match:
            result.add_suggestion(
                'co_markup_limit',
                f"{co_match.group(1)}%",
                ConfidenceLevel.HIGH,
                source_text=co_match.group(0)
            )


class SubcontractParser(ContractParser):
    """
    Specialized parser for subcontracts.
    Inherits contract parsing but adds subcontract-specific checks.
    """

    def __init__(self):
        super().__init__()
        self.doc_type = "subcontract"

        # Additional patterns specific to subcontracts
        self.red_flag_patterns['scope_creep'] = {
            'patterns': [
                r'all work.*?necessary',
                r'complete.*?all.*?required',
                r'whatever.*?needed',
            ],
            'severity': 3,
            'message': 'Potential scope creep language'
        }
