#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования PostgreSQL с системой расчета коэффициентов усушки.

Этот скрипт демонстрирует основные возможности работы с PostgreSQL базой данных,
включая подключение, создание записей и выполнение аналитических запросов.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import inspect

# Получаем путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.join(current_dir, '..')
project_root = os.path.abspath(project_root)

# Добавляем путь к проекту
sys.path.insert(0, project_root)

# Импортируем модули напрямую
try:
    from src.logger_config import log
    from src.config import DEFAULT_CONFIG
    from src.core.database.database import init_database, get_db_session, get_database_url
    from src.core.database.services import get_database_service
    from src.core.database.integration import get_database_integration
    from src.core.database.utils import (
        initialize_database, test_database_connection, 
        get_database_info, vacuum_database
    )
    from src.core.database.timescaledb import (
        check_timescaledb_extension, create_hypertable, 
        optimize_with_timescaledb, get_timescaledb_info
    )
except ImportError:
    # Если импорт не работает, пробуем другой путь
    try:
        from logger_config import log
        from config import DEFAULT_CONFIG
        from core.database.database import init_database, get_db_session, get_database_url
        from core.database.services import get_database_service
        from core.database.integration import get_database_integration
        from core.database.utils import (
            initialize_database, test_database_connection, 
            get_database_info, vacuum_database
        )
        from core.database.timescaledb import (
            check_timescaledb_extension, create_hypertable, 
            optimize_with_timescaledb, get_timescaledb_info
        )
    except ImportError:
        # Последняя попытка
        sys.path.insert(0, os.path.join(project_root, 'src'))
        from logger_config import log
        from config import DEFAULT_CONFIG
        from core.database.database import init_database, get_db_session, get_database_url
        from core.database.services import get_database_service
        from core.database.integration import get_database_integration
        from core.database.utils import (
            initialize_database, test_database_connection, 
            get_database_info, vacuum_database
        )
        from core.database.timescaledb import (
            check_timescaledb_extension, create_hypertable, 
            optimize_with_timescaledb, get_timescaledb_info
        )

