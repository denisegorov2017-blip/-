#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления тестовыми данными.

Отвечает за автоматическую очистку тестовых данных и организацию их в подпапки.
"""

import os
import shutil
import glob
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log


class TestDataManager:
    """
    Менеджер тестовых данных для автоматической очистки и организации файлов.
    """
    
    def __init__(self, results_dir: str = "результаты"):
        """
        Инициализирует менеджер тестовых данных.

        Args:
            results_dir (str): Директория с результатами (по умолчанию "результаты")
        """
        self.results_dir = results_dir
        self.test_subdir = os.path.join(results_dir, "тестовые_данные")
        self.real_data_subdir = os.path.join(results_dir, "реальные_данные")
        
        # Создаем необходимые директории
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.test_subdir, exist_ok=True)
        os.makedirs(self.real_data_subdir, exist_ok=True)
        
        log.info("TestDataManager инициализирован")
    
    def organize_existing_files(self):
        """
        Организует существующие файлы в соответствующие подпапки.
        """
        log.info("Организация существующих файлов...")
        
        # Список файлов, которые точно являются тестовыми
        test_patterns = [
            "*test*",
            "*_тест_*",
            "test_*",
            "*_test_*",
            "*fish_batch_test_results*",
            "*_оптимизация_*"
        ]
        
        # Список файлов, которые точно являются реальными данными
        real_patterns = [
            "*b3ded820-4385-4a42-abc7-75dc0756d335*",
            "*вся номенклатура*"
        ]
        
        # Получаем все файлы в директории результатов
        all_files = glob.glob(os.path.join(self.results_dir, "*"))
        
        organized_count = 0
        
        for file_path in all_files:
            # Пропускаем поддиректории
            if os.path.isdir(file_path):
                continue
                
            filename = os.path.basename(file_path)
            
            # Проверяем, является ли файл тестовым
            is_test_file = any(pattern in filename.lower() for pattern in test_patterns)
            
            # Проверяем, является ли файл реальными данными
            is_real_file = any(pattern in filename for pattern in real_patterns)
            
            # Определяем целевую директорию
            if is_test_file:
                target_dir = self.test_subdir
            elif is_real_file:
                target_dir = self.real_data_subdir
            else:
                # Для остальных файлов определяем по времени создания
                target_dir = self._determine_file_category(file_path)
            
            # Перемещаем файл если он не в нужной директории
            if os.path.dirname(file_path) != target_dir:
                try:
                    target_path = os.path.join(target_dir, filename)
                    shutil.move(file_path, target_path)
                    log.info(f"Файл перемещен: {filename} -> {target_dir}")
                    organized_count += 1
                except Exception as e:
                    log.error(f"Ошибка при перемещении файла {filename}: {e}")
        
        log.info(f"Организовано файлов: {organized_count}")
    
    def _determine_file_category(self, file_path: str) -> str:
        """
        Определяет категорию файла на основе времени создания и содержания.

        Args:
            file_path (str): Путь к файлу

        Returns:
            str: Путь к целевой директории
        """
        try:
            # Получаем время создания файла
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            current_time = datetime.now()
            
            # Если файл создан менее 24 часов назад, считаем его тестовым
            if current_time - creation_time < timedelta(hours=24):
                return self.test_subdir
            else:
                return self.real_data_subdir
        except Exception as e:
            log.error(f"Ошибка при определении категории файла {file_path}: {e}")
            return self.test_subdir  # По умолчанию в тестовые
    
    def cleanup_old_test_data(self, days_old: int = 7):
        """
        Удаляет старые тестовые данные и пустые директории.

        Args:
            days_old (int): Количество дней, после которых данные считаются старыми (по умолчанию 7)
        """
        log.info(f"Очистка тестовых данных старше {days_old} дней...")
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        # Проверяем тестовую поддиректорию
        if os.path.exists(self.test_subdir):
            for filename in os.listdir(self.test_subdir):
                file_path = os.path.join(self.test_subdir, filename)
                
                try:
                    # Получаем время последнего изменения
                    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Если файл старше указанного срока, удаляем его
                    if modification_time < cutoff_date:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        log.info(f"Удален старый тестовый файл: {filename}")
                        deleted_count += 1
                except Exception as e:
                    log.error(f"Ошибка при удалении файла {filename}: {e}")
        
        log.info(f"Удалено старых тестовых файлов: {deleted_count}")
        
        # Удаляем пустые директории
        self._remove_empty_directories()
    
    def _remove_empty_directories(self):
        """
        Удаляет пустые директории в директории результатов.
        """
        log.info("Удаление пустых директорий...")
        removed_count = 0
        
        # Получаем все поддиректории в директории результатов
        for item in os.listdir(self.results_dir):
            item_path = os.path.join(self.results_dir, item)
            
            # Проверяем, является ли элемент директорией
            if os.path.isdir(item_path):
                try:
                    # Проверяем, пустая ли директория
                    if not os.listdir(item_path):
                        os.rmdir(item_path)
                        log.info(f"Удалена пустая директория: {item}")
                        removed_count += 1
                except Exception as e:
                    log.error(f"Ошибка при удалении директории {item}: {e}")
        
        log.info(f"Удалено пустых директорий: {removed_count}")
    
    def get_test_data_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику по тестовым данным.

        Returns:
            Dict[str, Any]: Статистика по тестовым данным
        """
        stats = {
            'test_files_count': 0,
            'real_files_count': 0,
            'test_files_size': 0,
            'real_files_size': 0
        }
        
        try:
            # Статистика по тестовым файлам
            if os.path.exists(self.test_subdir):
                for filename in os.listdir(self.test_subdir):
                    file_path = os.path.join(self.test_subdir, filename)
                    if os.path.isfile(file_path):
                        stats['test_files_count'] += 1
                        stats['test_files_size'] += os.path.getsize(file_path)
            
            # Статистика по реальным файлам
            if os.path.exists(self.real_data_subdir):
                for filename in os.listdir(self.real_data_subdir):
                    file_path = os.path.join(self.real_data_subdir, filename)
                    if os.path.isfile(file_path):
                        stats['real_files_count'] += 1
                        stats['real_files_size'] += os.path.getsize(file_path)
        except Exception as e:
            log.error(f"Ошибка при сборе статистики: {e}")
        
        return stats


def main():
    """Демонстрация работы менеджера тестовых данных."""
    print("🔧 Менеджер тестовых данных")
    print("=" * 50)
    
    # Создаем менеджер
    manager = TestDataManager()
    
    # Организуем существующие файлы
    print("📂 Организация существующих файлов...")
    manager.organize_existing_files()
    
    # Очистка старых тестовых данных
    print("🗑️  Очистка старых тестовых данных...")
    manager.cleanup_old_test_data()
    
    # Получаем статистику
    print("📊 Статистика:")
    stats = manager.get_test_data_stats()
    print(f"   Тестовых файлов: {stats['test_files_count']} ({stats['test_files_size'] / 1024:.1f} КБ)")
    print(f"   Реальных файлов: {stats['real_files_count']} ({stats['real_files_size'] / 1024:.1f} КБ)")


if __name__ == "__main__":
    main()