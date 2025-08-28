#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленное тестирование для рефакторинговой системы ShrinkageSystem.

Этот тест проверяет основной публичный метод `process_dataset` и соответствует
новой архитектуре, где ShrinkageSystem является оркестратором.
"""

import sys
import os
import pandas as pd

# Импортируем ShrinkageSystem из нового расположения
from src.core.shrinkage_system import ShrinkageSystem

def test_refactored_shrinkage_system():
    """Тестирование обновленной системы через публичный метод process_dataset."""
    print("🧪 Тестирование рефакторинговой системы ShrinkageSystem")
    print("=" * 60)
    
    # 1. Создаем систему. Конфигурация будет загружена по умолчанию.
    system = ShrinkageSystem()
    
    # 2. Устанавливаем процент излишка (5%) для адаптивной модели
    surplus_rate = 0.05
    system.set_surplus_rate(surplus_rate)
    print(f"📊 Установлен глобальный процент излишка: {surplus_rate*100:.1f}%")
    
    # 3. Готовим тестовые данные
    # Приход 50, с излишком 5% это 50 * 1.05 = 52.5
    # Баланс = 100 (нач) + 52.5 (приход с излишком) - 20 (расход) = 132.5
    # Усушка = 132.5 - 128 (конечный) = 4.5
    test_data = [
        {
            'Номенклатура': 'Тестовый продукт',
            'Начальный_остаток': 100.0,
            'Приход': 50.0,
            'Расход': 20.0,
            'Конечный_остаток': 128.0,
            'Период_хранения_дней': 7
        }
    ]
    dataset = pd.DataFrame(test_data)
    
    print("\n📊 Входные данные для теста:")
    print(dataset.to_string())
    
    # 4. Вызываем главный публичный метод системы
    print("\n🚀 Запуск system.process_dataset(...) с адаптивной моделью...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename="test_run.xlsx",
        use_adaptive=True
    )
    
    # 5. Проверяем результаты с помощью assert
    print("\n🔍 Проверка результатов...")
    
    assert results is not None, "Результат не должен быть None"
    print("  ✅ Результат получен.")
    
    assert results['status'] == 'success', f"Статус должен быть 'success', а не '{results['status']}'"
    print(f"  ✅ Статус: {results['status']}")
    
    assert 'coefficients' in results and len(results['coefficients']) == 1, "Должен быть 1 результат расчета коэффициентов"
    print("  ✅ Найден 1 набор коэффициентов.")
    
    result = results['coefficients'][0]
    accuracy = result.get('Точность', 0)
    
    # В данной задаче модель должна идеально сойтись
    assert accuracy > 99.0, f"Точность должна быть > 99%, а она {accuracy:.1f}%"
    print(f"  ✅ Точность расчета: {accuracy:.1f}% (пройдено)")
    
    assert result.get('Учет_излишка') == f"{surplus_rate*100:.1f}%", "В результате должен быть указан правильный процент излишка"
    print(f"  ✅ Учет излишка: {result.get('Учет_излишка')}")

    print("\n🎉 Тест обновленной системы завершен успешно!")