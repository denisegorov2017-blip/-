# План реализации PostgreSQL базы данных для агента Qoder

## 1. Обзор текущей реализации

Система уже имеет полностью реализованную базу данных с использованием SQLAlchemy ORM, но в настоящее время использует SQLite в качестве движка. Необходимо переключить систему на использование PostgreSQL с расширением TimescaleDB для оптимизации временных рядов.

### 1.1 Текущая архитектура базы данных

- **ORM**: SQLAlchemy
- **Текущий движок**: SQLite
- **Модели**: 18 таблиц реализованы в [src/core/database/models.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/models.py)
- **Сервисный слой**: Реализован в [src/core/database/services.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/services.py)
- **Интеграция**: Реализована в [src/core/database/integration.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/integration.py)
- **Утилиты**: Реализованы в [src/core/database/utils.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/utils.py)
- **CLI инструменты**: Реализованы в [src/core/database/cli.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/cli.py)

### 1.2 Зависимости

В [requirements.txt](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/requirements.txt) уже указаны необходимые зависимости:
- `sqlalchemy>=2.0.0`
- `alembic>=1.10.0`
- `psycopg2-binary>=2.9.0`

## 2. План реализации

### 2.1 Этап 1: Конфигурация PostgreSQL

#### Задачи:
1. Обновить [src/config.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/config.py) для поддержки PostgreSQL URL
2. Обновить [src/core/database/database.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/database.py) для поддержки PostgreSQL подключения
3. Добавить поддержку TimescaleDB расширения

### 2.2 Этап 2: Миграция схемы данных

#### Задачи:
1. Создать Alembic миграции для PostgreSQL
2. Адаптировать существующие модели для PostgreSQL
3. Обновить индексы и ограничения для оптимизации PostgreSQL

### 2.3 Этап 3: Интеграция TimescaleDB

#### Задачи:
1. Добавить TimescaleDB расширение для временных таблиц
2. Оптимизировать таблицы с временными данными
3. Настроить гипертаблицы для [calculation_data](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/models.py#L39-L66) и [coefficients](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/models.py#L83-L97)

### 2.4 Этап 4: Тестирование и валидация

#### Задачи:
1. Создать тестовую среду PostgreSQL
2. Протестировать все существующие функции с PostgreSQL
3. Проверить производительность и оптимизировать при необходимости

### 2.5 Этап 5: Документация и развертывание

#### Задачи:
1. Обновить документацию по настройке PostgreSQL
2. Создать скрипты для развертывания базы данных
3. Подготовить руководство по миграции с SQLite на PostgreSQL

## 3. Подробная реализация

### 3.1 Обновление конфигурации

В [src/config.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/config.py) необходимо добавить поддержку PostgreSQL URL:

```python
# === Настройки базы данных ===
# Включена ли база данных
'enable_database': True,

# URL для подключения к базе данных
# SQLite: 'sqlite:///shrinkage_database.db'
# PostgreSQL: 'postgresql://user:password@localhost:5432/shrinkage_db'
'database_url': 'sqlite:///shrinkage_database.db',

# Директория для резервных копий базы данных
'database_backup_path': 'backups/',

# Интервал создания резервных копий (в часах)
'database_backup_interval': 24,
```

### 3.2 Обновление подключения к базе данных

В [src/core/database/database.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/database.py) обновить функцию `get_database_url()` и `create_database_engine()`:

```python
def get_database_url():
    """
    Получает URL для подключения к базе данных.
    
    Returns:
        str: URL для подключения к базе данных
    """
    from src.config import DEFAULT_CONFIG
    return DEFAULT_CONFIG.get('database_url', f"sqlite:///{DB_PATH}")

def create_database_engine():
    """
    Создает движок базы данных.
    
    Returns:
        Engine: Движок SQLAlchemy для работы с базой данных
    """
    try:
        database_url = get_database_url()
        log.info(f"Создание подключения к базе данных: {database_url}")
        
        if database_url.startswith('sqlite'):
            # Для SQLite используем StaticPool для избежания проблем с блокировками
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={'check_same_thread': False},
                echo=False  # Установите True для отладки SQL запросов
            )
        elif database_url.startswith('postgresql'):
            # Для PostgreSQL
            engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                echo=False  # Установите True для отладки SQL запросов
            )
        else:
            raise ValueError(f"Неподдерживаемый тип базы данных: {database_url}")
        
        return engine
    except Exception as e:
        log.error(f"Ошибка при создании подключения к базе данных: {e}")
        raise
```

### 3.3 Добавление поддержки TimescaleDB

Для интеграции TimescaleDB необходимо:

1. Установить расширение TimescaleDB в PostgreSQL
2. Обновить модели для использования гипертаблиц
3. Добавить функции для создания гипертаблиц

### 3.4 Создание миграций Alembic

Создать миграции для PostgreSQL в [src/core/database/alembic/](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/alembic/) директории.

## 4. Тестирование

### 4.1 Модульные тесты

Обновить существующие тесты в [tests/test_database_integration.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/tests/test_database_integration.py) и [tests/test_shrinkage_database_integration.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/tests/test_shrinkage_database_integration.py) для работы с PostgreSQL.

### 4.2 Интеграционные тесты

Создать новые тесты для проверки функциональности TimescaleDB.

## 5. Документация

### 5.1 Руководство по установке PostgreSQL

Создать документацию по установке и настройке PostgreSQL с TimescaleDB.

### 5.2 Руководство по миграции

Создать руководство по миграции с SQLite на PostgreSQL.

### 5.3 Руководство администратора

Создать руководство по администрированию базы данных PostgreSQL для системы.