"""SQLite implementation of the EventStore."""
from __future__ import annotations

import uuid

from tic.shared.domain.event_store import EventStore


class SqliteEventStore(EventStore):
    """SQLite-backed append-only event store.

    Each campaign's events are stored in an isolated SQLite database
    under .tic/campaigns/<uuid>.db.
    """

    def append(self, campaign_id: uuid.UUID, event: object) -> None:
        raise NotImplementedError

    def load(self, campaign_id: uuid.UUID) -> list[object]:
        raise NotImplementedError
