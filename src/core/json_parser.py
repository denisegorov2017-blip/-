#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер JSON. Отвечает за преобразование структурированного JSON-файла в чистый DataFrame.
"""

import json
import pandas as pd
from pydantic import ValidationError
from .data_models_json import JsonDataModel

def parse_from_json(json_path: str) -> pd.DataFrame:
    """
    Генерирует датасет для расчета коэффициентов из JSON-файла.
    
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
            return _parse_new_format(data)
        else:
            # Старый формат - используем валидацию
            validated_data = JsonDataModel.model_validate(data)
            return _parse_old_format(validated_data)
    except FileNotFoundError:
        raise ValueError(f"Файл не найден: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Ошибка декодирования JSON: {json_path}")
    except ValidationError as e:
        raise ValueError(f"Ошибка валидации данных в файле {json_path}: {e}")

def _parse_new_format(data):
    """Парсит новый формат JSON файла."""
    # For simplicity, we'll assume the data is in the first sheet
    sheet_name = list(data["sheets"].keys())[0]
    sheet_data = data["sheets"][sheet_name]

    structural_config = {
        'nomenclature_patterns': [
            'ВЯЛЕНЫЙ', 'ВЯЛЕНАЯ', 'Г/К', 'Х/К', 'КОПЧЕНЫЙ', 'КОПЧЕНАЯ',
            'СУШЕНЫЙ', 'СУШЕНАЯ', 'ТУШКА', 'ФИЛЕ', 'СТЕЙК', 'С/С', 'СЛАБОСОЛ'
        ],
        'summary_keywords': ['ИТОГО', 'ВСЕГО', 'САЛЬДО', 'ОБЩИЙ ИТОГ'],
    }

    all_metrics = []
    nomenclature_rows = []

    # Find all nomenclature rows
    for i, row in enumerate(sheet_data):
        if not row or not row[0]:
            continue
        # Check if the first cell contains any of the nomenclature patterns
        if any(p in str(row[0]) for p in structural_config['nomenclature_patterns']):
            # Check if it's likely a nomenclature row (e.g., second cell is empty)
            if len(row) > 1 and (row[1] is None or str(row[1]).strip() == ""):
                nomenclature_rows.append({'index': i, 'name': row[0]})

    # Process each nomenclature section
    for i, nom_row in enumerate(nomenclature_rows):
        start_idx = nom_row['index']
        end_idx = nomenclature_rows[i + 1]['index'] if i + 1 < len(nomenclature_rows) else len(sheet_data)
        section = sheet_data[start_idx:end_idx]

        # Find the summary row in the section
        summary_row = None
        for row in reversed(section):
            if row and row[0] and any(k in str(row[0]) for k in structural_config['summary_keywords']):
                summary_row = row
                break
        
        if not summary_row:
            summary_row = section[-1] # Assume last row is summary if no keyword found

        # Extract metrics from summary row (assuming fixed column positions)
        try:
            initial_balance = float(str(summary_row[4]).replace(',', '.')) if len(summary_row) > 4 and summary_row[4] is not None else 0.0
            incoming = float(str(summary_row[6]).replace(',', '.')) if len(summary_row) > 6 and summary_row[6] is not None else 0.0
            outgoing = float(str(summary_row[7]).replace(',', '.')) if len(summary_row) > 7 and summary_row[7] is not None else 0.0
            final_balance = float(str(summary_row[8]).replace(',', '.')) if len(summary_row) > 8 and summary_row[8] is not None else 0.0

            if initial_balance > 0:
                # Документы инвентаризации содержат информацию о недостачах
                # Система анализирует эту информацию для определения части, связанной с усушкой
                theoretical_balance = initial_balance + incoming - outgoing
                inventory_shortage = theoretical_balance - final_balance
                storage_days = 7  # Simplified, as in the original parser

                # Всегда добавляем запись для анализа недостач
                metric = {
                    'Номенклатура': nom_row['name'],
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Теоретический_остаток': theoretical_balance,
                    'Недостача_по_инвентаризации': inventory_shortage,
                    'Коэффициент_недостачи': inventory_shortage / initial_balance,
                    'Период_хранения_дней': storage_days,
                    'Количество_документов': 0  # Simplified
                }
                all_metrics.append(metric)
        except (ValueError, IndexError):
            # Skip rows that don't have the expected numeric data
            continue

    if not all_metrics:
        return pd.DataFrame()

    return pd.DataFrame(all_metrics)

