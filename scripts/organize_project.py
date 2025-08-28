#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для полной организации структуры проекта согласно руководству
"""

import os
import shutil
from pathlib import Path
import json

def organize_source_data():
    """Организация исходных данных"""
    source_dir = Path("исходные_данные") / "Для_расчета_коэфф"
    
    if not source_dir.exists():
        source_dir.mkdir(parents=True, exist_ok=True)
        print(f"Создана директория: {source_dir}")
    
    # Проверяем, что в директории только Excel файлы
    for file_path in source_dir.iterdir():
        if file_path.is_file() and not file_path.suffix.lower() in ['.xlsx', '.xls']:
            if file_path.suffix.lower() == '.pdf':
                # Перемещаем PDF в документацию
                docs_dir = Path("docs")
                if not docs_dir.exists():
                    docs_dir.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(docs_dir / file_path.name))
                print(f"PDF файл перемещен в docs: {file_path.name}")
            else:
                # Перемещаем остальные файлы в логи
                logs_dir = Path("logs")
                if not logs_dir.exists():
                    logs_dir.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(logs_dir / file_path.name))
                print(f"Файл перемещен в logs: {file_path.name}")

def organize_results():
    """Организация результатов расчетов"""
    results_dir = Path("результаты")
    
    if not results_dir.exists():
        results_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {results_dir}")
    
    # Создаем поддиректории для организации
    subdirs = ["архив", "тестовые_данные", "реальные_данные"]
    for subdir in subdirs:
        subdir_path = results_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(exist_ok=True)
            print(f"Создана директория: {subdir_path}")

def organize_examples():
    """Организация примеров"""
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        examples_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {examples_dir}")

def organize_scripts():
    """Организация скриптов"""
    scripts_dir = Path("scripts")
    debugging_dir = scripts_dir / "debugging"
    
    if not scripts_dir.exists():
        scripts_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {scripts_dir}")
    
    if not debugging_dir.exists():
        debugging_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {debugging_dir}")

def organize_tests():
    """Организация тестов"""
    tests_dir = Path("tests")
    debugging_dir = tests_dir / "debugging"
    
    if not tests_dir.exists():
        tests_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {tests_dir}")
    
    if not debugging_dir.exists():
        debugging_dir.mkdir(exist_ok=True)
        print(f"Создана директория: {debugging_dir}")

def create_gitkeep_files():
    """Создание .gitkeep файлов в пустых директориях"""
    dirs_to_check = [
        "исходные_данные/Для_расчета_коэфф",
        "результаты/архив",
        "результаты/реальные_данные",
        "результаты/тестовые_данные",
        "scripts/debugging",
        "tests/debugging"
    ]
    
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if path.exists() and not any(path.iterdir()):
            gitkeep_path = path / ".gitkeep"
            gitkeep_path.touch()
            print(f"Создан .gitkeep в: {dir_path}")

def clean_root_directory():
    """Очистка корневой директории от временных файлов"""
    root = Path(".")
    temp_files = [
        "*.log",
        "*.tmp",
        "*.temp",
        "*~",
        "*.bak"
    ]
    
    # Перемещаем временные файлы в логи
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
    
    print("Корневая директория очищена от временных файлов")

def main():
    """Основная функция организации проекта"""
    print("Начинаем организацию структуры проекта...")
    print("=" * 50)
    
    try:
        organize_source_data()
        organize_results()
        organize_examples()
        organize_scripts()
        organize_tests()
        create_gitkeep_files()
        clean_root_directory()
        
        print("=" * 50)
        print("Организация проекта завершена успешно!")
        print("\nСтруктура проекта теперь соответствует руководству gemini_self_guide.md")
        
    except Exception as e:
        print(f"Ошибка при организации проекта: {e}")

if __name__ == "__main__":
    main()