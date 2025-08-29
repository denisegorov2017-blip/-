#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели данных для базы данных системы расчета коэффициентов усушки.

Этот файл определяет структуры данных, используемые в проекте для хранения
информации о расчетах коэффициентов усушки, номенклатуре, моделях и результатах.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class SourceData(Base):
    """
    Хранит информацию об исходных файлах данных.
    """
    __tablename__ = 'source_data'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_hash = Column(String)
    processed = Column(Boolean, default=False)
    quality_score = Column(Float)

class Nomenclature(Base):
    """
    Хранит информацию о номенклатурных позициях.
    """
    __tablename__ = 'nomenclature'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    product_type = Column(String)
    product_type_code = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    validation_flags = Column(String)

class CalculationData(Base):
    """
    Хранит нормализованные данные для расчетов.
    """
    __tablename__ = 'calculation_data'
    
    id = Column(Integer, primary_key=True)
    source_data_id = Column(Integer, ForeignKey('source_data.id'))
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'))
    initial_balance = Column(Float)
    incoming = Column(Float)
    outgoing = Column(Float)
    final_balance = Column(Float)
    storage_days = Column(Integer)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    data_quality_flag = Column(String)
    inventory_confidence = Column(Float)
    inventory_period_start = Column(DateTime)
    inventory_period_end = Column(DateTime)
    is_valid_inventory_period = Column(Boolean)
    is_preliminary_forecast = Column(Boolean)
    preliminary_period_end = Column(DateTime)
    human_error_probability = Column(Float)
    validation_errors = Column(Text)
    manual_review_required = Column(Boolean)
    pre_shrinkage_days = Column(Integer)
    pre_shrinkage_amount = Column(Float)
    adjusted_shrinkage_rate = Column(Float)
    inventory_shrinkage_total = Column(Float)
    actual_deduction_batch = Column(String)
    fifo_principle_applied = Column(Boolean)
    fifo_batch_sequence = Column(JSON)

class Model(Base):
    """
    Хранит информацию о моделях расчета.
    """
    __tablename__ = 'models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model_type = Column(String)
    description = Column(Text)
    version = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)

