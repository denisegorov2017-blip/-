#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to examine the parsed data and understand the validation issues
"""

import sys
import os
import pandas as pd

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def debug_parsed_data():
    """Debug the parsed data to understand the validation issues"""
    try:
        print("Debugging parsed data...")
        print("=" * 50)
        
        # Import the improved parser
        from src.core.improved_json_parser import parse_from_json
        
        # Use existing JSON file
        json_path = os.path.join("результаты", "b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.json")
        
        if not os.path.exists(json_path):
            print(f"ERROR: JSON file not found at {json_path}")
            return False
            
        print(f"Using JSON file: {json_path}")
        
        # Parse the data
        dataset = parse_from_json(json_path)
        
        if dataset.empty:
            print("ERROR: No data found in JSON file")
            return False
            
        print(f"SUCCESS: Parsed {len(dataset)} records from JSON")
        
        # Show some sample data
        print("\nSample data:")
        print(dataset.head(20))
        
        # Check data types
        print("\nData types:")
        print(dataset.dtypes)
        
        # Check for NaN values
        print("\nNaN value counts:")
        print(dataset.isnull().sum())
        
        # Check for specific columns
        print("\nChecking specific columns:")
        for col in ['Приход', 'Расход']:
            if col in dataset.columns:
                print(f"\n{col}:")
                print(f"  - Type: {type(dataset[col].iloc[0])}")
                print(f"  - Sample values: {dataset[col].head(10).tolist()}")
                print(f"  - NaN count: {dataset[col].isnull().sum()}")
                print(f"  - Zero count: {(dataset[col] == 0).sum()}")
        
        # Check a specific problematic row
        print("\nExamining a specific row (БЫЧКИ ВЯЛЕНЫЕ):")
        row = dataset[dataset['Номенклатура'] == 'БЫЧКИ ВЯЛЕНЫЕ']
        if not row.empty:
            print(row)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running parsed data debug...")
    print("=" * 60)
    
    debug_parsed_data()