# GitPlach - Система контроля версий

## Архитектура системы

### Основные компоненты
- **Хранилище** (`.myvcs/`):
  - `commits/` - каталог коммитов
  - `objects/` - хранилище файлов
  - `index` - индекс изменений
  - `HEAD` - текущая ветка
  - `config` - конфигурация

### Ключевые классы
```python
class GitPlach:
    # Инициализация репозитория
    @staticmethod
    def init() -> bool
    
    # Работа с файлами
    @staticmethod
    def add(filepath: str) -> bool
    @staticmethod
    def remove(filepath: str) -> bool
    
    # Управление версиями
    @staticmethod
    def save(message: str) -> bool
    @staticmethod
    def check() -> bool
    
    # Вспомогательные методы
    @staticmethod
    def _get_file_hash(filepath: str) -> str