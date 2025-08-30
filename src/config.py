#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Централизованный файл конфигурации для проекта "Система Расчета Усушки".

Этот файл содержит все основные настройки, управляющие поведением системы,
такие как параметры моделей, пути для сохранения результатов и пороговые значения.

Файл следует стандартам PEP 8 и использует типизацию для улучшения читаемости и поддержки.
"""

from typing import Dict, Any, Union


# Словарь с конфигурацией по умолчанию.
# Эти значения используются, если не указаны другие при запуске системы.
DEFAULT_CONFIG: Dict[str, Any] = {
    # === ОСНОВНЫЕ НАСТРОЙКИ РАСЧЕТОВ ===
    # Тип используемой модели: 'exponential', 'linear', 'polynomial'
    'model_type': 'exponential',
    
    # Период по умолчанию (в днях) для предварительных расчетов, если не указан
    'default_period': 7,
    
    # Минимальный порог точности для расчетов (в процентах)
    # Используется для фильтрации или выделения результатов
    'min_accuracy': 50.0,
    
    # Использовать ли адаптивную модель по умолчанию
    'use_adaptive_model': False,
    
    # Средний процент излишка при поступлении товара (0.0 = 0%)
    # Используется в адаптивной модели. 0.01 = 1%
    'average_surplus_rate': 0.0,
    
    # === НАСТРОЙКИ ИНТЕРФЕЙСА ===
    # Тема интерфейса: 'light', 'dark', 'system'
    'theme': 'light',
    
    # Язык интерфейса: 'ru', 'en'
    'language': 'ru',
    
    # Размеры окна по умолчанию
    'window_width': 1200,
    'window_height': 800,
    
    # === НАСТРОЙКИ ВЫВОДА И ОТЧЕТОВ ===
    # Директория для сохранения всех сгенерированных отчетов и результатов
    'output_dir': 'результаты',
    
    # Автоматически открывать отчеты после генерации
    'auto_open_reports': True,
    
    # Тема отчетов: 'default', 'dark', 'light', 'colorful'
    'report_theme': 'default',
    
    # === НАСТРОЙКИ БАЗЫ ДАННЫХ ===
    # Включена ли база данных
    'enable_database': True,
    
    # URL для подключения к базе данных
    # SQLite: 'sqlite:///shrinkage_database.db'
    # PostgreSQL: 'postgresql://user:password@localhost:5432/shrinkage_db'
    'database_url': 'sqlite:///shrinkage_database.db',
    
    # Директория для резервных копий базы данных
    'database_backup_path': 'backups/',
    
    # Интервал создания резервных копий (в часах)
    'database_backup_interval': 24,
    
    # Включена ли верификация коэффициентов
    'enable_verification': False,
    
    # === НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ ===
    # Максимальное количество потоков для параллельной обработки
    'max_threads': 4,
    
    # Размер батча для обработки данных
    'batch_size': 1000,
    
    # === НАСТРОЙКИ ЛОГИРОВАНИЯ ===
    # Уровень логирования: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    'log_level': 'INFO',
    
    # Максимальный размер файла лога (в мегабайтах)
    'log_max_size': 10,
    
    # Количество ротаций логов для хранения
    'log_backup_count': 5,
    
    # === НАСТРОЙКИ ИИ ДЛЯ РАСЧЕТОВ ===
    # Включить использование внешнего ИИ для расчетов
    'enable_external_ai_calculations': False,
    
    # API ключ для внешнего ИИ сервиса для расчетов
    'external_ai_calculations_api_key': '',
    
    # Модель ИИ для расчетов
    'external_ai_calculations_model': 'gpt-3.5-turbo',
    
    # Базовый URL для ИИ API для расчетов
    'external_ai_calculations_base_url': 'https://api.openai.com/v1',
    
    # Включить использование локального ИИ (LM Studio) для расчетов
    'enable_local_ai_calculations': False,
    
    # Модель локального ИИ для расчетов
    'local_ai_calculations_model': 'gpt-3.5-turbo',
    
    # Базовый URL для локального ИИ API для расчетов
    'local_ai_calculations_base_url': 'http://localhost:1234/v1',
    
    # Включить использование OpenRouter для расчетов
    'enable_openrouter_calculations': False,
    
    # API ключ для OpenRouter для расчетов
    'openrouter_calculations_api_key': '',
    
    # Модель OpenRouter для расчетов
    'openrouter_calculations_model': 'openai/gpt-3.5-turbo',
    
    # === НАСТРОЙКИ ИИ ДЛЯ АНАЛИЗА ПАТТЕРНОВ ===
    # Включить использование внешнего ИИ для анализа паттернов
    'enable_external_ai_patterns': False,
    
    # API ключ для внешнего ИИ сервиса для анализа паттернов
    'external_ai_patterns_api_key': '',
    
    # Модель ИИ для анализа паттернов
    'external_ai_patterns_model': 'gpt-4',
    
    # Базовый URL для ИИ API для анализа паттернов
    'external_ai_patterns_base_url': 'https://api.openai.com/v1',
    
    # Включить использование локального ИИ (LM Studio) для анализа паттернов
    'enable_local_ai_patterns': False,
    
    # Модель локального ИИ для анализа паттернов
    'local_ai_patterns_model': 'llama3',
    
    # Базовый URL для локального ИИ API для анализа паттернов
    'local_ai_patterns_base_url': 'http://localhost:1235/v1',
    
    # Включить использование OpenRouter для анализа паттернов
    'enable_openrouter_patterns': False,
    
    # API ключ для OpenRouter для анализа паттернов
    'openrouter_patterns_api_key': '',
    
    # Модель OpenRouter для анализа паттернов
    'openrouter_patterns_model': 'anthropic/claude-3-sonnet',
    
    # === УСТАРЕВШИЕ НАСТРОЙКИ ИИ (СОВМЕСТИМОСТЬ) ===
    # Включить использование внешнего ИИ
    'enable_external_ai': False,
    
    # API ключ для внешнего ИИ сервиса
    'external_ai_api_key': '',
    
    # Модель ИИ для использования
    'external_ai_model': 'gpt-3.5-turbo',
    
    # Базовый URL для ИИ API
    'external_ai_base_url': 'https://api.openai.com/v1',
    
    # Включить использование локального ИИ (LM Studio)
    'enable_local_ai': False,
    
    # Модель локального ИИ для использования
    'local_ai_model': 'gpt-3.5-turbo',
    
    # Базовый URL для локального ИИ API
    'local_ai_base_url': 'http://localhost:1234/v1',
    
    # Включить использование OpenRouter
    'enable_openrouter': False,
    
    # API ключ для OpenRouter
    'openrouter_api_key': '',
    
    # Модель OpenRouter для использования
    'openrouter_model': 'openai/gpt-3.5-turbo',
}


# Конфигурационные профили для разных сценариев использования
DEVELOPMENT_CONFIG: Dict[str, Any] = {
    **DEFAULT_CONFIG,
    'log_level': 'DEBUG',
    'enable_database': True,
    'database_url': 'sqlite:///shrinkage_database_dev.db',
}

TESTING_CONFIG: Dict[str, Any] = {
    **DEFAULT_CONFIG,
    'log_level': 'WARNING',
    'enable_database': False,
    'output_dir': 'test_results',
}

PRODUCTION_CONFIG: Dict[str, Any] = {
    **DEFAULT_CONFIG,
    'log_level': 'ERROR',
    'enable_database': True,
    'database_backup_interval': 12,
}


def get_config_profile(profile: str = 'default') -> Dict[str, Any]:
    """
    Получить конфигурационный профиль по имени.
    
    Args:
        profile (str): Имя профиля ('default', 'development', 'testing', 'production')
        
    Returns:
        Dict[str, Any]: Словарь с настройками для указанного профиля
    """
    profiles = {
        'default': DEFAULT_CONFIG,
        'development': DEVELOPMENT_CONFIG,
        'testing': TESTING_CONFIG,
        'production': PRODUCTION_CONFIG,
    }
    
    return profiles.get(profile, DEFAULT_CONFIG)


# Валидация конфигурации
CONFIG_VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    'model_type': {
        'type': str,
        'allowed_values': ['exponential', 'linear', 'polynomial'],
        'required': True
    },
    'default_period': {
        'type': int,
        'min': 1,
        'max': 365,
        'required': True
    },
    'min_accuracy': {
        'type': float,
        'min': 0.0,
        'max': 100.0,
        'required': True
    },
    'use_adaptive_model': {
        'type': bool,
        'required': True
    },
    'average_surplus_rate': {
        'type': float,
        'min': 0.0,
        'max': 1.0,
        'required': True
    },
    'theme': {
        'type': str,
        'allowed_values': ['light', 'dark', 'system'],
        'required': True
    },
    'language': {
        'type': str,
        'allowed_values': ['ru', 'en'],
        'required': True
    },
    'window_width': {
        'type': int,
        'min': 800,
        'max': 3840,
        'required': True
    },
    'window_height': {
        'type': int,
        'min': 600,
        'max': 2160,
        'required': True
    },
    'output_dir': {
        'type': str,
        'required': True
    },
    'auto_open_reports': {
        'type': bool,
        'required': True
    },
    'report_theme': {
        'type': str,
        'allowed_values': ['default', 'dark', 'light', 'colorful'],
        'required': True
    },
    'enable_database': {
        'type': bool,
        'required': True
    },
    'database_url': {
        'type': str,
        'required': True
    },
    'database_backup_path': {
        'type': str,
        'required': True
    },
    'database_backup_interval': {
        'type': int,
        'min': 1,
        'max': 168,
        'required': True
    },
    'enable_verification': {
        'type': bool,
        'required': True
    },
    'max_threads': {
        'type': int,
        'min': 1,
        'max': 32,
        'required': True
    },
    'batch_size': {
        'type': int,
        'min': 10,
        'max': 10000,
        'required': True
    },
    'log_level': {
        'type': str,
        'allowed_values': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'required': True
    },
    'log_max_size': {
        'type': int,
        'min': 1,
        'max': 100,
        'required': True
    },
    'log_backup_count': {
        'type': int,
        'min': 1,
        'max': 20,
        'required': True
    },
    'enable_external_ai_calculations': {
        'type': bool,
        'required': True
    },
    'external_ai_calculations_api_key': {
        'type': str,
        'required': False
    },
    'external_ai_calculations_model': {
        'type': str,
        'required': True
    },
    'external_ai_calculations_base_url': {
        'type': str,
        'required': True
    },
    'enable_local_ai_calculations': {
        'type': bool,
        'required': True
    },
    'local_ai_calculations_model': {
        'type': str,
        'required': True
    },
    'local_ai_calculations_base_url': {
        'type': str,
        'required': True
    },
    'enable_openrouter_calculations': {
        'type': bool,
        'required': True
    },
    'openrouter_calculations_api_key': {
        'type': str,
        'required': False
    },
    'openrouter_calculations_model': {
        'type': str,
        'required': True
    },
    'enable_external_ai_patterns': {
        'type': bool,
        'required': True
    },
    'external_ai_patterns_api_key': {
        'type': str,
        'required': False
    },
    'external_ai_patterns_model': {
        'type': str,
        'required': True
    },
    'external_ai_patterns_base_url': {
        'type': str,
        'required': True
    },
    'enable_local_ai_patterns': {
        'type': bool,
        'required': True
    },
    'local_ai_patterns_model': {
        'type': str,
        'required': True
    },
    'local_ai_patterns_base_url': {
        'type': str,
        'required': True
    },
    'enable_openrouter_patterns': {
        'type': bool,
        'required': True
    },
    'openrouter_patterns_api_key': {
        'type': str,
        'required': False
    },
    'openrouter_patterns_model': {
        'type': str,
        'required': True
    },
    # Устаревшие настройки (сохранены для совместимости)
    'enable_external_ai': {
        'type': bool,
        'required': True
    },
    'external_ai_api_key': {
        'type': str,
        'required': False
    },
    'external_ai_model': {
        'type': str,
        'required': True
    },
    'external_ai_base_url': {
        'type': str,
        'required': True
    },
    'enable_local_ai': {
        'type': bool,
        'required': True
    },
    'local_ai_model': {
        'type': str,
        'required': True
    },
    'local_ai_base_url': {
        'type': str,
        'required': True
    },
    'enable_openrouter': {
        'type': bool,
        'required': True
    },
    'openrouter_api_key': {
        'type': str,
        'required': False
    },
    'openrouter_model': {
        'type': str,
        'required': True
    },
}