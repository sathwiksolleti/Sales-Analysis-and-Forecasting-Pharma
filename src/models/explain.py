from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import joblib
from src.models.lgbm import LightGBMForecaster

def get_feature_importance(model, feature_names: List[str]) -> pd.DataFrame:
    """Extract feature importance from LightGBM model."""
    if not hasattr(model, 'model') or not hasattr(model.model, 'feature_importances_'):
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance_df

def explain_predictions_with_shap(model, X: pd.DataFrame, feature_names: List[str]) -> Optional[Dict]:
    """Generate SHAP explanations for LightGBM predictions."""
    try:
        import shap
    except ImportError:
        print("SHAP not installed. Install with: pip install shap")
        return None
    
    if not hasattr(model, 'model'):
        return None
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model.model)
    shap_values = explainer.shap_values(X[feature_names])
    
    return {
        'shap_values': shap_values,
        'feature_names': feature_names,
        'expected_value': explainer.expected_value
    }

def save_model_explanations(model, feature_names: List[str], X: pd.DataFrame, output_dir: Path, sku_id: str):
    """Save feature importance and SHAP explanations for a model."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Feature importance
    importance_df = get_feature_importance(model, feature_names)
    if not importance_df.empty:
        importance_path = output_dir / f"feature_importance_{sku_id.replace('/', '_')}.csv"
        importance_df.to_csv(importance_path, index=False)
        print(f"Saved feature importance: {importance_path}")
    
    # SHAP explanations
    shap_explanations = explain_predictions_with_shap(model, X, feature_names)
    if shap_explanations:
        shap_path = output_dir / f"shap_values_{sku_id.replace('/', '_')}.npy"
        np.save(shap_path, shap_explanations['shap_values'])
        
        # Save metadata
        metadata = {
            'feature_names': shap_explanations['feature_names'],
            'expected_value': shap_explanations['expected_value'],
            'n_samples': len(X)
        }
        import json
        with open(output_dir / f"shap_metadata_{sku_id.replace('/', '_')}.json", 'w') as f:
            json.dump(metadata, f)
        
        print(f"Saved SHAP explanations: {shap_path}")

def create_explanation_summary(models_dir: Path, output_dir: Path):
    """Create a summary of all model explanations."""
    importance_files = list(models_dir.glob("feature_importance_*.csv"))
    
    if not importance_files:
        return
    
    all_importance = []
    for file in importance_files:
        df = pd.read_csv(file)
        sku_id = file.stem.replace("feature_importance_", "").replace("_", "/")
        df['sku_id'] = sku_id
        all_importance.append(df)
    
    if all_importance:
        combined_importance = pd.concat(all_importance, ignore_index=True)
        
        # Top features across all SKUs
        top_features = combined_importance.groupby('feature')['importance'].mean().sort_values(ascending=False)
        
        summary = {
            'top_features': top_features.head(10).to_dict(),
            'total_models': len(importance_files),
            'avg_features_per_model': combined_importance.groupby('sku_id').size().mean()
        }
        
        # Save summary
        summary_path = output_dir / "explanation_summary.json"
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Saved explanation summary: {summary_path}")
