"""Tests for ImportSaveHandler use case."""

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from tic.campaign.application.import_save import (
    ImportSaveCommand,
    ImportSaveHandler,
    ImportSaveResult,
)
from tic.campaign.domain.campaign import Campaign, SaveAlreadyImported
from tic.campaign.domain.campaign_repository import CampaignRepository
from tic.campaign.domain.events.save_imported import SaveImported
from tic.campaign.application.save_file_reader import SaveFileReader
from tic.campaign.application.save_file_data import SaveFileData
from tic.shared.domain.event_store import EventStore
from tic.shared.domain.message_bus import MessageBus


class FakeSaveFileReader(SaveFileReader):
    """Fake save file reader for testing."""

    def __init__(self, save_data: SaveFileData) -> None:
        self.save_data = save_data

    def read(self, path: Path) -> SaveFileData:
        return self.save_data


class FakeCampaignRepository(CampaignRepository):
    """Fake campaign repository for testing."""

    def __init__(self) -> None:
        self.campaigns: dict[str, Campaign] = {}

    def get(self, campaign_id: UUID) -> Campaign | None:
        for campaign in self.campaigns.values():
            if campaign.id == campaign_id:
                return campaign
        return None

    def get_by_name(self, name: str) -> Campaign | None:
        return self.campaigns.get(name)

    def save(self, campaign: Campaign) -> None:
        self.campaigns[campaign.name] = campaign


class FakeEventStore(EventStore):
    """Fake event store for testing."""

    def __init__(self) -> None:
        self.events: dict[str, list[object]] = {}

    def append(self, campaign_id: str, event: object) -> None:
        if campaign_id not in self.events:
            self.events[campaign_id] = []
        self.events[campaign_id].append(event)

    def load(self, campaign_id: str) -> list[object]:
        return self.events.get(campaign_id, [])


class FakeMessageBus(MessageBus):
    """Fake message bus for testing."""

    def __init__(self) -> None:
        self.published_events: list[object] = []

    def publish(self, event: object) -> None:
        self.published_events.append(event)

    def subscribe(self, event_type: type, handler: object) -> None:
        pass

    def unsubscribe(self, event_type: type, handler: object) -> None:
        pass


class TestImportSaveHandler:
    """Tests for ImportSaveHandler."""

    @pytest.fixture
    def sample_save_file_data(self) -> SaveFileData:
        """Create test save file data."""
        return SaveFileData(
            game_date=datetime(2045, 3, 15, 10, 30, 0),
            scenario_meta_template_name="Demigod",
            days_in_campaign=100,
            difficulty=3,
            cp_maintenance_bonus=0,
            campaign_name="ResistCouncil",
            faction_display_name="Resistance",
            selected_factions=["Resistance", "Illuminati"],
            research_speed_multiplier=1.0,
            alien_progression_speed=1.0,
            campaign_start_year=2045,
            finished_techs_names=[],
            use_harsh_tree=False,
            end_game_techs_completed_by_category={},
        )

    @pytest.fixture
    def handler(self, sample_save_file_data: SaveFileData) -> tuple[ImportSaveHandler, FakeCampaignRepository, FakeEventStore, FakeMessageBus]:
        """Create handler with fake dependencies."""
        repository = FakeCampaignRepository()
        event_store = FakeEventStore()
        message_bus = FakeMessageBus()
        reader = FakeSaveFileReader(sample_save_file_data)

        return (
            ImportSaveHandler(
                save_file_reader=reader,
                campaign_repository=repository,
                event_store=event_store,
                message_bus=message_bus,
            ),
            repository,
            event_store,
            message_bus,
        )

    def test_successful_import_creates_new_campaign(
        self, handler: tuple, sample_save_file_data: SaveFileData
    ) -> None:
        """Test importing a save file creates a new campaign."""
        import_handler, repository, event_store, message_bus = handler
        command = ImportSaveCommand(file_path=Path("/fake/save.json"))

        result = import_handler.handle(command)

        assert result.is_new is True
        assert result.campaign_id is not None
        assert sample_save_file_data.campaign_name in repository.campaigns

    def test_successful_import_publishes_event(
        self, handler: tuple, sample_save_file_data: SaveFileData
    ) -> None:
        """Test importing a save publishes SaveImported event."""
        import_handler, repository, event_store, message_bus = handler
        command = ImportSaveCommand(file_path=Path("/fake/save.json"))

        result = import_handler.handle(command)

        assert len(message_bus.published_events) == 1
        event = message_bus.published_events[0]
        assert isinstance(event, SaveImported)
        assert event.campaign_id == result.campaign_id
        assert event.game_date == sample_save_file_data.game_date

    def test_successful_import_appends_to_event_store(
        self, handler: tuple, sample_save_file_data: SaveFileData
    ) -> None:
        """Test importing a save appends to event store."""
        import_handler, repository, event_store, message_bus = handler
        command = ImportSaveCommand(file_path=Path("/fake/save.json"))

        result = import_handler.handle(command)

        events = event_store.load(str(result.campaign_id))
        assert len(events) == 1
        assert isinstance(events[0], SaveImported)

    def test_import_existing_campaign_does_not_create_new(
        self, handler: tuple, sample_save_file_data: SaveFileData
    ) -> None:
        """Test importing to existing campaign does not create new campaign."""
        import_handler, repository, event_store, message_bus = handler

        # Pre-populate repository with existing campaign
        existing_campaign = Campaign.create_new(
            sample_save_file_data.campaign_name,
            created_at=datetime(2045, 1, 1),
        )
        repository.save(existing_campaign)

        command = ImportSaveCommand(file_path=Path("/fake/save.json"))
        result = import_handler.handle(command)

        assert result.is_new is False
        assert result.campaign_id == existing_campaign.id

    def test_deduplication_raises_save_already_imported(
        self, handler: tuple, sample_save_file_data: SaveFileData
    ) -> None:
        """Test importing same game_date twice raises SaveAlreadyImported."""
        import_handler, repository, event_store, message_bus = handler

        # First import
        command = ImportSaveCommand(file_path=Path("/fake/save.json"))
        import_handler.handle(command)

        # Second import with same game_date should raise
        with pytest.raises(SaveAlreadyImported):
            import_handler.handle(command)
