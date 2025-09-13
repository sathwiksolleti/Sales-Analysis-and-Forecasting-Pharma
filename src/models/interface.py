from __future__ import annotations
from typing import Protocol, Optional
import pandas as pd

class Forecaster(Protocol):
    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> "Forecaster": ...
    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> pd.Series: ...
