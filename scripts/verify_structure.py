#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки корректности структуры проекта
"""

import os
from pathlib import Path

def verify_directory_structure():
    """Проверка структуры директорий проекта"""
    
    # Ожидаемая структура директорий
    expected_dirs = [
        "исходные_данные",
        "исходные_данные/Для_расчета_коэфф",
        "src",
        "src/core",
        "tests",
        "tests/debugging",
        "docs",
        "examples",
        "scripts",
        "scripts/debugging",
        "результаты",
        "результаты/архив",
        "результаты/тестовые_данные",
        "результаты/реальные_данные",
        "logs"
    ]
    
    # Проверяем наличие директорий
    missing_dirs = []
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("⚠️  Обнаружены отсутствующие директории:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        return False
    else:
        print("✅ Все необходимые директории присутствуют")
        return True

def verify_key_files():
    """Проверка наличия ключевых файлов"""
    
    # Ожидаемые ключевые файлы
    key_files = [
        "requirements.txt",
        "launch.py",
        "src/gui.py",
        "src/dashboard.py",
        "src/core/adaptive_shrinkage_calculator.py",
        "scripts/organize_project.py",
        "README.md"
    ]
    
    # Проверяем наличие файлов
    missing_files = []
    for file_path in key_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Обнаружены отсутствующие файлы:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✅ Все ключевые файлы присутствуют")
        return True

def verify_source_data():
    """Проверка структуры исходных данных"""
    
    source_dir = Path("исходные_данные/Для_расчета_коэфф")
    if not source_dir.exists():
        print("⚠️  Директория с исходными данными не найдена")
        return False
    
    # Проверяем, что в директории только Excel файлы (или пусто)
    non_excel_files = []
    for file_path in source_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() not in ['.xlsx', '.xls']:
            non_excel_files.append(file_path.name)
    
    if non_excel_files:
        print("⚠️  В директории исходных данных найдены файлы не Excel формата:")
        for file_name in non_excel_files:
            print(f"  - {file_name}")
        return False
    else:
        print("✅ Исходные данные корректны (только Excel файлы)")
        return True

def verify_results_structure():
    """Проверка структуры результатов"""
    
    results_dir = Path("результаты")
    if not results_dir.exists():
        print("⚠️  Директория результатов не найдена")
        return False
    
    # Проверяем наличие поддиректорий
    subdirs = ["архив", "тестовые_данные", "реальные_данные"]
    missing_subdirs = []
    for subdir in subdirs:
        if not (results_dir / subdir).exists():
            missing_subdirs.append(subdir)
    
    if missing_subdirs:
        print("⚠️  Отсутствуют поддиректории в результатах:")
        for subdir in missing_subdirs:
            print(f"  - {subdir}")
        return False
    else:
        print("✅ Структура директории результатов корректна")
        return True

def main():
    """Основная функция проверки структуры"""
    print("🔍 Проверка структуры проекта...")
    print("=" * 50)
    
    checks = [
        verify_directory_structure,
        verify_key_files,
        verify_source_data,
        verify_results_structure
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 Структура проекта полностью соответствует требованиям!")
        print("   Проект организован согласно руководству gemini_self_guide.md")
    else:
        print("❌ Обнаружены проблемы со структурой проекта")
        print("   Запустите 'python scripts/organize_project.py' для исправления")
    
    return all_passed

if __name__ == "__main__":
    main()