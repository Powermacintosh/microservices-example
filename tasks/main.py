import uvicorn, strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api_v1.rest import router as rest_api_router_v1
from infrastructure.kafka.producer import lifespan
from strawberry.fastapi import GraphQLRouter
from api_v1.graphql.tasks.resolvers import Mutation, Query
from api_v1.graphql.context import get_context_wrapper

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)

app = FastAPI(
    title='Tasks API',
    description='API for tasks',
    version='1.0.0',
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)

app.include_router(router=rest_api_router_v1, prefix=settings.api_v1_prefix)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
graphql_app = GraphQLRouter(
    schema=schema,
    context_getter=get_context_wrapper,
    graphql_ide='graphiql',
    multipart_uploads_enabled=True
)

app.include_router(
    router=graphql_app,
    prefix=settings.api_v1_prefix + '/graphql',
    include_in_schema=False
)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=settings.api_v1_port, reload=True)