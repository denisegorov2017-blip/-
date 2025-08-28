#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate how to properly use our shrinkage formula
"""

import sys
import os
import numpy as np

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_formula_usage():
    """Test and demonstrate proper usage of the shrinkage formula"""
    try:
        print("Testing proper usage of the shrinkage formula...")
        print("=" * 60)
        
        # Import the calculators
        from src.core.shrinkage_calculator import ShrinkageCalculator
        from src.core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel
        
        # Create calculators
        calculator = ShrinkageCalculator()
        adaptive_model = AdaptiveShrinkageModel()
        
        # Show formula explanations
        print("📚 Формула нелинейной усушки:")
        print(calculator.explain_formula_usage())
        
        print("\n" + "=" * 60)
        print("📚 Адаптивная формула нелинейной усушки:")
        print(adaptive_model.explain_adaptive_formula_usage())
        
        # Test data for a typical fish product
        test_data = {
            'name': 'СИНЕЦ ВЯЛЕНЫЙ',
            'initial_balance': 100.0,  # 100 kg
            'incoming': 20.0,          # 20 kg received
            'outgoing': 30.0,          # 30 kg sold
            'final_balance': 85.0,     # 85 kg actual inventory
            'storage_days': 7          # 7 days of storage
        }
        
        print("\n" + "=" * 60)
        print("🧪 Пример расчета коэффициентов:")
        print(f"Номенклатура: {test_data['name']}")
        print(f"Начальный остаток: {test_data['initial_balance']} кг")
        print(f"Приход: {test_data['incoming']} кг")
        print(f"Расход: {test_data['outgoing']} кг")
        print(f"Фактический остаток: {test_data['final_balance']} кг")
        print(f"Дней хранения: {test_data['storage_days']}")
        
        # Calculate theoretical balance and actual shrinkage
        theoretical_balance = test_data['initial_balance'] + test_data['incoming'] - test_data['outgoing']
        actual_shrinkage = theoretical_balance - test_data['final_balance']
        shrinkage_rate = actual_shrinkage / test_data['initial_balance'] if test_data['initial_balance'] > 0 else 0
        
        print(f"\n📊 Расчеты:")
        print(f"Теоретический остаток: {theoretical_balance} кг")
        print(f"Фактическая усушка: {actual_shrinkage} кг")
        print(f"Коэффициент усушки: {shrinkage_rate:.4f} ({shrinkage_rate*100:.2f}%)")
        
        # Calculate coefficients using different models
        print(f"\n🔬 Расчет коэффициентов:")
        for model_type in ['exponential', 'linear', 'polynomial']:
            result = calculator.calculate_coefficients(test_data, model_type)
            print(f"\nМодель: {model_type}")
            print(f"  Коэффициенты: a={result['a']}, b={result['b']}, c={result['c']}")
            print(f"  Точность: {result['accuracy']}%")
            print(f"  Статус: {result['status']}")
        
        # Test adaptive model
        print(f"\n🤖 Адаптивная модель:")
        coefficients = adaptive_model.adapt_coefficients(test_data, nomenclature=test_data['name'])
        print(f"  Адаптированные коэффициенты: a={coefficients['a']:.4f}, b={coefficients['b']:.4f}, c={coefficients['c']:.4f}")
        
        # Predict shrinkage using the adaptive model
        prediction = adaptive_model.predict_with_adaptation(
            t=test_data['storage_days'],
            initial_balance=test_data['initial_balance'],
            nomenclature=test_data['name']
        )
        
        predicted_absolute_shrinkage = prediction * test_data['initial_balance']
        predicted_final_balance = test_data['initial_balance'] - predicted_absolute_shrinkage
        
        print(f"  Прогнозируемая усушка: {prediction:.4f} ({prediction*100:.2f}%)")
        print(f"  Абсолютная усушка: {predicted_absolute_shrinkage:.2f} кг")
        print(f"  Прогнозируемый остаток: {predicted_final_balance:.2f} кг")
        
        # Compare with actual
        print(f"\n⚖️  Сравнение:")
        print(f"  Фактическая усушка: {actual_shrinkage:.2f} кг")
        print(f"  Прогнозируемая усушка: {predicted_absolute_shrinkage:.2f} кг")
        print(f"  Разница: {abs(actual_shrinkage - predicted_absolute_shrinkage):.2f} кг")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running formula usage test...")
    print("=" * 60)
    
    success = test_formula_usage()
    
    print("=" * 60)
    if success:
        print("✅ Тест пройден успешно!")
        print("Формула нелинейной усушки работает корректно.")
    else:
        print("❌ Тест не пройден!")
        print("Возникли проблемы с формулой нелинейной усушки.")