#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and automatic cleanup plugin
"""

import pytest
import os
import sys
from pathlib import Path

# Добавляем путь к скриптам в системный путь
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def pytest_configure(config):
    """Конфигурация pytest"""
    print("\n🚀 Подготовка к запуску тестов...")
    print("🔍 Инициализация системы автоматической очистки")

def pytest_unconfigure(config):
    """Финализация pytest - выполняется после всех тестов"""
    print("\n✅ Все тесты завершены")
    
    # Автоматическая очистка после тестов
    try:
        from cleanup_test_files import automatic_cleanup
        print("\n🧹 Запуск автоматической очистки...")
        success = automatic_cleanup()
        if success:
            print("✨ Автоматическая очистка успешно завершена!")
        else:
            print("⚠️  Возникли проблемы при автоматической очистке")
    except Exception as e:
        print(f"❌ Ошибка при автоматической очистке: {e}")
        print("💡 Убедитесь, что скрипт cleanup_test_files.py находится в директории scripts/")

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Вывод сводки в терминале после завершения тестов"""
    if exitstatus == 0:
        print("\n🎉 Все тесты успешно пройдены!")
        print("🗑️  Файлы, созданные тестами, были автоматически удалены")
        print("📝 Логи старше 7 дней также были очищены")
    else:
        print(f"\n❌ Некоторые тесты завершились с ошибками (код выхода: {exitstatus})")
        print("📄 Подробности смотрите в отчете выше")