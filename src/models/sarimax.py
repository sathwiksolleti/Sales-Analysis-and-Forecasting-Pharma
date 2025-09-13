from __future__ import annotations
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import Optional, Tuple

class SarimaxForecaster:
    def __init__(self, order=(1,1,1), seasonal_order=(1,0,1,52)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.result = None

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None):
        self.result = SARIMAX(y, exog=X, order=self.order, seasonal_order=self.seasonal_order, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> pd.Series:
        return self.result.get_forecast(steps=horizon, exog=X_future).predicted_mean

    def predict_with_intervals(self, horizon: int, X_future: Optional[pd.DataFrame] = None, alpha: float = 0.05) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Return mean forecast and (lower, upper) confidence intervals.

        Parameters
        ----------
        horizon : int
            Number of periods to forecast.
        X_future : pd.DataFrame | None
            Future exogenous variables aligned with the forecast horizon.
        alpha : float
            Significance level for intervals (e.g., 0.05 yields 95% interval).
        """
        fc = self.result.get_forecast(steps=horizon, exog=X_future)
        mean = fc.predicted_mean
        ci = fc.conf_int(alpha=alpha)
        lower = ci.iloc[:, 0]
        upper = ci.iloc[:, 1]
        return mean, lower, upper
