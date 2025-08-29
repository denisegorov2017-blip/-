# Техническая спецификация системы базы данных для расчета коэффициентов усушки

## Введение

Этот документ содержит техническую спецификацию для реализации системы базы данных в проекте "Система Расчета Усушки". Система базы данных предназначена для хранения, управления и анализа данных, связанных с расчетом коэффициентов усушки рыбы и рыбопродуктов.

## Архитектура системы

### Общая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Приложение (GUI/API)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Сервисный слой (ORM)                      │
│              (src/core/database_service.py)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                Модели данных (SQLAlchemy)                   │
│                 (src/core/models.py)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Драйвер базы данных                       │
│                   (src/core/database.py)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    SQLite Database                          │
└─────────────────────────────────────────────────────────────┘
```

### Технологии

1. **База данных**: SQLite 3
2. **ORM**: SQLAlchemy 1.4+
3. **Миграции**: Alembic
4. **Язык программирования**: Python 3.8+

## Модели данных

### 1. Номенклатура (Nomenclature)

#### Описание
Хранит информацию о номенклатурных позициях продукции.

#### Поля
| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| id | INTEGER | Да | Уникальный идентификатор |
| name | TEXT | Да | Название номенклатуры |
| product_type | TEXT | Да | Тип продукции (fresh_fish, salt_cured, etc.) |
| created_at | TIMESTAMP | Да | Дата создания записи |
| updated_at | TIMESTAMP | Да | Дата последнего обновления |

#### Индексы
- Первичный ключ по [id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L22-L22)
- Уникальный индекс по [name](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L23-L23)

### 2. Записи инвентаризации (InventoryRecord)

#### Описание
Хранит данные инвентаризации для каждой номенклатуры.

#### Поля
| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| id | INTEGER | Да | Уникальный идентификатор |
| nomenclature_id | INTEGER | Да | Ссылка на номенклатуру |
| period_start | DATE | Да | Начало периода |
| period_end | DATE | Да | Конец периода |
| initial_balance | REAL | Да | Начальный остаток |
| incoming | REAL | Да | Приход |
| outgoing | REAL | Да | Расход |
| final_balance | REAL | Да | Конечный остаток |
| storage_days | INTEGER | Да | Период хранения в днях |
| shrinkage_amount | REAL | Нет | Фактическая недостача из инвентаризации |
| shrinkage_coefficient | REAL | Нет | Коэффициент усушки |
| other_losses | REAL | Нет | Другие потери |
| created_at | TIMESTAMP | Да | Дата создания записи |

#### Индексы
- Первичный ключ по [id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L41-L41)
- Внешний ключ по [nomenclature_id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L42-L42)
- Индекс по [period_start](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L43-L43), [period_end](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L44-L44)

### 3. Коэффициенты усушки (ShrinkageCoefficient)

#### Описание
Хранит рассчитанные коэффициенты усушки для каждой номенклатуры.

#### Поля
| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| id | INTEGER | Да | Уникальный идентификатор |
| nomenclature_id | INTEGER | Да | Ссылка на номенклатуру |
| model_type | TEXT | Да | Тип модели (exponential, linear, polynomial) |
| coefficient_a | REAL | Нет | Коэффициент a |
| coefficient_b | REAL | Нет | Коэффициент b |
| coefficient_c | REAL | Нет | Коэффициент c |
| accuracy | REAL | Нет | Точность модели |
| period_start | DATE | Да | Начало периода |
| period_end | DATE | Да | Конец периода |
| data_points | INTEGER | Нет | Количество точек данных |
| is_adaptive | BOOLEAN | Нет | Признак адаптивной модели |
| created_at | TIMESTAMP | Да | Дата создания записи |

#### Индексы
- Первичный ключ по [id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L74-L74)
- Внешний ключ по [nomenclature_id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L75-L75)
- Индекс по [model_type](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L76-L76)

### 4. Прогнозы (Prediction)

#### Описание
Хранит результаты прогнозирования усушки.

#### Поля
| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| id | INTEGER | Да | Уникальный идентификатор |
| nomenclature_id | INTEGER | Да | Ссылка на номенклатуру |
| initial_balance | REAL | Да | Начальный остаток |
| predicted_shrinkage | REAL | Да | Прогнозируемая усушка |
| shrinkage_rate | REAL | Да | Коэффициент усушки |
| final_balance | REAL | Да | Прогнозируемый остаток |
| days | INTEGER | Да | Период прогнозирования в днях |
| model_type | TEXT | Да | Тип модели |
| coefficient_a | REAL | Нет | Коэффициент a |
| coefficient_b | REAL | Нет | Коэффициент b |
| coefficient_c | REAL | Нет | Коэффициент c |
| created_at | TIMESTAMP | Да | Дата создания записи |

#### Индексы
- Первичный ключ по [id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L107-L107)
- Внешний ключ по [nomenclature_id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L108-L108)

### 5. Логи расчетов (CalculationLog)

#### Описание
Хранит логи операций расчета и прогнозирования.

#### Поля
| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| id | INTEGER | Да | Уникальный идентификатор |
| nomenclature_id | INTEGER | Да | Ссылка на номенклатуру |
| operation_type | TEXT | Да | Тип операции (calculation, prediction, adaptation) |
| status | TEXT | Да | Статус операции (success, error, warning) |
| message | TEXT | Нет | Сообщение о результате операции |
| details | TEXT | Нет | Детали операции в формате JSON |
| created_at | TIMESTAMP | Да | Дата создания записи |

#### Индексы
- Первичный ключ по [id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L155-L155)
- Внешний ключ по [nomenclature_id](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L156-L156)
- Индекс по [operation_type](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L157-L157), [status](file:///C:/Users/D_909/Desktop/%D0%B4%D0%BB%D1%8F%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0/src/core/models.py#L158-L158)

## API сервисного слоя

### Основные функции

#### 1. Управление номенклатурой
```python
def create_nomenclature(name: str, product_type: str) -> Nomenclature
def get_nomenclature_by_id(nomenclature_id: int) -> Nomenclature
def get_nomenclature_by_name(name: str) -> Nomenclature
def list_nomenclatures() -> List[Nomenclature]
def update_nomenclature(nomenclature_id: int, **kwargs) -> Nomenclature
def delete_nomenclature(nomenclature_id: int) -> bool
```

#### 2. Управление записями инвентаризации
```python
def create_inventory_record(**kwargs) -> InventoryRecord
def get_inventory_record_by_id(record_id: int) -> InventoryRecord
def list_inventory_records(nomenclature_id: int = None, 
                          start_date: date = None, 
                          end_date: date = None) -> List[InventoryRecord]
