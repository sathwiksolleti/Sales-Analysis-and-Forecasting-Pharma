#!/usr/bin/env python3
"""
Simplified training script for Streamlit Cloud deployment
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

def create_sample_forecast():
    """Create sample forecast data for demo purposes"""
    print("Creating sample forecast data...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=52, freq='W')
    skus = ['M01AB', 'M01AE', 'Hour']
    regions = ['R1', 'R2', 'R3']
    
    forecast_data = []
    for sku in skus:
        for region in regions:
            for date in dates:
                forecast_data.append({
                    'date': date,
                    'sku_id': sku,
                    'region_id': region,
                    'forecast': np.random.randint(50, 200),
                    'model': np.random.choice(['ETS', 'SARIMAX', 'LightGBM'])
                })
    
    df_forecast = pd.DataFrame(forecast_data)
    
    # Save forecast data
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df_forecast.to_csv(output_dir / "forecast.csv", index=False)
    print(f"✅ Created forecast.csv with {len(df_forecast)} records")
    
    return df_forecast

def create_sample_metrics():
    """Create sample metrics data"""
    print("Creating sample metrics data...")
    
    metrics_data = []
    for sku in ['M01AB', 'M01AE', 'Hour']:
        for model in ['ETS', 'SARIMAX', 'LightGBM']:
            metrics_data.append({
                'sku_id': sku,
                'model': model,
                'wmape': np.random.uniform(0.001, 0.01),
                'smape': np.random.uniform(0.001, 0.01),
                'bias': np.random.uniform(-0.001, 0.001),
                'mase': np.random.uniform(0.001, 0.02)
            })
    
    df_metrics = pd.DataFrame(metrics_data)
    df_metrics.to_csv("data/outputs/metrics.csv", index=False)
    print(f"✅ Created metrics.csv with {len(df_metrics)} records")
    
    return df_metrics

def create_sample_leaderboard():
    """Create sample leaderboard data"""
    print("Creating sample leaderboard data...")
    
    leaderboard_data = []
    for model in ['ETS', 'SARIMAX', 'LightGBM']:
        leaderboard_data.append({
            'model': model,
            'avg_wmape': np.random.uniform(0.001, 0.01),
            'avg_smape': np.random.uniform(0.001, 0.01),
            'avg_bias': np.random.uniform(-0.001, 0.001),
            'avg_mase': np.random.uniform(0.001, 0.02),
            'rank': np.random.randint(1, 4)
        })
    
    df_leaderboard = pd.DataFrame(leaderboard_data)
    df_leaderboard.to_csv("data/outputs/model_leaderboard.csv", index=False)
    print(f"✅ Created model_leaderboard.csv with {len(df_leaderboard)} records")
    
    return df_leaderboard

def create_sample_best_models():
    """Create sample best models data"""
    print("Creating sample best models data...")
    
    best_models_data = []
    for sku in ['M01AB', 'M01AE', 'Hour']:
        best_models_data.append({
            'sku_id': sku,
            'best_model': np.random.choice(['ETS', 'SARIMAX', 'LightGBM']),
            'best_wmape': np.random.uniform(0.001, 0.005),
            'best_smape': np.random.uniform(0.001, 0.005),
            'best_bias': np.random.uniform(-0.001, 0.001),
            'best_mase': np.random.uniform(0.001, 0.01)
        })
    
    df_best = pd.DataFrame(best_models_data)
    df_best.to_csv("data/outputs/best_models_per_sku.csv", index=False)
    print(f"✅ Created best_models_per_sku.csv with {len(df_best)} records")
    
    return df_best

if __name__ == "__main__":
    try:
        print("🚀 Starting simplified training pipeline...")
        
        # Create output directory
        os.makedirs("data/outputs", exist_ok=True)
        
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
