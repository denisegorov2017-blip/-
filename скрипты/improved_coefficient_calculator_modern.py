"""
Современная версия скрипта для расчета коэффициентов усушки с использованием модульной архитектуры.
"""

import pandas as pd
import numpy as np
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Импортируем модули проекта
from data_structure import DataStructure, validate_data_structure, print_data_structure_info
from data_converter import to_csv, from_csv
# from pdf_parser import parse_pdf_report  # TODO: Реализовать PDF парсер
# from excel_parser import parse_excel_report  # TODO: Реализовать Excel парсер

# Импортируем существующие модули
from analytics import forecast_shrinkage
from improved_coefficient_calculator import (
    setup_logging, 
    calculate_coefficients_improved,
    save_coefficients_to_csv,
    save_coefficients_to_html,
    save_failures_to_html
)


def load_data(input_file: str, calculation_start_date: Optional[datetime] = None) -> DataStructure:
    """
    Загружает данные из файла и возвращает унифицированную структуру данных.
    
    Args:
        input_file: Путь к входному файлу
        calculation_start_date: Дата начала расчета (для извлечения остатков на заданную дату)
        
    Returns:
        Унифицированная структура данных
    """
    # Определяем тип файла по расширению
    _, ext = os.path.splitext(input_file)
    
    if ext.lower() == '.pdf':
        # TODO: Реализовать загрузку данных из PDF
        print("Загрузка данных из PDF файла пока не реализована")
        # data_structure = parse_pdf_report(input_file)
        raise NotImplementedError("Загрузка данных из PDF файла пока не реализована")
    elif ext.lower() in ['.xls', '.xlsx']:
        # TODO: Реализовать загрузку данных из Excel
        print("Загрузка данных из Excel файла пока не реализована")
        # data_structure = parse_excel_report(input_file)
        raise NotImplementedError("Загрузка данных из Excel файла пока не реализована")
    elif ext.lower() == '.csv':
        # Для CSV файлов используем существующую функцию
        from improved_coefficient_calculator import parse_inventory_data_improved
        nomenclature_data, group_data = parse_inventory_data_improved(input_file, calculation_start_date)
        
        # Преобразуем данные в унифицированную структуру
        data_structure = _convert_legacy_data(nomenclature_data, group_data)
        return data_structure
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}")


def _convert_legacy_data(
    nomenclature_data: List[Dict], 
    group_data: List[str]
) -> DataStructure:
    """
    Преобразует данные из legacy формата в унифицированную структуру.
    
    Args:
        nomenclature_data: Список словарей с данными по номенклатурам
        group_data: Список названий групп товаров
        
    Returns:
        Унифицированная структура данных
    """
    # TODO: Реализовать преобразование данных
    # Пока возвращаем заглушку
    from data_structure import create_empty_data_structure
    return create_empty_data_structure()


def calculate_shrinkage_coefficients(data_structure: DataStructure) -> List[Dict]:
    """
    Рассчитывает коэффициенты усушки для всех номенклатур.
    
    Args:
        data_structure: Унифицированная структура данных
        
    Returns:
        Список словарей с результатами расчета
    """
    # Проверяем валидность структуры данных
    if not validate_data_structure(data_structure):
        raise ValueError("Невалидная структура данных")
    
    results = []
    failed_items = []
    
    # Проходим по всем номенклатурам
    for nomenclature in data_structure["nomenclatures"]:
        try:
            # Рассчитываем коэффициенты для номенклатуры
            coefficients, reason, weight = calculate_coefficients_improved(nomenclature)
            
            if coefficients:
                results.append({
                    'Номенклатура': nomenclature['name'],
                    'a': coefficients['a'],
                    'b (день⁻¹)': coefficients['b'],
                    'c': coefficients['c'],
                    'Примечание': f"Расчет по данным за период. Усушка {nomenclature['summary']['initial'] + nomenclature['summary']['income'] - nomenclature['summary']['expense'] - nomenclature['summary']['final']:.3f} кг."
                })
            else:
                failed_items.append({
                    'name': nomenclature['name'],
                    'reason': reason,
                    'weight': weight
                })
        except Exception as e:
            failed_items.append({
                'name': nomenclature['name'],
                'reason': f"Ошибка при расчете: {str(e)}",
                'weight': None
            })
    
    return results


def main():
    """
    Основная функция для расчета коэффициентов усушки.
    """
    try:
        # Создаем парсер аргументов командной строки
        parser = argparse.ArgumentParser(description="Расчет коэффициентов усушки")
        parser.add_argument('--input_file', type=str, help='Путь к входному файлу')
        parser.add_argument('--calculation_start_date', type=str, help='Дата начала расчета (ГГГГ-ММ-ДД)')
        parser.add_argument('--output_dir', type=str, default='../результаты', help='Директория для выходных файлов')
        args = parser.parse_args()
        
        # Настройка логирования
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        info_logger, error_logger = setup_logging(project_root)
        info_logger.info("Запуск расчета коэффициентов усушки")
        
        # Определяем путь к входному файлу
        if args.input_file:
            input_file = args.input_file
        else:
            input_file = os.path.join(
                project_root, 
                "исходные_данные", 
                "Для_расчета_коэфф", 
                "sheet_1_Лист_1.csv"
            )
        
        # Проверяем существование входного файла
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Входной файл не найден: {input_file}")
        
        # Определяем дату начала расчета
        calculation_start_date = None
        if args.calculation_start_date:
            try:
                calculation_start_date = datetime.strptime(args.calculation_start_date, "%Y-%m-%d")
                print(f"Будет использован остаток на утро {args.calculation_start_date}")
            except ValueError:
                print(f"Неверный формат даты: {args.calculation_start_date}. Используется остаток по умолчанию.")
        
        # Загружаем данные
        print(f"Загрузка данных из файла: {input_file}")
        data_structure = load_data(input_file, calculation_start_date)
        
        # Выводим информацию о структуре данных
        print_data_structure_info(data_structure)
        
        # Рассчитываем коэффициенты усушки
        print("Расчет коэффициентов усушки...")
        results = calculate_shrinkage_coefficients(data_structure)
        
        # Сохраняем результаты
        output_dir = args.output_dir if args.output_dir else os.path.join(project_root, "результаты")
        os.makedirs(output_dir, exist_ok=True)
        
        csv_output_file = os.path.join(output_dir, "коэффициенты_усушки_улучшенные_modern.csv")
        html_output_file = os.path.join(output_dir, "коэффициенты_усушки_улучшенные_modern.html")
        
        if results:
            save_coefficients_to_csv(results, csv_output_file, [], html_output_file)
            save_coefficients_to_html(results, html_output_file)
            print(f"Результаты сохранены в файлы:")
            print(f"  - CSV: {csv_output_file}")
            print(f"  - HTML: {html_output_file}")
        else:
            print("Не удалось рассчитать коэффициенты ни для одной номенклатуры")
            
        info_logger.info(f"Расчет завершен. Успешно: {len(results)}")
        print(f"\nРасчет завершен. Успешно: {len(results)}")
        
    except Exception as e:
        print(f"Произошла критическая ошибка: {str(e)}")
        if 'error_logger' in locals():
            error_logger.error(f"Критическая ошибка: {str(e)}")


if __name__ == "__main__":
    main()