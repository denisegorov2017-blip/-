#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки работы менеджера тестовых данных.
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.test_data_manager import TestDataManager


def test_test_data_manager():
    """Тест для проверки работы менеджера тестовых данных."""
    print("🔧 Тест менеджера тестовых данных")
    print("=" * 50)
    
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 Временная директория: {temp_dir}")
        
        # Создаем тестовые файлы
        test_files = [
            "test_data_1.json",
            "sample_data.xlsx",
            "тест_данные.csv"
        ]
        
        # Создаем тестовые файлы
        for filename in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Тестовые данные для файла {filename}")
        
        # Создаем пустую директорию для тестирования удаления пустых директорий
        empty_dir_path = os.path.join(temp_dir, "пустая_директория")
        os.makedirs(empty_dir_path, exist_ok=True)
        
        # Создаем менеджер тестовых данных
        manager = TestDataManager(temp_dir)
        
        # Проверяем создание поддиректорий
        assert os.path.exists(manager.test_subdir), "Поддиректория для тестовых данных не создана"
        assert os.path.exists(manager.real_data_subdir), "Поддиректория для реальных данных не создана"
        print("✅ Поддиректории созданы успешно")
        
        # Организуем файлы
        print("📂 Организация файлов...")
        manager.organize_existing_files()
        
        # Проверяем перемещение файлов
        test_files_moved = os.listdir(manager.test_subdir)
        
        print(f"   Тестовые файлы: {test_files_moved}")
        
        # Проверяем, что тестовые файлы перемещены правильно
        for filename in test_files:
            assert filename in test_files_moved, f"Файл {filename} не перемещен в тестовую директорию"
        
        print("✅ Файлы организованы успешно")
        
        # Проверяем статистику
        stats = manager.get_test_data_stats()
        print(f"📊 Статистика: {stats}")
        
        assert stats['test_files_count'] == 3, f"Неверное количество тестовых файлов: {stats['test_files_count']}"
        
        print("✅ Статистика корректна")
        
        # Проверяем очистку старых данных
        print("🗑️  Проверка очистки старых данных...")
        old_file_path = os.path.join(manager.test_subdir, "old_test_file.txt")
        with open(old_file_path, 'w', encoding='utf-8') as f:
            f.write("Старый тестовый файл")
        
        # Меняем время модификации файла на 10 дней назад
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_file_path, (old_time, old_time))
        
        # Проверяем, что файл существует
        assert os.path.exists(old_file_path), "Старый файл не создан"
        
        # Очищаем старые данные (файлы старше 7 дней)
        manager.cleanup_old_test_data(days_old=7)
        
        # Проверяем, что старый файл удален
        assert not os.path.exists(old_file_path), "Старый файл не удален"
        print("✅ Очистка старых данных работает корректно")
        
        # Проверяем удаление пустых директорий
        print("🗑️  Проверка удаления пустых директорий...")
        # Создаем еще одну пустую директорию
        another_empty_dir = os.path.join(temp_dir, "another_empty_dir")
        os.makedirs(another_empty_dir, exist_ok=True)
        
        # Убеждаемся, что директория существует
        assert os.path.exists(another_empty_dir), "Пустая директория не создана"
        
        # Выполняем очистку, которая должна удалить пустые директории
        manager._remove_empty_directories()
        
        # Проверяем, что пустая директория удалена
        assert not os.path.exists(another_empty_dir), "Пустая директория не удалена"
        print("✅ Удаление пустых директорий работает корректно")
    
    print("\n✅ Все тесты пройдены успешно!")


if __name__ == "__main__":
    test_test_data_manager()