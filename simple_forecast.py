#!/usr/bin/env python3
"""
Ultra-simplified forecast script for Streamlit Cloud deployment
Uses only built-in Python libraries - no external dependencies
"""
import os
import sys
import csv
import random

def create_inventory_data():
    """Create sample inventory planning data"""
    print("Creating inventory planning data...")
    
    # Create output directory
    os.makedirs("data/outputs", exist_ok=True)
    
    skus = ['M01AB', 'M01AE', 'N02BA', 'N02BE', 'N05B', 'N05C', 'R03', 'R06']
    
    with open("data/outputs/inventory_planning.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sku_id', 'annual_demand', 'safety_stock_weekly', 'reorder_point_weekly', 'service_level', 'lead_time_weeks'])
        
        for sku in skus:
            annual_demand = random.randint(1000, 10000)
            safety_stock = random.randint(50, 200)
            reorder_point = random.randint(100, 500)
            lead_time = random.randint(1, 4)
            writer.writerow([sku, annual_demand, safety_stock, reorder_point, '95%', lead_time])
    
    print("✅ Created inventory_planning.csv with sample data")

if __name__ == "__main__":
    try:
        print("🚀 Starting ultra-simplified forecast pipeline...")
        
        # Create inventory data
        create_inventory_data()
        
        print("🎉 Forecast pipeline completed successfully!")
        print("✅ Inventory planning data created")
        
    except Exception as e:
        print(f"❌ Error in forecast pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
