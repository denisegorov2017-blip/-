#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the structure of the Excel file and identify data patterns.
"""

import pandas as pd
import numpy as np

def analyze_excel_structure():
    """Analyze the structure of the Excel file."""
    file_path = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    print("Reading Excel file...")
    # Read the Excel file without assuming headers
    df = pd.read_excel(file_path, header=None)
    
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Column names: {list(df.columns)}")
    
    # Look for rows that might contain headers or data
    print("\nAnalyzing rows for potential data structure...")
    
    # Check first 50 rows for patterns
    for i in range(min(50, len(df))):
        row = df.iloc[i]
        # Convert row to string for searching
        row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
        
        # Look for key terms
        if ('Номенклатура' in row_str or 
            'остаток' in row_str.lower() or 
            'приход' in row_str.lower() or 
            'расход' in row_str.lower() or
            'Количество' in row_str):
            print(f"Row {i:2d}: {row_str}")
            
    # Look for rows with numeric data that might represent inventory values
    print("\nLooking for rows with numeric data...")
    numeric_rows = []
    
    for i in range(min(100, len(df))):  # Check first 100 rows
        row = df.iloc[i]
        # Count numeric values in the row
        numeric_count = 0
        for cell in row:
            if pd.notna(cell):
                try:
                    float(cell)
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass
        
        # If row has multiple numeric values, it might be data
        if numeric_count >= 2:
            row_values = [cell if pd.notna(cell) else '' for cell in row]
            numeric_rows.append((i, row_values, numeric_count))
    
    # Show top rows with most numeric values
    print(f"\nTop rows with numeric data (showing up to 10):")
    for i, (row_idx, row_values, count) in enumerate(sorted(numeric_rows, key=lambda x: x[2], reverse=True)[:10]):
        print(f"Row {row_idx:3d} ({count} numeric values): {row_values}")

if __name__ == "__main__":
    analyze_excel_structure()