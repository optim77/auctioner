from handlers import NOTIFICATION_EVENTS
from parsers import PARSER_EVENTS


class NotificationServiceDispatcher:

    @staticmethod
    def dispatch(event: dict) -> None:
        event_type = event.get("event_type")

        parser = PARSER_EVENTS.get(event_type)

        if parser is None:
            raise ValueError(
                f"No parser registered for event type: {event_type}"
            )

        parsed_event = parser(event)

        handler = NOTIFICATION_EVENTS.get(event_type)

        if handler is None:
            raise ValueError(
                f"No handler registered for event type: {event_type}"
            )

        handler(parsed_event)