"""Event store abstraction for persistence."""

from abc import ABC, abstractmethod
from typing import Any


class EventStore(ABC):
    """Abstract base class for event store implementations.

    The event store is append-only and campaign-isolated. All events for a given
    campaign are stored together and can be loaded in order.
    """

    @abstractmethod
    def append(self, campaign_id: str, event: Any) -> None:
        """Append an event to the store for a campaign.

        Args:
            campaign_id: The campaign identifier.
            event: The event to append (typically a dataclass instance).
        """

    @abstractmethod
    def load(self, campaign_id: str) -> list[Any]:
        """Load all events for a campaign in order.

        Args:
            campaign_id: The campaign identifier.

        Returns:
            A list of events in append order. Empty list if no events exist.
        """
