#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования расширенных аналитических функций базы данных.

Этот скрипт демонстрирует использование новых аналитических функций,
добавленных в систему базы данных для анализа коэффициентов усушки.
"""

import sys
import os
import inspect

# Получаем путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.join(current_dir, '..')
project_root = os.path.abspath(project_root)

# Добавляем путь к проекту
sys.path.insert(0, project_root)

from src.core.database.database import init_database, get_db_session
from src.core.database.services import get_database_service
from src.core.database.models import Nomenclature, Model, CalculationData, Coefficient, Analytics

def main():
    """Основная функция примера."""
    print("=== Пример использования расширенных аналитических функций ===\n")
    
    # 1. Инициализация базы данных
    print("1. Инициализация базы данных...")
    engine = init_database()
    Session = get_db_session()
    print("   База данных инициализирована успешно\n")
    
    # 2. Создание тестовых данных
    print("2. Создание тестовых данных...")
    session = Session()
    db_service = get_database_service(session)
    
    # Создаем тестовую номенклатуру
    nomenclature = db_service.create_nomenclature(
        name="СИНЕЦ ВЯЛЕНЫЙ",
        product_type="fish_dried"
    )
    nomenclature_id = nomenclature.id
    print(f"   Создана номенклатура: {nomenclature.name} (ID: {nomenclature_id})")
    
    # Создаем тестовую модель
    model = db_service.create_model(
        name="ShrinkageCalculator_exponential",
        model_type="exponential",
        version="1.0"
    )
    model_id = model.id
    print(f"   Создана модель: {model.name} (ID: {model_id})")
    
    # Создаем тестовые данные для расчетов с разными датами
    calculation_dates = [
        datetime.now() - timedelta(days=20),
        datetime.now() - timedelta(days=15),
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=5),
        datetime.now()
    ]
    
    calculation_data_ids = []
    coefficient_ids = []
    
    for i, calc_date in enumerate(calculation_dates):
        # Создаем расчетные данные
        calculation_data = db_service.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature_id,
            initial_balance=100.0 + i*10,
            incoming=20.0 + i*2,
            outgoing=30.0 + i*3,
            final_balance=90.0 + i*5,
            storage_days=7 + i,
            calculation_date=calc_date
        )
        calculation_data_ids.append(calculation_data.id)
        print(f"   Созданы расчетные данные (ID: {calculation_data.id})")
        
        # Создаем коэффициенты с улучшающейся точностью
        coefficient = db_service.create_coefficient(
            calculation_data_id=calculation_data.id,
            model_id=model_id,
            coefficient_a=0.01 + i*0.002,
            coefficient_b=0.02 + i*0.001,
            coefficient_c=0.001 + i*0.0002,
            accuracy_r2=0.80 + i*0.03,  # Улучшающаяся точность
            calculation_date=calc_date
        )
        coefficient_ids.append(coefficient.id)
        print(f"   Созданы коэффициенты (ID: {coefficient.id})")
    
    # Создаем аналитику
    analytics = db_service.create_analytics(
        nomenclature_id=nomenclature_id,
        model_id=model_id,
        avg_accuracy=0.86,  # Среднее из (0.80, 0.83, 0.86, 0.89, 0.92)
        total_calculations=5,
        period_start=datetime.now() - timedelta(days=30),
        period_end=datetime.now()
    )
    print(f"   Создана аналитика (ID: {analytics.id})")
    
    session.commit()
    session.close()
    print("   Тестовые данные созданы успешно\n")
    
    # 3. Использование расширенных аналитических функций
    print("3. Использование расширенных аналитических функций...")
    
    # 3.1. Анализ трендов по номенклатуре
    print("   3.1. Анализ трендов по номенклатуре...")
    session2 = Session()
    db_service2 = get_database_service(session2)
    
    trend_analysis = db_service2.get_nomenclature_trend_analysis(nomenclature_id, days=30)
    
    print(f"      Количество точек данных: {len(trend_analysis['trend_data'])}")
    print(f"      Средний коэффициент A: {trend_analysis['avg_coefficient_a']:.4f}")
    print(f"      Средний коэффициент B: {trend_analysis['avg_coefficient_b']:.4f}")
    print(f"      Средний коэффициент C: {trend_analysis['avg_coefficient_c']:.4f}")
    print(f"      Направление тренда точности: {trend_analysis['accuracy_trend']}")
    print(f"      Период анализа: {trend_analysis['analysis_period_days']} дней")
    
    # Выводим детализированные данные
    print("      Детализированные данные:")
    for i, data_point in enumerate(trend_analysis['trend_data']):
        print(f"        Точка {i+1}: Дата={data_point['date'].strftime('%Y-%m-%d')}, "
              f"Точность={data_point['accuracy']:.2f}, "
              f"A={data_point['coefficient_a']:.4f}, "
              f"B={data_point['coefficient_b']:.4f}, "
              f"C={data_point['coefficient_c']:.4f}")
    
    session2.close()
    print()
    
    # 3.2. Сравнительный анализ моделей
    print("   3.2. Сравнительный анализ моделей...")
    session3 = Session()
    db_service3 = get_database_service(session3)
    
    # Создаем еще одну модель для сравнения
    model2 = db_service3.create_model(
        name="ShrinkageCalculator_linear",
        model_type="linear",
        version="1.0"
    )
    model2_id = model2.id
    print(f"      Создана дополнительная модель: {model2.name} (ID: {model2_id})")
    
    # Создаем аналитику для второй модели с худшей точностью
    analytics2 = db_service3.create_analytics(
        nomenclature_id=nomenclature_id,
        model_id=model2_id,
        avg_accuracy=0.75,
        total_calculations=3
    )
    print(f"      Создана аналитика для второй модели (ID: {analytics2.id})")
    
    session3.commit()
    session3.close()
    
    # Выполняем сравнительный анализ
    session4 = Session()
    db_service4 = get_database_service(session4)
    
    model_comparison = db_service4.get_model_comparison_analysis()
    
    print(f"      Всего моделей: {model_comparison['total_models']}")
    print(f"      Лучшая модель: {model_comparison['best_model']['model_name']} "
          f"(Точность: {model_comparison['best_model']['avg_accuracy']:.2f})")
    
    print("      Сравнение всех моделей:")
    for i, model_data in enumerate(model_comparison['models']):
        print(f"        {i+1}. {model_data['model_name']} ({model_data['model_type']})")
        print(f"           Точность: {model_data['avg_accuracy']:.2f}")
        print(f"           Количество расчетов: {model_data['calculation_count']}")
        print(f"           Уникальных номенклатур: {model_data['unique_nomenclatures']}")
    
    session4.close()
    print()
    
    # 3.3. Отчет о производительности номенклатур
    print("   3.3. Отчет о производительности номенклатур...")
    session5 = Session()
    db_service5 = get_database_service(session5)
    
    # Создаем дополнительные номенклатуры для отчета
    nomenclature2 = db_service5.create_nomenclature(
        name="КЕФАЛЬ ВЯЛЕНАЯ",
        product_type="fish_dried"
    )
    nomenclature2_id = nomenclature2.id
    print(f"      Создана дополнительная номенклатура: {nomenclature2.name} (ID: {nomenclature2_id})")
    
    nomenclature3 = db_service5.create_nomenclature(
        name="СКУМБРИЯ ХК",
        product_type="fish_fresh"
    )
    nomenclature3_id = nomenclature3.id
    print(f"      Создана дополнительная номенклатура: {nomenclature3.name} (ID: {nomenclature3_id})")
    
    # Создаем дополнительные расчетные данные для новых номенклатур
    # Номенклатура 2 - 2 расчета
    for i in range(2):
        calc_data = db_service5.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature2_id,
            initial_balance=120.0 + i*5,
            incoming=25.0 + i*1,
            outgoing=35.0 + i*2,
            final_balance=110.0 + i*3,
            storage_days=5 + i
        )
        
        coeff = db_service5.create_coefficient(
            calculation_data_id=calc_data.id,
            model_id=model_id,
            coefficient_a=0.015 + i*0.001,
            coefficient_b=0.025 + i*0.001,
            coefficient_c=0.0015 + i*0.0001,
            accuracy_r2=0.85 + i*0.02
        )
    
    # Номенклатура 3 - 4 расчета
    for i in range(4):
        calc_data = db_service5.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature3_id,
            initial_balance=150.0 + i*8,
            incoming=30.0 + i*3,
            outgoing=40.0 + i*4,
            final_balance=140.0 + i*6,
            storage_days=8 + i
        )
        
        coeff = db_service5.create_coefficient(
            calculation_data_id=calc_data.id,
            model_id=model_id,
            coefficient_a=0.02 + i*0.001,
            coefficient_b=0.03 + i*0.001,
            coefficient_c=0.002 + i*0.0001,
            accuracy_r2=0.88 + i*0.01
        )
    
    # Создаем аналитику для новых номенклатур
    db_service5.create_analytics(
        nomenclature_id=nomenclature2_id,
        model_id=model_id,
        avg_accuracy=0.86,
        total_calculations=2
    )
    
    db_service5.create_analytics(
        nomenclature_id=nomenclature3_id,
        model_id=model_id,
        avg_accuracy=0.90,
        total_calculations=4
    )
    
    session5.commit()
    session5.close()
    
    # Генерируем отчет о производительности
    session6 = Session()
    db_service6 = get_database_service(session6)
    
    performance_report = db_service6.get_nomenclature_performance_report(limit=10)
    
    print(f"      Всего номенклатур в отчете: {performance_report['total_nomenclatures']}")
    print("      Топ номенклатур по количеству расчетов:")
    
    for i, item in enumerate(performance_report['top_performing']):
        print(f"        {i+1}. {item['nomenclature_name']}")
        print(f"           Количество расчетов: {item['calculation_count']}")
        print(f"           Средняя точность: {item['avg_accuracy']:.2f}")
        print(f"           Количество ошибок: {item['error_count']}")
    
    session6.close()
    print()
    
    # 4. Заключение
    print("4. Заключение")
    print("   Расширенные аналитические функции успешно продемонстрированы.")
    print("   Они предоставляют мощные возможности для анализа:")
    print("   - Трендов по номенклатурам")
    print("   - Сравнения эффективности моделей")
    print("   - Производительности номенклатур")
    print("\n=== Пример завершен успешно ===")

# Добавляем необходимые импорты в функцию main
def _add_imports():
    global datetime, timedelta
    from datetime import datetime, timedelta

if __name__ == "__main__":
    _add_imports()
    main()