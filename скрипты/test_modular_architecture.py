"""
Тестовый скрипт для проверки работы модульной архитектуры.
"""

import os
import sys
from datetime import datetime

# Добавляем путь к скриптам в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from data_structure import create_empty_data_structure, validate_data_structure, print_data_structure_info
from data_converter import to_csv, from_csv


def test_data_structure():
    """Тестирование модуля data_structure."""
    print("=== Тестирование модуля data_structure ===")
    
    # Создаем пустую структуру данных
    print("1. Создание пустой структуры данных...")
    data_structure = create_empty_data_structure()
    print("   Пустая структура данных создана")
    
    # Выводим информацию о структуре данных
    print("2. Вывод информации о структуре данных...")
    print_data_structure_info(data_structure)
    
    # Проверяем валидность структуры данных
    print("3. Проверка валидности структуры данных...")
    is_valid = validate_data_structure(data_structure)
    print(f"   Структура данных валидна: {is_valid}")
    
    print()


def test_data_converter():
    """Тестирование модуля data_converter."""
    print("=== Тестирование модуля data_converter ===")
    
    # Создаем тестовую структуру данных
    print("1. Создание тестовой структуры данных...")
    data_structure = create_empty_data_structure()
    
    # Заполняем структуру данными
    data_structure["report_info"]["period_start"] = datetime(2025, 7, 15)
    data_structure["report_info"]["period_end"] = datetime(2025, 7, 21)
    data_structure["report_info"]["warehouse"] = "Монетка рыба (Рыба Дачная)"
    
    # Добавляем тестовые номенклатуры
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
    
    # Выводим информацию о структуре данных
    print("2. Вывод информации о структуре данных...")
    print_data_structure_info(data_structure)
    
    # Проверяем валидность структуры данных
    print("3. Проверка валидности структуры данных...")
    is_valid = validate_data_structure(data_structure)
    print(f"   Структура данных валидна: {is_valid}")
    
    if not is_valid:
        print("   ОШИБКА: Структура данных не валидна!")
        return
    
    # Преобразуем структуру данных в CSV
    print("4. Преобразование структуры данных в CSV...")
    project_root = os.path.dirname(script_dir)
    test_output_path = os.path.join(project_root, "результаты", "test_modular_architecture.csv")
    
    try:
        to_csv(data_structure, test_output_path)
        print(f"   Данные успешно преобразованы в CSV и сохранены в файл: {test_output_path}")
    except Exception as e:
        print(f"   ОШИБКА: Не удалось преобразовать данные в CSV: {str(e)}")
        return
    
    # Загружаем данные из CSV
    print("5. Загрузка данных из CSV...")
    try:
        loaded_data_structure = from_csv(test_output_path.replace(".csv", ""))
        print("   Данные успешно загружены из CSV")
    except Exception as e:
        print(f"   ОШИБКА: Не удалось загрузить данные из CSV: {str(e)}")
        return
    
    # Проверяем валидность загруженной структуры данных
    print("6. Проверка валидности загруженной структуры данных...")
    is_loaded_valid = validate_data_structure(loaded_data_structure)
    print(f"   Загруженная структура данных валидна: {is_loaded_valid}")
    
    if not is_loaded_valid:
        print("   ОШИБКА: Загруженная структура данных не валидна!")
        return
    
    # Сравниваем структуры данных
    print("7. Сравнение исходной и загруженной структур данных...")
    if _compare_data_structures(data_structure, loaded_data_structure):
        print("   Структуры данных совпадают")
    else:
        print("   ОШИБКА: Структуры данных не совпадают!")
    
    print()


def _compare_data_structures(ds1: dict, ds2: dict) -> bool:
    """
    Сравнивает две структуры данных.
    
    Args:
        ds1: Первая структура данных
        ds2: Вторая структура данных
        
    Returns:
        True, если структуры данных совпадают, иначе False
    """
    # Проверяем информацию об отчете
    if ds1["report_info"] != ds2["report_info"]:
        print("   Различается информация об отчете")
        return False
    
    # Проверяем количество номенклатур
    if len(ds1["nomenclatures"]) != len(ds2["nomenclatures"]):
        print("   Различается количество номенклатур")
        return False
    
    # Проверяем каждую номенклатуру
    for i, (nom1, nom2) in enumerate(zip(ds1["nomenclatures"], ds2["nomenclatures"])):
        # Проверяем основные поля
        main_fields = ["name", "initial_balance", "incoming", "outgoing", "final_balance"]
        for field in main_fields:
            if nom1[field] != nom2[field]:
                print(f"   Различается поле {field} в номенклатуре {i}")
                return False
        
        # Проверяем документы (упрощенно)
        if len(nom1["documents"]) != len(nom2["documents"]):
            print(f"   Различается количество документов в номенклатуре {i}")
            return False
        
        # Проверяем партии (упрощенно)
        if len(nom1["batches"]) != len(nom2["batches"]):
            print(f"   Различается количество партий в номенклатуре {i}")
            return False
    
    return True


def main():
    """Основная функция для тестирования модульной архитектуры."""
    print("Тестирование модульной архитектуры")
    print("=" * 50)
    
    # Тестируем модуль data_structure
    test_data_structure()
    
    # Тестируем модуль data_converter
    test_data_converter()
    
    print("Тестирование завершено")


if __name__ == "__main__":
    main()