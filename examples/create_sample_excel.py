#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create a sample Excel file for testing the shrinkage calculation system
"""

import pandas as pd
import os

def create_sample_excel():
    """Create a sample Excel file with test data"""
    
    # Create sample data
    data = [
        # Header rows
        ["Номенклатура", "Характеристика", "Ед. изм.", "", "Остаток на 01.01.2023", "", "Поступило", "Реализовано", "Остаток на 31.01.2023", "", ""],
        ["", "", "", "Кол-во", "Сумма", "Кол-во", "Сумма", "Кол-во", "Сумма", "Кол-во", "Сумма"],
        
        # Product 1 - Вяленая рыба
        ["ВЯЛЕНАЯ РЫБА МОРЕСКОЙ КОРОЛЬ КАВКАЗСКИЙ", "", "кг", "", "", "", "", "", "", "", ""],
        ["", "", "кг", 1000, 50000, 200, 10000, 800, 40000, 400, 20000],
        ["", "", "", "", "", "", "", "", "", "", ""],
        
        # Product 2 - Копченая рыба (Г/К)
        ["РЫБА ГОРЯЧЕГО КОПЧЕНИЯ ТУШКА", "", "кг", "", "", "", "", "", "", "", ""],
        ["", "", "кг", 500, 25000, 150, 7500, 400, 20000, 250, 12500],
        ["", "", "", "", "", "", "", "", "", "", ""],
        
        # Product 3 - Холодное копчение
        ["РЫБА ХОЛОДНОГО КОПЧЕНИЯ ФИЛЕ", "", "кг", "", "", "", "", "", "", "", ""],
        ["", "", "кг", 800, 40000, 100, 5000, 600, 30000, 300, 15000],
        ["", "", "", "", "", "", "", "", "", "", ""],
        
        # Product 4 - Слабосоленая
        ["РЫБА СЛАБОСОЛЕННАЯ СТЕЙК", "", "кг", "", "", "", "", "", "", "", ""],
        ["", "", "кг", 600, 30000, 120, 6000, 500, 25000, 220, 11000],
        ["", "", "", "", "", "", "", "", "", "", ""],
        
        # Summary row
        ["ИТОГО", "", "", 2900, 145000, 570, 28500, 2300, 115000, 1170, 58500],
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_dir = "исходные_данные"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "sample_data.xlsx")
    df.to_excel(file_path, index=False, header=False)
    
    print(f"Sample Excel file created: {file_path}")
    return file_path

if __name__ == "__main__":
    create_sample_excel()