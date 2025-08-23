"""
Модуль для преобразования унифициентов нелинейной усушки, и предварительный расчет усушки 1.1\скрипты\data_converter.py.
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


def to_csv(data_structure: Dict[str, Any], output_path: str) -> None:
    """
    Преобразует унифицированную структуру данных в CSV формат и сохраняет в файл.
    
    Args:
        data_structure: Унифицированная структура данных
        output_path: Путь к выходному CSV файлу
    """
    # Создаем DataFrame для информации об отчете
    report_info_df = pd.DataFrame([data_structure["report_info"]])
    
    # Создаем DataFrame для номенклатур
    nomenclatures_data = []
    for nomenclature in data_structure["nomenclatures"]:
        nomenclature_data = {
            "nomenclature_name": nomenclature["name"],
            "initial_balance": nomenclature["initial_balance"],
            "incoming": nomenclature["incoming"],
            "outgoing": nomenclature["outgoing"],
            "final_balance": nomenclature["final_balance"]
        }
        
        # Добавляем информацию о документах
        for document in nomenclature.get("documents", []):
            nomenclature_data[f"document_{document['type']}"] = f"{document['date']}: {document.get('details', '')}"
        
        # Добавляем информацию о партиях
        for batch in nomenclature.get("batches", []):
            nomenclature_data[f"batch_{batch['date']}"] = f"Баланс: {batch['initial_balance']} -> {batch['final_balance']}"
        
        nomenclatures_data.append(nomenclature_data)
    
    nomenclatures_df = pd.DataFrame(nomenclatures_data)
    
    # Сохраняем в CSV файлы
    report_info_output = output_path.replace(".csv", "_report_info.csv")
    nomenclatures_output = output_path.replace(".csv", "_nomenclatures.csv")
    
    report_info_df.to_csv(report_info_output, index=False, encoding='utf-8')
    nomenclatures_df.to_csv(nomenclatures_output, index=False, encoding='utf-8')
    
    print(f"Данные сохранены в файлы:")
    print(f"  - Информация об отчете: {report_info_output}")
    print(f"  - Номенклатуры: {nomenclatures_output}")


def from_csv(csv_path: str) -> Dict[str, Any]:
    """
    Загружает данные из CSV файлов и возвращает унифицированную структуру данных.
    
    Args:
        csv_path: Путь к базовому CSV файлу (без суффикса _report_info или _nomenclatures)
        
    Returns:
        Унифицированная структура данных
    """
    # Формируем пути к файлам
    report_info_path = csv_path.replace(".csv", "_report_info.csv")
    nomenclatures_path = csv_path.replace(".csv", "_nomenclatures.csv")
    
    # Проверяем существование файлов
    if not os.path.exists(report_info_path):
        raise FileNotFoundError(f"Файл с информацией об отчете не найден: {report_info_path}")
    
    if not os.path.exists(nomenclatures_path):
        raise FileNotFoundError(f"Файл с номенклатурами не найден: {nomenclatures_path}")
    
    # Загружаем информацию об отчете
    report_info_df = pd.read_csv(report_info_path, encoding='utf-8')
    report_info = report_info_df.iloc[0].to_dict()
    
    # Загружаем информацию о номенклатурах
    nomenclatures_df = pd.read_csv(nomenclatures_path, encoding='utf-8')
    nomenclatures = []
    
    for _, row in nomenclatures_df.iterrows():
        nomenclature = {
            "name": row["nomenclature_name"],
            "initial_balance": row["initial_balance"],
            "incoming": row["incoming"],
            "outgoing": row["outgoing"],
            "final_balance": row["final_balance"],
            "documents": [],  # TODO: Реализовать извлечение документов
            "batches": []     # TODO: Реализовать извлечение партий
        }
        nomenclatures.append(nomenclature)
    
    # Формируем унифицированную структуру данных
    data_structure = {
        "report_info": report_info,
        "nomenclatures": nomenclatures
    }
    
    return data_structure


def validate_data_structure(data_structure: Dict[str, Any]) -> bool:
    """
    Проверяет валидность унифицированной структуры данных.
    
    Args:
        data_structure: Унифицированная структура данных
        
    Returns:
        True, если структура валидна, иначе False
    """
    # TODO: Реализовать логику валидации структуры данных
    
    # Проверяем обязательные поля
    required_fields = ["report_info", "nomenclatures"]
    for field in required_fields:
        if field not in data_structure:
            print(f"Отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем структуру информации об отчете
    report_info_fields = ["period_start", "period_end", "warehouse", "creation_date"]
    for field in report_info_fields:
        if field not in data_structure["report_info"]:
            print(f"В информации об отчете отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем структуру номенклатур
    for i, nomenclature in enumerate(data_structure["nomenclatures"]):
        nomenclature_fields = ["name", "initial_balance", "incoming", "outgoing", "final_balance"]
        for field in nomenclature_fields:
            if field not in nomenclature:
                print(f"В номенклатуре {i} отсутствует обязательное поле: {field}")
                return False
    
    return True


def main():
    """
    Тестовая функция для проверки работы конвертера.
    """
    import os
    
    # Получаем путь к тестовому CSV файлу
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Путь к тестовому CSV файлу
    test_csv_path = os.path.join(
        project_root, 
        "исходные_данные", 
        "Для_расчета_коэфф",
        "sheet_1_Лист_1.csv"
    )
    
    # Проверяем существование файла
    if not os.path.exists(test_csv_path):
        print(f"Тестовый файл не найден: {test_csv_path}")
        return
    
    # TODO: Реализовать тестирование конвертера
    print("Тестирование конвертера данных")
    print("(Пока не реализовано)")


if __name__ == "__main__":
    main()