#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Специализированный процессор для данных о партиях рыбы с датами прихода и инвентаризации.

Этот модуль предназначен для обработки специфического формата Excel файлов,
используемых в рыбной промышленности, где партии товаров отслеживаются
по дате прихода и инвентаризации.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
import sys
import os

# Добавляем путь к корню проекта для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.logger_config import log
from src.core.data_models import NomenclatureRow
from src.core.shrinkage_system import ShrinkageSystem


class FishBatchDataProcessor:
    """
    Специализированный процессор для обработки данных о партиях рыбы.
    
    Обрабатывает специфический формат Excel файлов с партиями товаров,
    где дата прихода и инвентаризации являются началом и концом отсчета.
    """
    
    def __init__(self):
        """Инициализирует процессор данных о партиях рыбы."""
        self.nomenclature_data = {}
        log.info("FishBatchDataProcessor инициализирован")
    
    def process_fish_batch_excel(self, file_path: str) -> pd.DataFrame:
        """
        Обрабатывает специфический формат Excel файла с партиями рыбы.
        
        Args:
            file_path (str): Путь к Excel файлу
            
        Returns:
            pd.DataFrame: Обработанные данные в формате, пригодном для расчета усушки
        """
        log.info(f"Начало обработки файла партий рыбы: {file_path}")
        
        try:
            # Читаем Excel файл без предположений о структуре
            df_raw = pd.read_excel(file_path, header=None)
            log.info(f"Файл загружен. Размер: {df_raw.shape}")
            
            # Извлекаем данные о партиях
            batch_data = self._extract_batch_data(df_raw)
            
            # Преобразуем в формат для расчета усушки
            shrinkage_data = self._convert_to_shrinkage_format(batch_data)
            
            # Создаем DataFrame
            df_result = pd.DataFrame(shrinkage_data)
            
            log.success(f"Обработка завершена. Извлечено {len(df_result)} записей")
            return df_result
            
        except Exception as e:
            log.error(f"Ошибка при обработке файла партий рыбы: {e}")
            raise
    
    def _extract_batch_data(self, df_raw: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Извлекает данные о партиях из неструктурированного DataFrame.
        
        Args:
            df_raw (pd.DataFrame): Исходный DataFrame с данными
            
        Returns:
            List[Dict[str, Any]]: Список словарей с данными о партиях
        """
        log.info("Извлечение данных о партиях...")
        
        batch_data = []
        current_nomenclature = None
        current_initial_balance = 0.0
        total_incoming = 0.0
        total_outgoing = 0.0
        current_final_balance = 0.0
        
        # Проходим по строкам, начиная с 11-й (где начинаются данные)
        for i in range(11, len(df_raw)):
            row = df_raw.iloc[i]
            
            # Пропускаем пустые строки
            if row.isna().all():
                continue
            
            # Получаем значение номенклатуры (первый столбец)
            nomenclature = row[0] if len(row) > 0 and not pd.isna(row[0]) else None
            
            if nomenclature is None:
                continue
                
            nomenclature_str = str(nomenclature).strip()
            
            # Пропускаем строки с документами
            if self._is_document_row(nomenclature_str):
                continue
            
            # Пропускаем строки с датами
            if self._is_date_row(nomenclature_str):
                continue
            
            # Если это новая номенклатура
            if self._is_product_row(nomenclature_str):
                # Сохраняем предыдущую номенклатуру, если есть данные
                if current_nomenclature and any([current_initial_balance, total_incoming, total_outgoing, current_final_balance]):
                    batch_data.append({
                        'nomenclature': current_nomenclature,
                        'initial_balance': current_initial_balance,
                        'incoming': total_incoming,
                        'outgoing': total_outgoing,
                        'final_balance': current_final_balance
                    })
                
                # Начинаем новую номенклатуру
                current_nomenclature = nomenclature_str
                current_initial_balance = 0.0
                total_incoming = 0.0
                total_outgoing = 0.0
                current_final_balance = 0.0
                
                # Извлекаем значения из соответствующих столбцов
                # Начальный остаток (столбец 4)
                if len(row) > 4 and not pd.isna(row[4]):
                    try:
                        current_initial_balance = float(row[4])
                    except (ValueError, TypeError):
                        pass
                
                # Приход (столбец 6)
                if len(row) > 6 and not pd.isna(row[6]):
                    try:
                        total_incoming = float(row[6])
                    except (ValueError, TypeError):
                        pass
                
                # Расход (столбец 7)
                if len(row) > 7 and not pd.isna(row[7]):
                    try:
                        total_outgoing = float(row[7])
                    except (ValueError, TypeError):
                        pass
                
                # Конечный остаток (столбец 8)
                if len(row) > 8 and not pd.isna(row[8]):
                    try:
                        current_final_balance = float(row[8])
                    except (ValueError, TypeError):
                        pass
            else:
                # Это может быть дополнительная информация о той же номенклатуре
                # Извлекаем дополнительные значения
                incoming_add = 0.0
                outgoing_add = 0.0
                final_add = 0.0
                
                # Приход (столбец 6)
                if len(row) > 6 and not pd.isna(row[6]):
                    try:
                        incoming_add = float(row[6])
                    except (ValueError, TypeError):
                        pass
                
                # Расход (столбец 7)
                if len(row) > 7 and not pd.isna(row[7]):
                    try:
                        outgoing_add = float(row[7])
                    except (ValueError, TypeError):
                        pass
                
                # Конечный остаток (столбец 8)
                if len(row) > 8 and not pd.isna(row[8]):
                    try:
                        final_add = float(row[8])
                    except (ValueError, TypeError):
                        pass
                
                # Добавляем к текущим значениям
                total_incoming += incoming_add
                total_outgoing += outgoing_add
                current_final_balance = max(current_final_balance, final_add)
        
        # Не забываем сохранить последнюю номенклатуру
        if current_nomenclature and any([current_initial_balance, total_incoming, total_outgoing, current_final_balance]):
            batch_data.append({
                'nomenclature': current_nomenclature,
                'initial_balance': current_initial_balance,
                'incoming': total_incoming,
                'outgoing': total_outgoing,
                'final_balance': current_final_balance
            })
        
        log.info(f"Извлечено {len(batch_data)} партий товаров")
        return batch_data
    
    def _is_document_row(self, text: str) -> bool:
        """
        Проверяет, является ли строка строкой документа.
        
        Args:
            text (str): Текст для проверки
            
        Returns:
            bool: True, если это строка документа
        """
        document_keywords = [
            'отчет', 'накладная', 'инвентаризация', 'приходная', 
            'документ', 'списание', 'перемещение'
        ]
        return any(keyword in text.lower() for keyword in document_keywords)
    
    def _is_date_row(self, text: str) -> bool:
        """
        Проверяет, является ли строка строкой с датой.
        
        Args:
            text (str): Текст для проверки
            
        Returns:
            bool: True, если это строка с датой
        """
        # Проверяем формат даты ДД.ММ.ГГГГ
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        return bool(re.match(date_pattern, text.strip()))
    
    def _is_product_row(self, text: str) -> bool:
        """
        Проверяет, является ли строка строкой с продуктом.
        
        Args:
            text (str): Текст для проверки
            
        Returns:
            bool: True, если это строка с продуктом
        """
        # Исключаем строки с документами и датами
        if self._is_document_row(text) or self._is_date_row(text):
            return False
        
        # Строка с продуктом должна содержать буквы и не быть пустой
        return bool(re.search(r'[а-яА-Яa-zA-Z]', text))
    
    def _convert_to_shrinkage_format(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Преобразует данные о партиях в формат для расчета усушки.
        
        Args:
            batch_data (List[Dict[str, Any]]): Данные о партиях
            
        Returns:
            List[Dict[str, Any]]: Данные в формате для расчета усушки
        """
        log.info("Преобразование данных в формат для расчета усушки...")
        
        shrinkage_data = []
        
        for batch in batch_data:
            # Проверяем, что данные валидны
            if batch['initial_balance'] <= 0 and batch['incoming'] <= 0:
                continue
            
            shrinkage_record = {
                'Номенклатура': batch['nomenclature'],
                'Начальный_остаток': batch['initial_balance'],
                'Приход': batch['incoming'],
                'Расход': batch['outgoing'],
                'Конечный_остаток': batch['final_balance'],
                'Период_хранения_дней': 7  # По умолчанию 7 дней
            }
            
            shrinkage_data.append(shrinkage_record)
        
        log.info(f"Преобразовано {len(shrinkage_data)} записей для расчета усушки")
        return shrinkage_data
    
    def calculate_shrinkage_for_batches(self, file_path: str, use_adaptive: bool = True) -> Dict[str, Any]:
        """
        Выполняет полный расчет усушки для партий товаров.
        
        Args:
            file_path (str): Путь к Excel файлу
            use_adaptive (bool): Использовать адаптивную модель
            
        Returns:
            Dict[str, Any]: Результаты расчета усушки
        """
        log.info(f"Начало расчета усушки для партий товаров из файла: {file_path}")
        
        try:
            # Обрабатываем данные
            df_shrinkage = self.process_fish_batch_excel(file_path)
            
            if df_shrinkage.empty:
                return {
                    'status': 'error',
                    'message': 'Не удалось извлечь данные для расчета усушки'
                }
            
            # Инициализируем систему расчета усушки
            system = ShrinkageSystem()
            
            # Выполняем расчет
            results = system.process_dataset(
                df_shrinkage, 
                file_path.split('/')[-1], 
                use_adaptive=use_adaptive
            )
            
            log.success("Расчет усушки для партий товаров завершен")
            return results
            
        except Exception as e:
            log.error(f"Ошибка при расчете усушки для партий товаров: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка при расчете усушки: {str(e)}'
            }


def main():
    """Демонстрация работы специализированного процессора."""
    print("🐟 Специализированный процессор данных о партиях рыбы")
    print("=" * 60)
    
    # Создаем процессор
    processor = FishBatchDataProcessor()
    
    # Путь к файлу с данными
    file_path = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    try:
        print(f"📂 Обработка файла: {file_path}")
        
        # Обрабатываем данные
        results = processor.calculate_shrinkage_for_batches(file_path, use_adaptive=True)
        
        if results['status'] == 'success':
            print("✅ Расчет выполнен успешно!")
            print(f"📊 Обработано записей: {len(results['coefficients'])}")
            print(f"❌ Ошибок: {len(results['errors'])}")
            print(f"📈 Средняя точность: {results['summary']['avg_accuracy']:.2f}%")
            
            # Показываем несколько примеров
            print("\n📋 Примеры результатов:")
            for i, coeff in enumerate(results['coefficients'][:5]):
                print(f"   {coeff['Номенклатура']}:")
                print(f"     a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}")
                print(f"     Точность: {coeff['Точность']:.2f}%")
                
            # Показываем информацию об ошибках
            if results['errors']:
                print("\n❌ Примеры ошибок:")
                for i, error in enumerate(results['errors'][:5]):
                    print(f"   {error['Номенклатура']}:")
                    print(f"     Причина: {error['Причина']}")
                    if 'Отклонение' in error:
                        print(f"     Отклонение: {error['Отклонение']:.3f}")
        else:
            print(f"❌ Ошибка: {results['message']}")
            
    except Exception as e:
        print(f"❌ Ошибка при обработке: {e}")


if __name__ == "__main__":
    main()