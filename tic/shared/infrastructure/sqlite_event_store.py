"""SQLite implementation of the event store."""

import dataclasses
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from tic.shared.domain.event_store import EventStore
from tic.shared.infrastructure.sqlite_schema import create_event_store_schema


class EventEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and UUID objects."""

    def default(self, obj: Any) -> Any:
        """Encode datetime and UUID objects as strings."""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class SqliteEventStore(EventStore):
    """SQLite implementation of the event store.

    Events are stored in an append-only table, serialized as JSON with their
    type name for later deserialization.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize the SQLite event store.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        create_event_store_schema(self.db_path)

    def append(self, campaign_id: str, event: Any) -> None:
        """Append an event to the store.

        Args:
            campaign_id: The campaign identifier.
            event: The event to append (typically a dataclass instance).
        """
        # Get the event type name
        event_type = f"{event.__class__.__module__}.{event.__class__.__name__}"

        # Serialize the event data
        if dataclasses.is_dataclass(event):
            event_data_dict = dataclasses.asdict(event)
        else:
            # Fallback for non-dataclass objects
            event_data_dict = event.__dict__

        event_data_json = json.dumps(event_data_dict, cls=EventEncoder)

        # Store in database
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (campaign_id, event_type, event_data)
                VALUES (?, ?, ?)
                """,
                (campaign_id, event_type, event_data_json),
            )
            conn.commit()
        finally:
            conn.close()

    def load(self, campaign_id: str) -> list[Any]:
        """Load all events for a campaign in order.

        Args:
            campaign_id: The campaign identifier.

        Returns:
            A list of events in append order. Empty list if no events exist.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT event_type, event_data
                FROM events
                WHERE campaign_id = ?
                ORDER BY id ASC
                """,
                (campaign_id,),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        events: list[Any] = []
        for event_type, event_data_json in rows:
            event_data = json.loads(event_data_json)
            # Reconstruct the event object
            event = self._deserialize_event(event_type, event_data)
            events.append(event)

        return events

    def _deserialize_event(self, event_type: str, event_data: dict[str, Any]) -> Any:
        """Deserialize an event from its stored representation.

        Args:
            event_type: The fully-qualified event type name.
            event_data: The event data dictionary.

        Returns:
            The reconstructed event object.

        Raises:
            ValueError: If the event type cannot be found or deserialized.
        """
        try:
            # Import the module and get the class
            module_name, class_name = event_type.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            event_class = getattr(module, class_name)

            # Reconstruct the dataclass instance
            if dataclasses.is_dataclass(event_class):
                return event_class(**event_data)
            else:
                # Fallback for non-dataclass
                instance = event_class.__new__(event_class)
                instance.__dict__.update(event_data)
                return instance
        except (ImportError, AttributeError, TypeError) as e:
            raise ValueError(f"Cannot deserialize event type {event_type}: {e}") from e
