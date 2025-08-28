#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized test for processing real shrinkage data with specific structure optimization.
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.shrinkage_system import ShrinkageSystem
from src.core.data_models import NomenclatureRow
from src.core.excel_toolkit import ExcelProcessor

def load_and_process_real_excel_data():
    """Load and process the real Excel data with optimized structure handling."""
    file_path = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    print("📂 Loading and processing real Excel data...")
    print(f"   File: {file_path}")
    
    # Use ExcelProcessor for better handling
    try:
        processor = ExcelProcessor(file_path)
        print(f"✅ Excel file loaded successfully")
        print(f"   Sheets: {processor.sheet_names}")
        print(f"   Shape: {processor.get_shape()}")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None
    
    # Get the first sheet data
    sheet_name = processor.sheet_names[0] if processor.sheet_names else None
    if not sheet_name:
        print("❌ No sheets found in Excel file")
        return None
    
    # Get the raw data
    df_raw = processor.df[sheet_name] if isinstance(processor.df, dict) else processor.df
    
    # Identify column positions based on header row (row 8)
    if len(df_raw) < 9:
        print("❌ Not enough rows in Excel file")
        return None
    
    header_row = df_raw.iloc[8]
    print(f"📋 Header row: {list(header_row)}")
    
    # Find column indices
    nomenclature_col = None
    initial_balance_col = None
    incoming_col = None
    outgoing_col = None
    final_balance_col = None
    
    # Look for column headers in row 8
    for i, cell in enumerate(header_row):
        if pd.isna(cell):
            continue
        cell_str = str(cell).lower()
        if 'номенклатура' in cell_str:
            nomenclature_col = i
        elif 'начальный остаток' in cell_str:
            initial_balance_col = i
        elif 'приход' in cell_str:
            incoming_col = i
        elif 'расход' in cell_str:
            outgoing_col = i
        elif 'конечный остаток' in cell_str:
            final_balance_col = i
    
    print(f"📊 Column indices - Nomenclature: {nomenclature_col}, Initial: {initial_balance_col}, Incoming: {incoming_col}, Outgoing: {outgoing_col}, Final: {final_balance_col}")
    
    if nomenclature_col is None or initial_balance_col is None or incoming_col is None or outgoing_col is None or final_balance_col is None:
        print("❌ Could not identify all required columns")
        return None
    
    # Extract product data rows (starting from row 11)
    data_rows = []
    
    for i in range(11, min(500, len(df_raw))):  # Process up to 500 rows
        row = df_raw.iloc[i]
        
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Extract values
        nomenclature = row[nomenclature_col] if nomenclature_col < len(row) else None
        
        # Skip rows without nomenclature
        if pd.isna(nomenclature) or str(nomenclature).strip() == '':
            continue
            
        # Skip document rows (they typically contain "отчет", "накладная", "инвентаризация", dates, etc.)
        nomenclature_str = str(nomenclature).lower()
        if any(keyword in nomenclature_str for keyword in ['отчет', 'накладная', 'инвентаризация', 'приходная', 'документ']):
            continue
            
        # Skip rows that look like dates
        if len(nomenclature_str) > 8 and nomenclature_str[2] == '.' and nomenclature_str[5] == '.':
            continue
        
        initial_balance = row[initial_balance_col] if initial_balance_col < len(row) else 0
        incoming = row[incoming_col] if incoming_col < len(row) else 0
        outgoing = row[outgoing_col] if outgoing_col < len(row) else 0
        final_balance = row[final_balance_col] if final_balance_col < len(row) else 0
        
        # Try to convert numeric values
        try:
            initial_balance = float(initial_balance) if not pd.isna(initial_balance) else 0
            incoming = float(incoming) if not pd.isna(incoming) else 0
            outgoing = float(outgoing) if not pd.isna(outgoing) else 0
            final_balance = float(final_balance) if not pd.isna(final_balance) else 0
            
            # Only include rows with valid data
            if any([initial_balance, incoming, outgoing, final_balance]):
                data_rows.append({
                    'Номенклатура': str(nomenclature),
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance
                })
        except (ValueError, TypeError):
            # Skip rows with invalid data
            continue
    
    print(f"✅ Extracted {len(data_rows)} product rows from real data")
    
    if not data_rows:
        print("❌ No valid data rows extracted")
        return None
    
    # Show first few rows
    print("\n📋 First 5 extracted rows:")
    for i, row in enumerate(data_rows[:5]):
        print(f"   {i+1}. {row['Номенклатура']}: Initial={row['Начальный_остаток']}, Incoming={row['Приход']}, Outgoing={row['Расход']}, Final={row['Конечный_остаток']}")
    
    return data_rows

def validate_data_with_pydantic(data_rows):
    """Validate the extracted data with Pydantic models."""
    print("\n🔍 Validating data with Pydantic models...")
    
    valid_rows = []
    invalid_rows = []
    
    # Add the required storage days field before validation
    for i, row in enumerate(data_rows):
        # Add the required field
        row_with_storage_days = row.copy()
        row_with_storage_days['Период_хранения_дней'] = 7  # Assuming 7 days storage period
        
        try:
            validated_data = NomenclatureRow.model_validate(row_with_storage_days)
            valid_rows.append(validated_data.model_dump(by_alias=True))
        except Exception as e:
            invalid_rows.append((i, row, str(e)))
    
    print(f"✅ Validated {len(valid_rows)} rows successfully")
    print(f"❌ Found {len(invalid_rows)} invalid rows")
    
    if invalid_rows:
        print("\n📋 Invalid rows details:")
        for idx, row, error in invalid_rows[:5]:  # Show first 5 invalid rows
            print(f"   Row {idx}: {row.get('Номенклатура', 'Unknown')} - Error: {error}")
    
    return valid_rows

