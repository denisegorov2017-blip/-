#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to understand what the parser is finding in the JSON data
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def debug_json_parsing():
    """Debug the JSON parsing process"""
    try:
        print("Debugging JSON parsing...")
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
        
        print("JSON structure:")
        print(f"  - Keys: {list(data.keys())}")
        print(f"  - Has 'sheets': {'sheets' in data}")
        
        if "sheets" in data:
            sheet_names = list(data["sheets"].keys())
            print(f"  - Sheet names: {sheet_names}")
            
            if sheet_names:
                first_sheet = sheet_names[0]
                sheet_data = data["sheets"][first_sheet]
                print(f"  - First sheet has {len(sheet_data)} rows")
                
                # Show first few rows
                print("First 10 rows of the first sheet:")
                for i, row in enumerate(sheet_data[:10]):
                    print(f"    Row {i}: {row}")
                    
                # Check for nomenclature patterns
                structural_config = {
                    'nomenclature_patterns': [
                        'ВЯЛЕНЫЙ', 'ВЯЛЕНАЯ', 'Г/К', 'Х/К', 'КОПЧЕНЫЙ', 'КОПЧЕНАЯ',
                        'СУШЕНЫЙ', 'СУШЕНАЯ', 'ТУШКА', 'ФИЛЕ', 'СТЕЙК', 'С/С', 'СЛАБОСОЛ'
                    ],
                    'summary_keywords': ['ИТОГО', 'ВСЕГО', 'САЛЬДО', 'ОБЩИЙ ИТОГ'],
                }
                
                print("\nSearching for nomenclature patterns:")
                nomenclature_rows = []
                for i, row in enumerate(sheet_data):
                    if not row or not row[0]:
                        continue
                    # Check if the first cell contains any of the nomenclature patterns
                    first_cell = str(row[0]) if row[0] is not None else ""
                    matches = [p for p in structural_config['nomenclature_patterns'] if p in first_cell]
                    if matches:
                        # Check if it's likely a nomenclature row (e.g., second cell is empty)
                        is_nomenclature_row = False
                        if len(row) > 1:
                            second_cell = str(row[1]) if row[1] is not None else ""
                            if second_cell.strip() == "":
                                is_nomenclature_row = True
                        else:
                            is_nomenclature_row = True
                            
                        if is_nomenclature_row:
                            nomenclature_rows.append({'index': i, 'name': first_cell, 'matches': matches})
                            print(f"    Found nomenclature at row {i}: '{first_cell}' (matches: {matches})")
                
                print(f"\nFound {len(nomenclature_rows)} nomenclature rows")
                
                # Check for summary keywords
                print("\nSearching for summary keywords:")
                summary_rows = []
                for i, row in enumerate(sheet_data):
                    if not row or not row[0]:
                        continue
                    first_cell = str(row[0]) if row[0] is not None else ""
                    matches = [k for k in structural_config['summary_keywords'] if k in first_cell]
                    if matches:
                        summary_rows.append({'index': i, 'name': first_cell, 'matches': matches})
                        print(f"    Found summary at row {i}: '{first_cell}' (matches: {matches})")
                
                print(f"\nFound {len(summary_rows)} summary rows")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running JSON parsing debug...")
    print("=" * 60)
    
    debug_json_parsing()