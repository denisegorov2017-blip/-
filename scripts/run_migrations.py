#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска миграций базы данных.

Этот скрипт позволяет выполнять миграции базы данных с помощью Alembic.
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

# Добавляем путь к alembic
alembic_path = os.path.join(project_root, 'src', 'core', 'database')
sys.path.insert(0, alembic_path)

from alembic.config import Config
from alembic import command
from src.core.database.database import get_database_url

def main():
    """Основная функция скрипта."""
    print("=== Запуск миграций базы данных ===\n")
    
    try:
        # Определяем путь к файлу конфигурации Alembic
        alembic_ini_path = os.path.join(project_root, 'src', 'core', 'database', 'alembic.ini')
        
        # Проверяем существование файла конфигурации
        if not os.path.exists(alembic_ini_path):
            print(f"Файл конфигурации Alembic не найден: {alembic_ini_path}")
            print("Пожалуйста, убедитесь, что файл alembic.ini существует")
            return 1
        
        # Создаем конфигурацию Alembic
        alembic_cfg = Config(alembic_ini_path)
        
        # Устанавливаем URL базы данных
        database_url = get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        print(f"URL базы данных: {database_url}")
        
        # Определяем команду
        if len(sys.argv) < 2:
            print("Доступные команды:")
            print("  upgrade [revision]    - Применить миграции")
            print("  downgrade [revision]  - Откатить миграции")
            print("  current               - Показать текущую версию")
            print("  history               - Показать историю миграций")
            print("  revision              - Создать новую миграцию")
            return 0
        
        cmd = sys.argv[1]
        
        if cmd == 'upgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            print(f"Применение миграций до версии: {revision}")
            command.upgrade(alembic_cfg, revision)
            print("Миграции успешно применены")
            
        elif cmd == 'downgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else '-1'
            print(f"Откат миграций до версии: {revision}")
            command.downgrade(alembic_cfg, revision)
            print("Миграции успешно откачены")
            
        elif cmd == 'current':
            print("Текущая версия базы данных:")
            command.current(alembic_cfg)
            
        elif cmd == 'history':
            print("История миграций:")
            command.history(alembic_cfg)
            
        elif cmd == 'revision':
            message = sys.argv[2] if len(sys.argv) > 2 else 'Auto migration'
            print(f"Создание новой миграции: {message}")
            command.revision(alembic_cfg, message=message, autogenerate=True)
            print("Миграция создана успешно")
            
        else:
            print(f"Неизвестная команда: {cmd}")
            return 1
            
    except Exception as e:
        print(f"Ошибка при выполнении миграций: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())