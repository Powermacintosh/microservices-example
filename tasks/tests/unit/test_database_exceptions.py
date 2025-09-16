import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    TimeoutError as SQLTimeoutError,
    SQLAlchemyError
)

from infrastructure.database.exceptions import (
    DatabaseError,
    DatabaseIntegrityError,
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseTimeoutError,
    DatabaseUnknownError
)


def test_database_error_initialization():
    """Тест базового DatabaseError"""
    # Тест с кастомным сообщением
    error = DatabaseError('Test error')
    assert str(error) == 'Test error'
    assert error.message == 'Test error'
    assert error.original_exception is None
    
    # Тест с пустым сообщением
    empty_error = DatabaseError('')
    assert str(empty_error) == ''
    assert empty_error.message == ''
    
    # Тест с числовым сообщением
    numeric_error = DatabaseError(123)
    assert str(numeric_error) == '123'
    assert str(numeric_error.message) == '123'  # Convert to string for comparison


def test_database_error_with_original_exception():
    """Тест DatabaseError с исключением"""
    # Тест с простым исключением
    original = ValueError('Original error')
    error = DatabaseError('Test error', original)
    assert error.original_exception is original
    assert str(error) == 'Test error'
    
    # Тест с SQLAlchemy исключением
    sqlalchemy_error = IntegrityError('Integrity error', None, None)
    db_error = DatabaseError('DB error', sqlalchemy_error)
    assert db_error.original_exception is sqlalchemy_error
    assert str(db_error) == 'DB error'


def test_database_integrity_error():
    """Тест DatabaseIntegrityError"""
    # Тест с кастомным сообщением
    original = IntegrityError('Integrity error', None, None)
    error = DatabaseIntegrityError('Test integrity error', original)
    assert isinstance(error, DatabaseError)
    assert 'Test integrity error' in str(error)
    
    # Тест с сообщением по умолчанию
    error_default = DatabaseIntegrityError(original_exception=original)
    assert 'Ошибка целостности базы данных' in str(error_default)


def test_database_connection_error():
    """Тест DatabaseConnectionError"""
    # Тест с кастомным сообщением
    original = OperationalError('Connection failed', None, None)
    error = DatabaseConnectionError('Test connection error', original)
    assert isinstance(error, DatabaseError)
    assert 'Test connection error' in str(error)
    
    # Тест с сообщением по умолчанию
    error_default = DatabaseConnectionError(original_exception=original)
    assert 'Ошибка подключения к базе данных' in str(error_default)


def test_database_timeout_error():
    """Тест DatabaseTimeoutError"""
    # Тест с кастомным сообщением
    original = SQLTimeoutError('Query timed out', None, None)
    error = DatabaseTimeoutError('Test timeout error', original)
    assert isinstance(error, DatabaseError)
    assert 'Test timeout error' in str(error)
    
    # Тест с сообщением по умолчанию
    error_default = DatabaseTimeoutError(original_exception=original)
    assert 'Ошибка таймаута базы данных' in str(error_default)


def test_database_unknown_error():
    """Тест DatabaseUnknownError"""
    # Тест с кастомным сообщением
    original = Exception('Unknown error')
    error = DatabaseUnknownError('Test unknown error', original)
    assert isinstance(error, DatabaseError)
    assert 'Test unknown error' in str(error)
    
    # Тест с сообщением по умолчанию
    error_default = DatabaseUnknownError(original_exception=original)
    assert 'Непредвиденная ошибка' in str(error_default)


def test_from_sqlalchemy_integrity_error():
    """Тест from_sqlalchemy с IntegrityError"""
    # Создаем мок для IntegrityError
    error_msg = "(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint"
    original = IntegrityError(error_msg, None, None)
    
    # Тест с контекстом
    error = DatabaseError.from_sqlalchemy(original, 'создание пользователя')
    assert isinstance(error, DatabaseIntegrityError)
    assert 'создание пользователя' in str(error)
    assert 'Ошибка базы данных в создание пользователя' in str(error)
    assert error_msg in str(error)
    
    # Тест без контекста
    error_no_context = DatabaseError.from_sqlalchemy(original)
    assert isinstance(error_no_context, DatabaseIntegrityError)
    assert 'Ошибка базы данных' in str(error_no_context)
    assert error_msg in str(error_no_context)


