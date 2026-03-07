"""SaveImported domain event."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SaveImported:
    """Fired when a Terra Invicta save file is successfully imported.

    This event records all metadata extracted from the save file, serving as
    the source of truth for campaign metadata across all projections.
    """

    campaign_id: UUID
    """The campaign this save belongs to."""

    name: str
    """The campaign name (faction identity, e.g., 'ResistCouncil')."""

    faction_display_name: str
    """Human-readable display name of the player faction."""

    game_date: datetime
    """The in-game date of this save. Used for deduplication."""

    difficulty: int
    """Difficulty level (0-4 typically, depending on difficulty slider)."""

    scenario: str
    """Scenario name (e.g., 'Demigod', 'Impossible')."""

    selected_factions: list[str]
    """List of factions selected for this scenario."""

    research_speed_multiplier: float
    """Multiplier applied to research speed (e.g., 1.0, 0.8, 1.2)."""

    alien_progression_speed: float
    """Multiplier applied to alien progression speed."""

    cp_maintenance_bonus: int
    """Control point maintenance freebies (raw integer count)."""

    imported_at: datetime
    """When this save was imported into TIC."""
