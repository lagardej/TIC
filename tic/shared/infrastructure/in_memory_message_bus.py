"""In-memory implementation of the message bus."""

from typing import Any

from tic.shared.domain.message_bus import EventHandler, MessageBus


class InMemoryMessageBus(MessageBus):
    """In-memory message bus implementation.

    Synchronous, suitable for tests and local development. All subscribers
    are invoked immediately when an event is published.
    """

    def __init__(self) -> None:
        """Initialize the message bus."""
        self._handlers: dict[type, list[EventHandler]] = {}

    def publish(self, event: Any) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish.
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            handler(event)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Subscribe a handler to events of a specific type.

        Args:
            event_type: The event class to subscribe to.
            handler: A callable that receives the event instance.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: EventHandler) -> None:
        """Unsubscribe a handler from events of a specific type.

        Args:
            event_type: The event class to unsubscribe from.
            handler: The handler callable previously registered.
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not registered, silently ignore
