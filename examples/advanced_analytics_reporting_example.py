#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования расширенной аналитики и генерации отчетов.

Этот скрипт демонстрирует, как использовать расширенные аналитические функции
и генерировать отчеты на основе данных из базы данных.
"""

import sys
import os
from datetime import datetime

# Добавляем путь к src директории
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Исправляем импорты
sys.path.insert(0, project_root)

from src.logger_config import log
from src.config import DEFAULT_CONFIG
from src.core.database.database import get_db_session, init_database
from src.core.database.services import get_database_service
from src.core.advanced_analytics_reporter import AdvancedAnalyticsReporter


def main():
    """Основная функция для демонстрации расширенной аналитики."""
    print("=== Демонстрация расширенной аналитики ===")
    
    try:
        # Инициализируем базу данных
        init_database()
        print("✓ База данных инициализирована")
        
        # Получаем сессию базы данных
        Session = get_db_session()
        session = Session()
        db_service = get_database_service(session)
        
        # Создаем репортер для расширенной аналитики
        config = DEFAULT_CONFIG.copy()
        config['output_dir'] = os.path.join(project_root, 'результаты', 'аналитика')
        reporter = AdvancedAnalyticsReporter(config)
        
        print("\n1. Генерация отчета о сравнении моделей...")
        try:
            model_report_path = reporter.generate_model_comparison_report()
            print(f"✓ Отчет о сравнении моделей сохранен: {model_report_path}")
        except Exception as e:
            print(f"✗ Ошибка при генерации отчета о сравнении моделей: {e}")
        
        print("\n2. Генерация отчета о производительности номенклатур...")
        try:
            performance_report_path = reporter.generate_nomenclature_performance_report(limit=15)
            print(f"✓ Отчет о производительности номенклатур сохранен: {performance_report_path}")
        except Exception as e:
            print(f"✗ Ошибка при генерации отчета о производительности номенклатур: {e}")
        
        # Получаем список номенклатур для генерации трендового анализа
        try:
            # Получаем все номенклатуры
            from src.core.database.models import Nomenclature
            nomenclatures = session.query(Nomenclature).all()
            
            if nomenclatures:
                print(f"\n3. Генерация трендового анализа для {min(3, len(nomenclatures))} номенклатур...")
                # Генерируем трендовый анализ для первых 3 номенклатур
                for i, nomenclature in enumerate(nomenclatures[:3]):
                    try:
                        trend_report_path = reporter.generate_trend_analysis_report(
                            nomenclature_id=nomenclature.id,
                            nomenclature_name=nomenclature.name,
                            days=30
                        )
                        print(f"✓ Трендовый анализ для '{nomenclature.name}' сохранен: {trend_report_path}")
                    except Exception as e:
                        print(f"✗ Ошибка при генерации трендового анализа для '{nomenclature.name}': {e}")
            else:
                print("\n3. Нет номенклатур для трендового анализа")
        except Exception as e:
            print(f"✗ Ошибка при получении списка номенклатур: {e}")
        
        # Генерируем комплексный отчет
        print("\n4. Генерация комплексного аналитического отчета...")
        try:
            comprehensive_reports = reporter.generate_comprehensive_analytics_report()
            print("✓ Комплексный аналитический отчет сгенерирован:")
            for report_type, report_path in comprehensive_reports.items():
                print(f"  - {report_type}: {report_path}")
        except Exception as e:
            print(f"✗ Ошибка при генерации комплексного аналитического отчета: {e}")
        
        # Закрываем сессию
        session.close()
        
        print("\n=== Демонстрация завершена ===")
        
    except Exception as e:
        log.error(f"Ошибка в примере расширенной аналитики: {e}")
        print(f"✗ Критическая ошибка: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Все отчеты успешно сгенерированы!")
        print("📁 Отчеты сохранены в директории 'результаты/аналитика'")
    else:
        print("\n❌ Возникли ошибки при генерации отчетов")
        sys.exit(1)