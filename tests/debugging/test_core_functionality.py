#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify core functionality without GUI
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_core_functionality():
    """Test the core functionality without GUI"""
    try:
        print("Testing core functionality...")
        print("=" * 50)
        
        # Import core modules
        from src.core.shrinkage_system import ShrinkageSystem
        from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
        from src.core.json_parser import parse_from_json
        
        print("SUCCESS: Core modules imported successfully")
        
        # Test with sample data
        sample_file_path = os.path.join("исходные_данные", "sample_data.xlsx")
        if not os.path.exists(sample_file_path):
            print(f"ERROR: Sample file not found at {sample_file_path}")
            return False
            
        print(f"Using sample file: {sample_file_path}")
        
        # Step 1: Convert Excel to JSON
        print("Step 1: Converting Excel to JSON...")
        json_path = os.path.join("результаты", f"{Path(sample_file_path).stem}.json")
        preserver = ExcelHierarchyPreserver(sample_file_path)
        success = preserver.to_json(json_path)
        
        if not success:
            print("ERROR: Failed to convert Excel to JSON")
            return False
            
        print(f"SUCCESS: Excel converted to JSON: {json_path}")
        
        # Step 2: Parse JSON
        print("Step 2: Parsing JSON...")
        dataset = parse_from_json(json_path)
        
        if dataset.empty:
            print("ERROR: No data found in JSON file")
            return False
            
        print(f"SUCCESS: Parsed {len(dataset)} records from JSON")
        
        # Step 3: Calculate coefficients
        print("Step 3: Calculating coefficients...")
        system = ShrinkageSystem()
        results = system.process_dataset(
            dataset=dataset,
            source_filename=os.path.basename(sample_file_path),
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
    print("Running core functionality tests...")
    print("=" * 60)
    
    success = test_core_functionality()
    
    print("=" * 60)
    if success:
        print("Core functionality test PASSED!")
        print("The system is working correctly.")
        sys.exit(0)
    else:
        print("Core functionality test FAILED!")
        print("There are issues with the core system.")
        sys.exit(1)