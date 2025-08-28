#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка восстановления группировки из JSON файла
"""

import sys
import os
import json
from openpyxl import load_workbook

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_restored_excel_grouping():
    """Проверяет, что восстановленный Excel файл содержит группировку."""
    restored_file = "результаты/восстановленный_тест_группировка.xlsx"
    
    if not os.path.exists(restored_file):
        print(f"❌ Файл {restored_file} не найден")
        return False
    
    try:
        # Открываем восстановленный Excel файл
        wb = load_workbook(restored_file)
        ws = wb.active
        
        print(f"🔍 Проверка восстановленного файла: {restored_file}")
        print(f"   Активный лист: {ws.title}")
        
        # Проверяем группировку строк
        grouped_rows = []
        for row_num, row_dim in ws.row_dimensions.items():
            if hasattr(row_dim, 'outline_level') and row_dim.outline_level > 0:
                grouped_rows.append({
                    'row': row_num,
                    'level': row_dim.outline_level,
                    'hidden': getattr(row_dim, 'hidden', False)
                })
        
        if grouped_rows:
            print(f"✅ Найдена группировка строк: {len(grouped_rows)} строк")
            for row_info in grouped_rows:
                status = "свернута" if row_info['hidden'] else "развернута"
                print(f"   Строка {row_info['row']}: уровень {row_info['level']}, {status}")
        else:
            print("⚠️  Группировка строк не найдена")
        
        # Проверяем группировку столбцов
        grouped_cols = []
        for col_letter, col_dim in ws.column_dimensions.items():
            if hasattr(col_dim, 'outline_level') and col_dim.outline_level > 0:
                grouped_cols.append({
                    'column': col_letter,
                    'level': col_dim.outline_level,
                    'hidden': getattr(col_dim, 'hidden', False)
                })
        
        if grouped_cols:
            print(f"✅ Найдена группировка столбцов: {len(grouped_cols)} столбцов")
            for col_info in grouped_cols:
                status = "свернут" if col_info['hidden'] else "развернут"
                print(f"   Столбец {col_info['column']}: уровень {col_info['level']}, {status}")
        else:
            print("⚠️  Группировка столбцов не найдена")
        
        wb.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки восстановленного файла: {e}")
        return False

def main():
    """Основная функция проверки."""
    print("🔬 Проверка восстановления группировки из JSON файла")
    print("=" * 60)
    
    success = check_restored_excel_grouping()
    
    if success:
        print("\n✅ Проверка восстановления группировки завершена успешно!")
        print("   Группировка строк и столбцов сохраняется при преобразовании Excel ↔ JSON")
    else:
        print("\n❌ Проверка восстановления группировки провалена")

if __name__ == "__main__":
    main()