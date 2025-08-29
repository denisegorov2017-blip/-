#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы с TimescaleDB.

Этот файл предоставляет функции для интеграции TimescaleDB с существующей системой базы данных.
"""

from sqlalchemy import text
from src.logger_config import log
from src.core.database.database import get_db_session

def check_timescaledb_extension() -> bool:
    """
    Проверяет, доступно ли расширение TimescaleDB.
    
    Returns:
        bool: True, если расширение доступно
    """
    try:
        Session = get_db_session()
        session = Session()
        
        # Проверяем наличие расширения TimescaleDB
        result = session.execute(text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'"))
        extension_exists = result.fetchone() is not None
        
        session.close()
        
        if extension_exists:
            log.info("Расширение TimescaleDB доступно")
        else:
            log.warning("Расширение TimescaleDB не установлено")
            
        return extension_exists
    except Exception as e:
        log.error(f"Ошибка при проверке расширения TimescaleDB: {e}")
        return False

def create_hypertable(table_name: str, time_column: str = 'calculation_date') -> bool:
    """
    Создает гипертаблицу TimescaleDB для указанной таблицы.
    
    Args:
        table_name (str): Имя таблицы
        time_column (str): Имя временной колонки (по умолчанию 'calculation_date')
        
    Returns:
        bool: True, если гипертаблица создана успешно
    """
    try:
        # Проверяем, доступно ли расширение TimescaleDB
        if not check_timescaledb_extension():
            log.warning("Невозможно создать гипертаблицу: расширение TimescaleDB не доступно")
            return False
            
        Session = get_db_session()
        session = Session()
        
        # Проверяем, является ли таблица уже гипертаблицей
        result = session.execute(text(
            "SELECT hypertable_name FROM timescaledb_information.hypertables "
            "WHERE hypertable_name = :table_name"
        ), {'table_name': table_name})
        
        is_hypertable = result.fetchone() is not None
        
        if is_hypertable:
            log.info(f"Таблица {table_name} уже является гипертаблицей")
            session.close()
            return True
            
        # Создаем гипертаблицу
        session.execute(text(
            f"SELECT create_hypertable('{table_name}', '{time_column}', if_not_exists => TRUE)"
        ))
        session.commit()
        session.close()
        
        log.success(f"Гипертаблица для {table_name} создана успешно")
        return True
    except Exception as e:
        log.error(f"Ошибка при создании гипертаблицы для {table_name}: {e}")
        try:
            session.close()
        except:
            pass
        return False

def optimize_with_timescaledb() -> bool:
    """
    Оптимизирует таблицы с использованием TimescaleDB.
    
    Returns:
        bool: True, если оптимизация успешна
    """
    try:
        # Таблицы, которые могут быть оптимизированы как гипертаблицы
        hypertable_candidates = [
            ('calculation_data', 'calculation_date'),
            ('coefficients', 'calculation_date'),
            ('forecasts', 'forecast_date'),
            ('analytics', 'last_updated'),
            ('ai_patterns', 'discovery_date'),
            ('validation_errors', 'detection_date'),
            ('priority_periods', 'created_date'),
            ('preliminary_forecasts', 'forecast_date'),
            ('surplus_specifications', 'created_date'),
            ('surplus_recommendations', 'created_date'),
            ('surplus_patterns', 'created_date'),
            ('pattern_validations', 'validation_date'),
            ('feedback_preferences', 'updated_date'),
            ('data_lineage', 'process_timestamp'),
            ('ml_model_registry', 'created_date')
        ]
        
        success_count = 0
        for table_name, time_column in hypertable_candidates:
            if create_hypertable(table_name, time_column):
                success_count += 1
                
        log.info(f"Оптимизировано {success_count} из {len(hypertable_candidates)} таблиц с помощью TimescaleDB")
        return success_count > 0
    except Exception as e:
        log.error(f"Ошибка при оптимизации с TimescaleDB: {e}")
        return False

def get_timescaledb_info() -> dict:
    """
    Получает информацию о TimescaleDB.
    
    Returns:
        dict: Словарь с информацией о TimescaleDB
    """
    try:
        if not check_timescaledb_extension():
            return {
                'timescaledb_available': False,
                'hypertables': [],
                'version': None
            }
            
        Session = get_db_session()
        session = Session()
        
        # Получаем версию TimescaleDB
        version_result = session.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'"))
        version = version_result.fetchone()
        version = version[0] if version else None
        
        # Получаем список гипертаблиц
        hypertables_result = session.execute(text(
            "SELECT hypertable_name, num_dimensions FROM timescaledb_information.hypertables"
        ))
        hypertables = [{'name': row[0], 'dimensions': row[1]} for row in hypertables_result.fetchall()]
        
        session.close()
        
        return {
            'timescaledb_available': True,
            'version': version,
            'hypertables': hypertables,
            'hypertables_count': len(hypertables)
        }
    except Exception as e:
        log.error(f"Ошибка при получении информации о TimescaleDB: {e}")
        return {
            'timescaledb_available': False,
            'error': str(e)
        }