#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the real data structure from the Excel file.
"""

import pandas as pd
import numpy as np

def analyze_real_data():
    """Analyze the real data structure from the Excel file."""
    file_path = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    print("Reading Excel file...")
    # Read the Excel file without assuming headers
    df = pd.read_excel(file_path, header=None)
    
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Based on the analysis, row 8 seems to contain the column headers
    # Let's identify the column positions
    header_row = df.iloc[8]
    print(f"Header row (row 8): {list(header_row)}")
    
    # Find column indices
    nomenclature_col = None
    initial_balance_col = None
    incoming_col = None
    outgoing_col = None
    final_balance_col = None
    
    # Look for column headers in row 8
    for i, cell in enumerate(header_row):
        if pd.isna(cell):
            continue
        cell_str = str(cell).lower()
        if 'номенклатура' in cell_str:
            nomenclature_col = i
        elif 'начальный остаток' in cell_str:
            initial_balance_col = i
        elif 'приход' in cell_str:
            incoming_col = i
        elif 'расход' in cell_str:
            outgoing_col = i
        elif 'конечный остаток' in cell_str:
            final_balance_col = i
    
    print(f"Column indices - Nomenclature: {nomenclature_col}, Initial: {initial_balance_col}, Incoming: {incoming_col}, Outgoing: {outgoing_col}, Final: {final_balance_col}")
    
    # Now let's extract the actual data rows
    # Data seems to start from row 11 onwards
    print("\nSample data rows (11-25):")
    for i in range(11, min(26, len(df))):
        row = df.iloc[i]
        print(f"{i:2d}: {list(row)}")
    
    # Let's also check what the actual column values are for a few rows
    print("\nExtracting structured data for first 5 product rows:")
    product_count = 0
    for i in range(11, min(100, len(df))):  # Check first 100 rows
        if product_count >= 5:
            break
            
        row = df.iloc[i]
        
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Extract values
        nomenclature = row[nomenclature_col] if nomenclature_col is not None and nomenclature_col < len(row) else None
        
        # Skip rows without nomenclature
        if pd.isna(nomenclature) or str(nomenclature).strip() == '':
            continue
            
        # Skip document rows (they typically contain "отчет", "накладная", "инвентаризация", dates, etc.)
        nomenclature_str = str(nomenclature).lower()
        if any(keyword in nomenclature_str for keyword in ['отчет', 'накладная', 'инвентаризация', 'приходная', 'документ']):
            continue
            
        # Skip rows that look like dates
        if len(nomenclature_str) > 8 and nomenclature_str[2] == '.' and nomenclature_str[5] == '.':
            continue
        
        initial_balance = row[initial_balance_col] if initial_balance_col is not None and initial_balance_col < len(row) else None
        incoming = row[incoming_col] if incoming_col is not None and incoming_col < len(row) else None
        outgoing = row[outgoing_col] if outgoing_col is not None and outgoing_col < len(row) else None
        final_balance = row[final_balance_col] if final_balance_col is not None and final_balance_col < len(row) else None
        
        print(f"Row {i}: Номенклатура='{nomenclature}', Начальный остаток={initial_balance}, Приход={incoming}, Расход={outgoing}, Конечный остаток={final_balance}")
        product_count += 1

if __name__ == "__main__":
    analyze_real_data()