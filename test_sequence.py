#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the updated logical sequence.
"""

from src.core.shrinkage_system import ShrinkageSystem
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from src.core.improved_json_parser import parse_from_json
import os

def test_logical_sequence():
    """Test the updated logical sequence."""
    print("Testing updated logical sequence...")
    
    # Step 1: Convert Excel to JSON
    print("Step 1: Converting Excel to JSON...")
    preserver = ExcelHierarchyPreserver('исходные_данные/sample_data.xlsx')
    preserver.to_json('результаты/sample_data.json')
    print("Excel to JSON conversion completed.")
    
    # Step 2: Parse JSON
    print("Step 2: Parsing JSON...")
    dataset = parse_from_json('результаты/sample_data.json')
    print(f"JSON parsing completed. Dataset has {len(dataset)} rows.")
    
    # Step 3: Process dataset
    print("Step 3: Processing dataset...")
    system = ShrinkageSystem()
    results = system.process_dataset(dataset, 'sample_data.xlsx')
    print(f"Processing completed with status: {results['status']}")
    print(f"Total positions: {results['summary']['total_positions']}")
    print(f"Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
    print(f"Error count: {results['summary']['error_count']}")
    
    # Step 4: Check generated reports
    print("Step 4: Checking generated reports...")
    reports = results.get('reports', {})
    advanced_reports = results.get('advanced_reports', {})
    
    print("Generated reports:")
    for report_type, report_path in reports.items():
        if report_path and os.path.exists(report_path):
            print(f"  - {report_type}: {report_path}")
        else:
            print(f"  - {report_type}: Not generated")
    
    print("Generated advanced reports:")
    for report_type, report_path in advanced_reports.items():
        if report_path and os.path.exists(report_path):
            print(f"  - {report_type}: {report_path}")
        else:
            print(f"  - {report_type}: Not generated")
    
    print("Logical sequence test completed successfully!")

if __name__ == "__main__":
    test_logical_sequence()