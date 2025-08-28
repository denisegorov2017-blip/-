#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест для проверки работы всех улучшенных интерфейсов
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_file_structure():
    """Проверка структуры файлов проекта"""
    print("🔍 Проверка структуры файлов проекта...")
    
    required_files = [
        "src/gui.py",
        "src/dashboard.py", 
        "src/core/shrinkage_html_reporter.py",
        "requirements.txt",
        "README.md",
        "launch.py",
        "launch.bat",
        "ENHANCEMENTS_SUMMARY.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ Отсутствует файл: {file_path}")
        else:
            print(f"✅ Найден файл: {file_path}")
    
    if missing_files:
        print(f"❌ Не найдено {len(missing_files)} файлов из {len(required_files)}")
    assert not missing_files, f"Не найдено {len(missing_files)} обязательных файлов"
    print(f"✅ Все {len(required_files)} файлов найдены")

def test_module_imports():
    """Проверка импорта модулей"""
    print("\n🔍 Проверка импорта модулей...")
    
    modules_to_test = [
        "flet",
        "streamlit",
        "pandas",
        "numpy",
        "scipy",
        "plotly",
        "loguru"
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ Модуль {module} успешно импортирован")
        except ImportError as e:
            failed_imports.append(module)
            print(f"❌ Не удалось импортировать модуль {module}: {e}")
    
    if failed_imports:
        print(f"❌ Не удалось импортировать {len(failed_imports)} модулей из {len(modules_to_test)}")
    assert not failed_imports, f"Не удалось импортировать {len(failed_imports)} модулей"
    print(f"✅ Все {len(modules_to_test)} модулей успешно импортированы")

def test_project_modules():
    """Проверка импорта модулей проекта"""
    print("\n🔍 Проверка импорта модулей проекта...")
    
    try:
        # Проверяем импорт основных модулей проекта
        from core.shrinkage_system import ShrinkageSystem
        print("✅ Модуль ShrinkageSystem успешно импортирован")
        
        
        
        from core.shrinkage_html_reporter import ShrinkageHTMLReporter
        print("✅ Модуль ShrinkageHTMLReporter успешно импортирован")
        
    except Exception as e:
        assert False, f"Ошибка при импорте модулей проекта: {e}"

def test_directory_structure():
    """Проверка структуры директорий"""
    print("\n🔍 Проверка структуры директорий...")
    
    required_dirs = [
        "src",
        "src/core",
        "исходные_данные",
        "результаты"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
            print(f"❌ Отсутствует директория: {dir_path}")
        else:
            print(f"✅ Найдена директория: {dir_path}")
    
    if missing_dirs:
        print(f"❌ Не найдено {len(missing_dirs)} директорий из {len(required_dirs)}")
    assert not missing_dirs, f"Не найдено {len(missing_dirs)} обязательных директорий"
    print(f"✅ Все {len(required_dirs)} директорий найдены")

def test_file_permissions():
    """Проверка прав доступа к файлам"""
    print("\n🔍 Проверка прав доступа к файлам...")
    
    test_files = [
        "src/gui.py",
        "src/dashboard.py",
        "src/core/shrinkage_html_reporter.py"
    ]
    
    permission_issues = []
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                # Проверяем возможность чтения
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1)  # Читаем первый символ
                print(f"✅ Файл {file_path} доступен для чтения")
            except Exception as e:
                permission_issues.append(file_path)
                print(f"❌ Проблема с доступом к файлу {file_path}: {e}")
        else:
            permission_issues.append(file_path)
            print(f"❌ Файл {file_path} не найден")
    
    if permission_issues:
        print(f"❌ Проблемы с доступом к {len(permission_issues)} файлам из {len(test_files)}")
    assert not permission_issues, f"Проблемы с доступом к {len(permission_issues)} файлам"
    print(f"✅ Все {len(test_files)} файлов доступны для чтения")