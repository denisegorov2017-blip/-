#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the improved JSON parser works with real data
"""

import sys
import os

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_improved_parser():
    """Test the improved parser with real data"""
    try:
        print("Testing improved JSON parser with real data...")
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
        print(dataset.head(10))
        
        # Check that we have the expected columns
        expected_columns = [
            'Номенклатура', 'Начальный_остаток', 'Приход', 'Расход', 
            'Конечный_остаток', 'Теоретический_остаток', 'Усушка', 
            'Коэффициент_усушки', 'Период_хранения_дней', 'Количество_документов'
        ]
        
        missing_columns = [col for col in expected_columns if col not in dataset.columns]
        if missing_columns:
            print(f"WARNING: Missing columns: {missing_columns}")
        else:
            print("SUCCESS: All expected columns present")
        
        # Check for negative values (which shouldn't exist)
        negative_balances = (dataset['Начальный_остаток'] < 0).sum()
        if negative_balances > 0:
            print(f"WARNING: Found {negative_balances} records with negative initial balance")
        else:
            print("SUCCESS: No negative initial balances found")
        
        # Check that we have some meaningful data
        non_zero_records = len(dataset[
            (dataset['Начальный_остаток'] > 0) | 
            (dataset['Приход'] > 0) | 
            (dataset['Расход'] > 0) | 
            (dataset['Конечный_остаток'] > 0)
        ])
        
        if non_zero_records > 0:
            print(f"SUCCESS: Found {non_zero_records} records with meaningful data")
        else:
            print("WARNING: No records with meaningful data found")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running improved parser test...")
    print("=" * 60)
    
    success = test_improved_parser()
    
    print("=" * 60)
    if success:
        print("Improved parser test PASSED!")
        print("The parser can successfully handle real data structures.")
        sys.exit(0)
    else:
        print("Improved parser test FAILED!")
        print("There are issues with the parser.")
        sys.exit(1)