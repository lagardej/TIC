"""Abstract repository contract for Campaign persistence."""
from __future__ import annotations

from abc import ABC, abstractmethod

from tic.campaign.domain.campaign import Campaign


class CampaignRepository(ABC):
    """Defines the persistence contract for Campaign aggregates.

    Implementations live in infrastructure/. The application layer
    depends only on this interface.
    """

    @abstractmethod
    def find_by_faction(self, faction_name: str) -> Campaign | None:
        """Return the campaign for the given faction, or None if not found."""

    @abstractmethod
    def save(self, campaign: Campaign) -> None:
        """Persist a campaign (create or update)."""
