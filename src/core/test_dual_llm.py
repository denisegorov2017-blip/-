#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки функциональности двойной LLM системы.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.core.ai_chat import AIChat


def test_dual_llm_initialization():
    """Тест инициализации двойной LLM системы."""
    print("Тест 1: Инициализация двойной LLM системы")
    
    # Создаем экземпляр AIChat
    ai_chat = AIChat()
    
    # Проверяем наличие новых параметров конфигурации
    assert hasattr(ai_chat, 'enable_external_ai_calculations'), "Отсутствует параметр enable_external_ai_calculations"
    assert hasattr(ai_chat, 'enable_external_ai_patterns'), "Отсутствует параметр enable_external_ai_patterns"
    assert hasattr(ai_chat, 'enable_local_ai_calculations'), "Отсутствует параметр enable_local_ai_calculations"
    assert hasattr(ai_chat, 'enable_local_ai_patterns'), "Отсутствует параметр enable_local_ai_patterns"
    assert hasattr(ai_chat, 'enable_openrouter_calculations'), "Отсутствует параметр enable_openrouter_calculations"
    assert hasattr(ai_chat, 'enable_openrouter_patterns'), "Отсутствует параметр enable_openrouter_patterns"
    
    print("  ✓ Все параметры двойной LLM системы присутствуют")
    

def test_calculation_methods():
    """Тест методов для расчетов."""
    print("Тест 2: Методы для расчетов")
    
    # Создаем экземпляр AIChat
    ai_chat = AIChat()
    
    # Проверяем наличие методов для расчетов
    assert hasattr(ai_chat, 'get_calculation_response'), "Отсутствует метод get_calculation_response"
    assert hasattr(ai_chat, 'get_external_ai_calculations_response'), "Отсутствует метод get_external_ai_calculations_response"
    assert hasattr(ai_chat, 'get_local_ai_calculations_response'), "Отсутствует метод get_local_ai_calculations_response"
    assert hasattr(ai_chat, 'get_openrouter_calculations_response'), "Отсутствует метод get_openrouter_calculations_response"
    
    print("  ✓ Все методы для расчетов присутствуют")


def test_pattern_analysis_methods():
    """Тест методов для анализа паттернов."""
    print("Тест 3: Методы для анализа паттернов")
    
    # Создаем экземпляр AIChat
    ai_chat = AIChat()
    
    # Проверяем наличие методов для анализа паттернов
    assert hasattr(ai_chat, 'get_pattern_analysis_response'), "Отсутствует метод get_pattern_analysis_response"
    assert hasattr(ai_chat, 'get_external_ai_patterns_response'), "Отсутствует метод get_external_ai_patterns_response"
    assert hasattr(ai_chat, 'get_local_ai_patterns_response'), "Отсутствует метод get_local_ai_patterns_response"
    assert hasattr(ai_chat, 'get_openrouter_patterns_response'), "Отсутствует метод get_openrouter_patterns_response"
    
    print("  ✓ Все методы для анализа паттернов присутствуют")


def test_data_formatting():
    """Тест форматирования данных для анализа."""
    print("Тест 4: Форматирование данных для анализа")
    
    # Создаем экземпляр AIChat
    ai_chat = AIChat()
    
    # Проверяем наличие метода форматирования данных
    assert hasattr(ai_chat, 'format_data_for_analysis'), "Отсутствует метод format_data_for_analysis"
    
    # Тестируем форматирование данных
    test_data = {
        "metadata": {
            "total_records": 5,
            "date_range": "2023-01-01 to 2023-12-31"
        },
        "records": [
            {"id": 1, "value": 100},
            {"id": 2, "value": 150},
            {"id": 3, "value": 200},
            {"id": 4, "value": 175},
            {"id": 5, "value": 300}
        ],
        "statistics": {
            "average": 185,
            "min": 100,
            "max": 300
        }
    }
    
    formatted_data = ai_chat.format_data_for_analysis(test_data)
    
    # Проверяем, что форматированные данные содержат ключевые элементы
    assert "Анализ данных:" in formatted_data, "Форматированные данные не содержат заголовок"
    assert "Метаданные:" in formatted_data, "Форматированные данные не содержат метаданные"
    assert "Записи" in formatted_data, "Форматированные данные не содержат записи"
    assert "Статистика:" in formatted_data, "Форматированные данные не содержат статистику"
    
    print("  ✓ Форматирование данных работает корректно")
    print(f"  Пример форматированных данных:\n{formatted_data[:200]}...")


