"""File system save loader — reads .json and .gz Terra Invicta save files."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from tic.campaign.application.save_loader import SaveLoader
from tic.campaign.domain.parsed_save import ParsedSave

NAMESPACE_PREFIX = "PavonisInteractive.TerraInvicta."
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"


class FileSystemSaveLoader(SaveLoader):
    """Loads Terra Invicta save files from the local file system.

    Supports both plain .json and .gz compressed saves.
    Encoding: UTF-8 with BOM (utf-8-sig).
    """

    def load(self, path: Path) -> ParsedSave:
        raise NotImplementedError
