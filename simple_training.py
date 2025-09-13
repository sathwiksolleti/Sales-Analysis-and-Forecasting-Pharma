#!/usr/bin/env python3
"""
Ultra-simplified training script for Streamlit Cloud deployment
Uses only built-in Python libraries - no external dependencies
"""
import os
import sys
import csv
import random
from datetime import datetime, timedelta

def create_sample_forecast():
    """Create sample forecast data for demo purposes"""
    print("Creating sample forecast data...")
    
    # Create output directory
    os.makedirs("data/outputs", exist_ok=True)
    
    # Create sample data using only built-in libraries
    skus = ['M01AB', 'M01AE', 'Hour']
    regions = ['R1', 'R2', 'R3']
    models = ['ETS', 'SARIMAX', 'LightGBM']
    
    # Create CSV file
    with open("data/outputs/forecast.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['date', 'sku_id', 'region_id', 'forecast', 'model'])
        
        # Generate 52 weeks of data
        start_date = datetime(2024, 1, 1)
        for week in range(52):
            date = start_date + timedelta(weeks=week)
            date_str = date.strftime('%Y-%m-%d')
            
            for sku in skus:
                for region in regions:
                    forecast = random.randint(50, 200)
                    model = random.choice(models)
                    writer.writerow([date_str, sku, region, forecast, model])
    
    print("✅ Created forecast.csv with sample data")

def create_sample_metrics():
    """Create sample metrics data"""
    print("Creating sample metrics data...")
    
    skus = ['M01AB', 'M01AE', 'Hour']
    models = ['ETS', 'SARIMAX', 'LightGBM']
    
    with open("data/outputs/metrics.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sku_id', 'model', 'wmape', 'smape', 'bias', 'mase'])
        
        for sku in skus:
            for model in models:
                wmape = round(random.uniform(0.001, 0.01), 6)
                smape = round(random.uniform(0.001, 0.01), 6)
                bias = round(random.uniform(-0.001, 0.001), 6)
                mase = round(random.uniform(0.001, 0.02), 6)
                writer.writerow([sku, model, wmape, smape, bias, mase])
    
    print("✅ Created metrics.csv with sample data")

def create_sample_leaderboard():
    """Create sample leaderboard data"""
    print("Creating sample leaderboard data...")
    
    models = ['ETS', 'SARIMAX', 'LightGBM']
    
    with open("data/outputs/model_leaderboard.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['model', 'avg_wmape', 'avg_smape', 'avg_bias', 'avg_mase', 'rank'])
        
        for i, model in enumerate(models, 1):
            avg_wmape = round(random.uniform(0.001, 0.01), 6)
            avg_smape = round(random.uniform(0.001, 0.01), 6)
            avg_bias = round(random.uniform(-0.001, 0.001), 6)
            avg_mase = round(random.uniform(0.001, 0.02), 6)
            writer.writerow([model, avg_wmape, avg_smape, avg_bias, avg_mase, i])
    
    print("✅ Created model_leaderboard.csv with sample data")

def create_sample_best_models():
    """Create sample best models data"""
    print("Creating sample best models data...")
    
    skus = ['M01AB', 'M01AE', 'Hour']
    models = ['ETS', 'SARIMAX', 'LightGBM']
    
    with open("data/outputs/best_models_per_sku.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sku_id', 'best_model', 'best_wmape', 'best_smape', 'best_bias', 'best_mase'])
        
        for sku in skus:
            best_model = random.choice(models)
            best_wmape = round(random.uniform(0.001, 0.005), 6)
            best_smape = round(random.uniform(0.001, 0.005), 6)
            best_bias = round(random.uniform(-0.001, 0.001), 6)
            best_mase = round(random.uniform(0.001, 0.01), 6)
            writer.writerow([sku, best_model, best_wmape, best_smape, best_bias, best_mase])
    
    print("✅ Created best_models_per_sku.csv with sample data")

if __name__ == "__main__":
    try:
        print("🚀 Starting ultra-simplified training pipeline...")
        
        # Create sample data files
        create_sample_forecast()
        create_sample_metrics()
        create_sample_leaderboard()
        create_sample_best_models()
        
        print("🎉 Training pipeline completed successfully!")
        print("✅ All output files created in data/outputs/")
        
    except Exception as e:
        print(f"❌ Error in training pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
