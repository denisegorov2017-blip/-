#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to examine more of the JSON data
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def debug_json_data_further():
    """Debug the JSON data further to understand the structure"""
    try:
        print("Debugging JSON data further...")
        print("=" * 50)
        
        # Use existing data file
        json_path = os.path.join("результаты", "b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.json")
        if not os.path.exists(json_path):
            print(f"ERROR: JSON file not found at {json_path}")
            return False
            
        print(f"Reading JSON file: {json_path}")
        
        # Load the JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "sheets" in data:
            sheet_names = list(data["sheets"].keys())
            if sheet_names:
                first_sheet = sheet_names[0]
                sheet_data = data["sheets"][first_sheet]
                print(f"First sheet has {len(sheet_data)} rows")
                
                # Look for rows with actual data
                print("Looking for rows with data:")
                data_rows = []
                for i, row in enumerate(sheet_data):
                    # Skip empty rows
                    if not row or all(cell is None or (isinstance(cell, str) and cell.strip() == "") for cell in row):
                        continue
                    
                    # Check if this looks like a data row
                    non_empty_cells = [cell for cell in row if cell is not None and str(cell).strip() != ""]
                    if len(non_empty_cells) >= 3:  # At least 3 non-empty cells
                        data_rows.append((i, row))
                        if len(data_rows) <= 20:  # Show first 20 data rows
                            print(f"    Row {i}: {row}")
                        elif len(data_rows) == 21:
                            print("    ... (more rows found)")
                
                print(f"\nFound {len(data_rows)} rows with significant data")
                
                # Look for specific patterns in the data
                print("\nLooking for specific patterns:")
                for i, row in data_rows[:50]:  # Check first 50 data rows
                    first_cell = str(row[0]) if len(row) > 0 and row[0] is not None else ""
                    if "ВЯЛЕН" in first_cell or "КОПЧЕН" in first_cell or "СЛАБОСОЛ" in first_cell:
                        print(f"    Found potential nomenclature at row {i}: {first_cell}")
                        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running JSON data debug...")
    print("=" * 60)
    
    debug_json_data_further()