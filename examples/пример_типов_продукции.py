#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования системы расчета коэффициентов усушки с различными типами продукции
"""

import sys
import os
import pandas as pd

# Добавляем путь к папке src, чтобы можно было импортировать модули проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shrinkage_project.adaptive_shrinkage_calculator import AdaptiveShrinkageModel

def main():
    """Демонстрация работы системы с различными типами продукции."""
    print("🔬 Расчет коэффициентов усушки для различных типов рыбной продукции")
    print("=" * 70)
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Примеры номенклатур разных типов продукции
    product_examples = [
        ("ЩУКА СВЕЖАЯ", 100.0, "Свежая рыба"),
        ("СКУМБРИЯ С/С", 100.0, "Слабосоленая рыба"),
        ("СЕЛЬДЬ Х/К", 100.0, "Холодное копчение"),
        ("ОКУНЬ Г/К", 100.0, "Горячее копчение"),
        ("ТРЕСКА КОПЧЕНАЯ", 100.0, "Копченая рыба"),
        ("СУДАК СУШЕНАЯ", 100.0, "Сушеная/вяленая рыба")
    ]
    
    # Результаты
    results = []
    
    print("📊 Прогнозы усушки для 100 кг продукции за 7 дней хранения:")
    print("-" * 70)
    
    for nomenclature, initial_weight, product_type_desc in product_examples:
        # Определяем тип продукции
        product_type = model.determine_product_type(nomenclature)
        
        # Прогнозируем усушку
        forecast = model.predict_with_adaptation(7, nomenclature=nomenclature)
        
        # Рассчитываем процент усушки
        shrinkage_percentage = (forecast / initial_weight) * 100
        
        print(f"{nomenclature:20} ({product_type_desc:15}) -> {forecast:.3f} кг ({shrinkage_percentage:.2f}%)")
        
        # Получаем коэффициенты для конкретного типа продукции
        product_coeffs = model.product_coefficients[product_type]
        adapted_a = model.base_coefficients['a'] * product_coeffs['a_multiplier']
        adapted_b = model.base_coefficients['b'] * product_coeffs['b_multiplier']
        adapted_c = model.base_coefficients['c'] * product_coeffs['c_multiplier']
        
        # Сохраняем результаты для CSV
        results.append({
            "Номенклатура": nomenclature,
            "Тип продукции": product_type,
            "a": adapted_a,
            "b": adapted_b,
            "c": adapted_c,
            "Прогноз усушки": forecast
        })
    
    print("\n" + "=" * 70)
    print("📋 Важное замечание:")
    print("   Указанные диапазоны усушки являются РЕКОМЕНДУЕМЫМИ значениями.")
    print("   Модель может выходить за эти пределы в зависимости от:")
    print("   - Условий хранения (температура, влажность)")
    print("   - Сезонных факторов")
    print("   - Качества исходного сырья")
    print("   - Технологии обработки")
    print("   - Длительности хранения")
    
    # Сохраняем результаты в CSV файл
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../результаты'))
    os.makedirs(results_dir, exist_ok=True)
    
    df = pd.DataFrame(results)
    csv_path = os.path.join(results_dir, "пример_типов_продукции.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 Результаты сохранены в файл: {csv_path}")

if __name__ == "__main__":
    main()