def update_inventory_record(record_id: int, **kwargs) -> InventoryRecord
def delete_inventory_record(record_id: int) -> bool
```

#### 3. Управление коэффициентами усушки
```python
def create_shrinkage_coefficient(**kwargs) -> ShrinkageCoefficient
def get_coefficient_by_id(coefficient_id: int) -> ShrinkageCoefficient
def get_latest_coefficients(nomenclature_id: int, 
                           model_type: str = None) -> List[ShrinkageCoefficient]
def list_coefficients(nomenclature_id: int = None, 
                     model_type: str = None) -> List[ShrinkageCoefficient]
def update_coefficient(coefficient_id: int, **kwargs) -> ShrinkageCoefficient
def delete_coefficient(coefficient_id: int) -> bool
```

#### 4. Управление прогнозами
```python
def create_prediction(**kwargs) -> Prediction
def get_prediction_by_id(prediction_id: int) -> Prediction
def list_predictions(nomenclature_id: int = None, 
                    start_date: datetime = None) -> List[Prediction]
def delete_prediction(prediction_id: int) -> bool
```

#### 5. Управление логами
```python
def create_calculation_log(**kwargs) -> CalculationLog
def get_log_by_id(log_id: int) -> CalculationLog
def list_logs(nomenclature_id: int = None, 
             operation_type: str = None, 
             status: str = None) -> List[CalculationLog]
