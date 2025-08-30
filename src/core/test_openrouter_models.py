#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для модуля openrouter_models.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Добавляем путь к src директории
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.core.openrouter_models import (
    get_openrouter_models, 
    categorize_models, 
    get_model_pricing_info,
    format_pricing_info,
    get_recommended_free_models,
    get_recommended_paid_models,
    get_model_tooltip_text
)


class TestOpenRouterModels(unittest.TestCase):
    """Тесты для модуля openrouter_models."""

    def setUp(self):
        """Подготовка тестовых данных."""
        # Очищаем кэш перед каждым тестом
        global _cached_models, _cache_timestamp
        _cached_models = None
        _cache_timestamp = None

    @patch('src.core.openrouter_models.requests.get')
    def test_get_openrouter_models_success(self, mock_get):
        """Тест успешного получения списка моделей."""
        # Подготавливаем моковые данные
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "test/model-1",
                    "name": "Test Model 1",
                    "pricing": {"prompt": "0.0000000", "completion": "0.0000000"}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызываем тестируемую функцию
        result = get_openrouter_models()

        # Проверяем результаты
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], "test/model-1")

    @patch('src.core.openrouter_models.requests.get')
    def test_get_openrouter_models_failure(self, mock_get):
        """Тест обработки ошибки при получении списка моделей."""
        # Настраиваем мок для выбрасывания исключения
        mock_get.side_effect = Exception("Network error")

        # Вызываем тестируемую функцию
        result = get_openrouter_models()

        # Проверяем, что возвращается пустой список моделей
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 0)

    def test_categorize_models(self):
        """Тест разделения моделей на бесплатные и платные."""
        # Подготавливаем тестовые данные
        models_data = {
            "data": [
                {
                    "id": "free/model",
                    "pricing": {"prompt": "0.0000000", "completion": "0.0000000"}
                },
                {
                    "id": "paid/model",
                    "pricing": {"prompt": "0.0000005", "completion": "0.0000015"}
                }
            ]
        }

        # Вызываем тестируемую функцию
        free_models, paid_models = categorize_models(models_data)

        # Проверяем результаты
        self.assertEqual(len(free_models), 1)
        self.assertEqual(len(paid_models), 1)
        self.assertEqual(free_models[0]["id"], "free/model")
        self.assertEqual(paid_models[0]["id"], "paid/model")

    def test_format_pricing_info(self):
        """Тест форматирования информации о ценах."""
        # Тест для бесплатной модели
        free_pricing = {"prompt": "0.0000000", "completion": "0.0000000"}
        result = format_pricing_info(free_pricing)
        self.assertEqual(result, "Бесплатная модель")

        # Тест для платной модели
        paid_pricing = {"prompt": "0.0000005", "completion": "0.0000015"}
        result = format_pricing_info(paid_pricing)
        self.assertIn("Цены:", result)
        self.assertIn("входных токенов", result)
        self.assertIn("выходных токенов", result)

        # Тест для пустых данных
        result = format_pricing_info({})
        self.assertEqual(result, "Информация о ценах недоступна")

    def test_get_recommended_free_models(self):
        """Тест получения списка рекомендуемых бесплатных моделей."""
        result = get_recommended_free_models()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Проверяем, что в списке есть известные бесплатные модели
        self.assertIn("mistralai/mistral-7b-instruct", result)

    def test_get_recommended_paid_models(self):
        """Тест получения списка рекомендуемых платных моделей."""
        result = get_recommended_paid_models()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Проверяем, что в списке есть известные платные модели
        self.assertIn("openai/gpt-4o", result)

    @patch('src.core.openrouter_models.get_openrouter_models')
    def test_get_model_tooltip_text(self, mock_get_models):
        """Тест генерации текста всплывающей подсказки."""
        # Подготавливаем моковые данные
        mock_get_models.return_value = {
            "data": [
                {
                    "id": "test/model",
                    "name": "Test Model",
                    "description": "Test description",
                    "pricing": {"prompt": "0.0000000", "completion": "0.0000000"},
                    "top_provider": {"context_length": 16385}
                }
            ]
        }

        # Вызываем тестируемую функцию
        result = get_model_tooltip_text("test/model")

        # Проверяем результаты
        self.assertIn("Test Model", result)
        self.assertIn("Test description", result)
        self.assertIn("Бесплатная модель", result)
        self.assertIn("контекст", result.lower())


if __name__ == '__main__':
    unittest.main()