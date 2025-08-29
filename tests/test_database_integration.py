#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для интеграции базы данных с системой расчета коэффициентов усушки.
"""

import pytest
import pandas as pd
from datetime import datetime
import os
import sys

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.database.database import init_database, get_db_session
from src.core.database.models import Base, Nomenclature, CalculationData, Model, Coefficient
from src.core.database.services import get_database_service
from src.core.database.integration import DatabaseIntegration, get_database_integration
from src.core.database.utils import initialize_database, test_database_connection, get_database_info

class TestDatabaseIntegration:
    """Тесты для интеграции базы данных."""
    
    def setup_method(self):
        """Подготовка к тестированию."""
        # Инициализируем базу данных перед каждым тестом
        self.engine = init_database()
        self.Session = get_db_session()
    
    def teardown_method(self):
        """Очистка после тестирования."""
        # Очищаем таблицы после каждого теста
        session = self.Session()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()
    
    def test_database_initialization(self):
        """Тест инициализации базы данных."""
        # Проверяем, что база данных инициализируется успешно
        assert test_database_connection() == True
        
        # Проверяем, что можем получить информацию о базе данных
        info = get_database_info()
        assert isinstance(info, dict)
        assert 'database_url' in info
        assert 'size_bytes' in info
    
    def test_database_models_creation(self):
        """Тест создания записей в таблицах базы данных."""
        session = self.Session()
        db_service = get_database_service(session)
        
        # Создаем тестовую номенклатуру
        nomenclature = db_service.create_nomenclature(
            name="Тестовая номенклатура",
            product_type="fish_fresh"
        )
        
        assert nomenclature.id is not None
        assert nomenclature.name == "Тестовая номенклатура"
        assert nomenclature.product_type == "fish_fresh"
        
        # Создаем тестовую модель
        model = db_service.create_model(
            name="TestModel",
            model_type="exponential",
            version="1.0"
        )
        
        assert model.id is not None
        assert model.name == "TestModel"
        assert model.model_type == "exponential"
        assert model.version == "1.0"
        
        session.close()
    
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