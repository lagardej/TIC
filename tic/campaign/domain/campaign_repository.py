"""Campaign repository abstraction."""

from abc import ABC, abstractmethod
from uuid import UUID

from tic.campaign.domain.campaign import Campaign


class CampaignRepository(ABC):
    """Abstract base class for campaign persistence.

    The repository handles loading and saving Campaign aggregates.
    It is responsible for translating between the aggregate's domain
    representation and the storage layer.
    """

    @abstractmethod
    def get(self, campaign_id: UUID) -> Campaign | None:
        """Retrieve a campaign by its UUID.

        Args:
            campaign_id: The campaign UUID.

        Returns:
            The Campaign aggregate, or None if not found.
        """

    @abstractmethod
    def get_by_name(self, name: str) -> Campaign | None:
        """Retrieve a campaign by its faction name.

        Args:
            name: The campaign name (e.g., "ResistCouncil").

        Returns:
            The Campaign aggregate, or None if not found.
        """

    @abstractmethod
    def save(self, campaign: Campaign) -> None:
        """Save or update a campaign.

        Args:
            campaign: The Campaign aggregate to persist.
        """
