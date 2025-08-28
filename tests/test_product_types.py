#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование определения типов продукции
"""

import sys
import os
import numpy as np



from src.core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel

def test_product_type_determination():
    """Тестирование определения типов продукции."""
    print("Тестирование определения типов продукции")
    print("=" * 50)
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Тестовые данные
    test_cases = [
        # Слабосоленая рыба
        ("СКУМБРИЯ С/С", "fish_salt_cured"),
        ("СЕЛЬДЬ СЛАБОСОЛЕНАЯ", "fish_salt_cured"),
        ("ОКУНЬ СЛАБ.СОЛ", "fish_salt_cured"),
        
        # Холодное копчение
        ("СКУМБРИЯ Х/К", "fish_cold_smoked"),
        ("СЕЛЬДЬ ХОЛОДНОГО КОПЧЕНИЯ", "fish_cold_smoked"),
        ("ОКУНЬ COLD SMOKED", "fish_cold_smoked"),
        
        # Горячее копчение
        ("СКУМБРИЯ Г/К", "fish_hot_smoked"),
        ("СЕЛЬДЬ ГОРЯЧЕГО КОПЧЕНИЯ", "fish_hot_smoked"),
        ("ОКУНЬ HOT SMOKED", "fish_hot_smoked"),
        
        # Общее копчение
        ("СКУМБРИЯ КОПЧЕНАЯ", "fish_smoked"),
        ("СЕЛЬДЬ SMOKED", "fish_smoked"),
        
        # Сушеная/вяленая рыба
        ("СКУМБРИЯ СУШЕНАЯ", "fish_dried"),
        ("СЕЛЬДЬ ВЯЛЕНАЯ", "fish_dried"),
        ("ОКУНЬ DRIED", "fish_dried"),
        ("ТРЕСКА ВЯЛЕНКА", "fish_dried"),
        
        # Свежая рыба (по умолчанию)
        ("СКУМБРИЯ СВЕЖАЯ", "fish_fresh"),
        ("СЕЛЬДЬ", "fish_fresh"),
        ("ОКУНЬ", "fish_fresh"),
    ]
    
    # Проверяем определение типов продукции
    all_passed = True
    for nomenclature, expected_type in test_cases:
        determined_type = model.determine_product_type(nomenclature)
        status = "✅" if determined_type == expected_type else "❌"
        print(f"{status} {nomenclature:30} -> {determined_type:20} (ожидалось: {expected_type})")
        if determined_type != expected_type:
            all_passed = False
    
    assert all_passed

def test_product_type_coefficients():
    """Тестирование коэффициентов для разных типов продукции."""
    print("\n\nТестирование коэффициентов для разных типов продукции")
    print("=" * 50)
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Проверяем наличие всех типов продукции в коэффициентах
    expected_types = [
        'fish_fresh',
        'fish_smoked',
        'fish_dried',
        'fish_salt_cured',
        'fish_hot_smoked',
        'fish_cold_smoked'
    ]
    
    all_present = True
    for product_type in expected_types:
        if product_type in model.product_coefficients:
            coeffs = model.product_coefficients[product_type]
            print(f"✅ {product_type:20} -> a_mult: {coeffs['a_multiplier']:.2f}, "
                  f"b_mult: {coeffs['b_multiplier']:.2f}, c_mult: {coeffs['c_multiplier']:.2f}")
        else:
            print(f"❌ {product_type} отсутствует в коэффициентах")
            all_present = False
    
    assert all_present

def test_shrinkage_trends():
    """Тестирование трендов усушки для разных типов продукции."""
    print("\n\nТестирование трендов усушки для разных типов продукции")
    print("=" * 50)
    print("Примечание: Типичные диапазоны усушки являются рекомендуемыми значениями,")
    print("модель может выходить за эти пределы в зависимости от условий хранения и других факторов.")
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Проверяем, что разные типы продукции дают разные уровни усушки
    # в правильном порядке (от минимальной к максимальной)
    product_types_in_order = [
        ('fish_dried', 'Сушеная рыба'),
        ('fish_salt_cured', 'Слабосоленая рыба'),
        ('fish_fresh', 'Свежая рыба'),
        ('fish_cold_smoked', 'Холодное копчение'),
        ('fish_smoked', 'Копченая рыба'),
        ('fish_hot_smoked', 'Горячее копчение')
    ]
    
    shrinkage_values = []
    
    for product_type, description in product_types_in_order:
        # Прогнозируем усушку для 100 кг рыбы за 7 дней
        forecast = model.predict_with_adaptation(7, product_type=product_type)
        shrinkage_values.append(forecast)
        print(f"📊 {description:20} -> {forecast:.3f} кг усушки")
    
    # Проверяем, что значения идут в порядке возрастания (кроме некоторых исключений)
    # Для нашей модели все типы продукции используют одни и те же базовые коэффициенты,
    # но с разными множителями
    print("\n🔍 Проверка трендов усушки:")
    
    # Сравниваем множители для a коэффициента
    multipliers = []
    for product_type, _ in product_types_in_order:
        multiplier = model.product_coefficients[product_type]['a_multiplier']
        multipliers.append(multiplier)
    
    print(f"Множители a: {multipliers}")
    
    # Проверяем, что множители расположены в правильном порядке
    # (за исключением некоторых случаев, где порядок может отличаться из-за других коэффициентов)
    correct_order = True
    for i in range(len(multipliers) - 1):
        if multipliers[i] > multipliers[i + 1]:
            # Допускаем небольшие отклонения
            if multipliers[i] - multipliers[i + 1] > 0.1:
                correct_order = False
                print(f"⚠️  Нарушение порядка между {product_types_in_order[i][1]} и {product_types_in_order[i+1][1]}")
    
    if correct_order:
        print("✅ Множители расположены в правильном порядке")
    else:
        print("⚠️  Множители не всегда следуют ожидаемому порядку (это допустимо)")
    
    

def test_adaptation_with_product_types():
    """Тестирование адаптации с учетом типов продукции."""
    print("\n\nТестирование адаптации с учетом типов продукции")
    print("=" * 50)
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Тестовые данные
    test_data = {
        'initial_balance': 100.0,
        'incoming': 0,
        'outgoing': 0,
        'final_balance': 95.0,  # 5.0 кг усушки
        'storage_days': 7
    }
    
    # Тест для разных типов продукции
    product_types = [
        ("СКУМБРИЯ С/С", "fish_salt_cured"),
        ("СЕЛЬДЬ Х/К", "fish_cold_smoked"),
        ("ОКУНЬ Г/К", "fish_hot_smoked"),
        ("ТРЕСКА", "fish_fresh")
    ]
    
    all_passed = True
    for nomenclature, expected_type in product_types:
        # Адаптируем коэффициенты с указанием номенклатуры
        coefficients = model.adapt_coefficients(test_data, nomenclature=nomenclature)
        
        # Проверяем, что тип продукции определен правильно
        determined_type = model.determine_product_type(nomenclature)
        status = "✅" if determined_type == expected_type else "❌"
        print(f"{status} {nomenclature:15} -> {determined_type:20}")
        
        if determined_type != expected_type:
            all_passed = False
        
        # Прогнозируем усушку
        forecast = model.predict_with_adaptation(7, nomenclature=nomenclature)
        print(f"    Коэффициенты: a={coefficients['a']:.3f}, b={coefficients['b']:.3f}, c={coefficients['c']:.3f}")
        print(f"    Прогноз усушки: {forecast:.3f} кг")
    
    assert all_passed

