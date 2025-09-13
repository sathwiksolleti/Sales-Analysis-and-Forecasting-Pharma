from __future__ import annotations
import pandas as pd
from lightgbm import LGBMRegressor
from typing import List, Optional

class LightGBMForecaster:
    def __init__(self, feature_cols: List[str]):
        self.feature_cols = feature_cols
        self.model = LGBMRegressor(
            n_estimators=400, learning_rate=0.05, max_depth=-1, subsample=0.9, colsample_bytree=0.9, random_state=42
        )

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None):
        X_local = X[self.feature_cols]
        self.model.fit(X_local, y)
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> pd.Series:
        preds = self.model.predict(X_future[self.feature_cols])
        return pd.Series(preds, index=X_future.index)
