"""ImportSave use case — orchestrates the save file import workflow."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID

from tic.campaign.application.save_file_reader import SaveFileReader
from tic.campaign.domain.campaign import Campaign
from tic.campaign.domain.campaign_repository import CampaignRepository
from tic.campaign.domain.events.save_imported import SaveImported
from tic.shared.domain.event_store import EventStore
from tic.shared.domain.message_bus import MessageBus


@dataclass
class ImportSaveCommand:
    """Command to import a Terra Invicta save file.

    Attributes:
        file_path: Path to the save file (.json or .gz).
    """

    file_path: Path


@dataclass
class ImportSaveResult:
    """Result of importing a save file.

    Attributes:
        campaign_id: UUID of the campaign that was imported.
        is_new: True if this was a new campaign, False if appended to existing.
    """

    campaign_id: UUID
    is_new: bool


class ImportSaveHandler:
    """Orchestrates the save file import use case.

    Responsibilities:
    1. Read the save file
    2. Resolve or create the campaign by name
    3. Check deduplication (game_date)
    4. Publish SaveImported event
    5. Append to event store
    """

    def __init__(
        self,
        save_file_reader: SaveFileReader,
        campaign_repository: CampaignRepository,
        event_store: EventStore,
        message_bus: MessageBus,
    ) -> None:
        """Initialize the handler with dependencies.

        Args:
            save_file_reader: Implementation of save file reading.
            campaign_repository: Campaign persistence.
            event_store: Event store for appending SaveImported.
            message_bus: Message bus for publishing SaveImported.
        """
        self.save_file_reader = save_file_reader
        self.campaign_repository = campaign_repository
        self.event_store = event_store
        self.message_bus = message_bus

    def handle(self, command: ImportSaveCommand) -> ImportSaveResult:
        """Handle the import save command.

        Orchestrates:
        1. Read save file → SaveFileData
        2. Resolve campaign by name (get_by_name)
        3. If not found, create new campaign
        4. Record save import (guards against duplicates via game_date)
        5. Create SaveImported event with all extracted metadata
        6. Append to event store
        7. Publish to message bus
        8. Return result

        Args:
            command: ImportSaveCommand with file path.

        Returns:
            ImportSaveResult with campaign_id and is_new flag.

        Raises:
            SaveAlreadyImported: If game_date already imported for this campaign.
            FileNotFoundError: If save file not found.
            ValueError: If save file cannot be parsed.
        """
        # Step 1: Read save file
        save_data = self.save_file_reader.read(command.file_path)

        # Step 2-3: Resolve or create campaign
        campaign = self.campaign_repository.get_by_name(save_data.campaign_name)
        is_new = False

        if campaign is None:
            campaign = Campaign.create_new(
                save_data.campaign_name,
                created_at=datetime.now(),
            )
            is_new = True

        # Step 4: Record save import (deduplication guard)
        campaign.record_save_import(save_data.game_date)

        # Step 5: Create SaveImported event
        event = SaveImported(
            campaign_id=campaign.id,
            name=save_data.campaign_name,
            faction_display_name=save_data.faction_display_name,
            game_date=save_data.game_date,
            difficulty=save_data.difficulty,
            scenario=save_data.scenario_meta_template_name,
            selected_factions=save_data.selected_factions,
            research_speed_multiplier=save_data.research_speed_multiplier,
            alien_progression_speed=save_data.alien_progression_speed,
            cp_maintenance_bonus=save_data.cp_maintenance_bonus,
            imported_at=datetime.now(),
        )

        # Step 6: Append to event store
        self.event_store.append(str(campaign.id), event)

        # Step 7: Publish to message bus
        self.message_bus.publish(event)

        # Step 8: Save campaign (persist deduplication state)
        self.campaign_repository.save(campaign)

        # Return result
        return ImportSaveResult(campaign_id=campaign.id, is_new=is_new)