def delete_old_logs(days_old: int = 30) -> int  # Возвращает количество удаленных записей
```

#### 6. Аналитические функции
```python
def get_nomenclature_statistics(nomenclature_id: int) -> dict
def get_model_accuracy_statistics(model_type: str) -> dict
def get_prediction_accuracy_history(nomenclature_id: int) -> List[dict]
def get_shrinkage_trends(nomenclature_id: int, 
                        start_date: date, 
                        end_date: date) -> List[dict]
```

## Интеграция с существующей системой

### Модификация ShrinkageSystem

#### Добавление зависимости от базы данных
```python
# В __init__ класса ShrinkageSystem
from core.database import get_db_session
from core.database_service import DatabaseService

# Инициализация сервиса базы данных
self.db_service = DatabaseService()
```

#### Сохранение результатов расчетов
```python
# В методе process_dataset
def process_dataset(self, dataset: pd.DataFrame, source_filename: str, use_adaptive: bool = False):
    # Существующая логика расчета
    processing_results = self.data_processor.calculate_coefficients(dataset, self.surplus_rates)
    
    # Новая логика сохранения в базу данных
    self._save_calculation_results(processing_results, source_filename)
    
    return processing_results

def _save_calculation_results(self, results: dict, source_filename: str):
    """Сохраняет результаты расчетов в базу данных"""
    try:
        # Сохранение номенклатур
        # Сохранение коэффициентов
        # Сохранение логов
        pass
    except Exception as e:
        log.error(f"Ошибка сохранения результатов в БД: {e}")
```

### Модификация ShrinkageCalculator

#### Использование исторических данных
```python
# В методе calculate_coefficients
def calculate_coefficients(self, nomenclature_data: Dict[str, Any], model_type: str = 'exponential'):
    # Получение исторических данных из базы
    historical_data = self.db_service.get_historical_data(nomenclature_data['name'])
    
    # Использование исторических данных для улучшения расчетов
    # ...
    
    return result
```

## Миграция данных

### Скрипт миграции из JSON в базу данных
```python
def migrate_json_to_database(json_file_path: str):
    """Мигрирует данные из JSON файла в базу данных"""
    # Чтение JSON файла
    # Преобразование данных в формат базы данных
    # Сохранение в соответствующие таблицы
    pass
```

## Производительность и оптимизация

### Индексация
1. Создание индексов по часто используемым полям
2. Оптимизация запросов с помощью составных индексов

### Кэширование
1. Реализация кэширования часто запрашиваемых данных
2. Использование механизма кэширования SQLAlchemy

### Пагинация
1. Реализация пагинации для больших наборов данных
2. Ограничение количества возвращаемых записей

## Безопасность

### Защита данных
1. Валидация всех входных данных
2. Использование параметризованных запросов
3. Ограничение доступа к чувствительным операциям

### Резервное копирование
1. Автоматическое создание резервных копий
2. Возможность восстановления из резервной копии

## Тестирование

### Unit-тесты
1. Тестирование всех моделей данных
2. Тестирование сервисного слоя
3. Тестирование функций миграции

### Интеграционные тесты
1. Тестирование интеграции с основной системой
2. Тестирование производительности
3. Тестирование обработки ошибок

## Развертывание

### Установка зависимостей
```bash
pip install sqlalchemy alembic
```

### Инициализация базы данных
```bash
alembic upgrade head
```

### Миграция существующих данных
```bash
python scripts/migrate_data.py
```

## Мониторинг и логирование

### Логирование операций
1. Логирование всех операций записи
2. Логирование ошибок и предупреждений
3. Логирование времени выполнения запросов

### Мониторинг производительности
1. Сбор метрик производительности
2. Мониторинг использования ресурсов
3. Оповещение о проблемах производительности

## Расширяемость

### Поддержка других СУБД
1. Абстракция слоя доступа к данным
2. Поддержка PostgreSQL, MySQL при необходимости

### Расширение функциональности
1. Добавление новых типов моделей
2. Расширение аналитических возможностей
3. Интеграция с внешними системами