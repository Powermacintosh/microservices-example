from typing import Optional, Type, TypeVar, Union
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    TimeoutError
)

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('database_logger')

T = TypeVar('T', bound='DatabaseError')


class DatabaseError(Exception):
    """Базовое исключение для ошибок БД"""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        self.message = message
        self.original_exception = original_exception
        logger.exception(f'{self.__class__.__name__}: {message}', exc_info=original_exception)
        super().__init__(self.message)

    @classmethod
    def from_sqlalchemy(
        cls: Type[T], 
        exc: Union[SQLAlchemyError, Exception], 
        context: Optional[str] = None
    ) -> T:
        """Создает соответствующее исключение из SQLAlchemy ошибки"""
        error_message = str(exc) if str(exc) else 'Неизвестная ошибка базы данных'
        context_part = f' в {context}' if context else ''
        message = f'Ошибка базы данных{context_part}: {error_message}'
        
        if isinstance(exc, IntegrityError):
            return DatabaseIntegrityError(message, exc)
        elif isinstance(exc, OperationalError):
            return DatabaseConnectionError(message, exc)
        elif isinstance(exc, TimeoutError):
            return DatabaseTimeoutError(message, exc)
        elif isinstance(exc, SQLAlchemyError):
            return DatabaseQueryError(message, exc)
        else:
            return DatabaseUnknownError(message, exc)

class DatabaseIntegrityError(DatabaseError):
    """Исключение для ошибок целостности БД (уникальность, внешние ключи)"""
    def __init__(self, message: str = 'Ошибка целостности базы данных', original_exception: Optional[Exception] = None):
        super().__init__(message, original_exception)

class DatabaseConnectionError(DatabaseError):
    """Исключение для ошибок подключения к БД"""
    def __init__(self, message: str = 'Ошибка подключения к базе данных', original_exception: Optional[Exception] = None):
        super().__init__(message, original_exception)

class DatabaseQueryError(DatabaseError):
    """Исключение для ошибок выполнения запросов"""
    def __init__(self, message: str = 'Ошибка выполнения запроса', original_exception: Optional[Exception] = None):
        super().__init__(message, original_exception)

class DatabaseTimeoutError(DatabaseError):
    """Исключение для таймаутов БД"""
    def __init__(self, message: str = 'Ошибка таймаута базы данных', original_exception: Optional[Exception] = None):
        super().__init__(message, original_exception)

class DatabaseUnknownError(DatabaseError):
    """Исключение для непредвиденных ошибок"""
    def __init__(self, message: str = 'Непредвиденная ошибка', original_exception: Optional[Exception] = None):
        super().__init__(message, original_exception)