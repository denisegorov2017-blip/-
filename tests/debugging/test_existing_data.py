#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify core functionality with existing data
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_core_functionality_with_existing_data():
    """Test the core functionality with existing data that we know works"""
    try:
        print("Testing core functionality with existing data...")
        print("=" * 50)
        
        # Import core modules
        from src.core.shrinkage_system import ShrinkageSystem
        from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from src.core.improved_json_parser import parse_from_json
        
        print("SUCCESS: Core modules imported successfully")
        
        # Test with existing data file that we know has been processed
        existing_json_path = os.path.join("результаты", "b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.json")
        if not os.path.exists(existing_json_path):
            print(f"ERROR: Existing JSON file not found at {existing_json_path}")
            return False
            
        print(f"Using existing JSON file: {existing_json_path}")
        
        # Step 2: Parse JSON
        print("Step 2: Parsing JSON...")
        dataset = parse_from_json(existing_json_path)
        
        if dataset.empty:
            print("ERROR: No data found in JSON file")
            return False
            
        print(f"SUCCESS: Parsed {len(dataset)} records from JSON")
        
        # Step 3: Calculate coefficients
        print("Step 3: Calculating coefficients...")
        system = ShrinkageSystem()
        results = system.process_dataset(
            dataset=dataset,
            source_filename=os.path.basename(existing_json_path),
            use_adaptive=False
        )
        
        if results.get('status') != 'success':
            print(f"ERROR: Calculation failed: {results.get('message', 'Unknown error')}")
            return False
            
        print("SUCCESS: Coefficients calculated successfully")
        
        # Check if reports were generated
        coefficients_report = results.get('reports', {}).get('coefficients', '')
        errors_report = results.get('reports', {}).get('errors', '')
        
        if coefficients_report and os.path.exists(coefficients_report):
            print(f"SUCCESS: Coefficients report generated: {coefficients_report}")
        else:
            print("WARNING: Coefficients report not found")
            
        if errors_report and os.path.exists(errors_report):
            print(f"SUCCESS: Errors report generated: {errors_report}")
        else:
            print("INFO: No errors report (this is normal if there were no errors)")
            
        # Print summary
        summary = results.get('summary', {})
        print(f"Summary:")
        print(f"  - Total positions processed: {summary.get('total_positions', 0)}")
        print(f"  - Average accuracy: {summary.get('avg_accuracy', 0):.2f}%")
        print(f"  - Error count: {summary.get('error_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running core functionality tests with existing data...")
    print("=" * 60)
    
    success = test_core_functionality_with_existing_data()
    
    print("=" * 60)
    if success:
        print("Core functionality test with existing data PASSED!")
        print("The system is working correctly.")
        sys.exit(0)
    else:
        print("Core functionality test with existing data FAILED!")
        print("There are issues with the core system.")
        sys.exit(1)