#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска тестов двойной LLM системы.
"""

import sys
import os

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    """Основная функция для запуска тестов."""
    print("Запуск тестов двойной LLM системы...")
    
    try:
        # Импортируем и запускаем тесты
        from src.core.test_dual_llm import run_all_tests
        run_all_tests()
        
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()