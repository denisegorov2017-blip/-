# Система Расчета Коэффициентов Нелинейной Усушки

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Описание

Система расчета коэффициентов нелинейной усушки - это комплексное решение для точного расчета и прогнозирования усушки продукции в различных отраслях. Система автоматизирует весь процесс от обработки исходных данных до генерации финальных отчетов с визуализацией.

## Основные возможности

- 📊 **Многоформатная обработка данных**: Поддержка Excel (xlsx, xls, xlsm), CSV и баз данных
- 🧠 **Адаптивная модель расчета**: Самообучающаяся модель с учетом внешних факторов
- 🖥️ **Множественные интерфейсы**: Flet, Tkinter, Streamlit и командная строка
- 📈 **Визуализация данных**: Интерактивные графики и дашборды
- ⚙️ **Гибкая конфигурация**: Расширенная система настроек для всех аспектов работы
- 🛡️ **Надежность**: Валидация данных, логирование, резервное копирование
- 🔌 **Интеграции**: REST API, базы данных (SQLite, PostgreSQL), ИИ-чат

## Установка

### Требования

- Python 3.9 или выше
- Windows 10/11, macOS 10.15+, или Linux

### Быстрая установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd shrinkage-calculator

# Создание виртуального окружения (рекомендуется)
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установка зависимостей
pip install -e .
```

### Установка с дополнительными зависимостями

```bash
# Для разработки
pip install -e ".[dev]"

# Для тестирования
pip install -e ".[test]"

# Для документации
pip install -e ".[docs]"
```

## Использование

### Запуск через графический интерфейс

```bash
# Запуск через меню выбора интерфейса
python launch.py

# Или напрямую через Flet GUI
python -m src.gui_complete

# Или через Tkinter GUI
python src/tkinter_gui.py

# Или через Streamlit дашборд
streamlit run src/dashboard.py
```

### Запуск через командную строку

```bash
# Обработка Excel файла
python -m src.cli process данные.xlsx

# Обработка с адаптивной моделью и излишком
python -m src.cli process данные.xlsx --adaptive --surplus 5.0

# Открыть отчет после генерации
python -m src.cli process данные.xlsx --open

# Просмотр текущих настроек
python -m src.cli settings --list

# Сброс настроек к значениям по умолчанию
python -m src.cli settings --reset
```

### Использование как библиотеки

```python
from src.core.shrinkage_system import ShrinkageSystem
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from src.core.improved_json_parser import parse_from_json

# Создание системы
system = ShrinkageSystem()

# Обработка данных
results = system.process_dataset(dataset, source_filename="данные.xlsx")
```

## Архитектура системы

```
shrinkage-calculator/
├── src/                    # Исходный код
│   ├── core/              # Ядро системы
│   ├── gui_complete.py    # Flet GUI
│   ├── tkinter_gui.py     # Tkinter GUI
│   ├── dashboard.py       # Streamlit дашборд
│   ├── cli.py             # Командная строка
│   ├── config.py          # Конфигурация
│   └── logger_config.py   # Настройки логирования
├── tests/                 # Тесты
├── документация/          # Документация
├── результаты/            # Результаты расчетов
├── backups/               # Резервные копии
├── logs/                  # Логи
└── examples/              # Примеры данных
```

## Система конфигурации

Система использует иерархическую конфигурацию с валидацией:

- **Профили**: default, development, testing, production
- **Категории**: расчеты, интерфейс, вывод, база данных, производительность
- **Валидация**: типы данных, диапазоны, допустимые значения

Подробнее в [документации по конфигурации](документация/configuration_system.md).

## Графические интерфейсы

### Flet GUI
Современный интерфейс с поддержкой тем и ИИ-чата.

### Tkinter GUI
Классический интерфейс с расширенными настройками.

### Streamlit Dashboard
Интерактивный веб-дашборд для анализа данных.

## API и интеграции

Система предоставляет REST API для интеграции с другими системами:

```python
# Запуск API сервера
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием кода
pytest --cov=src

# Запуск конкретных тестов
pytest tests/test_shrinkage_system.py
```

## Разработка

### Стиль кода

Проект следует стандартам PEP 8. Используйте black для форматирования:

```bash
black src/
```

### Предварительная фиксация

Настройте pre-commit hooks:

```bash
pre-commit install
```

## Документация

- [Бизнес-логика системы](BUSINESS_LOGIC.md)
- [Система конфигурации](документация/configuration_system.md)
- [Функция системных настроек](документация/system_settings_functionality.md)
- [Руководство пользователя](документация/user_guide.md)
- [API документация](документация/api.md)

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для подробностей.

## Контакты

Для вопросов и поддержки обращайтесь к разработчику системы.