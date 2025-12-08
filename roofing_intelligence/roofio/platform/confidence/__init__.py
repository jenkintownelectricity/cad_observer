"""
ROOFIO AI Confidence Scoring System

Determines when AI can proceed autonomously vs when it needs human review.

CONFIDENCE THRESHOLDS:
- 95-100%: Full AI proceeds autonomously
- 90-94%:  Full AI proceeds, flags for optional review
- 80-89%:  AUTO-PAUSE - Human review required
- Below 80%: STOP - Cannot proceed without human input
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json


class ConfidenceLevel(Enum):
    """Confidence level categories"""
    HIGH = "high"           # 95-100%: Proceed autonomously
    MODERATE = "moderate"   # 90-94%: Proceed with optional review flag
    LOW = "low"             # 80-89%: AUTO-PAUSE
    CRITICAL = "critical"   # Below 80%: STOP


@dataclass
class ConfidenceFactor:
    """Individual factor contributing to confidence score"""
    name: str
    weight: float  # 0.0 to 1.0
    score: int     # 0-100
    reason: str = ""

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


class ConfidenceCalculator:
    """
    Calculates AI confidence scores based on multiple factors.

    Factors:
    - Data Completeness: Are all required fields populated?
    - Data Consistency: Do values conflict with other records?
    - Historical Accuracy: How often has similar AI output been edited?
    - Ambiguity Detection: Are there multiple valid interpretations?
    - Risk Level: Financial/safety impact of error
    """

    DEFAULT_WEIGHTS = {
        "data_completeness": 0.25,
        "data_consistency": 0.20,
        "historical_accuracy": 0.20,
        "ambiguity": 0.20,
        "risk_level": 0.15,
    }

    def __init__(self, threshold: int = 90):
        self.threshold = threshold
        self.weights = self.DEFAULT_WEIGHTS.copy()

    def calculate(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        action_type: str,
        historical_edit_rate: float = 0.0,
        risk_category: str = "medium"
    ) -> "ConfidenceResult":
        """
        Calculate confidence score for an AI action.

        Args:
            data: The data being processed
            required_fields: Fields that must be present
            action_type: Type of action being performed
            historical_edit_rate: Rate at which similar outputs were edited (0-1)
            risk_category: low, medium, high, critical

        Returns:
            ConfidenceResult with score and factors
        """
        factors = []

        # Factor 1: Data Completeness
        completeness = self._calculate_completeness(data, required_fields)
        factors.append(ConfidenceFactor(
            name="data_completeness",
            weight=self.weights["data_completeness"],
            score=completeness["score"],
            reason=completeness["reason"]
        ))

        # Factor 2: Data Consistency
        consistency = self._calculate_consistency(data)
        factors.append(ConfidenceFactor(
            name="data_consistency",
            weight=self.weights["data_consistency"],
            score=consistency["score"],
            reason=consistency["reason"]
        ))

        # Factor 3: Historical Accuracy
        historical = self._calculate_historical(historical_edit_rate)
        factors.append(ConfidenceFactor(
            name="historical_accuracy",
            weight=self.weights["historical_accuracy"],
            score=historical["score"],
            reason=historical["reason"]
        ))

        # Factor 4: Ambiguity Detection
        ambiguity = self._detect_ambiguity(data, action_type)
        factors.append(ConfidenceFactor(
            name="ambiguity",
            weight=self.weights["ambiguity"],
            score=ambiguity["score"],
            reason=ambiguity["reason"]
        ))

        # Factor 5: Risk Level
        risk = self._calculate_risk(risk_category)
        factors.append(ConfidenceFactor(
            name="risk_level",
            weight=self.weights["risk_level"],
            score=risk["score"],
            reason=risk["reason"]
        ))

        # Calculate weighted total
        total_score = sum(f.weighted_score for f in factors)

        return ConfidenceResult(
            score=int(total_score),
            factors=factors,
            threshold=self.threshold,
            action_type=action_type
        )

    def _calculate_completeness(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """Check if all required fields are populated"""
        if not required_fields:
            return {"score": 100, "reason": "No required fields specified"}

        present = sum(1 for f in required_fields if data.get(f) is not None)
        missing = [f for f in required_fields if data.get(f) is None]

        score = int((present / len(required_fields)) * 100)

        if missing:
            reason = f"Missing fields: {', '.join(missing[:3])}"
            if len(missing) > 3:
                reason += f" (+{len(missing) - 3} more)"
        else:
            reason = "All required fields present"

        return {"score": score, "reason": reason}

    def _calculate_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for data inconsistencies"""
        issues = []

        # Check for common inconsistencies
        if "start_date" in data and "end_date" in data:
            if data["start_date"] and data["end_date"]:
                if data["start_date"] > data["end_date"]:
                    issues.append("End date before start date")

        if "total" in data and "subtotals" in data:
            calculated = sum(data.get("subtotals", []))
            if abs(data.get("total", 0) - calculated) > 0.01:
                issues.append("Total doesn't match subtotals")

        if "quantity" in data and data.get("quantity", 0) < 0:
            issues.append("Negative quantity")

        if "amount" in data and data.get("amount", 0) < 0:
            issues.append("Negative amount")

        if issues:
            score = max(0, 100 - (len(issues) * 20))
            reason = "; ".join(issues)
        else:
            score = 100
            reason = "No inconsistencies detected"

        return {"score": score, "reason": reason}

    def _calculate_historical(self, edit_rate: float) -> Dict[str, Any]:
        """Factor in historical edit rates for similar actions"""
        # edit_rate is 0-1 (0 = never edited, 1 = always edited)
        score = int((1 - edit_rate) * 100)

        if edit_rate > 0.5:
            reason = f"Similar outputs edited {int(edit_rate * 100)}% of the time"
        elif edit_rate > 0.2:
            reason = f"Moderate edit rate ({int(edit_rate * 100)}%)"
        else:
            reason = "Low historical edit rate"

        return {"score": score, "reason": reason}

    def _detect_ambiguity(
        self,
        data: Dict[str, Any],
        action_type: str
    ) -> Dict[str, Any]:
        """Detect ambiguous data that may have multiple interpretations"""
        issues = []

        # Check for ambiguous text fields
        text_fields = ["description", "question", "response", "notes", "reason"]
        for field in text_fields:
            value = data.get(field, "")
            if value and isinstance(value, str):
                # Check for ambiguity indicators
                ambig_words = ["maybe", "possibly", "unclear", "tbd", "or", "either"]
                if any(word in value.lower() for word in ambig_words):
                    issues.append(f"Ambiguous language in {field}")

                # Check for question marks in non-question fields
                if field != "question" and "?" in value:
                    issues.append(f"Uncertainty in {field}")

        # Check for incomplete references
        if "drawing_ref" in data and data.get("drawing_ref") == "TBD":
            issues.append("Drawing reference TBD")

        if "spec_ref" in data and not data.get("spec_ref"):
            issues.append("No specification reference")

        if issues:
            score = max(0, 100 - (len(issues) * 15))
            reason = "; ".join(issues[:2])
            if len(issues) > 2:
                reason += f" (+{len(issues) - 2} more)"
        else:
            score = 100
            reason = "No ambiguity detected"

        return {"score": score, "reason": reason}

    def _calculate_risk(self, risk_category: str) -> Dict[str, Any]:
        """Factor in risk level of the action"""
        risk_scores = {
            "low": 100,       # Informational, easily corrected
            "medium": 85,     # Some impact but recoverable
            "high": 70,       # Financial/legal impact
            "critical": 50,   # Safety-critical or major financial
        }

        risk_reasons = {
            "low": "Low-risk action",
            "medium": "Moderate financial/schedule impact",
            "high": "Significant financial or legal implications",
            "critical": "Safety-critical or major financial decision",
        }

        score = risk_scores.get(risk_category, 85)
        reason = risk_reasons.get(risk_category, "Unknown risk level")

        return {"score": score, "reason": reason}


