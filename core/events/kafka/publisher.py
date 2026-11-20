from collections.abc import Iterable

from events.kafka.handlers import KAFKA_EVENT_HANDLERS


class KafkaPublisher:
    @staticmethod
    def publish(event) -> None:
        handler = KAFKA_EVENT_HANDLERS.get(type(event))

        if handler is None:
            raise ValueError(
                f"No handler registered for {type(event).__name__}"
            )
        handler(event)

    @staticmethod
    def publish_many(events: Iterable) -> None:
        """Queue a batch of notifications without blocking on acknowledgements."""
        for event in events:
            KafkaPublisher.publish(event)
