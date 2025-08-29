#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования системы верификации точности коэффициентов усушки

Демонстрирует, как система проверяет точность рассчитанных коэффициентов 
путем обратного пересчета предварительной усушки по тем же коэффициентам.
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_verification_system import ShrinkageVerificationSystem
from core.shrinkage_system import ShrinkageSystem


def demonstrate_verification_process():
    """Демонстрирует процесс верификации коэффициентов усушки."""
    print("🔍 ДЕМОНСТРАЦИЯ СИСТЕМЫ ВЕРИФИКАЦИИ КОЭФФИЦИЕНТОВ УСУШКИ")
    print("=" * 60)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Создаем основную систему расчета коэффициентов
    shrinkage_system = ShrinkageSystem()
    
    # Подготавливаем тестовые данные (имитация данных инвентаризации)
    test_data = [
        {
            'Номенклатура': 'Рыба свежая, охлажденная',
            'Начальный_остаток': 1000.0,
            'Приход': 500.0,
            'Расход': 300.0,
            'Конечный_остаток': 1195.0,  # Усушка 5.0 кг
            'Период_хранения_дней': 7
        },
        {
            'Номенклатура': 'Рыба соленая',
            'Начальный_остаток': 800.0,
            'Приход': 400.0,
            'Расход': 200.0,
            'Конечный_остаток': 992.0,  # Усушка 8.0 кг
            'Период_хранения_дней': 7
        },
        {
            'Номенклатура': 'Рыба горячего копчения',
            'Начальный_остаток': 600.0,
            'Приход': 300.0,
            'Расход': 150.0,
            'Конечный_остаток': 735.0,  # Усушка 15.0 кг
            'Период_хранения_дней': 7
        }
    ]
    
    # Преобразуем в DataFrame
    dataset = pd.DataFrame(test_data)
    print("📊 Исходные данные для расчета коэффициентов:")
    print(dataset.to_string(index=False))
    
    # Рассчитываем коэффициенты с использованием основной системы
    print("\n🧮 Расчет коэффициентов усушки...")
    results = shrinkage_system.process_dataset(
        dataset=dataset,
        source_filename="demo_data.xlsx",
        use_adaptive=True
    )
    
    # Проверяем успешность расчета
    if results['status'] != 'success':
        print(f"❌ Ошибка расчета коэффициентов: {results.get('message', 'Неизвестная ошибка')}")
        return
    
    print("✅ Коэффициенты рассчитаны успешно!")
    
    # Выполняем верификацию для каждой номенклатуры
    print("\n🔍 Верификация точности коэффициентов...")
    coefficients_results = results['coefficients']
    
    for i, (original_row, coeff_result) in enumerate(zip(test_data, coefficients_results)):
        print(f"\n📋 Верификация для: {original_row['Номенклатура']}")
        
        # Подготавливаем данные в формате, понятном системе верификации
        verification_data = {
            'name': original_row['Номенклатура'],
            'initial_balance': original_row['Начальный_остаток'],
            'incoming': original_row['Приход'],
            'outgoing': original_row['Расход'],
            'final_balance': original_row['Конечный_остаток'],
            'storage_days': original_row['Период_хранения_дней']
        }
        
        # Извлекаем коэффициенты
        coefficients = {
            'model_type': coeff_result.get('Модель', 'exponential'),
            'coefficients': {
                'a': coeff_result.get('Коэф_a', 0.015),
                'b': coeff_result.get('Коэф_b', 0.049),
                'c': coeff_result.get('Коэф_c', 0.001)
            },
            'r_squared': coeff_result.get('Точность_R2', 95) / 100.0  # Преобразуем из процентов
        }
        
        # Выполняем верификацию
        verification_results = verification_system.verify_coefficients_accuracy(
            verification_data, coefficients
        )
        
        # Генерируем и выводим отчет
        report = verification_system.generate_verification_report(verification_results)
        print(report)
        
        # Сохраняем отчет в файл
        report_filename = f"результаты/отчет_верификации_{i+1}.txt"
        os.makedirs("результаты", exist_ok=True)
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"💾 Отчет сохранен в файл: {report_filename}")


def demonstrate_manual_verification():
    """Демонстрирует ручную верификацию с заданными коэффициентами."""
    print("\n\n🔍 ДЕМОНСТРАЦИЯ РУЧНОЙ ВЕРИФИКАЦИИ")
    print("=" * 60)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Пример данных инвентаризации
    inventory_data = {
        'name': 'Рыба мороженая',
        'initial_balance': 1200.0,
        'incoming': 600.0,
        'outgoing': 400.0,
        'final_balance': 1390.0,  # Усушка 10.0 кг
        'storage_days': 14
    }
    
    # Заданные коэффициенты (например, полученные из предыдущих расчетов)
    calculated_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.008,  # Коэффициент усушки
            'b': 0.05,   # Скорость усушки
            'c': 0.0005  # Линейный компонент
        },
        'r_squared': 0.92
    }
    
    print("📊 Данные инвентаризации:")
    print(f"   Номенклатура: {inventory_data['name']}")
    print(f"   Начальный остаток: {inventory_data['initial_balance']} кг")
    print(f"   Приход: {inventory_data['incoming']} кг")
    print(f"   Расход: {inventory_data['outgoing']} кг")
    print(f"   Конечный остаток: {inventory_data['final_balance']} кг")
    print(f"   Период хранения: {inventory_data['storage_days']} дней")
    
    print("\n🧮 Заданные коэффициенты:")
    coeffs = calculated_coefficients['coefficients']
    print(f"   Модель: {calculated_coefficients['model_type']}")
    print(f"   Коэффициент a: {coeffs['a']}")
    print(f"   Коэффициент b: {coeffs['b']}")
    print(f"   Коэффициент c: {coeffs['c']}")
    print(f"   Точность (R²): {calculated_coefficients['r_squared']:.4f}")
    
    # Выполняем верификацию
    print("\n🔍 Выполнение верификации...")
    verification_results = verification_system.verify_coefficients_accuracy(
        inventory_data, calculated_coefficients
    )
    
    # Генерируем отчет
    report = verification_system.generate_verification_report(verification_results)
    print("\n" + report)
    
    # Анализируем результаты
    if verification_results['verification_status'] == 'success':
        metrics = verification_results['accuracy_metrics']
        validation = verification_results['validation_status']
        
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        print(f"   Фактическая усушка: {metrics['actual_shrinkage']:.4f} кг")
        print(f"   Прогнозируемая усушка: {metrics['predicted_shrinkage']:.4f} кг")
        print(f"   Разница: {metrics['absolute_difference']:.4f} кг")
        print(f"   Статус валидации: {validation['overall_status'].upper()}")
        print(f"   Рекомендация: {validation['recommendation']}")


if __name__ == "__main__":
    # Создаем папку для результатов если её нет
    os.makedirs("результаты", exist_ok=True)
    
    try:
        demonstrate_verification_process()
        demonstrate_manual_verification()
        print("\n🎉 Демонстрация системы верификации завершена успешно!")
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении демонстрации: {str(e)}")
        import traceback
        traceback.print_exc()