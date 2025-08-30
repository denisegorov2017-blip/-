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
    
    def _generate_builtin_response(self, user_message: str) -> str:
        """
        Генерирует ответ на основе встроенного ИИ.
        
        Args:
            user_message (str): Сообщение пользователя.
            
        Returns:
            str: Ответ ИИ.
        """
        # Простая реализация встроенного ИИ на основе ключевых слов
        user_message_lower = user_message.lower()
        
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
            # Подготавливаем историю чата для отправки внешнему ИИ
            # Фильтруем только последние сообщения для контекста
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов."
            })
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            
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
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения."
            })
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            
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
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных."
            })
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            
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
            # Подготавливаем историю чата для отправки локальному ИИ
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов. Отвечайте на русском языке."
            })
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            
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
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения. Отвечайте на русском языке."
            })
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            
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
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных. Отвечайте на русском языке."
            })
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            
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
            # Подготавливаем историю чата для отправки OpenRouter
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - помощник по системе расчета коэффициентов усушки. Помогайте пользователям с вопросами о работе системы, подготовке данных и интерпретации результатов. Отвечайте на русском языке."
            })
            
            # Добавляем последние сообщения из истории (ограничиваем 10 последними сообщениями)
            recent_messages = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_messages:
                # Пропускаем сообщения с ролью system, так как мы добавили свое
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Добавляем текущее сообщение пользователя
            messages.append({
                "role": "user",
                "content": user_message
            })
            
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
            # Подготавливаем сообщения для расчетов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - математический ассистент. Ваша задача - выполнять точные математические расчеты и предоставлять пошаговые объяснения. Отвечайте на русском языке."
            })
            
            # Добавляем запрос для расчетов
            messages.append({
                "role": "user",
                "content": calculation_prompt
            })
            
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
            # Подготавливаем сообщения для анализа паттернов
            messages = []
            # Добавляем системное сообщение
            messages.append({
                "role": "system",
                "content": "Вы - аналитик данных. Ваша задача - выявлять скрытые паттерны, закономерности и аномалии в данных. Отвечайте на русском языке."
            })
            
            # Добавляем запрос для анализа паттернов
            messages.append({
                "role": "user",
                "content": pattern_prompt
            })
            
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
    
    def get_openrouter_model_tooltip(self, model_id: str) -> str:
        """
        Получает текст всплывающей подсказки для модели OpenRouter.
        
        Args:
            model_id (str): ID модели
            
        Returns:
            str: Текст подсказки
        """
        return get_model_tooltip_text(model_id)
    
    def update_settings(self, settings: Dict[str, Any]):
        """
        Обновляет настройки чата.
        
        Args:
            settings (Dict[str, Any]): Новые настройки.
        """
        self.config.update(settings)
        
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