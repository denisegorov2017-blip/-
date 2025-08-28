#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the shrinkage system with the extracted real data.
"""

import sys
import os
import pandas as pd
import json

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.shrinkage_system import ShrinkageSystem

def test_shrinkage_with_real_data():
    """Test the shrinkage system with real data."""
    print("🧪 Testing shrinkage system with real data")
    print("=" * 50)
    
    # Load the extracted data
    data_file = 'результаты/extracted_shrinkage_data_refined.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return False
    
    print(f"📄 Loading data from: {data_file}")
    
    # Load the data
    try:
        dataframe = pd.read_csv(data_file)
        print(f"✅ Loaded {len(dataframe)} rows of data")
        print("Column names:", list(dataframe.columns))
        print("\nFirst 5 rows:")
        print(dataframe.head())
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Test the shrinkage system
    print("\n⚙️  Initializing ShrinkageSystem...")
    try:
        system = ShrinkageSystem()
        print("✅ ShrinkageSystem initialized")
    except Exception as e:
        print(f"❌ Error initializing ShrinkageSystem: {e}")
        return False
    
    # Process the dataset
    print("\n📊 Processing dataset...")
    try:
        results = system.process_dataset(dataframe, "extracted_shrinkage_data_refined.csv", use_adaptive=True)
        if results['status'] == 'success':
            print(f"✅ Processing completed successfully")
            print(f"   Processed {len(results['coefficients'])} products")
            if 'summary' in results and 'avg_accuracy' in results['summary']:
                print(f"   Average accuracy: {results['summary']['avg_accuracy']:.2f}%")
            
            # Save results
            results_file = 'результаты/shrinkage_results_real_data.json'
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Results saved to: {results_file}")
            
            # Show some sample coefficients
            print("\n📈 Sample coefficients:")
            for i, coeff in enumerate(results['coefficients'][:5]):
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
    success = test_shrinkage_with_real_data()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")