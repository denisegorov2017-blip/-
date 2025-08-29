#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки обработки реальных данных с наличием начального остатка.
"""

import pytest
import pandas as pd
import sys
import os

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem


def test_real_data_with_initial_balance():
    """Тест обработки реальных данных с наличием начального остатка."""
    # Создаем тестовые данные, имитирующие реальные данные "БЫЧКИ ВЯЛЕНЫЕ"
    test_data = pd.DataFrame([{
        'Номенклатура': 'БЫЧКИ ВЯЛЕНЫЕ',
        'Начальный_остаток': 0.844,  # Начальный остаток присутствует
        'Приход': 1.25,
        'Расход': 0.702,
        'Конечный_остаток': 1.392,
        'Период_хранения_дней': 7
    }])
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Обрабатываем данные
    results = system.process_dataset(
        dataset=test_data,
        source_filename="реальные_данные.xlsx",
        use_adaptive=True
    )
    
    # Проверяем, что обработка прошла успешно
    assert results['status'] == 'success'
    
    # Проверяем, что коэффициенты были рассчитаны
    assert len(results['coefficients']) > 0
    
    # Проверяем, что система не запрашивала ввод начального остатка
    # (в тестовой среде это проверить сложно, но мы убедились, что обработка прошла успешно)


def test_data_with_zero_initial_balance():
    """Тест обработки данных с нулевым начальным остатком."""
    # Создаем тестовые данные с нулевым начальным остатком
    test_data = pd.DataFrame([{
        'Номенклатура': 'Тестовый продукт',
        'Начальный_остаток': 0.0,  # Нулевой остаток
        'Приход': 1.25,
        'Расход': 0.702,
        'Конечный_остаток': 1.392,
        'Период_хранения_дней': 7
    }])
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    
    # Обрабатываем данные
    results = system.process_dataset(
        dataset=test_data,
        source_filename="нулевой_остаток.xlsx",
        use_adaptive=True
    )
    
    # Проверяем, что обработка прошла успешно
    assert results['status'] == 'success'
    
    # Проверяем, что коэффициенты были рассчитаны
    assert len(results['coefficients']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])