def main():
    """Основная функция примера."""
    print("=== Пример использования PostgreSQL с системой расчета коэффициентов усушки ===\n")
    
    try:
        # 1. Проверка подключения к базе данных
        print("1. Проверка подключения к базе данных...")
        db_url = get_database_url()
        print(f"   URL базы данных: {db_url}")
        
        if test_database_connection():
            print("   Подключение к базе данных успешно\n")
        else:
            print("   Не удалось подключиться к базе данных\n")
            return
        
        # 2. Получение информации о базе данных
        print("2. Получение информации о базе данных...")
        info = get_database_info()
        print(f"   Тип базы данных: {info['database_type']}")
        print(f"   Размер базы данных: {info['size_mb']} МБ")
        print(f"   Общее количество записей: {info['total_rows']}\n")
        
        # 3. Проверка TimescaleDB
        print("3. Проверка TimescaleDB...")
        timescaledb_available = check_timescaledb_extension()
        if timescaledb_available:
            print("   Расширение TimescaleDB доступно")
            timescaledb_info = get_timescaledb_info()
            if timescaledb_info.get('version'):
                print(f"   Версия TimescaleDB: {timescaledb_info['version']}")
                print(f"   Количество гипертаблиц: {timescaledb_info['hypertables_count']}")
        else:
            print("   Расширение TimescaleDB не доступно\n")
        
        # 4. Работа с данными через сервисный слой
        print("4. Работа с данными через сервисный слой...")
        Session = get_db_session()
        session = Session()
        db_service = get_database_service(session)
        
        # Создаем тестовую номенклатуру
        nomenclature = db_service.create_nomenclature(
            name="СИНЕЦ ВЯЛЕНЫЙ PostgreSQL",
            product_type="fish_dried"
        )
        nomenclature_id = nomenclature.id
        nomenclature_name = nomenclature.name
        print(f"   Создана номенклатура: {nomenclature_name} (ID: {nomenclature_id})")
        
        # Создаем тестовую модель
        model = db_service.create_model(
            name="ShrinkageCalculator_PostgreSQL",
            model_type="exponential",
            version="1.0"
        )
        model_id = model.id
        model_name = model.name
        print(f"   Создана модель: {model_name} (ID: {model_id})")
        
        # Создаем тестовые данные для расчета
        source_data = db_service.create_source_data(
            file_name="инвентаризация_postgresql.xlsx",
            file_path="исходные_данные/инвентаризация_postgresql.xlsx",
            upload_date=datetime.now(),
            processed=True,
            quality_score=0.95
        )
        source_data_id = source_data.id
        source_data_name = source_data.file_name
        print(f"   Создана запись об исходных данных: {source_data_name} (ID: {source_data_id})")
        
        # Создаем расчетные данные
        calculation_data = db_service.create_calculation_data(
            source_data_id=source_data_id,
            nomenclature_id=nomenclature_id,
            initial_balance=100.0,
            incoming=20.0,
            outgoing=30.0,
            final_balance=85.0,
            storage_days=7,
            calculation_date=datetime.now(),
            data_quality_flag='clean',
            inventory_confidence=0.9,
            inventory_period_start=datetime.now() - timedelta(days=7),
            inventory_period_end=datetime.now()
        )
        calculation_data_id = calculation_data.id
        print(f"   Созданы расчетные данные (ID: {calculation_data_id})")
        
        # Создаем коэффициенты
        coefficient = db_service.create_coefficient(
            calculation_data_id=calculation_data_id,
            model_id=model_id,
            coefficient_a=0.02,
            coefficient_b=0.049,
            coefficient_c=0.001,
            accuracy_r2=0.95,
            calculation_date=datetime.now()
        )
        coefficient_id = coefficient.id
        print(f"   Созданы коэффициенты (ID: {coefficient_id})")
        
        # Создаем прогноз
        forecast = db_service.create_forecast(
            coefficient_id=coefficient_id,
            forecast_value=1.5,
            actual_value=1.4,
            deviation=0.1,
            forecast_date=datetime.now()
        )
        forecast_id = forecast.id
        print(f"   Создан прогноз (ID: {forecast_id})")
        
        # Создаем аналитику
        analytics = db_service.create_analytics(
            nomenclature_id=nomenclature_id,
            model_id=model_id,
            avg_accuracy=0.92,
            total_calculations=10,
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now()
        )
        analytics_id = analytics.id
        print(f"   Создана аналитика (ID: {analytics_id})")
        
        # Создаем ошибку валидации
        validation_error = db_service.create_validation_error(
            calculation_data_id=calculation_data_id,
            error_type="validation_failure",
            description="Нулевой остаток в конце периода",
            severity_level="medium",
            detected_by="system",
            detection_date=datetime.now()
        )
        validation_error_id = validation_error.id
        print(f"   Создана ошибка валидации (ID: {validation_error_id})")
        
        session.commit()
        session.close()
        print("   Данные успешно сохранены в базу данных\n")
        
        # 5. Получение статистики по номенклатуре
        print("5. Получение статистики по номенклатуре...")
        # Открываем новую сессию для получения статистики
        session2 = Session()
        db_service2 = get_database_service(session2)
        stats = db_service2.get_nomenclature_statistics(nomenclature_id)
        session2.close()
        print(f"   Количество расчетов: {stats['calculation_count']}")
        print(f"   Средняя точность: {stats['avg_accuracy']:.2f}")
        print(f"   Количество ошибок: {stats['error_count']}\n")
        
        # 6. Получение статистики по модели
        print("6. Получение статистики по модели...")
        session3 = Session()
        db_service3 = get_database_service(session3)
        model_stats = db_service3.get_model_accuracy_statistics(model_id)
        session3.close()
        print(f"   Средняя точность модели: {model_stats['avg_accuracy']:.2f}")
        print(f"   Количество расчетов: {model_stats['calculation_count']}\n")
        
        # 7. Использование интеграции с базой данных
        print("7. Использование интеграции с базой данных...")
        integration = get_database_integration()
        
        # Загрузка исторических данных
        historical_data = integration.load_historical_data(nomenclature_name)
        print(f"   Загружено {len(historical_data)} исторических записей\n")
        
        # Получение исторических коэффициентов
        coefficients = integration.get_nomenclature_coefficients(nomenclature_name)
        print(f"   Загружено {len(coefficients)} исторических коэффициентов\n")
        
        # Получение статистики по номенклатуре через интеграцию
        nom_stats = integration.get_nomenclature_statistics(nomenclature_name)
        print(f"   Статистика по номенклатуре: {nom_stats}\n")
        
        # 8. Оптимизация с TimescaleDB (если доступно)
        if timescaledb_available:
            print("8. Оптимизация с TimescaleDB...")
            optimization_success = optimize_with_timescaledb()
            if optimization_success:
                print("   Оптимизация с TimescaleDB выполнена успешно")
                # Получаем обновленную информацию
                updated_timescaledb_info = get_timescaledb_info()
                print(f"   Количество гипертаблиц: {updated_timescaledb_info['hypertables_count']}")
            else:
                print("   Оптимизация с TimescaleDB не выполнена\n")
        else:
            print("8. TimescaleDB не доступен для оптимизации\n")
        
        # 9. Оптимизация базы данных
        print("9. Оптимизация базы данных...")
        vacuum_success = vacuum_database()
        if vacuum_success:
            print("   База данных успешно оптимизирована\n")
        else:
            print("   Оптимизация базы данных не выполнена\n")
        
        # 10. Финальная информация о базе данных
        print("10. Финальная информация о базе данных...")
        final_info = get_database_info()
        print(f"   Общее количество записей: {final_info['total_rows']}")
        print("   Таблицы:")
        for table_name, row_count in final_info['tables'].items():
            print(f"     {table_name}: {row_count} записей")
        print()
        
        print("=== Пример завершен успешно ===")
        
    except Exception as e:
        log.error(f"Ошибка в примере: {e}")
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())