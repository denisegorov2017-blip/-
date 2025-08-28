#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to debug the _is_nomenclature_row function directly
"""

import sys
import os
import json

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_is_nomenclature_row():
    """Test the _is_nomenclature_row function directly"""
    try:
        print("Testing _is_nomenclature_row function...")
        print("=" * 50)
        
        # Import the function
        from src.core.improved_json_parser import _is_nomenclature_row
        
        # Test cases
        test_cases = [
            (["БЫЧКИ ВЯЛЕНЫЕ", None, None, None, 0.844, None, 1.25, 0.702, 1.392], "БЫЧКИ ВЯЛЕНЫЕ (should be True)"),
            (["21.06.2025 9:20:00", None, None, None, 0.844, None, None, 0.396, 0.448], "21.06.2025 9:20:00 (should be False)"),
            (["Отчет отдела о розничных продажах 000000000000219 от 16.07.2025 22:10:57", None, None, None, 0.844, None, None, 0.396, 0.448], "Document name (should be False)"),
            (["Монетка рыба (Рыба Дачная )", None, None, None, 603.289, None, 354.345, 340.35, 617.284], "Монетка рыба (should be True)"),
            (["ВЯЛЕНАЯ РЫБА (весовой товар)", None, None, None, 31.95, None, 33.078, 22, 43.028], "ВЯЛЕНАЯ РЫБА (should be True)"),
        ]
        
        # Dummy sheet data for testing
        dummy_sheet_data = []
        
        for i, (row, description) in enumerate(test_cases):
            result = _is_nomenclature_row(row, dummy_sheet_data, i)
            print(f"{description}: {result}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running _is_nomenclature_row test...")
    print("=" * 60)
    
    test_is_nomenclature_row()