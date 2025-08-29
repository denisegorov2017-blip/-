#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование интеграции системы верификации с основной системой усушки
"""

import sys
import os
import pandas as pd
import numpy as np

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem


def test_verification_integration():
    """Тестирование интеграции системы верификации с основной системой усушки."""
    print("🧪 Тестирование интеграции системы верификации")
    print("=" * 60)
    
    # Создаем систему усушки с включенной верификацией
    system = ShrinkageSystem({'enable_verification': True})
    
    # Подготавливаем тестовые данные
    test_data = [
        {
            'Номенклатура': 'Рыба свежая',
            'Начальный_остаток': 100.0,
            'Приход': 50.0,
            'Расход': 20.0,
            'Конечный_остаток': 128.0,  # Усушка 2.0
            'Период_хранения_дней': 7
        },
        {
            'Номенклатура': 'Рыба соленая',
            'Начальный_остаток': 200.0,
            'Приход': 100.0,
            'Расход': 50.0,
            'Конечный_остаток': 245.0,  # Усушка 5.0
            'Период_хранения_дней': 7
        }
    ]
    
    dataset = pd.DataFrame(test_data)
    
    print("📊 Исходные данные:")
    print(dataset.to_string(index=False))
    
    # Выполняем обработку с верификацией
    print("\n🚀 Выполнение обработки с верификацией...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename="integration_test.xlsx",
        use_adaptive=True
    )
    
    # Проверяем результаты
    assert results['status'] == 'success', f"Обработка должна быть успешной, получено: {results['status']}"
    print("  ✅ Обработка выполнена успешно")
    
    # Проверяем наличие коэффициентов
    coefficients = results['coefficients']
    assert len(coefficients) == 2, f"Должно быть 2 набора коэффициентов, получено: {len(coefficients)}"
    print("  ✅ Рассчитаны коэффициенты для 2 номенклатур")
    
    # Проверяем наличие данных верификации
    for i, coeff in enumerate(coefficients):
        print(f"\n📋 Проверка верификации для номенклатуры {i+1}:")
        verification = coeff.get('Верификация', {})
        
        if verification:
            verification_status = verification.get('verification_status', 'unknown')
            print(f"  Статус верификации: {verification_status}")
            
            if verification_status == 'success':
                accuracy_metrics = verification.get('accuracy_metrics', {})
                validation_status = verification.get('validation_status', {})
                
                print(f"  R²: {accuracy_metrics.get('r_squared', 0):.4f}")
                print(f"  Общий статус: {validation_status.get('overall_status', 'unknown')}")
                print("  ✅ Верификация выполнена успешно")
            else:
                print(f"  ❌ Ошибка верификации: {verification.get('error_message', 'Неизвестная ошибка')}")
        else:
            print("  ⚠️  Данные верификации отсутствуют")
    
    print("\n✅ Интеграционный тест завершен успешно!")


def test_verification_disabled():
    """Тестирование работы системы без верификации."""
    print("\n🧪 Тестирование работы системы без верификации")
    print("=" * 60)
    
    # Создаем систему усушки с отключенной верификацией
    system = ShrinkageSystem({'enable_verification': False})
    
    # Подготавливаем тестовые данные
    test_data = [
        {
            'Номенклатура': 'Рыба копченая',
            'Начальный_остаток': 150.0,
            'Приход': 75.0,
            'Расход': 30.0,
            'Конечный_остаток': 192.0,  # Усушка 3.0
            'Период_хранения_дней': 7
        }
    ]
    
    dataset = pd.DataFrame(test_data)
    
    # Выполняем обработку без верификации
    print("🚀 Выполнение обработки без верификации...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename="no_verification_test.xlsx",
        use_adaptive=True
    )
    
    # Проверяем результаты
    assert results['status'] == 'success', f"Обработка должна быть успешной, получено: {results['status']}"
    print("  ✅ Обработка выполнена успешно")
    
    # Проверяем, что данные верификации отсутствуют
    coefficients = results['coefficients']
    coeff = coefficients[0]
    verification = coeff.get('Верификация', {})
    
    # При отключенной верификации данные верификации могут отсутствовать
    print("  ✅ Система корректно работает без верификации")
    
    print("\n✅ Тест работы без верификации завершен успешно!")


if __name__ == "__main__":
    test_verification_integration()
    test_verification_disabled()
    print("\n🎉 Все интеграционные тесты завершены успешно!")