def test_from_sqlalchemy_operational_error():
    """Тест from_sqlalchemy с OperationalError"""
    error_msg = "(psycopg2.OperationalError) could not connect to server"
    original = OperationalError(error_msg, None, None)
    
    # Тест с контекстом
    error = DatabaseError.from_sqlalchemy(original, 'подключение к БД')
    assert isinstance(error, DatabaseConnectionError)
    assert 'подключение к БД' in str(error)
    assert 'Ошибка базы данных в подключение к БД' in str(error)
    assert error_msg in str(error)
    
    # Тест без контекста
    error_no_context = DatabaseError.from_sqlalchemy(original)
    assert isinstance(error_no_context, DatabaseConnectionError)
    assert 'Ошибка базы данных' in str(error_no_context)
    assert error_msg in str(error_no_context)


def test_from_sqlalchemy_timeout_error():
    """Тест from_sqlalchemy с TimeoutError"""
    error_msg = "TimeoutError: Query timed out after 30s"
    original = SQLTimeoutError(error_msg, None, None, None)
    
    # Тест с контекстом
    error = DatabaseError.from_sqlalchemy(original, 'выполнение запроса')
    assert isinstance(error, DatabaseTimeoutError)
    assert 'выполнение запроса' in str(error)
    assert 'Ошибка базы данных в выполнение запроса' in str(error)
    assert error_msg in str(error)
    
    # Тест без контекста
    error_no_context = DatabaseError.from_sqlalchemy(original)
    assert isinstance(error_no_context, DatabaseTimeoutError)
    assert 'Ошибка базы данных' in str(error_no_context)
    assert error_msg in str(error_no_context)


def test_from_sqlalchemy_generic_sqlalchemy_error():
    """Тест from_sqlalchemy с общим SQLAlchemyError"""
    error_msg = "(sqlalchemy.exc.SQLAlchemyError) An error occurred"
    original = SQLAlchemyError(error_msg)
    
    # Тест с контекстом
    error = DatabaseError.from_sqlalchemy(original, 'выполнении запроса')
    assert isinstance(error, DatabaseQueryError)
    assert 'выполнении запроса' in str(error)
    assert 'Ошибка базы данных в выполнении запроса' in str(error)
    assert error_msg in str(error)
    
    # Тест без контекста
    error_no_context = DatabaseError.from_sqlalchemy(original)
    assert isinstance(error_no_context, DatabaseQueryError)
    assert 'Ошибка базы данных' in str(error_no_context)
    assert error_msg in str(error_no_context)


def test_from_sqlalchemy_unknown_error():
    """Тест from_sqlalchemy с неизвестным исключением"""
    error_msg = "Неожиданная ошибка при работе с БД"
    original = Exception(error_msg)
    
    # Тест с контекстом
    error = DatabaseError.from_sqlalchemy(original, 'неизвестной операции')
    assert isinstance(error, DatabaseUnknownError)
    assert 'неизвестной операции' in str(error)
    assert 'Ошибка базы данных в неизвестной операции' in str(error)
    assert error_msg in str(error)
    assert error.original_exception is original
    
    # Тест без контекста
    error_no_context = DatabaseError.from_sqlalchemy(original)
    assert isinstance(error_no_context, DatabaseUnknownError)
    assert 'Ошибка базы данных' in str(error_no_context)
    assert error_msg in str(error_no_context)
    assert error_no_context.original_exception is original


@patch('infrastructure.database.exceptions.logger.exception')
def test_error_logging(mock_logger):
    """Тестирование логирования ошибок"""
    original = ValueError('Test error')
    error = DatabaseError('Test error', original)
    mock_logger.assert_called_once()


# if __name__ == "__main__":
#     pytest.main(["-v", "test_database_exceptions.py"])
