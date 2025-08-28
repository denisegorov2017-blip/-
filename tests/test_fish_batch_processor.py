#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для специализированного процессора данных о партиях рыбы.
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.specialized_fish_data_processor import FishBatchDataProcessor


def test_fish_batch_processor():
    """Тест специализированного процессора данных о партиях рыбы."""
    print("🧪 Тест специализированного процессора данных о партиях рыбы")
    print("=" * 70)
    
    # Создаем процессор
    processor = FishBatchDataProcessor()
    
    # Путь к тестовому файлу
    test_file = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    # Проверяем наличие файла
    if not os.path.exists(test_file):
        print(f"❌ Тестовый файл не найден: {test_file}")
        return False
    
    print(f"📂 Тестовый файл: {test_file}")
    
    try:
        # Тестируем обработку Excel файла
        print("\n1️⃣  Тест обработки Excel файла...")
        df_result = processor.process_fish_batch_excel(test_file)
        
        if not df_result.empty:
            print(f"✅ Обработка завершена успешно")
            print(f"📊 Извлечено записей: {len(df_result)}")
            print(f"📋 Столбцы: {list(df_result.columns)}")
            print(f"\n샘 Первые 3 записи:")
            print(df_result.head(3))
        else:
            print("❌ Результат обработки пуст")
            return False
        
        # Тестируем полный расчет усушки
        print("\n2️⃣  Тест полного расчета усушки...")
        results = processor.calculate_shrinkage_for_batches(test_file, use_adaptive=True)
        
        if results['status'] == 'success':
            print(f"✅ Расчет усушки выполнен успешно")
            print(f"📊 Обработано записей: {len(results['coefficients'])}")
            print(f"📈 Средняя точность: {results['summary']['avg_accuracy']:.2f}%")
            
            # Сохраняем результаты в подпапку для тестовых данных
            test_results_dir = os.path.join('результаты', 'тестовые_данные')
            os.makedirs(test_results_dir, exist_ok=True)
            test_results_file = os.path.join(test_results_dir, 'fish_batch_test_results.json')
            
            with open(test_results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Результаты сохранены в {test_results_file}")
            
            # Показываем примеры
            print(f"\n📋 Примеры коэффициентов (первые 3):")
            for i, coeff in enumerate(results['coefficients'][:3]):
                print(f"   {coeff['Номенклатура']}:")
                print(f"     a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}")
                print(f"     Точность: {coeff['Точность']:.2f}%")
        else:
            print(f"❌ Ошибка расчета усушки: {results['message']}")
            return False
        
        # Тестируем с базовой моделью
        print("\n3️⃣  Тест расчета усушки с базовой моделью...")
        results_basic = processor.calculate_shrinkage_for_batches(test_file, use_adaptive=False)
        
        if results_basic['status'] == 'success':
            print(f"✅ Расчет усушки с базовой моделью выполнен успешно")
            print(f"📊 Обработано записей: {len(results_basic['coefficients'])}")
            print(f"📈 Средняя точность: {results_basic['summary']['avg_accuracy']:.2f}%")
        else:
            print(f"❌ Ошибка расчета усушки с базовой моделью: {results_basic['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_validation():
    """Тест валидации данных."""
    print("\n🧪 Тест валидации данных")
    print("=" * 70)
    
    processor = FishBatchDataProcessor()
    
    # Тестовые данные
    test_cases = [
        ("отчет о продажах", True),  # Документ
        ("накладная 001", True),      # Документ
        ("21.07.2025", True),        # Дата
        ("15.07.2025 14:30:00", True), # Дата и время
        ("Монетка рыба", False),     # Продукт
        ("ВЯЛЕНАЯ РЫБА", False),     # Продукт
    ]
    
    print("🔍 Тест идентификации типов строк:")
    all_passed = True
    
    for i, (text_val, expected) in enumerate(test_cases):
        is_document = processor._is_document_row(text_val)
        is_date = processor._is_date_row(text_val)
        is_product = processor._is_product_row(text_val)
        
        # Для документов и дат ожидаем True, для продуктов False
        actual = is_document or is_date
        status = "✅" if actual == expected else "❌"
        
        print(f"   {status} '{text_val}': документ={is_document}, дата={is_date}, продукт={is_product}")
        
        if actual != expected:
            all_passed = False
    
    return all_passed


def main():
    """Основная функция тестирования."""
    print("🚀 ТЕСТИРОВАНИЕ СПЕЦИАЛИЗИРОВАННОГО ПРОЦЕССОРА ДАННЫХ О ПАРТИЯХ РЫБЫ")
    print("=" * 80)
    
    # Тест валидации данных
    validation_success = test_data_validation()
    
    # Основной тест
    processing_success = test_fish_batch_processor()
    
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    
    if validation_success and processing_success:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("   ✅ Валидация данных работает корректно")
        print("   ✅ Обработка Excel файлов работает корректно")
        print("   ✅ Расчет усушки выполняется успешно")
        print("   ✅ Обе модели (адаптивная и базовая) работают")
        print("\n📋 РЕКОМЕНДАЦИИ:")
        print("   • Система готова к работе с реальными данными о партиях рыбы")
        print("   • Все компоненты функционируют корректно")
        print("   • Результаты сохранены в директории 'результаты/тестовые_данные'")
        return True
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        if not validation_success:
            print("   • Проблемы с валидацией данных")
        if not processing_success:
            print("   • Проблемы с обработкой данных или расчетом усушки")
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        print("   • Проверьте логи для выявления конкретных ошибок")
        print("   • Убедитесь, что тестовый файл имеет правильную структуру")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)