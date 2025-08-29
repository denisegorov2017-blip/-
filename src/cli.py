#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Командная строка для системы расчета усушки.

Этот модуль предоставляет интерфейс командной строки для работы с системой
расчета коэффициентов усушки без использования графического интерфейса.
"""

import argparse
import sys
import os
from pathlib import Path
import webbrowser
from typing import Optional

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.core.shrinkage_system import ShrinkageSystem
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from src.core.improved_json_parser import parse_from_json
from src.core.settings_manager import SettingsManager
from src.logger_config import log


def process_excel_file(
    excel_path: str, 
    use_adaptive: bool = False,
    surplus_rate: float = 0.0,
    open_report: bool = False
) -> bool:
    """
    Обрабатывает Excel файл и генерирует отчет.
    
    Args:
        excel_path (str): Путь к Excel файлу
        use_adaptive (bool): Использовать адаптивную модель
        surplus_rate (float): Процент излишка
        open_report (bool): Открыть отчет после генерации
        
    Returns:
        bool: True если обработка прошла успешно, False в противном случае
    """
    try:
        log.info(f"Начало обработки файла: {excel_path}")
        
        # Проверяем существование файла
        if not os.path.exists(excel_path):
            log.error(f"Файл не найден: {excel_path}")
            return False
        
        # Получаем настройки
        settings_manager = SettingsManager()
        output_dir = settings_manager.get_setting('output_dir', 'результаты')
        
        # Создаем директорию для результатов если она не существует
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Этап 1: Конвертация Excel в JSON
        log.info("Этап 1/3: Конвертация Excel в JSON...")
        json_path = os.path.join(output_dir, f"{Path(excel_path).stem}.json")
        
        preserver = ExcelHierarchyPreserver(excel_path)
        preserver.to_json(json_path)
        log.info(f"Excel файл успешно сконвертирован в JSON: {json_path}")
        
        # Этап 2: Парсинг JSON
        log.info("Этап 2/3: Анализ и извлечение данных из JSON...")
        dataset = parse_from_json(json_path)
        log.info(f"Парсинг JSON завершен. Найдено {len(dataset)} валидных записей.")
        
        if dataset.empty:
            log.error("В файле не найдено данных для расчета.")
            return False
        
        # Этап 3: Расчет коэффициентов
        log.info("Этап 3/3: Расчет коэффициентов...")
        system = ShrinkageSystem()
        
        # Устанавливаем процент излишка если указан
        if surplus_rate > 0:
            system.set_surplus_rate(surplus_rate / 100.0)
        
        # Обрабатываем набор данных
        results = system.process_dataset(
            dataset=dataset,
            source_filename=os.path.basename(excel_path),
            use_adaptive=use_adaptive
        )
        
        if results.get('status') == 'success':
            report_path = results.get('reports', {}).get('coefficients', '')
            log.success(f"Расчет успешно завершен. Отчет сохранен в: {report_path}")
            
            # Открываем отчет если требуется
            if open_report and report_path and os.path.exists(report_path):
                try:
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                    log.info("Отчет открыт в браузере")
                except Exception as e:
                    log.warning(f"Не удалось открыть отчет: {e}")
            
            return True
        else:
            error_msg = results.get('message', 'Неизвестная ошибка')
            log.error(f"Ошибка в процессе расчета: {error_msg}")
            return False
            
    except Exception as e:
        log.exception(f"Произошла ошибка при обработке файла: {e}")
        return False


def main():
    """Основная функция CLI интерфейса."""
    parser = argparse.ArgumentParser(
        description="Система расчета коэффициентов нелинейной усушки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s process data.xlsx
  %(prog)s process data.xlsx --adaptive --surplus 5.0
  %(prog)s process data.xlsx --open
  %(prog)s settings --list
  %(prog)s settings --reset
        """
    )
    
    # Подкоманды
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда обработки файла
    process_parser = subparsers.add_parser('process', help='Обработать Excel файл')
    process_parser.add_argument('file', help='Путь к Excel файлу (.xlsx, .xls, .xlsm)')
    process_parser.add_argument('--adaptive', action='store_true', 
                               help='Использовать адаптивную модель расчета')
    process_parser.add_argument('--surplus', type=float, default=0.0,
                               help='Процент излишка при поступлении (0-100)')
    process_parser.add_argument('--open', action='store_true',
                               help='Открыть отчет после генерации')
    
    # Команда управления настройками
    settings_parser = subparsers.add_parser('settings', help='Управление настройками')
    settings_parser.add_argument('--list', action='store_true', help='Показать текущие настройки')
    settings_parser.add_argument('--reset', action='store_true', help='Сбросить настройки к значениям по умолчанию')
    settings_parser.add_argument('--backup', action='store_true', help='Создать резервную копию настроек')
    settings_parser.add_argument('--restore', type=str, metavar='BACKUP_FILE',
                                help='Восстановить настройки из резервной копии')
    
    # Команда получения информации
    info_parser = subparsers.add_parser('info', help='Показать информацию о системе')
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Если команда не указана, показываем помощь
    if not args.command:
        parser.print_help()
        return 0
    
    # Обработка команд
    if args.command == 'process':
        # Проверяем расширение файла
        valid_extensions = ['.xlsx', '.xls', '.xlsm']
        file_ext = Path(args.file).suffix.lower()
        
        if file_ext not in valid_extensions:
            print(f"Ошибка: Неподдерживаемый формат файла. Поддерживаются: {', '.join(valid_extensions)}")
            return 1
        
        # Обрабатываем файл
        success = process_excel_file(
            excel_path=args.file,
            use_adaptive=args.adaptive,
            surplus_rate=args.surplus,
            open_report=args.open
        )
        
        return 0 if success else 1
    
    elif args.command == 'settings':
        settings_manager = SettingsManager()
        
        if args.list:
            print("Текущие настройки системы:")
            print("-" * 50)
            for key, value in settings_manager.get_all_settings().items():
                print(f"{key}: {value}")
            return 0
        
        elif args.reset:
            if settings_manager.reset_to_defaults():
                print("Настройки сброшены к значениям по умолчанию")
                return 0
            else:
                print("Ошибка при сбросе настроек")
                return 1
        
        elif args.backup:
            if settings_manager.backup_settings():
                print("Резервная копия настроек создана")
                return 0
            else:
                print("Ошибка при создании резервной копии")
                return 1
        
        elif args.restore:
            if settings_manager.restore_settings_from_backup(args.restore):
                print(f"Настройки восстановлены из {args.restore}")
                return 0
            else:
                print(f"Ошибка при восстановлении настроек из {args.restore}")
                return 1
        
        else:
            settings_parser.print_help()
            return 1
    
    elif args.command == 'info':
        print("Система расчета коэффициентов нелинейной усушки")
        print("=" * 50)
        print("Версия: 1.2.1")
        print("Автор: Разработчик системы")
        print("Описание: Система для точного расчета и прогнозирования усушки продукции")
        print("\nПоддерживаемые форматы файлов:")
        print("  - Excel (.xlsx, .xls, .xlsm)")
        print("\nДоступные интерфейсы:")
        print("  - Графический интерфейс (Flet)")
        print("  - Графический интерфейс (Tkinter)")
        print("  - Веб-дашборд (Streamlit)")
        print("  - Командная строка (CLI)")
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())