class Coefficient(Base):
    """
    Хранит рассчитанные коэффициенты.
    """
    __tablename__ = 'coefficients'
    
    id = Column(Integer, primary_key=True)
    calculation_data_id = Column(Integer, ForeignKey('calculation_data.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    coefficient_a = Column(Float)
    coefficient_b = Column(Float)
    coefficient_c = Column(Float)
    accuracy_r2 = Column(Float)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    adjusted_for_pre_shrinkage = Column(Boolean)
    pre_shrinkage_factor = Column(Float)
    effective_shrinkage_rate = Column(Float)

class Forecast(Base):
    """
    Хранит прогнозы усушки.
    """
    __tablename__ = 'forecasts'
    
    id = Column(Integer, primary_key=True)
    coefficient_id = Column(Integer, ForeignKey('coefficients.id'))
    forecast_value = Column(Float)
    actual_value = Column(Float)
    deviation = Column(Float)
    forecast_date = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    """
    Хранит агрегированные данные для анализа.
    """
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    avg_accuracy = Column(Float)
    total_calculations = Column(Integer)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)

class AIPattern(Base):
    """
    Хранит паттерны и аномалии, найденные с помощью ИИ.
    """
    __tablename__ = 'ai_patterns'
    
    id = Column(Integer, primary_key=True)
    pattern_type = Column(String)
    description = Column(Text)
    confidence_level = Column(Float)
    affected_nomenclature = Column(String)
    discovery_date = Column(DateTime, default=datetime.utcnow)
    pattern_data = Column(JSON)

class ValidationError(Base):
    """
    Хранит информацию об ошибках, найденных в данных.
    """
    __tablename__ = 'validation_errors'
    
    id = Column(Integer, primary_key=True)
    calculation_data_id = Column(Integer, ForeignKey('calculation_data.id'))
    error_type = Column(String)
    description = Column(Text)
    severity_level = Column(String)
    detected_by = Column(String)
    detection_date = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolution_date = Column(DateTime)
    notes = Column(Text)

class PriorityPeriod(Base):
    """
    Хранит информацию о периодах с повышенным приоритетом для анализа.
    """
    __tablename__ = 'priority_periods'
    
    id = Column(Integer, primary_key=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    priority_level = Column(Integer)
    description = Column(Text)
    created_by = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

class PreliminaryForecast(Base):
    """
    Хранит информацию о предварительных прогнозах усушки.
    """
    __tablename__ = 'preliminary_forecasts'
    
    id = Column(Integer, primary_key=True)
    calculation_data_id = Column(Integer, ForeignKey('calculation_data.id'))
    forecast_model_id = Column(Integer, ForeignKey('models.id'))
    forecast_period_days = Column(Integer)
    expected_shrinkage = Column(Float)
    confidence_level = Column(Float)
    forecast_date = Column(DateTime, default=datetime.utcnow)
    actual_shrinkage = Column(Float)
    forecast_accuracy = Column(Float)
    notes = Column(Text)
    pre_shrinkage_adjusted = Column(Boolean)
    adjusted_expected_shrinkage = Column(Float)
    batch_storage_history = Column(JSON)

class SurplusSpecification(Base):
    """
    Хранит информацию о периодических указаниях излишков для товаров.
    """
    __tablename__ = 'surplus_specifications'
    
    id = Column(Integer, primary_key=True)
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'))
    surplus_percentage = Column(Float)
    specification_start_date = Column(DateTime)
    specification_end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    notes = Column(Text)

class SurplusRecommendation(Base):
    """
    Хранит автоматически сгенерированные рекомендации по излишкам.
    """
    __tablename__ = 'surplus_recommendations'
    
    id = Column(Integer, primary_key=True)
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'))
    recommended_surplus_percentage = Column(Float)
    confidence_level = Column(Float)
    analysis_period_start = Column(DateTime)
    analysis_period_end = Column(DateTime)
    calculation_method = Column(String)
    supporting_data = Column(JSON)
    created_date = Column(DateTime, default=datetime.utcnow)
    is_accepted = Column(Boolean, default=False)
    acceptance_date = Column(DateTime)

class SurplusPattern(Base):
    """
    Хранит информацию о постоянных паттернах излишков.
    """
    __tablename__ = 'surplus_patterns'
    
    id = Column(Integer, primary_key=True)
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'), nullable=True)
    product_type = Column(String)
    surplus_percentage = Column(Float)
    pattern_condition = Column(String)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_from_recommendation_id = Column(Integer, ForeignKey('surplus_recommendations.id'))
    validation_count = Column(Integer, default=0)
    last_validated_date = Column(DateTime)
    confidence_level = Column(Float)
    feedback_count = Column(Integer, default=0)
    last_feedback_date = Column(DateTime)

class PatternValidation(Base):
    """
    Хранит результаты валидации и обратной связи по автоматическим паттернам.
    """
    __tablename__ = 'pattern_validations'
    
    id = Column(Integer, primary_key=True)
    surplus_pattern_id = Column(Integer, ForeignKey('surplus_patterns.id'))
    validation_date = Column(DateTime, default=datetime.utcnow)
    actual_surplus_percentage = Column(Float)
    predicted_surplus_percentage = Column(Float)
    deviation = Column(Float)
    validation_result = Column(String)
    user_feedback = Column(Text)
    is_confirmed = Column(Boolean, default=False)
    confirmation_date = Column(DateTime)

class FeedbackPreference(Base):
    """
    Хранит гибкие настройки обратной связи.
    """
    __tablename__ = 'feedback_preferences'
    
    id = Column(Integer, primary_key=True)
    feedback_frequency = Column(String)
    auto_confirm_threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow)

class DataLineage(Base):
    """
    Хранит информацию о происхождении данных для целей аудита.
    """
    __tablename__ = 'data_lineage'
    
    id = Column(Integer, primary_key=True)
    source_file_id = Column(Integer, ForeignKey('source_data.id'))
    calculation_data_id = Column(Integer, ForeignKey('calculation_data.id'))
    process_name = Column(String)
    process_timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    input_records = Column(Integer)
    output_records = Column(Integer)
    status = Column(String)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    version = Column(String)

class MLModelRegistry(Base):
    """
    Хранит информацию о версиях различных моделей расчета усушки.
    """
    __tablename__ = 'ml_model_registry'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    version = Column(String)
    algorithm_type = Column(String)
    parameters = Column(JSON)
    training_date = Column(DateTime)
    accuracy_metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_by = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)