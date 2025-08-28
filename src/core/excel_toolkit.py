#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дополнительные утилиты для работы с Excel файлами
"""

import pandas as pd
import os
import json
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
import numpy as np


class ExcelProcessor:
    """Класс для обработки Excel файлов."""
    
    def __init__(self, file_path: str):
        """
        Инициализация процессора Excel.
        
        Args:
            file_path: Путь к Excel файлу
        """
        self.file_path = file_path
        self.df = None
        self.sheet_names = []
        self.load_file()
    
    def load_file(self) -> None:
        """Загружает Excel файл."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        
        file_extension = Path(self.file_path).suffix.lower()
        
        try:
            if file_extension in ['.xlsx', '.xlsm']:
                # Для новых форматов Excel используем openpyxl для сохранения структуры
                excel_file = pd.ExcelFile(self.file_path, engine='openpyxl')
                self.sheet_names = excel_file.sheet_names
                # Загружаем все листы в словарь
                self.df = excel_file.parse(sheet_name=None, header=None, dtype=str)
                excel_file.close()
            elif file_extension == '.xls':
                # Для старых форматов Excel используем xlrd
                excel_file = pd.ExcelFile(self.file_path, engine='xlrd')
                self.sheet_names = excel_file.sheet_names
                # Загружаем все листы в словарь
                self.df = excel_file.parse(sheet_name=None, header=None, dtype=str)
                excel_file.close()
            else:
                # Для других форматов пытаемся загрузить стандартным способом
                self.df = pd.read_excel(self.file_path, header=None, dtype=str)
                self.sheet_names = [0] if isinstance(self.df, pd.DataFrame) else list(self.df.keys())
                
        except Exception as e:
            raise ValueError(f"Ошибка чтения Excel файла: {str(e)}")
    
    def get_shape(self) -> tuple:
        """Возвращает размеры DataFrame (строки, колонки)."""
        if isinstance(self.df, dict):
            # Если у нас несколько листов, возвращаем размеры первого
            first_sheet = list(self.df.keys())[0]
            return self.df[first_sheet].shape if self.df[first_sheet] is not None else (0, 0)
        return self.df.shape if self.df is not None else (0, 0)
    
    def get_cell_value(self, row: int, col: int, sheet_name: Optional[str] = None) -> Any:
        """
        Получает значение ячейки по координатам.
        
        Args:
            row: Номер строки (начиная с 0)
            col: Номер колонки (начиная с 0)
            sheet_name: Имя листа (если не указано, используется первый лист)
            
        Returns:
            Значение ячейки или None
        """
        try:
            df_to_use = self._get_sheet_df(sheet_name)
            if df_to_use is not None and 0 <= row < len(df_to_use) and 0 <= col < len(df_to_use.columns):
                return df_to_use.iloc[row, col]
        except Exception:
            pass
        return None
    
    def _get_sheet_df(self, sheet_name: Optional[str] = None):
        """Получает DataFrame для указанного листа."""
        if isinstance(self.df, dict):
            if sheet_name is None:
                # Если имя листа не указано, используем первый
                sheet_name = list(self.df.keys())[0]
            return self.df.get(sheet_name)
        return self.df
    
    def find_text(self, search_text: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Находит текст в файле.
        
        Args:
            search_text: Искомый текст
            case_sensitive: Учитывать регистр
            
        Returns:
            Список найденных позиций
        """
        results = []
        if self.df is None:
            return results
        
        search_term = search_text if case_sensitive else search_text.lower()
        
        # Обрабатываем все листы
        sheets_to_process = self.df.items() if isinstance(self.df, dict) else [(0, self.df)]
        
        for sheet_name, sheet_df in sheets_to_process:
            if sheet_df is None:
                continue
                
            for row_idx, row in sheet_df.iterrows():
                for col_idx, cell_value in enumerate(row):
                    if pd.notna(cell_value):
                        cell_text = str(cell_value)
                        if not case_sensitive:
                            cell_text = cell_text.lower()
                        
                        if search_term in cell_text:
                            results.append({
                                'sheet': sheet_name,
                                'row': row_idx,
                                'col': col_idx,
                                'value': str(row.iloc[col_idx]),
                                'sheet_position': f"R{row_idx+1}C{col_idx+1}"
                            })
        
        return results
    
    def get_row_data(self, row_index: int, sheet_name: Optional[str] = None) -> List[Any]:
        """
        Получает данные всей строки.
        
        Args:
            row_index: Индекс строки
            sheet_name: Имя листа (если не указано, используется первый лист)
            
        Returns:
            Список значений в строке
        """
        df_to_use = self._get_sheet_df(sheet_name)
        if df_to_use is not None and 0 <= row_index < len(df_to_use):
            return df_to_use.iloc[row_index].tolist()
        return []
    
    def get_column_data(self, col_index: int, sheet_name: Optional[str] = None) -> List[Any]:
        """
        Получает данные всей колонки.
        
        Args:
            col_index: Индекс колонки
            sheet_name: Имя листа (если не указано, используется первый лист)
            
        Returns:
            Список значений в колонке
        """
        df_to_use = self._get_sheet_df(sheet_name)
        if df_to_use is not None and 0 <= col_index < len(df_to_use.columns):
            return df_to_use.iloc[:, col_index].tolist()
        return []
    
    def filter_non_empty_rows(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Возвращает только непустые строки."""
        df_to_use = self._get_sheet_df(sheet_name)
        if df_to_use is not None:
            return df_to_use.dropna(how='all')
        return pd.DataFrame()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Возвращает сводку о данных."""
        if self.df is None:
            return {'error': 'Данные не загружены'}
        
        summary = {
            'total_sheets': len(self.sheet_names),
            'sheet_names': self.sheet_names,
            'sheets': {}
        }
        
        for sheet_name in self.sheet_names:
            sheet_df = self.df[sheet_name]
            total_rows, total_cols = sheet_df.shape
            non_empty_rows = sheet_df.dropna(how='all').shape[0]
            
            # Анализ заполненности колонок
            col_fill_stats = {}
            for col_idx in range(total_cols):
                filled = sheet_df.iloc[:, col_idx].count()
                col_fill_stats[f'col_{col_idx}'] = {
                    'filled': filled,
                    'percentage': round((filled / total_rows) * 100, 1) if total_rows > 0 else 0
                }
            
            summary['sheets'][sheet_name] = {
                'total_rows': total_rows,
                'total_columns': total_cols,
                'non_empty_rows': non_empty_rows,
                'fill_rate': round((non_empty_rows / total_rows) * 100, 1) if total_rows > 0 else 0,
                'column_stats': col_fill_stats
            }
        
        return summary
    
    def export_to_csv(self, output_path: str, encoding: str = 'utf-8') -> bool:
        """
        Экспортирует данные в CSV.
        
        Args:
            output_path: Путь для сохранения CSV
            encoding: Кодировка файла
            
        Returns:
            True если успешно
        """
        try:
            if self.df is not None:
                # Создаем директорию если не существует
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                self.df.to_csv(output_path, index=False, encoding=encoding)
                return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
        return False
    
    def export_to_json(self, output_path: str, preserve_hierarchy: bool = True) -> bool:
        """
        Экспортирует данные в JSON формат с сохранением иерархии.
        
        Args:
            output_path: Путь для сохранения JSON
            preserve_hierarchy: Сохранять иерархию листов Excel
            
        Returns:
            True если успешно
        """
        try:
            if self.df is not None:
                # Создаем директорию если не существует
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                json_data = {}
                
                if isinstance(self.df, dict) and preserve_hierarchy:
                    # Сохраняем структуру с несколькими листами
                    json_data['sheets'] = {}
                    for sheet_name, sheet_df in self.df.items():
                        if sheet_df is not None:
                            # Преобразуем DataFrame в список словарей
                            json_data['sheets'][sheet_name] = sheet_df.where(pd.notnull(sheet_df), None).to_dict('records')
                else:
                    # Сохраняем как один лист
                    df_to_use = list(self.df.values())[0] if isinstance(self.df, dict) else self.df
                    json_data = df_to_use.where(pd.notnull(df_to_use), None).to_dict('records')
                
                # Сохраняем в файл
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
                
                return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
        return False
    
    def to_hierarchical_dict(self) -> Dict[str, Any]:
        """
        Преобразует данные в иерархический словарь с сохранением структуры Excel.
        
        Returns:
            Иерархический словарь с данными
        """
        if self.df is None:
            return {}
        
        if isinstance(self.df, dict):
            # Если у нас несколько листов
            result = {}
            for sheet_name, sheet_df in self.df.items():
                if sheet_df is not None:
                    # Преобразуем в матрицу значений
                    result[sheet_name] = sheet_df.where(pd.notnull(sheet_df), None).values.tolist()
            return result
        else:
            # Если у нас один лист
            return self.df.where(pd.notnull(self.df), None).values.tolist()


def batch_process_excel_files(directory: str, pattern: str = "*.xls*") -> List[Dict[str, Any]]:
    """
    Обрабатывает несколько Excel файлов в директории.
    
    Args:
        directory: Путь к директории
        pattern: Шаблон для поиска файлов
        
    Returns:
        Список информации о файлах
    """
    results = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return [{'error': f'Директория не найдена: {directory}'}]
    
    excel_files = list(directory_path.glob(pattern))
    
    for file_path in excel_files:
        try:
            processor = ExcelProcessor(str(file_path))
            summary = processor.get_data_summary()
            
            file_info = {
                'filename': file_path.name,
                'filepath': str(file_path),
                'size_kb': round(file_path.stat().st_size / 1024, 1),
                'summary': summary
            }
            
            results.append(file_info)
            
        except Exception as e:
            results.append({
                'filename': file_path.name,
                'filepath': str(file_path),
                'error': str(e)
            })
    
    return results


def compare_excel_files(file1_path: str, file2_path: str) -> Dict[str, Any]:
    """
    Сравнивает два Excel файла.
    
    Args:
        file1_path: Путь к первому файлу
        file2_path: Путь к второму файлу
        
    Returns:
        Результат сравнения
    """
    try:
        proc1 = ExcelProcessor(file1_path)
        proc2 = ExcelProcessor(file2_path)
        
        shape1 = proc1.get_shape()
        shape2 = proc2.get_shape()
        
        summary1 = proc1.get_data_summary()
        summary2 = proc2.get_data_summary()
        
        return {
            'file1': {
                'name': os.path.basename(file1_path),
                'shape': shape1,
                'summary': summary1
            },
            'file2': {
                'name': os.path.basename(file2_path),
                'shape': shape2,
                'summary': summary2
            },
            'comparison': {
                'same_dimensions': shape1 == shape2,
                'rows_diff': shape2[0] - shape1[0],
                'cols_diff': shape2[1] - shape1[1]
            }
        }
        
    except Exception as e:
        return {'error': str(e)}


def extract_text_content(file_path: str, min_length: int = 3) -> List[str]:
    """
    Извлекает текстовое содержимое из Excel файла.
    
    Args:
        file_path: Путь к Excel файлу
        min_length: Минимальная длина текста для включения
        
    Returns:
        Список уникальных текстовых значений
    """
    try:
        processor = ExcelProcessor(file_path)
        
        if processor.df is None:
            return []
        
        # Собираем все текстовые значения
        text_values = set()
        
        # Обрабатываем все листы
        sheets_to_process = processor.df.items() if isinstance(processor.df, dict) else [(0, processor.df)]
        
        for sheet_name, sheet_df in sheets_to_process:
            if sheet_df is None:
                continue
                
            for row_idx, row in sheet_df.iterrows():
                for cell_value in row:
                    if pd.notna(cell_value):
                        text_val = str(cell_value).strip()
                        if len(text_val) >= min_length:
                            text_values.add(text_val)
        
        return sorted(list(text_values))
        
    except Exception as e:
        print(f"Ошибка извлечения текста: {e}")
        return []


def json_to_excel(json_path: str, output_excel_path: str, engine: str = 'openpyxl') -> bool:
    """
    Преобразует JSON файл обратно в Excel.
    
    Args:
        json_path: Путь к JSON файлу
        output_excel_path: Путь для сохранения Excel файла
        engine: Движок для записи Excel (openpyxl или xlsxwriter)
        
    Returns:
        True если успешно
    """
    try:
        # Читаем JSON файл
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
        
        # Проверяем структуру JSON
        if 'sheets' in json_data:
            # Много листов
            with pd.ExcelWriter(output_excel_path, engine=engine) as writer:
                for sheet_name, sheet_data in json_data['sheets'].items():
                    if sheet_data:
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Один лист
            df = pd.DataFrame(json_data)
            df.to_excel(output_excel_path, index=False, engine=engine)
        
        return True
    except Exception as e:
        print(f"Ошибка преобразования JSON в Excel: {e}")
        return False


# Пример использования
if __name__ == "__main__":
    print("🔧 Утилиты для работы с Excel файлами")
    print("=" * 50)
    
    # Поиск Excel файлов в текущей директории
    current_dir = os.getcwd()
    files_info = batch_process_excel_files(current_dir)
    
    print(f"Найдено файлов: {len(files_info)}")
    
    for info in files_info[:3]:  # Показываем первые 3 файла
        if 'error' in info:
            print(f"❌ {info.get('filename', 'Неизвестный файл')}: {info['error']}")
        else:
            print(f"✅ {info['filename']}")
            print(f"   Размер: {info['size_kb']} КБ")
            summary = info['summary']
            print(f"   Листов: {summary['total_sheets']}")
            print(f"   Имена листов: {', '.join(summary['sheet_names'][:3])}...")
