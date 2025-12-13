"""
Base Parser Framework with Learning Feedback Loop

Core concept:
1. Parse document -> Extract data -> Generate suggestions
2. User confirms or corrects suggestions
3. Corrections are stored for model improvement
4. Over time, accuracy improves for this company's document patterns
"""

import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for extracted data"""
    HIGH = "high"       # 90%+ confident - auto-fill
    MEDIUM = "medium"   # 70-89% - suggest with highlight
    LOW = "low"         # 50-69% - suggest with warning
    GUESS = "guess"     # <50% - needs human review


class SuggestionStatus(Enum):
    """Status of a suggestion"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    REJECTED = "rejected"


@dataclass
class Suggestion:
    """
    A suggested value extracted from a document.
    User can confirm (click to accept) or correct (teaches the model).
    """
    field_name: str
    suggested_value: Any
    confidence: ConfidenceLevel
    source_text: str = ""           # Original text this was extracted from
    source_location: str = ""       # Page/line reference
    status: SuggestionStatus = SuggestionStatus.PENDING
    corrected_value: Any = None     # If user corrected, what they changed it to
    correction_reason: str = ""     # Why was the suggestion wrong?

    def confirm(self):
        """User confirmed the suggestion was correct"""
        self.status = SuggestionStatus.CONFIRMED

    def correct(self, new_value: Any, reason: str = ""):
        """User corrected the suggestion - this teaches the model"""
        self.status = SuggestionStatus.CORRECTED
        self.corrected_value = new_value
        self.correction_reason = reason

    def reject(self, reason: str = ""):
        """User rejected - value was wrong and not applicable"""
        self.status = SuggestionStatus.REJECTED
        self.correction_reason = reason

    def to_dict(self) -> dict:
        return {
            'field_name': self.field_name,
            'suggested_value': self.suggested_value,
            'confidence': self.confidence.value,
            'source_text': self.source_text,
            'source_location': self.source_location,
            'status': self.status.value,
            'corrected_value': self.corrected_value,
            'correction_reason': self.correction_reason
        }


@dataclass
class Flag:
    """A warning or note about the document"""
    flag_type: str          # 'warning', 'info', 'danger'
    message: str
    source_text: str = ""
    source_location: str = ""
    severity: int = 1       # 1-5, 5 being most severe

    def to_dict(self) -> dict:
        return {
            'type': self.flag_type,
            'message': self.message,
            'source_text': self.source_text,
            'source_location': self.source_location,
            'severity': self.severity
        }


@dataclass
class ParserResult:
    """
    Result of parsing a document.
    Contains extracted data, suggestions for review, and flags.
    """
    doc_type: str
    filename: str
    parsed_at: datetime = field(default_factory=datetime.now)

    # Confirmed/extracted data
    extracted_data: Dict[str, Any] = field(default_factory=dict)

    # Suggestions needing user review
    suggestions: List[Suggestion] = field(default_factory=list)

    # Warnings and flags
    flags: List[Flag] = field(default_factory=list)

    # Raw text for reference
    raw_text: str = ""

    # Parsing metadata
    parser_version: str = "1.0.0"
    processing_time_ms: int = 0

    def add_suggestion(self, field_name: str, value: Any,
                       confidence: ConfidenceLevel,
                       source_text: str = "",
                       source_location: str = ""):
        """Add a suggestion for user review"""
        self.suggestions.append(Suggestion(
            field_name=field_name,
            suggested_value=value,
            confidence=confidence,
            source_text=source_text,
            source_location=source_location
        ))

    def add_flag(self, flag_type: str, message: str,
                 source_text: str = "", severity: int = 1):
        """Add a warning or flag about the document"""
        self.flags.append(Flag(
            flag_type=flag_type,
            message=message,
            source_text=source_text,
            severity=severity
        ))

    def get_high_confidence_data(self) -> Dict[str, Any]:
        """Get only high-confidence extractions (safe to auto-fill)"""
        result = dict(self.extracted_data)
        for sugg in self.suggestions:
            if sugg.confidence == ConfidenceLevel.HIGH:
                result[sugg.field_name] = sugg.suggested_value
        return result

    def get_all_suggestions_by_confidence(self) -> Dict[str, List[Suggestion]]:
        """Group suggestions by confidence level"""
        result = {level.value: [] for level in ConfidenceLevel}
        for sugg in self.suggestions:
            result[sugg.confidence.value].append(sugg)
        return result

    def to_dict(self) -> dict:
        return {
            'doc_type': self.doc_type,
            'filename': self.filename,
            'parsed_at': self.parsed_at.isoformat(),
            'extracted_data': self.extracted_data,
            'suggestions': [s.to_dict() for s in self.suggestions],
            'flags': [f.to_dict() for f in self.flags],
            'parser_version': self.parser_version,
            'processing_time_ms': self.processing_time_ms
        }


class BaseParser:
    """
    Base class for document parsers.
    Subclass this for specific document types.
    """

    def __init__(self):
        self.doc_type = "generic"
        self.version = "1.0.0"

    def parse(self, content: str, filename: str = None) -> ParserResult:
        """
        Parse document content and return structured result.
        Override in subclasses for specific document types.
        """
        import time
        start = time.time()

        result = ParserResult(
            doc_type=self.doc_type,
            filename=filename or "unknown",
            raw_text=content,
            parser_version=self.version
        )

        # Run extraction
        self._extract_data(content, result)

        # Calculate processing time
        result.processing_time_ms = int((time.time() - start) * 1000)

        return result

    def _extract_data(self, content: str, result: ParserResult):
        """
        Override this method in subclasses to extract document-specific data.
        """
        pass

    # =========================================================================
    # UTILITY METHODS FOR SUBCLASSES
    # =========================================================================

    def find_pattern(self, content: str, pattern: str,
                     flags: int = re.IGNORECASE) -> List[tuple]:
        """Find all matches of a regex pattern"""
        return re.findall(pattern, content, flags)

    def find_money(self, content: str) -> List[str]:
        """Extract dollar amounts from text"""
        pattern = r'\$[\d,]+(?:\.\d{2})?'
        return re.findall(pattern, content)

    def find_percentages(self, content: str) -> List[str]:
        """Extract percentages from text"""
        pattern = r'\d+(?:\.\d+)?%'
        return re.findall(pattern, content)

    def find_dates(self, content: str) -> List[str]:
        """Extract dates from text"""
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, content, re.IGNORECASE))
        return dates

    def find_durations(self, content: str) -> List[str]:
        """Extract duration references (days, weeks, months)"""
        pattern = r'\d+\s*(?:calendar |working |business )?(?:days?|weeks?|months?)'
        return re.findall(pattern, content, re.IGNORECASE)

    def extract_near_keyword(self, content: str, keyword: str,
                             chars_after: int = 100) -> str:
        """Extract text near a keyword"""
        pattern = f'{keyword}[:\\s]*(.{{1,{chars_after}}})'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
