"""File system save loader — reads .json and .gz Terra Invicta save files."""
from __future__ import annotations

import gzip
import json
from datetime import datetime
from pathlib import Path

from tic.campaign.application.save_loader import SaveLoader
from tic.campaign.domain.parsed_save import ParsedSave

NAMESPACE_PREFIX = "PavonisInteractive.TerraInvicta."


class FileSystemSaveLoader(SaveLoader):
    """Loads Terra Invicta save files from the local file system.

    Supports both plain .json and .gz compressed saves.
    Encoding: UTF-8 with BOM (utf-8-sig).
    """

    def load(self, path: Path) -> ParsedSave:
        """Load a save file and return its parsed representation.

        Args:
            path: Path to the save file (.json or .gz).

        Returns:
            ParsedSave with faction, date, and gamestates.

        Raises:
            ValueError: If TIMetadataState or TITimeState is missing.
        """
        raw = self._read(path)
        gamestates = self._strip_prefixes(raw.get("gamestates", {}))
        faction_name = self._extract_faction_name(gamestates)
        game_date = self._extract_game_date(gamestates)
        return ParsedSave(faction_name=faction_name, game_date=game_date, gamestates=gamestates)

    def _read(self, path: Path) -> dict:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8-sig") as f:
                return json.load(f)
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)

    def _strip_prefixes(self, gamestates: dict) -> dict:
        return {
            k[len(NAMESPACE_PREFIX):] if k.startswith(NAMESPACE_PREFIX) else k: v
            for k, v in gamestates.items()
        }

    def _extract_faction_name(self, gamestates: dict) -> str:
        entries = gamestates.get("TIMetadataState")
        if not entries:
            raise ValueError("TIMetadataState is missing or empty")
        return entries[0]["Value"]["playerFactionName"]

    def _extract_game_date(self, gamestates: dict) -> datetime:
        entries = gamestates.get("TITimeState")
        if not entries:
            raise ValueError("TITimeState is missing or empty")
        dt = entries[0]["Value"]["currentDateTime"]
        return datetime(
            year=dt["year"],
            month=dt["month"],
            day=dt["day"],
            hour=dt["hour"],
            minute=dt["minute"],
            second=dt["second"],
        )
