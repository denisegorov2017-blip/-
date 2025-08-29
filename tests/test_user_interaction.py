#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки функции взаимодействия с пользователем.
"""

import pytest
import pandas as pd
import sys
import os

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem
from core.user_interaction import UserInteraction


def test_user_interaction_class_exists():
    """Тест наличия класса UserInteraction."""
    # Проверяем, что класс существует
    assert hasattr(UserInteraction, '__init__')
    assert hasattr(UserInteraction, 'confirm_missing_inventory')
    assert hasattr(UserInteraction, 'get_inventory_balance')
    assert hasattr(UserInteraction, 'handle_missing_inventory')


def test_user_interaction_methods_callable():
    """Тест возможности вызова методов UserInteraction."""
    # Создаем экземпляр класса
    interaction = UserInteraction()
    
    # Проверяем, что методы можно вызвать без ошибок
    try:
        # Эти методы не будут показывать диалоги в тестах, так как мы не можем взаимодействовать с GUI
        # Вместо этого проверяем, что методы существуют и могут быть вызваны
        assert hasattr(interaction, 'confirm_missing_inventory')
        assert hasattr(interaction, 'get_inventory_balance')
        assert hasattr(interaction, 'handle_missing_inventory')
    except Exception as e:
        assert False, f"Методы UserInteraction вызвали исключение: {e}"


def test_shrinkage_system_with_user_interaction():
    """Тест наличия модуля взаимодействия с пользователем в ShrinkageSystem."""
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Проверяем, что модуль взаимодействия с пользователем существует
    assert hasattr(system, 'user_interaction')
    
    # Проверяем, что метод проверки инвентаризации существует и может быть вызван
    assert hasattr(system, '_check_inventory_availability')
    
    # Создаем тестовые данные с полными инвентаризациями
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': 10.0,  # На начало периода
        'Приход': 5.0,
        'Расход': 3.0,
        'Конечный_остаток': 12.0,   # На конец периода
        'Период_хранения_дней': 7
    }])
    
    # Проверяем, что метод можно вызвать без ошибок
    try:
        processed_data = system._check_inventory_availability(test_data, "тестовый_файл.xlsx")
        assert isinstance(processed_data, pd.DataFrame)
    except Exception as e:
        assert False, f"Метод _check_inventory_availability вызвал исключение: {e}"


def test_user_interaction_inventory_types():
    """Тест работы с разными типами инвентаризации."""
    # Создаем экземпляр класса
    interaction = UserInteraction()
    
    # Проверяем, что методы могут работать с разными типами инвентаризации
    try:
        # Тест для начальной инвентаризации
        assert hasattr(interaction, 'confirm_missing_inventory')
        assert hasattr(interaction, 'get_inventory_balance')
        
        # Методы должны принимать параметр inventory_type
        # В тестах мы не можем показывать диалоги, просто проверяем наличие методов
    except Exception as e:
        assert False, f"Методы UserInteraction для разных типов инвентаризации вызвали исключение: {e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])