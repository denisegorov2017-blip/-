#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ядро-оркестратор системы. Отвечает за координацию компонентов.

Принимает DataFrame -> Координирует DataProcessor и ReportGenerator -> Возвращает результаты.
См. GEMINI_SELF_GUIDE.md для описания полной архитектуры.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import sys
import os

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Imports that work for both relative and direct execution
from logger_config import log
from config import DEFAULT_CONFIG
from core.shrinkage_calculator import ShrinkageCalculator
from core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel, BatchAdaptiveModel
from core.data_processor import DataProcessor
from core.reporting import ReportGenerator


class ShrinkageSystem:
    """
    Главный класс-оркестратор системы расчета коэффициентов усушки.
    Координирует работу процессора данных и генератора отчетов.
    """
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        """
        Инициализирует систему.
        
        Args:
            custom_config (Optional[Dict[str, Any]]): Пользовательская конфигурация, 
                                                     которая переопределит значения по умолчанию.
        """
        # 1. Конфигурация
        self.config = DEFAULT_CONFIG.copy()
        if custom_config:
            self.config.update(custom_config)
        
        # 2. Инициализация моделей и калькуляторов (зависимости для DataProcessor)
        self.calculator = ShrinkageCalculator()
        self.adaptive_model = AdaptiveShrinkageModel()
        # self.batch_model = BatchAdaptiveModel() # Пока не используется в новой структуре, можно отключить

        # 3. Инициализация основных компонентов
        self.data_processor = DataProcessor(self.config, self.calculator, self.adaptive_model)
        self.report_generator = ReportGenerator(self.config)
        
        # 4. Управление состоянием (остается здесь, т.к. это высокоуровневая логика)
        self.surplus_rates = {}  # {nomenclature: surplus_rate}
        self.set_surplus_rate(self.config.get('average_surplus_rate', 0.0)) # Установка глобального значения

        log.info("ShrinkageSystem (Оркестратор) инициализирована.")

    def set_surplus_rate(self, surplus_rate: float, nomenclature: Optional[str] = None):
        """Установка процента излишка при поступлении."""
        log.info(f"Установка процента излишка: {surplus_rate:.4f} для номенклатуры: {nomenclature or 'по умолчанию'}")
        if nomenclature is None:
            # Устанавливаем глобальное значение
            self.config['average_surplus_rate'] = surplus_rate
            self.adaptive_model.set_surplus_rate(surplus_rate)
        else:
            # Устанавливаем значение для конкретной номенклатуры
            self.surplus_rates[nomenclature] = surplus_rate
            self.adaptive_model.set_surplus_rate(surplus_rate, nomenclature)
    
    def get_surplus_rate(self, nomenclature: Optional[str] = None) -> float:
        """Получение процента излишка при поступлении."""
        if nomenclature is not None and nomenclature in self.surplus_rates:
            return self.surplus_rates[nomenclature]
        return self.config['average_surplus_rate']

    def process_dataset(self, 
                        dataset: pd.DataFrame, 
                        source_filename: str,
                        use_adaptive: bool = False) -> Dict[str, Any]:
        """
        Полная обработка набора данных: расчет + отчеты.
        
        Args:
            dataset (pd.DataFrame): Входной набор данных.
            source_filename (str): Имя исходного файла.
            use_adaptive (bool): Флаг использования адаптивной модели.

        Returns:
            Dict[str, Any]: Словарь с результатами обработки.
        """
        log.info(f"Начало обработки датасета из файла: {source_filename}")
        self.config['use_adaptive_model'] = use_adaptive
        
        if use_adaptive:
            log.info("Используется адаптивная модель расчета.")
        
        try:
            if dataset.empty:
                log.warning("Входной датасет пуст. Расчет невозможен.")
                return {'status': 'error', 'message': 'Входной датасет пуст'}

            # 1. Расчет коэффициентов
            log.info(f"Этап 1: Расчет коэффициентов для {len(dataset)} позиций...")
            processing_results = self.data_processor.calculate_coefficients(dataset, self.surplus_rates)
            coefficients_results = processing_results['coefficients']
            error_results = processing_results['errors']
            
            # 2. Генерация отчетов и сводки
            log.info("Этап 2: Генерация отчетов и сводки...")
            report_data = self.report_generator.generate(
                coefficients_results, 
                source_filename,
                errors=error_results
            )
            
            log.success(f"Обработка завершена. Средняя точность: {report_data['summary']['avg_accuracy']:.1f}%")
            
            return {
                'status': 'success',
                'coefficients': coefficients_results,
                'errors': error_results,
                'preliminary': [], # Заглушка, т.к. логика отключена
                'reports': report_data['reports'],
                'summary': report_data['summary'],
                'source_file': source_filename
            }
            
        except Exception as e:
            log.exception("Критическая ошибка в process_dataset (оркестратор)")
            return {'status': 'error', 'message': str(e)}