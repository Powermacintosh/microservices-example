from aiokafka import AIOKafkaProducer

async def get_producer() -> AIOKafkaProducer:
    from main import app  # Ленивый импорт
    return app.state.kafka_producer
