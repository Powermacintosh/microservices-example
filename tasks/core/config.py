# -*- encoding: utf-8 -*-
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ConfigurationDB(BaseModel):
    #########################
    #  PostgreSQL database  #
    #########################
    
    DB_USER: str = os.getenv('TASKS_DB_USER')
    DB_PASS: str = os.getenv('TASKS_DB_PASS')
    DB_HOST: str = os.getenv('TASKS_DB_HOST')
    DB_PORT: int = os.getenv('TASKS_DB_PORT', 5432)
    DB_NAME: str = os.getenv('TASKS_DB_NAME')
    
    @property
    def async_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    echo: bool = False


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
    TOPIC: str = os.getenv('KAFKA_TOPIC', 'task_events')
    GROUP_ID: str = os.getenv('KAFKA_GROUP_ID', 'tasks_app_group')
    CLIENT_ID: str = os.getenv('KAFKA_CLIENT_ID', 'tasks_app')
    STARTUP_RETRIES: int = os.getenv('KAFKA_STARTUP_RETRIES', 3)
    RETRY_BACKOFF: float = os.getenv('KAFKA_RETRY_BACKOFF', 1.0)

class Setting(BaseSettings):
    # ENV
    MODE: str = os.getenv('MODE', 'development')

    # FASTAPI
    api_v1_prefix: str = '/api/v1'
    api_v1_port: int = os.getenv('TASKS_APP_PORT', 5001)
    
    # DATABASE
    db: ConfigurationDB = ConfigurationDB()
    
    # CORS
    cors: ConfigurationCORS = ConfigurationCORS()

    # KAFKA
    kafka: ConfigurationKafka = ConfigurationKafka()
    

settings = Setting()