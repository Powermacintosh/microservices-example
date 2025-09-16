# -*- encoding: utf-8 -*-
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings


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
 
class Setting(BaseSettings):
    # FASTAPI
    api_v1_prefix: str = '/api/v1'
    api_v1_port: int = os.getenv('GATEWAY_PORT', 5000)
    
    # MICROSERVICES
    tasks_microservice_url: str = os.getenv('TASKS_MICROSERVICE_URL', 'http://tasks_app:5001')
    
    # CORS
    cors: ConfigurationCORS = ConfigurationCORS()

    # KAFKA
    kafka: ConfigurationKafka = ConfigurationKafka()
    
settings = Setting()