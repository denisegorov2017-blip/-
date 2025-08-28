#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for the launch script with Tkinter GUI option
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_launch_script_import():
    """Test that the launch script can be imported without errors"""
    try:
        # This will execute the launch script and test if it imports correctly
        import launch
        print("SUCCESS: Launch script imported successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import launch script: {e}")
        return False

def test_launch_functions_exist():
    """Test that required functions exist in the launch script"""
    try:
        import launch
        
        # Check that all required functions exist
        assert hasattr(launch, 'launch_flet_gui')
        assert hasattr(launch, 'launch_tkinter_gui')
        assert hasattr(launch, 'launch_streamlit_dashboard')
        assert hasattr(launch, 'show_menu')
        assert hasattr(launch, 'main')
        
        print("SUCCESS: All required functions exist in launch script")
        return True
    except Exception as e:
        print(f"ERROR: Required functions missing in launch script: {e}")
        return False

def test_menu_options():
    """Test that the menu includes the Tkinter GUI option"""
    try:
        import launch
        
        # Capture the menu output
        import io
        import contextlib
        
        # Redirect stdout to capture print statements
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            launch.show_menu()
        
        menu_output = captured_output.getvalue()
        
        # Check that menu contains Tkinter option
        assert "Графический интерфейс (Tkinter)" in menu_output
        assert "2. 🖼️" in menu_output  # Check the numbering
        
        print("SUCCESS: Menu includes Tkinter GUI option with correct numbering")
        return True
    except Exception as e:
        print(f"ERROR: Menu test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing launch script with Tkinter GUI option...")
    print("=" * 50)
    
    tests = [
        test_launch_script_import,
        test_launch_functions_exist,
        test_menu_options
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("All launch script tests passed! Tkinter GUI option is properly integrated.")
    else:
        print("Some launch script tests failed. Please check the errors above.")