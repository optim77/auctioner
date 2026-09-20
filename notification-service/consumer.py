import json

from kafka import KafkaConsumer
from dispatcher import NotificationServiceDispatcher

consumer = KafkaConsumer(
    "bid.outbid",
    bootstrap_servers=["localhost:9092"],
    group_id="notification-service",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

for message in consumer:
    NotificationServiceDispatcher.dispatch(message.value)