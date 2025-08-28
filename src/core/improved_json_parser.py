#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный парсер JSON для реальных данных.
Отвечает за преобразование структурированного JSON-файла в чистый DataFrame,
учитывая реальную структуру данных из Excel файлов.
"""

import json
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any
from datetime import datetime

def parse_from_json(json_path: str) -> pd.DataFrame:
    """
    Генерирует датасет для расчета коэффициентов из JSON-файла с реальной структурой.
    
    Args:
        json_path: Путь к JSON файлу.
        
    Returns:
        pandas.DataFrame: Подготовленный датасет.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем, является ли это новым форматом (с ключом "sheets")
        if "sheets" in data:
            # Новый формат - используем его напрямую
            return _parse_real_format(data)
        else:
            # Если старый формат, пробуем обработать как новый
            return _parse_real_format({"sheets": {"Sheet1": data}})
    except FileNotFoundError:
        raise ValueError(f"Файл не найден: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Ошибка декодирования JSON: {json_path}")
    except Exception as e:
        raise ValueError(f"Ошибка обработки данных в файле {json_path}: {e}")

def _parse_real_format(data: Dict[str, Any]) -> pd.DataFrame:
    """Парсит реальный формат JSON файла."""
    # For simplicity, we'll assume the data is in the first sheet
    sheet_names = list(data["sheets"].keys())
    if not sheet_names:
        return pd.DataFrame()
    
    sheet_name = sheet_names[0]
    sheet_data = data["sheets"][sheet_name]
    
    if not sheet_data:
        return pd.DataFrame()
    
    # Ищем заголовки таблицы
    header_row_idx = -1
    balance_headers_idx = -1
    
    # Ищем строку с заголовками баланса
    for i, row in enumerate(sheet_data):
        if len(row) >= 9 and row[4] is not None and "Начальный остаток" in str(row[4]):
            header_row_idx = i
            balance_headers_idx = i + 1  # Следующая строка содержит детали
            break
    
    if header_row_idx == -1:
        # Если не нашли стандартные заголовки, ищем альтернативные
        return _parse_alternative_format(sheet_data)
    
    # Определяем индексы колонок
    initial_balance_col = 4  # "Количество Начальный остаток"
    incoming_col = 6         # "Количество Приход"
    outgoing_col = 7         # "Количество Расход"
    final_balance_col = 8    # "Количество Конечный остаток"
    
    # Собираем данные по номенклатурам
    all_metrics = []
    
    # Проходим по строкам данных
    i = balance_headers_idx + 1
    while i < len(sheet_data):
        row = sheet_data[i]
        
        # Проверяем, является ли строка номенклатурой
        if _is_nomenclature_row(row, sheet_data, i):
            nomenclature_name = str(row[0]) if row[0] is not None else ""
            
            # Ищем следующую номенклатуру или конец данных
            next_nom_idx = _find_next_nomenclature(sheet_data, i + 1)
            if next_nom_idx == -1:
                next_nom_idx = len(sheet_data)
            
            # Собираем все данные для этой номенклатуры
            initial_balance, incoming, outgoing, final_balance = _extract_balance_data(
                sheet_data, i + 1, next_nom_idx - 1,
                initial_balance_col, incoming_col, outgoing_col, final_balance_col
            )
            
            # Рассчитываем период хранения
            storage_days = _calculate_storage_days(sheet_data, i + 1, next_nom_idx - 1)
            
            # Создаем запись, если есть данные
            if initial_balance > 0 or incoming > 0 or outgoing > 0 or final_balance > 0:
                theoretical_balance = initial_balance + incoming - outgoing
                shrinkage = max(0, theoretical_balance - final_balance)
                
                metric = {
                    'Номенклатура': nomenclature_name,
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Теоретический_остаток': theoretical_balance,
                    'Усушка': shrinkage,
                    'Коэффициент_усушки': shrinkage / initial_balance if initial_balance > 0 else 0,
                    'Период_хранения_дней': storage_days,
                    'Количество_документов': next_nom_idx - i - 1
                }
                all_metrics.append(metric)
            
            i = next_nom_idx
        else:
            i += 1
    
    if not all_metrics:
        return pd.DataFrame()
    
    return pd.DataFrame(all_metrics)

