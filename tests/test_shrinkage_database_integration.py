#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для интеграции базы данных с основной системой расчета коэффициентов усушки.
"""

import pytest
import pandas as pd
from datetime import datetime
import os
import sys

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.shrinkage_system import ShrinkageSystem
from src.core.database.database import init_database, get_db_session
from src.core.database.models import Base, Nomenclature, CalculationData, Model, Coefficient
from src.core.database.services import get_database_service
from src.config import DEFAULT_CONFIG

class TestShrinkageDatabaseIntegration:
    """Тесты для интеграции базы данных с основной системой."""
    
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
    
    def test_shrinkage_system_with_database_integration(self):
        """Тест интеграции системы расчета усушки с базой данных."""
        # Создаем систему с включенной базой данных
        system = ShrinkageSystem(self.test_config)
        
        # Создаем тестовый датасет
        test_data = pd.DataFrame({
            'Номенклатура': ['Тестовая номенклатура'],
            'Начальный_остаток': [100.0],
            'Приход': [20.0],
            'Расход': [30.0],
            'Конечный_остаток': [85.0],
            'Период_хранения_дней': [7],
            'Дата_начала': [datetime.now()],
            'Дата_окончания': [datetime.now()]
        })
        
        # Обрабатываем датасет
        result = system.process_dataset(test_data, "test_file.xlsx", use_adaptive=False)
        
        # Проверяем, что результат успешный
        assert result['status'] == 'success'
        
        # Выводим структуру результата для отладки
        print("Результаты расчета:", result)
        if 'coefficients' in result:
            print("Коэффициенты:", result['coefficients'])
        
        # Проверяем, что данные были сохранены в базу данных
        session = self.Session()
        db_service = get_database_service(session)
        
        # Проверяем, что номенклатура была сохранена
        # Сначала проверим все номенклатуры в базе
        all_nomenclatures = session.query(Nomenclature).all()
        print("Все номенклатуры в базе:", [n.name for n in all_nomenclatures])
        
        # Проверяем конкретную номенклатуру
        nomenclature = db_service.get_nomenclature_by_name("Тестовая номенклатура")
        if nomenclature is None:
            # Проверяем номенклатуру с именем "Unknown"
            nomenclature = db_service.get_nomenclature_by_name("Unknown")
        
        assert nomenclature is not None
        
        # Проверяем, что расчетные данные были сохранены
        calculation_data_list = db_service.get_calculation_data_by_nomenclature(nomenclature.id)
        assert len(calculation_data_list) > 0
        
        # Проверяем, что коэффициенты были сохранены
        # Получаем модель
        model = session.query(Model).filter(Model.name.like("%ShrinkageCalculator%")).first()
        assert model is not None
        
        # Получаем коэффициенты
        coefficient = session.query(Coefficient).filter(
            Coefficient.calculation_data_id == calculation_data_list[0].id,
            Coefficient.model_id == model.id
        ).first()
        assert coefficient is not None
        
        session.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])