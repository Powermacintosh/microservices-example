import httpx
from typing import Union, Optional
from fastapi import status, HTTPException
from api_v1.rest.tasks.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskUpdatePartial,
)

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('httpx')


class ExternalServiceFacade:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def proxy_endpoint(
        self,
        endpoint: str,
        data: Optional[Union[TaskCreate, TaskUpdate, TaskUpdatePartial, dict]] = None,
        method: Optional[str] = 'get',
    ):
        async with httpx.AsyncClient() as client:
            try:
                if method == 'post':
                    response = await client.post(
                        f'{self.base_url}/api/v1/{endpoint}',
                        json=data.model_dump(),
                        follow_redirects=True
                    )
                elif method == 'put':
                    response = await client.put(
                        f'{self.base_url}/api/v1/{endpoint}',
                        json=data.model_dump(),
                        follow_redirects=True
                    )
                elif method == 'patch':
                    response = await client.patch(
                        f'{self.base_url}/api/v1/{endpoint}',
                        json=data.model_dump(exclude_unset=True),
                        follow_redirects=True
                    )
                elif method == 'delete':
                    response = await client.delete(
                        f'{self.base_url}/api/v1/{endpoint}',
                        follow_redirects=True
                    )   
                else:
                    response = await client.get(
                        f'{self.base_url}/api/v1/{endpoint}',
                        params=data,
                        follow_redirects=True
                    )
                response.raise_for_status()
                if response.status_code == 204:
                    return status.HTTP_204_NO_CONTENT
                else:
                    return response.json()
            except httpx.HTTPStatusError as e:
                logger.error('HTTPStatusError', exc_info=e)
                # Если ответ JSON, возвращаем его как есть
                if 'application/json' in e.response.headers.get('content-type', ''):
                    error_detail = e.response.json()
                else:
                    error_detail = {
                        'detail': str(e),
                        'status_code': e.response.status_code,
                        'url': str(e.request.url)
                    }
                # Перебрасываем с подробной ошибкой
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=error_detail
                )

    