#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с моделями OpenRouter и получения актуальной информации о них.

Этот модуль предоставляет функции для получения списка моделей OpenRouter,
их цен и разделения на бесплатные и платные.
"""

import requests
import json
from typing import Dict, List, Tuple, Optional
from logger_config import log


# Кэшированные данные моделей
_cached_models = None
_cache_timestamp = None
_cache_timeout = 3600  # 1 час


def get_openrouter_models(force_refresh: bool = False) -> Dict:
    """
    Получает список моделей OpenRouter с их информацией.
    
    Args:
        force_refresh (bool): Принудительно обновить кэш
        
    Returns:
        Dict: Словарь с информацией о моделях
    """
    global _cached_models, _cache_timestamp
    
    # Проверяем кэш
    import time
    current_time = time.time()
    if not force_refresh and _cached_models and _cache_timestamp:
        if current_time - _cache_timestamp < _cache_timeout:
            return _cached_models
    
    try:
        # Запрашиваем данные у OpenRouter API
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        response.raise_for_status()
        models_data = response.json()
        
        # Кэшируем данные
        _cached_models = models_data
        _cache_timestamp = current_time
        
        return models_data
    except Exception as e:
        log.error(f"Ошибка при получении списка моделей OpenRouter: {e}")
        # Возвращаем кэшированные данные, если они есть
        if _cached_models:
            return _cached_models
        # Иначе возвращаем пустой словарь
        return {"data": []}


def categorize_models(models_data: Dict) -> Tuple[List[Dict], List[Dict]]:
    """
    Разделяет модели на бесплатные и платные.
    
    Args:
        models_data (Dict): Данные о моделях от OpenRouter API
        
    Returns:
        Tuple[List[Dict], List[Dict]]: Кортеж из списков бесплатных и платных моделей
    """
    free_models = []
    paid_models = []
    
    for model in models_data.get("data", []):
        try:
            pricing = model.get("pricing", {})
            prompt_price = float(pricing.get("prompt", "0"))
            completion_price = float(pricing.get("completion", "0"))
            
            # Если цена 0 или очень маленькая, считаем модель бесплатной
            if prompt_price <= 0.0000001 and completion_price <= 0.0000001:
                free_models.append(model)
            else:
                paid_models.append(model)
        except (ValueError, TypeError):
            # Если не удалось распарсить цены, считаем модель платной
            paid_models.append(model)
    
    return free_models, paid_models


def get_model_pricing_info(model_id: str) -> Optional[Dict]:
    """
    Получает информацию о ценах для конкретной модели.
    
    Args:
        model_id (str): ID модели
        
    Returns:
        Optional[Dict]: Информация о ценах или None, если модель не найдена
    """
    models_data = get_openrouter_models()
    
    for model in models_data.get("data", []):
        if model.get("id") == model_id:
            return model.get("pricing", {})
    
    return None


def format_pricing_info(pricing: Dict) -> str:
    """
    Форматирует информацию о ценах для отображения.
    
    Args:
        pricing (Dict): Информация о ценах
        
    Returns:
        str: Отформатированная строка с информацией о ценах
    """
    if not pricing:
        return "Информация о ценах недоступна"
    
    try:
        prompt_price = float(pricing.get("prompt", "0"))
        completion_price = float(pricing.get("completion", "0"))
        
        if prompt_price <= 0.0000001 and completion_price <= 0.0000001:
            return "Бесплатная модель"
        else:
            # Конвертируем в более читаемый формат (за 1000 токенов)
            prompt_price_per_1k = prompt_price * 1000
            completion_price_per_1k = completion_price * 1000
            
            return f"Цены: {prompt_price_per_1k:.6f}$ за 1000 входных токенов, {completion_price_per_1k:.6f}$ за 1000 выходных токенов"
    except (ValueError, TypeError):
        return "Информация о ценах недоступна"


def get_recommended_free_models() -> List[str]:
    """
    Возвращает список рекомендуемых бесплатных моделей.
    
    Returns:
        List[str]: Список ID рекомендуемых бесплатных моделей
    """
    # Список известных бесплатных моделей
    known_free_models = [
        "mistralai/mistral-7b-instruct",
        "nousresearch/nous-capybara-7b",
        "openchat/openchat-7b",
        "undi95/toppy-m-7b",
        "lynn/soliloquy-l3",
        "pygmalionai/mythalion-13b",
        "microsoft/wizardlm-2-7b",
        "neversleep/noromaid-20b"
    ]
    
    return known_free_models


def get_recommended_paid_models() -> List[str]:
    """
    Возвращает список рекомендуемых платных моделей.
    
    Returns:
        List[str]: Список ID рекомендуемых платных моделей
    """
    # Список известных мощных платных моделей
    known_paid_models = [
        "openai/gpt-4o",
        "openai/gpt-4-turbo",
        "anthropic/claude-3-5-sonnet",
        "anthropic/claude-3-opus",
        "google/gemini-pro",
        "meta-llama/llama-3-70b-instruct"
    ]
    
    return known_paid_models


def get_model_tooltip_text(model_id: str) -> str:
    """
    Генерирует текст всплывающей подсказки для модели.
    
    Args:
        model_id (str): ID модели
        
    Returns:
        str: Текст подсказки
    """
    models_data = get_openrouter_models()
    
    # Ищем модель в данных
    model_info = None
    for model in models_data.get("data", []):
        if model.get("id") == model_id:
            model_info = model
            break
    
    if not model_info:
        return f"Модель: {model_id}\nИнформация недоступна"
    
    # Получаем базовую информацию
    name = model_info.get("name", model_id)
    description = model_info.get("description", "Описание недоступно")
    
    # Ограничиваем длину описания
    if len(description) > 200:
        description = description[:200] + "..."
    
    # Получаем информацию о ценах
    pricing = model_info.get("pricing", {})
    pricing_info = format_pricing_info(pricing)
    
    # Получаем информацию о провайдере
    provider = model_info.get("top_provider", {})
    context_length = provider.get("context_length", "Неизвестно")
    
    # Формируем текст подсказки
    tooltip_text = f"Модель: {name}\n\n"
    tooltip_text += f"Описание: {description}\n\n"
    tooltip_text += f"Цены: {pricing_info}\n"
    tooltip_text += f"Контекст: до {context_length} токенов"
    
    return tooltip_text


# Пример использования
if __name__ == "__main__":
    # Получаем список моделей
    models = get_openrouter_models()
    
    # Разделяем на бесплатные и платные
    free_models, paid_models = categorize_models(models)
    
    print(f"Найдено бесплатных моделей: {len(free_models)}")
    print(f"Найдено платных моделей: {len(paid_models)}")
    
    # Показываем несколько примеров
    print("\nПримеры бесплатных моделей:")
    for model in free_models[:3]:
        print(f"- {model.get('name', model.get('id', 'Неизвестная модель'))}")
    
    print("\nПримеры платных моделей:")
    for model in paid_models[:3]:
        print(f"- {model.get('name', model.get('id', 'Неизвестная модель'))}")
        pricing = model.get("pricing", {})
        print(f"  {format_pricing_info(pricing)}")