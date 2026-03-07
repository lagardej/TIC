"""Tests for SaveImported event."""

from datetime import datetime
from uuid import uuid4

from tic.campaign.domain.events.save_imported import SaveImported


class TestSaveImported:
    """Tests for the SaveImported event."""

    def test_save_imported_creation(self) -> None:
        """Test creating a SaveImported event with all fields."""
        campaign_id = uuid4()
        game_date = datetime(2045, 3, 15, 10, 30, 0)
        imported_at = datetime.now()

        event = SaveImported(
            campaign_id=campaign_id,
            name="ResistCouncil",
            faction_display_name="Resistance",
            game_date=game_date,
            difficulty=3,
            scenario="Demigod",
            selected_factions=["Resistance", "Illuminati", "Cult"],
            research_speed_multiplier=1.0,
            alien_progression_speed=1.0,
            cp_maintenance_bonus=0,
            imported_at=imported_at,
        )

        assert event.campaign_id == campaign_id
        assert event.name == "ResistCouncil"
        assert event.faction_display_name == "Resistance"
        assert event.game_date == game_date
        assert event.difficulty == 3
        assert event.scenario == "Demigod"
        assert event.selected_factions == ["Resistance", "Illuminati", "Cult"]
        assert event.research_speed_multiplier == 1.0
        assert event.alien_progression_speed == 1.0
        assert event.cp_maintenance_bonus == 0
        assert event.imported_at == imported_at

    def test_save_imported_field_types(self) -> None:
        """Test that SaveImported fields have correct types."""
        campaign_id = uuid4()
        game_date = datetime(2045, 3, 15, 10, 30, 0)
        imported_at = datetime.now()

        event = SaveImported(
            campaign_id=campaign_id,
            name="ResistCouncil",
            faction_display_name="Resistance",
            game_date=game_date,
            difficulty=2,
            scenario="Impossible",
            selected_factions=["Resistance"],
            research_speed_multiplier=0.8,
            alien_progression_speed=1.2,
            cp_maintenance_bonus=5,
            imported_at=imported_at,
        )

        # Type checks
        assert isinstance(event.campaign_id, type(campaign_id))
        assert isinstance(event.name, str)
        assert isinstance(event.faction_display_name, str)
        assert isinstance(event.game_date, datetime)
        assert isinstance(event.difficulty, int)
        assert isinstance(event.scenario, str)
        assert isinstance(event.selected_factions, list)
        assert all(isinstance(f, str) for f in event.selected_factions)
        assert isinstance(event.research_speed_multiplier, float)
        assert isinstance(event.alien_progression_speed, float)
        assert isinstance(event.cp_maintenance_bonus, int)
        assert isinstance(event.imported_at, datetime)
