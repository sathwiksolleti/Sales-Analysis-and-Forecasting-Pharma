from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from pathlib import Path

DATA_DIR = Path("data")
OUTPUTS_DIR = DATA_DIR / "outputs"
RAW_DIR = DATA_DIR / "raw"
from src.utils.config import settings

def ensure_dirs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

def generate_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = pd.date_range("2022-01-02", periods=140, freq="W-SUN")
    skus = ["SKU_A", "SKU_B", "SKU_C"]
    regions = ["North", "South"]
    rows = []
    rng_np = np.arange(len(rng))
    for sku in skus:
        for region in regions:
            base = 80 if sku == "SKU_A" else 50 if sku == "SKU_B" else 30
            seasonal = 15 * np.sin(2 * np.pi * rng_np / 52) + 10
            trend = 0.2 * rng_np
            noise = np.random.normal(0, 6, size=len(rng))
            units = np.clip(base + seasonal + trend + noise, 0, None)
            promo_weeks = set(np.random.choice(rng, size=6, replace=False))
            for dt, u in zip(rng, units):
                discount = 0.0
                lift = 1.0
                if dt in promo_weeks:
                    discount = float(np.random.choice([0.1, 0.15, 0.2]))
                    lift = 1.0 + discount * 2.5
                stockout_flag = 1 if np.random.rand() < 0.02 else 0
                sold = 0 if stockout_flag else u * lift
                rows.append({
                    "date": dt,
                    "sku_id": sku,
                    "region_id": region,
                    "channel_id": "Retail",
                    "units": float(np.round(sold, 1)),
                    "price": 10.0 if sku == "SKU_A" else 7.5 if sku == "SKU_B" else 6.0,
                    "discount": discount,
                    "promo_flag": 1 if discount > 0 else 0,
                    "stockout_flag": stockout_flag
                })
    sales = pd.DataFrame(rows)
    promo = sales.loc[sales.promo_flag == 1, ["sku_id","region_id","date","discount"]].copy()
    return sales, promo

def _read_table(fp: Path) -> pd.DataFrame:
    if fp.suffix.lower() in [".xlsx", ".xls"]:
        try:
            if fp.suffix.lower() == ".xlsx":
                return pd.read_excel(fp, engine="openpyxl")
            return pd.read_excel(fp, engine="xlrd")
        except ImportError:
            raise ImportError("Reading Excel requires 'openpyxl' for .xlsx or 'xlrd==1.2.0' for .xls.")
        except Exception:
            # Some files with .xls extension are actually CSV; try CSV fallback
            try:
                return pd.read_csv(fp)
            except Exception:
                raise
    return pd.read_csv(fp)

def _normalize_schema(df_raw: pd.DataFrame, colmap: Dict[str, str]) -> pd.DataFrame:
    # Case-insensitive and whitespace-tolerant mapping from user columns to internal names
    source_cols_lower = {c.lower().strip(): c for c in df_raw.columns}
    rename_map: Dict[str, str] = {}
    for internal, source in colmap.items():
        src_key = source.lower().strip()
        if src_key in source_cols_lower and source_cols_lower[src_key] != internal:
            rename_map[source_cols_lower[src_key]] = internal
    df = df_raw.rename(columns=rename_map).copy()
    return df

def _aggregate_to_week(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]) 
    df = df.sort_values(["sku_id","region_id","date"]) 
    df.set_index("date", inplace=True)
    agg_dict = {"units": "sum"}
    if "price" in df.columns:
        agg_dict["price"] = "mean"
    if "discount" in df.columns:
        agg_dict["discount"] = "mean"
    if "promo_flag" in df.columns:
        agg_dict["promo_flag"] = "max"
    if "stockout_flag" in df.columns:
        agg_dict["stockout_flag"] = "max"
    group_cols = ["sku_id","region_id"]
    keep_cols: List[str] = [c for c in ["channel_id"] if c in df.columns]
    resampled = (
        df.groupby(group_cols)
          .resample("W-SUN")
          .agg({**agg_dict, **{c: "last" for c in keep_cols}})
          .reset_index()
    )
    return resampled

