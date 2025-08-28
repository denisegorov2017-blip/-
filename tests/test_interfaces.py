#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that both interfaces can run properly
"""

import sys
import os

def test_flet_gui_import():
    """Test that the Flet GUI can be imported without errors"""
    try:
        import src.gui
        print("✅ Flet GUI imported successfully")
        
    except Exception as e:
        print(f"❌ Error importing Flet GUI: {e}")
        return False

def test_streamlit_dashboard_import():
    """Test that the Streamlit dashboard can be imported without errors"""
    try:
        import src.dashboard
        print("✅ Streamlit dashboard imported successfully")
        
    except Exception as e:
        assert False, f"Error importing Streamlit dashboard: {e}"

def test_shrinkage_system_import():
    """Test that the ShrinkageSystem can be imported without errors"""
    try:
        from src.core.shrinkage_system import ShrinkageSystem
        print("✅ ShrinkageSystem imported successfully")
        
    except Exception as e:
        print(f"❌ Error importing ShrinkageSystem: {e}")
        return False



