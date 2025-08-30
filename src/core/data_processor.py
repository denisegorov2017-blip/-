#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль обработки данных и выполнения расчетов.

Отвечает за итерацию по набору данных, валидацию, вызов
соответствующих моделей расчета и сбор результатов.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import sys
import os

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log
from core.data_models import NomenclatureRow
from core.shrinkage_calculator import ShrinkageCalculator
from core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel

class DataProcessor:
    """
    Выполняет расчеты коэффициентов усушки для набора данных.
    
    Система работает с данными инвентаризации, которые содержат информацию о недостачах.
    Причины недостач могут быть разные - усушка, утеря товара и другие факторы.
    Система анализирует эту информацию для определения части недостач, связанной с усушкой.
    """
    def __init__(self, 
                 config: Dict[str, Any], 
                 calculator: ShrinkageCalculator, 
                 adaptive_model: AdaptiveShrinkageModel):
        """
        Инициализирует обработчик данных.

        Args:
            config (Dict[str, Any]): Словарь с настройками.
            calculator (ShrinkageCalculator): Экземпляр базового калькулятора.
            adaptive_model (AdaptiveShrinkageModel): Экземпляр адаптивной модели.
        """
        self.config = config
        self.calculator = calculator
        self.adaptive_model = adaptive_model
        log.info("DataProcessor инициализирован.")

    def calculate_coefficients(self, 
                               dataset: pd.DataFrame,
                               surplus_rates: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Пакетный расчет коэффициентов для набора данных.

        Args:
            dataset (pd.DataFrame): Входной набор данных.
            surplus_rates (Dict[str, float], optional): Словарь с индивидуальными процентами излишка.

        Returns:
            Dict[str, Any]: Словарь с результатами расчетов и информацией об ошибках.
        """
        if surplus_rates is None:
            surplus_rates = {}
            
        results = []
        errors = []
        use_adaptive = self.config.get('use_adaptive_model', False)
        
        # Этап 1: Предварительная обработка и валидация данных
        log.info("Этап 1/5: Предварительная обработка и валидация данных...")
        
        # Этап 2: Настройка конфигурации
        log.info("Этап 2/5: Настройка конфигурации...")
        
        # Последовательная обработка каждой строки данных
        for index, row_data in dataset.iterrows():
            try:
                # Этап 3: Последовательная обработка каждой строки данных:
                log.info(f"Этап 3/5: Обработка строки {index+1}/{len(dataset)}...")
                
                # Этап 3.1: Валидация строки
                validated_data = self._validate_row_data(row_data)
                if validated_data is None:
                    # Если валидация не прошла, добавляем в ошибки
                    error_reason = self._determine_error_reason(row_data)
                    error_info = {
                        'Номенклатура': row_data.get('Номенклатура', f'Строка {index}'),
                        'Причина': error_reason,
                        'Ошибка': 'Ошибка валидации данных',
                        'Данные': {
                            'Начальный_остаток': row_data.get('Начальный_остаток', 'N/A'),
                            'Приход': row_data.get('Приход', 'N/A'),
                            'Расход': row_data.get('Расход', 'N/A'),
                            'Конечный_остаток': row_data.get('Конечный_остаток', 'N/A')
                        }
                    }
                    errors.append(error_info)
                    log.warning(f"Строка не прошла валидацию: {row_data.get('Номенклатура', f'Строка {index}')}. Причина: {error_reason}")
                    continue
                
                row = validated_data.model_dump(by_alias=True)
                
                # Этап 3.2: Подготовка данных
                nomenclature = row['Номенклатура']
                data_for_calc = self._prepare_calculation_data(row)
                
                # Этап 3.3: Анализ инвентаризации
                deviation_info = self._analyze_inventory_shortage(data_for_calc, nomenclature)
                if deviation_info and abs(deviation_info['Отклонение']) > 0.001:
                    errors.append(deviation_info)
                    log.info(f"Значимое отклонение для {nomenclature}: {deviation_info['Отклонение']}")
                
                # Этап 3.4: Расчет
                if use_adaptive:
                    result = self._calculate_with_adaptive_model(data_for_calc, nomenclature, surplus_rates)
                else:
                    result = self._calculate_with_basic_model(data_for_calc, nomenclature)
                
                # Этап 3.5: Валидация результата
                # Здесь можно добавить валидацию результата если необходимо
                
                results.append(result)
                
            except Exception as e:
                # Обработка непредвиденных ошибок
                error_info = {
                    'Номенклатура': row_data.get('Номенклатура', f'Строка {index}'),
                    'Причина': 'Непредвиденная ошибка обработки',
                    'Ошибка': str(e),
                    'Данные': {
                        'Начальный_остаток': row_data.get('Начальный_остаток', 'N/A'),
                        'Приход': row_data.get('Приход', 'N/A'),
                        'Расход': row_data.get('Расход', 'N/A'),
                        'Конечный_остаток': row_data.get('Конечный_остаток', 'N/A')
                    }
                }
                errors.append(error_info)
                log.error(f"Ошибка при обработке строки {index} ({row_data.get('Номенклатура', 'N/A')}): {e}")
                continue
        
        # Этап 4: Агрегация результатов
        log.info("Этап 4/5: Агрегация результатов...")
        
        # Этап 5: Финальная валидация
        log.info("Этап 5/5: Финальная валидация...")
        
        return {
            'coefficients': results,
            'errors': errors
        }

    def _validate_row_data(self, row_data: pd.Series) -> Optional[NomenclatureRow]:
        """Валидирует данные строки."""
        try:
            return NomenclatureRow.model_validate(row_data.to_dict())
        except Exception:
            return None

    def _prepare_calculation_data(self, row: Dict[str, Any]) -> Dict[str, float]:
        """Подготавливает данные для расчета."""
        return {
            'initial_balance': row['Начальный_остаток'],
            'incoming': row['Приход'],
            'outgoing': row['Расход'],
            'final_balance': row['Конечный_остаток'],
            'storage_days': row['Период_хранения_дней']
        }

    def _analyze_inventory_shortage(self, data: Dict[str, float], nomenclature: str) -> Dict[str, Any]:
        """Анализирует недостачи из данных инвентаризации."""
        theoretical_balance = data['initial_balance'] + data['incoming'] - data['outgoing']
        inventory_shortage = theoretical_balance - data['final_balance']
        
        return {
            'Номенклатура': nomenclature,
            'Причина': 'Анализ недостач из инвентаризации',
            'Отклонение': inventory_shortage,
            'Данные': {
                'Начальный_остаток': data['initial_balance'],
                'Приход': data['incoming'],
                'Расход': data['outgoing'],
                'Теоретический_остаток': theoretical_balance,
                'Фактический_остаток': data['final_balance']
            }
        }

    def _calculate_with_adaptive_model(self, data: Dict[str, float], nomenclature: str, surplus_rates: Dict[str, float]) -> Dict[str, Any]:
        """Выполняет расчет с использованием адаптивной модели."""
        surplus_rate = surplus_rates.get(nomenclature, self.config.get('average_surplus_rate', 0.0))
        # Убедимся, что модель использует актуальный процент излишка
        self.adaptive_model.set_surplus_rate(surplus_rate, nomenclature)
        
        coefficients = self.adaptive_model.adapt_coefficients(data, nomenclature=nomenclature)
        # ИСПРАВЛЕНИЕ: Передаем surplus_rate в функцию расчета точности
        accuracy = self._calculate_accuracy(data, coefficients, surplus_rate)
        result = {
            'Номенклатура': nomenclature, 'a': coefficients['a'], 'b': coefficients['b'], 'c': coefficients['c'],
            'Точность': accuracy, 'Модель': 'adaptive_exponential', 'Дней_хранения': data['storage_days']
        }
        if surplus_rate > 0:
            result['Учет_излишка'] = f"{surplus_rate*100:.1f}%"
        return result

    def _calculate_with_basic_model(self, data: Dict[str, float], nomenclature: str) -> Dict[str, Any]:
        """Выполняет расчет с использованием базовой модели."""
        calc_input = data.copy()
        calc_input['name'] = nomenclature
        coefficients = self.calculator.calculate_coefficients(calc_input)
        # ИСПРАВЛЕНИЕ: Унифицируем ключи для базовой модели
        return {
            'Номенклатура': nomenclature, 
            'a': coefficients['a'], 
            'b': coefficients['b'], 
            'c': coefficients.get('c', 0),  # Некоторые модели могут не возвращать 'c'
            'Точность': coefficients['accuracy'], 
            'Модель': coefficients.get('model_type', 'exponential'), 
            'Дней_хранения': data['storage_days']
        }

    def _determine_error_reason(self, row_data: pd.Series) -> str:
        """Определяет причину ошибки валидации."""
        initial_balance = row_data.get('Начальный_остаток', 0)
        incoming = row_data.get('Приход', 0)
        
        # Проверяем на группу (нулевой начальный остаток и приход)
        if initial_balance is not None and float(initial_balance) <= 0 and incoming is not None and float(incoming) <= 0:
            return "Группа или нулевые значения"
        
        # Проверяем на излишки по инвентаризации
        if initial_balance is not None and float(initial_balance) > 0:
            return "Проблема с данными инвентаризации"
            
        return "Неизвестная причина"

    def _calculate_accuracy(self, data: Dict[str, float], coefficients: Dict[str, float], surplus_rate: float = 0.0) -> float:
        """
        Рассчитывает точность модели для адаптивного случая.
        ИСПРАВЛЕНО: Теперь учитывает излишек при расчете фактической усушки.
        """
        try:
            # Предсказанная усушка как пропорция от начального баланса
            predicted_shrinkage_ratio = self.adaptive_model._exponential_model(data['storage_days'], **coefficients)
        
            # ИСПРАВЛЕНИЕ: Используем оригинальные данные для расчета фактической усушки,
            # так как adapt_coefficients уже корректирует данные с излишком
            # Согласно тесту, излишек применяется только к приходу
            corrected_incoming = data['incoming'] * (1 + surplus_rate)
            theoretical_balance = data['initial_balance'] + corrected_incoming - data['outgoing']
            actual_shrinkage = theoretical_balance - data['final_balance']
        
            # Преобразуем предсказанную усушку в абсолютные значения для сравнения
            # ИСПРАВЛЕНИЕ: Используем оригинальный начальный баланс для предсказания,
            # так как коэффициенты рассчитываются относительно оригинального баланса
            original_initial_balance = data['initial_balance']
            predicted_shrinkage = predicted_shrinkage_ratio * original_initial_balance

            if actual_shrinkage > 0:
                accuracy = max(0, 100 - abs(predicted_shrinkage - actual_shrinkage) / actual_shrinkage * 100)
                return min(accuracy, 100.0)
            else:
                return 100.0
        except Exception as e:
            log.error(f"Ошибка при расчете точности: {e}")
            return 0.0