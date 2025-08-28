#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование функций сохранения иерархии Excel файлов
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path

# Импортируем наши новые модули
# Добавляем путь к корню проекта, чтобы можно было импортировать модули проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.excel_toolkit import ExcelProcessor, json_to_excel
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver, json_to_excel as preserver_json_to_excel


def create_test_excel_file(filename: str = "test_hierarchy.xlsx") -> str:
    """Создает тестовый Excel файл с несколькими листами."""
    # Создаем тестовые данные
    data1 = {
        'A': [1, 2, 3, 4],
        'B': ['Январь', 'Февраль', 'Март', 'Апрель'],
        'C': [100, 200, 150, 300]
    }
    
    data2 = {
        'X': [10, 20, 30],
        'Y': ['Красный', 'Зеленый', 'Синий'],
        'Z': [5.5, 7.2, 3.8]
    }
    
    # Создаем DataFrame
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    
    # Сохраняем в Excel файл с несколькими листами
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Продажи', index=False)
        df2.to_excel(writer, sheet_name='Цвета', index=False)
    
    return filename


def test_excel_processor():
    """Тестирование ExcelProcessor с новыми возможностями."""
    print("🧪 Тестирование ExcelProcessor")
    print("=" * 50)
    
    # Создаем тестовый файл
    test_file = create_test_excel_file("тестовый_файл.xlsx")
    
    try:
        # Создаем процессор
        processor = ExcelProcessor(test_file)
        
        # Получаем информацию о файле
        print(f"✅ Файл загружен: {test_file}")
        print(f"✅ Количество листов: {len(processor.sheet_names)}")
        print(f"✅ Имена листов: {processor.sheet_names}")
        
        # Получаем сводку
        summary = processor.get_data_summary()
        print(f"✅ Сводка по файлу:")
        print(f"   Всего листов: {summary['total_sheets']}")
        
        # Экспортируем в JSON
        json_output = "результаты/тест_процессора.json"
        os.makedirs(os.path.dirname(json_output), exist_ok=True)
        
        if processor.export_to_json(json_output):
            print(f"✅ Экспорт в JSON выполнен: {json_output}")
            
            # Проверяем содержимое JSON файла
            with open(json_output, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                print(f"✅ Структура JSON файла:")
                if 'sheets' in json_data:
                    print(f"   Найдено листов в JSON: {len(json_data['sheets'])}")
                    for sheet_name in json_data['sheets']:
                        print(f"   - {sheet_name}: {len(json_data['sheets'][sheet_name])} строк")
                else:
                    print(f"   Одиночный лист: {len(json_data)} строк")
        else:
            print("❌ Ошибка экспорта в JSON")
            
        # Преобразуем JSON обратно в Excel
        restored_excel = "результаты/восстановленный_файл.xlsx"
        os.makedirs(os.path.dirname(restored_excel), exist_ok=True)
        
        if json_to_excel(json_output, restored_excel):
            print(f"✅ Преобразование JSON в Excel выполнено: {restored_excel}")
        else:
            print("❌ Ошибка преобразования JSON в Excel")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования ExcelProcessor: {e}")
    
    finally:
        # Удаляем тестовый файл
        if os.path.exists(test_file):
            os.remove(test_file)


def test_excel_hierarchy_preserver():
    """Тестирование ExcelHierarchyPreserver."""
    print("\n🧪 Тестирование ExcelHierarchyPreserver")
    print("=" * 50)
    
    # Создаем тестовый файл
    test_file = create_test_excel_file("тестовый_файл2.xlsx")
    
    try:
        # Создаем объект для сохранения иерархии
        preserver = ExcelHierarchyPreserver(test_file)
        
        # Получаем информацию о структуре
        structure_info = preserver.get_structure_info()
        print(f"✅ Файл загружен: {test_file}")
        print(f"✅ Количество листов: {structure_info['sheet_count']}")
        
        if 'sheets' in structure_info:
            for sheet_name, sheet_info in structure_info['sheets'].items():
                print(f"   Лист '{sheet_name}': {sheet_info['rows']} строк, {sheet_info['columns']} колонок")
        
        # Преобразуем в JSON
        json_output = "результаты/иерархия_тест.json"
        os.makedirs(os.path.dirname(json_output), exist_ok=True)
        
        if preserver.to_json(json_output):
            print(f"✅ Преобразование в JSON выполнено: {json_output}")
        else:
            print("❌ Ошибка преобразования в JSON")
            
        # Преобразуем в CSV файлы
        csv_output_dir = "результаты/csv_тест"
        os.makedirs(csv_output_dir, exist_ok=True)
        
        if preserver.to_hierarchical_csv(csv_output_dir):
            print(f"✅ Преобразование в CSV выполнено: {csv_output_dir}")
            # Проверяем созданные файлы
            csv_files = list(Path(csv_output_dir).glob("*.csv"))
            print(f"✅ Создано CSV файлов: {len(csv_files)}")
            for csv_file in csv_files:
                print(f"   - {csv_file.name}")
        else:
            print("❌ Ошибка преобразования в CSV")
            
        # Преобразуем JSON обратно в Excel
        restored_excel = "результаты/восстановленный_файл2.xlsx"
        os.makedirs(os.path.dirname(restored_excel), exist_ok=True)
        
        if preserver_json_to_excel(json_output, restored_excel):
            print(f"✅ Преобразование JSON в Excel выполнено: {restored_excel}")
        else:
            print("❌ Ошибка преобразования JSON в Excel")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования ExcelHierarchyPreserver: {e}")
    
    finally:
        # Удаляем тестовый файл
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """Основная функция для запуска тестов."""
    print("🚀 Тестирование новых возможностей сохранения иерархии Excel файлов")
    print("=" * 70)
    
    # Создаем директорию для результатов
    os.makedirs("результаты", exist_ok=True)
    
    # Запускаем тесты
    test_excel_processor()
    test_excel_hierarchy_preserver()
    
    print("\n✅ Тестирование завершено. Результаты сохранены в папке 'результаты'")


if __name__ == "__main__":
    main()