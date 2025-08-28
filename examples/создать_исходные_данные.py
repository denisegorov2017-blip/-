#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание правильного Excel файла с исходными данными для расчета коэффициентов усушки
"""

import sys
import os
import pandas as pd

def create_sample_data():
    """Создание примерного Excel файла с исходными данными."""
    print("📝 Создание примерного Excel файла с исходными данными")
    print("=" * 50)
    
    # Путь к папке с исходными данными
    source_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../исходные_данные/Для_расчета_коэфф'))
    
    # Создаем папку, если она не существует
    os.makedirs(source_data_dir, exist_ok=True)
    
    # Создаем примерные данные
    data = {
        'Номенклатура': [
            'ЩУКА СВЕЖАЯ',
            'СКУМБРИЯ С/С',
            'СЕЛЬДЬ Х/К',
            'ОКУНЬ Г/К',
            'ТРЕСКА КОПЧЕНАЯ',
            'СУДАК СУШЕНАЯ'
        ],
        'Начальный остаток': [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        'Приход': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Расход': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Конечный остаток': [99.85, 99.91, 99.90, 99.92, 99.90, 99.93],
        'Период хранения (дней)': [7, 7, 7, 7, 7, 7]
    }
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Путь к файлу
    file_path = os.path.join(source_data_dir, 'пример_данных_по_усушке.xlsx')
    
    # Сохраняем в Excel файл
    df.to_excel(file_path, index=False)
    
    print(f"✅ Создан файл: {file_path}")
    print(f"📊 Количество строк: {len(df)}")
    print("\n📋 Содержимое файла:")
    print(df.to_string(index=False))
    
    return file_path

if __name__ == "__main__":
    create_sample_data()