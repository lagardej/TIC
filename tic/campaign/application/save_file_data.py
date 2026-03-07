"""SaveFileData value object — extracted save file metadata."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SaveFileData:
    """Typed representation of extracted save file metadata.

    This value object contains all data extracted from the three source types
    (TITimeState, TIGlobalValuesState, TIGlobalResearchState). It serves as
    a canonical, immutable container for save file information, independent
    of the raw JSON structure.
    """

    # From TITimeState
    game_date: datetime
    scenario_meta_template_name: str
    days_in_campaign: int

    # From TIGlobalValuesState
    difficulty: int
    cp_maintenance_bonus: int
    campaign_name: str
    faction_display_name: str
    selected_factions: list[str]
    research_speed_multiplier: float
    alien_progression_speed: float

    # From TIGlobalResearchState
    campaign_start_year: int
    finished_techs_names: list[str]
    use_harsh_tree: bool
    end_game_techs_completed_by_category: dict[str, int]

    # Additional derived fields for convenience
    scenario: str = ""  # Alias for scenario_meta_template_name
