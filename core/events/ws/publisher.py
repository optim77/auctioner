from events.ws.handlers import WS_EVENT_HANDLERS


class EventPublisher:
    @staticmethod
    def publish(event) -> None:
        handler = WS_EVENT_HANDLERS .get(type(event))

        if handler is None:
            raise ValueError(
                f"No handler registered for {type(event).__name__}"
            )
        handler(event)