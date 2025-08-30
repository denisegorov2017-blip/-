#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работы модуля openrouter_models.
"""

import sys
import os

# Добавляем путь к src директории
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Создаем директорию logs если её нет
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

try:
    from src.core.openrouter_models import (
        get_openrouter_models, 
        categorize_models, 
        get_model_tooltip_text
    )
    
    print("🔍 Тестирование модуля openrouter_models...")
    
    # Получаем список моделей
    print("📥 Получение списка моделей OpenRouter...")
    models = get_openrouter_models()
    
    if models and "data" in models:
        print(f"✅ Получено {len(models['data'])} моделей")
        
        # Разделяем на бесплатные и платные
        free_models, paid_models = categorize_models(models)
        print(f"🆓 Бесплатных моделей: {len(free_models)}")
        print(f"💰 Платных моделей: {len(paid_models)}")
        
        # Проверяем подсказку для модели
        if models["data"]:
            first_model_id = models["data"][0]["id"]
            print(f"ℹ️  Получение подсказки для модели: {first_model_id}")
            tooltip = get_model_tooltip_text(first_model_id)
            print(f"📝 Подсказка: {tooltip[:100]}...")
            
        print("✅ Все тесты пройдены успешно!")
    else:
        print("❌ Не удалось получить список моделей")
        
except Exception as e:
    print(f"❌ Ошибка при тестировании: {e}")
    import traceback
    traceback.print_exc()