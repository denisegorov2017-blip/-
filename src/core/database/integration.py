#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция базы данных с системой расчета коэффициентов усушки.

Этот файл предоставляет функции для интеграции базы данных с основной системой
расчета коэффициентов усушки, включая сохранение результатов расчетов
и загрузку исторических данных для адаптивных моделей.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from src.logger_config import log
from src.config import DEFAULT_CONFIG

# Импортируем компоненты базы данных
from src.core.database.database import get_db_session
from src.core.database.models import (
    SourceData, Nomenclature, CalculationData, Model, Coefficient, 
    Forecast, Analytics, ValidationError
)
from src.core.database.services import get_database_service

# Импортируем существующие компоненты системы
from src.core.data_models import NomenclatureRow

class DatabaseIntegration:
    """
    Класс для интеграции базы данных с системой расчета коэффициентов усушки.
    """
    
    def __init__(self):
        """
        Инициализирует интеграцию с базой данных.
        """
        self.enabled = DEFAULT_CONFIG.get('enable_database', False)
        if not self.enabled:
            log.info("Интеграция с базой данных отключена в конфигурации")
            return
            
        try:
            self.Session = get_db_session()
            log.info("Интеграция с базой данных инициализирована")
        except Exception as e:
            log.error(f"Ошибка при инициализации интеграции с базой данных: {e}")
            self.enabled = False
    
    def save_calculation_results(self, 
                                source_filename: str,
                                dataset: pd.DataFrame,
                                coefficients_results: List[Dict[str, Any]],
                                error_results: List[Dict[str, Any]]) -> bool:
        """
        Сохраняет результаты расчетов в базу данных.
        
        Args:
            source_filename (str): Имя исходного файла
            dataset (pd.DataFrame): Входной набор данных
            coefficients_results (List[Dict[str, Any]]): Результаты расчета коэффициентов
            error_results (List[Dict[str, Any]]): Результаты ошибок
            
        Returns:
            bool: True, если сохранение успешно
        """
        if not self.enabled:
            return True
            
        try:
            session = self.Session()
            db_service = get_database_service(session)
            
            # Создаем запись об исходных данных
            source_data = db_service.create_source_data(
                file_name=source_filename,
                file_path=source_filename,
                upload_date=datetime.now(),
                processed=True,
                quality_score=1.0
            )
            
            # Сохраняем результаты для каждой номенклатуры
            for result in coefficients_results:
                # Создаем или получаем запись о номенклатуре
                nomenclature_name = result.get('Номенклатура') or result.get('nomenclature', 'Unknown')
                nomenclature = db_service.create_nomenclature(
                    name=nomenclature_name,
                    product_type=result.get('product_type', 'Unknown')
                )
                
                # Создаем запись с расчетными данными
                # Находим соответствующую строку в dataset
                nomenclature_name = result.get('Номенклатура') or result.get('nomenclature', 'Unknown')
                nomenclature_data = dataset[dataset['Номенклатура'] == nomenclature_name]
                if not nomenclature_data.empty:
                    row_data = nomenclature_data.iloc[0]
                    calculation_data = db_service.create_calculation_data(
                        source_data_id=source_data.id,
                        nomenclature_id=nomenclature.id,
                        initial_balance=row_data.get('Начальный_остаток', 0),
                        incoming=row_data.get('Приход', 0),
                        outgoing=row_data.get('Расход', 0),
                        final_balance=row_data.get('Конечный_остаток', 0),
                        storage_days=row_data.get('Период_хранения_дней', 0),
                        calculation_date=datetime.now(),
                        data_quality_flag='clean'
                    )
                
                # Создаем или получаем запись о модели
                model = db_service.create_model(
                    name=f"ShrinkageCalculator_{result.get('model_type', 'exponential')}",
                    model_type=result.get('model_type', 'exponential'),
                    version="1.0"
                )
                
                # Создаем запись с коэффициентами
                coefficient = db_service.create_coefficient(
                    calculation_data_id=calculation_data.id if 'calculation_data' in locals() else None,
                    model_id=model.id,
                    coefficient_a=result.get('a', 0),
                    coefficient_b=result.get('b', 0),
                    coefficient_c=result.get('c', 0),
                    accuracy_r2=result.get('accuracy', 0),
                    calculation_date=datetime.now()
                )
            
            # Сохраняем ошибки
            for error in error_results:
                # Находим соответствующую номенклатуру
                nomenclature_name = error.get('Номенклатура') or error.get('nomenclature', 'Unknown')
                nomenclature = db_service.get_nomenclature_by_name(nomenclature_name)
                if nomenclature:
                    # Находим соответствующие расчетные данные
                    calculation_data_list = db_service.get_calculation_data_by_nomenclature(nomenclature.id)
                    if calculation_data_list:
                        calculation_data = calculation_data_list[-1]  # Берем последнюю запись
                        
                        # Создаем запись об ошибке
                        db_service.create_validation_error(
                            calculation_data_id=calculation_data.id,
                            error_type=error.get('error_type', 'unknown'),
                            description=error.get('message', '') or error.get('Причина', ''),
                            severity_level='medium',
                            detected_by='system',
                            detection_date=datetime.now()
                        )
            
            session.commit()
            session.close()
            
            log.success(f"Результаты расчетов сохранены в базу данных для файла {source_filename}")
            return True
            
        except Exception as e:
            log.error(f"Ошибка при сохранении результатов расчетов в базу данных: {e}")
            try:
                session.rollback()
                session.close()
            except:
                pass
            return False
    
    def load_historical_data(self, nomenclature_name: str) -> List[Dict[str, Any]]:
        """
        Загружает исторические данные для указанной номенклатуры.
        
        Args:
            nomenclature_name (str): Название номенклатуры
            
        Returns:
            List[Dict[str, Any]]: Список исторических данных
        """
        if not self.enabled:
            return []
            
        try:
            session = self.Session()
            db_service = get_database_service(session)
            
            # Получаем номенклатуру
            nomenclature = db_service.get_nomenclature_by_name(nomenclature_name)
            if not nomenclature:
                session.close()
                return []
            
            # Получаем исторические расчетные данные
            calculation_data_list = db_service.get_calculation_data_by_nomenclature(nomenclature.id)
            
            # Преобразуем данные в формат, подходящий для адаптивных моделей
            historical_data = []
            for calc_data in calculation_data_list:
                data_point = {
                    'initial_balance': calc_data.initial_balance,
                    'incoming': calc_data.incoming,
                    'outgoing': calc_data.outgoing,
                    'final_balance': calc_data.final_balance,
                    'storage_days': calc_data.storage_days,
                    'calculation_date': calc_data.calculation_date
                }
                historical_data.append(data_point)
            
            session.close()
            
            log.info(f"Загружено {len(historical_data)} исторических записей для номенклатуры {nomenclature_name}")
            return historical_data
            
        except Exception as e:
            log.error(f"Ошибка при загрузке исторических данных для номенклатуры {nomenclature_name}: {e}")
            return []
    
    def get_nomenclature_coefficients(self, nomenclature_name: str, model_type: str = 'exponential') -> List[Dict[str, Any]]:
        """
        Получает исторические коэффициенты для указанной номенклатуры.
        
        Args:
            nomenclature_name (str): Название номенклатуры
            model_type (str): Тип модели
            
        Returns:
            List[Dict[str, Any]]: Список исторических коэффициентов
        """
        if not self.enabled:
            return []
            
        try:
            session = self.Session()
            db_service = get_database_service(session)
            
            # Получаем номенклатуру
            nomenclature = db_service.get_nomenclature_by_name(nomenclature_name)
            if not nomenclature:
                session.close()
                return []
            
            # Получаем модель
            model = session.query(Model).filter(
                Model.name.like(f"%{model_type}%")
            ).first()
            
            if not model:
                session.close()
                return []
            
            # Получаем расчетные данные для номенклатуры
            calculation_data_list = db_service.get_calculation_data_by_nomenclature(nomenclature.id)
            
            # Получаем коэффициенты для каждой записи
            coefficients = []
            for calc_data in calculation_data_list:
                coefficient = session.query(Coefficient).filter(
                    Coefficient.calculation_data_id == calc_data.id,
                    Coefficient.model_id == model.id
                ).first()
                
                if coefficient:
                    coeff_data = {
                        'a': coefficient.coefficient_a,
                        'b': coefficient.coefficient_b,
                        'c': coefficient.coefficient_c,
                        'accuracy': coefficient.accuracy_r2,
                        'calculation_date': coefficient.calculation_date
                    }
                    coefficients.append(coeff_data)
            
            session.close()
            
            log.info(f"Загружено {len(coefficients)} исторических коэффициентов для номенклатуры {nomenclature_name}")
            return coefficients
            
        except Exception as e:
            log.error(f"Ошибка при загрузке исторических коэффициентов для номенклатуры {nomenclature_name}: {e}")
            return []
    
    def save_forecast(self, 
                     nomenclature_name: str,
                     initial_balance: float,
                     forecast_result: Dict[str, Any]) -> bool:
        """
        Сохраняет результаты прогноза в базу данных.
        
        Args:
            nomenclature_name (str): Название номенклатуры
            initial_balance (float): Начальный остаток
            forecast_result (Dict[str, Any]): Результаты прогноза
            
        Returns:
            bool: True, если сохранение успешно
        """
        if not self.enabled:
            return True
            
        try:
            session = self.Session()
            db_service = get_database_service(session)
            
            # Получаем номенклатуру
            nomenclature = db_service.get_nomenclature_by_name(nomenclature_name)
            if not nomenclature:
                # Создаем новую номенклатуру
                nomenclature = db_service.create_nomenclature(
                    name=nomenclature_name,
                    product_type=forecast_result.get('product_type', 'Unknown')
                )
            
            # Создаем модель прогноза, если она не существует
            model = session.query(Model).filter(
                Model.name == 'ForecastModel'
            ).first()
            
            if not model:
                model = db_service.create_model(
                    name='ForecastModel',
                    model_type='forecast',
                    version="1.0"
                )
            
            # Создаем запись с расчетными данными для прогноза
            calculation_data = db_service.create_calculation_data(
                source_data_id=None,  # Прогноз не связан с исходными данными
                nomenclature_id=nomenclature.id,
                initial_balance=initial_balance,
                incoming=0,
                outgoing=0,
                final_balance=forecast_result.get('final_balance', 0),
                storage_days=forecast_result.get('days', 0),
                calculation_date=datetime.now(),
                data_quality_flag='forecast',
                is_preliminary_forecast=True
            )
            
            # Создаем запись с коэффициентами
            coefficient = db_service.create_coefficient(
                calculation_data_id=calculation_data.id,
                model_id=model.id,
                coefficient_a=forecast_result.get('coefficients_used', {}).get('a', 0),
                coefficient_b=forecast_result.get('coefficients_used', {}).get('b', 0),
                coefficient_c=forecast_result.get('coefficients_used', {}).get('c', 0),
                accuracy_r2=0,  # Прогноз не имеет точности в том же смысле
                calculation_date=datetime.now()
            )
            
            # Создаем запись с прогнозом
            forecast = db_service.create_forecast(
                coefficient_id=coefficient.id,
                forecast_value=forecast_result.get('predicted_shrinkage', 0),
                forecast_date=datetime.now()
            )
            
            session.commit()
            session.close()
            
            log.success(f"Прогноз сохранен в базу данных для номенклатуры {nomenclature_name}")
            return True
            
        except Exception as e:
            log.error(f"Ошибка при сохранении прогноза в базу данных: {e}")
            try:
                session.rollback()
                session.close()
            except:
                pass
            return False
    
    def get_nomenclature_statistics(self, nomenclature_name: str) -> Dict[str, Any]:
        """
        Получает статистику по номенклатуре.
        
        Args:
            nomenclature_name (str): Название номенклатуры
            
        Returns:
            Dict[str, Any]: Статистика по номенклатуре
        """
        if not self.enabled:
            return {}
            
        try:
            session = self.Session()
            db_service = get_database_service(session)
            
            # Получаем статистику через сервис
            nomenclature = db_service.get_nomenclature_by_name(nomenclature_name)
            if not nomenclature:
                session.close()
                return {}
            
            stats = db_service.get_nomenclature_statistics(nomenclature.id)
            session.close()
            
            return stats
        except Exception as e:
            log.error(f"Ошибка при получении статистики по номенклатуре {nomenclature_name}: {e}")
            return {}

