"""
ROOFIO Badge System

Visual indicators for Full AI vs AI Assist mode.
Includes confidence display and activity status.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from datetime import datetime


class BadgeType(Enum):
    """Types of badges displayed"""
    FULL_AI = "full_ai"
    FULL_AI_PAUSED = "full_ai_paused"
    ASSIST = "assist"
    DISABLED = "disabled"


@dataclass
class Badge:
    """Visual badge for position status"""
    badge_type: BadgeType
    position_name: str
    assigned_to: Optional[str] = None  # Human name for assist mode
    confidence_score: Optional[int] = None
    confidence_display: Optional[str] = None  # Visual bar
    actions_today: int = 0
    flagged_count: int = 0
    paused_reason: Optional[str] = None

    @property
    def emoji(self) -> str:
        """Get badge emoji"""
        return {
            BadgeType.FULL_AI: "\U0001F916",  # Robot
            BadgeType.FULL_AI_PAUSED: "\u26A0\uFE0F",  # Warning
            BadgeType.ASSIST: "\U0001F9D1\u200D\U0001F4BC",  # Office worker
            BadgeType.DISABLED: "\u26D4",  # No entry
        }.get(self.badge_type, "")

    @property
    def label(self) -> str:
        """Get badge label text"""
        return {
            BadgeType.FULL_AI: "ROOFIO AUTONOMOUS",
            BadgeType.FULL_AI_PAUSED: "ROOFIO PAUSED",
            BadgeType.ASSIST: "ROOFIO ASSIST",
            BadgeType.DISABLED: "DISABLED",
        }.get(self.badge_type, "UNKNOWN")

    @property
    def color(self) -> str:
        """Get badge color (for UI)"""
        return {
            BadgeType.FULL_AI: "#22c55e",      # Green
            BadgeType.FULL_AI_PAUSED: "#f59e0b",  # Amber
            BadgeType.ASSIST: "#3b82f6",       # Blue
            BadgeType.DISABLED: "#6b7280",     # Gray
        }.get(self.badge_type, "#6b7280")

    def render_text(self) -> str:
        """Render badge as text for CLI/terminal"""
        lines = []

        # Header with emoji and label
        header = f"{self.emoji} [{self.label}]"
        if self.assigned_to:
            header += f" {self.assigned_to}"

        lines.append(header)

        # Confidence display (if applicable)
        if self.confidence_score is not None:
            bar = self._render_confidence_bar()
            lines.append(f"   Confidence: {bar} {self.confidence_score}%")

        # Activity summary
        if self.badge_type in [BadgeType.FULL_AI, BadgeType.FULL_AI_PAUSED]:
            lines.append(f"   Actions Today: {self.actions_today}")
            if self.flagged_count > 0:
                lines.append(f"   Flagged: {self.flagged_count}")

        # Paused reason
        if self.badge_type == BadgeType.FULL_AI_PAUSED and self.paused_reason:
            lines.append(f"   Reason: {self.paused_reason}")

        return "\n".join(lines)

    def _render_confidence_bar(self) -> str:
        """Render confidence as visual bar"""
        if self.confidence_score is None:
            return "n/a"

        filled = int(self.confidence_score / 10)
        empty = 10 - filled

        if self.confidence_score >= 90:
            char = "\u2588"  # Full block
        elif self.confidence_score >= 80:
            char = "\u2593"  # Dark shade
        else:
            char = "\u2591"  # Light shade

        return char * filled + "\u2591" * empty

    def to_dict(self) -> dict:
        """Convert to dictionary for API/JSON"""
        return {
            "badge_type": self.badge_type.value,
            "position_name": self.position_name,
            "emoji": self.emoji,
            "label": self.label,
            "color": self.color,
            "assigned_to": self.assigned_to,
            "confidence_score": self.confidence_score,
            "actions_today": self.actions_today,
            "flagged_count": self.flagged_count,
            "paused_reason": self.paused_reason,
        }


@dataclass
class PositionBadgeDisplay:
    """Full display for a position including badge and status"""
    position_name: str
    badge: Badge
    handling: List[str]  # What functions it's handling
    suggestions: List[str] = None  # For assist mode
    pending_review: List[dict] = None  # Items needing human review

    def render_text(self) -> str:
        """Render complete position display as text"""
        lines = [self.badge.render_text()]

        # What it's handling
        if self.handling:
            lines.append(f"   Handling: {', '.join(self.handling)}")

        # Available actions (assist mode)
        if self.suggestions:
            lines.append(f"   Available: {', '.join(self.suggestions)}")

        # Pending review items
        if self.pending_review:
            lines.append(f"   Pending Review: {len(self.pending_review)} items")

        return "\n".join(lines)


# =============================================================================
# BADGE FACTORY FUNCTIONS
# =============================================================================

def create_full_ai_badge(
    position_name: str,
    confidence_score: int,
    actions_today: int = 0,
    flagged_count: int = 0
) -> Badge:
    """Create a Full AI mode badge"""
    return Badge(
        badge_type=BadgeType.FULL_AI,
        position_name=position_name,
        confidence_score=confidence_score,
        actions_today=actions_today,
        flagged_count=flagged_count,
    )


def create_paused_badge(
    position_name: str,
    confidence_score: int,
    paused_reason: str
) -> Badge:
    """Create a paused Full AI badge"""
    return Badge(
        badge_type=BadgeType.FULL_AI_PAUSED,
        position_name=position_name,
        confidence_score=confidence_score,
        paused_reason=paused_reason,
    )


def create_assist_badge(
    position_name: str,
    assigned_to: str
) -> Badge:
    """Create an AI Assist mode badge"""
    return Badge(
        badge_type=BadgeType.ASSIST,
        position_name=position_name,
        assigned_to=assigned_to,
    )


def create_disabled_badge(position_name: str) -> Badge:
    """Create a disabled badge"""
    return Badge(
        badge_type=BadgeType.DISABLED,
        position_name=position_name,
    )


# =============================================================================
# DASHBOARD RENDERER
# =============================================================================

class DashboardRenderer:
    """Renders the complete position dashboard"""

    def __init__(self, company_name: str):
        self.company_name = company_name
        self.positions: List[PositionBadgeDisplay] = []

    def add_position(self, display: PositionBadgeDisplay):
        """Add a position to the dashboard"""
        self.positions.append(display)

    def render_text(self) -> str:
        """Render complete dashboard as text"""
        lines = [
            "=" * 70,
            f"  ROOFIO CONTROL CENTER - {self.company_name}",
            "=" * 70,
            "",
            "POSITION STATUS:",
            "-" * 40,
        ]

        for pos in self.positions:
            lines.append("")
            lines.append(pos.render_text())

        # Summary
        full_ai_count = sum(1 for p in self.positions if p.badge.badge_type == BadgeType.FULL_AI)
        assist_count = sum(1 for p in self.positions if p.badge.badge_type == BadgeType.ASSIST)
        paused_count = sum(1 for p in self.positions if p.badge.badge_type == BadgeType.FULL_AI_PAUSED)

        lines.extend([
            "",
            "-" * 40,
            f"Summary: {full_ai_count} Full AI | {assist_count} Assist | {paused_count} Paused",
            "=" * 70,
        ])

        return "\n".join(lines)

    def get_pending_reviews(self) -> List[dict]:
        """Get all items pending human review"""
        pending = []
        for pos in self.positions:
            if pos.pending_review:
                for item in pos.pending_review:
                    item["position"] = pos.position_name
                    pending.append(item)
        return pending


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_dashboard():
    """Example of dashboard rendering"""
    dashboard = DashboardRenderer("Barrett Roofing Co.")

    # Project Manager - Full AI
    pm_badge = create_full_ai_badge("PROJECT MANAGER", 94, actions_today=12, flagged_count=0)
    dashboard.add_position(PositionBadgeDisplay(
        position_name="PROJECT MANAGER",
        badge=pm_badge,
        handling=["Submittals", "Schedule", "RFIs", "Pay Apps"],
    ))

    # Shop Drawing Detailer - Assist mode
    detail_badge = create_assist_badge("SHOP DRAWING DETAILER", "Armand")
    dashboard.add_position(PositionBadgeDisplay(
        position_name="SHOP DRAWING DETAILER",
        badge=detail_badge,
        handling=[],
        suggestions=["New RFI", "New CO", "Daily Report", "+ More"],
    ))

    # Safety - Full AI but paused
    safety_badge = create_paused_badge("SAFETY OFFICER", 72, "Ambiguous crane load data")
    dashboard.add_position(PositionBadgeDisplay(
        position_name="SAFETY OFFICER",
        badge=safety_badge,
        handling=["JHA", "Toolbox Talks", "Fall Protection"],
        pending_review=[{"task": "Crane Lift Plan", "confidence": 72}],
    ))

    # QC - Assist mode
    qc_badge = create_assist_badge("QC INSPECTOR", "Field Crew")
    dashboard.add_position(PositionBadgeDisplay(
        position_name="QC INSPECTOR",
        badge=qc_badge,
        handling=[],
        suggestions=["Checklist Gen", "Photo Tagging", "Punch List"],
    ))

    print(dashboard.render_text())
    return dashboard


if __name__ == "__main__":
    example_dashboard()
