"""SaveImported domain event."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SaveImported:
    """Raised when a save file snapshot is successfully imported into a campaign."""

    campaign_id: uuid.UUID
    game_date: datetime
    gamestates: dict  # raw parsed gamestates keyed by stripped type name
