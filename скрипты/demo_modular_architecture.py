"""
Демонстрационный скрипт для работы новой модульной архитектуры.
"""

import os
import sys
from datetime import datetime

# Добавляем путь к скриптам в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from data_structure import create_empty_data_structure, validate_data_structure, print_data_structure_info
from data_converter import to_csv, from_csv


def demo_data_structure():
    """Демонстрация работы с унифицированной структурой данных."""
    print("=== Демонстрация работы с унифицированной структурой данных ===")
    
    # 1. Создаем пустую структуру данных
    print("1. Создание пустой структуры данных...")
    data_structure = create_empty_data_structure()
    print("   Пустая структура данных создана")
    
    # 2. Заполняем структуру данными
    print("2. Заполнение структуры данными...")
    
    # Заполняем информацию об отчете
    data_structure["report_info"]["period_start"] = datetime(2025, 7, 15)
    data_structure["report_info"]["period_end"] = datetime(2025, 7, 21)
    data_structure["report_info"]["warehouse"] = "Монетка рыба (Рыба Дачная)"
    data_structure["report_info"]["creation_date"] = datetime.now()
    
    # Добавляем номенклатуры
    data_structure["nomenclatures"].append({
        "name": "Тушка",
        "initial_balance": 205.71,
        "incoming": 52.46,
        "outgoing": 80.69,
        "final_balance": 177.48,
        "documents": [
            {
                "type": "Inventory",
                "date": datetime(2025, 7, 14, 22, 56, 44),
                "details": {
                    "document_number": "000000000000158"
                }
            }
        ],
        "batches": [
            {
                "date": datetime(2025, 7, 14, 22, 56, 44),
                "initial_balance": 205.71,
                "incoming": 0,
                "outgoing": 0,
                "final_balance": 205.71
            }
        ]
    })
    
    data_structure["nomenclatures"].append({
        "name": "Монетка рыба (Рыба Дачная)",
        "initial_balance": 603.289,
        "incoming": 354.345,
        "outgoing": 340.35,
        "final_balance": 617.284,
        "documents": [],
        "batches": []
    })
    
    print("   Структура данных заполнена")
    
    # 3. Выводим информацию о структуре данных
    print("3. Вывод информации о структуре данных...")
    print_data_structure_info(data_structure)
    
    # 4. Проверяем валидность структуры данных
    print("4. Проверка валидности структуры данных...")
    is_valid = validate_data_structure(data_structure)
    print(f"   Структура данных валидна: {is_valid}")
    
    if not is_valid:
        print("   ОШИБКА: Структура данных не валидна!")
        return False
    
    print()
    return True


def demo_data_converter():
    """Демонстрация работы модуля преобразования данных."""
    print("=== Демонстрация работы модуля преобразования данных ===")
    
    # 1. Создаем тестовую структуру данных
    print("1. Создание тестовой структуры данных...")
    data_structure = create_empty_data_structure()
    
    # Заполняем структуру данными
    data_structure["report_info"]["period_start"] = datetime(2025, 7, 15)
    data_structure["report_info"]["period_end"] = datetime(2025, 7, 21)
    data_structure["report_info"]["warehouse"] = "Монетка рыба (Рыба Дачная)"
    
    data_structure["nomenclatures"].append({
        "name": "Тушка",
        "initial_balance": 205.71,
        "incoming": 52.46,
        "outgoing": 80.69,
        "final_balance": 177.48,
        "documents": [
            {
                "type": "Inventory",
                "date": datetime(2025, 7, 14, 22, 56, 44),
                "details": {
                    "document_number": "000000000000158"
                }
            }
        ],
        "batches": [
            {
                "date": datetime(2025, 7, 14, 22, 56, 44),
                "initial_balance": 205.71,
                "incoming": 0,
                "outgoing": 0,
                "final_balance": 205.71
            }
        ]
    })
    
    data_structure["nomenclatures"].append({
        "name": "Монетка рыба (Рыба Дачная)",
        "initial_balance": 603.289,
        "incoming": 354.345,
        "outgoing": 340.35,
        "final_balance": 617.284,
        "documents": [],
        "batches": []
    })
    
    print("   Тестовая структура данных создана и заполнена")
    
    # 2. Преобразуем структуру данных в CSV
    print("2. Преобразование структуры данных в CSV...")
    project_root = os.path.dirname(script_dir)
    demo_output_path = os.path.join(project_root, "результаты", "demo_modular_architecture.csv")
    
    try:
        to_csv(data_structure, demo_output_path)
        print(f"   Данные успешно преобразованы в CSV и сохранены в файл: {demo_output_path}")
    except Exception as e:
        print(f"   ОШИБКА: Не удалось преобразовать данные в CSV: {str(e)}")
        return False
    
    # 3. Загружаем данные из CSV
    print("3. Загрузка данных из CSV...")
    try:
        loaded_data_structure = from_csv(demo_output_path.replace(".csv", ""))
        print("   Данные успешно загружены из CSV")
    except Exception as e:
        print(f"   ОШИБКА: Не удалось загрузить данные из CSV: {str(e)}")
        return False
    
    # 4. Проверяем валидность загруженной структуры данных
    print("4. Проверка валидности загруженной структуры данных...")
    is_loaded_valid = validate_data_structure(loaded_data_structure)
    print(f"   Загруженная структура данных валидна: {is_loaded_valid}")
    
    if not is_loaded_valid:
        print("   ОШИБКА: Загруженная структура данных не валидна!")
        return False
    
    print()
    return True


def main():
    """Основная функция для демонстрации работы модульной архитектуры."""
    print("Демонстрация работы модульной архитектуры")
    print("=" * 50)
    
    # Демонстрируем работу с унифицированной структурой данных
    success1 = demo_data_structure()
    
    # Демонстрируем работу модуля преобразования данных
    success2 = demo_data_converter()
    
    # Выводим итог
    print("=" * 50)
    if success1 and success2:
        print("Демонстрация работы модульной архитектуры завершена успешно!")
    else:
        print("При демонстрации работы модульной архитектуры произошли ошибки!")


if __name__ == "__main__":
    main()