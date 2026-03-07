"""ImportSave command and handler."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tic.campaign.application.save_loader import SaveLoader
from tic.campaign.domain.campaign_repository import CampaignRepository


@dataclass(frozen=True)
class ImportSave:
    """Command: import a Terra Invicta save file into the appropriate campaign."""

    save_path: Path


class ImportSaveHandler:
    """Handles the ImportSave command.

    Responsibilities:
    - Parse the save file
    - Resolve or create the campaign for the save's faction
    - Deduplicate by game date
    - Emit SaveImported (and CampaignCreated if new)
    """

    def __init__(
        self,
        campaign_repository: CampaignRepository,
        save_loader: SaveLoader,
    ) -> None:
        self._campaign_repository = campaign_repository
        self._save_loader = save_loader

    def handle(self, command: ImportSave) -> None:
        raise NotImplementedError