def test_settings_update():
    """Тест обновления настроек."""
    print("Тест 5: Обновление настроек")
    
    # Создаем экземпляр AIChat
    ai_chat = AIChat()
    
    # Сохраняем исходные значения
    original_settings = {
        'enable_external_ai_calculations': ai_chat.enable_external_ai_calculations,
        'enable_external_ai_patterns': ai_chat.enable_external_ai_patterns,
        'enable_local_ai_calculations': ai_chat.enable_local_ai_calculations,
        'enable_local_ai_patterns': ai_chat.enable_local_ai_patterns,
        'enable_openrouter_calculations': ai_chat.enable_openrouter_calculations,
        'enable_openrouter_patterns': ai_chat.enable_openrouter_patterns,
    }
    
    # Новые тестовые настройки
    test_settings = {
        'enable_external_ai_calculations': True,
        'external_ai_calculations_api_key': 'test_calc_key',
        'external_ai_calculations_model': 'gpt-4',
        'external_ai_calculations_base_url': 'https://api.test.com/v1',
        
        'enable_external_ai_patterns': True,
        'external_ai_patterns_api_key': 'test_pattern_key',
        'external_ai_patterns_model': 'gpt-4-turbo',
        'external_ai_patterns_base_url': 'https://api.test.com/v1',
        
        'enable_local_ai_calculations': True,
        'local_ai_calculations_model': 'llama3',
        'local_ai_calculations_base_url': 'http://localhost:1234/v1',
        
        'enable_local_ai_patterns': True,
        'local_ai_patterns_model': 'qwen',
        'local_ai_patterns_base_url': 'http://localhost:1235/v1',
        
        'enable_openrouter_calculations': True,
        'openrouter_calculations_api_key': 'test_or_calc_key',
        'openrouter_calculations_model': 'openai/gpt-4',
        
        'enable_openrouter_patterns': True,
        'openrouter_patterns_api_key': 'test_or_pattern_key',
        'openrouter_patterns_model': 'anthropic/claude-3-opus',
    }
    
    # Обновляем настройки
    ai_chat.update_settings(test_settings)
    
    # Проверяем, что настройки обновились
    assert ai_chat.enable_external_ai_calculations == True, "Настройка enable_external_ai_calculations не обновилась"
    assert ai_chat.external_ai_calculations_api_key == 'test_calc_key', "Настройка external_ai_calculations_api_key не обновилась"
    assert ai_chat.external_ai_calculations_model == 'gpt-4', "Настройка external_ai_calculations_model не обновилась"
    assert ai_chat.enable_external_ai_patterns == True, "Настройка enable_external_ai_patterns не обновилась"
    assert ai_chat.external_ai_patterns_api_key == 'test_pattern_key', "Настройка external_ai_patterns_api_key не обновилась"
    assert ai_chat.external_ai_patterns_model == 'gpt-4-turbo', "Настройка external_ai_patterns_model не обновилась"
    assert ai_chat.enable_local_ai_calculations == True, "Настройка enable_local_ai_calculations не обновилась"
    assert ai_chat.local_ai_calculations_model == 'llama3', "Настройка local_ai_calculations_model не обновилась"
    assert ai_chat.enable_local_ai_patterns == True, "Настройка enable_local_ai_patterns не обновилась"
    assert ai_chat.local_ai_patterns_model == 'qwen', "Настройка local_ai_patterns_model не обновилась"
    assert ai_chat.enable_openrouter_calculations == True, "Настройка enable_openrouter_calculations не обновилась"
    assert ai_chat.openrouter_calculations_api_key == 'test_or_calc_key', "Настройка openrouter_calculations_api_key не обновилась"
    assert ai_chat.openrouter_calculations_model == 'openai/gpt-4', "Настройка openrouter_calculations_model не обновилась"
    assert ai_chat.enable_openrouter_patterns == True, "Настройка enable_openrouter_patterns не обновилась"
    assert ai_chat.openrouter_patterns_api_key == 'test_or_pattern_key', "Настройка openrouter_patterns_api_key не обновилась"
    assert ai_chat.openrouter_patterns_model == 'anthropic/claude-3-opus', "Настройка openrouter_patterns_model не обновилась"
    
    # Восстанавливаем исходные настройки
    ai_chat.update_settings(original_settings)
    
    print("  ✓ Обновление настроек работает корректно")


def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск тестов для двойной LLM системы")
    print("=" * 50)
    
    try:
        test_dual_llm_initialization()
        test_calculation_methods()
        test_pattern_analysis_methods()
        test_data_formatting()
        test_settings_update()
        
        print("\n" + "=" * 50)
        print("Все тесты пройдены успешно! ✓")
        
    except Exception as e:
        print(f"\nОшибка при выполнении тестов: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()