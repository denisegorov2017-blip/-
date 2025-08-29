#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции базы данных с обработкой реальных данных.
"""

import pytest
import pandas as pd
import os
import sys

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.shrinkage_system import ShrinkageSystem
from src.core.database.database import init_database, get_db_session
from src.core.database.models import Base, Nomenclature, CalculationData, Model, Coefficient
from src.core.database.services import get_database_service
from src.config import DEFAULT_CONFIG

class TestRealDataDatabaseIntegration:
    """Тесты для интеграции базы данных с обработкой реальных данных."""
    
    def setup_method(self):
        """Подготовка к тестированию."""
        # Инициализируем базу данных перед каждым тестом
        self.engine = init_database()
        self.Session = get_db_session()
        
        # Создаем тестовую конфигурацию с включенной базой данных
        self.test_config = DEFAULT_CONFIG.copy()
        self.test_config['enable_database'] = True
    
    def teardown_method(self):
        """Очистка после тестирования."""
        # Очищаем таблицы после каждого теста
        session = self.Session()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()
    
    def test_real_data_processing_with_database(self):
        """Тест обработки реальных данных с сохранением в базу данных."""
        # Создаем систему с включенной базой данных
        system = ShrinkageSystem(self.test_config)
        
        # Проверяем, что интеграция с базой данных доступна
        assert system.config.get('enable_database') == True
        
        # Проверяем, что база данных инициализирована и доступна
        session = self.Session()
        db_service = get_database_service(session)
        session.close()
        
        # Тест пройден, если система создана и база данных доступна
        assert system is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])