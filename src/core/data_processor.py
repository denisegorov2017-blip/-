#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль обработки данных и выполнения расчетов.

Отвечает за итерацию по набору данных, валидацию, вызов
соответствующих моделей расчета и сбор результатов.
"""

import pandas as pd
from typing import Dict, List, Any, Optional

from logger_config import log
from core.data_models import NomenclatureRow
from core.shrinkage_calculator import ShrinkageCalculator
from core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel

class DataProcessor:
    """
    Выполняет расчеты коэффициентов усушки для набора данных.
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
        
        for _, row_data in dataset.iterrows():
            try:
                validated_data = NomenclatureRow.model_validate(row_data.to_dict())
                row = validated_data.model_dump(by_alias=True)
            except Exception as e:
                # Определяем причину ошибки
                error_reason = self._determine_error_reason(row_data)
                error_info = {
                    'Номенклатура': row_data.get('Номенклатура', 'N/A'),
                    'Причина': error_reason,
                    'Ошибка': str(e),
                    'Данные': {
                        'Начальный_остаток': row_data.get('Начальный_остаток', 'N/A'),
                        'Приход': row_data.get('Приход', 'N/A'),
                        'Расход': row_data.get('Расход', 'N/A'),
                        'Конечный_остаток': row_data.get('Конечный_остаток', 'N/A')
                    }
                }
                errors.append(error_info)
                log.warning(f"Строка не прошла валидацию: {row_data.get('Номенклатура', 'N/A')}. Причина: {error_reason}. Ошибка: {e}")
                continue

            nomenclature = row['Номенклатура']
            data_for_calc = {
                'initial_balance': row['Начальный_остаток'],
                'incoming': row['Приход'],
                'outgoing': row['Расход'],
                'final_balance': row['Конечный_остаток'],
                'storage_days': row['Период_хранения_дней']
            }

            # Проверяем на нулевую усушку
            theoretical_balance = data_for_calc['initial_balance'] + data_for_calc['incoming'] - data_for_calc['outgoing']
            actual_shrinkage = theoretical_balance - data_for_calc['final_balance']
            
            # Добавляем информацию об отклонении для всех записей, но помечаем как ошибку только значимые отклонения
            deviation_info = {
                'Номенклатура': nomenclature,
                'Причина': 'Нулевая усушка',
                'Отклонение': actual_shrinkage,
                'Данные': {
                    'Начальный_остаток': data_for_calc['initial_balance'],
                    'Приход': data_for_calc['incoming'],
                    'Расход': data_for_calc['outgoing'],
                    'Теоретический_остаток': theoretical_balance,
                    'Фактический_остаток': data_for_calc['final_balance']
                }
            }
            
            # Помечаем как ошибку только значимые отклонения (больше 0.001 по модулю)
            if abs(actual_shrinkage) > 0.001:
                errors.append(deviation_info)
                log.info(f"Значимое отклонение для {nomenclature}: {actual_shrinkage}")
            # else:
            #     log.info(f"Нулевая усушка для {nomenclature}: отклонение {actual_shrinkage}")

            if use_adaptive:
                surplus_rate = surplus_rates.get(nomenclature, self.config.get('average_surplus_rate', 0.0))
                # Убедимся, что модель использует актуальный процент излишка
                self.adaptive_model.set_surplus_rate(surplus_rate, nomenclature)
                
                coefficients = self.adaptive_model.adapt_coefficients(data_for_calc, nomenclature=nomenclature)
                # ИСПРАВЛЕНИЕ: Передаем surplus_rate в функцию расчета точности
                accuracy = self._calculate_accuracy(data_for_calc, coefficients, surplus_rate)
                result = {
                    'Номенклатура': nomenclature, 'a': coefficients['a'], 'b': coefficients['b'], 'c': coefficients['c'],
                    'Точность': accuracy, 'Модель': 'adaptive_exponential', 'Дней_хранения': data_for_calc['storage_days']
                }
                if surplus_rate > 0:
                    result['Учет_излишка'] = f"{surplus_rate*100:.1f}%"
            else:
                calc_input = data_for_calc.copy()
                calc_input['name'] = nomenclature
                coefficients = self.calculator.calculate_coefficients(calc_input)
                # ИСПРАВЛЕНИЕ: Унифицируем ключи для базовой модели
                result = {
                    'Номенклатура': nomenclature, 
                    'a': coefficients['a'], 
                    'b': coefficients['b'], 
                    'c': coefficients.get('c', 0),  # Некоторые модели могут не возвращать 'c'
                    'Точность': coefficients['accuracy'], 
                    'Модель': coefficients.get('model_type', 'exponential'), 
                    'Дней_хранения': data_for_calc['storage_days']
                }
            results.append(result)
        
        return {
            'coefficients': results,
            'errors': errors
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