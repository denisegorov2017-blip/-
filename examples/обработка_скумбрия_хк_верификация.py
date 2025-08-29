#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обработка данных по СКУМБРИЯ Х/К с верификацией коэффициентов усушки

Этот скрипт специально создан для обработки сложных данных инвентаризации
по номенклатуре "СКУМБРИЯ Х/К" с последующей верификацией точности 
рассчитанных коэффициентов.
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


def process_scomber_data_with_verification():
    """Обработка данных по СКУМБРИЯ Х/К с верификацией коэффициентов."""
    print("🔍 Обработка данных по СКУМБРИЯ Х/К с верификацией коэффициентов")
    print("=" * 70)
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Данные по СКУМБРИЯ Х/К из предоставленной информации
    # Начальный остаток: 11.412 кг
    # Приход: 9.070 кг
    # Расход: 14.504 кг
    # Конечный остаток: 5.978 кг
    # Период хранения: 6 дней (с 15.07.2025 по 21.07.2025)
    
    product_data = [{
        'Номенклатура': 'СКУМБРИЯ Х/К',
        'Начальный_остаток': 11.412,
        'Приход': 9.070,
        'Расход': 14.504,
        'Конечный_остаток': 5.978,
        'Период_хранения_дней': 6
    }]
    
    # Преобразуем в DataFrame
    dataset = pd.DataFrame(product_data)
    
    print("📊 Исходные данные:")
    print(f"   Номенклатура: СКУМБРИЯ Х/К")
    print(f"   Начальный остаток: 11.412 кг")
    print(f"   Приход: 9.070 кг")
    print(f"   Расход: 14.504 кг")
    print(f"   Конечный остаток: 5.978 кг")
    print(f"   Период хранения: 6 дней")
    
    # Рассчитываем фактическую усушку
    initial_balance = 11.412
    incoming = 9.070
    outgoing = 14.504
    final_balance = 5.978
    
    theoretical_balance = initial_balance + incoming - outgoing
    actual_shrinkage = theoretical_balance - final_balance
    
    print(f"\n🧮 Расчет фактической усушки:")
    print(f"   Теоретический баланс: {initial_balance} + {incoming} - {outgoing} = {theoretical_balance:.3f} кг")
    print(f"   Фактическая усушка: {theoretical_balance:.3f} - {final_balance} = {actual_shrinkage:.3f} кг")
    
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
    print(f"\n🔍 Результаты расчета коэффициентов:")
    
    if coefficients:
        coeff = coefficients[0]
        nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
        accuracy = coeff.get('Точность_R2', 0)
        model = coeff.get('Модель', 'Неизвестная')
        a_coeff = coeff.get('a', 0)
        b_coeff = coeff.get('b', 0)
        c_coeff = coeff.get('c', 0)
        
        print(f"   Номенклатура: {nomenclature}")
        print(f"   Модель: {model}")
        print(f"   Коэффициенты: a={a_coeff:.6f}, b={b_coeff:.6f}, c={c_coeff:.6f}")
        print(f"   Точность (R²): {accuracy:.2f}%")
        
        # Проверяем верификацию
        verification_data = coeff.get('Верификация', {})
        if verification_data:
            verification_status = verification_data.get('verification_status', 'unknown')
            if verification_status == 'success':
                metrics = verification_data.get('accuracy_metrics', {})
                validation = verification_data.get('validation_status', {})
                overall_status = validation.get('overall_status', 'unknown')
                
                print(f"\n🔍 Результаты верификации:")
                print(f"   Статус верификации: {verification_status.upper()}")
                print(f"   Общий статус: {overall_status.upper()}")
                print(f"   Прогнозируемая усушка: {metrics.get('predicted_shrinkage', 0):.3f} кг")
                print(f"   Фактическая усушка: {metrics.get('actual_shrinkage', 0):.3f} кг")
                print(f"   R² верификации: {metrics.get('r_squared', 0):.4f}")
                print(f"   Разница: {metrics.get('difference', 0):.4f} кг")
            else:
                print(f"   Статус верификации: {verification_status.upper()}")
                error_msg = verification_data.get('error_message', 'Неизвестная ошибка')
                print(f"   Ошибка: {error_msg}")
        else:
            print("   Верификация: НЕТ ДАННЫХ")
    else:
        print("❌ Не удалось рассчитать коэффициенты")
        return
    
    # Дополнительно выполняем прямую верификацию с помощью ShrinkageVerificationSystem
    print(f"\n🔍 Дополнительная верификация с помощью ShrinkageVerificationSystem...")
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Подготавливаем данные для верификации
    original_data = {
        'name': 'СКУМБРИЯ Х/К',
        'initial_balance': initial_balance,
        'incoming': incoming,
        'outgoing': outgoing,
        'final_balance': final_balance,
        'storage_days': 6
    }
    
    # Подготавливаем коэффициенты для верификации
    verification_coefficients = {
        'model_type': model,
        'coefficients': {
            'a': a_coeff,
            'b': b_coeff,
            'c': c_coeff
        },
        'r_squared': accuracy / 100.0  # Преобразуем процент в коэффициент
    }
    
    # Выполняем верификацию
    verification_results = verification_system.verify_coefficients_accuracy(
        original_data, verification_coefficients
    )
    
    if verification_results['verification_status'] == 'success':
        metrics = verification_results['accuracy_metrics']
        validation = verification_results['validation_status']
        
        print(f"📊 Результаты дополнительной верификации:")
        print(f"   Прогнозируемая усушка: {metrics['predicted_shrinkage']:.3f} кг")
        print(f"   Фактическая усушка: {metrics['actual_shrinkage']:.3f} кг")
        print(f"   Разница: {metrics['difference']:.4f} кг")
        print(f"   R² верификации: {metrics['r_squared']:.4f}")
        print(f"   Статус: {validation['overall_status'].upper()}")
        
        # Генерируем отчет
        report = verification_system.generate_verification_report(verification_results)
        print(f"\n📄 Отчет верификации:")
        print(report)
        
        # Сохраняем отчет
        output_dir = "результаты"
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, "верификация_СКУМБРИЯ_ХК_подробная.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n💾 Отчет верификации сохранен в: {report_file}")
    else:
        print(f"❌ Ошибка верификации: {verification_results.get('error_message', 'Неизвестная ошибка')}")
    
    # Сохраняем коэффициенты
    output_dir = "результаты"
    os.makedirs(output_dir, exist_ok=True)
    
    coefficients_file = os.path.join(output_dir, "коэффициенты_усушки_СКУМБРИЯ_ХК_с_верификацией.json")
    with open(coefficients_file, 'w', encoding='utf-8') as f:
        json.dump(coefficients, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
    
    print(f"\n🎉 Обработка данных по СКУМБРИЯ Х/К с верификацией завершена!")


if __name__ == "__main__":
    process_scomber_data_with_verification()