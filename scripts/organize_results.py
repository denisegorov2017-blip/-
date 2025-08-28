#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для организации результатов расчетов и очистки старых файлов
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def organize_results():
    """Организация файлов результатов по датам и типам"""
    
    # Пути к директориям
    results_dir = Path("результаты")
    test_data_dir = results_dir / "тестовые_данные"
    
    # Создаем директории для организации
    old_results_dir = results_dir / "архив_результатов"
    old_results_dir.mkdir(exist_ok=True)
    
    # Перемещаем старые файлы в архив
    for file_path in results_dir.glob("*"):
        if file_path.is_file() and file_path.name not in [".gitkeep"]:
            # Пропускаем файлы, созданные сегодня
            if "20250828" in str(file_path):
                continue
                
            # Перемещаем старые файлы в архив
            shutil.move(str(file_path), str(old_results_dir / file_path.name))
    
    print("Файлы результатов организованы")

def cleanup_test_data():
    """Очистка временных тестовых файлов"""
    
    test_data_dir = Path("результаты") / "тестовые_данные"
    
    if not test_data_dir.exists():
        return
    
    # Счетчики для удаленных файлов
    removed_count = 0
    
    # Удаляем временные файлы
    temp_patterns = [
        "*_temp.*",
        "*_tmp.*",
        "*.tmp",
        "*.temp"
    ]
    
    # Удаляем файлы старше 7 дней (имитация)
    # В реальной реализации здесь будет проверка даты создания файлов
    
    print(f"Очищено временных файлов: {removed_count}")

if __name__ == "__main__":
    print("Организация файлов проекта...")
    organize_results()
    cleanup_test_data()
    print("Организация завершена!")