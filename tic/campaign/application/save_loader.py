"""Abstract save loader — contract for loading a Terra Invicta save file."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from tic.campaign.domain.parsed_save import ParsedSave


class SaveLoader(ABC):
    """Loads a Terra Invicta save file and returns a ParsedSave.

    Implementations live in infrastructure/ and handle the specifics
    of file format (.json, .gz) and encoding.
    """

    @abstractmethod
    def load(self, path: Path) -> ParsedSave:
        """Load a save file and return its parsed representation.

        Args:
            path: Path to the save file (.json or .gz).

        Returns:
            ParsedSave with faction, date, and gamestates.

        Raises:
            ValueError: If required metadata is missing from the save.
        """
