"""CampaignCreated domain event."""
from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignCreated:
    """Raised when a new campaign is created on first save import."""

    campaign_id: uuid.UUID
    faction_name: str
