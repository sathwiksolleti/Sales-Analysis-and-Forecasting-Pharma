from __future__ import annotations
import pandas as pd
from pandas.tseries.frequencies import to_offset
import holidays as pyholidays
from src.utils.config import settings

def add_calendar(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df["year"] = df[date_col].dt.year
    df["weekofyear"] = df[date_col].dt.isocalendar().week.astype(int)
    df["month"] = df[date_col].dt.month
    df["quarter"] = df[date_col].dt.quarter
    country_holidays = pyholidays.country_holidays(settings.country)
    df["is_holiday"] = df[date_col].dt.date.astype("O").isin(country_holidays).astype(int)
    return df

def add_lag_roll(df: pd.DataFrame, group_cols=("sku_id","region_id"), y_col="units") -> pd.DataFrame:
    df = df.copy().sort_values(list(group_cols) + ["date"])
    if getattr(settings, "light_features", False):
        lag_list = [1,2,4]
        win_list = [4,8]
    else:
        lag_list = [1,2,4,8,12]
        win_list = [4,8,12,26]
    for lag in lag_list:
        df[f"lag_{lag}"] = df.groupby(list(group_cols))[y_col].shift(lag)
    for win in win_list:
        df[f"rollmean_{win}"] = df.groupby(list(group_cols))[y_col].shift(1).rolling(win).mean()
        df[f"rollstd_{win}"] = df.groupby(list(group_cols))[y_col].shift(1).rolling(win).std()
    df["zero_flag"] = (df[y_col] == 0).astype(int)
    return df

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    freq = to_offset(settings.frequency)
    all_idx = []
    for (sku, region), g in df.groupby(["sku_id","region_id"], sort=False):
        full = pd.DataFrame({"date": pd.date_range(g["date"].min(), g["date"].max(), freq=freq)})
        full["sku_id"] = sku
        full["region_id"] = region
        all_idx.append(full)
    idx = pd.concat(all_idx, ignore_index=True)
    df = idx.merge(df, on=["date","sku_id","region_id"], how="left").sort_values(["sku_id","region_id","date"]) 
    for col in ["price","discount","promo_flag","stockout_flag","channel_id"]:
        if col in df.columns:
            df[col] = df.groupby(["sku_id","region_id"])[col].ffill().bfill()
    df = add_calendar(df)
    df = add_lag_roll(df)
    df = df.dropna(subset=["lag_1","rollmean_4"]) 
    return df
