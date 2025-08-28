#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование пер-номенклатурного учета излишка
"""

import sys
import os



from src.core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel
from src.core.shrinkage_system import ShrinkageSystem

def test_nomenclature_surplus_direct():
    """Тестирование пер-номенклатурного учета излишка напрямую через модель"""
    print("Тестирование пер-номенклатурного учета излишка напрямую через модель")
    print("=" * 60)
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Устанавливаем разные проценты излишка для разных номенклатур
    model.set_surplus_rate(0.05, "СКУМБРИЯ ХК")  # 5% излишка для скумбрии
    model.set_surplus_rate(0.10, "СЕЛЬДЬ ХК")    # 10% излишка для сельди
    model.set_surplus_rate(0.03, "ОКУНЬ ХК")     # 3% излишка для окуня
    
    print("Установлены проценты излишка:")
    print(f"  СКУМБРИЯ ХК: {model.get_surplus_rate('СКУМБРИЯ ХК')*100:.1f}%")
    print(f"  СЕЛЬДЬ ХК: {model.get_surplus_rate('СЕЛЬДЬ ХК')*100:.1f}%")
    print(f"  ОКУНЬ ХК: {model.get_surplus_rate('ОКУНЬ ХК')*100:.1f}%")
    print(f"  По умолчанию: {model.get_surplus_rate()*100:.1f}%")
    
    # Данные для разных номенклатур
    mackerel_data = {
        'initial_balance': 100.0,
        'incoming': 0,
        'outgoing': 0,
        'final_balance': 99.75,  # С учетом 5% излишка и усушки
        'storage_days': 7
    }
    
    herring_data = {
        'initial_balance': 100.0,
        'incoming': 0,
        'outgoing': 0,
        'final_balance': 99.50,  # С учетом 10% излишка и усушки
        'storage_days': 7
    }
    
    perch_data = {
        'initial_balance': 100.0,
        'incoming': 0,
        'outgoing': 0,
        'final_balance': 99.85,  # С учетом 3% излишка и усушки
        'storage_days': 7
    }
    
    # Адаптируем коэффициенты для каждой номенклатуры
    mackerel_coeff = model.adapt_coefficients(mackerel_data, nomenclature="СКУМБРИЯ ХК")
    herring_coeff = model.adapt_coefficients(herring_data, nomenclature="СЕЛЬДЬ ХК")
    perch_coeff = model.adapt_coefficients(perch_data, nomenclature="ОКУНЬ ХК")
    
    # Прогнозы с учетом излишка
    mackerel_forecast = model.predict_with_adaptation(7, initial_balance=100.0, nomenclature="СКУМБРИЯ ХК")
    herring_forecast = model.predict_with_adaptation(7, initial_balance=100.0, nomenclature="СЕЛЬДЬ ХК")
    perch_forecast = model.predict_with_adaptation(7, initial_balance=100.0, nomenclature="ОКУНЬ ХК")
    default_forecast = model.predict_with_adaptation(7, initial_balance=100.0)  # Без указания номенклатуры
    
    print("\nРезультаты адаптации коэффициентов:")
    print(f"  СКУМБРИЯ ХК: a={mackerel_coeff['a']:.3f}, b={mackerel_coeff['b']:.3f}, c={mackerel_coeff['c']:.3f}")
    print(f"  СЕЛЬДЬ ХК: a={herring_coeff['a']:.3f}, b={herring_coeff['b']:.3f}, c={herring_coeff['c']:.3f}")
    print(f"  ОКУНЬ ХК: a={perch_coeff['a']:.3f}, b={perch_coeff['b']:.3f}, c={perch_coeff['c']:.3f}")
    
    print("\nПрогнозы усушки:")
    print(f"  СКУМБРИЯ ХК: {mackerel_forecast:.3f} кг")
    print(f"  СЕЛЬДЬ ХК: {herring_forecast:.3f} кг")
    print(f"  ОКУНЬ ХК: {perch_forecast:.3f} кг")
    print(f"  По умолчанию: {default_forecast:.3f} кг")
    
    # Проверяем, что излишки разные
    assert model.get_surplus_rate("СКУМБРИЯ ХК") == 0.05, "Неверный излишек для скумбрии"
    assert model.get_surplus_rate("СЕЛЬДЬ ХК") == 0.10, "Неверный излишек для сельди"
    assert model.get_surplus_rate("ОКУНЬ ХК") == 0.03, "Неверный излишек для окуня"
    assert model.get_surplus_rate() == 0.0, "Неверный излишек по умолчанию"
    
    print("\n✅ Тест пер-номенклатурного учета излишка напрямую через модель пройден успешно!")
    

def test_nomenclature_surplus_system():
    """Тестирование пер-номенклатурного учета излишка через систему"""
    print("\n\nТестирование пер-номенклатурного учета излишка через систему")
    print("=" * 60)
    
    # Создаем систему
    system = ShrinkageSystem()
    
    # Устанавливаем разные проценты излишка для разных номенклатур
    system.set_surplus_rate(0.05, "СКУМБРИЯ ХК")  # 5% излишка для скумбрии
    system.set_surplus_rate(0.10, "СЕЛЬДЬ ХК")    # 10% излишка для сельди
    
    print("Установлены проценты излишка в системе:")
    print(f"  СКУМБРИЯ ХК: {system.get_surplus_rate('СКУМБРИЯ ХК')*100:.1f}%")
    print(f"  СЕЛЬДЬ ХК: {system.get_surplus_rate('СЕЛЬДЬ ХК')*100:.1f}%")
    print(f"  По умолчанию: {system.get_surplus_rate()*100:.1f}%")
    
    print("\n✅ Тест пер-номенклатурного учета излишка через систему пройден успешно!")
    

