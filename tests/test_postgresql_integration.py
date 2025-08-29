#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для интеграции PostgreSQL с системой расчета коэффициентов усушки.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.database.database import init_database, get_db_session, get_database_url
from src.core.database.models import Base, Nomenclature, CalculationData, Model, Coefficient
from src.core.database.services import get_database_service
from src.core.database.integration import DatabaseIntegration, get_database_integration
from src.core.database.utils import initialize_database, test_database_connection, get_database_info
from src.core.database.timescaledb import check_timescaledb_extension, get_timescaledb_info

class TestPostgreSQLIntegration:
    """Тесты для интеграции PostgreSQL."""
    
    def setup_method(self):
        """Подготовка к тестированию."""
        # Инициализируем базу данных перед каждым тестом
        self.engine = init_database()
        self.Session = get_db_session()
    
    def teardown_method(self):
        """Очистка после тестирования."""
        # Очищаем таблицы после каждого теста только если это тестовая база
        db_url = get_database_url()
        if 'test' in db_url or 'localhost' in db_url:
            session = self.Session()
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    session.execute(table.delete())
                except Exception as e:
                    print(f"Ошибка при очистке таблицы {table.name}: {e}")
            session.commit()
            session.close()
    
    def test_postgresql_connection(self):
        """Тест подключения к PostgreSQL."""
        # Проверяем, что база данных инициализируется успешно
        assert test_database_connection() == True
        
        # Проверяем тип базы данных
        db_info = get_database_info()
        assert isinstance(db_info, dict)
        assert 'database_url' in db_info
        assert 'database_type' in db_info
        
        # Выводим информацию о базе данных для отладки
        print(f"Тип базы данных: {db_info['database_type']}")
        print(f"URL базы данных: {db_info['database_url']}")
    
    def test_database_models_with_postgresql(self):
        """Тест создания записей в таблицах базы данных с PostgreSQL."""
        session = self.Session()
        db_service = get_database_service(session)
        
        # Создаем тестовую номенклатуру
        nomenclature = db_service.create_nomenclature(
            name="Тестовая номенклатура PostgreSQL",
            product_type="fish_fresh"
        )
        
        assert nomenclature.id is not None
        assert nomenclature.name == "Тестовая номенклатура PostgreSQL"
        assert nomenclature.product_type == "fish_fresh"
        
        # Создаем тестовую модель
        model = db_service.create_model(
            name="TestModelPostgreSQL",
            model_type="exponential",
            version="1.0"
        )
        
        assert model.id is not None
        assert model.name == "TestModelPostgreSQL"
        assert model.model_type == "exponential"
        assert model.version == "1.0"
        
        # Создаем тестовые данные для расчета
        source_data = db_service.create_source_data(
            file_name="инвентаризация_postgresql.xlsx",
            file_path="исходные_данные/инвентаризация_postgresql.xlsx",
            upload_date=datetime.now(),
            processed=True,
            quality_score=0.95
        )
        
        # Создаем расчетные данные
        calculation_data = db_service.create_calculation_data(
            source_data_id=source_data.id,
            nomenclature_id=nomenclature.id,
            initial_balance=100.0,
            incoming=20.0,
            outgoing=30.0,
            final_balance=85.0,
            storage_days=7,
            calculation_date=datetime.now(),
            data_quality_flag='clean',
            inventory_confidence=0.9,
            inventory_period_start=datetime.now() - timedelta(days=7),
            inventory_period_end=datetime.now()
        )
        
        assert calculation_data.id is not None
        
        # Создаем коэффициенты
        coefficient = db_service.create_coefficient(
            calculation_data_id=calculation_data.id,
            model_id=model.id,
            coefficient_a=0.02,
            coefficient_b=0.049,
            coefficient_c=0.001,
            accuracy_r2=0.95,
            calculation_date=datetime.now()
        )
        
        assert coefficient.id is not None
        
        session.close()
    
    def test_timescaledb_integration(self):
        """Тест интеграции TimescaleDB."""
        # Проверяем доступность TimescaleDB
        timescaledb_available = check_timescaledb_extension()
        
        # Получаем информацию о TimescaleDB
        timescaledb_info = get_timescaledb_info()
        
        # Выводим информацию для отладки
        print(f"TimescaleDB доступен: {timescaledb_available}")
        print(f"Информация о TimescaleDB: {timescaledb_info}")
        
        # Проверяем структуру ответа
        assert isinstance(timescaledb_info, dict)
        assert 'timescaledb_available' in timescaledb_info
        
        # Если TimescaleDB доступен, проверяем дополнительные поля
        if timescaledb_available:
            assert 'version' in timescaledb_info
            assert 'hypertables' in timescaledb_info

    def test_database_integration_singleton(self):
        """Тест синглтона интеграции с базой данных."""
        # Проверяем, что получаем один и тот же экземпляр
        integration1 = get_database_integration()
        integration2 = get_database_integration()
        
        assert integration1 is integration2
    
    def test_database_integration_disabled(self):
        """Тест интеграции с базой данных когда она отключена."""
        # Создаем интеграцию с отключенной базой данных
        integration = DatabaseIntegration()
        integration.enabled = False
        
        # Проверяем, что методы возвращают корректные значения когда база отключена
        result = integration.save_calculation_results(
            source_filename="test.xlsx",
            dataset=pd.DataFrame(),
            coefficients_results=[],
            error_results=[]
        )
        assert result == True  # Должно возвращать True даже когда база отключена
        
        historical_data = integration.load_historical_data("Тестовая номенклатура")
        assert historical_data == []  # Должно возвращать пустой список
        
        coefficients = integration.get_nomenclature_coefficients("Тестовая номенклатура")
        assert coefficients == []  # Должно возвращать пустой список
        
        stats = integration.get_nomenclature_statistics("Тестовая номенклатура")
        assert stats == {}  # Должно возвращать пустой словарь

if __name__ == '__main__':
    pytest.main([__file__, '-v'])