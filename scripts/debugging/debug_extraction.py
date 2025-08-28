#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed debug script to understand the data extraction issues
"""

import sys
import os
import json

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def debug_extraction():
    """Detailed debug of the data extraction process"""
    try:
        print("Detailed debugging of data extraction...")
        print("=" * 50)
        
        # Import the improved parser functions
        from src.core.improved_json_parser import _is_nomenclature_row, _extract_balance_data
        
        # Use existing JSON file
        json_path = os.path.join("результаты", "b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.json")
        
        if not os.path.exists(json_path):
            print(f"ERROR: JSON file not found at {json_path}")
            return False
            
        print(f"Reading JSON file: {json_path}")
        
        # Load the JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the sheet data
        sheet_data = data["sheets"]["Лист_1"]
        print(f"Sheet has {len(sheet_data)} rows")
        
        # Find the header row
        header_row_idx = -1
        for i, row in enumerate(sheet_data):
            if len(row) >= 9 and row[4] is not None and "Начальный остаток" in str(row[4]):
                header_row_idx = i
                print(f"Header row found at index {i}")
                break
        
        if header_row_idx == -1:
            print("ERROR: Could not find header row")
            return False
        
        # Column indices
        initial_col = 4   # "Количество Начальный остаток"
        incoming_col = 6  # "Количество Приход"
        outgoing_col = 7  # "Количество Расход"
        final_col = 8     # "Количество Конечный остаток"
        
        # Find some nomenclature rows and examine their data
        print("\nExamining nomenclature rows and their data:")
        nomenclature_count = 0
        for i in range(header_row_idx + 2, min(len(sheet_data), header_row_idx + 100)):
            row = sheet_data[i]
            if _is_nomenclature_row(row, sheet_data, i):
                nomenclature_count += 1
                nomenclature_name = row[0] if row[0] is not None else "Unknown"
                print(f"\nNomenclature row {i}: '{nomenclature_name}'")
                
                # Show the row data
                print(f"  Row data: {row}")
                
                # Extract balance data
                initial_balance, incoming, outgoing, final_balance = _extract_balance_data(
                    sheet_data, i, i, initial_col, incoming_col, outgoing_col, final_col)
                
                print(f"  Extracted data:")
                print(f"    Initial balance: {initial_balance}")
                print(f"    Incoming: {incoming}")
                print(f"    Outgoing: {outgoing}")
                print(f"    Final balance: {final_balance}")
                
                # Check for NaN values
                import math
                if math.isnan(incoming):
                    print(f"    WARNING: Incoming is NaN")
                if math.isnan(outgoing):
                    print(f"    WARNING: Outgoing is NaN")
                
                if nomenclature_count >= 10:  # Limit output
                    break
        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running detailed extraction debug...")
    print("=" * 60)
    
    debug_extraction()