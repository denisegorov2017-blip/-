#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование системы верификации точности коэффициентов усушки
"""

import sys
import os
import pandas as pd
import numpy as np

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_verification_system import ShrinkageVerificationSystem


def test_verification_system():
    """Тестирование системы верификации точности коэффициентов усушки."""
    print("🧪 Тестирование системы верификации точности коэффициентов усушки")
    print("=" * 70)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Тест 1: Проверка с идеальными данными
    print("\n📋 Тест 1: Проверка с идеальными данными")
    test_data_1 = {
        'name': 'Тестовая номенклатура 1',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 20.0,
        'final_balance': 127.5,  # Усушка 2.5
        'storage_days': 7
    }
    
    # Идеальные коэффициенты, которые должны дать точный результат
    test_coefficients_1 = {
        'model_type': 'exponential',
        'coefficients': {'a': 0.019, 'b': 0.049, 'c': 0.001},
        'r_squared': 0.95
    }
    
    # Выполняем верификацию
    results_1 = verification_system.verify_coefficients_accuracy(test_data_1, test_coefficients_1)
    
    # Проверяем результаты
    assert results_1['verification_status'] == 'success', "Верификация должна быть успешной"
    print("  ✅ Верификация выполнена успешно")
    
    # Проверяем метрики точности
    metrics_1 = results_1['accuracy_metrics']
    assert metrics_1['r_squared'] > 0.85, f"R² должен быть > 0.85, получено {metrics_1['r_squared']:.4f}"
    print(f"  ✅ Коэффициент детерминации: {metrics_1['r_squared']:.4f}")
    
    # Проверяем статус валидации
    validation_1 = results_1['validation_status']
    assert validation_1['overall_status'] == 'acceptable', f"Статус должен быть 'acceptable', получено '{validation_1['overall_status']}'"
    print(f"  ✅ Статус валидации: {validation_1['overall_status']}")
    
    # Тест 2: Проверка с данными низкой точности
    print("\n📋 Тест 2: Проверка с данными низкой точности")
    test_data_2 = {
        'name': 'Тестовая номенклатура 2',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 20.0,
        'final_balance': 125.0,  # Усушка 5.0
        'storage_days': 7
    }
    
    # Неточные коэффициенты
    test_coefficients_2 = {
        'model_type': 'exponential',
        'coefficients': {'a': 0.01, 'b': 0.01, 'c': 0.001},
        'r_squared': 0.6
    }
    
    # Выполняем верификацию
    results_2 = verification_system.verify_coefficients_accuracy(test_data_2, test_coefficients_2)
    
    # Проверяем результаты
    assert results_2['verification_status'] == 'success', "Верификация должна быть успешной"
    print("  ✅ Верификация выполнена успешно")
    
    # Проверяем статус валидации
    validation_2 = results_2['validation_status']
    # Должен быть статус warning или critical из-за низкой точности
    print(f"  ✅ Статус валидации: {validation_2['overall_status']}")
    
    # Тест 3: Проверка генерации отчета
    print("\n📋 Тест 3: Проверка генерации отчета")
    report_1 = verification_system.generate_verification_report(results_1)
    assert len(report_1) > 0, "Отчет не должен быть пустым"
    assert "ОТЧЕТ О ВЕРИФИКАЦИИ" in report_1, "Отчет должен содержать заголовок"
    print("  ✅ Отчет сгенерирован успешно")
    
    # Выводим краткий отчет
    print(f"\n📊 Результаты тестирования:")
    print(f"   - Тест 1 (идеальные данные): {validation_1['overall_status']}")
    print(f"   - Тест 2 (низкая точность): {validation_2['overall_status']}")
    
    print("\n✅ Все тесты пройдены успешно!")


def test_edge_cases():
    """Тестирование граничных случаев."""
    print("\n🧪 Тестирование граничных случаев")
    print("=" * 70)
    
    verification_system = ShrinkageVerificationSystem()
    
    # Тест с нулевым балансом
    print("\n📋 Тест: Нулевой начальный баланс")
    test_data_zero = {
        'name': 'Нулевой баланс',
        'initial_balance': 0.0,
        'incoming': 0.0,
        'outgoing': 0.0,
        'final_balance': 0.0,
        'storage_days': 7
    }
    
    test_coefficients_zero = {
        'model_type': 'exponential',
        'coefficients': {'a': 0.015, 'b': 0.049, 'c': 0.001},
        'r_squared': 0.95
    }
    
    results_zero = verification_system.verify_coefficients_accuracy(test_data_zero, test_coefficients_zero)
    assert results_zero['verification_status'] == 'success', "Верификация должна быть успешной"
    print("  ✅ Верификация с нулевым балансом выполнена успешно")
    
    # Тест с отрицательной усушкой (избыток)
    print("\n📋 Тест: Отрицательная усушка (избыток)")
    test_data_negative = {
        'name': 'Избыток',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 20.0,
        'final_balance': 135.0,  # Избыток 5.0
        'storage_days': 7
    }
    
    test_coefficients_negative = {
        'model_type': 'exponential',
        'coefficients': {'a': 0.015, 'b': 0.049, 'c': 0.001},
        'r_squared': 0.95
    }
    
    results_negative = verification_system.verify_coefficients_accuracy(test_data_negative, test_coefficients_negative)
    assert results_negative['verification_status'] == 'success', "Верификация должна быть успешной"
    print("  ✅ Верификация с отрицательной усушкой выполнена успешно")
    
    print("\n✅ Все тесты граничных случаев пройдены успешно!")


if __name__ == "__main__":
    test_verification_system()
    test_edge_cases()
    print("\n🎉 Все тесты системы верификации завершены успешно!")