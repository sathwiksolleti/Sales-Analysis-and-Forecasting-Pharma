#!/usr/bin/env python3
"""
Forecasting wrapper script that handles imports correctly
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the forecasting
if __name__ == "__main__":
    try:
        print("Starting forecasting pipeline...")
        
        # Import the modules
        from src.data.ingest import load_sales, validate_sales
        from src.features.build_features import prepare_features
        from src.models.ets import ETSForecaster
        from src.models.sarimax import SarimaxForecaster
        from src.models.lgbm import LightGBMForecaster
        from src.utils.config import settings
        import pandas as pd
        import numpy as np
        from pathlib import Path
        import joblib
        
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
        
        # Load best models per SKU
        output_dir = Path("data/outputs")
        best_models_file = output_dir / "best_models_per_sku.csv"
        
        if not best_models_file.exists():
            print("No best models file found. Please run training first.")
            sys.exit(1)
        
        best_models_df = pd.read_csv(best_models_file)
        print(f"Loaded best models for {len(best_models_df)} SKUs")
        
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
        
        # Generate forecasts
        forecasts = []
        for i, sku in enumerate(skus):
            print(f"Forecasting SKU {i+1}/{len(skus)}: {sku}")
            
            sku_data = df_features[df_features['sku_id'] == sku].copy()
            sku_data = sku_data.sort_values('date')
            
            if len(sku_data) < 30:  # Skip SKUs with insufficient data
                print(f"Skipping {sku}: insufficient data ({len(sku_data)} records)")
                continue
            
            # Get best model for this SKU
            sku_best_models = best_models_df[best_models_df['sku_id'] == sku]
            if sku_best_models.empty:
                print(f"No best model found for {sku}, using ETS")
                best_model_name = 'ETS'
            else:
                best_model_name = sku_best_models.iloc[0]['model']
            
            # Train the best model
            model = models[best_model_name]
            
            # Prepare data
            y = sku_data['units']
            exog_cols = [c for c in sku_data.columns if c not in ['date', 'units', 'sku_id', 'region_id']]
            X = sku_data[exog_cols] if exog_cols else None
            
            # Filter to numeric columns for models that need it
            if best_model_name in ['SARIMAX', 'LightGBM'] and X is not None:
                numeric_cols = X.select_dtypes(include=['number']).columns
                X = X[numeric_cols] if len(numeric_cols) > 0 else None
            
            if best_model_name == 'ETS':
                model.fit(y)
                forecast = model.predict(12)
            elif best_model_name == 'SARIMAX':
                model.fit(y, X)
                forecast = model.predict(12, X)
            elif best_model_name == 'LightGBM':
                model.fit(y, X)
                forecast = model.predict(12, X)
            else:
                continue
            
            # Ensure forecast is a numpy array with correct length
            if hasattr(forecast, 'values'):
                forecast_values = forecast.values
            else:
                forecast_values = forecast
            
            # Ensure we have exactly 12 values and no negative forecasts
            if len(forecast_values) != 12:
                forecast_values = forecast_values[:12] if len(forecast_values) > 12 else np.pad(forecast_values, (0, 12 - len(forecast_values)), 'constant')
            
            # Ensure no negative forecasts (sales can't be negative)
            forecast_values = np.maximum(forecast_values, 0)
            
            # Generate weekly forecasts instead of daily
            forecast_df = pd.DataFrame({
                'sku_id': sku,
                'date': pd.date_range(start=sku_data['date'].max() + pd.Timedelta(weeks=1), periods=12, freq='W'),
                'forecast': forecast_values,
                'model': best_model_name
            })
            
            forecasts.append(forecast_df)
            print(f"Generated forecast for {sku} using {best_model_name}")
        
        # Save forecasts
        if forecasts:
            forecasts_df = pd.concat(forecasts, ignore_index=True)
            
            # Create outputs directory
            output_dir = Path("data/outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save forecasts
            forecast_file = output_dir / "forecast.csv"
            forecasts_df.to_csv(forecast_file, index=False)
            print(f"Saved forecasts to {forecast_file}")
            
            print("Forecasting completed successfully!")
        else:
            print("No forecasts generated - check your data")
            
    except Exception as e:
        print(f"Error during forecasting: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
