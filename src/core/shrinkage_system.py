#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ядро-оркестратор системы. Отвечает за координациюку компонентов.

Принимает DataFrame -> Координирует DataProcessor и ReportGenerator -> Возвращает результаты.
См. GEMINI_SELF_GUIDE.md для описания полной архитектуры.

ВАЖНО: Система работает с данными инвентаризации, содержащими информацию о недостачах.
Система анализирует эти данные для определения части недостач, связанной с усушкой.
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
from core.user_interaction import UserInteraction

# Импортируем интеграцию с базой данных
try:
    from core.database.integration import save_calculation_results
    DATABASE_INTEGRATION_AVAILABLE = True
    log.info("Интеграция с базой данных доступна")
except ImportError as e:
    DATABASE_INTEGRATION_AVAILABLE = False
    log.warning(f"Интеграция с базой данных недоступна: {e}")

# Импортируем расширенный аналитический репортер
try:
    from core.advanced_analytics_reporter import AdvancedAnalyticsReporter
    ADVANCED_ANALYTICS_AVAILABLE = True
    log.info("Расширенная аналитика доступна")
except ImportError as e:
    ADVANCED_ANALYTICS_AVAILABLE = False
    log.warning(f"Расширенная аналитика недоступна: {e}")


class ShrinkageSystem:
    """
    Главный класс-оркестратор системы расчета коэфициентов усушки.
    Координирует работу процессора данных и генератора отчетов.
    
    Система работает с данными инвентаризации, которые содержат информацию о недостачах.
    Причины недостач могут быть разные - усушка, утеря товара и другие факторы.
    Система анализирует эту информацию для определения части недостач, связанной с усушкой.
    
    ВАЖНО: Система НЕ рассчитывает усушку по балансам, а анализирует уже имеющиеся 
    данные о недостачах из инвентаризаций.
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
        self.user_interaction = UserInteraction()  # Добавляем модуль взаимодействия с пользователем
        
        # 4. Инициализация расширенного аналитического репортера (если доступен)
        if ADVANCED_ANALYTICS_AVAILABLE:
            self.advanced_analytics_reporter = AdvancedAnalyticsReporter(self.config)
        else:
            self.advanced_analytics_reporter = None
        
        # 5. Управление состоянием (остается здесь, т.к. это высокоуровневая логика)
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

    def _check_inventory_availability(self, dataset: pd.DataFrame, source_filename: str) -> pd.DataFrame:
        """
        Проверяет наличие начальной и конечной инвентаризации в данных.
        Выводит предупреждение, если данные неполные.
        
        ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации.
        Конечный остаток берется на конец периода по датам инвентаризации.
        Это критически важно для правильного расчета периода хранения и коэффициентов усушки.
        
        Args:
            dataset (pd.DataFrame): Входной набор данных.
            source_filename (str): Имя исходного файла.
            
        Returns:
            pd.DataFrame: Обновленный набор данных с возможными изменениями остатков.
        """
        # Создаем копию датасета для возможных изменений
        updated_dataset = dataset.copy()
        
        # Список для хранения информации о номенклатурах с нулевыми начальными остатками
        zero_balance_items = []
        
        # Проверяем каждую номенклатуру в датасете
        for idx, row in updated_dataset.iterrows():
            nomenclature = row.get('Номенклатура', 'Неизвестная номенклатура')
            initial_balance = row.get('Начальный_остаток', None)
            final_balance = row.get('Конечный_остаток', None)
            
            # Функция для безопасного преобразования значения в число
            def safe_float_convert(value):
                if value is None or pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # Преобразуем значения в числа
            initial_balance_float = safe_float_convert(initial_balance)
            final_balance_float = safe_float_convert(final_balance)
            
            # Если начальный остаток отсутствует или равен 0, устанавливаем его равным нулю
            if initial_balance is None or pd.isna(initial_balance) or (isinstance(initial_balance, str) and initial_balance.strip() == ''):
                log.warning(f"Для номенклатуры '{nomenclature}' отсутствует начальная инвентаризация (на начало периода по датам). "
                           f"Устанавливаем начальный остаток равным 0. Файл: {source_filename}")
                updated_dataset.at[idx, 'Начальный_остаток'] = 0.0
                initial_balance_float = 0.0
                # Добавляем в список для отчета
                zero_balance_items.append({
                    'Номенклатура': nomenclature,
                    'Начальный_остаток': 0.0,
                    'Приход': row.get('Приход', 0.0),
                    'Расход': row.get('Расход', 0.0),
                    'Конечный_остаток': final_balance_float if final_balance is not None and not pd.isna(final_balance) else 'Отсутствует'
                })
            elif initial_balance_float == 0.0:
                # Добавляем в список для отчета номенклатуры с уже имеющимися нулевыми остатками
                zero_balance_items.append({
                    'Номенклатура': nomenclature,
                    'Начальный_остаток': initial_balance_float,
                    'Приход': row.get('Приход', 0.0),
                    'Расход': row.get('Расход', 0.0),
                    'Конечный_остаток': final_balance_float if final_balance is not None and not pd.isna(final_balance) else 'Отсутствует'
                })
            elif initial_balance_float < 0:
                log.warning(f"Для номенклатуры '{nomenclature}' начальная инвентаризация имеет отрицательное значение. "
                           f"Файл: {source_filename}")
            
            # Проверяем наличие конечного остатка (на конец периода по датам инвентаризации)
            if final_balance is None or pd.isna(final_balance) or (isinstance(final_balance, str) and final_balance.strip() == ''):
                log.warning(f"Для номенклатуры '{nomenclature}' отсутствует конечная инвентаризация (на конец периода по датам). "
                           f"Файл: {source_filename}")
            elif final_balance_float < 0:
                log.warning(f"Для номенклатуры '{nomenclature}' конечная инвентаризация имеет отрицательное значение. "
                           f"Файл: {source_filename}")
            
            # Если оба значения отсутствуют, выводим более сильное предупреждение
            if (initial_balance_float == 0.0 and 
                (final_balance is None or pd.isna(final_balance) or (isinstance(final_balance, str) and final_balance.strip() == ''))):
                log.warning(f"Для номенклатуры '{nomenclature}' отсутствует конечная инвентаризация. "
                           f"Расчет коэффициентов усушки может быть неточным. Файл: {source_filename}")
        
        # Если есть номенклатуры с нулевыми начальными остатками, выводим отчет
        if zero_balance_items:
            log.info("Отчет о номенклатурах с нулевыми начальными остатками для проверки пользователем:")
            log.info("Номенклатура | Нач. остаток | Приход | Расход | Кон. остаток")
            log.info("-" * 65)
            for item in zero_balance_items:
                log.info(f"{item['Номенклатура']:<15} | {item['Начальный_остаток']:<12} | {item['Приход']:<6} | {item['Расход']:<6} | {item['Конечный_остаток']}")
        
        return updated_dataset

    def process_dataset(self, 
                        dataset: pd.DataFrame, 
                        source_filename: str,
                        use_adaptive: bool = False) -> Dict[str, Any]:
        """
        Полная обработка набора данных: анализ недостач + расчет коэффициентов усушки + отчеты.
        
        Args:
            dataset (pd.DataFrame): Входной набор данных с информацией о недостачах из инвентаризации.
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
            # Этап 1: Проверка входных данных
            if dataset.empty:
                log.warning("Входной датасет пуст. Расчет невозможен.")
                return self._create_error_response('Входной датасет пуст')

            # Этап 2: Проверяем наличие начальной и конечной инвентаризации
            log.info("Этап 1/4: Проверка наличия инвентаризационных данных...")
            processed_dataset = self._check_inventory_availability(dataset, source_filename)
            
            # Этап 3: Расчет коэффициентов
            log.info(f"Этап 2/4: Расчет коэффициентов для {len(processed_dataset)} позиций...")
            processing_results = self.data_processor.calculate_coefficients(processed_dataset, self.surplus_rates)
            coefficients_results = processing_results['coefficients']
            error_results = processing_results['errors']
            
            # Этап 4: Сохраняем результаты в базу данных (если интеграция доступна)
            if DATABASE_INTEGRATION_AVAILABLE and self.config.get('enable_database', False):
                log.info("Этап 3/4: Сохранение результатов в базу данных...")
                try:
                    save_calculation_results(
                        source_filename=source_filename,
                        dataset=processed_dataset,
                        coefficients_results=coefficients_results,
                        error_results=error_results
                    )
                    log.success("Результаты успешно сохранены в базу данных")
                except Exception as e:
                    error_msg = f"Ошибка при сохранении результатов в базу данных: {e}"
                    log.error(error_msg)
                    error_results.append({
                        'Номенклатура': 'Система',
                        'Причина': 'Ошибка сохранения в БД',
                        'Ошибка': error_msg
                    })
            
            # Этап 5: Генерация отчетов и сводки
            log.info("Этап 4/4: Генерация отчетов и сводки...")
            try:
                report_data = self.report_generator.generate(
                    coefficients_results, 
                    source_filename,
                    errors=error_results
                )
            except Exception as e:
                error_msg = f"Ошибка при генерации отчетов: {e}"
                log.error(error_msg)
                return self._create_error_response(error_msg)
            
            # Этап 6: Генерация расширенных аналитических отчетов (если доступно)
            advanced_reports = {}
            if ADVANCED_ANALYTICS_AVAILABLE and self.config.get('enable_database', False):
                log.info("Генерация расширенных аналитических отчетов...")
                try:
                    advanced_reports = self.advanced_analytics_reporter.generate_comprehensive_analytics_report()
                    log.success("Расширенные аналитические отчеты успешно сгенерированы")
                except Exception as e:
                    error_msg = f"Ошибка при генерации расширенных аналитических отчетов: {e}"
                    log.error(error_msg)
                    error_results.append({
                        'Номенклатура': 'Система',
                        'Причина': 'Ошибка генерации аналитики',
                        'Ошибка': error_msg
                    })
            
            log.success(f"Обработка завершена. Средняя точность: {report_data['summary']['avg_accuracy']:.1f}%")
            
            return {
                'status': 'success',
                'coefficients': coefficients_results,
                'errors': error_results,
                'preliminary': [], # Заглушка, т.к. логика отключена
                'reports': report_data['reports'],
                'summary': report_data['summary'],
                'advanced_reports': advanced_reports,
                'source_file': source_filename
            }
            
        except Exception as e:
            error_msg = f"Критическая ошибка в process_dataset (оркестратор): {e}"
            log.exception(error_msg)
            return self._create_error_response(error_msg)
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Создает стандартный ответ об ошибке."""
        return {
            'status': 'error',
            'message': message,
            'coefficients': [],
            'errors': [{'Номенклатура': 'Система', 'Причина': 'Критическая ошибка', 'Ошибка': message}],
            'preliminary': [],
            'reports': {},
            'summary': {'total_positions': 0, 'avg_accuracy': 0, 'error_count': 1},
            'advanced_reports': {},
            'source_file': ''
        }