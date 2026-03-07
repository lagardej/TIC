"""Message bus abstraction for event publishing and subscription."""

from abc import ABC, abstractmethod
from typing import Any, Callable


EventHandler = Callable[[Any], None]


class MessageBus(ABC):
    """Abstract base class for message bus implementations.

    The message bus allows contexts to publish domain events and other
    contexts to subscribe to them without direct coupling.
    """

    @abstractmethod
    def publish(self, event: Any) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish (typically a dataclass instance).
                 The event type is inferred from its class.
        """

    @abstractmethod
    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Subscribe a handler to events of a specific type.

        Args:
            event_type: The event class to subscribe to.
            handler: A callable that receives the event instance.
                    Should accept exactly one argument (the event).
        """

    @abstractmethod
    def unsubscribe(self, event_type: type, handler: EventHandler) -> None:
        """Unsubscribe a handler from events of a specific type.

        Args:
            event_type: The event class to unsubscribe from.
            handler: The handler callable previously registered.
        """
