"""Tests for in-memory message bus implementation."""

from dataclasses import dataclass
from typing import Any

import pytest

from tic.shared.infrastructure.in_memory_message_bus import InMemoryMessageBus


@dataclass
class SampleEvent:
    """A simple test event."""

    value: str


class TestInMemoryMessageBus:
    """Tests for InMemoryMessageBus."""

    @pytest.fixture
    def message_bus(self) -> InMemoryMessageBus:
        """Create an InMemoryMessageBus instance."""
        return InMemoryMessageBus()

    def test_publish_and_subscribe_single_handler(
        self, message_bus: InMemoryMessageBus
    ) -> None:
        """Test publishing an event to a single subscriber."""
        handled_events: list[Any] = []

        def handler(event: Any) -> None:
            handled_events.append(event)

        message_bus.subscribe(SampleEvent, handler)
        event = SampleEvent(value="test")
        message_bus.publish(event)

        assert len(handled_events) == 1
        assert isinstance(handled_events[0], SampleEvent)
        assert handled_events[0].value == "test"

    def test_publish_with_multiple_handlers(
        self, message_bus: InMemoryMessageBus
    ) -> None:
        """Test that an event reaches all registered handlers."""
        handler1_events: list[Any] = []
        handler2_events: list[Any] = []

        def handler1(event: Any) -> None:
            handler1_events.append(event)

        def handler2(event: Any) -> None:
            handler2_events.append(event)

        message_bus.subscribe(SampleEvent, handler1)
        message_bus.subscribe(SampleEvent, handler2)
        event = SampleEvent(value="test")
        message_bus.publish(event)

        assert len(handler1_events) == 1
        assert len(handler2_events) == 1
        assert handler1_events[0].value == "test"
        assert handler2_events[0].value == "test"

    def test_multiple_publishes_to_same_handler(
        self, message_bus: InMemoryMessageBus
    ) -> None:
        """Test that a handler receives multiple published events."""
        handled_events: list[Any] = []

        def handler(event: Any) -> None:
            handled_events.append(event)

        message_bus.subscribe(SampleEvent, handler)
        message_bus.publish(SampleEvent(value="first"))
        message_bus.publish(SampleEvent(value="second"))
        message_bus.publish(SampleEvent(value="third"))

        assert len(handled_events) == 3
        assert handled_events[0].value == "first"
        assert handled_events[1].value == "second"
        assert handled_events[2].value == "third"

    def test_no_handlers_for_event_type(self, message_bus: InMemoryMessageBus) -> None:
        """Test that publishing without handlers does not raise."""
        event = SampleEvent(value="test")
        # Should not raise
        message_bus.publish(event)

    def test_unsubscribe_prevents_handler_from_receiving_events(
        self, message_bus: InMemoryMessageBus
    ) -> None:
        """Test that unsubscribing a handler prevents it from receiving events."""
        handled_events: list[Any] = []

        def handler(event: Any) -> None:
            handled_events.append(event)

        message_bus.subscribe(SampleEvent, handler)
        message_bus.publish(SampleEvent(value="first"))

        # Unsubscribe
        message_bus.unsubscribe(SampleEvent, handler)
        message_bus.publish(SampleEvent(value="second"))

        assert len(handled_events) == 1
        assert handled_events[0].value == "first"