def _is_nomenclature_row(row: List[Any], sheet_data: List[List[Any]], idx: int) -> bool:
    """Проверяет, является ли строка строкой номенклатуры."""
    if not row or row[0] is None:
        return False
    
    first_cell = str(row[0]).strip()
    
    # Проверяем, что это не строка с документом или датой
    first_cell_lower = first_cell.lower()
    if any(keyword in first_cell_lower for keyword in [
        'документ', 'партия', 'отчет', 'инвентаризация', 'приходная', 'списано', 'отбор', 'параметры'
    ]):
        return False
    
    # Проверяем, является ли это дата в формате дд.мм.гггг или гггг-мм-дд
    import re
    date_patterns = [
        r'\d{2}\.\d{2}\.\d{4}',  # дд.мм.гггг
        r'\d{4}-\d{2}-\d{2}',    # гггг-мм-дд
    ]
    for pattern in date_patterns:
        if re.match(pattern, first_cell):
            return False
    
    # Проверяем, содержит ли строка время (чч:мм:сс)
    if re.search(r'\d{1,2}:\d{2}(:\d{2})?', first_cell):
        return False
    
    # Проверяем, что следующая строка не продолжение этой
    if idx + 1 < len(sheet_data):
        next_row = sheet_data[idx + 1]
        if next_row and len(next_row) > 0 and next_row[0] is None:
            return False
    
    # Проверяем, что в строке есть числовые данные
    numeric_cols = [4, 6, 7, 8]  # Колонки с балансами
    has_numeric_data = any(
        len(row) > col and row[col] is not None and _is_numeric_value(row[col])
        for col in numeric_cols
    )
    
    # Дополнительная проверка: номенклатура обычно не содержит слов вроде "отчет", "накладная" и т.д.
    # и должна быть достаточно длинной (обычно больше 3 символов)
    is_likely_nomenclature = (
        len(first_cell) > 3 and
        not any(keyword in first_cell_lower for keyword in [
            'отчет', 'накладная', 'списание', 'инвентаризация', 'перемещение'
        ])
    )
    
    # Special case: if the first cell looks like a date/time but has numeric data in balance columns,
    # it might still be a nomenclature row
    if not is_likely_nomenclature and has_numeric_data:
        # Check if this looks like a date/time string
        time_pattern = r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}(:\d{2})?'
        if re.search(time_pattern, first_cell):
            # This is likely a document name with timestamp, not a nomenclature row
            return False
    
    return has_numeric_data and is_likely_nomenclature

def _is_numeric_value(value) -> bool:
    """Проверяет, является ли значение числовым."""
    if value is None:
        return False
    try:
        float(str(value).replace(',', '.'))
        return True
    except (ValueError, TypeError):
        return False

def _find_next_nomenclature(sheet_data: List[List[Any]], start_idx: int) -> int:
    """Находит индекс следующей строки номенклатуры."""
    for i in range(start_idx, len(sheet_data)):
        row = sheet_data[i]
        if _is_nomenclature_row(row, sheet_data, i):
            return i
    return -1

