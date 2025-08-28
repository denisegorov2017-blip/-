#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all GUI functionality
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from src.core.specialized_fish_data_processor import FishBatchDataProcessor
        from src.core.test_data_manager import TestDataManager
        from src.tkinter_gui import ShrinkageCalculatorGUI
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_fish_batch_processor():
    """Test that the fish batch processor can be instantiated"""
    try:
        from src.core.specialized_fish_data_processor import FishBatchDataProcessor
        processor = FishBatchDataProcessor()
        print("✅ FishBatchDataProcessor instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ FishBatchDataProcessor error: {e}")
        return False

def test_test_data_manager():
    """Test that the test data manager can be instantiated"""
    try:
        from src.core.test_data_manager import TestDataManager
        manager = TestDataManager()
        print("✅ TestDataManager instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ TestDataManager error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing GUI functionality...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_fish_batch_processor,
        test_test_data_manager
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Результаты: {passed}/{len(tests)} тестов пройдено")
    
    if passed == len(tests):
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("❌ Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())