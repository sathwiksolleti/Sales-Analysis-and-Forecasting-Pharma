from __future__ import annotations
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Any
from src.models.ets import ETSForecaster
from src.models.sarimax import SarimaxForecaster
from src.models.lgbm import LightGBMForecaster
from src.utils.config import settings

def select_best_model(metrics_df: pd.DataFrame) -> str:
    """Select best model based on WMAPE from a single SKU's results."""
    if metrics_df.empty:
        return 'ETS'  # Default fallback
    
    # Find the model with lowest WMAPE
    best_idx = metrics_df["wmape"].idxmin()
    return metrics_df.loc[best_idx, "model"]

def select_best_model_per_sku(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Select best model for each SKU based on WMAPE."""
    if metrics_df.empty:
        return pd.DataFrame()
    
    # Group by SKU and find best model
    best_models = []
    for sku in metrics_df["sku_id"].unique():
        sku_metrics = metrics_df[metrics_df["sku_id"] == sku]
        best_idx = sku_metrics["wmape"].idxmin()
        best_model = sku_metrics.loc[best_idx]
        best_models.append({
            "sku_id": sku,
            "best_model": best_model["model"],
            "wmape": best_model["wmape"],
            "smape": best_model["smape"],
            "mase": best_model["mase"],
            "bias": best_model["bias"]
        })
    
    return pd.DataFrame(best_models)

def create_model_leaderboard(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Create overall model performance leaderboard."""
    if metrics_df.empty:
        return pd.DataFrame()
    
    leaderboard = metrics_df.groupby("model").agg({
        "wmape": ["mean", "std", "count"],
        "smape": ["mean", "std"],
        "mase": ["mean", "std"],
        "bias": ["mean", "std"]
    }).round(4)
    
    # Flatten column names
    leaderboard.columns = ['_'.join(col).strip() for col in leaderboard.columns]
    leaderboard = leaderboard.reset_index()
    
    # Add ranking
    leaderboard = leaderboard.sort_values("wmape_mean")
    leaderboard["rank"] = range(1, len(leaderboard) + 1)
    
    return leaderboard

def save_best_models(sales_data: pd.DataFrame, best_models_df: pd.DataFrame, output_dir: Path):
    """Train and save the best model for each SKU."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for _, row in best_models_df.iterrows():
        sku_id = row["sku_id"]
        model_name = row["best_model"]
        
        # Get data for this SKU
        sku_data = sales_data[sales_data["sku_id"] == sku_id].copy()
        if sku_data.empty:
            continue
            
        sku_data = sku_data.sort_values("date")
        y = sku_data["units"]
        
        # Prepare features
        exog_cols = [c for c in sku_data.columns if c not in ["date", "units", "sku_id", "region_id"]]
        X = sku_data[exog_cols] if exog_cols else None
        
        # Train the best model
        if model_name == "ETS":
            model = ETSForecaster(seasonal="add", seasonal_periods=52).fit(y)
        elif model_name == "SARIMAX":
            model = SarimaxForecaster().fit(y, X)
        elif model_name == "LightGBM":
            feat_cols = [c for c in exog_cols if c.startswith(("lag_", "rollmean_", "rollstd_", "promo_flag", "discount", "is_holiday", "month", "weekofyear", "quarter"))]
            model = LightGBMForecaster(feature_cols=feat_cols).fit(y, X)
        else:
            continue
        
        # Save model
        model_path = output_dir / f"best_model_{sku_id.replace('/', '_')}.joblib"
        joblib.dump(model, model_path)
        print(f"Saved best model for {sku_id}: {model_name} -> {model_path}")

def load_best_model(sku_id: str, models_dir: Path):
    """Load the best trained model for a specific SKU."""
    model_path = models_dir / f"best_model_{sku_id.replace('/', '_')}.joblib"
    if model_path.exists():
        return joblib.load(model_path)
    return None