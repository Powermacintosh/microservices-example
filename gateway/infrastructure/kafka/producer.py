import json
from aiokafka import AIOKafkaProducer
from core.config import settings

producer = AIOKafkaProducer(
    bootstrap_servers=settings.kafka.BOOTSTRAP,
    client_id=settings.kafka.CLIENT_ID,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)