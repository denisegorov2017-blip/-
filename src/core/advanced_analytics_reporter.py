#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для генерации расширенных аналитических отчетов.

Этот модуль предоставляет функции для создания отчетов на основе расширенной аналитики,
включая трендовый анализ, сравнение моделей и отчеты о производительности номенклатур.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import json

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log
from core.database.database import get_db_session
from core.database.services import get_database_service


class AdvancedAnalyticsReporter:
    """
    Генератор расширенных аналитических отчетов на основе данных из базы данных.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализирует генератор расширенных аналитических отчетов.

        Args:
            config (Dict[str, Any]): Словарь с настройками.
        """
        self.config = config
        self.output_dir = config.get('output_dir', 'результаты')
        log.info("AdvancedAnalyticsReporter инициализирован.")

    def generate_trend_analysis_report(self, 
                                     nomenclature_id: int, 
                                     nomenclature_name: str,
                                     days: int = 30,
                                     output_dir: Optional[str] = None) -> str:
        """
        Генерирует отчет о трендах для указанной номенклатуры.

        Args:
            nomenclature_id (int): ID номенклатуры
            nomenclature_name (str): Название номенклатуры
            days (int): Количество дней для анализа (по умолчанию 30)
            output_dir (Optional[str]): Директория для сохранения отчета

        Returns:
            str: Путь к сгенерированному отчету
        """
        try:
            # Получаем данные для анализа
            Session = get_db_session()
            session = Session()
            db_service = get_database_service(session)
            
            trend_analysis = db_service.get_nomenclature_trend_analysis(nomenclature_id, days)
            
            session.close()
            
            # Создаем директорию для отчетов если она не существует
            target_dir = output_dir or self.output_dir
            os.makedirs(target_dir, exist_ok=True)
            
            # Генерируем HTML отчет
            report_path = os.path.join(
                target_dir, 
                f"трендовый_анализ_{nomenclature_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            html_content = self._generate_trend_analysis_html(trend_analysis, nomenclature_name, days)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.success(f"Отчет о трендах для номенклатуры '{nomenclature_name}' сохранен в {report_path}")
            return report_path
            
        except Exception as e:
            log.error(f"Ошибка при генерации отчета о трендах: {e}")
            raise

    def generate_model_comparison_report(self, output_dir: Optional[str] = None) -> str:
        """
        Генерирует отчет о сравнении моделей.

        Args:
            output_dir (Optional[str]): Директория для сохранения отчета

        Returns:
            str: Путь к сгенерированному отчету
        """
        try:
            # Получаем данные для анализа
            Session = get_db_session()
            session = Session()
            db_service = get_database_service(session)
            
            model_comparison = db_service.get_model_comparison_analysis()
            
            session.close()
            
            # Создаем директорию для отчетов если она не существует
            target_dir = output_dir or self.output_dir
            os.makedirs(target_dir, exist_ok=True)
            
            # Генерируем HTML отчет
            report_path = os.path.join(
                target_dir, 
                f"сравнение_моделей_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            html_content = self._generate_model_comparison_html(model_comparison)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.success(f"Отчет о сравнении моделей сохранен в {report_path}")
            return report_path
            
        except Exception as e:
            log.error(f"Ошибка при генерации отчета о сравнении моделей: {e}")
            raise

    def generate_nomenclature_performance_report(self, 
                                               limit: int = 10,
                                               output_dir: Optional[str] = None) -> str:
        """
        Генерирует отчет о производительности номенклатур.

        Args:
            limit (int): Количество номенклатур в отчете (по умолчанию 10)
            output_dir (Optional[str]): Директория для сохранения отчета

        Returns:
            str: Путь к сгенерированному отчету
        """
        try:
            # Получаем данные для анализа
            Session = get_db_session()
            session = Session()
            db_service = get_database_service(session)
            
            performance_report = db_service.get_nomenclature_performance_report(limit)
            
            session.close()
            
            # Создаем директорию для отчетов если она не существует
            target_dir = output_dir or self.output_dir
            os.makedirs(target_dir, exist_ok=True)
            
            # Генерируем HTML отчет
            report_path = os.path.join(
                target_dir, 
                f"производительность_номенклатур_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            html_content = self._generate_nomenclature_performance_html(performance_report, limit)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log.success(f"Отчет о производительности номенклатур сохранен в {report_path}")
            return report_path
            
        except Exception as e:
            log.error(f"Ошибка при генерации отчета о производительности номенклатур: {e}")
            raise

    def generate_comprehensive_analytics_report(self, 
                                              output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Генерирует комплексный аналитический отчет со всеми видами аналитики.

        Args:
            output_dir (Optional[str]): Директория для сохранения отчетов

        Returns:
            Dict[str, str]: Словарь с путями к сгенерированным отчетам
        """
        try:
            reports = {}
            
            # Генерируем отчет о сравнении моделей
            reports['model_comparison'] = self.generate_model_comparison_report(output_dir)
            
            # Генерируем отчет о производительности номенклатур
            reports['nomenclature_performance'] = self.generate_nomenclature_performance_report(20, output_dir)
            
            log.success("Комплексный аналитический отчет сгенерирован")
            return reports
            
        except Exception as e:
            log.error(f"Ошибка при генерации комплексного аналитического отчета: {e}")
            raise

    def _generate_trend_analysis_html(self, 
                                    trend_analysis: Dict[str, Any], 
                                    nomenclature_name: str,
                                    days: int) -> str:
        """Генерирует HTML для отчета о трендах."""
        # Определяем направление тренда
        trend_direction_map = {
            'improving': 'Улучшается',
            'deteriorating': 'Ухудшается',
            'stable': 'Стабильный',
            'insufficient_data': 'Недостаточно данных',
            'unknown': 'Неизвестно'
        }
        
        trend_direction = trend_direction_map.get(
            trend_analysis.get('trend_direction', 'unknown'), 
            trend_direction_map['unknown']
        )
        
        accuracy_trend = trend_direction_map.get(
            trend_analysis.get('accuracy_trend', 'unknown'), 
            trend_direction_map['unknown']
        )
        
        # Создаем таблицу с данными о трендах
        trend_data_html = ""
        for data_point in trend_analysis.get('trend_data', []):
            trend_data_html += f"""
                <tr>
                    <td>{data_point['date'].strftime('%Y-%m-%d')}</td>
                    <td>{data_point['coefficient_a']:.6f}</td>
                    <td>{data_point['coefficient_b']:.6f}</td>
                    <td>{data_point['coefficient_c']:.6f}</td>
                    <td>{data_point['accuracy']:.2f}%</td>
                </tr>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналитический отчет по трендам для {nomenclature_name}</title>
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #0ea5e9;
            --light: #f8fafc;
            --dark: #0f172a;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --border-radius: 12px;
            --box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
            color: var(--gray-800);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }}

        .header h1 {{
            margin: 0 0 15px 0;
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        .header .subtitle {{
            margin: 0 0 25px 0;
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 400;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: white;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin: 30px;
        }}

        .stat-card {{
            background: var(--light);
            border-radius: var(--border-radius);
            padding: 25px;
            text-align: center;
            border: 1px solid var(--gray-200);
            transition: var(--transition);
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}

        .stat-card h3 {{
            font-size: 1.1rem;
            color: var(--gray-600);
            margin-bottom: 15px;
        }}

        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .trend-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px;
            background: white;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .trend-table th {{
            background: var(--primary);
            color: white;
            text-align: left;
            padding: 15px 20px;
            font-weight: 600;
        }}

        .trend-table td {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--gray-200);
        }}

        .trend-table tr:last-child td {{
            border-bottom: none;
        }}

        .trend-table tr:hover {{
            background: var(--gray-100);
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--gray-600);
            font-size: 0.9rem;
            border-top: 1px solid var(--gray-200);
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Аналитический отчет по трендам</h1>
            <div class="subtitle">Номенклатура: {nomenclature_name}</div>
            <div class="subtitle">Период анализа: {days} дней</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Средний коэффициент A</h3>
                <div class="value">{trend_analysis['avg_coefficient_a']:.6f}</div>
            </div>
            <div class="stat-card">
                <h3>Средний коэффициент B</h3>
                <div class="value">{trend_analysis['avg_coefficient_b']:.6f}</div>
            </div>
            <div class="stat-card">
                <h3>Средний коэффициент C</h3>
                <div class="value">{trend_analysis['avg_coefficient_c']:.6f}</div>
            </div>
            <div class="stat-card">
                <h3>Тренд точности</h3>
                <div class="value">{accuracy_trend}</div>
            </div>
        </div>

        <h2 style="padding: 0 30px; margin: 30px 0 20px 0;">Детализация по датам</h2>
        <table class="trend-table">
            <thead>
                <tr>
                    <th>Дата</th>
                    <th>Коэффициент A</th>
                    <th>Коэффициент B</th>
                    <th>Коэффициент C</th>
                    <th>Точность (R²)</th>
                </tr>
            </thead>
            <tbody>
                {trend_data_html}
            </tbody>
        </table>

        <div class="footer">
            <p>Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p>Система расчета коэффициентов усушки</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content

    def _generate_model_comparison_html(self, model_comparison: Dict[str, Any]) -> str:
        """Генерирует HTML для отчета о сравнении моделей."""
        # Создаем таблицу с данными о моделях
        models_html = ""
        for i, model in enumerate(model_comparison.get('models', []), 1):
            # Определяем цвет для строки в зависимости от места
            row_color = ""
            if i == 1:
                row_color = "style='background-color: #ecfdf5;'"  # Зеленый для лучшей модели
            elif i == len(model_comparison.get('models', [])):
                row_color = "style='background-color: #fef2f2;'"  # Красный для худшей модели
            
            models_html += f"""
                <tr {row_color}>
                    <td>{i}</td>
                    <td>{model['model_name']}</td>
                    <td>{model['model_type']}</td>
                    <td>{model['avg_accuracy']:.2f}%</td>
                    <td>{model['calculation_count']}</td>
                    <td>{model['unique_nomenclatures']}</td>
                </tr>
            """
        
        best_model = model_comparison.get('best_model', {})
        best_model_name = best_model.get('model_name', 'Не определена') if best_model else 'Не определена'
        best_model_accuracy = best_model.get('avg_accuracy', 0) if best_model else 0
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сравнительный анализ моделей</title>
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #0ea5e9;
            --light: #f8fafc;
            --dark: #0f172a;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --border-radius: 12px;
            --box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
            color: var(--gray-800);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }}

        .header h1 {{
            margin: 0 0 15px 0;
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        .header .subtitle {{
            margin: 0 0 25px 0;
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 400;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: white;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin: 30px;
        }}

        .stat-card {{
            background: var(--light);
            border-radius: var(--border-radius);
            padding: 25px;
            text-align: center;
            border: 1px solid var(--gray-200);
            transition: var(--transition);
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}

        .stat-card h3 {{
            font-size: 1.1rem;
            color: var(--gray-600);
            margin-bottom: 15px;
        }}

        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .models-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px;
            background: white;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .models-table th {{
            background: var(--primary);
            color: white;
            text-align: left;
            padding: 15px 20px;
            font-weight: 600;
        }}

        .models-table td {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--gray-200);
        }}

        .models-table tr:last-child td {{
            border-bottom: none;
        }}

        .models-table tr:hover {{
            background: var(--gray-100);
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--gray-600);
            font-size: 0.9rem;
            border-top: 1px solid var(--gray-200);
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Сравнительный анализ моделей</h1>
            <div class="subtitle">Сравнение эффективности различных моделей расчета усушки</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Всего моделей</h3>
                <div class="value">{model_comparison['total_models']}</div>
            </div>
            <div class="stat-card">
                <h3>Лучшая модель</h3>
                <div class="value">{best_model_name}</div>
            </div>
            <div class="stat-card">
                <h3>Точность лучшей модели</h3>
                <div class="value">{best_model_accuracy:.2f}%</div>
            </div>
        </div>

        <h2 style="padding: 0 30px; margin: 30px 0 20px 0;">Сравнение моделей</h2>
        <table class="models-table">
            <thead>
                <tr>
                    <th>Место</th>
                    <th>Название модели</th>
                    <th>Тип модели</th>
                    <th>Средняя точность</th>
                    <th>Количество расчетов</th>
                    <th>Уникальных номенклатур</th>
                </tr>
            </thead>
            <tbody>
                {models_html}
            </tbody>
        </table>

        <div class="footer">
            <p>Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p>Система расчета коэффициентов усушки</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content

    def _generate_nomenclature_performance_html(self, 
                                              performance_report: Dict[str, Any], 
                                              limit: int) -> str:
        """Генерирует HTML для отчета о производительности номенклатур."""
        # Создаем таблицу с данными о производительности
        performance_html = ""
        for i, item in enumerate(performance_report.get('top_performing', []), 1):
            # Определяем цвет для строки в зависимости от места
            row_color = ""
            if i == 1:
                row_color = "style='background-color: #ecfdf5;'"  # Зеленый для лучшей номенклатуры
            elif i >= len(performance_report.get('top_performing', [])) - 2:
                row_color = "style='background-color: #fef2f2;'"  # Красный для худших номенклатур
            
            performance_html += f"""
                <tr {row_color}>
                    <td>{i}</td>
                    <td>{item['nomenclature_name']}</td>
                    <td>{item['calculation_count']}</td>
                    <td>{item['avg_accuracy']:.2f}%</td>
                    <td>{item['error_count']}</td>
                </tr>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет о производительности номенклатур</title>
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #0ea5e9;
            --light: #f8fafc;
            --dark: #0f172a;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --border-radius: 12px;
            --box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
            color: var(--gray-800);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }}

        .header h1 {{
            margin: 0 0 15px 0;
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        .header .subtitle {{
            margin: 0 0 25px 0;
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 400;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: white;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin: 30px;
        }}

        .stat-card {{
            background: var(--light);
            border-radius: var(--border-radius);
            padding: 25px;
            text-align: center;
            border: 1px solid var(--gray-200);
            transition: var(--transition);
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}

        .stat-card h3 {{
            font-size: 1.1rem;
            color: var(--gray-600);
            margin-bottom: 15px;
        }}

        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px;
            background: white;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .performance-table th {{
            background: var(--primary);
            color: white;
            text-align: left;
            padding: 15px 20px;
            font-weight: 600;
        }}

        .performance-table td {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--gray-200);
        }}

        .performance-table tr:last-child td {{
            border-bottom: none;
        }}

        .performance-table tr:hover {{
            background: var(--gray-100);
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--gray-600);
            font-size: 0.9rem;
            border-top: 1px solid var(--gray-200);
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Отчет о производительности номенклатур</h1>
            <div class="subtitle">Топ-{limit} номенклатур по количеству расчетов</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Всего номенклатур в отчете</h3>
                <div class="value">{performance_report['total_nomenclatures']}</div>
            </div>
        </div>

        <h2 style="padding: 0 30px; margin: 30px 0 20px 0;">Рейтинг производительности</h2>
        <table class="performance-table">
            <thead>
                <tr>
                    <th>Место</th>
                    <th>Номенклатура</th>
                    <th>Количество расчетов</th>
                    <th>Средняя точность</th>
                    <th>Количество ошибок</th>
                </tr>
            </thead>
            <tbody>
                {performance_html}
            </tbody>
        </table>

        <div class="footer">
            <p>Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p>Система расчета коэффициентов усушки</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content