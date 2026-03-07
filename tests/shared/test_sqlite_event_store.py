"""Tests for SQLite event store implementation."""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from tic.shared.domain.event_store import EventStore
from tic.shared.infrastructure.sqlite_event_store import SqliteEventStore


@dataclass
class TestEvent:
    """A simple test event."""

    campaign_id: str
    value: str


class TestSqliteEventStore:
    """Tests for SqliteEventStore."""

    @pytest.fixture
    def db_path(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test.db"

    @pytest.fixture
    def event_store(self, db_path: Path) -> SqliteEventStore:
        """Create a SqliteEventStore instance."""
        return SqliteEventStore(db_path)

    def test_append_and_load_single_event(self, event_store: SqliteEventStore) -> None:
        """Test appending and loading a single event."""
        campaign_id = str(uuid4())
        event = TestEvent(campaign_id=campaign_id, value="test")

        event_store.append(campaign_id, event)

        events = event_store.load(campaign_id)
        assert len(events) == 1
        assert events[0].campaign_id == campaign_id
        assert events[0].value == "test"

    def test_append_multiple_events_preserves_order(
        self, event_store: SqliteEventStore
    ) -> None:
        """Test that multiple events are stored in order."""
        campaign_id = str(uuid4())

        event_store.append(campaign_id, TestEvent(campaign_id=campaign_id, value="first"))
        event_store.append(campaign_id, TestEvent(campaign_id=campaign_id, value="second"))
        event_store.append(campaign_id, TestEvent(campaign_id=campaign_id, value="third"))

        events = event_store.load(campaign_id)
        assert len(events) == 3
        assert events[0].value == "first"
        assert events[1].value == "second"
        assert events[2].value == "third"

    def test_load_empty_campaign_returns_empty_list(
        self, event_store: SqliteEventStore
    ) -> None:
        """Test that loading a non-existent campaign returns empty list."""
        campaign_id = str(uuid4())
        events = event_store.load(campaign_id)
        assert events == []

    def test_campaign_isolation(self, event_store: SqliteEventStore) -> None:
        """Test that events from different campaigns are isolated."""
        campaign_1 = str(uuid4())
        campaign_2 = str(uuid4())

        event_store.append(campaign_1, TestEvent(campaign_id=campaign_1, value="campaign1"))
        event_store.append(campaign_2, TestEvent(campaign_id=campaign_2, value="campaign2"))

        events_1 = event_store.load(campaign_1)
        events_2 = event_store.load(campaign_2)

        assert len(events_1) == 1
        assert len(events_2) == 1
        assert events_1[0].value == "campaign1"
        assert events_2[0].value == "campaign2"

    def test_append_only_constraint(self, event_store: SqliteEventStore) -> None:
        """Test that the event store is append-only."""
        campaign_id = str(uuid4())
        event1 = TestEvent(campaign_id=campaign_id, value="first")

        event_store.append(campaign_id, event1)
        events_before = event_store.load(campaign_id)

        # Append another event
        event2 = TestEvent(campaign_id=campaign_id, value="second")
        event_store.append(campaign_id, event2)

        events_after = event_store.load(campaign_id)
        # Verify previous event is still there unchanged
        assert len(events_after) == 2
        assert events_after[0].value == "first"
