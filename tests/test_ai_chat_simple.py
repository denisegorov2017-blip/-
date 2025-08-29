#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простые тесты для проверки расширенной функциональности AIChat.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ai_chat import AIChat


def test_methods_exist():
    """Тест наличия новых методов."""
    print("Тест 1: Проверка наличия новых методов")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Проверяем наличие новых методов
        assert hasattr(ai_chat, 'get_local_ai_response')
        assert hasattr(ai_chat, 'get_openrouter_response')
        assert hasattr(ai_chat, 'update_settings')
        
        print("✓ Все новые методы присутствуют")


def test_settings_attributes():
    """Тест наличия новых атрибутов настроек."""
    print("\nТест 2: Проверка наличия новых атрибутов настроек")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Проверяем наличие новых атрибутов
        assert hasattr(ai_chat, 'enable_local_ai')
        assert hasattr(ai_chat, 'local_ai_model')
        assert hasattr(ai_chat, 'local_ai_base_url')
        assert hasattr(ai_chat, 'enable_openrouter')
        assert hasattr(ai_chat, 'openrouter_api_key')
        assert hasattr(ai_chat, 'openrouter_model')
        
        print("✓ Все новые атрибуты настроек присутствуют")


def test_update_settings():
    """Тест обновления настроек."""
    print("\nТест 3: Проверка обновления настроек")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Обновляем настройки
        new_settings = {
            'enable_local_ai': True,
            'local_ai_model': 'test-model',
            'local_ai_base_url': 'http://test.local:1234/v1',
            'enable_openrouter': True,
            'openrouter_api_key': 'test-key',
            'openrouter_model': 'test/provider'
        }
        
        ai_chat.update_settings(new_settings)
        
        # Проверяем обновленные значения
        assert ai_chat.enable_local_ai == True
        assert ai_chat.local_ai_model == 'test-model'
        assert ai_chat.local_ai_base_url == 'http://test.local:1234/v1'
        assert ai_chat.enable_openrouter == True
        assert ai_chat.openrouter_api_key == 'test-key'
        assert ai_chat.openrouter_model == 'test/provider'
        
        print("✓ Обновление настроек работает корректно")


def test_russian_responses():
    """Тест русскоязычных ответов."""
    print("\nТест 4: Проверка русскоязычных ответов")
    
    # Создаем временные файлы для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        chat_history_file = os.path.join(temp_dir, "test_chat_history.json")
        
        # Создаем экземпляр AIChat
        ai_chat = AIChat({'chat_history_file': chat_history_file})
        
        # Тестируем русскоязычные запросы
        response = ai_chat.get_response("Привет")
        assert "Здравствуйте" in response or "встроенный ИИ-ассистент" in response
        print("✓ Русскоязычные ответы работают корректно")


def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск простых тестов для расширенной функциональности AIChat")
    print("=" * 60)
    
    try:
        test_methods_exist()
        test_settings_attributes()
        test_update_settings()
        test_russian_responses()
        
        print("\n" + "=" * 60)
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