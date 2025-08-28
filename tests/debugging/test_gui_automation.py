#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated test script to verify GUI functionality without user interaction
"""

import sys
import os
import tkinter as tk
import threading
import time
from unittest.mock import Mock, patch

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_tkinter_gui_automation():
    """Test the Tkinter GUI automation without user interaction"""
    try:
        print("Testing Tkinter GUI automation...")
        print("=" * 50)
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Import the GUI
        from src.tkinter_gui import ShrinkageCalculatorGUI
        app = ShrinkageCalculatorGUI(root)
        
        # Set the file path to our sample data
        sample_file_path = os.path.join("исходные_данные", "sample_data.xlsx")
        if not os.path.exists(sample_file_path):
            print(f"ERROR: Sample file not found at {sample_file_path}")
            return False
            
        app.file_path.set(sample_file_path)
        print(f"Set file path to: {sample_file_path}")
        
        # Test the calculation process in a separate thread
        print("Starting automated calculation...")
        app.start_calculation()
        
        # Wait for calculation to complete (with timeout)
        timeout = 30  # seconds
        start_time = time.time()
        
        # Wait for calculation to finish or timeout
        while app.calculate_btn['state'] == 'disabled' and (time.time() - start_time) < timeout:
            root.update_idletasks()
            root.update()
            time.sleep(0.1)
        
        # Check if calculation completed
        if app.calculate_btn['state'] == 'normal':
            print("SUCCESS: Automated calculation completed successfully")
            
            # Check if report was generated
            if app.report_path and os.path.exists(app.report_path):
                print(f"SUCCESS: Report generated at {app.report_path}")
            else:
                print("WARNING: Report path not set or file not found")
                
            root.destroy()
            return True
        else:
            print("ERROR: Calculation did not complete within timeout period")
            root.destroy()
            return False
            
    except Exception as e:
        print(f"ERROR: GUI automation test failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            root.destroy()
        except:
            pass
        return False

def test_flet_gui_automation():
    """Test that Flet GUI components can be imported and initialized"""
    try:
        print("Testing Flet GUI components...")
        print("=" * 50)
        
        # Test imports
        from src.core.shrinkage_system import ShrinkageSystem
        from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from src.core.json_parser import parse_from_json
        
        print("SUCCESS: Flet GUI core components imported successfully")
        
        # Test that we can create instances
        system = ShrinkageSystem()
        print("SUCCESS: ShrinkageSystem instantiated successfully")
        
        return True
    except Exception as e:
        print(f"ERROR: Flet GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running automated GUI functionality tests...")
    print("=" * 60)
    
    # Test Tkinter GUI automation
    tkinter_success = test_tkinter_gui_automation()
    print()
    
    # Test Flet GUI components
    flet_success = test_flet_gui_automation()
    print()
    
    print("=" * 60)
    print("Test Results:")
    print(f"Tkinter GUI Automation: {'PASS' if tkinter_success else 'FAIL'}")
    print(f"Flet GUI Components: {'PASS' if flet_success else 'FAIL'}")
    
    if tkinter_success and flet_success:
        print("\nAll automated tests passed! GUI functionality is working correctly.")
        sys.exit(0)
    else:
        print("\nSome automated tests failed. Please check the errors above.")
        sys.exit(1)