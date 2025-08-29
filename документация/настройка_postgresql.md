# Настройка PostgreSQL для системы расчета коэффициентов усушки

## 1. Установка PostgreSQL

### 1.1 Установка на Windows

1. Скачайте установщик PostgreSQL с [официального сайта](https://www.postgresql.org/download/windows/)
2. Запустите установщик и следуйте инструкциям мастера установки
3. При установке выберите компоненты:
   - PostgreSQL Server
   - pgAdmin 4
   - Command Line Tools
4. Задайте пароль для суперпользователя (postgres)
5. Выберите порт (по умолчанию 5432)
6. Завершите установку

### 1.2 Установка на Linux (Ubuntu/Debian)

```bash
# Обновите список пакетов
sudo apt update

# Установите PostgreSQL
sudo apt install postgresql postgresql-contrib

# Запустите службу PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 1.3 Установка на macOS

```bash
# Установка через Homebrew
brew install postgresql

# Запуск службы
brew services start postgresql
```

## 2. Настройка базы данных

### 2.1 Создание базы данных

#### В Windows (через pgAdmin):
1. Откройте pgAdmin
2. Подключитесь к серверу PostgreSQL
3. Щелкните правой кнопкой мыши на "Databases"
4. Выберите "Create" → "Database"
5. Введите имя базы данных (например, `shrinkage_db`)
6. Нажмите "Save"

#### В командной строке:
```bash
# Переключитесь на пользователя postgres (в Linux/macOS)
sudo -u postgres psql

# Создайте базу данных
CREATE DATABASE shrinkage_db;

# Создайте пользователя (опционально)
CREATE USER shrinkage_user WITH PASSWORD 'your_password';

# Назначьте привилегии
GRANT ALL PRIVILEGES ON DATABASE shrinkage_db TO shrinkage_user;

# Выйдите из psql
\q
```

## 3. Установка TimescaleDB

### 3.1 Установка на Windows

TimescaleDB для Windows устанавливается вместе с PostgreSQL при выборе соответствующих компонентов в установщике.

### 3.2 Установка на Linux

```bash
# Добавьте репозиторий TimescaleDB
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list

# Обновите список пакетов
sudo apt update

# Установите TimescaleDB
sudo apt install timescaledb-2-postgresql-14

# Настройте TimescaleDB
sudo timescaledb-tune --quiet --yes

# Перезапустите PostgreSQL
sudo systemctl restart postgresql
```

### 3.3 Установка на macOS

```bash
# Установка через Homebrew
brew tap timescale/tap
brew install timescaledb

# Настройте TimescaleDB
/usr/local/bin/timescaledb-tune --quiet --yes

# Перезапустите PostgreSQL
brew services restart postgresql
```

### 3.4 Активация расширения TimescaleDB

```sql
-- Подключитесь к вашей базе данных
psql -U your_user -d shrinkage_db

-- Активируйте расширение TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Проверьте установку
SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';
```

## 4. Настройка конфигурации системы

### 4.1 Обновление файла конфигурации

Откройте файл [src/config.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/config.py) и обновите параметр `database_url`:

```python
# Для локальной установки PostgreSQL
'database_url': 'postgresql://postgres:your_password@localhost:5432/shrinkage_db'

# Или с пользователем
'database_url': 'postgresql://shrinkage_user:your_password@localhost:5432/shrinkage_db'
```

### 4.2 Тестирование подключения

```bash
# Перейдите в директорию проекта
cd путь/к/проекту

# Запустите тест подключения
python -m src.core.database.cli test
```

## 5. Инициализация базы данных

```bash
# Инициализируйте базу данных
python -m src.core.database.cli init
```

## 6. Оптимизация с TimescaleDB

После инициализации базы данных можно оптимизировать таблицы с помощью TimescaleDB:

```bash
# Создайте скрипт оптимизации (пример)
python -c "
from src.core.database.timescaledb import optimize_with_timescaledb
optimize_with_timescaledb()
"
```

## 7. Миграция существующих данных

Если у вас есть существующие данные в SQLite:

1. Экспортируйте данные из SQLite:
   ```bash
   python scripts/migrate_to_postgresql.py
   ```

2. Выберите опцию экспорта в CSV

3. Импортируйте данные в PostgreSQL (потребуется отдельный скрипт импорта)

## 8. Резервное копирование и восстановление

### 8.1 Резервное копирование

```bash
# Используйте pg_dump для резервного копирования
pg_dump -U your_user -h localhost -d shrinkage_db > backup.sql
```

### 8.2 Восстановление

```bash
# Используйте pg_restore для восстановления
psql -U your_user -h localhost -d shrinkage_db < backup.sql
```

## 9. Мониторинг и обслуживание

### 9.1 Проверка состояния базы данных

```bash
# Получите информацию о базе данных
python -m src.core.database.cli info
```

### 9.2 Оптимизация базы данных

```bash
# Выполните оптимизацию
python -m src.core.database.cli vacuum
```

## 10. Устранение неполадок

### 10.1 Ошибка подключения

Если возникает ошибка подключения:
1. Проверьте, запущен ли сервер PostgreSQL
2. Проверьте правильность URL подключения
3. Убедитесь, что пользователь имеет доступ к базе данных

### 10.2 Ошибка TimescaleDB

Если TimescaleDB не работает:
1. Проверьте, установлено ли расширение
2. Убедитесь, что версия TimescaleDB совместима с PostgreSQL
3. Проверьте логи PostgreSQL на наличие ошибок

### 10.3 Проблемы с производительностью

Для оптимизации производительности:
1. Используйте гипертаблицы для временных данных
2. Настройте индексы
3. Регулярно выполняйте VACUUM и ANALYZE