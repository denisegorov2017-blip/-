#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки функции проверки наличия инвентаризаций.
"""

import pytest
import pandas as pd
import sys
import os

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem


def test_inventory_check_with_complete_data():
    """Тест проверки инвентаризаций с полными данными."""
    # Создаем тестовые данные с полными инвентаризациями
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': 10.0,
        'Приход': 5.0,
        'Расход': 3.0,
        'Конечный_остаток': 12.0,
        'Период_хранения_дней': 7
    }])
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Обрабатываем данные (не ожидаем ошибок)
    results = system.process_dataset(
        dataset=test_data,
        source_filename="тестовый_файл.xlsx",
        use_adaptive=True
    )
    
    # Проверяем, что обработка прошла успешно
    assert results['status'] == 'success'


def test_inventory_check_function_exists():
    """Тест наличия функции проверки инвентаризаций."""
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Проверяем, что метод существует
    assert hasattr(system, '_check_inventory_availability')
    
    # Создаем тестовые данные
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': 10.0,
        'Приход': 5.0,
        'Расход': 3.0,
        'Конечный_остаток': 12.0,
        'Период_хранения_дней': 7
    }])
    
    # Проверяем, что метод можно вызвать без ошибок
    try:
        result_data = system._check_inventory_availability(test_data, "тестовый_файл.xlsx")
        assert isinstance(result_data, pd.DataFrame)
    except Exception as e:
        assert False, f"Метод _check_inventory_availability вызвал исключение: {e}"


def test_inventory_check_with_missing_initial_balance():
    """Тест проверки инвентаризаций с отсутствующим начальным остатком."""
    # Создаем тестовые данные с отсутствующим начальным остатком
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': None,  # Отсутствует
        'Приход': 5.0,
        'Расход': 3.0,
        'Конечный_остаток': 12.0,
        'Период_хранения_дней': 7
    }])
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Проверяем, что метод проверки инвентаризации может обрабатывать отсутствующие значения
    try:
        result_data = system._check_inventory_availability(test_data, "тестовый_файл.xlsx")
        assert isinstance(result_data, pd.DataFrame)
        # Проверяем, что отсутствующий начальный остаток автоматически установлен равным 0.0
        assert result_data.iloc[0]['Начальный_остаток'] == 0.0
    except Exception as e:
        assert False, f"Метод _check_inventory_availability вызвал исключение: {e}"


def test_inventory_check_with_missing_final_balance():
    """Тест проверки инвентаризаций с отсутствующим конечным остатком."""
    # Создаем тестовые данные с отсутствующим конечным остатком
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': 10.0,
        'Приход': 5.0,
        'Расход': 3.0,
        'Конечный_остаток': None,  # Отсутствует
        'Период_хранения_дней': 7
    }])
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Проверяем, что метод проверки инвентаризации может обрабатывать отсутствующие значения
    try:
        result_data = system._check_inventory_availability(test_data, "тестовый_файл.xlsx")
        assert isinstance(result_data, pd.DataFrame)
        # Проверяем, что значение осталось None
        assert pd.isna(result_data.iloc[0]['Конечный_остаток'])
    except Exception as e:
        assert False, f"Метод _check_inventory_availability вызвал исключение: {e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])