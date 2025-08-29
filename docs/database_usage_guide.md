# Руководство по использованию базы данных системы расчета коэффициентов усушки

## Обзор

База данных системы расчета коэффициентов усушки предоставляет возможность хранения, анализа и извлечения исторических данных о расчетах коэффициентов усушки рыбной продукции. Система использует SQLite в качестве основной СУБД с возможностью миграции на PostgreSQL в будущем.

## Архитектура базы данных

### Технологии

- **SQLite** - основная СУБД для локального использования
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - инструмент для миграций базы данных
- **Python** - язык программирования

### Основные таблицы

1. **source_data** - информация об исходных файлах данных
2. **nomenclature** - информация о номенклатурных позициях
3. **calculation_data** - нормализованные данные для расчетов
4. **models** - информация о моделях расчета
5. **coefficients** - рассчитанные коэффициенты
6. **forecasts** - прогнозы усушки
7. **analytics** - агрегированные данные для анализа
8. **ai_patterns** - паттерны и аномалии, найденные с помощью ИИ
9. **validation_errors** - информация об ошибках валидации
10. **priority_periods** - периоды с повышенным приоритетом для анализа
11. **preliminary_forecasts** - предварительные прогнозы усушки
12. **surplus_specifications** - информация о периодических указаниях излишков
13. **surplus_recommendations** - автоматически сгенерированные рекомендации по излишкам
14. **surplus_patterns** - информация о постоянных паттернах излишков
15. **pattern_validations** - результаты валидации и обратной связи по паттернам
16. **feedback_preferences** - гибкие настройки обратной связи
17. **data_lineage** - информация о происхождении данных
18. **ml_model_registry** - реестр моделей машинного обучения

## Установка и настройка

### Установка зависимостей

Для работы с базой данных необходимо установить дополнительные зависимости:

```bash
pip install sqlalchemy alembic psycopg2-binary
```

Эти зависимости уже добавлены в файл `requirements.txt`.

### Конфигурация

Конфигурация базы данных находится в файле `src/config.py`:

```python
DEFAULT_CONFIG = {
    # ... другие настройки ...
    
    # === Настройки базы данных ===
    # Включена ли база данных
    'enable_database': False,
    
    # URL для подключения к базе данных
    'database_url': 'sqlite:///shrinkage_database.db',
    
    # Директория для резервных копий базы данных
    'database_backup_path': 'backups/',
    
    # Интервал создания резервных копий (в часах)
    'database_backup_interval': 24
}
```

Для включения базы данных установите параметр `'enable_database': True`.

## Использование базы данных

### Инициализация базы данных

Для инициализации базы данных выполните команду:

```bash
python -m alembic.config -c src/core/database/alembic.ini upgrade head
```

Или используйте CLI утилиту:

```bash
python src/core/database/cli.py init
```

### Работа с данными через интеграцию

Система автоматически сохраняет результаты расчетов в базу данных, если интеграция включена в конфигурации.

#### Сохранение результатов расчетов

```python
from src.core.database.integration import save_calculation_results

# Сохранение результатов расчетов
save_calculation_results(
    source_filename="исходные_данные/инвентаризация.xlsx",
    dataset=dataframe,
    coefficients_results=coefficients,
    error_results=errors
)
```

#### Загрузка исторических данных

```python
from src.core.database.integration import load_historical_data

# Загрузка исторических данных для номенклатуры
historical_data = load_historical_data("СИНЕЦ ВЯЛЕНЫЙ")
```

### Использование CLI утилиты

CLI утилита предоставляет набор команд для управления базой данных:

```bash
# Инициализация базы данных
python src/core/database/cli.py init

# Получение информации о базе данных
python src/core/database/cli.py info

# Создание резервной копии
python src/core/database/cli.py backup

# Восстановление из резервной копии
python src/core/database/cli.py restore backup.db.bak

# Оптимизация базы данных
python src/core/database/cli.py vacuum

# Тестирование подключения
python src/core/database/cli.py test
```

## Интеграция с основной системой

### Автоматическое сохранение результатов

