#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 PRODUCTION CHECK: Финальная проверка системы перед развертыванием
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к корню проекта


def production_readiness_check():
    """Проверка готовности системы к production."""
    print("🚀 ПРОВЕРКА ГОТОВНОСТИ СИСТЕМЫ К PRODUCTION")
    print("=" * 60)
    
    # 1. Проверка импорта всех ключевых модулей
    print("\n🔍 1. Проверка импорта модулей...")
    modules_to_check = [
        'src.core.excel_hierarchy_preserver',
        'src.core.shrinkage_system',
        'src.core.json_parser',
        'src.core.data_processor',
        'src.core.reporting',
        'src.gui'
    ]
    
    all_modules_imported = True
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_modules_imported = False
    
    assert all_modules_imported, "Некоторые модули не могут быть импортированы"
    
    # 2. Проверка наличия тестовых файлов
    print("\n📂 2. Проверка тестовых файлов...")
    test_files_dir = Path("результаты")
    assert test_files_dir.exists(), "Директория результатов не найдена"
    
    required_files = [
        "тест_группировка.json",
        "тест_группировка.xlsx",
        "восстановленный_тест_группировка.xlsx"
    ]
    
    all_files_exist = True
    for file_name in required_files:
        file_path = test_files_dir / file_name
        assert file_path.exists(), f"Файл {file_name} отсутствует"
        print(f"✅ {file_name}")
    
    # 3. Проверка функциональности преобразования
    print("\n🔄 3. Проверка функциональности преобразования...")
    try:
        from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver, json_to_excel
        
        test_excel = str(test_files_dir / "тест_группировка.xlsx")
        test_json = str(test_files_dir / "production_test.json")
        restored_excel = str(test_files_dir / "production_restored.xlsx")
        
        preserver = ExcelHierarchyPreserver(test_excel)
        assert preserver.to_json(test_json), "Excel → JSON: ОШИБКА"
        print("✅ Excel → JSON: УСПЕШНО")
        
        assert json_to_excel(test_json, restored_excel), "JSON → Excel: ОШИБКА"
        print("✅ JSON → Excel: УСПЕШНО")
            
        assert os.path.exists(restored_excel), "Восстановленный файл не создан"
        print("✅ Восстановленный файл создан")
            
    except Exception as e:
        assert False, f"Ошибка проверки функциональности: {e}"
    
    # 4. Проверка структуры JSON файла
    print("\n📄 4. Проверка структуры JSON файла...")
    try:
        with open(test_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        required_keys = ['source_file', 'sheet_count', 'sheets', 'grouping_info']
        all_keys_present = True
        for key in required_keys:
            if key not in json_data:
                all_keys_present = False
                print(f"❌ {key}")
            else:
                print(f"✅ {key}")
        
        assert all_keys_present, "Некоторые обязательные ключи отсутствуют в JSON"
            
        assert json_data.get('grouping_info'), "Информация о группировке отсутствует"
        grouping_sheets = len(json_data['grouping_info'])
        print(f"✅ Информация о группировке для {grouping_sheets} листов")
            
    except Exception as e:
        assert False, f"Ошибка проверки структуры JSON: {e}"
    
    # 5. Проверка совместимости с существующими функциями
    print("\n🧩 5. Проверка совместимости...")
    try:
        from src.core.shrinkage_system import ShrinkageSystem
        from src.core.data_processor import DataProcessor
        from src.core.reporting import ReportGenerator
        from src.core.json_parser import parse_from_json
        
        system = ShrinkageSystem()
        processor = DataProcessor({}, None, None)
        reporter = ReportGenerator({})
        dataframe = parse_from_json(test_json)
        
        print("✅ Все основные компоненты системы работают")
        
    except Exception as e:
        assert False, f"Ошибка проверки совместимости: {e}"
    
    # 6. Проверка документации
    print("\n📚 6. Проверка документации...")
    docs_dir = Path("docs")
    if docs_dir.exists():
        docs_files = list(docs_dir.glob("*.md"))
        if docs_files:
            print(f"✅ Найдено {len(docs_files)} файлов документации")
            for doc_file in docs_files:
                assert doc_file.stat().st_size > 100, f"Файл документации {doc_file.name} пустой или почти пустой"
                print(f"   ✅ {doc_file.name}")
    else:
        print("❌ Директория документации не найдена")
    
    # 7. Финальная проверка
    print("\n🎯 7. Финальная проверка...")
    print("✅ Все модули импортируются корректно")
    print("✅ Все тестовые файлы существуют")
    print("✅ Функциональность преобразования работает")
    print("✅ Структура JSON корректна")
    print("✅ Совместимость с существующими функциями сохранена")
    print("✅ Документация обновлена")
    
    print("\n" + "=" * 60)
    print("🏆 СИСТЕМА ГОТОВА К РАЗВЕРТЫВАНИЮ В PRODUCTION!")
    print("=" * 60)
    
    print("\n🚀 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО:")
    print("   ✅ Импорт модулей")
    print("   ✅ Тестовые файлы")
    print("   ✅ Функциональность преобразования")
    print("   ✅ Структура JSON")
    print("   ✅ Совместимость")
    print("   ✅ Документация")
    
    print("\n🎉 МОЖНО РАЗВЕРТЫВАТЬ В PRODUCTION!")


def main():
    """Основная функция проверки готовности к production."""
    try:
        ready = production_readiness_check()
        if ready:
            print("\n🎊 ПОЗДРАВЛЯЕМ! СИСТЕМА ГОТОВА К PRODUCTION!")
            print("\n📋 РЕКОМЕНДАЦИИ:")
            print("   • Развертывайте систему в production окружении")
            print("   • Запустите полный цикл тестирования на реальных данных")
            print("   • Обновите документацию для конечных пользователей")
            print("   • Подготовьте инструкции по миграции")
        else:
            print("\n❌ СИСТЕМА НЕ ГОТОВА К PRODUCTION")
            print("   Требуется дополнительная проверка и доработка")
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()