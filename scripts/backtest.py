from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.data.ingest import load_sales, validate_sales
from src.features.build_features import prepare_features
from src.models.ets import ETSForecaster
from src.models.sarimax import SarimaxForecaster
from src.models.lgbm import LightGBMForecaster
from src.utils.config import settings
from src.evaluate.backtest import rolling_backtest
from src.evaluate.select import select_best_model_per_sku, create_model_leaderboard, save_best_models
from src.models.explain import save_model_explanations, create_explanation_summary

OUT_DIR = Path("data/outputs")


def backtest_model(frame: pd.DataFrame, model_name: str):
    group_cols = ["sku_id","region_id"]
    # numeric exogenous only
    num_cols = frame.select_dtypes(include=["number"]).columns.tolist()
    exog_cols = [c for c in num_cols if c not in ["units"]]
    horizon = settings.quick_horizon if getattr(settings, "quick_mode", False) else settings.horizon
    folds = 2 if getattr(settings, "quick_mode", False) else 4

    if model_name == "ETS":
        def fit_fn(y, X):
            return ETSForecaster(seasonal="add", seasonal_periods=52).fit(y)
        def pred_fn(model, h, Xf):
            return model.predict(h)
        return rolling_backtest(frame, group_cols, "date", "units", horizon, fit_fn, pred_fn, None, folds=folds)

    if model_name == "SARIMAX":
        def fit_fn(y, X):
            return SarimaxForecaster().fit(y, X)
        def pred_fn(model, h, Xf):
            return model.predict(h, Xf)
        return rolling_backtest(frame, group_cols, "date", "units", horizon, fit_fn, pred_fn, exog_cols, folds=folds)

    if model_name == "LightGBM" and settings.use_lgbm:
        feat_cols = [c for c in exog_cols if c.startswith(("lag_","rollmean_","rollstd_","promo_flag","discount","is_holiday","month","weekofyear","quarter"))]
        def fit_fn(y, X):
            return LightGBMForecaster(feature_cols=feat_cols).fit(y, X)
        def pred_fn(model, h, Xf):
            return model.predict(h, Xf)
        return rolling_backtest(frame, group_cols, "date", "units", horizon, fit_fn, pred_fn, feat_cols, folds=folds)

    return pd.DataFrame()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sales = validate_sales(load_sales(sample=False))
    feats = prepare_features(sales)
    # limit number of series in quick mode
    if getattr(settings, "quick_mode", False):
        groups = feats[["sku_id","region_id"]].drop_duplicates().head(getattr(settings, "max_groups", 10))
        feats = feats.merge(groups, on=["sku_id","region_id"], how="inner")

    metrics_all = []
    model_list = ["ETS", "SARIMAX", "LightGBM"]
    if getattr(settings, "quick_mode", False):
        model_list = ["ETS"]
    for name in model_list:
        dfm = backtest_model(feats, name)
        if not dfm.empty:
            dfm["model"] = name
            metrics_all.append(dfm)

    df_metrics = pd.concat(metrics_all, ignore_index=True)
    df_metrics.to_csv(OUT_DIR / "metrics.csv", index=False)
    print("Saved:", OUT_DIR / "metrics.csv")
    
    # Model selection and leaderboard
    best_models_df = select_best_model_per_sku(df_metrics)
    if not best_models_df.empty:
        best_models_df.to_csv(OUT_DIR / "best_models_per_sku.csv", index=False)
        print("Saved:", OUT_DIR / "best_models_per_sku.csv")
        
        # Create leaderboard
        leaderboard_df = create_model_leaderboard(df_metrics)
        leaderboard_df.to_csv(OUT_DIR / "model_leaderboard.csv", index=False)
        print("Saved:", OUT_DIR / "model_leaderboard.csv")
        
        # Save trained best models
        models_dir = OUT_DIR / "trained_models"
        save_best_models(sales, best_models_df, models_dir)
        
        # Generate model explanations for LightGBM models
        explanations_dir = OUT_DIR / "explanations"
        for _, row in best_models_df.iterrows():
            if row["best_model"] == "LightGBM":
                sku_id = row["sku_id"]
                sku_data = feats[feats["sku_id"] == sku_id].copy()
                if not sku_data.empty:
                    # Load the saved model
                    model_path = models_dir / f"best_model_{sku_id.replace('/', '_')}.joblib"
                    if model_path.exists():
                        model = joblib.load(model_path)
                        feat_cols = [c for c in sku_data.columns if c.startswith(("lag_", "rollmean_", "rollstd_", "promo_flag", "discount", "is_holiday", "month", "weekofyear", "quarter"))]
                        if feat_cols:
                            X = sku_data[feat_cols].fillna(0)
                            save_model_explanations(model, feat_cols, X, explanations_dir, sku_id)
        
        # Create explanation summary
        create_explanation_summary(models_dir, explanations_dir)

if __name__ == "__main__":
    main()