# Глобальный экземпляр интеграции
db_integration = None

def get_database_integration() -> DatabaseIntegration:
    """
    Получает глобальный экземпляр интеграции с базой данных.
    
    Returns:
        DatabaseIntegration: Экземпляр интеграции с базой данных
    """
    global db_integration
    if db_integration is None:
        db_integration = DatabaseIntegration()
    return db_integration

# Функции для удобного использования в других модулях
def save_calculation_results(source_filename: str,
                           dataset: pd.DataFrame,
                           coefficients_results: List[Dict[str, Any]],
                           error_results: List[Dict[str, Any]]) -> bool:
    """
    Сохраняет результаты расчетов в базу данных.
    
    Args:
        source_filename (str): Имя исходного файла
        dataset (pd.DataFrame): Входной набор данных
        coefficients_results (List[Dict[str, Any]]): Результаты расчета коэффициентов
        error_results (List[Dict[str, Any]]): Результаты ошибок
        
    Returns:
        bool: True, если сохранение успешно
    """
    integration = get_database_integration()
    return integration.save_calculation_results(
        source_filename, dataset, coefficients_results, error_results
    )

def load_historical_data(nomenclature_name: str) -> List[Dict[str, Any]]:
    """
    Загружает исторические данные для указанной номенклатуры.
    
    Args:
        nomenclature_name (str): Название номенклатуры
        
    Returns:
        List[Dict[str, Any]]: Список исторических данных
    """
    integration = get_database_integration()
    return integration.load_historical_data(nomenclature_name)

def save_forecast(nomenclature_name: str,
                 initial_balance: float,
                 forecast_result: Dict[str, Any]) -> bool:
    """
    Сохраняет результаты прогноза в базу данных.
    
    Args:
        nomenclature_name (str): Название номенклатуры
        initial_balance (float): Начальный остаток
        forecast_result (Dict[str, Any]): Результаты прогноза
        
    Returns:
        bool: True, если сохранение успешно
    """
    integration = get_database_integration()
    return integration.save_forecast(nomenclature_name, initial_balance, forecast_result)