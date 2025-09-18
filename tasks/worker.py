import asyncio, json
from aiokafka import AIOKafkaConsumer, TopicPartition
from api_v1.rest.tasks.dependencies import unit_of_work
from api_v1.rest.tasks.service import TaskService
from api_v1.rest.tasks.schemas import TaskCreate
from datetime import datetime

from core.config import settings

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('kafka_logger')


async def handle_message(msg, consumer):
    try:
        data = json.loads(msg.value.decode())
    except Exception as e:
        logger.exception('Невалидный json', exc_info=e)
        await consumer.commit({TopicPartition(msg.topic, msg.partition): msg.offset + 1})
        return

    if data.get('event') != 'TaskCreation':
        await consumer.commit({TopicPartition(msg.topic, msg.partition): msg.offset + 1})
        return

    try:
        task = TaskCreate.model_validate(data['task'])
    except Exception as e:
        logger.exception('Невалидный payload', exc_info=e)
        await consumer.commit({TopicPartition(msg.topic, msg.partition): msg.offset + 1})
        return

    try:
        async with unit_of_work() as uow:
            svc = TaskService(uow)
            await svc.create_task(task)
        # Только подтверждаем offset если все успешно
        await consumer.commit({TopicPartition(msg.topic, msg.partition): msg.offset + 1})
    except Exception as e:
        logger.exception('Ошибка записи в базу данных', exc_info=e)
        # Не подтверждаем offset если была ошибка обработки сообщения
        # Таким образом сообщение будет повторно обработано
        return

async def run_consumer():
    consumer = AIOKafkaConsumer(
        settings.kafka.TOPIC,
        bootstrap_servers=settings.kafka.BOOTSTRAP,
        group_id=settings.kafka.GROUP_ID,
        enable_auto_commit=False,
        auto_offset_reset='earliest' # начать с самого старого сообщения
    )
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info('Сообщение от %s: %s...' % (datetime.fromtimestamp(msg.timestamp/1000), msg.value[:100]))
            logger.info('Сообщение содержит - топик: %s, партиция: %s, offset: %s, ключ: %s, значение: %s, время: %s', msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)
            await handle_message(msg, consumer)
    finally:
        await consumer.stop()

if __name__ == '__main__':
    asyncio.run(run_consumer())
