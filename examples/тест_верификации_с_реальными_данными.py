#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест системы верификации с реальными данными из файла
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_verification_system import ShrinkageVerificationSystem


def test_verification_with_real_data():
    """Тест системы верификации с реальными данными."""
    print("🔍 Тест системы верификации с реальными данными")
    print("=" * 60)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Пример реальных данных из файла
    test_cases = [
        {
            'name': 'ВЯЛЕНАЯ РЫБА (весовой товар)',
            'initial_balance': 31.950,
            'incoming': 33.078,
            'outgoing': 22.000,
            'final_balance': 43.028,
            'storage_days': 7
        },
        {
            'name': 'ВОБЛА АСТРАХАНЬ вяленая',
            'initial_balance': 5.020,
            'incoming': 10.000,
            'outgoing': 9.734,
            'final_balance': 5.286,
            'storage_days': 7
        },
        {
            'name': 'КАМБАЛА ВЯЛ БЕЗ ИКРЫ',
            'initial_balance': 2.478,
            'incoming': 2.240,
            'outgoing': 1.402,
            'final_balance': 3.316,
            'storage_days': 7
        }
    ]
    
    # Тестовые коэффициенты (реалистичные значения)
    test_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.015,  # 1.5% максимальная усушка
            'b': 0.049,  # Скорость достижения максимума
            'c': 0.001   # Линейный компонент
        },
        'r_squared': 0.95  # Высокая точность
    }
    
    print("📊 Тестовые данные:")
    for i, case in enumerate(test_cases):
        theoretical_balance = case['initial_balance'] + case['incoming'] - case['outgoing']
        actual_shrinkage = theoretical_balance - case['final_balance']
        print(f"   {i+1}. {case['name'][:30]:30} | Усушка: {actual_shrinkage:8.3f} кг")
    
    print(f"\n🧮 Тестовые коэффициенты:")
    coeffs = test_coefficients['coefficients']
    print(f"   Модель: {test_coefficients['model_type']}")
    print(f"   a = {coeffs['a']:.4f}, b = {coeffs['b']:.4f}, c = {coeffs['c']:.4f}")
    print(f"   R² = {test_coefficients['r_squared']:.4f}")
    
    # Выполняем верификацию для каждого тестового случая
    print(f"\n🔍 Результаты верификации:")
    for i, case in enumerate(test_cases):
        print(f"\n   Тест {i+1}: {case['name'][:30]}")
        
        # Выполняем верификацию
        results = verification_system.verify_coefficients_accuracy(case, test_coefficients)
        
        if results['verification_status'] == 'success':
            # Выводим метрики точности
            metrics = results['accuracy_metrics']
            validation = results['validation_status']
            
            print(f"     Прогнозируемая усушка: {metrics['predicted_shrinkage']:8.3f} кг")
            print(f"     Фактическая усушка:   {metrics['actual_shrinkage']:8.3f} кг")
            print(f"     Разница:              {metrics['difference']:8.3f} кг")
            print(f"     R²:                   {metrics['r_squared']:8.4f}")
            print(f"     Статус:               {validation['overall_status'].upper()}")
        else:
            print(f"     Ошибка верификации: {results.get('error_message', 'Неизвестная ошибка')}")
    
    # Генерируем отчет для первого теста
    print(f"\n📄 Пример отчета верификации:")
    results = verification_system.verify_coefficients_accuracy(test_cases[0], test_coefficients)
    report = verification_system.generate_verification_report(results)
    print(report)


if __name__ == "__main__":
    test_verification_with_real_data()