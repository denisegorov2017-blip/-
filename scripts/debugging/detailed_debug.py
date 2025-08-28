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

def detailed_debug():
    """Detailed debug of the data extraction process"""
    try:
        print("Detailed debugging of data extraction...")
        print("=" * 50)
        
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
                print(f"Header row: {row}")
                break
        
        if header_row_idx == -1:
            print("ERROR: Could not find header row")
            return False
        
        # Show some rows around the header
        print("\nRows around header:")
        for i in range(max(0, header_row_idx - 2), min(len(sheet_data), header_row_idx + 10)):
            print(f"Row {i}: {sheet_data[i]}")
        
        # Find some nomenclature rows
        print("\nLooking for nomenclature rows:")
        nomenclature_rows = []
        for i in range(header_row_idx + 2, min(len(sheet_data), header_row_idx + 50)):
            row = sheet_data[i]
            if row and row[0] and not str(row[0]).startswith(("Отчет", "Приходная", "2025")):
                # Check if it looks like a product name
                if len(str(row[0])) > 5 and not any(keyword in str(row[0]).lower() for keyword in ["документ", "партия", "отбор"]):
                    nomenclature_rows.append((i, row))
                    print(f"Nomenclature row {i}: {row}")
                    if len(nomenclature_rows) >= 5:
                        break
        
        # Show data for one nomenclature item and its following rows
        if nomenclature_rows:
            nom_idx, nom_row = nomenclature_rows[0]
            print(f"\nDetailed data for '{nom_row[0]}' (row {nom_idx}):")
            print(f"Initial balance (col 4): {nom_row[4] if len(nom_row) > 4 else 'N/A'}")
            print(f"Incoming (col 6): {nom_row[6] if len(nom_row) > 6 else 'N/A'}")
            print(f"Outgoing (col 7): {nom_row[7] if len(nom_row) > 7 else 'N/A'}")
            print(f"Final balance (col 8): {nom_row[8] if len(nom_row) > 8 else 'N/A'}")
            
            # Show following rows
            print(f"\nFollowing rows:")
            for i in range(nom_idx + 1, min(len(sheet_data), nom_idx + 10)):
                row = sheet_data[i]
                print(f"Row {i}: {row}")
                if row and row[0] and not str(row[0]).startswith(("Отчет", "Приходная", "2025")):
                    # Check if it looks like a product name
                    if len(str(row[0])) > 5 and not any(keyword in str(row[0]).lower() for keyword in ["документ", "партия", "отбор"]):
                        print("  ^ Next nomenclature row")
                        break
        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running detailed debug...")
    print("=" * 60)
    
    detailed_debug()