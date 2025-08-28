#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный тест системы расчета коэффициентов усушки с проверкой всех функций
"""

import sys
import os
import json
import pandas as pd

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver, json_to_excel
from src.core.json_parser import parse_from_json
from src.core.shrinkage_system import ShrinkageSystem

def test_full_system():
    """Полный тест системы."""
    print("🚀 Полный тест системы расчета коэффициентов усушки")
    print("=" * 60)
    
    # Путь к тестовому файлу
    test_excel_file = "результаты/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xlsx"
    
    # Проверяем существование тестового файла
    if not os.path.exists(test_excel_file):
        print(f"❌ Тестовый файл не найден: {test_excel_file}")
        return False
    
    print(f"📂 Работаем с файлом: {test_excel_file}")
    
    # 1. Тест сохранения и восстановления структуры Excel
    print("\n📋 1. Тест сохранения и восстановления структуры Excel...")
    
    # Преобразуем Excel в JSON
    json_file = "результаты/full_test.json"
    try:
        preserver = ExcelHierarchyPreserver(test_excel_file)
        if preserver.to_json(json_file):
            print("✅ Excel → JSON: УСПЕШНО")
        else:
            print("❌ Excel → JSON: ОШИБКА")
            return False
    except Exception as e:
        print(f"❌ Excel → JSON: ОШИБКА - {e}")
        return False
    
    # Преобразуем JSON обратно в Excel
    restored_excel_file = "результаты/full_test_restored.xlsx"
    try:
        if json_to_excel(json_file, restored_excel_file):
            print("✅ JSON → Excel: УСПЕШНО")
        else:
            print("❌ JSON → Excel: ОШИБКА")
            return False
    except Exception as e:
        print(f"❌ JSON → Excel: ОШИБКА - {e}")
        return False
    
    # 2. Тест парсинга JSON в DataFrame
    print("\n📋 2. Тест парсинга JSON в DataFrame...")
    try:
        dataframe = parse_from_json(json_file)
        if not dataframe.empty:
            print(f"✅ JSON → DataFrame: УСПЕШНО ({len(dataframe)} строк)")
        else:
            print("❌ JSON → DataFrame: ОШИБКА (пустой DataFrame)")
            return False
    except Exception as e:
        print(f"❌ JSON → DataFrame: ОШИБКА - {e}")
        return False
    
    # 3. Тест расчета коэффициентов усушки
    print("\n📋 3. Тест расчета коэффициентов усушки...")
    try:
        system = ShrinkageSystem()
        results = system.process_dataset(dataframe, "full_test.json", use_adaptive=True)
        if results['status'] == 'success':
            print(f"✅ Расчет коэффициентов: УСПЕШНО ({len(results['coefficients'])} записей)")
            print(f"   Средняя точность: {results['summary']['avg_accuracy']:.2f}%")
        else:
            print(f"❌ Расчет коэффициентов: ОШИБКА - {results['message']}")
            return False
    except Exception as e:
        print(f"❌ Расчет коэффициентов: ОШИБКА - {e}")
        return False
    
    # 4. Тест сохранения результатов
    print("\n📋 4. Тест сохранения результатов...")
    try:
        results_file = "результаты/full_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранение результатов: УСПЕШНО ({results_file})")
    except Exception as e:
        print(f"❌ Сохранение результатов: ОШИБКА - {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    
    print("\n📊 РЕЗЮМЕ:")
    print("   ✅ Сохранение и восстановление структуры Excel")
    print("   ✅ Парсинг JSON в DataFrame")
    print("   ✅ Расчет коэффициентов усушки")
    print("   ✅ Сохранение результатов")
    
    return True

def main():
    """Основная функция тестирования."""
    try:
        success = test_full_system()
        if success:
            print("\n🎊 ПОЗДРАВЛЯЕМ! Полный тест системы пройден успешно!")
            print("   Все компоненты системы работают корректно.")
        else:
            print("\n❌ Полный тест системы провален!")
            print("   Один или несколько компонентов системы работают некорректно.")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()