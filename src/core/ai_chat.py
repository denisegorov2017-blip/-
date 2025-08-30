#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с ИИ чатом в системе расчета усушки.

Этот модуль предоставляет функции для взаимодействия с встроенными и внешними ИИ моделями
для помощи пользователям в работе с системой.
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log
from src.core.openrouter_models import get_model_tooltip_text


class AIChat:
    """
    Класс для работы с ИИ чатом в системе.
    
    Предоставляет функции для взаимодействия с встроенными и внешними ИИ моделями
    для помощи пользователям в работе с системой расчета коэффициентов усушки.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализирует ИИ чат.
        
        Args:
            config (Optional[Dict[str, Any]]): Конфигурация чата.
        """
        self.config = config or {}
        
        # Загружаем настройки из файла, если они существуют
        self._load_settings()
        
        self.chat_history_file = self.config.get('chat_history_file', 'результаты/ai_chat_history.json')
        self.feedback_file = self.config.get('feedback_file', 'результаты/user_feedback.json')
        self.ratings_file = self.config.get('ratings_file', 'результаты/chat_ratings.json')
        self.knowledge_base_file = self.config.get('knowledge_base_file', 'результаты/ai_knowledge_base.json')
        self.training_data_file = self.config.get('training_data_file', 'результаты/ai_training_data.json')
        
        # Внешний ИИ настройки (для расчетов)
        self.enable_external_ai_calculations = self.config.get('enable_external_ai_calculations', False)
        self.external_ai_calculations_api_key = self.config.get('external_ai_calculations_api_key', '')
        self.external_ai_calculations_model = self.config.get('external_ai_calculations_model', 'gpt-3.5-turbo')
        self.external_ai_calculations_base_url = self.config.get('external_ai_calculations_base_url', 'https://api.openai.com/v1')
        
        # Внешний ИИ настройки (для анализа паттернов)
        self.enable_external_ai_patterns = self.config.get('enable_external_ai_patterns', False)
        self.external_ai_patterns_api_key = self.config.get('external_ai_patterns_api_key', '')
        self.external_ai_patterns_model = self.config.get('external_ai_patterns_model', 'gpt-4')
        self.external_ai_patterns_base_url = self.config.get('external_ai_patterns_base_url', 'https://api.openai.com/v1')
        
        # Локальный ИИ настройки (LM Studio) (для расчетов)
        self.enable_local_ai_calculations = self.config.get('enable_local_ai_calculations', False)
        self.local_ai_calculations_model = self.config.get('local_ai_calculations_model', 'gpt-3.5-turbo')
        self.local_ai_calculations_base_url = self.config.get('local_ai_calculations_base_url', 'http://localhost:1234/v1')
        
        # Локальный ИИ настройки (LM Studio) (для анализа паттернов)
        self.enable_local_ai_patterns = self.config.get('enable_local_ai_patterns', False)
        self.local_ai_patterns_model = self.config.get('local_ai_patterns_model', 'llama3')
        self.local_ai_patterns_base_url = self.config.get('local_ai_patterns_base_url', 'http://localhost:1235/v1')
        
        # OpenRouter настройки (для расчетов)
        self.enable_openrouter_calculations = self.config.get('enable_openrouter_calculations', False)
        self.openrouter_calculations_api_key = self.config.get('openrouter_calculations_api_key', '')
        self.openrouter_calculations_model = self.config.get('openrouter_calculations_model', 'openai/gpt-3.5-turbo')
        
        # OpenRouter настройки (для анализа паттернов)
        self.enable_openrouter_patterns = self.config.get('enable_openrouter_patterns', False)
        self.openrouter_patterns_api_key = self.config.get('openrouter_patterns_api_key', '')
        self.openrouter_patterns_model = self.config.get('openrouter_patterns_model', 'anthropic/claude-3-sonnet')
        
        # Устаревшие настройки (сохранены для совместимости)
        self.enable_external_ai = self.config.get('enable_external_ai', False)
        self.external_ai_api_key = self.config.get('external_ai_api_key', '')
        self.external_ai_model = self.config.get('external_ai_model', 'gpt-3.5-turbo')
        self.external_ai_base_url = self.config.get('external_ai_base_url', 'https://api.openai.com/v1')
        
        self.enable_local_ai = self.config.get('enable_local_ai', False)
        self.local_ai_model = self.config.get('local_ai_model', 'gpt-3.5-turbo')
        self.local_ai_base_url = self.config.get('local_ai_base_url', 'http://localhost:1234/v1')
        
        self.enable_openrouter = self.config.get('enable_openrouter', False)
        self.openrouter_api_key = self.config.get('openrouter_api_key', '')
        self.openrouter_model = self.config.get('openrouter_model', 'openai/gpt-3.5-turbo')
        
        # Загружаем историю чата
        self.chat_history = self._load_chat_history()
        
        # Загружаем обратную связь и рейтинги
        self.user_feedback = self._load_user_feedback()
        self.chat_ratings = self._load_chat_ratings()
        
        # Загружаем базу знаний
        self.knowledge_base = self._load_knowledge_base()
        
        # Загружаем данные для обучения
        self.training_data = self._load_training_data()
        
        log.info("AIChat инициализирован")
    
    def _load_settings(self):
        """
        Загружает настройки чата из файла.
        """
        try:
            settings_file = 'результаты/ai_chat_settings.json'
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.config.update(saved_settings)
        except Exception as e:
            log.error(f"Ошибка при загрузке настроек чата: {e}")
    
    def _load_chat_history(self) -> List[Dict[str, str]]:
        """
        Загружает историю чата из файла.
        
        Returns:
            List[Dict[str, str]]: История чата.
        """
        try:
            if os.path.exists(self.chat_history_file):
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем директорию если она не существует
                os.makedirs(os.path.dirname(self.chat_history_file), exist_ok=True)
                return []
        except Exception as e:
            log.error(f"Ошибка при загрузке истории чата: {e}")
            return []
    
    def _save_chat_history(self):
        """
        Сохраняет историю чата в файл.
        """
        try:
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении истории чата: {e}")
    
    def _load_user_feedback(self) -> List[Dict[str, Any]]:
        """
        Загружает пользовательскую обратную связь из файла.
        
        Returns:
            List[Dict[str, Any]]: Обратная связь пользователей.
        """
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем директорию если она не существует
                os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
                return []
        except Exception as e:
            log.error(f"Ошибка при загрузке обратной связи: {e}")
            return []
    
    def _save_user_feedback(self):
        """
        Сохраняет пользовательскую обратную связь в файл.
        """
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_feedback, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении обратной связи: {e}")
    
    def _load_chat_ratings(self) -> Dict[str, Any]:
        """
        Загружает рейтинги чатов из файла.
        
        Returns:
            Dict[str, Any]: Рейтинги чатов.
        """
        try:
            if os.path.exists(self.ratings_file):
                with open(self.ratings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем директорию если она не существует
                os.makedirs(os.path.dirname(self.ratings_file), exist_ok=True)
                return {}
        except Exception as e:
            log.error(f"Ошибка при загрузке рейтингов чатов: {e}")
            return {}
    
    def _save_chat_ratings(self):
        """
        Сохраняет рейтинги чатов в файл.
        """
        try:
            with open(self.ratings_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_ratings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении рейтингов чатов: {e}")
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Загружает базу знаний из файла.
        
        Returns:
            Dict[str, Any]: База знаний.
        """
        try:
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем директорию если она не существует
                os.makedirs(os.path.dirname(self.knowledge_base_file), exist_ok=True)
                # Возвращаем базовую структуру базы знаний
                return {
                    "responses": {},
                    "patterns": {},
                    "faq": {}
                }
        except Exception as e:
            log.error(f"Ошибка при загрузке базы знаний: {e}")
            return {
                "responses": {},
                "patterns": {},
                "faq": {}
            }
    
    def _save_knowledge_base(self):
        """
        Сохраняет базу знаний в файл.
        """
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении базы знаний: {e}")
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """
        Загружает данные для обучения из файла.
        
        Returns:
            List[Dict[str, Any]]: Данные для обучения.
        """
        try:
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем директорию если она не существует
                os.makedirs(os.path.dirname(self.training_data_file), exist_ok=True)
                return []
        except Exception as e:
            log.error(f"Ошибка при загрузке данных для обучения: {e}")
            return []
    
    def _save_training_data(self):
        """
        Сохраняет данные для обучения в файл.
        """
        try:
            with open(self.training_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении данных для обучения: {e}")
    
    def add_message(self, role: str, content: str):
        """
        Добавляет сообщение в историю чата.
        
        Args:
            role (str): Роль отправителя ("user" или "assistant").
            content (str): Содержание сообщения.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.chat_history.append(message)
        self._save_chat_history()
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Возвращает историю чата.
        
        Returns:
            List[Dict[str, str]]: История чата.
        """
        return self.chat_history
    
    def clear_chat_history(self):
        """
        Очищает историю чата.
        """
        self.chat_history = []
        self._save_chat_history()
    
    def add_user_feedback(self, message_id: str, feedback: str):
        """
        Добавляет обратную связь пользователя.
        
        Args:
            message_id (str): ID сообщения.
            feedback (str): Обратная связь пользователя.
        """
        feedback_entry = {
            "message_id": message_id,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        self.user_feedback.append(feedback_entry)
        self._save_user_feedback()
    
    def add_chat_rating(self, chat_id: str, rating: int, comment: str = ""):
        """
        Добавляет рейтинг чата.
        
        Args:
            chat_id (str): ID чата.
            rating (int): Рейтинг (1-5).
            comment (str): Комментарий к рейтингу.
        """
        self.chat_ratings[chat_id] = {
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        self._save_chat_ratings()
    
    def get_response(self, user_message: str) -> str:
        """
        Получает ответ от ИИ на сообщение пользователя.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ ИИ.
        """
        # Добавляем сообщение пользователя в историю
        self.add_message("user", user_message)
        
        # Определяем тип ИИ для использования (по умолчанию - для чата)
        # Приоритет: OpenRouter -> Локальный ИИ -> Внешний ИИ -> Встроенный ИИ
        if self.enable_openrouter and self.openrouter_api_key:
            response = self.get_openrouter_response(user_message)
        elif self.enable_local_ai:
            response = self.get_local_ai_response(user_message)
        elif self.enable_external_ai and self.external_ai_api_key:
            response = self.get_external_ai_response(user_message)
        else:
            # Генерируем ответ на основе встроенного ИИ
            response = self._generate_builtin_response(user_message)
        
        # Добавляем ответ ИИ в историю
        self.add_message("assistant", response)
        
        return response
    
    def get_calculation_response(self, calculation_data: str) -> str:
        """
        Получает ответ от ИИ для расчетов.
        
        Args:
            calculation_data (str): Данные для расчетов.
            
        Returns:
            str: Результат расчетов от ИИ.
        """
        # Формируем запрос для расчетов
        calculation_prompt = f"""Выполните расчеты на основе следующих данных:
{calculation_data}

Пожалуйста, предоставьте точные математические расчеты и объясните шаги."""

        # Определяем тип ИИ для использования (для расчетов)
        # Приоритет: Специализированные настройки -> Общие настройки -> Встроенный ИИ
        if self.enable_openrouter_calculations and self.openrouter_calculations_api_key:
            response = self.get_openrouter_calculations_response(calculation_prompt)
        elif self.enable_local_ai_calculations:
            response = self.get_local_ai_calculations_response(calculation_prompt)
        elif self.enable_external_ai_calculations and self.external_ai_calculations_api_key:
            response = self.get_external_ai_calculations_response(calculation_prompt)
        else:
            # Используем общие настройки, если специализированные не настроены
            if self.enable_openrouter and self.openrouter_api_key:
                response = self.get_openrouter_response(calculation_prompt)
            elif self.enable_local_ai:
                response = self.get_local_ai_response(calculation_prompt)
            elif self.enable_external_ai and self.external_ai_api_key:
                response = self.get_external_ai_response(calculation_prompt)
            else:
                # Генерируем ответ на основе встроенного ИИ
                response = self._generate_builtin_response(calculation_prompt)
        
        return response
    
    def get_pattern_analysis_response(self, data_for_analysis: str) -> str:
        """
        Получает ответ от ИИ для анализа паттернов.
        
        Args:
            data_for_analysis (str): Данные для анализа паттернов.
            
        Returns:
            str: Результат анализа паттернов от ИИ.
        """
        # Формируем запрос для анализа паттернов
        pattern_prompt = f"""Проанализируйте следующие данные на наличие скрытых паттернов и закономерностей:
{data_for_analysis}

Пожалуйста, определите любые повторяющиеся паттерны, аномалии или интересные закономерности в данных."""

        # Определяем тип ИИ для использования (для анализа паттернов)
        # Приоритет: Специализированные настройки -> Общие настройки -> Встроенный ИИ
        if self.enable_openrouter_patterns and self.openrouter_patterns_api_key:
            response = self.get_openrouter_patterns_response(pattern_prompt)
        elif self.enable_local_ai_patterns:
            response = self.get_local_ai_patterns_response(pattern_prompt)
        elif self.enable_external_ai_patterns and self.external_ai_patterns_api_key:
            response = self.get_external_ai_patterns_response(pattern_prompt)
        else:
            # Используем общие настройки, если специализированные не настроены
            if self.enable_openrouter and self.openrouter_api_key:
                response = self.get_openrouter_response(pattern_prompt)
            elif self.enable_local_ai:
                response = self.get_local_ai_response(pattern_prompt)
            elif self.enable_external_ai and self.external_ai_api_key:
                response = self.get_external_ai_response(pattern_prompt)
            else:
                # Генерируем ответ на основе встроенного ИИ
                response = self._generate_builtin_response(pattern_prompt)
        
        return response
    
    def estimate_tokens(self, text: str) -> int:
        """
        Оценивает количество токенов в тексте.
        Приблизительная оценка: 1 токен ≈ 4 символа для английского языка,
        1 токен ≈ 1.5 символа для русского языка.
        
        Args:
            text (str): Текст для оценки.
            
        Returns:
            int: Приблизительное количество токенов.
        """
        # Проверяем, содержит ли текст кириллические символы
        cyrillic_chars = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
        total_chars = len(text)
        
        # Если более 30% символов - кириллические, используем коэффициент для русского языка
        if total_chars > 0 and (cyrillic_chars / total_chars) > 0.3:
            # Для русского языка: 1 токен ≈ 1.5 символа
            return int(total_chars / 1.5)
        else:
            # Для английского языка: 1 токен ≈ 4 символа
            return int(total_chars / 4)
    
    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Оценивает стоимость запроса к ИИ на основе количества токенов.
        
        Args:
            model (str): Модель ИИ.
            prompt_tokens (int): Количество токенов в запросе.
            completion_tokens (int): Количество токенов в ответе.
            
        Returns:
            float: Приблизительная стоимость в долларах США.
        """
        # Цены в долларах США за 1000 токенов (приблизительные значения)
        pricing = {
            # OpenAI модели
            'gpt-3.5-turbo': {'prompt': 0.0015, 'completion': 0.002},
            'gpt-4': {'prompt': 0.03, 'completion': 0.06},
            'gpt-4-turbo': {'prompt': 0.01, 'completion': 0.03},
            
            # Anthropic модели
            'claude-3-haiku': {'prompt': 0.00025, 'completion': 0.00125},
            'claude-3-sonnet': {'prompt': 0.003, 'completion': 0.015},
            'claude-3-opus': {'prompt': 0.015, 'completion': 0.075},
            
            # OpenRouter модели (примерные цены)
            'openai/gpt-3.5-turbo': {'prompt': 0.0015, 'completion': 0.002},
            'openai/gpt-4': {'prompt': 0.03, 'completion': 0.06},
            'anthropic/claude-3-sonnet': {'prompt': 0.003, 'completion': 0.015},
            
            # По умолчанию для неизвестных моделей
            'default': {'prompt': 0.002, 'completion': 0.004}
        }
        
        # Получаем цены для модели или используем значения по умолчанию
        model_pricing = pricing.get(model, pricing['default'])
        
        # Рассчитываем стоимость
        prompt_cost = (prompt_tokens / 1000) * model_pricing['prompt']
        completion_cost = (completion_tokens / 1000) * model_pricing['completion']
        
        return prompt_cost + completion_cost
    
    def check_cost_limits(self, estimated_cost: float) -> bool:
        """
        Проверяет, не превышает ли оценочная стоимость установленные лимиты.
        
        Args:
            estimated_cost (float): Оценочная стоимость запроса.
            
        Returns:
            bool: True если стоимость в пределах лимитов, False если превышает.
        """
        # Получаем лимит из конфигурации (по умолчанию 0.1 USD)
        cost_limit = self.config.get('ai_cost_limit', 0.1)
        
        if estimated_cost > cost_limit:
            log.warning(f"Оценочная стоимость запроса ({estimated_cost:.4f} USD) превышает лимит ({cost_limit} USD)")
            return False
        
        return True
    
    def analyze_user_feedback(self):
        """
        Анализирует обратную связь пользователей для улучшения качества ответов.
        """
        if not self.user_feedback:
            return
        
        # Анализируем обратную связь
        feedback_analysis = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "common_themes": {}
        }
        
        for feedback in self.user_feedback:
            feedback_text = feedback.get("feedback", "").lower()
            # Простой анализ тональности на основе ключевых слов
            if any(word in feedback_text for word in ["хорошо", "отлично", "спасибо", "полезно", "понятно"]):
                feedback_analysis["positive"] += 1
            elif any(word in feedback_text for word in ["плохо", "неправильно", "ошибка", "непонятно", "неудобно"]):
                feedback_analysis["negative"] += 1
            else:
                feedback_analysis["neutral"] += 1
            
            # Поиск общих тем в обратной связи
            themes = ["расчет", "данные", "отчет", "интерфейс", "ошибка", "помощь"]
            for theme in themes:
                if theme in feedback_text:
                    if theme not in feedback_analysis["common_themes"]:
                        feedback_analysis["common_themes"][theme] = 0
                    feedback_analysis["common_themes"][theme] += 1
        
        log.info(f"Анализ обратной связи: {feedback_analysis}")
        return feedback_analysis
    
    def train_on_chat_history(self):
        """
        Обучает встроенный ИИ на истории чатов на основе рейтингов пользователей.
        """
        if not self.chat_ratings or not self.chat_history:
            return
        
        # Собираем данные для обучения
        training_examples = []
        
        # Проходим по рейтингам чатов
        for chat_id, rating_data in self.chat_ratings.items():
            rating = rating_data.get("rating", 0)
            # Используем только высокие рейтинги (4-5 звезд) для обучения
            if rating >= 4:
                # Находим соответствующие сообщения в истории чата
                chat_messages = []
                for message in self.chat_history:
                    # В реальной реализации здесь должна быть логика сопоставления
                    # Для упрощения берем последние сообщения
                    chat_messages.append(message)
                
                # Создаем обучающий пример
                if len(chat_messages) >= 2:
                    # Предпоследнее сообщение - запрос пользователя
                    user_message = chat_messages[-2]["content"] if chat_messages[-2]["role"] == "user" else ""
                    # Последнее сообщение - ответ ИИ
                    ai_response = chat_messages[-1]["content"] if chat_messages[-1]["role"] == "assistant" else ""
                    
                    if user_message and ai_response:
                        training_examples.append({
                            "input": user_message,
                            "output": ai_response,
                            "rating": rating
                        })
        
        # Обновляем базу знаний на основе положительных примеров
        if training_examples:
            self.update_knowledge_base(training_examples)
    
    def update_knowledge_base(self, training_examples: List[Dict[str, Any]]):
        """
        Обновляет базу знаний на основе обучающих примеров.
        
        Args:
            training_examples (List[Dict[str, Any]]): Список обучающих примеров.
        """
        # Добавляем примеры в данные для обучения
        self.training_data.extend(training_examples)
        self._save_training_data()
        
        # Обновляем базу знаний
        for example in training_examples:
            user_input = example["input"].lower()
            ai_output = example["output"]
            
            # Извлекаем ключевые слова из запроса пользователя
            keywords = self._extract_keywords(user_input)
            
            # Обновляем шаблоны ответов
            for keyword in keywords:
                if keyword not in self.knowledge_base["responses"]:
                    self.knowledge_base["responses"][keyword] = []
                # Добавляем ответ, если его еще нет
                if ai_output not in self.knowledge_base["responses"][keyword]:
                    self.knowledge_base["responses"][keyword].append(ai_output)
        
        # Сохраняем обновленную базу знаний
        self._save_knowledge_base()
        
        log.info(f"База знаний обновлена на основе {len(training_examples)} примеров")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Извлекает ключевые слова из текста.
        
        Args:
            text (str): Текст для анализа.
            
        Returns:
            List[str]: Список ключевых слов.
        """
        # Простая реализация извлечения ключевых слов
        # В реальной системе можно использовать более сложные методы NLP
        import re
        
        # Удаляем знаки препинания и приводим к нижнему регистру
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Разбиваем на слова
        words = text.split()
        
        # Фильтруем стоп-слова (упрощенный список)
        stop_words = {"и", "в", "на", "с", "о", "к", "по", "из", "от", "для", "не", "же", "бы", "ли", "быть", "как", "что", "это", "который"}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def reasoning_engine(self, user_message: str) -> Optional[str]:
        """
        Механизм рассуждения для решения сложных задач.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            Optional[str]: Результат рассуждения или None, если не удалось обработать.
        """
        user_message_lower = user_message.lower()
        
        # Проверяем, является ли запрос сложной задачей, требующей рассуждения
        if any(keyword in user_message_lower for keyword in ["как", "почему", "объясни", "посчитай", "рассчитай", "анализ"]):
            # Простая логика рассуждения на основе шаблонов
            if "расчет" in user_message_lower and ("коэффициент" in user_message_lower or "усушк" in user_message_lower):
                return self._reason_about_shrinkage_calculation(user_message)
            elif "инвентаризац" in user_message_lower and ("данны" in user_message_lower or "файл" in user_message_lower):
                return self._reason_about_inventory_data(user_message)
            elif "точност" in user_message_lower or "верификаци" in user_message_lower:
                return self._reason_about_accuracy_verification(user_message)
            elif "паттерн" in user_message_lower or "закономерн" in user_message_lower:
                return self._reason_about_patterns(user_message)
        
        # Для простых запросов возвращаем None, чтобы использовать обычный механизм
        return None
    
    def _reason_about_shrinkage_calculation(self, user_message: str) -> str:
        """
        Рассуждение о расчете коэффициентов усушки.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Результат рассуждения.
        """
        return """Для расчета коэффициентов усушки система использует следующий подход:
        
1. Сбор данных: Система анализирует исторические данные инвентаризации, включая начальные и конечные остатки, приход и расход.

2. Формула расчета: Используется нелинейная модель усушки: S(t) = a*(1 - exp(-b*t)) + c*t
   - a: максимальная усушка
   - b: скорость достижения максимальной усушки
   - c: линейная компонента
   - t: период хранения в днях

3. Адаптация: Система адаптирует коэффициенты на основе новых данных инвентаризации для повышения точности.

4. Верификация: Результаты проверяются на точность с помощью обратного пересчета и сравнения с фактическими данными.

Если у вас есть конкретные данные, я могу помочь вам понять, как они будут обработаны системой."""
    
    def _reason_about_inventory_data(self, user_message: str) -> str:
        """
        Рассуждение о данных инвентаризации.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Результат рассуждения.
        """
        return """Данные инвентаризации играют ключевую роль в работе системы:
        
1. Источник информации: Инвентаризации предоставляют фактические данные о наличии товара в разные периоды времени.

2. Расчет недостач: Система сравнивает ожидаемые остатки (на основе прихода и расхода) с фактическими данными инвентаризации для определения недостач.

3. Периоды хранения: Данные инвентаризации используются для определения периодов хранения товаров, что критически важно для расчета усушки.

4. Адаптивное обучение: Система использует данные инвентаризации для самообучения и уточнения коэффициентов усушки.

Для корректной работы система требует:
- Номенклатуру товаров
- Даты и значения начальных остатков
- Даты и значения конечных остатков
- Приход и расход между инвентаризациями"""
    
    def _reason_about_accuracy_verification(self, user_message: str) -> str:
        """
        Рассуждение о верификации точности.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Результат рассуждения.
        """
        return """Система включает многоуровневую верификацию точности расчетов:
        
1. Обратный пересчет: Система проверяет коэффициенты, выполняя обратный пересчет предварительной усушки по тем же коэффициентам.

2. Сравнение с фактическими данными: Рассчитанные значения сравниваются с фактическими данными инвентаризации.

3. Метрики точности: Система рассчитывает несколько метрик:
   - R² (коэффициент детерминации)
   - RMSE (среднеквадратическая ошибка)
   - MAE (средняя абсолютная ошибка)

4. Пороги качества: Результаты оцениваются по шкале от 0% до 100% точности.

Эта верификация позволяет пользователям оценить надежность расчетов и принимать обоснованные решения."""
    
    def _reason_about_patterns(self, user_message: str) -> str:
        """
        Рассуждение о паттернах и закономерностях.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Результат рассуждения.
        """
        return """Анализ паттернов в данных усушки позволяет выявить скрытые закономерности:
        
1. Сезонные колебания: Некоторые товары могут иметь сезонные изменения в усушке.

2. Зависимость от условий хранения: Температура, влажность и другие факторы могут влиять на усушку.

3. Типы продукции: Разные категории товаров могут иметь различные паттерны усушки.

4. Аномалии: Система может выявлять аномальные значения, которые требуют дополнительного внимания.

Для глубокого анализа паттернов рекомендуется использовать специализированные ИИ-модели через внешние сервисы или локальные установки."""
    
    def _generate_builtin_response(self, user_message: str) -> str:
        """
        Генерирует ответ на основе встроенного ИИ.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ ИИ.
        """
        # Применяем механизм рассуждения
        reasoning_result = self.reasoning_engine(user_message)
        if reasoning_result:
            return reasoning_result
        
        # Ищем ответ в базе знаний
        user_message_lower = user_message.lower()
        keywords = self._extract_keywords(user_message_lower)
        
        # Ищем совпадения по ключевым словам
        best_responses = []
        for keyword in keywords:
            if keyword in self.knowledge_base["responses"]:
                # Добавляем все ответы для этого ключевого слова
                for response in self.knowledge_base["responses"][keyword]:
                    best_responses.append(response)
        
        # Если нашли ответы в базе знаний, возвращаем случайный из них
        if best_responses:
            import random
            return random.choice(best_responses)
        
        # Если нет совпадений, используем базовые правила
        if "привет" in user_message_lower or "здравствуй" in user_message_lower:
            return "Здравствуйте! Я встроенный ИИ-ассистент системы расчета коэффициентов усушки. Чем могу помочь?"
        
        elif "помощь" in user_message_lower or "help" in user_message_lower:
            return """Я могу помочь вам с:
1. Объяснением работы системы расчета коэффициентов усушки
2. Пояснением по данным инвентаризации
3. Рекомендациями по подготовке данных
4. Объяснением результатов расчетов
5. Решением технических проблем

Просто задайте мне вопрос!"""
        
        elif "инвентаризация" in user_message_lower or "остаток" in user_message_lower:
            return """Система работает с данными инвентаризации, которые содержат информацию о недостачах.
Начальный остаток берется на начало периода по датам инвентаризации.
Конечный остаток берется на конец периода по датам инвентаризации.
Если в данных отсутствуют инвентаризации, система выводит предупреждение, но продолжает работу с имеющимися данными."""
        
        elif "коэффициент" in user_message_lower or "расчет" in user_message_lower:
            return """Система использует формулу нелинейной усушки: S(t) = a*(1 - exp(-b*t)) + c*t
где:
- a = максимальная усушка
- b = скорость достижения максимальной усушки
- c = линейная компонента
- t = период хранения в днях

Коэффициенты a, b и c рассчитываются на основе исторических данных инвентаризации."""
        
        elif "данные" in user_message_lower or "excel" in user_message_lower:
            return """Для корректной работы система требует Excel файлы со следующими столбцами:
- Номенклатура
- Начальный остаток (на начало периода по датам инвентаризации)
- Приход
- Расход
- Конечный остаток (на конец периода по датам инвентаризации)
- Период хранения (дней)

Чем полнее данные, тем точнее расчеты коэффициентов усушки."""
        
        elif "точность" in user_message_lower or "верификация" in user_message_lower:
            return """Система включает механизм верификации коэффициентов:
1. Обратный пересчет предварительной усушки по тем же коэффициентам
2. Сравнение прогнозируемых и фактических значений усушки
3. Расчет метрик точности (R², RMSE, MAE)

Точность отображается в отчетах и может варьироваться от 0% до 100%."""
        
        elif "расчет" in user_message_lower and ("математик" in user_message_lower or "точн" in user_message_lower):
            return """Для выполнения математических расчетов рекомендуется использовать специализированную модель ИИ.
Пожалуйста, настройте внешний ИИ или локальную модель для выполнения точных расчетов."""
        
        elif "паттерн" in user_message_lower or "закономерн" in user_message_lower:
            return """Для анализа паттернов и закономерностей в данных рекомендуется использовать мощную модель ИИ.
Пожалуйста, настройте внешний ИИ или локальную модель для выявления скрытых паттернов."""
        
        else:
            # Базовый ответ для других запросов
            return """Спасибо за ваш вопрос! Я встроенный ИИ-ассистент системы расчета коэффициентов усушки.
            
Моя основная функция - помогать пользователям понимать работу системы и правильно готовить данные для расчетов.
            
Если у вас есть конкретный вопрос о работе с системой, пожалуйста, уточните его, и я постараюсь дать более подробный ответ.

Вы также можете обратиться к документации системы или использовать внешние ИИ-сервисы для более сложных запросов."""
    
    def get_external_ai_response(self, user_message: str) -> str:
        """
        Получает ответ от внешнего ИИ (если включено).
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ внешнего ИИ.
        """
        if not self.enable_external_ai or not self.external_ai_api_key:
            return "Внешний ИИ не настроен. Пожалуйста, настройте API ключ в конфигурации."
        
        try:
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(user_message)
            
            # Подготавливаем историю чата для отправки внешнему ИИ
            # Фильтруем только последние сообщения для контекста
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                    prompt_tokens += self.estimate_tokens(msg["content"])
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            prompt_tokens += self.estimate_tokens(user_message)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 200  # Приблизительная оценка длины ответа
            estimated_cost = self.estimate_cost(self.external_ai_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.external_ai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.external_ai_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Отправляем запрос к API
            response = requests.post(
                f"{self.external_ai_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к внешнему ИИ: {e}")
            return f"Ошибка сети при взаимодействии с внешним ИИ: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от внешнего ИИ: {e}")
            return "Ошибка обработки ответа от внешнего ИИ. Проверьте настройки API."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от внешнего ИИ: {e}")
            return f"Произошла ошибка при взаимодействии с внешним ИИ: {str(e)}"
    
    def get_external_ai_calculations_response(self, calculation_prompt: str) -> str:
        """
        Получает ответ от внешнего ИИ для расчетов.
        
        Args:
            calculation_prompt (str): Запрос для расчетов.
            
        Returns:
            str: Ответ внешнего ИИ для расчетов.
        """
        if not self.enable_external_ai_calculations or not self.external_ai_calculations_api_key:
            return "Внешний ИИ для расчетов не настроен. Пожалуйста, настройте API ключ в конфигурации."
        
        try:
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(calculation_prompt)
            
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            prompt_tokens += self.estimate_tokens(calculation_prompt)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для расчетов
            estimated_cost = self.estimate_cost(self.external_ai_calculations_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.external_ai_calculations_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.external_ai_calculations_model,
                "messages": messages,
                "temperature": 0.2,  # Низкая температура для точных расчетов
                "max_tokens": 1000
            }
            
            # Отправляем запрос к API
            response = requests.post(
                f"{self.external_ai_calculations_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к внешнему ИИ для расчетов: {e}")
            return f"Ошибка сети при взаимодействии с внешним ИИ для расчетов: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от внешнего ИИ для расчетов: {e}")
            return "Ошибка обработки ответа от внешнего ИИ для расчетов. Проверьте настройки API."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от внешнего ИИ для расчетов: {e}")
            return f"Произошла ошибка при взаимодействии с внешним ИИ для расчетов: {str(e)}"
    
    def get_external_ai_patterns_response(self, pattern_prompt: str) -> str:
        """
        Получает ответ от внешнего ИИ для анализа паттернов.
        
        Args:
            pattern_prompt (str): Запрос для анализа паттернов.
            
        Returns:
            str: Ответ внешнего ИИ для анализа паттернов.
        """
        if not self.enable_external_ai_patterns or not self.external_ai_patterns_api_key:
            return "Внешний ИИ для анализа паттернов не настроен. Пожалуйста, настройте API ключ в конфигурации."
        
        try:
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(pattern_prompt)
            
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            prompt_tokens += self.estimate_tokens(pattern_prompt)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для анализа
            estimated_cost = self.estimate_cost(self.external_ai_patterns_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.external_ai_patterns_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.external_ai_patterns_model,
                "messages": messages,
                "temperature": 0.5,  # Средняя температура для анализа
                "max_tokens": 1000
            }
            
            # Отправляем запрос к API
            response = requests.post(
                f"{self.external_ai_patterns_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к внешнему ИИ для анализа паттернов: {e}")
            return f"Ошибка сети при взаимодействии с внешним ИИ для анализа паттернов: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от внешнего ИИ для анализа паттернов: {e}")
            return "Ошибка обработки ответа от внешнего ИИ для анализа паттернов. Проверьте настройки API."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от внешнего ИИ для анализа паттернов: {e}")
            return f"Произошла ошибка при взаимодействии с внешним ИИ для анализа паттернов: {str(e)}"
    
    def apply_token_saving_mode(self, text: str, saving_level: str = "medium") -> str:
        """
        Применяет режим экономии токенов к тексту.
        
        Args:
            text (str): Исходный текст.
            saving_level (str): Уровень экономии ("low", "medium", "high").
            
        Returns:
            str: Текст с примененным режимом экономии токенов.
        """
        if saving_level == "low":
            # Низкий уровень экономии - минимальные изменения
            # Удаляем лишние пробелы и сокращаем повторяющиеся символы
            import re
            # Удаляем повторяющиеся пробелы
            text = re.sub(r'\s+', ' ', text)
            # Удаляем повторяющиеся символы (более 3 подряд)
            text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
            return text.strip()
        
        elif saving_level == "medium":
            # Средний уровень экономии
            import re
            # Удаляем повторяющиеся пробелы
            text = re.sub(r'\s+', ' ', text)
            # Удаляем повторяющиеся символы (более 2 подряд)
            text = re.sub(r'(.)\1{2,}', r'\1\1', text)
            # Сокращаем длинные слова (более 15 символов) до первых 15 символов + "..."
            words = text.split()
            shortened_words = []
            for word in words:
                if len(word) > 15:
                    shortened_words.append(word[:15] + "...")
                else:
                    shortened_words.append(word)
            return " ".join(shortened_words).strip()
        
        elif saving_level == "high":
            # Высокий уровень экономии
            import re
            # Удаляем повторяющиеся пробелы
            text = re.sub(r'\s+', ' ', text)
            # Удаляем повторяющиеся символы (более 1 подряд)
            text = re.sub(r'(.)\1{1,}', r'\1', text)
            # Сокращаем слова до первых 10 символов + "..."
            words = text.split()
            shortened_words = []
            for word in words:
                if len(word) > 10:
                    shortened_words.append(word[:10] + ".")
                else:
                    shortened_words.append(word)
            # Ограничиваем общую длину текста
            result = " ".join(shortened_words).strip()
            if len(result) > 500:
                result = result[:500] + "..."
            return result
        
        else:
            # Без экономии
            return text.strip()
    
    def adapt_to_model_specifics(self, model: str, prompt: str) -> str:
        """
        Адаптирует запрос под особенности конкретной модели ИИ.
        
        Args:
            model (str): Модель ИИ.
            prompt (str): Исходный запрос.
            
        Returns:
            str: Адаптированный запрос.
        """
        # Применяем общие оптимизации
        # Удаляем лишние пробелы
        import re
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        # Адаптация под конкретные модели
        if 'gpt' in model.lower():
            # Для моделей GPT добавляем четкие инструкции в начало
            if not prompt.startswith("Выполните") and not prompt.startswith("Проанализируйте") and not prompt.startswith("Объясните"):
                prompt = "Пожалуйста, выполните следующий запрос: " + prompt
            return prompt
        
        elif 'claude' in model.lower():
            # Для моделей Claude добавляем структурированные инструкции
            if "Human:" not in prompt and "Assistant:" not in prompt:
                prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
            return prompt
        
        elif 'llama' in model.lower() or 'mistral' in model.lower():
            # Для моделей Llama и Mistral добавляем инструкции в формате системного сообщения
            # (это будет обрабатываться на уровне формирования сообщений)
            return prompt
        
        elif 'qwen' in model.lower():
            # Для моделей Qwen оптимизируем под русский язык
            # Добавляем указание отвечать на русском языке, если в тексте есть кириллица
            if any('\u0400' <= char <= '\u04FF' for char in prompt):
                if "Ответ на русском" not in prompt and "на русском языке" not in prompt:
                    prompt = "Ответ на русском языке: " + prompt
            return prompt
        
        else:
            # Для остальных моделей возвращаем как есть
            return prompt
    
    def get_local_ai_response(self, user_message: str) -> str:
        """
        Получает ответ от локального ИИ через LM Studio.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ локального ИИ.
        """
        if not self.enable_local_ai:
            return "Локальный ИИ не включен. Пожалуйста, включите локальный ИИ в настройках."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                user_message = self.apply_token_saving_mode(user_message, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            user_message = self.adapt_to_model_specifics(self.local_ai_model, user_message)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(user_message)
            
            # Подготавливаем историю чата для отправки локальному ИИ
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    content = msg["content"]
                    # Применяем режим экономии токенов к истории тоже
                    if token_saving_mode != 'none':
                        content = self.apply_token_saving_mode(content, token_saving_mode)
                    # Адаптируем под модель
                    content = self.adapt_to_model_specifics(self.local_ai_model, content)
                    
                    messages.append({
                        "role": msg["role"],
                        "content": content
                    })
                    prompt_tokens += self.estimate_tokens(content)
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            prompt_tokens += self.estimate_tokens(user_message)
            
            # Оцениваем стоимость запроса (для локальных моделей стоимость 0, но оцениваем для информации)
            estimated_completion_tokens = 200  # Приблизительная оценка длины ответа
            estimated_cost = self.estimate_cost(self.local_ai_model, prompt_tokens, estimated_completion_tokens)
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.local_ai_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Отправляем запрос к локальному серверу LM Studio
            response = requests.post(
                f"{self.local_ai_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # Увеличенный таймаут для локальных моделей
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к локальному ИИ: {e}")
            return f"Ошибка сети при взаимодействии с локальным ИИ: {str(e)}. Убедитесь, что LM Studio запущен и сервер активен."
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от локального ИИ: {e}")
            return "Ошибка обработки ответа от локального ИИ. Проверьте настройки локального ИИ."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от локального ИИ: {e}")
            return f"Произошла ошибка при взаимодействии с локальным ИИ: {str(e)}"
    
    def get_local_ai_calculations_response(self, calculation_prompt: str) -> str:
        """
        Получает ответ от локального ИИ для расчетов.
        
        Args:
            calculation_prompt (str): Запрос для расчетов.
            
        Returns:
            str: Ответ локального ИИ для расчетов.
        """
        if not self.enable_local_ai_calculations:
            return "Локальный ИИ для расчетов не включен. Пожалуйста, включите локальный ИИ в настройках."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                calculation_prompt = self.apply_token_saving_mode(calculation_prompt, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            calculation_prompt = self.adapt_to_model_specifics(self.local_ai_calculations_model, calculation_prompt)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(calculation_prompt)
            
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            prompt_tokens += self.estimate_tokens(calculation_prompt)
            
            # Оцениваем стоимость запроса (для локальных моделей стоимость 0, но оцениваем для информации)
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для расчетов
            estimated_cost = self.estimate_cost(self.local_ai_calculations_model, prompt_tokens, estimated_completion_tokens)
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.local_ai_calculations_model,
                "messages": messages,
                "temperature": 0.2,  # Низкая температура для точных расчетов
                "max_tokens": 1000
            }
            
            # Отправляем запрос к локальному серверу LM Studio
            response = requests.post(
                f"{self.local_ai_calculations_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # Увеличенный таймаут для локальных моделей
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к локальному ИИ для расчетов: {e}")
            return f"Ошибка сети при взаимодействии с локальным ИИ для расчетов: {str(e)}. Убедитесь, что LM Studio запущен и сервер активен."
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от локального ИИ для расчетов: {e}")
            return "Ошибка обработки ответа от локального ИИ для расчетов. Проверьте настройки локального ИИ."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от локального ИИ для расчетов: {e}")
            return f"Произошла ошибка при взаимодействии с локальным ИИ для расчетов: {str(e)}"
    
    def get_local_ai_patterns_response(self, pattern_prompt: str) -> str:
        """
        Получает ответ от локального ИИ для анализа паттернов.
        
        Args:
            pattern_prompt (str): Запрос для анализа паттернов.
            
        Returns:
            str: Ответ локального ИИ для анализа паттернов.
        """
        if not self.enable_local_ai_patterns:
            return "Локальный ИИ для анализа паттернов не включен. Пожалуйста, включите локальный ИИ в настройках."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                pattern_prompt = self.apply_token_saving_mode(pattern_prompt, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            pattern_prompt = self.adapt_to_model_specifics(self.local_ai_patterns_model, pattern_prompt)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(pattern_prompt)
            
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            prompt_tokens += self.estimate_tokens(pattern_prompt)
            
            # Оцениваем стоимость запроса (для локальных моделей стоимость 0, но оцениваем для информации)
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для анализа
            estimated_cost = self.estimate_cost(self.local_ai_patterns_model, prompt_tokens, estimated_completion_tokens)
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.local_ai_patterns_model,
                "messages": messages,
                "temperature": 0.5,  # Средняя температура для анализа
                "max_tokens": 1000
            }
            
            # Отправляем запрос к локальному серверу LM Studio
            response = requests.post(
                f"{self.local_ai_patterns_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # Увеличенный таймаут для локальных моделей
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к локальному ИИ для анализа паттернов: {e}")
            return f"Ошибка сети при взаимодействии с локальным ИИ для анализа паттернов: {str(e)}. Убедитесь, что LM Studio запущен и сервер активен."
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от локального ИИ для анализа паттернов: {e}")
            return "Ошибка обработки ответа от локального ИИ для анализа паттернов. Проверьте настройки локального ИИ."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от локального ИИ для анализа паттернов: {e}")
            return f"Произошла ошибка при взаимодействии с локальным ИИ для анализа паттернов: {str(e)}"
    
    def get_openrouter_calculations_response(self, calculation_prompt: str) -> str:
        """
        Получает ответ от OpenRouter для расчетов.
        
        Args:
            calculation_prompt (str): Запрос для расчетов.
            
        Returns:
            str: Ответ от OpenRouter для расчетов.
        """
        if not self.enable_openrouter_calculations or not self.openrouter_calculations_api_key:
            return "OpenRouter для расчетов не настроен. Пожалуйста, настройте API ключ OpenRouter в конфигурации."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                calculation_prompt = self.apply_token_saving_mode(calculation_prompt, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            calculation_prompt = self.adapt_to_model_specifics(self.openrouter_calculations_model, calculation_prompt)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(calculation_prompt)
            
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            prompt_tokens += self.estimate_tokens(calculation_prompt)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для расчетов
            estimated_cost = self.estimate_cost(self.openrouter_calculations_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.openrouter_calculations_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.openrouter_calculations_model,
                "messages": messages,
                "temperature": 0.2,  # Низкая температура для точных расчетов
                "max_tokens": 1000
            }
            
            # Отправляем запрос к OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к OpenRouter для расчетов: {e}")
            return f"Ошибка сети при взаимодействии с OpenRouter для расчетов: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от OpenRouter для расчетов: {e}")
            return "Ошибка обработки ответа от OpenRouter для расчетов. Проверьте настройки OpenRouter."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от OpenRouter для расчетов: {e}")
            return f"Произошла ошибка при взаимодействии с OpenRouter для расчетов: {str(e)}"
    
    def get_openrouter_patterns_response(self, pattern_prompt: str) -> str:
        """
        Получает ответ от OpenRouter для анализа паттернов.
        
        Args:
            pattern_prompt (str): Запрос для анализа паттернов.
            
        Returns:
            str: Ответ от OpenRouter для анализа паттернов.
        """
        if not self.enable_openrouter_patterns or not self.openrouter_patterns_api_key:
            return "OpenRouter для анализа паттернов не настроен. Пожалуйста, настройте API ключ OpenRouter в конфигурации."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                pattern_prompt = self.apply_token_saving_mode(pattern_prompt, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            pattern_prompt = self.adapt_to_model_specifics(self.openrouter_patterns_model, pattern_prompt)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(pattern_prompt)
            
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            prompt_tokens += self.estimate_tokens(pattern_prompt)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 500  # Приблизительная оценка длины ответа для анализа
            estimated_cost = self.estimate_cost(self.openrouter_patterns_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.openrouter_patterns_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.openrouter_patterns_model,
                "messages": messages,
                "temperature": 0.5,  # Средняя температура для анализа
                "max_tokens": 1000
            }
            
            # Отправляем запрос к OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к OpenRouter для анализа паттернов: {e}")
            return f"Ошибка сети при взаимодействии с OpenRouter для анализа паттернов: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от OpenRouter для анализа паттернов: {e}")
            return "Ошибка обработки ответа от OpenRouter для анализа паттернов. Проверьте настройки OpenRouter."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от OpenRouter для анализа паттернов: {e}")
            return f"Произошла ошибка при взаимодействии с OpenRouter для анализа паттернов: {str(e)}"
    
    def get_openrouter_response(self, user_message: str) -> str:
        """
        Получает ответ от OpenRouter.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ от OpenRouter.
        """
        if not self.enable_openrouter or not self.openrouter_api_key:
            return "OpenRouter не настроен. Пожалуйста, настройте API ключ OpenRouter в конфигурации."
        
        try:
            # Применяем режим экономии токенов, если включено
            token_saving_mode = self.config.get('token_saving_mode', 'none')
            if token_saving_mode != 'none':
                user_message = self.apply_token_saving_mode(user_message, token_saving_mode)
            
            # Адаптируем запрос под особенности модели
            user_message = self.adapt_to_model_specifics(self.openrouter_model, user_message)
            
            # Оцениваем количество токенов в запросе
            prompt_tokens = self.estimate_tokens(user_message)
            
            # Подготавливаем историю чата для отправки OpenRouter
            messages = []
            # Добавляем системное сообщение
            system_message = "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов. Отвечайте на русском языке."
            messages.append({
                "role": "system",
                "content": system_message
            })
            prompt_tokens += self.estimate_tokens(system_message)
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    content = msg["content"]
                    # Применяем режим экономии токенов к истории тоже
                    if token_saving_mode != 'none':
                        content = self.apply_token_saving_mode(content, token_saving_mode)
                    # Адаптируем под модель
                    content = self.adapt_to_model_specifics(self.openrouter_model, content)
                    
                    messages.append({
                        "role": msg["role"],
                        "content": content
                    })
                    prompt_tokens += self.estimate_tokens(content)
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            prompt_tokens += self.estimate_tokens(user_message)
            
            # Оцениваем стоимость запроса
            estimated_completion_tokens = 200  # Приблизительная оценка длины ответа
            estimated_cost = self.estimate_cost(self.openrouter_model, prompt_tokens, estimated_completion_tokens)
            
            # Проверяем лимиты стоимости
            if not self.check_cost_limits(estimated_cost):
                return f"Запрос отклонен: оценочная стоимость ({estimated_cost:.4f} USD) превышает установленный лимит. Пожалуйста, уточните ваш запрос или увеличьте лимит."
            
            # Подготавливаем заголовки для API запроса
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем тело запроса
            payload = {
                "model": self.openrouter_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Отправляем запрос к OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем ответ из JSON
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"].strip()
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка сети при запросе к OpenRouter: {e}")
            return f"Ошибка сети при взаимодействии с OpenRouter: {str(e)}"
        except KeyError as e:
            log.error(f"Ошибка обработки ответа от OpenRouter: {e}")
            return "Ошибка обработки ответа от OpenRouter. Проверьте настройки OpenRouter."
        except Exception as e:
            log.error(f"Неожиданная ошибка при получении ответа от OpenRouter: {e}")
            return f"Произошла ошибка при взаимодействии с OpenRouter: {str(e)}"
        
        # Локальный ИИ настройки (LM Studio) (для анализа паттернов)
        self.enable_local_ai_patterns = self.config.get('enable_local_ai_patterns', False)
        self.local_ai_patterns_model = self.config.get('local_ai_patterns_model', 'llama3')
        self.local_ai_patterns_base_url = self.config.get('local_ai_patterns_base_url', 'http://localhost:1235/v1')
        
        # OpenRouter настройки (для расчетов)
        self.enable_openrouter_calculations = self.config.get('enable_openrouter_calculations', False)
        self.openrouter_calculations_api_key = self.config.get('openrouter_calculations_api_key', '')
        self.openrouter_calculations_model = self.config.get('openrouter_calculations_model', 'openai/gpt-3.5-turbo')
        
        # OpenRouter настройки (для анализа паттернов)
        self.enable_openrouter_patterns = self.config.get('enable_openrouter_patterns', False)
        self.openrouter_patterns_api_key = self.config.get('openrouter_patterns_api_key', '')
        self.openrouter_patterns_model = self.config.get('openrouter_patterns_model', 'anthropic/claude-3-sonnet')
        
        # Устаревшие настройки (сохранены для совместимости)
        self.enable_external_ai = self.config.get('enable_external_ai', False)
        self.external_ai_api_key = self.config.get('external_ai_api_key', '')
        self.external_ai_model = self.config.get('external_ai_model', 'gpt-3.5-turbo')
        self.external_ai_base_url = self.config.get('external_ai_base_url', 'https://api.openai.com/v1')
        
        self.enable_local_ai = self.config.get('enable_local_ai', False)
        self.local_ai_model = self.config.get('local_ai_model', 'gpt-3.5-turbo')
        self.local_ai_base_url = self.config.get('local_ai_base_url', 'http://localhost:1234/v1')
        
        self.enable_openrouter = self.config.get('enable_openrouter', False)
        self.openrouter_api_key = self.config.get('openrouter_api_key', '')
        self.openrouter_model = self.config.get('openrouter_model', 'openai/gpt-3.5-turbo')
        
        # Сохраняем настройки в файл конфигурации
        self._save_settings()
    
    def _save_settings(self):
        """
        Сохраняет настройки чата в файл.
        """
        try:
            settings_file = 'результаты/ai_chat_settings.json'
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Ошибка при сохранении настроек чата: {e}")

    def format_data_for_analysis(self, data: Dict[str, Any]) -> str:
        """
        Форматирует данные для лучшего анализа ИИ.
        
        Args:
            data (Dict[str, Any]): Исходные данные
            
        Returns:
            str: Отформатированные данные для анализа
        """
        formatted_data = "Анализ данных:\n"
        
        # Добавляем метаданные
        if 'metadata' in data:
            formatted_data += f"Метаданные:\n"
            for key, value in data['metadata'].items():
                formatted_data += f"  {key}: {value}\n"
            formatted_data += "\n"
        
        # Добавляем основные данные
        if 'records' in data:
            formatted_data += f"Записи ({len(data['records'])} шт.):\n"
            for i, record in enumerate(data['records'][:10]):  # Ограничиваем первыми 10 записями
                formatted_data += f"  Запись {i+1}:\n"
                for key, value in record.items():
                    formatted_data += f"    {key}: {value}\n"
            if len(data['records']) > 10:
                formatted_data += f"  ... и еще {len(data['records']) - 10} записей\n"
            formatted_data += "\n"
        
        # Добавляем статистику, если есть
        if 'statistics' in data:
            formatted_data += "Статистика:\n"
            for key, value in data['statistics'].items():
                formatted_data += f"  {key}: {value}\n"
            formatted_data += "\n"
        
        # Добавляем инструкции для ИИ
        formatted_data += "Пожалуйста, проанализируйте эти данные и выявите скрытые паттерны, аномалии или интересные закономерности.\n"
        formatted_data += "Обратите особое внимание на возможные корреляции между различными параметрами.\n"
        
        return formatted_data


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр класса
    ai_chat = AIChat()
    
    # Пример использования
    print("🔍 Демонстрация работы ИИ чата")
    print("=" * 50)
    
    # Добавляем сообщение пользователя
    user_msg = "Как работает система расчета коэффициентов усушки?"
    ai_chat.add_message("user", user_msg)
    
    # Получаем ответ ИИ
    response = ai_chat.get_response(user_msg)
    print(f"Пользователь: {user_msg}")
    print(f"ИИ: {response}")
    
    # Показываем историю чата
    print("\nИстория чата:")
    for msg in ai_chat.get_chat_history():
        print(f"{msg['timestamp']} [{msg['role']}]: {msg['content']}")