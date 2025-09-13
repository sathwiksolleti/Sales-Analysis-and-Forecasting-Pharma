from __future__ import annotations
import numpy as np

def wmape(y_true, y_pred) -> float:
    import numpy as np
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    denom = np.sum(np.abs(y_true)) + 1e-8
    return float(np.sum(np.abs(y_true - y_pred)) / denom)

def smape(y_true, y_pred) -> float:
    import numpy as np
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    denom = (np.abs(y_true) + np.abs(y_pred)) + 1e-8
    return float(np.mean(2.0 * np.abs(y_true - y_pred) / denom))

def bias(y_true, y_pred) -> float:
    import numpy as np
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_pred - y_true))

def mase(y_true, y_pred, seasonal_period: int = 52) -> float:
    import numpy as np
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) <= seasonal_period + 1:
        return float("nan")
    diffs = np.abs(y_true[seasonal_period:] - y_true[:-seasonal_period])
    scale = np.mean(diffs) + 1e-8
    return float(np.mean(np.abs(y_true - y_pred)) / scale)
