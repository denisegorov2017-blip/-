#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервисные функции для работы с базой данных.

Этот файл предоставляет функции для выполнения CRUD операций
и других сервисных функций работы с базой данных.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from src.logger_config import log

# Импортируем модели
from src.core.database.models import (
    SourceData, Nomenclature, CalculationData, Model, Coefficient, 
    Forecast, Analytics, AIPattern, ValidationError, PriorityPeriod,
    PreliminaryForecast, SurplusSpecification, SurplusRecommendation,
    SurplusPattern, PatternValidation, FeedbackPreference, DataLineage,
    MLModelRegistry
)

class DatabaseService:
    """
    Сервис для работы с базой данных системы расчета коэффициентов усушки.
    """
    
    def __init__(self, session: Session):
        """
        Инициализирует сервис базы данных.
        
        Args:
            session (Session): Сессия SQLAlchemy для работы с базой данных
        """
        self.session = session
    
    # === Операции с исходными данными ===
    
    def create_source_data(self, file_name: str, file_path: str, **kwargs) -> SourceData:
        """
        Создает запись об исходных данных.
        
        Args:
            file_name (str): Имя файла
            file_path (str): Путь к файлу
            **kwargs: Дополнительные параметры
            
        Returns:
            SourceData: Созданная запись об исходных данных
        """
        try:
            source_data = SourceData(
                file_name=file_name,
                file_path=file_path,
                **kwargs
            )
            self.session.add(source_data)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись об исходных данных: {file_name}")
            return source_data
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи об исходных данных: {e}")
            raise
    
    def get_source_data_by_id(self, source_data_id: int) -> Optional[SourceData]:
        """
        Получает запись об исходных данных по ID.
        
        Args:
            source_data_id (int): ID записи об исходных данных
            
        Returns:
            Optional[SourceData]: Запись об исходных данных или None
        """
        try:
            return self.session.query(SourceData).filter(SourceData.id == source_data_id).first()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении записи об исходных данных: {e}")
            raise
    
    # === Операции с номенклатурой ===
    
    def create_nomenclature(self, name: str, product_type: str = None, **kwargs) -> Nomenclature:
        """
        Создает запись о номенклатуре.
        
        Args:
            name (str): Название номенклатуры
            product_type (str): Тип продукции
            **kwargs: Дополнительные параметры
            
        Returns:
            Nomenclature: Созданная запись о номенклатуре
        """
        try:
            # Проверяем, существует ли уже такая номенклатура
            existing = self.session.query(Nomenclature).filter(Nomenclature.name == name).first()
            if existing:
                return existing
            
            nomenclature = Nomenclature(
                name=name,
                product_type=product_type,
                **kwargs
            )
            self.session.add(nomenclature)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись о номенклатуре: {name}")
            return nomenclature
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи о номенклатуре: {e}")
            raise
    
    def get_nomenclature_by_name(self, name: str) -> Optional[Nomenclature]:
        """
        Получает запись о номенклатуре по названию.
        
        Args:
            name (str): Название номенклатуры
            
        Returns:
            Optional[Nomenclature]: Запись о номенклатуре или None
        """
        try:
            return self.session.query(Nomenclature).filter(Nomenclature.name == name).first()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении записи о номенклатуре: {e}")
            raise
    
    # === Операции с расчетными данными ===
    
    def create_calculation_data(self, source_data_id: int, nomenclature_id: int, **kwargs) -> CalculationData:
        """
        Создает запись с расчетными данными.
        
        Args:
            source_data_id (int): ID исходных данных
            nomenclature_id (int): ID номенклатуры
            **kwargs: Дополнительные параметры
            
        Returns:
            CalculationData: Созданная запись с расчетными данными
        """
        try:
            calculation_data = CalculationData(
                source_data_id=source_data_id,
                nomenclature_id=nomenclature_id,
                **kwargs
            )
            self.session.add(calculation_data)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись с расчетными данными для номенклатуры ID {nomenclature_id}")
            return calculation_data
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи с расчетными данными: {e}")
            raise
    
    def get_calculation_data_by_nomenclature(self, nomenclature_id: int) -> List[CalculationData]:
        """
        Получает все записи с расчетными данными для указанной номенклатуры.
        
        Args:
            nomenclature_id (int): ID номенклатуры
            
        Returns:
            List[CalculationData]: Список записей с расчетными данными
        """
        try:
            return self.session.query(CalculationData).filter(
                CalculationData.nomenclature_id == nomenclature_id
            ).all()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении записей с расчетными данными: {e}")
            raise
    
    # === Операции с моделями ===
    
    def create_model(self, name: str, model_type: str, version: str = "1.0", **kwargs) -> Model:
        """
        Создает запись о модели.
        
        Args:
            name (str): Название модели
            model_type (str): Тип модели
            version (str): Версия модели
            **kwargs: Дополнительные параметры
            
        Returns:
            Model: Созданная запись о модели
        """
        try:
            model = Model(
                name=name,
                model_type=model_type,
                version=version,
                **kwargs
            )
            self.session.add(model)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись о модели: {name} ({model_type})")
            return model
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи о модели: {e}")
            raise
    
    # === Операции с коэффициентами ===
    
    def create_coefficient(self, calculation_data_id: int, model_id: int, **kwargs) -> Coefficient:
        """
        Создает запись с коэффициентами.
        
        Args:
            calculation_data_id (int): ID расчетных данных
            model_id (int): ID модели
            **kwargs: Дополнительные параметры
            
        Returns:
            Coefficient: Созданная запись с коэффициентами
        """
        try:
            coefficient = Coefficient(
                calculation_data_id=calculation_data_id,
                model_id=model_id,
                **kwargs
            )
            self.session.add(coefficient)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись с коэффициентами для расчета ID {calculation_data_id}")
            return coefficient
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи с коэффициентами: {e}")
            raise
    
    # === Операции с прогнозами ===
    
    def create_forecast(self, coefficient_id: int, forecast_value: float, **kwargs) -> Forecast:
        """
        Создает запись с прогнозом.
        
        Args:
            coefficient_id (int): ID коэффициентов
            forecast_value (float): Прогнозируемое значение
            **kwargs: Дополнительные параметры
            
        Returns:
            Forecast: Созданная запись с прогнозом
        """
        try:
            forecast = Forecast(
                coefficient_id=coefficient_id,
                forecast_value=forecast_value,
                **kwargs
            )
            self.session.add(forecast)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись с прогнозом для коэффициентов ID {coefficient_id}")
            return forecast
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи с прогнозом: {e}")
            raise
    
    # === Операции с аналитикой ===
    
    def create_analytics(self, nomenclature_id: int, model_id: int, **kwargs) -> Analytics:
        """
        Создает запись с аналитикой.
        
        Args:
            nomenclature_id (int): ID номенклатуры
            model_id (int): ID модели
            **kwargs: Дополнительные параметры
            
        Returns:
            Analytics: Созданная запись с аналитикой
        """
        try:
            analytics = Analytics(
                nomenclature_id=nomenclature_id,
                model_id=model_id,
                **kwargs
            )
            self.session.add(analytics)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись с аналитикой для номенклатуры ID {nomenclature_id}")
            return analytics
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи с аналитикой: {e}")
            raise
    
    # === Операции с ошибками валидации ===
    
    def create_validation_error(self, calculation_data_id: int, error_type: str, description: str, **kwargs) -> ValidationError:
        """
        Создает запись об ошибке валидации.
        
        Args:
            calculation_data_id (int): ID расчетных данных
            error_type (str): Тип ошибки
            description (str): Описание ошибки
            **kwargs: Дополнительные параметры
            
        Returns:
            ValidationError: Созданная запись об ошибке валидации
        """
        try:
            validation_error = ValidationError(
                calculation_data_id=calculation_data_id,
                error_type=error_type,
                description=description,
                **kwargs
            )
            self.session.add(validation_error)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись об ошибке валидации для расчета ID {calculation_data_id}")
            return validation_error
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи об ошибке валидации: {e}")
            raise
    
    # === Операции с приоритетными периодами ===
    
    def create_priority_period(self, period_start: datetime, period_end: datetime, **kwargs) -> PriorityPeriod:
        """
        Создает запись о приоритетном периоде.
        
        Args:
            period_start (datetime): Начало периода
            period_end (datetime): Окончание периода
            **kwargs: Дополнительные параметры
            
        Returns:
            PriorityPeriod: Созданная запись о приоритетном периоде
        """
        try:
            priority_period = PriorityPeriod(
                period_start=period_start,
                period_end=period_end,
                **kwargs
            )
            self.session.add(priority_period)
            self.session.flush()  # Используем flush вместо commit для получения ID
            # Не используем refresh, так как это может вызвать проблемы
            log.info(f"Создана запись о приоритетном периоде: {period_start} - {period_end}")
            return priority_period
        except SQLAlchemyError as e:
            self.session.rollback()
            log.error(f"Ошибка при создании записи о приоритетном периоде: {e}")
            raise
    
    # === Аналитические функции ===
    
    def get_nomenclature_statistics(self, nomenclature_id: int) -> Dict[str, Any]:
        """
        Получает статистику по номенклатуре.
        
        Args:
            nomenclature_id (int): ID номенклатуры
            
        Returns:
            Dict[str, Any]: Статистика по номенклатуре
        """
        try:
            # Получаем количество расчетов
            calculation_count = self.session.query(CalculationData).filter(
                CalculationData.nomenclature_id == nomenclature_id
            ).count()
            
            # Получаем среднюю точность
            avg_accuracy = self.session.query(Analytics.avg_accuracy).filter(
                Analytics.nomenclature_id == nomenclature_id
            ).first()
            
            # Получаем количество ошибок
            error_count = self.session.query(ValidationError).join(CalculationData).filter(
                CalculationData.nomenclature_id == nomenclature_id
            ).count()
            
            return {
                'calculation_count': calculation_count,
                'avg_accuracy': avg_accuracy[0] if avg_accuracy else 0,
                'error_count': error_count
            }
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении статистики по номенклатуре: {e}")
            raise
    
    def get_model_accuracy_statistics(self, model_id: int) -> Dict[str, Any]:
        """
        Получает статистику точности модели.
        
        Args:
            model_id (int): ID модели
            
        Returns:
            Dict[str, Any]: Статистика точности модели
        """
        try:
            # Получаем среднюю точность
            avg_accuracy = self.session.query(Analytics.avg_accuracy).filter(
                Analytics.model_id == model_id
            ).first()
            
            # Получаем количество расчетов
            calculation_count = self.session.query(Coefficient).filter(
                Coefficient.model_id == model_id
            ).count()
            
            return {
                'avg_accuracy': avg_accuracy[0] if avg_accuracy else 0,
                'calculation_count': calculation_count
            }
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении статистики точности модели: {e}")
            raise
    
    # === Расширенные аналитические функции ===
    
    def get_nomenclature_trend_analysis(self, nomenclature_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Получает анализ трендов по номенклатуре за указанный период.
        
        Args:
            nomenclature_id (int): ID номенклатуры
            days (int): Количество дней для анализа (по умолчанию 30)
            
        Returns:
            Dict[str, Any]: Анализ трендов по номенклатуре
        """
        try:
            from datetime import datetime, timedelta
            
            # Определяем период анализа
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Получаем коэффициенты за период
            coefficients = self.session.query(Coefficient).join(CalculationData).filter(
                CalculationData.nomenclature_id == nomenclature_id,
                Coefficient.calculation_date >= start_date,
                Coefficient.calculation_date <= end_date
            ).order_by(Coefficient.calculation_date).all()
            
            if not coefficients:
                return {
                    'trend_data': [],
                    'trend_direction': 'unknown',
                    'avg_coefficient_a': 0,
                    'avg_coefficient_b': 0,
                    'avg_coefficient_c': 0,
                    'accuracy_trend': 'unknown'
                }
            
            # Подготавливаем данные для анализа трендов
            trend_data = []
            for coeff in coefficients:
                trend_data.append({
                    'date': coeff.calculation_date,
                    'coefficient_a': coeff.coefficient_a,
                    'coefficient_b': coeff.coefficient_b,
                    'coefficient_c': coeff.coefficient_c,
                    'accuracy': coeff.accuracy_r2
                })
            
            # Рассчитываем средние значения
            avg_coefficient_a = sum([d['coefficient_a'] for d in trend_data]) / len(trend_data)
            avg_coefficient_b = sum([d['coefficient_b'] for d in trend_data]) / len(trend_data)
            avg_coefficient_c = sum([d['coefficient_c'] for d in trend_data]) / len(trend_data)
            
            # Определяем направление тренда (простой анализ по первому и последнему значению)
            if len(coefficients) > 1:
                first_accuracy = coefficients[0].accuracy_r2
                last_accuracy = coefficients[-1].accuracy_r2
                if last_accuracy > first_accuracy:
                    accuracy_trend = 'improving'
                elif last_accuracy < first_accuracy:
                    accuracy_trend = 'deteriorating'
                else:
                    accuracy_trend = 'stable'
            else:
                accuracy_trend = 'insufficient_data'
            
            return {
                'trend_data': trend_data,
                'trend_direction': accuracy_trend,
                'avg_coefficient_a': avg_coefficient_a,
                'avg_coefficient_b': avg_coefficient_b,
                'avg_coefficient_c': avg_coefficient_c,
                'accuracy_trend': accuracy_trend,
                'analysis_period_days': days
            }
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении анализа трендов по номенклатуре: {e}")
            raise
    
    def get_model_comparison_analysis(self) -> Dict[str, Any]:
        """
        Получает сравнительный анализ всех моделей.
        
        Returns:
            Dict[str, Any]: Сравнительный анализ моделей
        """
        try:
            # Получаем все модели
            models = self.session.query(Model).all()
            
            model_stats = []
            for model in models:
                # Получаем статистику для каждой модели
                stats = self.get_model_accuracy_statistics(model.id)
                
                # Получаем количество уникальных номенклатур
                unique_nomenclatures = self.session.query(CalculationData.nomenclature_id).join(Coefficient).filter(
                    Coefficient.model_id == model.id
                ).distinct().count()
                
                model_stats.append({
                    'model_id': model.id,
                    'model_name': model.name,
                    'model_type': model.model_type,
                    'avg_accuracy': stats['avg_accuracy'],
                    'calculation_count': stats['calculation_count'],
                    'unique_nomenclatures': unique_nomenclatures
                })
            
            # Сортируем по точности
            model_stats.sort(key=lambda x: x['avg_accuracy'], reverse=True)
            
            return {
                'models': model_stats,
                'best_model': model_stats[0] if model_stats else None,
                'total_models': len(model_stats)
            }
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении сравнительного анализа моделей: {e}")
            raise
    
    def get_nomenclature_performance_report(self, limit: int = 10) -> Dict[str, Any]:
        """
        Получает отчет о производительности номенклатур.
        
        Args:
            limit (int): Количество номенклатур в отчете (по умолчанию 10)
            
        Returns:
            Dict[str, Any]: Отчет о производительности номенклатур
        """
        try:
            # Получаем номенклатуры с наибольшим количеством расчетов
            nomenclature_counts = self.session.query(
                Nomenclature.id,
                Nomenclature.name,
                func.count(CalculationData.id).label('calculation_count')
            ).join(CalculationData).group_by(
                Nomenclature.id, Nomenclature.name
            ).order_by(func.count(CalculationData.id).desc()).limit(limit).all()
            
            performance_data = []
            for nomenclature_id, name, count in nomenclature_counts:
                # Получаем статистику по номенклатуре
                stats = self.get_nomenclature_statistics(nomenclature_id)
                
                # Получаем среднюю точность из аналитики
                avg_accuracy = self.session.query(func.avg(Analytics.avg_accuracy)).filter(
                    Analytics.nomenclature_id == nomenclature_id
                ).scalar()
                
                performance_data.append({
                    'nomenclature_id': nomenclature_id,
                    'nomenclature_name': name,
                    'calculation_count': count,
                    'avg_accuracy': avg_accuracy if avg_accuracy else stats['avg_accuracy'],
                    'error_count': stats['error_count']
                })
            
            return {
                'top_performing': performance_data,
                'total_nomenclatures': len(performance_data),
                'report_limit': limit
            }
        except SQLAlchemyError as e:
            log.error(f"Ошибка при получении отчета о производительности номенклатур: {e}")
            raise

# Функции для удобного использования сервиса
def get_database_service(session: Session) -> DatabaseService:
    """
    Получает сервис базы данных.
    
    Args:
        session (Session): Сессия SQLAlchemy
        
    Returns:
        DatabaseService: Сервис базы данных
    """
    return DatabaseService(session)