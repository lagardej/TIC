"""Campaign aggregate and related domain objects."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Campaign:
    """Aggregate root for a TIC campaign.

    A campaign is bound to a single faction and accumulates snapshots
    imported from Terra Invicta save files.
    """

    id: uuid.UUID
    faction_name: str
    snapshots: list[datetime] = field(default_factory=list)
