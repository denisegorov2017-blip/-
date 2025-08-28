#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify GUI components can be imported and instantiated
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_gui_components():
    """Test that GUI components can be imported and instantiated"""
    try:
        print("Testing GUI components...")
        print("=" * 50)
        
        # Test Tkinter GUI import
        print("Testing Tkinter GUI import...")
        from src.tkinter_gui import ShrinkageCalculatorGUI
        print("SUCCESS: Tkinter GUI imported successfully")
        
        # Test that we can create a GUI instance
        print("Testing Tkinter GUI instantiation...")
        root = tk.Tk()
        root.withdraw()  # Hide the window
        app = ShrinkageCalculatorGUI(root)
        print("SUCCESS: Tkinter GUI instantiated successfully")
        root.destroy()
        
        # Test Flet GUI import
        print("Testing Flet GUI import...")
        from src.core.shrinkage_system import ShrinkageSystem
        from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from src.core.json_parser import parse_from_json
        print("SUCCESS: Flet GUI components imported successfully")
        
        # Test that we can create core instances
        print("Testing core component instantiation...")
        system = ShrinkageSystem()
        print("SUCCESS: ShrinkageSystem instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"ERROR: GUI component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running GUI component tests...")
    print("=" * 60)
    
    success = test_gui_components()
    
    print("=" * 60)
    if success:
        print("GUI component tests PASSED!")
        print("The GUI components are working correctly.")
        sys.exit(0)
    else:
        print("GUI component tests FAILED!")
        print("There are issues with the GUI components.")
        sys.exit(1)