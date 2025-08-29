#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Командная строка для управления базой данных.

Этот файл предоставляет командную строку для выполнения различных операций
с базой данных, таких как инициализация, резервное копирование, восстановление и т.д.
"""

import argparse
import sys
import os
import inspect

# Получаем путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.join(current_dir, '..', '..', '..')
project_root = os.path.abspath(project_root)

# Добавляем путь к проекту
sys.path.insert(0, project_root)

# Импортируем модули напрямую
try:
    from src.logger_config import log
    from src.core.database.utils import (
        initialize_database, create_database_backup, 
        restore_database_from_backup, get_database_info,
        test_database_connection, vacuum_database
    )
except ImportError:
    # Если импорт не работает, пробуем другой путь
    try:
        from logger_config import log
        from core.database.utils import (
            initialize_database, create_database_backup, 
            restore_database_from_backup, get_database_info,
            test_database_connection, vacuum_database
        )
    except ImportError:
        # Последняя попытка
        sys.path.insert(0, os.path.join(project_root, 'src'))
        from logger_config import log
        from core.database.utils import (
            initialize_database, create_database_backup, 
            restore_database_from_backup, get_database_info,
            test_database_connection, vacuum_database
        )

def main():
    """
    Основная функция командной строки.
    """
    parser = argparse.ArgumentParser(
        description="Утилита управления базой данных системы расчета коэффициентов усушки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python cli.py init                    # Инициализация базы данных
  python cli.py info                    # Получение информации о базе данных
  python cli.py backup                  # Создание резервной копии
  python cli.py restore backup.db.bak   # Восстановление из резервной копии
  python cli.py vacuum                  # Оптимизация базы данных
  python cli.py test                    # Тестирование подключения
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда инициализации базы данных
    subparsers.add_parser('init', help='Инициализация базы данных')
    
    # Команда получения информации о базе данных
    subparsers.add_parser('info', help='Получение информации о базе данных')
    
    # Команда создания резервной копии
    backup_parser = subparsers.add_parser('backup', help='Создание резервной копии базы данных')
    backup_parser.add_argument('--path', help='Путь для сохранения резервной копии')
    
    # Команда восстановления из резервной копии
    restore_parser = subparsers.add_parser('restore', help='Восстановление базы данных из резервной копии')
    restore_parser.add_argument('backup_file', help='Путь к файлу резервной копии')
    
    # Команда оптимизации базы данных
    subparsers.add_parser('vacuum', help='Оптимизация базы данных')
    
    # Команда тестирования подключения
    subparsers.add_parser('test', help='Тестирование подключения к базе данных')
    
    # Если не передана команда, показываем помощь
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            handle_init()
        elif args.command == 'info':
            handle_info()
        elif args.command == 'backup':
            handle_backup(args.path)
        elif args.command == 'restore':
            handle_restore(args.backup_file)
        elif args.command == 'vacuum':
            handle_vacuum()
        elif args.command == 'test':
            handle_test()
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        log.error(f"Ошибка при выполнении команды '{args.command}': {e}")
        sys.exit(1)

def handle_init():
    """
    Обработка команды инициализации базы данных.
    """
    log.info("Инициализация базы данных...")
    try:
        engine = initialize_database()
        log.success("База данных успешно инициализирована")
    except Exception as e:
        log.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def handle_info():
    """
    Обработка команды получения информации о базе данных.
    """
    log.info("Получение информации о базе данных...")
    try:
        if not test_database_connection():
            log.error("Нет подключения к базе данных")
            return
            
        info = get_database_info()
        
        print("\n=== Информация о базе данных ===")
        print(f"URL базы данных: {info['database_url']}")
        print(f"Размер базы данных: {info['size_mb']} МБ ({info['size_bytes']} байт)")
        print(f"Общее количество записей: {info['total_rows']}")
        print("\nТаблицы:")
        for table_name, row_count in info['tables'].items():
            print(f"  {table_name}: {row_count} записей")
        print("================================\n")
        
        log.success("Информация о базе данных получена")
    except Exception as e:
        log.error(f"Ошибка при получении информации о базе данных: {e}")
        raise

def handle_backup(backup_path=None):
    """
    Обработка команды создания резервной копии.
    
    Args:
        backup_path (str): Путь для сохранения резервной копии
    """
    log.info("Создание резервной копии базы данных...")
    try:
        backup_file = create_database_backup(backup_path)
        if backup_file:
            log.success(f"Резервная копия создана: {backup_file}")
        else:
            log.warning("Не удалось создать резервную копию")
    except Exception as e:
        log.error(f"Ошибка при создании резервной копии: {e}")
        raise

def handle_restore(backup_file):
    """
    Обработка команды восстановления из резервной копии.
    
    Args:
        backup_file (str): Путь к файлу резервной копии
    """
    log.info(f"Восстановление базы данных из резервной копии: {backup_file}")
    try:
        if not os.path.exists(backup_file):
            log.error(f"Файл резервной копии не найден: {backup_file}")
            return
            
        success = restore_database_from_backup(backup_file)
        if success:
            log.success("База данных успешно восстановлена")
        else:
            log.error("Не удалось восстановить базу данных")
    except Exception as e:
        log.error(f"Ошибка при восстановлении базы данных: {e}")
        raise

def handle_vacuum():
    """
    Обработка команды оптимизации базы данных.
    """
    log.info("Оптимизация базы данных...")
    try:
        success = vacuum_database()
        if success:
            log.success("База данных успешно оптимизирована")
        else:
            log.warning("Не удалось оптимизировать базу данных")
    except Exception as e:
        log.error(f"Ошибка при оптимизации базы данных: {e}")
        raise

def handle_test():
    """
    Обработка команды тестирования подключения.
    """
    log.info("Тестирование подключения к базе данных...")
    try:
        success = test_database_connection()
        if success:
            log.success("Подключение к базе данных успешно")
        else:
            log.error("Не удалось подключиться к базе данных")
    except Exception as e:
        log.error(f"Ошибка при тестировании подключения: {e}")
        raise

if __name__ == '__main__':
    main()