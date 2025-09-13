#!/usr/bin/env python3
"""
Training wrapper script that handles imports correctly
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Check if required packages are available
try:
    import pandas as pd
    import numpy as np
    import plotly
    import sklearn
    import lightgbm
    import statsmodels
    print("✅ All required packages are available")
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("This script requires: pandas, numpy, plotly, scikit-learn, lightgbm, statsmodels")
    print("Please ensure requirements.txt is properly installed")
    sys.exit(1)

# Now import and run the training
if __name__ == "__main__":
    try:
        print("Starting training pipeline...")
        
        # Import the modules
        from src.data.ingest import load_sales, validate_sales
        from src.features.build_features import prepare_features
        from src.models.ets import ETSForecaster
        from src.models.sarimax import SarimaxForecaster
        from src.models.lgbm import LightGBMForecaster
        from src.utils.config import settings
        from src.evaluate.backtest import rolling_backtest
        from src.evaluate.select import select_best_model
        import pandas as pd
        from pathlib import Path
        
        print("All imports successful!")
        
        # Load and validate data
        print("Loading sales data...")
        df = load_sales(sample=False)  # Use uploaded data, not sample data
        df = validate_sales(df)
        print(f"Loaded {len(df)} records")
        
        # Prepare features
        print("Preparing features...")
        df_features = prepare_features(df)
        print(f"Features prepared: {df_features.shape}")
        
        # Get unique SKUs
        skus = df_features['sku_id'].unique()
        print(f"Found {len(skus)} unique SKUs")
        
        # Get numeric feature columns for LightGBM
        numeric_cols = df_features.select_dtypes(include=['number']).columns
        feature_cols = [c for c in numeric_cols if c not in ['units', 'sku_id', 'region_id']]
        
        # Initialize models
        models = {
            'ETS': ETSForecaster(),
            'SARIMAX': SarimaxForecaster(),
            'LightGBM': LightGBMForecaster(feature_cols=feature_cols)
        }
        
        # Run backtesting for each SKU
        results = []
        for i, sku in enumerate(skus):
            print(f"Processing SKU {i+1}/{len(skus)}: {sku}")
            
            sku_data = df_features[df_features['sku_id'] == sku].copy()
            sku_data = sku_data.sort_values('date')
            
            if len(sku_data) < 30:  # Skip SKUs with insufficient data
                print(f"Skipping {sku}: insufficient data ({len(sku_data)} records)")
                continue
            
            # Run backtesting
            sku_results = rolling_backtest(
                data=sku_data,
                models=models,
                n_splits=3,
                test_size=0.2
            )
            
            # Select best model
            best_model_name = select_best_model(sku_results)
            sku_results['best_model'] = best_model_name
            sku_results['sku_id'] = sku
            
            results.append(sku_results)
            print(f"Completed {sku}: best model = {best_model_name}")
        
        # Save results
        if results:
            results_df = pd.concat(results, ignore_index=True)
            
            # Create outputs directory
            output_dir = Path("data/outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save metrics
            metrics_file = output_dir / "metrics.csv"
            results_df.to_csv(metrics_file, index=False)
            print(f"Saved metrics to {metrics_file}")
            
            # Create model leaderboard
            leaderboard = results_df.groupby('model').agg({
                'wmape': 'mean',
                'smape': 'mean',
                'mase': 'mean',
                'bias': 'mean'
            }).round(4)
            leaderboard = leaderboard.sort_values('wmape')
            
            leaderboard_file = output_dir / "model_leaderboard.csv"
            leaderboard.to_csv(leaderboard_file)
            print(f"Saved leaderboard to {leaderboard_file}")
            
            # Create best models per SKU
            best_models = results_df[results_df['model'] == results_df['best_model']].copy()
            best_models_file = output_dir / "best_models_per_sku.csv"
            best_models.to_csv(best_models_file, index=False)
            print(f"Saved best models to {best_models_file}")
            
            print("Training completed successfully!")
        else:
            print("No results generated - check your data")
            
    except Exception as e:
        print(f"Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
