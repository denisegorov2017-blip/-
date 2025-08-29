# Реализация поддержки PostgreSQL в системе расчета коэффициентов усушки

## 1. Введение

В рамках данного проекта была реализована поддержка PostgreSQL в качестве альтернативной СУБД для системы расчета нелинейных коэффициентов усушки. Это позволяет использовать систему в производственных средах с большими объемами данных и обеспечивает лучшую масштабируемость по сравнению с SQLite.

## 2. Архитектурные изменения

### 2.1 Поддержка нескольких СУБД

Реализована гибкая архитектура, позволяющая использовать различные СУБД без изменения бизнес-логики системы:

1. **Конфигурация** - URL базы данных задается в [src/config.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/config.py)
2. **Подключение** - динамическое создание движка SQLAlchemy в [src/core/database/database.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/database.py)
3. **Модели** - универсальные модели SQLAlchemy, совместимые с разными СУБД

### 2.2 Интеграция TimescaleDB

Добавлена поддержка TimescaleDB для оптимизации работы с временными рядами:

1. **Гипертаблицы** - автоматическое создание гипертаблиц для временных данных
2. **Оптимизация** - улучшенная производительность запросов к временным данным
3. **Мониторинг** - инструменты для отслеживания состояния TimescaleDB

## 3. Реализованные компоненты

### 3.1 Ядро базы данных

Файл: [src/core/database/database.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/database.py)

- Динамическое определение типа СУБД по URL
- Создание движков для SQLite и PostgreSQL
- Универсальная инициализация базы данных

### 3.2 Модели данных

Файл: [src/core/database/models.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/models.py)

- 18 таблиц для хранения всех данных системы
- Совместимость с SQLite и PostgreSQL
- Поддержка временных меток для TimescaleDB

### 3.3 Сервисный слой

Файл: [src/core/database/services.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/services.py)

- CRUD операции для всех таблиц
- Аналитические функции
- Управление транзакциями

### 3.4 Интеграция с системой

Файл: [src/core/database/integration.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/integration.py)

- Сохранение результатов расчетов
- Загрузка исторических данных
- Получение статистики

### 3.5 Утилиты базы данных

Файл: [src/core/database/utils.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/utils.py)

- Резервное копирование и восстановление
- Получение информации о базе данных
- Оптимизация (VACUUM/REINDEX)
- Тестирование подключения

### 3.6 TimescaleDB интеграция

Файл: [src/core/database/timescaledb.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/timescaledb.py)

- Проверка доступности расширения
- Создание гипертаблиц
- Оптимизация с TimescaleDB
- Получение информации о TimescaleDB

### 3.7 CLI инструменты

Файл: [src/core/database/cli.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/cli.py)

- Инициализация базы данных
- Получение информации
- Резервное копирование
- Оптимизация
- Работа с TimescaleDB

### 3.8 Миграции

Файлы: [src/core/database/alembic/](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/database/alembic/)

- Поддержка Alembic миграций
- Конфигурация для разных СУБД
- Скрипты для запуска миграций

## 4. Скрипты и инструменты

### 4.1 Миграция с SQLite на PostgreSQL

Файл: [scripts/migrate_to_postgresql.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/scripts/migrate_to_postgresql.py)

- Экспорт данных из SQLite в CSV
- Поддержка всех таблиц системы

### 4.2 Инициализация PostgreSQL

Файл: [scripts/init_postgresql.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/scripts/init_postgresql.py)

- Проверка конфигурации
- Инициализация базы данных
- Оптимизация с TimescaleDB

### 4.3 Запуск миграций

Файл: [scripts/run_migrations.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/scripts/run_migrations.py)

- Управление миграциями Alembic
- Поддержка разных команд

## 5. Тестирование

### 5.1 Модульные тесты

Файл: [tests/test_postgresql_integration.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/tests/test_postgresql_integration.py)

- Тесты подключения к PostgreSQL
- Тесты создания записей
- Тесты интеграции TimescaleDB

### 5.2 Примеры использования

Файл: [examples/postgresql_example.py](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/examples/postgresql_example.py)

- Полный пример работы с PostgreSQL
- Демонстрация TimescaleDB возможностей

## 6. Документация

### 6.1 Настройка PostgreSQL

Файл: [документация/настройка_postgresql.md](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F/%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0_postgresql.md)

- Установка PostgreSQL
- Настройка базы данных
- Установка TimescaleDB
- Конфигурация системы

### 6.2 Миграция с SQLite

Файл: [документация/миграция_с_sqlite_на_postgresql.md](file:///c%3A/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F/%D0%BC%D0%B8%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F_%D1%81_sqlite_%D0%BD%D0%B0_postgresql.md)

- Подготовка к миграции
- Процесс миграции
- Решение проблем

## 7. Преимущества реализации

### 7.1 Производительность

- Лучшая обработка больших объемов данных
- Оптимизация временных рядов с TimescaleDB
- Поддержка параллельных соединений

### 7.2 Масштабируемость

- Поддержка кластеризации
- Возможность распределения нагрузки
- Лучшее управление ресурсами

### 7.3 Надежность

- Транзакционная целостность
- Расширенные возможности резервного копирования
- Лучшая система восстановления

### 7.4 Совместимость

- Сохранение обратной совместимости с SQLite
- Единый API для работы с разными СУБД
- Постепенная миграция без простоя системы

## 8. Заключение

Реализация поддержки PostgreSQL в системе расчета коэффициентов усушки значительно расширяет возможности системы и делает ее пригодной для использования в производственных средах. Интеграция с TimescaleDB обеспечивает оптимальную производительность при работе с временными рядами, что особенно важно для системы анализа усушки.

Все компоненты системы были успешно протестированы и готовы к использованию. Документация предоставляет полное руководство по настройке и использованию новой функциональности.