Когда база данных включена в конфигурации, система автоматически сохраняет результаты расчетов в базу данных после каждого выполнения метода `process_dataset` класса `ShrinkageSystem`.

### Использование исторических данных

Адаптивные модели могут использовать исторические данные из базы данных для улучшения точности расчетов. Это реализуется через методы интеграции, которые загружают исторические данные по запросу.

## Расширенная аналитика

### Анализ трендов по номенклатуре

Для анализа трендов по конкретной номенклатуре используйте метод `get_nomenclature_trend_analysis`:

```python
from src.core.database.database import get_db_session
from src.core.database.services import get_database_service

# Получение сессии и сервиса
Session = get_db_session()
session = Session()
db_service = get_database_service(session)

# Анализ трендов по номенклатуре за последние 30 дней
trend_analysis = db_service.get_nomenclature_trend_analysis(
    nomenclature_id=1, 
    days=30
)

print(f"Средний коэффициент A: {trend_analysis['avg_coefficient_a']}")
print(f"Средний коэффициент B: {trend_analysis['avg_coefficient_b']}")
print(f"Средний коэффициент C: {trend_analysis['avg_coefficient_c']}")
print(f"Направление тренда точности: {trend_analysis['accuracy_trend']}")

session.close()
```

### Сравнительный анализ моделей

Для сравнения эффективности различных моделей используйте метод `get_model_comparison_analysis`:

```python
from src.core.database.database import get_db_session
from src.core.database.services import get_database_service

# Получение сессии и сервиса
Session = get_db_session()
session = Session()
db_service = get_database_service(session)

# Сравнительный анализ всех моделей
model_comparison = db_service.get_model_comparison_analysis()

print(f"Лучшая модель: {model_comparison['best_model']['model_name']}")
print(f"Точность лучшей модели: {model_comparison['best_model']['avg_accuracy']:.2f}")

# Вывод статистики по всем моделям
for model in model_comparison['models']:
    print(f"Модель: {model['model_name']}, Точность: {model['avg_accuracy']:.2f}")

session.close()
```

### Отчет о производительности номенклатур

Для получения отчета о производительности номенклатур используйте метод `get_nomenclature_performance_report`:

```python
from src.core.database.database import get_db_session
from src.core.database.services import get_database_service

# Получение сессии и сервиса
Session = get_db_session()
session = Session()
db_service = get_database_service(session)

# Отчет о производительности топ-10 номенклатур
performance_report = db_service.get_nomenclature_performance_report(limit=10)

print(f"Всего номенклатур в отчете: {performance_report['total_nomenclatures']}")

# Вывод топ номенклатур
for item in performance_report['top_performing']:
    print(f"Номенклатура: {item['nomenclature_name']}")
    print(f"  Количество расчетов: {item['calculation_count']}")
    print(f"  Средняя точность: {item['avg_accuracy']:.2f}")
    print(f"  Количество ошибок: {item['error_count']}")

session.close()
```

## Расширенные аналитические отчеты

Система также предоставляет возможность генерации расширенных аналитических отчетов в формате HTML.

### Генерация отчета о трендах

```python
from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter
from src.config import DEFAULT_CONFIG

# Создание репортера
config = DEFAULT_CONFIG.copy()
reporter = AdvancedAnalyticsReporter(config)

# Генерация отчета о трендах для номенклатуры
report_path = reporter.generate_trend_analysis_report(
    nomenclature_id=1,
    nomenclature_name="СИНЕЦ ВЯЛЕНЫЙ",
    days=30
)

print(f"Отчет о трендах сохранен: {report_path}")
```

### Генерация отчета о сравнении моделей

```python
from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter
from src.config import DEFAULT_CONFIG

# Создание репортера
config = DEFAULT_CONFIG.copy()
reporter = AdvancedAnalyticsReporter(config)

# Генерация отчета о сравнении моделей
report_path = reporter.generate_model_comparison_report()

print(f"Отчет о сравнении моделей сохранен: {report_path}")
```

### Генерация отчета о производительности номенклатур

