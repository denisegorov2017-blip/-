#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract shrinkage data from the Excel file, filtering for actual products.
"""

import pandas as pd
import numpy as np
import re

def extract_shrinkage_data():
    """Extract shrinkage data from the Excel file, filtering for actual products."""
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
    data_rows = []
    
    for i in range(11, min(200, len(df))):  # Check first 200 data rows
        row = df.iloc[i]
        
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Extract values
        nomenclature = row[nomenclature_col] if nomenclature_col is not None and nomenclature_col < len(row) else None
        
        # Skip rows without nomenclature
        if pd.isna(nomenclature) or str(nomenclature).strip() == '':
            continue
            
        # Filter out document rows (they typically contain "отчет", "накладная", "инвентаризация", dates, etc.)
        nomenclature_str = str(nomenclature).lower()
        if any(keyword in nomenclature_str for keyword in ['отчет', 'накладная', 'инвентаризация', 'приходная', 'документ']):
            continue
            
        # Filter out rows that look like dates
        if re.match(r'\d{2}\.\d{2}\.\d{4}', nomenclature_str):
            continue
            
        # Filter out rows that look like timestamps
        if re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}:\d{2}', nomenclature_str):
            continue
        
        initial_balance = row[initial_balance_col] if initial_balance_col is not None and initial_balance_col < len(row) else None
        incoming = row[incoming_col] if incoming_col is not None and incoming_col < len(row) else None
        outgoing = row[outgoing_col] if outgoing_col is not None and outgoing_col < len(row) else None
        final_balance = row[final_balance_col] if final_balance_col is not None and final_balance_col < len(row) else None
        
        # Try to convert numeric values
        try:
            initial_balance = float(initial_balance) if not pd.isna(initial_balance) else 0
            incoming = float(incoming) if not pd.isna(incoming) else 0
            outgoing = float(outgoing) if not pd.isna(outgoing) else 0
            final_balance = float(final_balance) if not pd.isna(final_balance) else 0
            
            # Only include rows with valid data
            if any([initial_balance, incoming, outgoing, final_balance]):
                data_rows.append({
                    'Номенклатура': str(nomenclature),
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance
                })
        except (ValueError, TypeError):
            # Skip rows with invalid data
            continue
    
    print(f"\nExtracted {len(data_rows)} product data rows:")
    for i, row in enumerate(data_rows[:15]):  # Show first 15 rows
        print(f"Row {i+1}: {row}")
    
    return data_rows

def create_dataframe_for_shrinkage_system(data_rows):
    """Create a DataFrame in the format expected by the shrinkage system."""
    if not data_rows:
        print("No data rows extracted!")
        return pd.DataFrame()
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Add storage days (assuming 7 days based on the previous analysis)
    df['Период_хранения_дней'] = 7
    
    print(f"\nCreated DataFrame with {len(df)} rows")
    print("Column names:", list(df.columns))
    print("\nFirst 10 rows:")
    print(df.head(10))
    
    return df

if __name__ == "__main__":
    data_rows = extract_shrinkage_data()
    df = create_dataframe_for_shrinkage_system(data_rows)
    
    if not df.empty:
        # Save to CSV for testing
        df.to_csv('результаты/extracted_shrinkage_data_refined.csv', index=False, encoding='utf-8')
        print(f"\nData saved to результаты/extracted_shrinkage_data_refined.csv")
        
        # Also save to Excel
        df.to_excel('результаты/extracted_shrinkage_data_refined.xlsx', index=False)
        print(f"Data also saved to результаты/extracted_shrinkage_data_refined.xlsx")