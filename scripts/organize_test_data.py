#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для организации существующих тестовых данных в подпапки.
"""

import sys
import os

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.test_data_manager import TestDataManager


def main():
    """Основная функция для организации тестовых данных."""
    print("🔧 Организация тестовых данных")
    print("=" * 50)
    
    # Создаем менеджер тестовых данных
    manager = TestDataManager()
    
    # Организуем существующие файлы
    print("📂 Организация существующих файлов...")
    manager.organize_existing_files()
    
    # Очистка старых тестовых данных (по умолчанию старше 7 дней)
    print("🗑️  Очистка старых тестовых данных...")
    manager.cleanup_old_test_data()
    
    # Получаем и выводим статистику
    print("\n📊 Статистика по данным:")
    stats = manager.get_test_data_stats()
    print(f"   Тестовых файлов: {stats['test_files_count']} ({stats['test_files_size'] / 1024:.1f} КБ)")
    print(f"   Реальных файлов: {stats['real_files_count']} ({stats['real_files_size'] / 1024:.1f} КБ)")
    
    print("\n✅ Организация тестовых данных завершена!")


if __name__ == "__main__":
    main()