#!/usr/bin/env python3
"""
Simplified forecast script for Streamlit Cloud deployment
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

def create_inventory_data():
    """Create sample inventory planning data"""
    print("Creating inventory planning data...")
    
    inventory_data = []
    for sku in ['M01AB', 'M01AE', 'Hour']:
        inventory_data.append({
            'sku_id': sku,
            'annual_demand': np.random.randint(1000, 10000),
            'safety_stock_weekly': np.random.randint(50, 200),
            'reorder_point_weekly': np.random.randint(100, 500),
            'service_level': '95%',
            'lead_time_weeks': np.random.randint(1, 4)
        })
    
    df_inventory = pd.DataFrame(inventory_data)
    df_inventory.to_csv("data/outputs/inventory_planning.csv", index=False)
    print(f"✅ Created inventory_planning.csv with {len(df_inventory)} records")
    
    return df_inventory

if __name__ == "__main__":
    try:
        print("🚀 Starting simplified forecast pipeline...")
        
        # Create output directory
        os.makedirs("data/outputs", exist_ok=True)
        
        # Create inventory data
        create_inventory_data()
        
        print("🎉 Forecast pipeline completed successfully!")
        print("✅ Inventory planning data created")
        
    except Exception as e:
        print(f"❌ Error in forecast pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
