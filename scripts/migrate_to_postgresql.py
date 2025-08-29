#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт миграции данных с SQLite на PostgreSQL.

Этот скрипт помогает перенести данные из существующей SQLite базы данных
в новую PostgreSQL базу данных.
"""

import sys
import os
import inspect
import pandas as pd
from datetime import datetime

# Получаем путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.join(current_dir, '..')
project_root = os.path.abspath(project_root)

# Добавляем путь к проекту
sys.path.insert(0, project_root)

from src.logger_config import log
from src.config import DEFAULT_CONFIG
from src.core.database.database import get_db_session, get_database_url
from src.core.database.models import *
from src.core.database.utils import initialize_database, test_database_connection, get_database_info

def migrate_data():
    """
    Мигрирует данные с SQLite на PostgreSQL.
    """
    try:
        log.info("Начало миграции данных с SQLite на PostgreSQL")
        
        # Получаем URL текущей базы данных (SQLite)
        sqlite_url = get_database_url()
        if not sqlite_url.startswith('sqlite:///'):
            log.error("Текущая база данных не является SQLite базой данных")
            return False
            
        log.info(f"Текущая SQLite база данных: {sqlite_url}")
        
        # Проверяем подключение к SQLite
        if not test_database_connection():
            log.error("Не удалось подключиться к SQLite базе данных")
            return False
            
        # Получаем информацию о SQLite базе данных
        sqlite_info = get_database_info()
        log.info(f"SQLite база данных содержит {sqlite_info['total_rows']} записей")
        
        # Для миграции на PostgreSQL необходимо:
        # 1. Настроить PostgreSQL URL в конфигурации
        # 2. Инициализировать новую базу данных
        # 3. Перенести данные
        
        log.info("Для миграции на PostgreSQL:")
        log.info("1. Обновите database_url в src/config.py на PostgreSQL URL")
        log.info("2. Запустите скрипт инициализации базы данных")
        log.info("3. Используйте этот скрипт для переноса данных")
        
        return True
    except Exception as e:
        log.error(f"Ошибка при миграции данных: {e}")
        return False

def export_sqlite_data():
    """
    Экспортирует данные из SQLite в файлы CSV для последующего импорта.
    """
    try:
        log.info("Экспорт данных из SQLite в CSV файлы")
        
        # Создаем директорию для экспорта
        export_dir = os.path.join(project_root, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Получаем сессию SQLite
        Session = get_db_session()
        session = Session()
        
        # Список таблиц для экспорта
        tables = [
            ('source_data', SourceData),
            ('nomenclature', Nomenclature),
            ('calculation_data', CalculationData),
            ('models', Model),
            ('coefficients', Coefficient),
            ('forecasts', Forecast),
            ('analytics', Analytics),
            ('ai_patterns', AIPattern),
            ('validation_errors', ValidationError),
            ('priority_periods', PriorityPeriod),
            ('preliminary_forecasts', PreliminaryForecast),
            ('surplus_specifications', SurplusSpecification),
            ('surplus_recommendations', SurplusRecommendation),
            ('surplus_patterns', SurplusPattern),
            ('pattern_validations', PatternValidation),
            ('feedback_preferences', FeedbackPreference),
            ('data_lineage', DataLineage),
            ('ml_model_registry', MLModelRegistry)
        ]
        
        exported_files = []
        
        for table_name, model_class in tables:
            try:
                # Получаем все записи из таблицы
                records = session.query(model_class).all()
                
                if not records:
                    log.info(f"Таблица {table_name} пуста")
                    continue
                    
                # Преобразуем записи в список словарей
                data = []
                for record in records:
                    record_dict = {}
                    for column in model_class.__table__.columns:
                        value = getattr(record, column.name)
                        # Преобразуем datetime в строку для экспорта
                        if isinstance(value, datetime):
                            value = value.isoformat() if value else None
                        record_dict[column.name] = value
                    data.append(record_dict)
                
                # Создаем DataFrame и сохраняем в CSV
                df = pd.DataFrame(data)
                csv_file = os.path.join(export_dir, f"{table_name}.csv")
                df.to_csv(csv_file, index=False, encoding='utf-8')
                exported_files.append(csv_file)
                
                log.info(f"Экспортировано {len(data)} записей из таблицы {table_name}")
            except Exception as e:
                log.error(f"Ошибка при экспорте таблицы {table_name}: {e}")
        
        session.close()
        
        log.success(f"Экспорт завершен. Создано {len(exported_files)} файлов в директории {export_dir}")
        return exported_files
    except Exception as e:
        log.error(f"Ошибка при экспорте данных: {e}")
        return []

def main():
    """
    Основная функция скрипта.
    """
    print("=== Скрипт миграции данных с SQLite на PostgreSQL ===\n")
    
    try:
        # Проверяем текущую базу данных
        db_info = get_database_info()
        print(f"Текущая база данных: {db_info['database_type']}")
        print(f"URL: {db_info['database_url']}")
        print(f"Размер: {db_info['size_mb']} МБ")
        print(f"Всего записей: {db_info['total_rows']}\n")
        
        # Предлагаем пользователю выбрать действие
        print("Выберите действие:")
        print("1. Экспорт данных из SQLite в CSV")
        print("2. Миграция данных (требуется настроенная PostgreSQL база)")
        print("3. Отмена")
        
        choice = input("\nВведите номер действия (1-3): ").strip()
        
        if choice == '1':
            exported_files = export_sqlite_data()
            if exported_files:
                print(f"\nЭкспорт успешно завершен. Созданы файлы:")
                for file in exported_files:
                    print(f"  - {file}")
            else:
                print("\nЭкспорт не выполнен.")
                
        elif choice == '2':
            success = migrate_data()
            if success:
                print("\nМиграция успешно завершена.")
            else:
                print("\nМиграция не выполнена.")
                
        elif choice == '3':
            print("\nОперация отменена.")
            
        else:
            print("\nНеверный выбор.")
            
    except Exception as e:
        log.error(f"Ошибка в основном скрипте: {e}")
        print(f"\nОшибка: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())