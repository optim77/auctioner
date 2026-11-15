import json
import os
import threading

from kafka import KafkaProducer

_producer: KafkaProducer | None = None
_lock = threading.Lock()


def get_kafka_producer() -> KafkaProducer:
    """Return the shared KafkaProducer, creating it lazily on first use.

    Building the producer at import time made the whole application fail
    to boot whenever the Kafka broker was unavailable.
    """
    global _producer
    if _producer is None:
        with _lock:
            if _producer is None:
                _producer = KafkaProducer(
                    bootstrap_servers=os.getenv(
                        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
                    ),
                    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                )
    return _producer
