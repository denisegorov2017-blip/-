#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the Tkinter GUI functionality
"""

import sys
import os
import tkinter as tk
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_tkinter_gui_import():
    """Test that the Tkinter GUI can be imported without errors"""
    try:
        from tkinter_gui import ShrinkageCalculatorGUI
        print("SUCCESS: Tkinter GUI imported successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import Tkinter GUI: {e}")
        return False

def test_gui_creation():
    """Test that the GUI can be created without errors"""
    try:
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Import and create the GUI
        from tkinter_gui import ShrinkageCalculatorGUI
        app = ShrinkageCalculatorGUI(root)
        
        print("SUCCESS: GUI created successfully")
        root.destroy()
        return True
    except Exception as e:
        print(f"ERROR: Failed to create GUI: {e}")
        return False

def test_core_modules_import():
    """Test that core modules can be imported"""
    try:
        from core.shrinkage_system import ShrinkageSystem
        from core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from core.json_parser import parse_from_json
        print("SUCCESS: Core modules imported successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import core modules: {e}")
        return False

if __name__ == "__main__":
    print("Testing Tkinter GUI functionality...")
    print("=" * 50)
    
    tests = [
        test_core_modules_import,
        test_tkinter_gui_import,
        test_gui_creation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("All tests passed! Tkinter GUI is working correctly.")
    else:
        print("Some tests failed. Please check the errors above.")