def test_adaptive_model_processing(valid_rows):
    """Test processing with the adaptive model."""
    print("\n🧪 Testing adaptive model processing...")
    
    # Create DataFrame
    df = pd.DataFrame(valid_rows)
    
    # Add storage days (assuming 7 days based on the previous analysis)
    if 'Период_хранения_дней' not in df.columns:
        df['Период_хранения_дней'] = 7
    
    # Initialize system
    system = ShrinkageSystem()
    
    # Process with adaptive model
    results = system.process_dataset(df, "real_shrinkage_data.xls", use_adaptive=True)
    
    if results['status'] == 'success':
        print(f"✅ Adaptive model processing completed successfully")
        print(f"   Processed {len(results['coefficients'])} products")
        print(f"   Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
        
        # Save results
        results_file = 'результаты/shrinkage_results_adaptive_optimized.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 Results saved to: {results_file}")
        
        # Show sample coefficients
        print("\n📈 Sample coefficients (adaptive model):")
        for i, coeff in enumerate(results['coefficients'][:10]):
            print(f"   {coeff['Номенклатура']}: a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}, accuracy={coeff['Точность']:.2f}%")
        
        return True
    else:
        print(f"❌ Adaptive model processing failed: {results['message']}")
        return False

def test_basic_model_processing(valid_rows):
    """Test processing with the basic model."""
    print("\n🧪 Testing basic model processing...")
    
    # Create DataFrame
    df = pd.DataFrame(valid_rows)
    
    # Add storage days (assuming 7 days based on the previous analysis)
    if 'Период_хранения_дней' not in df.columns:
        df['Период_хранения_дней'] = 7
    
    # Initialize system
    system = ShrinkageSystem()
    
    # Process with basic model
    results = system.process_dataset(df, "real_shrinkage_data.xls", use_adaptive=False)
    
    if results['status'] == 'success':
        print(f"✅ Basic model processing completed successfully")
        print(f"   Processed {len(results['coefficients'])} products")
        print(f"   Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
        
        # Save results
        results_file = 'результаты/shrinkage_results_basic_optimized.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 Results saved to: {results_file}")
        
        # Show sample coefficients
        print("\n📈 Sample coefficients (basic model):")
        for i, coeff in enumerate(results['coefficients'][:10]):
            print(f"   {coeff['Номенклатура']}: a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}, accuracy={coeff['Точность']:.2f}%")
        
        return True
    else:
        print(f"❌ Basic model processing failed: {results['message']}")
        return False

def compare_models(adaptive_results_file, basic_results_file):
    """Compare results from both models."""
    print("\n📊 Comparing adaptive vs basic model results...")
    
    try:
        with open(adaptive_results_file, 'r', encoding='utf-8') as f:
            adaptive_results = json.load(f)
        
        with open(basic_results_file, 'r', encoding='utf-8') as f:
            basic_results = json.load(f)
        
        adaptive_coeffs = {coeff['Номенклатура']: coeff for coeff in adaptive_results['coefficients']}
        basic_coeffs = {coeff['Номенклатура']: coeff for coeff in basic_results['coefficients']}
        
        print("\n⚖️  Comparison of first 5 products:")
        for nomenclature in list(adaptive_coeffs.keys())[:5]:
            if nomenclature in basic_coeffs:
                a_adaptive = adaptive_coeffs[nomenclature]['a']
                b_adaptive = adaptive_coeffs[nomenclature]['b']
                c_adaptive = adaptive_coeffs[nomenclature]['c']
                accuracy_adaptive = adaptive_coeffs[nomenclature]['Точность']
                
                a_basic = basic_coeffs[nomenclature]['a']
                b_basic = basic_coeffs[nomenclature]['b']
                c_basic = basic_coeffs[nomenclature]['c']
                accuracy_basic = basic_coeffs[nomenclature]['Точность']
                
                print(f"   {nomenclature}:")
                print(f"     Adaptive: a={a_adaptive:.6f}, b={b_adaptive:.6f}, c={c_adaptive:.6f}, accuracy={accuracy_adaptive:.2f}%")
                print(f"     Basic:    a={a_basic:.6f}, b={b_basic:.6f}, c={c_basic:.6f}, accuracy={accuracy_basic:.2f}%")
                print(f"     Diff:     accuracy_diff={abs(accuracy_adaptive - accuracy_basic):.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Error comparing models: {e}")
        return False

def main():
    """Main function to run the optimized real data processing test."""
    print("🚀 OPTIMIZED REAL DATA PROCESSING TEST")
    print("=" * 60)
    
    # Create results directory if it doesn't exist
    Path("результаты").mkdir(exist_ok=True)
    
    # Load and process real data
    data_rows = load_and_process_real_excel_data()
    if not data_rows:
        print("❌ Failed to load and process real data")
        return False
    
    # Validate data
    valid_rows = validate_data_with_pydantic(data_rows)
    if not valid_rows:
        print("❌ No valid rows after Pydantic validation")
        return False
    
    # Test adaptive model
    adaptive_success = test_adaptive_model_processing(valid_rows)
    
    # Test basic model
    basic_success = test_basic_model_processing(valid_rows)
    
    # Compare models
    if adaptive_success and basic_success:
        compare_models(
            'результаты/shrinkage_results_adaptive_optimized.json',
            'результаты/shrinkage_results_basic_optimized.json'
        )
    
    print("\n" + "=" * 60)
    if adaptive_success and basic_success:
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("   ✅ Real data loaded and processed")
        print("   ✅ Data validated with Pydantic models")
        print("   ✅ Adaptive model processing successful")
        print("   ✅ Basic model processing successful")
        print("   ✅ Model comparison completed")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)