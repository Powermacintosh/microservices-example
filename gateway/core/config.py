# -*- encoding: utf-8 -*-
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()
class ConfigurationCORS(BaseModel):
    #########################
    #         CORS          #
    #########################
    origins: list = ['*']
    allow_credentials: bool = True
    methods: list = [
        'GET',
        'POST',
        'OPTIONS',
        'PATCH',
        'PUT',
        'DELETE',
    ]
    headers: list = [
        'Access-Control-Allow-Headers',
        'Content-Type',
        'Set-Cookie',
        'Authorization',
        'Access-Control-Allow-Origin',
    ]

class ConfigurationKafka(BaseModel):
    #########################
    #         KAFKA         #
    #########################
    BOOTSTRAP: str = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')
    CLIENT_ID: str = os.getenv('KAFKA_CLIENT_ID', 'gateway_app')
    TOPIC: str = os.getenv('KAFKA_TOPIC', 'task_events')
    GROUP_ID: str = os.getenv('KAFKA_GROUP_ID', 'gateway_app_group')
    STARTUP_RETRIES: int = os.getenv('KAFKA_STARTUP_RETRIES', 3)
    RETRY_BACKOFF: float = os.getenv('KAFKA_RETRY_BACKOFF', 1.0)
 
class Setting(BaseSettings):
    # ENV
    MODE: str = os.getenv('MODE', 'DEVELOPMENT')

    # FASTAPI
    api_v1_prefix: str = '/api/v1'
    api_v1_port: int = os.getenv('GATEWAY_PORT', 5000)
    
    # MICROSERVICES
    tasks_microservice_url: str = os.getenv('TASKS_MICROSERVICE_URL', 'http://localhost:5001')
    
    # CORS
    cors: ConfigurationCORS = ConfigurationCORS()

    # KAFKA
    kafka: ConfigurationKafka = ConfigurationKafka()
    
settings = Setting()