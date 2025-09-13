from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.data.ingest import load_sales, validate_sales
from src.features.build_features import prepare_features
from src.models.ets import ETSForecaster
from src.models.sarimax import SarimaxForecaster
from src.utils.config import settings

OUT_DIR = Path("data/outputs")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sales = validate_sales(load_sales(sample=False))
    feats = prepare_features(sales)

    forecasts = []
    horizon = settings.horizon

    for (sku, region), g in feats.groupby(["sku_id","region_id"], sort=False):
        g = g.sort_values("date")
        y = g["units"]
        exog_cols = [c for c in g.columns if c not in ["date","units","sku_id","region_id"]]
        X = g[exog_cols]

        # naive future exog: repeat last known calendar fields
        last = g.iloc[-1:].copy()
        future = []
        for i in range(1, horizon + 1):
            row = last.copy()
            row["date"] = row["date"] + pd.to_timedelta(i, unit="W")
            row["weekofyear"] = int(((last["weekofyear"].values[0] + i - 1) % 52) + 1)
            row["month"] = int(((last["month"].values[0] + (i // 4)) - 1) % 12 + 1)
            row["quarter"] = (row["month"] - 1) // 3 + 1
            row["promo_flag"] = 0
            row["discount"] = 0.0
            future.append(row)
        Xf = pd.concat(future, ignore_index=True)
        Xf = Xf.reindex(columns=exog_cols, fill_value=0)

        try:
            model = SarimaxForecaster().fit(y, X)
            mean, lower, upper = model.predict_with_intervals(horizon, Xf, alpha=0.05)
        except Exception:
            model = ETSForecaster(seasonal="add", seasonal_periods=52).fit(y)
            mean, lower, upper = model.predict_with_intervals(horizon, alpha=0.05)

        df_pred = pd.DataFrame({
            "date": pd.date_range(g["date"].iloc[-1] + pd.Timedelta(weeks=1), periods=horizon, freq="W-SUN"),
            "sku_id": sku,
            "region_id": region,
            "forecast": mean.values,
            "pi_low": lower.values,
            "pi_high": upper.values
        })
        forecasts.append(df_pred)

    out = pd.concat(forecasts, ignore_index=True)
    out.to_csv(OUT_DIR / "forecast.csv", index=False)
    print("Saved:", OUT_DIR / "forecast.csv")

if __name__ == "__main__":
    main()
