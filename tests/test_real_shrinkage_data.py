#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the shrinkage system with the specific real data structure.
"""

import sys
import os
import pandas as pd
import json

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.shrinkage_system import ShrinkageSystem
from src.core.data_models import NomenclatureRow

def extract_real_data():
    """Extract real data from the specific Excel file structure."""
    file_path = 'исходные_данные/Для_расчета_коэфф/b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls'
    
    print("Reading Excel file...")
    # Read the Excel file without assuming headers
    df = pd.read_excel(file_path, header=None)
    
    # Based on the analysis, row 8 contains the column headers
    nomenclature_col = 0
    initial_balance_col = 4
    incoming_col = 6
    outgoing_col = 7
    final_balance_col = 8
    
    # Extract the actual data rows
    data_rows = []
    
    for i in range(11, min(200, len(df))):  # Check first 200 rows
        row = df.iloc[i]
        
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Extract values
        nomenclature = row[nomenclature_col] if nomenclature_col is not None and nomenclature_col < len(row) else None
        
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
        
        initial_balance = row[initial_balance_col] if initial_balance_col is not None and initial_balance_col < len(row) else 0
        incoming = row[incoming_col] if incoming_col is not None and incoming_col < len(row) else 0
        outgoing = row[outgoing_col] if outgoing_col is not None and outgoing_col < len(row) else 0
        final_balance = row[final_balance_col] if final_balance_col is not None and final_balance_col < len(row) else 0
        
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
    
    return data_rows

def test_real_shrinkage_data():
    """Test the shrinkage system with real data."""
    print("🧪 Testing shrinkage system with real data structure")
    print("=" * 60)
    
    # Extract real data
    data_rows = extract_real_data()
    print(f"✅ Extracted {len(data_rows)} product rows from real data")
    
    if not data_rows:
        print("❌ No data extracted!")
        return False
    
    # Show first few rows
    print("\nFirst 5 extracted rows:")
    for i, row in enumerate(data_rows[:5]):
        print(f"  {i+1}. {row}")
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Add storage days (assuming 7 days based on the previous analysis)
    df['Период_хранения_дней'] = 7
    
    print(f"\n📊 Created DataFrame with {len(df)} rows")
    print("Column names:", list(df.columns))
    
    # Validate data with Pydantic model
    print("\n🔍 Validating data with Pydantic model...")
    valid_rows = []
    for _, row in df.iterrows():
        try:
            validated_data = NomenclatureRow.model_validate(row.to_dict())
            valid_rows.append(validated_data.model_dump(by_alias=True))
        except Exception as e:
            print(f"  ❌ Row validation failed for '{row.get('Номенклатура', 'Unknown')}': {e}")
    
    print(f"✅ Validated {len(valid_rows)} rows with Pydantic model")
    
    # Test the shrinkage system
    print("\n⚙️  Initializing ShrinkageSystem...")
    try:
        system = ShrinkageSystem()
        print("✅ ShrinkageSystem initialized")
    except Exception as e:
        print(f"❌ Error initializing ShrinkageSystem: {e}")
        return False
    
    # Process the dataset
    print("\n📊 Processing dataset with adaptive model...")
    try:
        results = system.process_dataset(df, "real_shrinkage_data.xls", use_adaptive=True)
        if results['status'] == 'success':
            print(f"✅ Processing completed successfully")
            print(f"   Processed {len(results['coefficients'])} products")
            if 'summary' in results and 'avg_accuracy' in results['summary']:
                print(f"   Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
            
            # Save results
            results_file = 'результаты/shrinkage_results_real_data_optimized.json'
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Results saved to: {results_file}")
            
            # Show some sample coefficients
            print("\n📈 Sample coefficients:")
            for i, coeff in enumerate(results['coefficients'][:10]):
                print(f"   {coeff['Номенклатура']}: a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}, accuracy={coeff['Точность']:.2f}%")
            
            return True
        else:
            print(f"❌ Processing failed: {results['message']}")
            return False
    except Exception as e:
        print(f"❌ Error processing dataset: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_shrinkage_data_without_adaptive():
    """Test the shrinkage system with real data using the basic model."""
    print("\n🧪 Testing shrinkage system with real data using basic model")
    print("=" * 60)
    
    # Extract real data
    data_rows = extract_real_data()
    print(f"✅ Extracted {len(data_rows)} product rows from real data")
    
    if not data_rows:
        print("❌ No data extracted!")
        return False
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Add storage days (assuming 7 days based on the previous analysis)
    df['Период_хранения_дней'] = 7
    
    # Test the shrinkage system
    print("\n⚙️  Initializing ShrinkageSystem...")
    try:
        system = ShrinkageSystem()
        print("✅ ShrinkageSystem initialized")
    except Exception as e:
        print(f"❌ Error initializing ShrinkageSystem: {e}")
        return False
    
    # Process the dataset with basic model
    print("\n📊 Processing dataset with basic model...")
    try:
        results = system.process_dataset(df, "real_shrinkage_data.xls", use_adaptive=False)
        if results['status'] == 'success':
            print(f"✅ Processing completed successfully")
            print(f"   Processed {len(results['coefficients'])} products")
            if 'summary' in results and 'avg_accuracy' in results['summary']:
                print(f"   Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
            
            # Save results
            results_file = 'результаты/shrinkage_results_real_data_basic.json'
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Results saved to: {results_file}")
            
            # Show some sample coefficients
            print("\n📈 Sample coefficients:")
            for i, coeff in enumerate(results['coefficients'][:10]):
                print(f"   {coeff['Номенклатура']}: a={coeff['a']:.6f}, b={coeff['b']:.6f}, c={coeff['c']:.6f}, accuracy={coeff['Точность']:.2f}%")
            
            return True
        else:
            print(f"❌ Processing failed: {results['message']}")
            return False
    except Exception as e:
        print(f"❌ Error processing dataset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with adaptive model
    success_adaptive = test_real_shrinkage_data()
    
    # Test with basic model
    success_basic = test_real_shrinkage_data_without_adaptive()
    
    if success_adaptive and success_basic:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")