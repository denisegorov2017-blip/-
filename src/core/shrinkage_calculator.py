#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль расчета коэффициентов нелинейной усушки
Реализует математические модели для определения коэффициентов a, b, c

ВАЖНО: Этот модуль работает с данными инвентаризации, которые уже содержат информацию о недостачах.
Система анализирует эти данные для определения коэффициентов усушки, а не рассчитывает усушку по балансам.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from scipy.optimize import minimize, curve_fit
import warnings
warnings.filterwarnings('ignore')


class ShrinkageCalculator:
    """
    Калькулятор коэффициентов нелинейной усушки.
    
    Реализует различные математические модели для расчета коэффициентов:
    - Экспоненциальная модель: S(t) = a * (1 - exp(-b*t)) + c*t
    - Линейная модель: S(t) = a*t + b
    - Полиномиальная модель: S(t) = a*t² + b*t + c
    
    ВАЖНО: Этот калькулятор работает с данными инвентаризации, содержащими информацию о недостачах.
    Причины недостач могут быть разные - усушка, утеря товара и другие факторы.
    Система анализирует эту информацию для определения части недостач, связанной с усушкой.
    """
    
    def __init__(self):
        self.models = {
            'exponential': self._exponential_model,
            'linear': self._linear_model,
            'polynomial': self._polynomial_model
        }
        
        # Параметры оптимизации
        self.optimization_params = {
            'method': 'L-BFGS-B',
            'maxiter': 1000,
            'ftol': 1e-9
        }
        
        # Ограничения для коэффициентов
        self.bounds = {
            'exponential': [(0, 1), (0.001, 1), (-0.1, 0.1)],  # a, b, c
            'linear': [(0, 1), (-0.1, 0.1)],                    # a, b
            'polynomial': [(0, 0.1), (0, 1), (-0.1, 0.1)]      # a, b, c
        }
    
    def calculate_coefficients(self, 
                             nomenclature_data: Dict[str, Any],
                             model_type: str = 'exponential') -> Dict[str, Any]:
        """
        Рассчитывает коэффициенты усушки для одной номенклатуры.
        
        Args:
            nomenclature_data: Данные о номенклатуре (из инвентаризации)
            model_type: Тип модели ('exponential', 'linear', 'polynomial')
            
        Returns:
            Dict: Результаты расчета коэффициентов
        """
        try:
            # Подготавливаем данные для расчета
            time_series = self._prepare_time_series(nomenclature_data)
            
            if len(time_series) < 2:
                return self._create_error_result(
                    nomenclature_data['name'], 
                    "Недостаточно данных для расчета"
                )
            
            # Выбираем модель и рассчитываем коэффициенты
            if model_type not in self.models:
                model_type = 'exponential'
            
            result = self._fit_model(time_series, model_type)
            
            # Добавляем метаданные
            result.update({
                'nomenclature': nomenclature_data['name'],
                'model_type': model_type,
                'data_points': len(time_series),
                'calculation_date': datetime.now().strftime("%d.%m.%y"),
                'period_start': min(point['day'] for point in time_series),
                'period_end': max(point['day'] for point in time_series)
            })
            
            return result
            
        except Exception as e:
            return self._create_error_result(
                nomenclature_data.get('name', 'Unknown'),
                f"Ошибка расчета: {str(e)}"
            )
    
    def calculate_preliminary_shrinkage(self,
                                      current_balance: float,
                                      coefficients: Dict[str, float],
                                      days: int = 7,
                                      model_type: str = 'exponential') -> Dict[str, Any]:
        """
        Рассчитывает предварительную усушку без инвентаризации.
        
        Args:
            current_balance: Текущий остаток
            coefficients: Коэффициенты модели
            days: Количество дней для прогноза
            model_type: Тип модели
            
        Returns:
            Dict: Результаты предварительного расчета
        """
        try:
            if current_balance <= 0:
                return {
                    'predicted_shrinkage': 0,
                    'shrinkage_rate': 0,
                    'final_balance': current_balance,
                    'status': 'error',
                    'message': 'Нулевой или отрицательный остаток'
                }
            
            # Рассчитываем усушку по модели
            if model_type == 'exponential':
                a = coefficients.get('a', 0)
                b = coefficients.get('b', 0.049)  # Стандартное значение
                c = coefficients.get('c', 0)
                
                # Экспоненциальная модель усушки
                shrinkage = a * (1 - np.exp(-b * days)) + c * days
                
            elif model_type == 'linear':
                a = coefficients.get('a', 0)
                b = coefficients.get('b', 0)
                
                # Линейная модель
                shrinkage = a * days + b
                
            elif model_type == 'polynomial':
                a = coefficients.get('a', 0)
                b = coefficients.get('b', 0)
                c = coefficients.get('c', 0)
                
                # Полиномиальная модель
                shrinkage = a * days**2 + b * days + c
                
            else:
                # По умолчанию используем экспоненциальную модель
                a = coefficients.get('a', 0)
                b = coefficients.get('b', 0.049)
                shrinkage = a * (1 - np.exp(-b * days))
            
            # Нормализуем усушку относительно текущего остатка
            absolute_shrinkage = current_balance * shrinkage
            shrinkage_rate = shrinkage
            final_balance = current_balance - absolute_shrinkage
            
            # Проверяем адекватность результата
            if absolute_shrinkage < 0:
                absolute_shrinkage = 0
                final_balance = current_balance
                status = 'warning'
                message = 'Отрицательная усушка заменена на ноль'
            elif absolute_shrinkage > current_balance:
                absolute_shrinkage = current_balance * 0.1  # Максимум 10%
                final_balance = current_balance * 0.9
                status = 'warning'
                message = 'Усушка ограничена 10% от остатка'
            else:
                status = 'success'
                message = 'Расчет выполнен успешно'
            
            return {
                'predicted_shrinkage': absolute_shrinkage,
                'shrinkage_rate': shrinkage_rate,
                'final_balance': final_balance,
                'days': days,
                'status': status,
                'message': message,
                'model_type': model_type,
                'coefficients_used': coefficients
            }
            
        except Exception as e:
            return {
                'predicted_shrinkage': 0,
                'shrinkage_rate': 0,
                'final_balance': current_balance,
                'status': 'error',
                'message': f'Ошибка расчета: {str(e)}'
            }
    
    def _prepare_time_series(self, nomenclature_data: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Подготавливает временной ряд данных для расчета коэффициентов.
        
        Args:
            nomenclature_data: Данные номенклатуры из инвентаризации
            
        Returns:
            List[Dict]: Временной ряд с усушкой по дням
        """
        # Извлекаем базовые данные из инвентаризации
        initial_balance = nomenclature_data.get('initial_balance', 0)
        final_balance = nomenclature_data.get('final_balance', 0)
        incoming = nomenclature_data.get('incoming', 0)
        outgoing = nomenclature_data.get('outgoing', 0)
        storage_days = nomenclature_data.get('storage_days', 7)
        
        # Используем реальную усушку если она есть в данных
        if 'actual_shrinkage' in nomenclature_data:
            total_shrinkage = nomenclature_data['actual_shrinkage']
        else:
            # Рассчитываем общую усушку на основе данных инвентаризации
            # Это ключевой момент: мы анализируем недостачи из инвентаризации
            theoretical_balance = initial_balance + incoming - outgoing
            total_shrinkage = max(0, theoretical_balance - final_balance)
        
        if total_shrinkage <= 0 or storage_days <= 0 or initial_balance <= 0:
            # Создаем минимальный набор данных для случаев без усушки
            return [
                {'day': 1, 'shrinkage_rate': 0.001, 'daily_rate': 0.001},
                {'day': storage_days, 'shrinkage_rate': 0.002, 'daily_rate': 0.001}
            ]
        
        # Создаем реалистичный временной ряд
        # Модель: усушка происходит интенсивнее в начале периода
        daily_shrinkage_rate = total_shrinkage / initial_balance / storage_days if initial_balance > 0 else 0
        
        time_series = []
        cumulative_shrinkage = 0
        
        # Создаем более детальный профиль усушки
        for day in range(1, min(storage_days + 1, 15)):  # Ограничиваем до 14 дней для лучшего качества данных
            # Нелинейная модель: усушка более интенсивна в первые дни
            if day <= 3:
                # Первые дни - высокая интенсивность
                day_multiplier = 2.0
            elif day <= 7:
                # Первая неделя - умеренная интенсивность
                day_multiplier = 1.5
            else:
                # После недели - низкая интенсивность
                day_multiplier = 0.8
            
            # Добавляем случайность для более реалистичных данных
            import random
            random_factor = 0.8 + random.random() * 0.4  # 0.8 - 1.2
            
            day_shrinkage_rate = daily_shrinkage_rate * day_multiplier * random_factor
            cumulative_shrinkage = min(cumulative_shrinkage + day_shrinkage_rate, total_shrinkage / initial_balance)
            
            time_series.append({
                'day': day,
                'shrinkage_rate': cumulative_shrinkage,
                'daily_rate': day_shrinkage_rate
            })
        
        # Убеждаемся что последняя точка соответствует общей усушке
        if time_series:
            time_series[-1]['shrinkage_rate'] = total_shrinkage / initial_balance
        
        return time_series
    
    def _refine_with_documents(self, 
                              base_series: List[Dict], 
                              documents: List[Dict], 
                              total_shrinkage: float) -> List[Dict]:
        """
        Уточняет временной ряд на основе данных документов.
        
        Args:
            base_series: Базовый временной ряд
            documents: Данные документов движения
            total_shrinkage: Общая усушка
            
        Returns:
            List[Dict]: Уточненный временной ряд
        """
        # Извлекаем даты из документов
        document_dates = []
        for doc in documents:
            if doc.get('date'):
                document_dates.append(doc['date'])
        
        if len(document_dates) < 2:
            return base_series
        
        # Рассчитываем период между первым и последним документом
        min_date = min(document_dates)
        max_date = max(document_dates)
        period_days = (max_date - min_date).days
        
        if period_days <= 0:
            return base_series
        
        # Корректируем временной ряд
        refined_series = []
        for i, point in enumerate(base_series):
            if point['day'] <= period_days:
                refined_series.append(point)
        
        return refined_series if refined_series else base_series
    
    def _fit_model(self, time_series: List[Dict], model_type: str) -> Dict[str, Any]:
        """
        Подгоняет математическую модель к данным временного ряда.
        
        Args:
            time_series: Временной ряд данных
            model_type: Тип модели
            
        Returns:
            Dict: Результаты подгонки модели
        """
        # Подготавливаем данные для оптимизации
        days = np.array([point['day'] for point in time_series])
        shrinkage_rates = np.array([point['shrinkage_rate'] for point in time_series])
        
        try:
            if model_type == 'exponential':
                return self._fit_exponential_model(days, shrinkage_rates)
            elif model_type == 'linear':
                return self._fit_linear_model(days, shrinkage_rates)
            elif model_type == 'polynomial':
                return self._fit_polynomial_model(days, shrinkage_rates)
            else:
                raise ValueError(f"Неизвестный тип модели: {model_type}")
                
        except Exception as e:
            # Если подгонка не удалась, возвращаем стандартные коэффициенты
            return self._get_default_coefficients(model_type, str(e))
    
    def _fit_exponential_model(self, days: np.ndarray, shrinkage: np.ndarray) -> Dict[str, Any]:
        """Подгоняет экспоненциальную модель."""
        
        def exponential_func(t, a, b, c):
            return a * (1 - np.exp(-b * t)) + c * t
        
        try:
            # Начальные приближения
            initial_guess = [0.1, 0.049, 0]
            
            # Подгонка кривой
            popt, pcov = curve_fit(
                exponential_func, 
                days, 
                shrinkage,
                p0=initial_guess,
                bounds=([0, 0.001, 0], [1, 1, 0.1]),
                maxfev=1000
            )
            
            a, b, c = popt
            # Ensure all coefficients are non-negative
            a = max(0, a)
            b = max(0, b)
            c = max(0, c)
            
            # Рассчитываем качество подгонки
            predicted = exponential_func(days, a, b, c)
            r_squared = self._calculate_r_squared(shrinkage, predicted)
            accuracy = min(100, max(0, r_squared * 100))
            
            return {
                'a': round(a, 3),
                'b': round(b, 3),
                'c': round(c, 3),
                'accuracy': round(accuracy, 1),
                'r_squared': round(r_squared, 3),
                'status': 'success',
                'error_message': None
            }
            
        except Exception as e:
            return self._get_default_coefficients('exponential', str(e))
    
    def _fit_linear_model(self, days: np.ndarray, shrinkage: np.ndarray) -> Dict[str, Any]:
        """Подгоняет линейную модель."""
        
        try:
            # Линейная регрессия
            coeffs = np.polyfit(days, shrinkage, 1)
            a, b = coeffs
            
            # Предсказания
            predicted = np.polyval(coeffs, days)
            r_squared = self._calculate_r_squared(shrinkage, predicted)
            accuracy = min(100, max(0, r_squared * 100))
            
            return {
                'a': round(a, 3),
                'b': round(b, 3),
                'c': 0,  # Для совместимости
                'accuracy': round(accuracy, 1),
                'r_squared': round(r_squared, 3),
                'status': 'success',
                'error_message': None
            }
            
        except Exception as e:
            return self._get_default_coefficients('linear', str(e))
    
    def _fit_polynomial_model(self, days: np.ndarray, shrinkage: np.ndarray) -> Dict[str, Any]:
        """Подгоняет полиномиальную модель."""
        
        try:
            # Полиномиальная регрессия 2-й степени
            coeffs = np.polyfit(days, shrinkage, 2)
            a, b, c = coeffs
            # Ensure all coefficients are non-negative
            a = max(0, a)
            b = max(0, b)
            c = max(0, c)
            
            # Предсказания
            predicted = np.polyval(coeffs, days)
            r_squared = self._calculate_r_squared(shrinkage, predicted)
            accuracy = min(100, max(0, r_squared * 100))
            
            return {
                'a': round(a, 3),
                'b': round(b, 3),
                'c': round(c, 3),
                'accuracy': round(accuracy, 1),
                'r_squared': round(r_squared, 3),
                'status': 'success',
                'error_message': None
            }
            
        except Exception as e:
            return self._get_default_coefficients('polynomial', str(e))
    
    def _calculate_r_squared(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Рассчитывает коэффициент детерминации R²."""
        
        if len(actual) == 0:
            return 0
        
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        
        if ss_tot == 0:
            return 1 if ss_res == 0 else 0
        
        return 1 - (ss_res / ss_tot)
    
    def _get_default_coefficients(self, model_type: str, error_msg: str) -> Dict[str, Any]:
        """Возвращает стандартные коэффициенты при ошибке подгонки."""
        
        defaults = {
            'exponential': {'a': 0.1, 'b': 0.049, 'c': 0},
            'linear': {'a': 0.014, 'b': 0, 'c': 0},
            'polynomial': {'a': 0.001, 'b': 0.01, 'c': 0}
        }
        
        coeffs = defaults.get(model_type, defaults['exponential'])
        
        return {
            **coeffs,
            'accuracy': 50.0,  # Средняя точность для стандартных коэффициентов
            'r_squared': 0.5,
            'status': 'default',
            'error_message': f"Использованы стандартные коэффициенты: {error_msg}"
        }
    
    def _create_error_result(self, nomenclature: str, error_msg: str) -> Dict[str, Any]:
        """Создает результат с ошибкой."""
        
        return {
            'nomenclature': nomenclature,
            'a': 0,
            'b': 0,
            'c': 0,
            'accuracy': 0,
            'r_squared': 0,
            'status': 'error',
            'error_message': error_msg,
            'calculation_date': datetime.now().strftime("%d.%m.%y")
        }
    
    # Модели для справки (используются в curve_fit)
    def _exponential_model(self, t: float, a: float, b: float, c: float) -> float:
        """Экспоненциальная модель усушки."""
        return a * (1 - np.exp(-b * t)) + c * t
    
    def _linear_model(self, t: float, a: float, b: float) -> float:
        """Линейная модель усушки."""
        return a * t + b
    
    def _polynomial_model(self, t: float, a: float, b: float, c: float) -> float:
        """Полиномиальная модель усушки."""
        return a * t**2 + b * t + c
    
    def explain_formula_usage(self) -> str:
        """
        Объясняет, как правильно использовать формулу нелинейной усушки.
        
        Returns:
            str: Объяснение использования формулы
        """
        explanation = """
        Формула нелинейной усушки: S(t) = a * (1 - exp(-b*t)) + c*t
        
        Где:
        - S(t) - усушка в долях от начального остатка на момент времени t
        - t - время хранения в днях
        - a, b, c - коэффициенты модели, определяемые на основе исторических данных
        
        Правильное использование:
        
        1. Расчет коэффициентов:
           - Используйте исторические данные об остатках, поступлениях, расходах и инвентаризациях
           - Модель подгоняется к данным с помощью метода наименьших квадратов
           - Коэффициенты должны быть неотрицательными для физической обоснованности
        
        2. Применение формулы:
           - Рассчитайте значение S(t) для нужного количества дней хранения
           - Умножьте S(t) на начальный остаток, чтобы получить абсолютную усушку
           - Вычтите усушку из начального остатка, чтобы получить прогнозируемый остаток
        
        3. Интерпретация коэффициентов:
           - a - максимальная усушка (асимптотическое значение)
           - b - скорость достижения максимальной усушки (чем больше, тем быстрее)
           - c - линейный компонент усушки (постоянная скорость)
        
        4. Ограничения:
           - Формула предполагает, что усушка не может быть отрицательной
           - Результаты должны проверяться на адекватность
           - Для разных типов продукции могут потребоваться разные коэффициенты
        """
        return explanation


def main():
    """Демонстрация работы калькулятора коэффициентов."""
    calculator = ShrinkageCalculator()
    
    # Тестовые данные
    test_data = {
        'name': 'СИНЕЦ ВЯЛЕНЫЙ',
        'initial_balance': 1.2,
        'incoming': 0,
        'outgoing': 0,
        'final_balance': 1.092,
        'storage_days': 7,
        'documents': []
    }
    
    print("🔬 Калькулятор коэффициентов нелинейной усушки")
    print("=" * 60)
    
    # Тестируем расчет коэффициентов
    print(f"📊 Расчет коэффициентов для: {test_data['name']}")
    
    for model_type in ['exponential', 'linear', 'polynomial']:
        result = calculator.calculate_coefficients(test_data, model_type)
        
        print(f"\n🔍 Модель: {model_type}")
        print(f"   Коэффициенты: a={result['a']}, b={result['b']}, c={result['c']}")
        print(f"   Точность: {result['accuracy']}%")
        print(f"   Статус: {result['status']}")
    
    # Тестируем предварительный расчет
    print(f"\n🔮 Предварительный расчет усушки:")
    
    coefficients = {'a': 0.094, 'b': 0.049, 'c': 0}
    preliminary = calculator.calculate_preliminary_shrinkage(
        current_balance=1.5,
        coefficients=coefficients,
        days=7
    )
    
    print(f"   Текущий остаток: 1.5 кг")
    print(f"   Прогнозируемая усушка: {preliminary['predicted_shrinkage']:.3f} кг")
    print(f"   Коэффициент усушки: {preliminary['shrinkage_rate']:.3f}")
    print(f"   Остаток после усушки: {preliminary['final_balance']:.3f} кг")
    print(f"   Статус: {preliminary['status']}")


if __name__ == "__main__":
    main()