def _auto_detect_columns(df_raw: pd.DataFrame) -> Dict[str, str]:
    cols_lower = {c.lower().strip(): c for c in df_raw.columns}
    candidates: Dict[str, List[str]] = {
        "date": ["date","datetime","timestamp","order_date","sales_date","datum"],
        "sku_id": ["sku_id","sku","product_id","product","item_id","item","material","material_id"],
        "region_id": ["region_id","region","market","zone","state","area"],
        "units": ["units","quantity","qty","sales","volume","units_sold","demand"]
    }
    detected: Dict[str, str] = {}
    for internal, opts in candidates.items():
        for opt in opts:
            key = opt.lower().strip()
            if key in cols_lower:
                detected[internal] = cols_lower[key]
                break
    return detected

def load_sales(sample: bool = True) -> pd.DataFrame:
    ensure_dirs()
    if sample or settings.use_sample:
        sales, _ = generate_sample_data()
        return sales
    path = Path(settings.csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}. Update settings.csv_path.")
    files: List[Path] = []
    if path.is_dir():
        for ext in ("*.csv","*.xlsx","*.xls"):
            files.extend(path.glob(ext))
    else:
        files = [path]
    if not files:
        raise FileNotFoundError(f"No data files found under {path} (csv/xlsx/xls).")
    base_colmap: Dict[str, str] = settings.column_map
    required_keys = ["date","sku_id","region_id","units"]
    frames: List[pd.DataFrame] = []
    for fp in files:
        df_raw = _read_table(fp)
        # Build per-file column map: auto-detected, overridden by settings.column_map when present
        auto_map = _auto_detect_columns(df_raw)
        effective_map: Dict[str, str] = {}
        for k in required_keys:
            # prefer settings mapping if the target exists in file; else use auto-detected
            if k in base_colmap and base_colmap[k]:
                val = base_colmap[k]
                if val.lower().strip() in {c.lower().strip() for c in df_raw.columns}:
                    effective_map[k] = val
                    continue
            if k in auto_map:
                effective_map[k] = auto_map[k]
        # Handle wide format: if units not identified but there are many product columns, melt
        if "units" not in effective_map and "sku_id" not in effective_map:
            lower_cols = {c.lower().strip(): c for c in df_raw.columns}
            date_col = effective_map.get("date") or auto_map.get("date")
            region_col = effective_map.get("region_id") or auto_map.get("region_id")
            known_meta = {x for x in [date_col, region_col, "year", "month", "hour", "weekday", "weekday name", "type"] if x}
            product_cols = [c for c in df_raw.columns if c not in known_meta]
            if date_col and product_cols:
                id_vars = [date_col]
                if region_col and region_col in df_raw.columns:
                    id_vars.append(region_col)
                melted = df_raw.melt(id_vars=id_vars, value_vars=product_cols, var_name="sku_id", value_name="units")
                melted = melted.rename(columns={date_col: "date"})
                if region_col and region_col in melted.columns:
                    melted = melted.rename(columns={region_col: "region_id"})
                if "region_id" not in melted.columns:
                    melted["region_id"] = "All"
                # If Type column exists, keep Actuals only
                type_col = None
                for cand in ["Type","type"]:
                    if cand in df_raw.columns:
                        type_col = cand
                        break
                if type_col is not None:
                    try:
                        melted = melted[df_raw[type_col].astype(str).str.lower().eq("actual")]
                    except Exception:
                        pass
                df_norm = melted
            else:
                missing = [k for k in required_keys if k not in effective_map]
                raise ValueError(f"{fp.name} missing required columns ({missing}). Available columns: {list(df_raw.columns)}")
        else:
            missing = [k for k in required_keys if k not in effective_map]
            if missing:
                raise ValueError(
                    f"{fp.name} missing required columns ({missing}). Available columns: {list(df_raw.columns)}"
                )
            # Normalize required + optional columns via settings map where present
            merged_map = {**effective_map, **{k: v for k, v in base_colmap.items() if k not in effective_map and v in df_raw.columns}}
            df_norm = _normalize_schema(df_raw, merged_map)
        # Coerce dtypes
        df_norm["date"] = pd.to_datetime(df_norm["date"], errors="coerce")
        df_norm["units"] = pd.to_numeric(df_norm["units"], errors="coerce")
        df_norm = df_norm.dropna(subset=["date","units"]) 
        frames.append(df_norm)
    df_all = pd.concat(frames, ignore_index=True, sort=False)
    df_week = _aggregate_to_week(df_all)
    df_week = df_week.sort_values(["sku_id","region_id","date"]).reset_index(drop=True)
    return df_week

def validate_sales(df: pd.DataFrame) -> pd.DataFrame:
    required = ["date","sku_id","region_id","units"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = df.sort_values(["sku_id","region_id","date"]).copy()
    return df
