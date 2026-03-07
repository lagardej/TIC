"""SaveFileReader abstraction for reading Terra Invicta save files."""

from abc import ABC, abstractmethod
from pathlib import Path

from tic.campaign.application.save_file_data import SaveFileData


class SaveFileReader(ABC):
    """Abstract base class for reading and parsing Terra Invicta save files.

    Implementations handle different file formats (plain JSON, gzip-compressed)
    and extract metadata from the raw save structure into a typed SaveFileData object.
    """

    @abstractmethod
    def read(self, path: Path) -> SaveFileData:
        """Read and parse a save file.

        Args:
            path: Path to the save file (.json or .gz).

        Returns:
            Extracted save file metadata as a SaveFileData value object.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file cannot be parsed (implementation-dependent).
        """
