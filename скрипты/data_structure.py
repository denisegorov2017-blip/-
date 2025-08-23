"""
Модуль для определения и валидации унифицированной структуры данных.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict


class Document(TypedDict):
    """Тип для описания документа."""
    type: str  # "Inventory", "Shipment", "Receipt", etc.
    date: datetime
    details: Dict[str, Any]  # Специфические детали документа


class Batch(TypedDict):
    """Тип для описания партии."""
    date: datetime
    initial_balance: float
    incoming: float
    outgoing: float
    final_balance: float


class Nomenclature(TypedDict):
    """Тип для описания номенклатуры."""
    name: str
    initial_balance: float
    incoming: float
    outgoing: float
    final_balance: float
    documents: List[Document]
    batches: List[Batch]


class ReportInfo(TypedDict):
    """Тип для описания информации об отчете."""
    period_start: datetime
    period_end: datetime
    warehouse: str
    creation_date: datetime


class DataStructure(TypedDict):
    """Тип для описания всей унифицированной структуры данных."""
    report_info: ReportInfo
    nomenclatures: List[Nomenclature]


def create_empty_data_structure() -> DataStructure:
    """
    Создает пустую унифицированную структуру данных.
    
    Returns:
        Пустая унифицированная структура данных
    """
    return {
        "report_info": {
            "period_start": datetime.min,
            "period_end": datetime.min,
            "warehouse": "",
            "creation_date": datetime.now()
        },
        "nomenclatures": []
    }


def validate_data_structure(data_structure: Dict[str, Any]) -> bool:
    """
    Проверяет валидность унифицированной структуры данных.
    
    Args:
        data_structure: Унифицированная структура данных
        
    Returns:
        True, если структура валидна, иначе False
    """
    # Проверяем обязательные поля
    required_fields = ["report_info", "nomenclatures"]
    for field in required_fields:
        if field not in data_structure:
            print(f"Отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем структуру информации об отчете
    report_info = data_structure["report_info"]
    report_info_fields = ["period_start", "period_end", "warehouse", "creation_date"]
    for field in report_info_fields:
        if field not in report_info:
            print(f"В информации об отчете отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем типы данных в информации об отчете
    if not isinstance(report_info["period_start"], datetime):
        print("Неверный тип данных для period_start")
        return False
    
    if not isinstance(report_info["period_end"], datetime):
        print("Неверный тип данных для period_end")
        return False
    
    if not isinstance(report_info["warehouse"], str):
        print("Неверный тип данных для warehouse")
        return False
    
    if not isinstance(report_info["creation_date"], datetime):
        print("Неверный тип данных для creation_date")
        return False
    
    # Проверяем структуру номенклатур
    for i, nomenclature in enumerate(data_structure["nomenclatures"]):
        nomenclature_fields = ["name", "initial_balance", "incoming", "outgoing", "final_balance", "documents", "batches"]
        for field in nomenclature_fields:
            if field not in nomenclature:
                print(f"В номенклатуре {i} отсутствует обязательное поле: {field}")
                return False
        
        # Проверяем типы данных в номенклатуре
        if not isinstance(nomenclature["name"], str):
            print(f"В номенклатуре {i} неверный тип данных для name")
            return False
        
        if not isinstance(nomenclature["initial_balance"], (int, float)):
            print(f"В номенклатуре {i} неверный тип данных для initial_balance")
            return False
        
        if not isinstance(nomenclature["incoming"], (int, float)):
            print(f"В номенклатуре {i} неверный тип данных для incoming")
            return False
        
        if not isinstance(nomenclature["outgoing"], (int, float)):
            print(f"В номенклатуре {i} неверный тип данных для outgoing")
            return False
        
        if not isinstance(nomenclature["final_balance"], (int, float)):
            print(f"В номенклатуре {i} неверный тип данных для final_balance")
            return False
        
        if not isinstance(nomenclature["documents"], list):
            print(f"В номенклатуре {i} неверный тип данных для documents")
            return False
        
        if not isinstance(nomenclature["batches"], list):
            print(f"В номенклатуре {i} неверный тип данных для batches")
            return False
    
    return True


def print_data_structure_info(data_structure: Dict[str, Any]) -> None:
    """
    Выводит информацию о структуре данных.
    
    Args:
        data_structure: Унифицированная структура данных
    """
    if not validate_data_structure(data_structure):
        print("Структура данных не валидна")
        return
    
    report_info = data_structure["report_info"]
    print("Информация об отчете:")
    print(f"  Период: с {report_info['period_start'].strftime('%d.%m.%Y')} по {report_info['period_end'].strftime('%d.%m.%Y')}")
    print(f"  Склад: {report_info['warehouse']}")
    print(f"  Дата создания: {report_info['creation_date'].strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"  Найдено номенклатур: {len(data_structure['nomenclatures'])}")


def main():
    """
    Тестовая функция для проверки работы модуля.
    """
    # Создаем пустую структуру данных
    data_structure = create_empty_data_structure()
    
    # Выводим информацию о структуре данных
    print("Пустая структура данных:")
    print_data_structure_info(data_structure)
    
    # Проверяем валидность структуры данных
    is_valid = validate_data_structure(data_structure)
    print(f"Структура данных валидна: {is_valid}")


if __name__ == "__main__":
    main()