def _parse_old_format(validated_data):
    """Парсит старый формат JSON файла."""
    # For simplicity, we'll assume the data is in the first sheet
    sheet_name = list(validated_data.sheets.keys())[0]
    sheet_data = validated_data.sheets[sheet_name]

    structural_config = {
        'nomenclature_patterns': [
            'ВЯЛЕНЫЙ', 'ВЯЛЕНАЯ', 'Г/К', 'Х/К', 'КОПЧЕНЫЙ', 'КОПЧЕНАЯ',
            'СУШЕНЫЙ', 'СУШЕНАЯ', 'ТУШКА', 'ФИЛЕ', 'СТЕЙК', 'С/С', 'СЛАБОСОЛ'
        ],
        'summary_keywords': ['ИТОГО', 'ВСЕГО', 'САЛЬДО', 'ОБЩИЙ ИТОГ'],
    }

    all_metrics = []
    nomenclature_rows = []

    # Find all nomenclature rows
    for i, row in enumerate(sheet_data):
        if not row or not row[0]:
            continue
        # Check if the first cell contains any of the nomenclature patterns
        if any(p in str(row[0]) for p in structural_config['nomenclature_patterns']):
            # Check if it's likely a nomenclature row (e.g., second cell is empty)
            if len(row) > 1 and (row[1] is None or str(row[1]).strip() == ""):
                nomenclature_rows.append({'index': i, 'name': row[0]})

    # Process each nomenclature section
    for i, nom_row in enumerate(nomenclature_rows):
        start_idx = nom_row['index']
        end_idx = nomenclature_rows[i + 1]['index'] if i + 1 < len(nomenclature_rows) else len(sheet_data)
        section = sheet_data[start_idx:end_idx]

        # Find the summary row in the section
        summary_row = None
        for row in reversed(section):
            if row and row[0] and any(k in str(row[0]) for k in structural_config['summary_keywords']):
                summary_row = row
                break
        
        if not summary_row:
            summary_row = section[-1] # Assume last row is summary if no keyword found

        # Extract metrics from summary row (assuming fixed column positions)
        try:
            initial_balance = float(str(summary_row[4]).replace(',', '.')) if len(summary_row) > 4 and summary_row[4] is not None else 0.0
            incoming = float(str(summary_row[6]).replace(',', '.')) if len(summary_row) > 6 and summary_row[6] is not None else 0.0
            outgoing = float(str(summary_row[7]).replace(',', '.')) if len(summary_row) > 7 and summary_row[7] is not None else 0.0
            final_balance = float(str(summary_row[8]).replace(',', '.')) if len(summary_row) > 8 and summary_row[8] is not None else 0.0

            if initial_balance > 0:
                # Документы инвентаризации содержат информацию о недостачах
                # Система анализирует эту информацию для определения части, связанной с усушкой
                theoretical_balance = initial_balance + incoming - outgoing
                inventory_shortage = theoretical_balance - final_balance
                storage_days = 7  # Simplified, as in the original parser

                # Всегда добавляем запись для анализа недостач
                metric = {
                    'Номенклатура': nom_row['name'],
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Теоретический_остаток': theoretical_balance,
                    'Недостача_по_инвентаризации': inventory_shortage,
                    'Коэффициент_недостачи': inventory_shortage / initial_balance,
                    'Период_хранения_дней': storage_days,
                    'Количество_документов': 0  # Simplified
                }
                all_metrics.append(metric)
        except (ValueError, IndexError):
            # Skip rows that don't have the expected numeric data
            continue

    if not all_metrics:
        return pd.DataFrame()

    return pd.DataFrame(all_metrics)