```python
from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter
from src.config import DEFAULT_CONFIG

# Создание репортера
config = DEFAULT_CONFIG.copy()
reporter = AdvancedAnalyticsReporter(config)

# Генерация отчета о производительности номенклатур
report_path = reporter.generate_nomenclature_performance_report(limit=20)

print(f"Отчет о производительности номенклатур сохранен: {report_path}")
```

### Генерация комплексного аналитического отчета

```python
from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter
from src.config import DEFAULT_CONFIG

# Создание репортера
config = DEFAULT_CONFIG.copy()
reporter = AdvancedAnalyticsReporter(config)

# Генерация комплексного аналитического отчета
reports = reporter.generate_comprehensive_analytics_report()

for report_type, report_path in reports.items():
    print(f"{report_type}: {report_path}")
```

## Миграции базы данных

### Создание новой миграции

Для создания новой миграции после изменения моделей:

```bash
python -m alembic.config -c src/core/database/alembic.ini revision --autogenerate -m "Описание изменений"
```

### Применение миграций

Для применения миграций:

```bash
python -m alembic.config -c src/core/database/alembic.ini upgrade head
```

## Резервное копирование и восстановление

### Создание резервной копии

```python
from src.core.database.utils import create_database_backup

# Создание резервной копии
backup_file = create_database_backup()
```

Или через CLI:

```bash
python src/core/database/cli.py backup
```

### Восстановление из резервной копии

```python
from src.core.database.utils import restore_database_from_backup

# Восстановление из резервной копии
restore_database_from_backup("shrinkage_database.db_20230101_120000.bak")
```

Или через CLI:

```bash
python src/core/database/cli.py restore shrinkage_database.db_20230101_120000.bak
```

## Мониторинг и обслуживание

### Получение информации о базе данных

```python
from src.core.database.utils import get_database_info

# Получение информации о базе данных
info = get_database_info()
print(f"Размер базы данных: {info['size_mb']} МБ")
print(f"Количество записей: {info['total_rows']}")
```

### Оптимизация базы данных

```python
from src.core.database.utils import vacuum_database

# Оптимизация базы данных (только для SQLite)
vacuum_database()
```

Или через CLI:

```bash
python src/core/database/cli.py vacuum
```

## Тестирование

### Запуск тестов

Для тестирования функциональности базы данных выполните:

```bash
pytest tests/test_database_integration.py -v
```

Для тестирования расширенной аналитики:

```bash
pytest tests/test_advanced_analytics.py -v
pytest tests/test_advanced_analytics_reporter.py -v
```

## Лучшие практики

### Безопасность

1. Не храните чувствительные данные в открытом виде
2. Используйте параметризованные запросы для предотвращения SQL-инъекций
3. Регулярно создавайте резервные копии

### Производительность

1. Используйте индексы для часто запрашиваемых полей
2. Ограничивайте количество возвращаемых записей при больших выборках
3. Регулярно выполняйте оптимизацию базы данных

### Обслуживание

1. Регулярно создавайте резервные копии
2. Мониторьте размер базы данных
3. Удаляйте устаревшие данные при необходимости

## Устранение неполадок

### Проблемы с подключением

1. Проверьте правильность URL подключения в конфигурации
2. Убедитесь, что файл базы данных доступен для чтения/записи
3. Проверьте, не заблокирован ли файл базы данных другим процессом

### Проблемы с миграциями

1. Убедитесь, что все зависимости установлены
2. Проверьте, что путь к конфигурационному файлу Alembic корректен
3. При необходимости удалите файл базы данных и выполните инициализацию заново

## Расширение функциональности

### Добавление новых таблиц

1. Добавьте новую модель в `src/core/database/models.py`
2. Создайте миграцию: `alembic revision --autogenerate -m "Добавление новой таблицы"`
3. Примените миграцию: `alembic upgrade head`

### Интеграция с внешними системами

1. Используйте SQLAlchemy для создания подключения к внешним базам данных
2. Реализуйте адаптеры для преобразования данных
3. Добавьте необходимые методы в сервисный слой

## Заключение

База данных системы расчета коэффициентов усушки предоставляет мощные возможности для хранения, анализа и извлечения исторических данных. При правильном использовании она может значительно повысить эффективность работы с данными усушки и улучшить точность прогнозов.