# -*- encoding: utf-8 -*-
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ConfigurationDB(BaseModel):
    #########################
    #  PostgreSQL database  #
    #########################
    load_dotenv()
    
    MODE: str = os.getenv('MODE')
    
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
    load_dotenv()
    
    BOOTSTRAP: str = os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')
    TOPIC: str = os.getenv('KAFKA_TOPIC', 'task_events')
    GROUP_ID: str = os.getenv('KAFKA_GROUP_ID', 'tasks_app_group')

class Setting(BaseSettings):
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