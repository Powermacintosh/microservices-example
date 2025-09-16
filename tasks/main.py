import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api_v1.rest import router as router_v1

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)

app = FastAPI(
    title='Tasks API',
    description='API for tasks',
    version='1.0.0',
    # docs_url=None,
    # redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=settings.api_v1_port, reload=True)