#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система верификации точности коэффициентов усушки

Реализует проверку точности рассчитанных коэффициентов путем выполнения 
обратных расчетов с использованием полученных коэффициентов для проверки 
того, что они дают результаты, согласующиеся с исходными данными.

Система работает по принципу, что если коэффициенты рассчитаны правильно, 
то их применение к тому же периоду должно воспроизвести исходные результаты 
усушки в пределах допустимой погрешности.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from scipy.optimize import minimize, curve_fit
import warnings
warnings.filterwarnings('ignore')

from .shrinkage_calculator import ShrinkageCalculator


class ShrinkageVerificationSystem:
    """
    Система верификации точности коэффициентов усушки.
    
    Проверяет точность рассчитанных коэффициентов путем обратного пересчета
    предварительной усушки по тем же коэффициентам.
    
    УЛУЧШЕНИЯ:
    - Проверка точного совпадения для достижения 100% точности
    - Улучшенные метрики оценки точности
    - Обработка особых случаев (без усушки, излишки)
    """
    
    def __init__(self):
        self.calculator = ShrinkageCalculator()
        # Критерии валидации
        self.validation_criteria = {
            'r_squared': {'acceptable': 0.85, 'warning': 0.7, 'critical': 0.7},
            'rmse': {'acceptable': 0.05, 'warning': 0.1, 'critical': 0.1},
            'mae': {'acceptable': 0.03, 'warning': 0.07, 'critical': 0.07}
        }
    
    def verify_coefficients_accuracy(self, 
                                   original_data: Dict[str, Any],
                                   coefficients: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет точность рассчитанных коэффициентов путем обратного пересчета.
        
        Args:
            original_data: Исходные данные инвентаризации
            coefficients: Рассчитанные коэффициенты
            
        Returns:
            Dict: Результаты проверки точности
        """
        try:
            # Получаем тип модели
            model_type = coefficients.get('model_type', 'exponential')
            
            # Рассчитываем предварительную усушку по тем же коэффициентам
            preliminary_results = self._calculate_preliminary_shrinkage_for_verification(
                original_data, coefficients, model_type
            )
            
            # Сравниваем с фактической усушкой из исходных данных
            actual_shrinkage = self._calculate_actual_shrinkage(original_data)
            
            # Рассчитываем метрики точности
            accuracy_metrics = self._calculate_accuracy_metrics(
                preliminary_results['predicted_shrinkage'],
                actual_shrinkage,
                original_data.get('initial_balance', 0)
            )
            
            # Для требования 100% точности значения должны точно совпадать
            is_exact_match = np.isclose(
                preliminary_results['predicted_shrinkage'], 
                actual_shrinkage, 
                rtol=1e-10
            )
            
            # Определяем статус валидации
            validation_status = self._determine_validation_status(accuracy_metrics)
            
            # Для 100% точности проверяем точное совпадение
            if is_exact_match:
                accuracy_metrics['accuracy'] = 100.0
                validation_status['overall_status'] = 'acceptable'
                validation_status['recommendation'] = 'Коэффициенты достигли 100% точности. Модель адекватна.'
            
            return {
                'verification_status': 'success',
                'preliminary_shrinkage': preliminary_results,
                'actual_shrinkage': actual_shrinkage,
                'accuracy_metrics': accuracy_metrics,
                'validation_status': validation_status,
                'coefficients_used': coefficients,
                'is_exact_match': is_exact_match,
                'verification_date': datetime.now().strftime("%d.%m.%y %H:%M:%S")
            }
            
        except Exception as e:
            return {
                'verification_status': 'error',
                'error_message': f'Ошибка верификации: {str(e)}',
                'verification_date': datetime.now().strftime("%d.%m.%y %H:%M:%S")
            }
    
    def _calculate_preliminary_shrinkage_for_verification(self,
                                                        original_data: Dict[str, Any],
                                                        coefficients: Dict[str, Any],
                                                        model_type: str) -> Dict[str, Any]:
        """
        Рассчитывает предварительную усушку для верификации.
        
        Args:
            original_data: Исходные данные
            coefficients: Коэффициенты модели
            model_type: Тип модели
            
        Returns:
            Dict: Результаты предварительного расчета
        """
        # Использование идентичной обработки данных для обратного расчета
        model_type = coefficients.get('model_type', 'exponential')
        coeff_values = coefficients.get('coefficients', {})
        
        # Расчет предсказанной усушки с использованием той же модели
        initial_balance = original_data.get('initial_balance', 0)
        storage_days = original_data.get('storage_days', 7)
        
        if model_type == 'exponential':
            a = coeff_values.get('a', 0)
            b = coeff_values.get('b', 0.049)
            c = coeff_values.get('c', 0)
            
            # Точный обратный расчет
            predicted_shrinkage_rate = a * (1 - np.exp(-b * storage_days)) + c * storage_days
            predicted_shrinkage = predicted_shrinkage_rate * initial_balance
        else:
            # Обработка других типов моделей
            return self.calculator.calculate_preliminary_shrinkage(
                current_balance=initial_balance,
                coefficients=coeff_values,
                days=storage_days,
                model_type=model_type
            )
        
        # Расчет фактической усушки из данных инвентаризации
        actual_shrinkage = self._calculate_actual_shrinkage(original_data)
        
        # Для требования 100% точности предсказанные значения должны точно совпадать с фактической усушкой
        is_exact_match = np.isclose(predicted_shrinkage, actual_shrinkage, rtol=1e-10)
        
        return {
            'predicted_shrinkage': predicted_shrinkage,
            'shrinkage_rate': predicted_shrinkage_rate,
            'final_balance': initial_balance - predicted_shrinkage,
            'days': storage_days,
            'status': 'success' if is_exact_match else 'warning',
            'message': 'Точное совпадение' if is_exact_match else 'Неточное совпадение',
            'model_type': model_type,
            'coefficients_used': coeff_values
        }
    
    def _calculate_actual_shrinkage(self, original_data: Dict[str, Any]) -> float:
        """
        Рассчитывает фактическую усушку из исходных данных.
        
        Args:
            original_data: Исходные данные инвентаризации
            
        Returns:
            float: Фактическая усушка
        """
        initial_balance = original_data.get('initial_balance', 0)
        incoming = original_data.get('incoming', 0)
        outgoing = original_data.get('outgoing', 0)
        final_balance = original_data.get('final_balance', 0)
        
        # Фактическая усушка = теоретический баланс - фактический конечный баланс
        theoretical_balance = initial_balance + incoming - outgoing
        actual_shrinkage = theoretical_balance - final_balance
        
        return max(0, actual_shrinkage)  # Усушка не может быть отрицательной
    
    def _calculate_accuracy_metrics(self, 
                                  predicted_shrinkage: float,
                                  actual_shrinkage: float,
                                  initial_balance: float) -> Dict[str, float]:
        """
        Рассчитывает метрики точности.
        
        Args:
            predicted_shrinkage: Прогнозируемая усушка
            actual_shrinkage: Фактическая усушка
            initial_balance: Начальный баланс
            
        Returns:
            Dict: Метрики точности
        """
        # Нормализуем значения относительно начального баланса
        if initial_balance > 0:
            predicted_normalized = predicted_shrinkage / initial_balance
            actual_normalized = actual_shrinkage / initial_balance
        else:
            predicted_normalized = predicted_shrinkage
            actual_normalized = actual_shrinkage
        
        # Рассчитываем метрики
        diff = predicted_normalized - actual_normalized
        abs_diff = abs(diff)
        
        # MAE (Средняя абсолютная ошибка)
        mae = abs_diff
        
        # RMSE (Среднеквадратическая ошибка)
        rmse = np.sqrt(diff ** 2)
        
        # R² (Коэффициент детерминации)
        # Для простого случая с одним значением используем приближение
        if actual_normalized > 0:
            r_squared = max(0, 1 - (diff ** 2) / (actual_normalized ** 2))
        else:
            r_squared = 1.0 if diff == 0 else 0.0
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r_squared': r_squared,
            'predicted_shrinkage': predicted_shrinkage,
            'actual_shrinkage': actual_shrinkage,
            'difference': diff,
            'absolute_difference': abs_diff
        }
    
    def _determine_validation_status(self, accuracy_metrics: Dict[str, float]) -> Dict[str, str]:
        """
        Определяет статус валидации на основе метрик точности.
        
        Args:
            accuracy_metrics: Метрики точности
            
        Returns:
            Dict: Статус валидации
        """
        r_squared = accuracy_metrics.get('r_squared', 0)
        rmse = accuracy_metrics.get('rmse', 0)
        mae = accuracy_metrics.get('mae', 0)
        
        criteria = self.validation_criteria
        
        # Определяем статус для каждой метрики
        r_squared_status = self._evaluate_metric(r_squared, criteria['r_squared'], higher_is_better=True)
        rmse_status = self._evaluate_metric(rmse, criteria['rmse'], higher_is_better=False)
        mae_status = self._evaluate_metric(mae, criteria['mae'], higher_is_better=False)
        
        # Общий статус - худший из всех
        statuses = [r_squared_status, rmse_status, mae_status]
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'acceptable'
        
        return {
            'overall_status': overall_status,
            'r_squared_status': r_squared_status,
            'rmse_status': rmse_status,
            'mae_status': mae_status,
            'recommendation': self._get_recommendation(overall_status)
        }
    
    def _evaluate_metric(self, value: float, thresholds: Dict[str, float], higher_is_better: bool) -> str:
        """
        Оценивает метрику по заданным порогам.
        
        Args:
            value: Значение метрики
            thresholds: Пороги для оценки
            higher_is_better: True если большее значение лучше
            
        Returns:
            str: Статус метрики
        """
        if higher_is_better:
            if value >= thresholds['acceptable']:
                return 'acceptable'
            elif value >= thresholds['warning']:
                return 'warning'
            else:
                return 'critical'
        else:
            if value <= thresholds['acceptable']:
                return 'acceptable'
            elif value <= thresholds['warning']:
                return 'warning'
            else:
                return 'critical'
    
    def _get_recommendation(self, status: str) -> str:
        """
        Возвращает рекомендацию на основе статуса валидации.
        
        Args:
            status: Статус валидации
            
        Returns:
            str: Рекомендация
        """
        recommendations = {
            'acceptable': 'Коэффициенты прошли проверку точности. Модель адекватна.',
            'warning': 'Коэффициенты имеют пониженную точность. Рекомендуется уточнение модели.',
            'critical': 'Коэффициенты не соответствуют критериям точности. Требуется уточнение модели.'
        }
        return recommendations.get(status, 'Неизвестный статус')
    
    def generate_verification_report(self, verification_results: Dict[str, Any]) -> str:
        """
        Генерирует отчет о верификации.
        
        Args:
            verification_results: Результаты верификации
            
        Returns:
            str: Отчет о верификации
        """
        if verification_results.get('verification_status') == 'error':
            return f"Ошибка верификации: {verification_results.get('error_message', 'Неизвестная ошибка')}"
        
        metrics = verification_results.get('accuracy_metrics', {})
        validation = verification_results.get('validation_status', {})
        
        report = f"""
ОТЧЕТ О ВЕРИФИКАЦИИ КОЭФФИЦИЕНТОВ УСУШКИ
=====================================

Дата верификации: {verification_results.get('verification_date', 'Не указана')}
Статус верификации: {verification_results.get('verification_status', 'Неизвестен')}

МЕТРИКИ ТОЧНОСТИ:
- Коэффициент детерминации (R²): {metrics.get('r_squared', 0):.4f}
- Среднеквадратическая ошибка (RMSE): {metrics.get('rmse', 0):.4f}
- Средняя абсолютная ошибка (MAE): {metrics.get('mae', 0):.4f}

СРАВНЕНИЕ РЕЗУЛЬТАТОВ:
- Прогнозируемая усушка: {metrics.get('predicted_shrinkage', 0):.4f}
- Фактическая усушка: {metrics.get('actual_shrinkage', 0):.4f}
- Разница: {metrics.get('difference', 0):.4f}

СТАТУС ВАЛИДАЦИИ:
- Общий статус: {validation.get('overall_status', 'Не определен').upper()}
- R² статус: {validation.get('r_squared_status', 'Не определен').upper()}
- RMSE статус: {validation.get('rmse_status', 'Не определен').upper()}
- MAE статус: {validation.get('mae_status', 'Не определен').upper()}

РЕКОМЕНДАЦИЯ:
{validation.get('recommendation', 'Рекомендация отсутствует')}

"""
        return report.strip()


# Пример использования системы верификации
if __name__ == "__main__":
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Пример данных для тестирования
    test_data = {
        'name': 'Тестовая номенклатура',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 20.0,
        'final_balance': 128.0,
        'storage_days': 7
    }
    
    # Пример коэффициентов
    test_coefficients = {
        'model_type': 'exponential',
        'coefficients': {'a': 0.015, 'b': 0.049, 'c': 0.001},
        'r_squared': 0.95
    }
    
    # Выполняем верификацию
    results = verification_system.verify_coefficients_accuracy(test_data, test_coefficients)
    
    # Генерируем отчет
    report = verification_system.generate_verification_report(results)
    print(report)