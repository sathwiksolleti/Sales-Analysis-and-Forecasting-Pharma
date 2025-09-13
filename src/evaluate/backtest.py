from __future__ import annotations
import pandas as pd
from typing import Callable, Any
from src.evaluate.metrics import wmape, smape, bias, mase

def rolling_backtest(
    data: pd.DataFrame,
    models: dict,
    n_splits: int = 3,
    test_size: float = 0.2
) -> pd.DataFrame:
    """Simplified rolling backtest for the training script."""
    results = []
    
    # Simple train/test split
    split_idx = int(len(data) * (1 - test_size))
    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]
    
    if len(test_data) < 10:  # Need at least 10 test points
        return pd.DataFrame()
    
    y_train = train_data['units']
    y_test = test_data['units']
    
    # Get exogenous variables if any
    exog_cols = [c for c in data.columns if c not in ['date', 'units', 'sku_id', 'region_id']]
    X_train = train_data[exog_cols] if exog_cols else None
    X_test = test_data[exog_cols] if exog_cols else None
    
    # Test each model
    for model_name, model in models.items():
        try:
            # Train model
            if model_name == 'ETS':
                model.fit(y_train)
                forecast = model.predict(len(test_data))
            elif model_name == 'SARIMAX':
                # Filter out non-numeric columns for SARIMAX
                numeric_cols = X_train.select_dtypes(include=['number']).columns if X_train is not None else []
                X_train_numeric = X_train[numeric_cols] if len(numeric_cols) > 0 else None
                X_test_numeric = X_test[numeric_cols] if len(numeric_cols) > 0 else None
                model.fit(y_train, X_train_numeric)
                forecast = model.predict(len(test_data), X_test_numeric)
            elif model_name == 'LightGBM':
                # Filter out non-numeric columns for LightGBM
                numeric_cols = X_train.select_dtypes(include=['number']).columns if X_train is not None else []
                X_train_numeric = X_train[numeric_cols] if len(numeric_cols) > 0 else None
                X_test_numeric = X_test[numeric_cols] if len(numeric_cols) > 0 else None
                model.fit(y_train, X_train_numeric)
                forecast = model.predict(len(test_data), X_test_numeric)
            else:
                continue
            
            # Calculate metrics
            results.append({
                'model': model_name,
                'wmape': wmape(y_test.values, forecast),
                'smape': smape(y_test.values, forecast),
                'bias': bias(y_test.values, forecast),
                'mase': mase(y_test.values, forecast, seasonal_period=52)
            })
            
        except Exception as e:
            print(f"Error with {model_name}: {str(e)}")
            continue
    
    return pd.DataFrame(results)

def rolling_backtest_original(
    frame: pd.DataFrame,
    group_cols: list[str],
    date_col: str,
    target_col: str,
    horizon: int,
    fit_fn: Callable[[pd.Series, pd.DataFrame | None], Any],
    pred_fn: Callable[[Any, int, pd.DataFrame | None], pd.Series],
    exog_cols: list[str] | None = None,
    folds: int = 4,
) -> pd.DataFrame:
    results = []
    for keys, g in frame.groupby(group_cols, sort=False):
        g = g.sort_values(date_col)
        n = len(g)
        if n <= horizon * (folds + 1):
            continue
        fold_size = max(horizon, (n // (folds + 1)))
        for f in range(folds):
            split = n - (folds - f) * fold_size
            train = g.iloc[:split]
            test = g.iloc[split:split + horizon]
            if len(test) < horizon:
                continue
            y = train[target_col].astype(float)
            X = None
            Xf = None
            if exog_cols:
                # keep only numeric columns and fill missing values
                X = train[exog_cols].select_dtypes(include=["number"]).fillna(0.0)
                Xf = test[exog_cols].select_dtypes(include=["number"]).fillna(0.0)
            model = fit_fn(y, X)
            preds = pred_fn(model, horizon, Xf)
            y_true = test[target_col].astype(float).values
            results.append({
                **({group_cols[0]: keys} if not isinstance(keys, tuple) else {c: v for c, v in zip(group_cols, keys)}),
                "fold": f,
                "wmape": wmape(y_true, preds),
                "smape": smape(y_true, preds),
                "bias": bias(y_true, preds),
                "mase": mase(y_true, preds, seasonal_period=52),
            })
    return pd.DataFrame(results)
