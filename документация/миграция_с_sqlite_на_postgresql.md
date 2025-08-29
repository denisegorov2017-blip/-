# Руководство по миграции с SQLite на PostgreSQL

## 1. Подготовка к миграции

### 1.1 Резервное копирование текущей базы данных

Перед началом миграции обязательно создайте резервную копию текущей SQLite базы данных:

```bash
# Создайте резервную копию файла базы данных
cp shrinkage_database.db shrinkage_database_backup.db

# Или используйте встроенный инструмент
python -m src.core.database.cli backup
```

### 1.2 Экспорт данных из SQLite

Используйте скрипт миграции для экспорта данных в CSV:

```bash
python scripts/migrate_to_postgresql.py
```

Выберите опцию 1 для экспорта данных в CSV файлы.

## 2. Настройка PostgreSQL

### 2.1 Установка PostgreSQL

Следуйте инструкциям в [настройка_postgresql.md](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F/%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0_postgresql.md) для установки и настройки PostgreSQL.

### 2.2 Создание базы данных

```sql
-- Подключитесь к PostgreSQL
psql -U postgres

-- Создайте базу данных
CREATE DATABASE shrinkage_db;

-- Создайте пользователя (опционально)
CREATE USER shrinkage_user WITH PASSWORD 'your_password';

-- Назначьте привилегии
GRANT ALL PRIVILEGES ON DATABASE shrinkage_db TO shrinkage_user;

-- Выйдите из psql
\q
```

## 3. Настройка конфигурации

### 3.1 Обновление файла конфигурации

Откройте файл [src/config.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/config.py) и обновите параметр `database_url`:

```python
# Обновите URL базы данных
'database_url': 'postgresql://shrinkage_user:your_password@localhost:5432/shrinkage_db'
```

### 3.2 Проверка конфигурации

```bash
# Проверьте подключение к новой базе данных
python -m src.core.database.cli test
```

## 4. Инициализация новой базы данных

```bash
# Инициализируйте структуру базы данных
python -m src.core.database.cli init
```

## 5. Импорт данных

### 5.1 Создание скрипта импорта

Создайте скрипт для импорта данных из CSV файлов в PostgreSQL базу данных:

```python
# import_data_to_postgresql.py
import pandas as pd
from sqlalchemy import create_engine
from src.config import DEFAULT_CONFIG

def import_data_from_csv():
    """Импортирует данные из CSV файлов в PostgreSQL базу данных."""
    
    # Получаем URL базы данных
    database_url = DEFAULT_CONFIG['database_url']
    
    # Создаем движок SQLAlchemy
    engine = create_engine(database_url)
    
    # Список таблиц для импорта
    tables = [
        'source_data',
        'nomenclature', 
        'calculation_data',
        'models',
        'coefficients',
        'forecasts',
        'analytics',
        'ai_patterns',
        'validation_errors',
        'priority_periods',
        'preliminary_forecasts',
        'surplus_specifications',
        'surplus_recommendations',
        'surplus_patterns',
        'pattern_validations',
        'feedback_preferences',
        'data_lineage',
        'ml_model_registry'
    ]
    
    imported_count = 0
    
    for table_name in tables:
        try:
            # Читаем CSV файл
            csv_file = f'exports/{table_name}.csv'
            df = pd.read_csv(csv_file)
            
            # Импортируем данные в таблицу
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Импортировано {len(df)} записей в таблицу {table_name}")
            imported_count += 1
            
        except FileNotFoundError:
            print(f"Файл {csv_file} не найден, пропускаем таблицу {table_name}")
        except Exception as e:
            print(f"Ошибка при импорте таблицы {table_name}: {e}")
    
    print(f"Импорт завершен. Обработано {imported_count} таблиц.")

if __name__ == '__main__':
    import_data_from_csv()
```

### 5.2 Запуск импорта

```bash
# Запустите скрипт импорта
python import_data_to_postgresql.py
```

## 6. Проверка миграции

### 6.1 Проверка данных

```bash
# Получите информацию о новой базе данных
python -m src.core.database.cli info
```

### 6.2 Тестирование функциональности

Запустите тесты для проверки работы с новой базой данных:

```bash
# Запустите тесты
python -m pytest tests/test_postgresql_integration.py -v
```

## 7. Оптимизация с TimescaleDB

### 7.1 Проверка TimescaleDB

```bash
# Получите информацию о TimescaleDB
python -m src.core.database.cli timescaledb
```

### 7.2 Оптимизация таблиц

```bash
# Оптимизируйте таблицы с TimescaleDB
python -m src.core.database.cli optimize
```

## 8. Переключение системы на новую базу данных

После успешной миграции и тестирования система будет автоматически использовать новую PostgreSQL базу данных, так как URL базы данных уже обновлен в конфигурации.

## 9. Удаление старых файлов (опционально)

После проверки, что все работает корректно, можно удалить старый файл SQLite базы данных:

```bash
# Удалите старый файл базы данных
rm shrinkage_database.db
```

## 10. Решение возможных проблем

### 10.1 Ошибки импорта данных

Если возникают ошибки при импорте данных:
1. Проверьте формат дат в CSV файлах
2. Убедитесь, что все обязательные поля заполнены
3. Проверьте ограничения целостности данных

### 10.2 Проблемы с подключением

Если возникают проблемы с подключением:
1. Проверьте правильность URL базы данных
2. Убедитесь, что PostgreSQL сервер запущен
3. Проверьте настройки аутентификации

### 10.3 Ошибки TimescaleDB

Если возникают ошибки с TimescaleDB:
1. Проверьте, установлено ли расширение
2. Убедитесь, что версии совместимы
3. Проверьте логи PostgreSQL

## 11. Мониторинг после миграции

### 11.1 Проверка производительности

Сравните время выполнения операций до и после миграции.

### 11.2 Мониторинг использования ресурсов

Отслеживайте использование CPU, памяти и дискового пространства.

### 11.3 Логирование ошибок

Проверяйте логи системы на наличие ошибок после миграции.