"""ParsedSave value object — the domain representation of a raw save file."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ParsedSave:
    """Raw data extracted from a Terra Invicta save file.

    Produced by the infrastructure save parser and consumed by the application layer.
    Keyed by stripped type name (PavonisInteractive.TerraInvicta. prefix removed).
    """

    faction_name: str
    game_date: datetime
    gamestates: dict
