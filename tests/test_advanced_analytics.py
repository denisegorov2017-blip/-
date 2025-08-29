#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для расширенных аналитических функций базы данных.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.database.database import init_database, get_db_session
from src.core.database.models import Base, Nomenclature, CalculationData, Model, Coefficient, Analytics
from src.core.database.services import get_database_service

class TestAdvancedAnalytics:
    """Тесты для расширенных аналитических функций."""
    
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
    
    def test_nomenclature_trend_analysis(self):
        """Тест анализа трендов по номенклатуре."""
        session = self.Session()
        db_service = get_database_service(session)
        
        # Создаем тестовую номенклатуру
        nomenclature = db_service.create_nomenclature(
            name="Тестовая номенклатура",
            product_type="fish_fresh"
        )
        nomenclature_id = nomenclature.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовую модель
        model = db_service.create_model(
            name="TestModel",
            model_type="exponential",
            version="1.0"
        )
        model_id = model.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовые данные для расчетов
        calculation_data = db_service.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature_id,
            initial_balance=100.0,
            incoming=20.0,
            outgoing=30.0,
            final_balance=90.0,
            storage_days=7
        )
        calculation_data_id = calculation_data.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовые коэффициенты с разной точностью для анализа тренда
        coeff1 = db_service.create_coefficient(
            calculation_data_id=calculation_data_id,
            model_id=model_id,
            coefficient_a=0.01,
            coefficient_b=0.02,
            coefficient_c=0.001,
            accuracy_r2=0.85,
            calculation_date=datetime.now() - timedelta(days=10)
        )
        
        coeff2 = db_service.create_coefficient(
            calculation_data_id=calculation_data_id,
            model_id=model_id,
            coefficient_a=0.015,
            coefficient_b=0.025,
            coefficient_c=0.0015,
            accuracy_r2=0.90,
            calculation_date=datetime.now() - timedelta(days=5)
        )
        
        coeff3 = db_service.create_coefficient(
            calculation_data_id=calculation_data_id,
            model_id=model_id,
            coefficient_a=0.02,
            coefficient_b=0.03,
            coefficient_c=0.002,
            accuracy_r2=0.95,
            calculation_date=datetime.now()
        )
        
        session.commit()
        session.close()
        
        # Тестируем анализ трендов
        session2 = self.Session()
        db_service2 = get_database_service(session2)
        
        trend_analysis = db_service2.get_nomenclature_trend_analysis(nomenclature_id, days=30)
        
        # Проверяем результаты
        assert 'trend_data' in trend_analysis
        assert len(trend_analysis['trend_data']) == 3
        assert abs(trend_analysis['avg_coefficient_a'] - 0.015) < 1e-10  # (0.01 + 0.015 + 0.02) / 3
        assert abs(trend_analysis['avg_coefficient_b'] - 0.025) < 1e-10  # (0.02 + 0.025 + 0.03) / 3
        assert abs(trend_analysis['avg_coefficient_c'] - 0.0015) < 1e-10  # (0.001 + 0.0015 + 0.002) / 3
        assert trend_analysis['accuracy_trend'] == 'improving'
        
        session2.close()
    
    def test_model_comparison_analysis(self):
        """Тест сравнительного анализа моделей."""
        session = self.Session()
        db_service = get_database_service(session)
        
        # Создаем тестовую номенклатуру
        nomenclature = db_service.create_nomenclature(
            name="Тестовая номенклатура",
            product_type="fish_fresh"
        )
        nomenclature_id = nomenclature.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем две тестовые модели
        model1 = db_service.create_model(
            name="Model1",
            model_type="exponential",
            version="1.0"
        )
        model1_id = model1.id  # Сохраняем ID перед закрытием сессии
        
        model2 = db_service.create_model(
            name="Model2",
            model_type="linear",
            version="1.0"
        )
        model2_id = model2.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовые данные для расчетов
        calculation_data1 = db_service.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature_id,
            initial_balance=100.0,
            incoming=20.0,
            outgoing=30.0,
            final_balance=90.0,
            storage_days=7
        )
        calculation_data1_id = calculation_data1.id  # Сохраняем ID перед закрытием сессии
        
        calculation_data2 = db_service.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature_id,
            initial_balance=150.0,
            incoming=25.0,
            outgoing=35.0,
            final_balance=140.0,
            storage_days=10
        )
        calculation_data2_id = calculation_data2.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовые коэффициенты для первой модели
        db_service.create_coefficient(
            calculation_data_id=calculation_data1_id,
            model_id=model1_id,
            coefficient_a=0.01,
            coefficient_b=0.02,
            coefficient_c=0.001,
            accuracy_r2=0.90
        )
        
        # Создаем тестовые коэффициенты для второй модели
        db_service.create_coefficient(
            calculation_data_id=calculation_data2_id,
            model_id=model2_id,
            coefficient_a=0.015,
            coefficient_b=0.025,
            coefficient_c=0.0015,
            accuracy_r2=0.95
        )
        
        # Создаем аналитику для моделей
        db_service.create_analytics(
            nomenclature_id=nomenclature_id,
            model_id=model1_id,
            avg_accuracy=0.90,
            total_calculations=1
        )
        
        db_service.create_analytics(
            nomenclature_id=nomenclature_id,
            model_id=model2_id,
            avg_accuracy=0.95,
            total_calculations=1
        )
        
        session.commit()
        session.close()
        
        # Тестируем сравнительный анализ моделей
        session2 = self.Session()
        db_service2 = get_database_service(session2)
        
        model_comparison = db_service2.get_model_comparison_analysis()
        
        # Проверяем результаты
        assert 'models' in model_comparison
        assert len(model_comparison['models']) == 2
        assert 'best_model' in model_comparison
        assert model_comparison['best_model'] is not None
        assert model_comparison['best_model']['model_name'] == "Model2"  # Модель с лучшей точностью
        assert abs(model_comparison['best_model']['avg_accuracy'] - 0.95) < 1e-10
        
        # Проверяем, что модели отсортированы по точности (по убыванию)
        assert model_comparison['models'][0]['avg_accuracy'] >= model_comparison['models'][1]['avg_accuracy']
        
        session2.close()
    
    def test_nomenclature_performance_report(self):
        """Тест отчета о производительности номенклатур."""
        session = self.Session()
        db_service = get_database_service(session)
        
        # Создаем тестовые номенклатуры
        nomenclature1 = db_service.create_nomenclature(
            name="Номенклатура 1",
            product_type="fish_fresh"
        )
        nomenclature1_id = nomenclature1.id  # Сохраняем ID перед закрытием сессии
        
        nomenclature2 = db_service.create_nomenclature(
            name="Номенклатура 2",
            product_type="fish_frozen"
        )
        nomenclature2_id = nomenclature2.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем тестовую модель
        model = db_service.create_model(
            name="TestModel",
            model_type="exponential",
            version="1.0"
        )
        model_id = model.id  # Сохраняем ID перед закрытием сессии
        
        # Создаем разное количество расчетных данных для каждой номенклатуры
        # Номенклатура 1 - 3 расчета
        calc_data_ids_1 = []
        for i in range(3):
            calc_data = db_service.create_calculation_data(
                source_data_id=1,
                nomenclature_id=nomenclature1_id,
                initial_balance=100.0 + i,
                incoming=20.0,
                outgoing=30.0,
                final_balance=90.0 + i,
                storage_days=7 + i
            )
            calc_data_ids_1.append(calc_data.id)  # Сохраняем ID перед закрытием сессии
            
            db_service.create_coefficient(
                calculation_data_id=calc_data.id,
                model_id=model_id,
                coefficient_a=0.01 + i*0.001,
                coefficient_b=0.02 + i*0.001,
                coefficient_c=0.001 + i*0.0001,
                accuracy_r2=0.85 + i*0.02
            )
        
        # Номенклатура 2 - 1 расчет
        calc_data2 = db_service.create_calculation_data(
            source_data_id=1,
            nomenclature_id=nomenclature2_id,
            initial_balance=150.0,
            incoming=25.0,
            outgoing=35.0,
            final_balance=140.0,
            storage_days=10
        )
        calc_data2_id = calc_data2.id  # Сохраняем ID перед закрытием сессии
        
        db_service.create_coefficient(
            calculation_data_id=calc_data2_id,
            model_id=model_id,
            coefficient_a=0.015,
            coefficient_b=0.025,
            coefficient_c=0.0015,
            accuracy_r2=0.90
        )
        
        # Создаем аналитику
        db_service.create_analytics(
            nomenclature_id=nomenclature1_id,
            model_id=model_id,
            avg_accuracy=0.89,  # Среднее из (0.85, 0.87, 0.89)
            total_calculations=3
        )
        
        db_service.create_analytics(
            nomenclature_id=nomenclature2_id,
            model_id=model_id,
            avg_accuracy=0.90,
            total_calculations=1
        )
        
        session.commit()
        session.close()
        
        # Тестируем отчет о производительности номенклатур
        session2 = self.Session()
        db_service2 = get_database_service(session2)
        
        performance_report = db_service2.get_nomenclature_performance_report(limit=10)
        
        # Проверяем результаты
        assert 'top_performing' in performance_report
        assert len(performance_report['top_performing']) == 2
        assert performance_report['total_nomenclatures'] == 2
        
        # Проверяем, что номенклатуры отсортированы по количеству расчетов (по убыванию)
        top_performing = performance_report['top_performing']
        assert top_performing[0]['nomenclature_name'] == "Номенклатура 1"  # Больше расчетов
        assert top_performing[0]['calculation_count'] == 3
        assert top_performing[1]['nomenclature_name'] == "Номенклатура 2"  # Меньше расчетов
        assert top_performing[1]['calculation_count'] == 1
        
        session2.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])