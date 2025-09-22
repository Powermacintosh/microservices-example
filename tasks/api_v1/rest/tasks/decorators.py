from functools import wraps
from fastapi import HTTPException, status
from typing import Callable, TypeVar, Any
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    TimeoutError
)
from .exceptions import (
    TaskNotFoundException
)

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('handle_errors_logger')


T = TypeVar('T')

def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.debug('Ошибка целостности данных', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e) or 'Конфликт данных'
            )
        except (OperationalError, TimeoutError) as e:
            logger.debug('Сервис временно недоступен', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Сервис временно недоступен'
            )
        except SQLAlchemyError as e:
            logger.debug('Некорректный запрос', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Некорректный запрос'
            )
        except TaskNotFoundException as e:
            logger.debug('Задача не найдена', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        except ValueError as e:
            logger.debug('Некорректные данные', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e) or 'Некорректные данные'
            )
        except Exception as e:
            logger.debug('Неожиданная ошибка', exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Внутренняя ошибка сервера'
            )
    return wrapper
