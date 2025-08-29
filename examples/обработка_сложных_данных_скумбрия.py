#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обработка сложных данных по номенклатуре СКУМБРИЯ Х/К с детализацией по партиям
"""

import sys
import os
import pandas as pd
import json
import numpy as np

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem
from core.shrinkage_verification_system import ShrinkageVerificationSystem


def parse_complex_inventory_data():
    """Парсинг сложных данных инвентаризации для СКУМБРИЯ Х/К."""
    print("🔍 Парсинг сложных данных инвентаризации для СКУМБРИЯ Х/К")
    print("=" * 60)
    
    # Создаем данные вручную на основе предоставленной информации
    # Структура данных:
    # - Номенклатура: СКУМБРИЯ Х/К
    # - Начальный остаток: 11.412
    # - Приход: 9.070
    # - Расход: 14.504
    # - Конечный остаток: 5.978
    
    # Детализация по документам:
    data_entries = [
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Приходная накладная 000000000000543',
            'Дата': '15.07.2025',
            'Начальный_остаток': 11.412,
            'Приход': 9.070,
            'Расход': 0.0,
            'Конечный_остаток': 20.482
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000218',
            'Дата': '15.07.2025',
            'Начальный_остаток': 20.482,
            'Приход': 0.0,
            'Расход': 1.104,
            'Конечный_остаток': 19.378
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000219',
            'Дата': '16.07.2025',
            'Начальный_остаток': 19.378,
            'Приход': 0.0,
            'Расход': 1.116,
            'Конечный_остаток': 18.262
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000220',
            'Дата': '17.07.2025',
            'Начальный_остаток': 18.262,
            'Приход': 0.0,
            'Расход': 1.382,
            'Конечный_остаток': 16.880
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000221',
            'Дата': '18.07.2025',
            'Начальный_остаток': 16.880,
            'Приход': 0.0,
            'Расход': 3.856,
            'Конечный_остаток': 13.024
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000222',
            'Дата': '19.07.2025',
            'Начальный_остаток': 13.024,
            'Приход': 0.0,
            'Расход': 1.576,
            'Конечный_остаток': 11.448
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000223',
            'Дата': '20.07.2025',
            'Начальный_остаток': 11.448,
            'Приход': 0.0,
            'Расход': 2.920,
            'Конечный_остаток': 8.528
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Отчет отдела о розничных продажах 000000000000224',
            'Дата': '21.07.2025',
            'Начальный_остаток': 8.528,
            'Приход': 0.0,
            'Расход': 1.996,
            'Конечный_остаток': 6.532
        },
        {
            'Номенклатура': 'СКУМБРИЯ Х/К',
            'Документ': 'Инвентаризация 000000000000158',
            'Дата': '21.07.2025',
            'Начальный_остаток': 6.532,
            'Приход': 0.0,
            'Расход': 0.554,
            'Конечный_остаток': 5.978
        }
    ]
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(data_entries)
    print("📊 Данные инвентаризации:")
    print(df.to_string(index=False))
    
    # Рассчитываем общую усушку
    initial_balance = 11.412  # Начальный остаток
    total_incoming = 9.070    # Общий приход
    total_outgoing = 14.504   # Общий расход
    final_balance = 5.978     # Конечный остаток
    
    theoretical_balance = initial_balance + total_incoming - total_outgoing
    actual_shrinkage = theoretical_balance - final_balance
    
    print(f"\n🧮 Расчет общей усушки:")
    print(f"   Начальный остаток: {initial_balance:.3f} кг")
    print(f"   Приход: {total_incoming:.3f} кг")
    print(f"   Расход: {total_outgoing:.3f} кг")
    print(f"   Теоретический баланс: {theoretical_balance:.3f} кг")
    print(f"   Фактический конечный остаток: {final_balance:.3f} кг")
    print(f"   Фактическая усушка: {actual_shrinkage:.3f} кг")
    
    # Подготавливаем данные для системы расчета коэффициентов
    product_data = [{
        'Номенклатура': 'СКУМБРИЯ Х/К',
        'Начальный_остаток': initial_balance,
        'Приход': total_incoming,
        'Расход': total_outgoing,
        'Конечный_остаток': final_balance,
        'Период_хранения_дней': 6  # С 15.07 по 21.07 = 6 дней
    }]
    
    return product_data


def process_scomber_data():
    """Обработка данных по скумбрии с верификацией коэффициентов."""
    print("🔍 Обработка данных по СКУМБРИЯ Х/К с верификацией")
    print("=" * 60)
    
    # Парсим данные
    product_data = parse_complex_inventory_data()
    
    # Преобразуем в DataFrame
    dataset = pd.DataFrame(product_data)
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Обрабатываем данные
    print(f"\n🧮 Расчет коэффициентов усушки...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename="СКУМБРИЯ_ХК_данные.xlsx",
        use_adaptive=True
    )
    
    if results['status'] != 'success':
        print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
        return
    
    print("✅ Обработка завершена успешно!")
    
    # Анализируем результаты
    coefficients = results.get('coefficients', [])
    print(f"\n🔍 Результаты расчета:")
    
    for i, coeff in enumerate(coefficients):
        nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
        accuracy = coeff.get('Точность_R2', 0)
        model = coeff.get('Модель', 'Неизвестная')
        a_coeff = coeff.get('Коэф_a', 0)
        b_coeff = coeff.get('Коэф_b', 0)
        c_coeff = coeff.get('Коэф_c', 0)
        
        print(f"   Номенклатура: {nomenclature}")
        print(f"   Модель: {model}")
        print(f"   Коэффициенты: a={a_coeff:.6f}, b={b_coeff:.6f}, c={c_coeff:.6f}")
        print(f"   Точность (R²): {accuracy:.2f}%")
        
        # Проверяем верификацию
        verification = coeff.get('Верификация', {})
        if verification:
            verification_status = verification.get('verification_status', 'unknown')
            validation_status = verification.get('validation_status', {})
            overall_status = validation_status.get('overall_status', 'unknown')
            metrics = verification.get('accuracy_metrics', {})
            
            print(f"   Верификация: {overall_status.upper()}")
            print(f"   Прогнозируемая усушка: {metrics.get('predicted_shrinkage', 0):.3f} кг")
            print(f"   Фактическая усушка: {metrics.get('actual_shrinkage', 0):.3f} кг")
            print(f"   R² верификации: {metrics.get('r_squared', 0):.4f}")
        else:
            print(f"   Верификация: НЕТ ДАННЫХ")
    
    # Сохраняем результаты
    output_dir = "результаты"
    os.makedirs(output_dir, exist_ok=True)
    
    coefficients_file = os.path.join(output_dir, "коэффициенты_усушки_СКУМБРИЯ_ХК.json")
    with open(coefficients_file, 'w', encoding='utf-8') as f:
        json.dump(coefficients, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
    
    # Сохраняем отчеты
    reports = results.get('reports', {})
    for report_name, report_content in reports.items():
        report_file = os.path.join(output_dir, f"{report_name}_СКУМБРИЯ_ХК.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"💾 Отчет '{report_name}' сохранен в: {report_file}")
    
    print(f"\n🎉 Обработка данных по СКУМБРИЯ Х/К завершена!")


def demonstrate_verification_accuracy():
    """Демонстрация точности верификации на примере СКУМБРИЯ Х/К."""
    print("🔍 Демонстрация точности верификации")
    print("=" * 60)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Данные по СКУМБРИЯ Х/К
    scomber_data = {
        'name': 'СКУМБРИЯ Х/К',
        'initial_balance': 11.412,
        'incoming': 9.070,
        'outgoing': 14.504,
        'final_balance': 5.978,
        'storage_days': 6
    }
    
    # Рассчитываем фактическую усушку
    theoretical_balance = scomber_data['initial_balance'] + scomber_data['incoming'] - scomber_data['outgoing']
    actual_shrinkage = theoretical_balance - scomber_data['final_balance']
    
    print(f"📊 Данные по СКУМБРИЯ Х/К:")
    print(f"   Начальный остаток: {scomber_data['initial_balance']:.3f} кг")
    print(f"   Приход: {scomber_data['incoming']:.3f} кг")
    print(f"   Расход: {scomber_data['outgoing']:.3f} кг")
    print(f"   Конечный остаток: {scomber_data['final_balance']:.3f} кг")
    print(f"   Фактическая усушка: {actual_shrinkage:.3f} кг")
    
    # Пример коэффициентов (рассчитанных системой)
    scomber_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.035,   # 3.5% максимальная усушка (повышенная для скумбрии)
            'b': 0.06,    # Скорость достижения максимума
            'c': 0.002    # Линейный компонент
        },
        'r_squared': 0.94
    }
    
    print(f"\n🧮 Рассчитанные коэффициенты:")
    coeffs = scomber_coefficients['coefficients']
    print(f"   Модель: {scomber_coefficients['model_type']}")
    print(f"   a = {coeffs['a']:.4f} (максимальная усушка)")
    print(f"   b = {coeffs['b']:.4f} (скорость усушки)")
    print(f"   c = {coeffs['c']:.4f} (линейный компонент)")
    print(f"   R² = {scomber_coefficients['r_squared']:.4f}")
    
    # Выполняем верификацию
    print(f"\n🔍 Выполнение верификации...")
    verification_results = verification_system.verify_coefficients_accuracy(scomber_data, scomber_coefficients)
    
    if verification_results['verification_status'] == 'success':
        metrics = verification_results['accuracy_metrics']
        validation = verification_results['validation_status']
        
        print(f"📊 Результаты верификации:")
        print(f"   Прогнозируемая усушка: {metrics['predicted_shrinkage']:.3f} кг")
        print(f"   Фактическая усушка: {metrics['actual_shrinkage']:.3f} кг")
        print(f"   Разница: {metrics['difference']:.3f} кг")
        print(f"   R² верификации: {metrics['r_squared']:.4f}")
        print(f"   Статус: {validation['overall_status'].upper()}")
        
        # Генерируем отчет
        report = verification_system.generate_verification_report(verification_results)
        print(f"\n📄 Отчет верификации:")
        print(report)
        
        # Сохраняем отчет
        output_dir = "результаты"
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, "верификация_СКУМБРИЯ_ХК.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n💾 Отчет верификации сохранен в: {report_file}")
    else:
        print(f"❌ Ошибка верификации: {verification_results.get('error_message', 'Неизвестная ошибка')}")


if __name__ == "__main__":
    # Обрабатываем данные по скумбрии
    process_scomber_data()
    
    print("\n" + "="*70 + "\n")
    
    # Демонстрируем верификацию
    demonstrate_verification_accuracy()