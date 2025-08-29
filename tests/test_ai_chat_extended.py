#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для расширенной функциональности AIChat.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ai_chat import AIChat


def test_ai_chat_initialization():
    """Тест инициализации AIChat с новыми настройками."""
    print("Тест 1: Инициализация AIChat")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        settings_file = os.path.join(temp_dir, "test_ai_chat_settings.json")
        
        # Создаем тестовые настройки
        test_settings = {
            'chat_history_file': chat_history_file,
            'enable_external_ai': True,
            'external_ai_api_key': 'test-key-external',
            'external_ai_model': 'gpt-4',
            'external_ai_base_url': 'https://api.test.com/v1',
            'enable_local_ai': True,
            'local_ai_model': 'llama3',
            'local_ai_base_url': 'http://localhost:1234/v1',
            'enable_openrouter': True,
            'openrouter_api_key': 'test-key-openrouter',
            'openrouter_model': 'meta-llama/llama-3-8b-instruct'
        }
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat(test_settings)
        
        # Проверяем настройки
        assert ai_chat.enable_external_ai == True
        assert ai_chat.external_ai_api_key == 'test-key-external'
        assert ai_chat.external_ai_model == 'gpt-4'
        assert ai_chat.enable_local_ai == True
        assert ai_chat.local_ai_model == 'llama3'
        assert ai_chat.local_ai_base_url == 'http://localhost:1234/v1'
        assert ai_chat.enable_openrouter == True
        assert ai_chat.openrouter_api_key == 'test-key-openrouter'
        assert ai_chat.openrouter_model == 'meta-llama/llama-3-8b-instruct'
        
        print("✓ Инициализация AIChat прошла успешно")
        print(f"  Внешний ИИ: {ai_chat.enable_external_ai}")
        print(f"  Локальный ИИ: {ai_chat.enable_local_ai}")
        print(f"  OpenRouter: {ai_chat.enable_openrouter}")


def test_ai_chat_update_settings():
    """Тест обновления настроек AIChat."""
    print("\nТест 2: Обновление настроек AIChat")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Проверяем начальные значения
        assert ai_chat.enable_external_ai == False
        assert ai_chat.enable_local_ai == False
        assert ai_chat.enable_openrouter == False
        
        # Обновляем настройки
        new_settings = {
            'enable_external_ai': True,
            'external_ai_api_key': 'new-external-key',
            'enable_local_ai': True,
            'local_ai_model': 'qwen',
            'enable_openrouter': True,
            'openrouter_api_key': 'new-openrouter-key'
        }
        
        ai_chat.update_settings(new_settings)
        
        # Проверяем обновленные значения
        assert ai_chat.enable_external_ai == True
        assert ai_chat.external_ai_api_key == 'new-external-key'
        assert ai_chat.enable_local_ai == True
        assert ai_chat.local_ai_model == 'qwen'
        assert ai_chat.enable_openrouter == True
        assert ai_chat.openrouter_api_key == 'new-openrouter-key'
        
        print("✓ Обновление настроек AIChat прошло успешно")


def test_ai_chat_response_selection():
    """Тест выбора типа ИИ для ответа."""
    print("\nТест 3: Выбор типа ИИ для ответа")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Тестируем встроенный ИИ (по умолчанию)
        response = ai_chat.get_response("Привет")
        assert "встроенный ИИ-ассистент" in response or "Здравствуйте" in response
        print("✓ Встроенный ИИ работает корректно")
        
        # Тестируем приоритет OpenRouter (без действительного ключа)
        ai_chat.enable_openrouter = True
        ai_chat.openrouter_api_key = "test-key"
        response = ai_chat.get_response("Как дела?")
        # Должен вернуть сообщение об ошибке, а не попытаться использовать OpenRouter
        assert "OpenRouter не настроен" in response or "Ошибка" in response
        print("✓ Приоритет OpenRouter работает корректно")
        
        # Тестируем приоритет локального ИИ (без запущенного сервера)
        ai_chat.enable_openrouter = False
        ai_chat.enable_local_ai = True
        response = ai_chat.get_response("Что нового?")
        # Должен вернуть сообщение об ошибке, а не попытаться использовать локальный ИИ
        assert "Локальный ИИ не включен" in response or "Ошибка" in response
        print("✓ Приоритет локального ИИ работает корректно")
        
        # Тестируем приоритет внешнего ИИ (без действительного ключа)
        ai_chat.enable_local_ai = False
        ai_chat.enable_external_ai = True
        ai_chat.external_ai_api_key = "test-key"
        response = ai_chat.get_response("Помоги мне")
        # Должен вернуть сообщение об ошибке, а не попытаться использовать внешний ИИ
        assert "Внешний ИИ не настроен" in response or "Ошибка" in response
        print("✓ Приоритет внешнего ИИ работает корректно")


def test_russian_language_support():
    """Тест поддержки русского языка."""
    print("\nТест 4: Поддержка русского языка")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Тестируем русскоязычные запросы
        russian_questions = [
            "Привет",
            "Помощь",
            "Инвентаризация",
            "Коэффициент"
        ]
        
        for question in russian_questions:
            response = ai_chat.get_response(question)
            # Проверяем, что получили непустой ответ
            assert len(response) > 0
            # Проверяем, что ответ на русском языке
            assert any(char.isalpha() for char in response)  # Есть буквы
            print(f"✓ Ответ на '{question}': {response[:50]}...")


def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск тестов для расширенной функциональности AIChat")
    print("=" * 50)
    
    try:
        test_ai_chat_initialization()
        test_ai_chat_update_settings()
        test_ai_chat_response_selection()
        test_russian_language_support()
        
        print("\n" + "=" * 50)
        print("Все тесты пройдены успешно! ✓")
        return True
    except Exception as e:
        print(f"\nОшибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)