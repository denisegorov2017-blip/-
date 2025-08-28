#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования системы расчета коэффициентов усушки с различными типами продукции
Сохраняет результаты с сохранением иерархии, как в исходных данных
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к папке src, чтобы можно было импортировать модули проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel

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
    
    # Подготавливаем иерархическую структуру данных
    hierarchical_data = {
        "source_file": "пример_типов_продукции.xlsx",
        "calculation_date": datetime.now().strftime("%Y-%m-%d"),
        "storage_period_days": 7,
        "product_types": {},
        "results": {}
    }
    
    print("📊 Прогнозы усушки для 100 кг продукции за 7 дней хранения:")
    print("-" * 70)
    
    # Группируем результаты по типам продукции
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
        
        # Добавляем информацию о типе продукции в иерархию
        if product_type not in hierarchical_data["product_types"]:
            hierarchical_data["product_types"][product_type] = {
                "description": product_type_desc,
                "coefficients": {
                    "a_multiplier": product_coeffs['a_multiplier'],
                    "b_multiplier": product_coeffs['b_multiplier'],
                    "c_multiplier": product_coeffs['c_multiplier']
                },
                "base_coefficients": {
                    "a": model.base_coefficients['a'],
                    "b": model.base_coefficients['b'],
                    "c": model.base_coefficients['c']
                },
                "adapted_coefficients": {
                    "a": adapted_a,
                    "b": adapted_b,
                    "c": adapted_c
                }
            }
        
        # Добавляем результаты в иерархию
        if product_type not in hierarchical_data["results"]:
            hierarchical_data["results"][product_type] = []
            
        hierarchical_data["results"][product_type].append({
            "nomenclature": nomenclature,
            "initial_weight": initial_weight,
            "forecast_shrinkage": forecast,
            "shrinkage_percentage": shrinkage_percentage
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
    
    # Сохраняем результаты в JSON файл с иерархической структурой
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../результаты'))
    os.makedirs(results_dir, exist_ok=True)
    
    json_path = os.path.join(results_dir, "пример_типов_продукции_иерархия.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(hierarchical_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в файл: {json_path}")
    
    # Также создаем упрощенную таблицу результатов
    summary_data = {
        "source_file": "пример_типов_продукции.xlsx",
        "calculation_date": datetime.now().strftime("%Y-%m-%d"),
        "storage_period_days": 7,
        "summary": []
    }
    
    for nomenclature, initial_weight, product_type_desc in product_examples:
        product_type = model.determine_product_type(nomenclature)
        forecast = model.predict_with_adaptation(7, nomenclature=nomenclature)
        shrinkage_percentage = (forecast / initial_weight) * 100
        
        summary_data["summary"].append({
            "Номенклатура": nomenclature,
            "Тип продукции": product_type,
            "Описание": product_type_desc,
            "Начальный вес (кг)": initial_weight,
            "Прогноз усушки (кг)": round(forecast, 3),
            "Процент усушки (%)": round(shrinkage_percentage, 2)
        })
    
    summary_json_path = os.path.join(results_dir, "пример_типов_продукции_сводка.json")
    
    with open(summary_json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Сводные результаты сохранены в файл: {summary_json_path}")

if __name__ == "__main__":
    main()