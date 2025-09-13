from __future__ import annotations
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from typing import Optional, Tuple

class ETSForecaster:
    def __init__(self, seasonal: Optional[str] = "add", seasonal_periods: int = 52):
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods
        self.model = None
        self.result = None

    def fit(self, y: pd.Series, X=None):
        y_clean = y.astype(float)
        use_seasonal = self.seasonal
        if len(y_clean) < 2 * self.seasonal_periods:
            use_seasonal = None
        self.model = ExponentialSmoothing(
            y_clean,
            trend="add",
            seasonal=use_seasonal,
            seasonal_periods=self.seasonal_periods if use_seasonal else None,
            initialization_method="estimated",
        )
        self.result = self.model.fit(optimized=True)
        return self

    def predict(self, horizon: int, X_future=None) -> pd.Series:
        return self.result.forecast(horizon)

    def predict_with_intervals(self, horizon: int, X_future=None, alpha: float = 0.05) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Naive intervals using residual std assuming normal errors."""
        import numpy as np
        preds = self.result.forecast(horizon)
        resid = getattr(self.result, "resid", None)
        if resid is None or len(resid) < 10:
            se = np.full(horizon, 1.0)
        else:
            se = np.std(resid, ddof=1)
        z = 1.959963984540054 if abs(1 - alpha) < 1e-6 or alpha == 0.05 else 1.959963984540054
        lower = preds - z * se
        upper = preds + z * se
        return preds, lower, upper
