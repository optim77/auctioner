import json
import os

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'],
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)