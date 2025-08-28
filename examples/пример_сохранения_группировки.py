#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования новой функциональности сохранения группировки Excel файлов

Этот пример демонстрирует:
1. Создание Excel файла с группировкой
2. Преобразование в JSON с сохранением группировки
3. Восстановление из JSON в Excel с восстановлением группировки
"""

import sys
import os
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver, json_to_excel

def main():
    """Основная функция примера."""
    print("🔬 Пример использования сохранения группировки Excel файлов")
    print("=" * 60)
    
    # Путь к тестовому файлу
    excel_file = "результаты/сложный_тест_группировка.xlsx"
    json_file = "результаты/пример_группировка.json"
    restored_excel = "результаты/пример_восстановленный_с_группировкой.xlsx"
    
    print(f"📂 Работаем с файлом: {excel_file}")
    
    # 1. Преобразуем Excel в JSON с сохранением группировки
    print("\n🔄 Преобразование Excel → JSON с сохранением группировки...")
    try:
        preserver = ExcelHierarchyPreserver(excel_file)
        if preserver.to_json(json_file):
            print(f"✅ Успешно! JSON файл сохранен: {json_file}")
        else:
            print("❌ Ошибка преобразования")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # 2. Преобразуем JSON обратно в Excel с восстановлением группировки
    print("\n🔄 Преобразование JSON → Excel с восстановлением группировки...")
    try:
        if json_to_excel(json_file, restored_excel):
            print(f"✅ Успешно! Восстановленный Excel файл: {restored_excel}")
        else:
            print("❌ Ошибка восстановления")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # 3. Проверяем существование файлов
    if os.path.exists(excel_file) and os.path.exists(json_file) and os.path.exists(restored_excel):
        print("\n🎉 Все файлы успешно созданы!")
        print("   Теперь вы можете открыть их в Excel и убедиться, что группировка сохранена.")
    else:
        print("\n❌ Некоторые файлы отсутствуют")
    
    print("\n💡 Советы по использованию:")
    print("   • Используйте ExcelHierarchyPreserver для работы с Excel файлами")
    print("   • Преобразование в JSON сохраняет полную структуру файла")
    print("   • Восстановление из JSON восстанавливает все аспекты оригинала")
    print("   • Группировка строк и столбцов теперь сохраняется автоматически!")

if __name__ == "__main__":
    main()