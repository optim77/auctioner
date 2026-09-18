import json

from kafka import KafkaConsumer
from parsers import parse_outbid_event
from notification_events import OutbidDTO
from handlers import handle_outbid_event

consumer = KafkaConsumer(
    "bid.outbid",
    bootstrap_servers=["localhost:9092"],
    group_id="notification-service",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

for message in consumer:
    print(message)
    event: OutbidDTO = parse_outbid_event(message.value)
    handle_outbid_event(event)