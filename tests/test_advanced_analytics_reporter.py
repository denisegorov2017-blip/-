#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для расширенного аналитического репортера.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter


class TestAdvancedAnalyticsReporter:
    """Тесты для расширенного аналитического репортера."""
    
    def setup_method(self):
        """Подготовка к тестированию."""
        self.config = {
            'output_dir': 'test_results'
        }
        self.reporter = AdvancedAnalyticsReporter(self.config)
    
    def test_initialization(self):
        """Тест инициализации репортера."""
        assert self.reporter.config == self.config
        assert self.reporter.output_dir == 'test_results'
    
    @patch('src.core.advanced_analytics_reporter.get_db_session')
    @patch('src.core.advanced_analytics_reporter.get_database_service')
    def test_generate_trend_analysis_report(self, mock_get_db_service, mock_get_db_session):
        """Тест генерации отчета о трендах."""
        # Мокаем сессию базы данных
        mock_session = Mock()
        mock_get_db_session.return_value = Mock(return_value=mock_session)
        
        # Мокаем сервис базы данных
        mock_db_service = Mock()
        mock_db_service.get_nomenclature_trend_analysis.return_value = {
            'trend_data': [
                {
                    'date': datetime(2023, 1, 1),
                    'coefficient_a': 0.01,
                    'coefficient_b': 0.02,
                    'coefficient_c': 0.001,
                    'accuracy': 0.85
                }
            ],
            'trend_direction': 'improving',
            'avg_coefficient_a': 0.01,
            'avg_coefficient_b': 0.02,
            'avg_coefficient_c': 0.001,
            'accuracy_trend': 'improving',
            'analysis_period_days': 30
        }
        mock_get_db_service.return_value = mock_db_service
        
        # Тестируем генерацию отчета
        try:
            report_path = self.reporter.generate_trend_analysis_report(
                nomenclature_id=1,
                nomenclature_name="Тестовая номенклатура",
                days=30
            )
            
            # Проверяем, что отчет был создан
            assert isinstance(report_path, str)
            assert report_path.endswith('.html')
            
            # Проверяем, что файл существует
            assert os.path.exists(report_path)
            
            # Удаляем тестовый файл
            os.remove(report_path)
            
        except Exception as e:
            pytest.fail(f"Ошибка при генерации отчета о трендах: {e}")
    
    @patch('src.core.advanced_analytics_reporter.get_db_session')
    @patch('src.core.advanced_analytics_reporter.get_database_service')
    def test_generate_model_comparison_report(self, mock_get_db_service, mock_get_db_session):
        """Тест генерации отчета о сравнении моделей."""
        # Мокаем сессию базы данных
        mock_session = Mock()
        mock_get_db_session.return_value = Mock(return_value=mock_session)
        
        # Мокаем сервис базы данных
        mock_db_service = Mock()
        mock_db_service.get_model_comparison_analysis.return_value = {
            'models': [
                {
                    'model_id': 1,
                    'model_name': 'Model1',
                    'model_type': 'exponential',
                    'avg_accuracy': 90.0,
                    'calculation_count': 10,
                    'unique_nomenclatures': 5
                },
                {
                    'model_id': 2,
                    'model_name': 'Model2',
                    'model_type': 'linear',
                    'avg_accuracy': 85.0,
                    'calculation_count': 8,
                    'unique_nomenclatures': 4
                }
            ],
            'best_model': {
                'model_id': 1,
                'model_name': 'Model1',
                'model_type': 'exponential',
                'avg_accuracy': 90.0,
                'calculation_count': 10,
                'unique_nomenclatures': 5
            },
            'total_models': 2
        }
        mock_get_db_service.return_value = mock_db_service
        
        # Тестируем генерацию отчета
        try:
            report_path = self.reporter.generate_model_comparison_report()
            
            # Проверяем, что отчет был создан
            assert isinstance(report_path, str)
            assert report_path.endswith('.html')
            
            # Проверяем, что файл существует
            assert os.path.exists(report_path)
            
            # Удаляем тестовый файл
            os.remove(report_path)
            
        except Exception as e:
            pytest.fail(f"Ошибка при генерации отчета о сравнении моделей: {e}")
    
    @patch('src.core.advanced_analytics_reporter.get_db_session')
    @patch('src.core.advanced_analytics_reporter.get_database_service')
    def test_generate_nomenclature_performance_report(self, mock_get_db_service, mock_get_db_session):
        """Тест генерации отчета о производительности номенклатур."""
        # Мокаем сессию базы данных
        mock_session = Mock()
        mock_get_db_session.return_value = Mock(return_value=mock_session)
        
        # Мокаем сервис базы данных
        mock_db_service = Mock()
        mock_db_service.get_nomenclature_performance_report.return_value = {
            'top_performing': [
                {
                    'nomenclature_id': 1,
                    'nomenclature_name': 'Номенклатура 1',
                    'calculation_count': 10,
                    'avg_accuracy': 90.0,
                    'error_count': 1
                },
                {
                    'nomenclature_id': 2,
                    'nomenclature_name': 'Номенклатура 2',
                    'calculation_count': 8,
                    'avg_accuracy': 85.0,
                    'error_count': 2
                }
            ],
            'total_nomenclatures': 2,
            'report_limit': 10
        }
        mock_get_db_service.return_value = mock_db_service
        
        # Тестируем генерацию отчета
        try:
            report_path = self.reporter.generate_nomenclature_performance_report(limit=10)
            
            # Проверяем, что отчет был создан
            assert isinstance(report_path, str)
            assert report_path.endswith('.html')
            
            # Проверяем, что файл существует
            assert os.path.exists(report_path)
            
            # Удаляем тестовый файл
            os.remove(report_path)
            
        except Exception as e:
            pytest.fail(f"Ошибка при генерации отчета о производительности номенклатур: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])