@dataclass
class ConfidenceResult:
    """Result of confidence calculation"""
    score: int
    factors: List[ConfidenceFactor]
    threshold: int
    action_type: str
    calculated_at: datetime = field(default_factory=datetime.now)

    @property
    def level(self) -> ConfidenceLevel:
        """Get confidence level category"""
        if self.score >= 95:
            return ConfidenceLevel.HIGH
        elif self.score >= 90:
            return ConfidenceLevel.MODERATE
        elif self.score >= 80:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.CRITICAL

    @property
    def should_proceed(self) -> bool:
        """Can AI proceed with this action?"""
        return self.score >= self.threshold

    @property
    def should_pause(self) -> bool:
        """Should AI pause for human review?"""
        return self.score < self.threshold

    @property
    def should_stop(self) -> bool:
        """Should AI stop completely?"""
        return self.score < 80

    @property
    def needs_optional_review(self) -> bool:
        """Flag for optional human review (90-94%)"""
        return 90 <= self.score < 95

    @property
    def status_message(self) -> str:
        """Human-readable status message"""
        if self.score >= 95:
            return "High confidence - proceeding autonomously"
        elif self.score >= 90:
            return "Moderate confidence - proceeding with optional review flag"
        elif self.score >= 80:
            return "Low confidence - PAUSED for human review"
        else:
            return "Critical - STOPPED, requires human input"

    @property
    def issues(self) -> List[str]:
        """List of issues reducing confidence"""
        issues = []
        for factor in self.factors:
            if factor.score < 90:
                issues.append(f"{factor.name}: {factor.reason}")
        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API"""
        return {
            "score": self.score,
            "level": self.level.value,
            "threshold": self.threshold,
            "should_proceed": self.should_proceed,
            "should_pause": self.should_pause,
            "action_type": self.action_type,
            "status_message": self.status_message,
            "issues": self.issues,
            "factors": {
                f.name: {
                    "score": f.score,
                    "weight": f.weight,
                    "weighted_score": f.weighted_score,
                    "reason": f.reason
                }
                for f in self.factors
            },
            "calculated_at": self.calculated_at.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# ACTION-SPECIFIC CONFIDENCE PROFILES
# =============================================================================

ACTION_PROFILES = {
    # High confidence actions (typically 95%+)
    "generate_submittal_log": {
        "required_fields": ["estimate_id", "products"],
        "risk_category": "low",
        "expected_confidence": 99,
    },
    "generate_sov": {
        "required_fields": ["estimate_id", "line_items"],
        "risk_category": "low",
        "expected_confidence": 99,
    },
    "generate_lien_waiver": {
        "required_fields": ["pay_app_id", "amount", "through_date"],
        "risk_category": "medium",
        "expected_confidence": 98,
    },
    "generate_toolbox_talk": {
        "required_fields": ["topic", "date"],
        "risk_category": "low",
        "expected_confidence": 99,
    },

    # Medium confidence actions (typically 85-94%)
    "generate_rfi": {
        "required_fields": ["subject", "question", "drawing_ref"],
        "risk_category": "medium",
        "expected_confidence": 90,
    },
    "generate_pay_app": {
        "required_fields": ["job_id", "period_from", "period_to", "sov_data"],
        "risk_category": "high",
        "expected_confidence": 92,
    },
    "generate_jha": {
        "required_fields": ["job_id", "products", "scope"],
        "risk_category": "high",
        "expected_confidence": 90,
    },

    # Lower confidence actions (typically require human review)
    "generate_change_order": {
        "required_fields": ["description", "reason", "labor_cost", "material_cost"],
        "risk_category": "high",
        "expected_confidence": 75,
    },
    "generate_insurance_supplement": {
        "required_fields": ["original_estimate_id", "missed_items"],
        "risk_category": "high",
        "expected_confidence": 80,
    },
    "generate_incident_report": {
        "required_fields": ["date", "description", "employees_involved"],
        "risk_category": "critical",
        "expected_confidence": 70,
    },
    "generate_crane_lift_plan": {
        "required_fields": ["load_weight", "radius", "equipment"],
        "risk_category": "critical",
        "expected_confidence": 70,
    },
}


def get_action_profile(action_type: str) -> Dict[str, Any]:
    """Get the confidence profile for an action type"""
    return ACTION_PROFILES.get(action_type, {
        "required_fields": [],
        "risk_category": "medium",
        "expected_confidence": 85,
    })
