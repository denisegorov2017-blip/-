#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт инициализации базы данных PostgreSQL для системы расчета коэффициентов усушки.

Этот скрипт инициализирует базу данных PostgreSQL и создает все необходимые таблицы.
"""

import sys
import os
import inspect

# Получаем путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.join(current_dir, '..')
project_root = os.path.abspath(project_root)

# Добавляем путь к проекту
sys.path.insert(0, project_root)

from src.logger_config import log
from src.core.database.database import init_database, get_database_url
from src.core.database.utils import test_database_connection, get_database_info
from src.core.database.timescaledb import check_timescaledb_extension, optimize_with_timescaledb

def main():
    """Основная функция скрипта."""
    print("=== Инициализация базы данных PostgreSQL ===\n")
    
    try:
        # 1. Проверка конфигурации
        print("1. Проверка конфигурации базы данных...")
        db_url = get_database_url()
        print(f"   URL базы данных: {db_url}")
        
        if not db_url.startswith('postgresql://'):
            print("   ВНИМАНИЕ: Текущая конфигурация не использует PostgreSQL!")
            print("   Пожалуйста, обновите database_url в src/config.py\n")
            return 1
        
        # 2. Проверка подключения
        print("2. Проверка подключения к базе данных...")
        if test_database_connection():
            print("   Подключение к базе данных успешно\n")
        else:
            print("   Не удалось подключиться к базе данных")
            print("   Проверьте настройки подключения и доступность сервера PostgreSQL\n")
            return 1
        
        # 3. Инициализация базы данных
        print("3. Инициализация базы данных...")
        try:
            engine = init_database()
            print("   База данных инициализирована успешно\n")
        except Exception as e:
            print(f"   Ошибка при инициализации базы данных: {e}\n")
            return 1
        
        # 4. Получение информации о базе данных
        print("4. Получение информации о базе данных...")
        info = get_database_info()
        print(f"   Тип базы данных: {info['database_type']}")
        print(f"   Размер базы данных: {info['size_mb']} МБ")
        print(f"   Общее количество записей: {info['total_rows']}")
        print(f"   Количество таблиц: {len(info['tables'])}\n")
        
        # 5. Проверка TimescaleDB
        print("5. Проверка TimescaleDB...")
        timescaledb_available = check_timescaledb_extension()
        if timescaledb_available:
            print("   Расширение TimescaleDB доступно")
            print("   Оптимизация таблиц с помощью TimescaleDB...")
            optimization_success = optimize_with_timescaledb()
            if optimization_success:
                print("   Оптимизация с TimescaleDB выполнена успешно\n")
            else:
                print("   Оптимизация с TimescaleDB не выполнена\n")
        else:
            print("   Расширение TimescaleDB не доступно")
            print("   Рекомендуется установить TimescaleDB для оптимизации временных рядов\n")
        
        # 6. Финальная проверка
        print("6. Финальная проверка...")
        final_info = get_database_info()
        print(f"   Все таблицы созданы успешно")
        print(f"   Количество таблиц: {len(final_info['tables'])}")
        print("   Таблицы:")
        for table_name, row_count in final_info['tables'].items():
            status = "пустая" if row_count == 0 else f"{row_count} записей"
            print(f"     - {table_name}: {status}")
        print()
        
        print("=== Инициализация завершена успешно ===")
        print("\nТеперь вы можете:")
        print("1. Запустить систему расчета усушки")
        print("2. Использовать CLI инструменты для управления базой данных")
        print("3. Запустить примеры использования PostgreSQL")
        
    except Exception as e:
        log.error(f"Ошибка в скрипте инициализации: {e}")
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())