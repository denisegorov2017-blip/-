#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that negative coefficients are prevented
"""

import sys
import os
import numpy as np

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_negative_coefficient_prevention():
    """Test that negative coefficients are prevented in both calculators"""
    try:
        print("Testing negative coefficient prevention...")
        print("=" * 50)
        
        # Test Adaptive Shrinkage Model
        print("Testing Adaptive Shrinkage Model...")
        from src.core.adaptive_shrinkage_calculator import AdaptiveShrinkageModel
        
        # Create model
        model = AdaptiveShrinkageModel()
        
        # Test data that might produce negative coefficients
        test_data = {
            'initial_balance': 100.0,
            'final_balance': 95.0,
            'incoming': 10.0,
            'outgoing': 5.0,
            'storage_days': 7
        }
        
        # Calculate coefficients
        coefficients = model._calculate_new_coefficients(test_data)
        
        print(f"Adaptive model coefficients: a={coefficients['a']}, b={coefficients['b']}, c={coefficients['c']}")
        
        # Check that all coefficients are non-negative
        assert coefficients['a'] >= 0, f"Negative 'a' coefficient: {coefficients['a']}"
        assert coefficients['b'] >= 0, f"Negative 'b' coefficient: {coefficients['b']}"
        assert coefficients['c'] >= 0, f"Negative 'c' coefficient: {coefficients['c']}"
        
        print("✅ Adaptive Shrinkage Model: All coefficients are non-negative")
        
        # Test Basic Shrinkage Calculator
        print("\nTesting Basic Shrinkage Calculator...")
        from src.core.shrinkage_calculator import ShrinkageCalculator
        
        # Create calculator
        calculator = ShrinkageCalculator()
        
        # Test data
        test_data_basic = {
            'name': 'TEST PRODUCT',
            'initial_balance': 100.0,
            'incoming': 10.0,
            'outgoing': 5.0,
            'final_balance': 95.0,
            'storage_days': 7,
            'documents': []
        }
        
        # Calculate coefficients
        result = calculator.calculate_coefficients(test_data_basic)
        
        print(f"Basic calculator coefficients: a={result['a']}, b={result['b']}, c={result['c']}")
        
        # Check that all coefficients are non-negative
        assert result['a'] >= 0, f"Negative 'a' coefficient: {result['a']}"
        assert result['b'] >= 0, f"Negative 'b' coefficient: {result['b']}"
        assert result['c'] >= 0, f"Negative 'c' coefficient: {result['c']}"
        
        print("✅ Basic Shrinkage Calculator: All coefficients are non-negative")
        
        # Test polynomial model specifically
        print("\nTesting polynomial model...")
        poly_result = calculator.calculate_coefficients(test_data_basic, 'polynomial')
        print(f"Polynomial model coefficients: a={poly_result['a']}, b={poly_result['b']}, c={poly_result['c']}")
        
        # Check that all coefficients are non-negative
        assert poly_result['a'] >= 0, f"Negative 'a' coefficient in polynomial model: {poly_result['a']}"
        assert poly_result['b'] >= 0, f"Negative 'b' coefficient in polynomial model: {poly_result['b']}"
        assert poly_result['c'] >= 0, f"Negative 'c' coefficient in polynomial model: {poly_result['c']}"
        
        print("✅ Polynomial Model: All coefficients are non-negative")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running negative coefficient prevention test...")
    print("=" * 60)
    
    success = test_negative_coefficient_prevention()
    
    print("=" * 60)
    if success:
        print("All tests PASSED! Negative coefficients are properly prevented.")
        sys.exit(0)
    else:
        print("Tests FAILED! There are issues with coefficient validation.")
        sys.exit(1)