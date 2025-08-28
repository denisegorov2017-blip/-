#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для генерации отчетов и сводной статистики.

Отвечает за создание HTML-отчетов и вычисление итоговых метрик
на основе результатов расчетов.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log
from core.shrinkage_html_reporter import ShrinkageHTMLReporter
from core.test_data_manager import TestDataManager


class ReportGenerator:
    """
    Генерирует отчеты и сводную статистику по результатам расчетов.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализирует генератор отчетов с заданной конфигурацией.

        Args:
            config (Dict[str, Any]): Словарь с настройками, например, output_dir.
        """
        self.config = config
        self.reporter = ShrinkageHTMLReporter()
        self.test_data_manager = TestDataManager(config.get('output_dir', 'результаты'))
        log.info("ReportGenerator инициализирован.")

    def generate(self, 
                 coefficients: List[Dict[str, Any]], 
                 source_filename: str,
                 preliminary: List[Dict[str, Any]] = None,
                 errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Основной метод для генерации всех отчетов и сводок.

        Args:
            coefficients (List[Dict[str, Any]]): Результаты расчета коэффициентов.
            source_filename (str): Имя исходного файла для именования отчетов.
            preliminary (List[Dict[str, Any]], optional): Результаты предварительного расчета. Defaults to None.
            errors (List[Dict[str, Any]], optional): Информация об ошибках. Defaults to None.

        Returns:
            Dict[str, Any]: Словарь, содержащий пути к отчетам и сводную статистику.
        """
        if preliminary is None:
            preliminary = []
            
        if errors is None:
            errors = []
            
        output_dir = self.config.get('output_dir', 'результаты')
        
        # Определяем, является ли это тестовыми данными
        is_test_data = self._is_test_data(source_filename)
        target_dir = self.test_data_manager.test_subdir if is_test_data else output_dir
        
        log.info("Генерация HTML отчетов...")
        reports = self._generate_reports(coefficients, preliminary, errors, target_dir, source_filename)
        
        log.info("Генерация сводной статистики...")
        summary = self._generate_summary(coefficients, preliminary, errors)
        
        return {
            'reports': reports,
            'summary': summary
        }

    def _generate_reports(self, 
                          coefficients: List[Dict[str, Any]], 
                          preliminary: List[Dict[str, Any]],
                          errors: List[Dict[str, Any]],
                          output_dir: str, 
                          source_filename: str) -> Dict[str, str]:
        """Генерирует HTML отчеты."""
        os.makedirs(output_dir, exist_ok=True)
        base_name = Path(source_filename).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports = {}
        
        if coefficients:
            coefficients_path = os.path.join(output_dir, f"коэффициенты_усушки_{base_name}_{timestamp}.html")
            self.reporter.generate_coefficients_report(coefficients, coefficients_path, "Коэффициенты усушки (автоматический расчет)")
            reports['coefficients'] = coefficients_path
        
        # Генерируем отчет об ошибках, если есть
        if errors:
            errors_path = os.path.join(output_dir, f"ошибки_расчета_{base_name}_{timestamp}.html")
            self.reporter.generate_errors_report(errors, errors_path, "Ошибки расчета усушки")
            reports['errors'] = errors_path
            
        # Логика для предварительных отчетов, если она будет возвращена
        # if preliminary:
        #     preliminary_path = os.path.join(output_dir, f"предварительный_расчет_{base_name}_{timestamp}.html")
        #     # self.reporter.generate_preliminary_report(preliminary, preliminary_path, "Предварительный расчет усушки")
        #     reports['preliminary'] = preliminary_path
            
        return reports

    def _generate_summary(self, 
                          coefficients: List[Dict[str, Any]], 
                          preliminary: List[Dict[str, Any]],
                          errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует сводную статистику."""
        if not coefficients:
            return {'total_positions': 0, 'avg_accuracy': 0, 'error_count': len(errors)}
        
        accuracies = [r.get('Точность', 0) for r in coefficients if r.get('Точность', 0) > 0]
        return {
            'total_positions': len(coefficients),
            'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            'error_count': len(errors)
        }
    
    def _is_test_data(self, source_filename: str) -> bool:
        """
        Определяет, являются ли данные тестовыми.

        Args:
            source_filename (str): Имя исходного файла

        Returns:
            bool: True, если данные тестовые
        """
        test_indicators = [
            'test', 'тест', 'fish_batch_test', 'sample', 'пример'
        ]
        
        filename_lower = source_filename.lower()
        return any(indicator in filename_lower for indicator in test_indicators)