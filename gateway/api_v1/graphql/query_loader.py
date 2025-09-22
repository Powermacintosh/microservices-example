from pathlib import Path


def load_query(query_name: str, section: str) -> str:
    """
    Загрузка GraphQL-запроса из файла
    
    Args:
        query_name: Название файла запроса без расширения
        section: Тип запроса ('tasks' или 'users')
        
    Returns:
        str: Запрос как строка
    """
    base_dir = Path(__file__).parent.parent
    query_path = base_dir / 'graphql' / section / 'queries' / f'{query_name}.graphql'
    
    try:
        with open(query_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f'Запрос не найден: {query_path}')

def load_mutation(mutation_name: str, section: str) -> str:
    """
    Загрузка GraphQL-мутации из файла
    
    Args:
        mutation_name: Название файла мутации без расширения
        section: Тип мутации ('tasks' или 'users')
        
    Returns:
        str: Мутация как строка
    """
    base_dir = Path(__file__).parent.parent
    mutation_path = base_dir / 'graphql' / section / 'mutations' / f'{mutation_name}.graphql'
    
    try:
        with open(mutation_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f'Мутация не найдена: {mutation_path}')