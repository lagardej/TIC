"""Abstract event store — append-only contract for domain event persistence."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class EventStore(ABC):
    """Append-only store for domain events.

    Each campaign has its own isolated store. Events are never modified
    or deleted — only appended. Projections are fully rebuildable from the store.
    """

    @abstractmethod
    def append(self, campaign_id: uuid.UUID, event: object) -> None:
        """Append an event to the store for the given campaign."""

    @abstractmethod
    def load(self, campaign_id: uuid.UUID) -> list[object]:
        """Load all events for the given campaign in insertion order."""
