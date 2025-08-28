#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive integration test for the Tkinter GUI
"""

import sys
import os
import tkinter as tk
import tempfile
import pandas as pd
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_tkinter_gui_integration():
    """Test the integration of Tkinter GUI with core modules"""
    try:
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Import the GUI
        from tkinter_gui import ShrinkageCalculatorGUI
        app = ShrinkageCalculatorGUI(root)
        
        # Test that all core modules can be accessed
        from core.shrinkage_system import ShrinkageSystem
        from core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from core.json_parser import parse_from_json
        
        print("SUCCESS: All core modules imported successfully")
        
        # Test that GUI variables are properly initialized
        assert app.file_path is not None
        assert app.use_adaptive is not None
        assert app.use_surplus is not None
        assert app.surplus_rate is not None
        assert app.status_text is not None
        
        print("SUCCESS: GUI variables initialized correctly")
        
        # Test that GUI methods exist
        assert hasattr(app, 'browse_file')
        assert hasattr(app, 'toggle_surplus_entry')
        assert hasattr(app, 'start_calculation')
        assert hasattr(app, 'run_calculation')
        assert hasattr(app, 'open_report')
        assert hasattr(app, 'open_results_folder')
        assert hasattr(app, 'update_status')
        
        print("SUCCESS: All required GUI methods exist")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"ERROR: Integration test failed: {e}")
        return False

def test_sample_data_processing():
    """Test processing of sample data through the system"""
    try:
        # Create sample data
        data = [
            ["Номенклатура", "Характеристика", "Ед. изм.", "", "Остаток на 01.01.2023", "", "Поступило", "Реализовано", "Остаток на 31.01.2023", "", ""],
            ["", "", "", "Кол-во", "Сумма", "Кол-во", "Сумма", "Кол-во", "Сумма", "Кол-во", "Сумма"],
            ["ВЯЛЕНАЯ РЫБА МОРЕСКОЙ КОРОЛЬ КАВКАЗСКИЙ", "", "кг", "", "", "", "", "", "", "", ""],
            ["", "", "кг", 1000, 50000, 200, 10000, 800, 40000, 400, 20000],
            ["ИТОГО", "", "", 1000, 50000, 200, 10000, 800, 40000, 400, 20000],
        ]
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            df = pd.DataFrame(data)
            df.to_excel(tmp_file.name, index=False, header=False)
            excel_path = tmp_file.name
        
        try:
            # Test ExcelHierarchyPreserver
            from core.excel_hierarchy_preserver import ExcelHierarchyPreserver
            preserver = ExcelHierarchyPreserver(excel_path)
            
            # Test JSON conversion
            json_path = excel_path.replace('.xlsx', '.json')
            success = preserver.to_json(json_path)
            assert success, "Failed to convert Excel to JSON"
            assert os.path.exists(json_path), "JSON file was not created"
            
            print("SUCCESS: Excel to JSON conversion works correctly")
            
            # Clean up JSON file
            if os.path.exists(json_path):
                os.remove(json_path)
        finally:
            # Clean up Excel file
            if os.path.exists(excel_path):
                os.remove(excel_path)
                
        return True
    except Exception as e:
        print(f"ERROR: Sample data processing test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Tkinter GUI integration...")
    print("=" * 50)
    
    tests = [
        test_tkinter_gui_integration,
        test_sample_data_processing
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("All integration tests passed! Tkinter GUI is properly integrated.")
    else:
        print("Some integration tests failed. Please check the errors above.")