def _extract_balance_data(sheet_data: List[Any], start_idx: int, end_idx: int,
                         initial_col: int, incoming_col: int, outgoing_col: int, final_col: int) -> tuple:
    """Извлекает балансовые данные для номенклатуры."""
    initial_balance = 0.0
    incoming = 0.0
    outgoing = 0.0
    final_balance = 0.0
    
    # For the nomenclature row (which should be the first row), we take the values directly
    if start_idx < len(sheet_data):
        row = sheet_data[start_idx]
        if len(row) > initial_col and row[initial_col] is not None:
            try:
                initial_balance = float(str(row[initial_col]).replace(',', '.'))
            except (ValueError, TypeError):
                pass
                
        if len(row) > incoming_col and row[incoming_col] is not None:
            try:
                incoming = float(str(row[incoming_col]).replace(',', '.'))
            except (ValueError, TypeError):
                pass
                
        if len(row) > outgoing_col and row[outgoing_col] is not None:
            try:
                outgoing = float(str(row[outgoing_col]).replace(',', '.'))
            except (ValueError, TypeError):
                pass
                
        if len(row) > final_col and row[final_col] is not None:
            try:
                final_balance = float(str(row[final_col]).replace(',', '.'))
            except (ValueError, TypeError):
                pass
    
    # Replace NaN values with 0.0
    import math
    if math.isnan(initial_balance):
        initial_balance = 0.0
    if math.isnan(incoming):
        incoming = 0.0
    if math.isnan(outgoing):
        outgoing = 0.0
    if math.isnan(final_balance):
        final_balance = 0.0
    
    return initial_balance, incoming, outgoing, final_balance

def _calculate_storage_days(sheet_data: List[List[Any]], start_idx: int, end_idx: int) -> int:
    """Рассчитывает период хранения в днях."""
    # Пытаемся извлечь даты из документа
    dates = []
    
    for i in range(start_idx, min(end_idx + 1, len(sheet_data))):
        row = sheet_data[i]
        if not row or len(row) < 4:
            continue
            
        # Ищем даты в первой колонке
        if row[0] is not None:
            date_str = str(row[0])
            # Пробуем распарсить дату
            parsed_date = _parse_date(date_str)
            if parsed_date:
                dates.append(parsed_date)
    
    if len(dates) >= 2:
        # Рассчитываем разницу между первой и последней датой
        dates.sort()
        delta = dates[-1] - dates[0]
        return max(1, delta.days)  # Минимум 1 день
    
    # По умолчанию 7 дней
    return 7

def _parse_date(date_str: str) -> datetime:
    """Парсит дату из строки."""
    if not date_str:
        return None
        
    # Пробуем различные форматы дат
    date_formats = [
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def _parse_alternative_format(sheet_data: List[List[Any]]) -> pd.DataFrame:
    """Парсит альтернативный формат данных."""
    # Ищем строки с данными по номенклатурам
    nomenclature_rows = []
    
    for i, row in enumerate(sheet_data):
        if not row or not row[0]:
            continue
            
        first_cell = str(row[0]).strip()
        # Используем улучшенную проверку для идентификации номенклатуры
        if _is_nomenclature_row(row, sheet_data, i):
            nomenclature_rows.append((i, row))
    
    # Создаем метрики для найденных номенклатур
    all_metrics = []
    
    for idx, row in nomenclature_rows:
        try:
            nomenclature_name = str(row[0]) if row[0] is not None else ""
            
            initial_balance = float(str(row[4]).replace(',', '.')) if len(row) > 4 and row[4] is not None else 0.0
            incoming = float(str(row[6]).replace(',', '.')) if len(row) > 6 and row[6] is not None else 0.0
            outgoing = float(str(row[7]).replace(',', '.')) if len(row) > 7 and row[7] is not None else 0.0
            final_balance = float(str(row[8]).replace(',', '.')) if len(row) > 8 and row[8] is not None else 0.0
            
            if initial_balance > 0 or incoming > 0 or outgoing > 0 or final_balance > 0:
                theoretical_balance = initial_balance + incoming - outgoing
                shrinkage = max(0, theoretical_balance - final_balance)
                
                metric = {
                    'Номенклатура': nomenclature_name,
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Теоретический_остаток': theoretical_balance,
                    'Усушка': shrinkage,
                    'Коэффициент_усушки': shrinkage / initial_balance if initial_balance > 0 else 0,
                    'Период_хранения_дней': 7,  # По умолчанию
                    'Количество_документов': 0
                }
                all_metrics.append(metric)
        except (ValueError, IndexError, TypeError):
            # Пропускаем строки с ошибками
            continue
    
    return pd.DataFrame(all_metrics) if all_metrics else pd.DataFrame()