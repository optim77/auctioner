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