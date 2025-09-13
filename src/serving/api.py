from __future__ import annotations
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="Pharma Sales Forecasting API",
    description="API for pharmaceutical sales forecasting and inventory planning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FP = Path("data/outputs/forecast.csv")

class ForecastResponse(BaseModel):
    sku_id: str
    region_id: str
    date: str
    forecast: float
    pi_low: Optional[float] = None
    pi_high: Optional[float] = None

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pharma-forecast-api"}

@app.get("/v1/forecast", response_model=List[ForecastResponse])
def get_forecast(
    sku_id: str = Query(..., description="Product SKU identifier"),
    region_id: str = Query(..., description="Region identifier"),
):
    """Get sales forecast for a specific SKU and region."""
    if not DATA_FP.exists():
        raise HTTPException(status_code=404, detail="Forecast data not found. Run backtest and forecast scripts first.")
    
    df = pd.read_csv(DATA_FP, parse_dates=["date"])
    out = df[(df["sku_id"] == sku_id) & (df["region_id"] == region_id)].copy().sort_values("date")
    
    if out.empty:
        raise HTTPException(status_code=404, detail=f"No forecast found for SKU: {sku_id}, Region: {region_id}")
    
    records = [
        ForecastResponse(
            sku_id=row["sku_id"],
            region_id=row["region_id"],
            date=row["date"].strftime("%Y-%m-%d"),
            forecast=float(row["forecast"]),
            pi_low=float(row["pi_low"]) if "pi_low" in out.columns and pd.notna(row["pi_low"]) else None,
            pi_high=float(row["pi_high"]) if "pi_high" in out.columns and pd.notna(row["pi_high"]) else None,
        )
        for _, row in out.iterrows()
    ]
    return records

# Backward compatibility
@app.get("/forecast", response_model=List[ForecastResponse])
def get_forecast_legacy(sku_id: str = Query(...), region_id: str = Query(...)):
    """Legacy forecast endpoint for backward compatibility."""
    return get_forecast(sku_id, region_id)


class Pair(BaseModel):
    sku_id: str
    region_id: str

@app.get("/v1/meta/pairs", response_model=List[Pair])
def get_pairs():
    """Get available SKU and region pairs."""
    if not DATA_FP.exists():
        raise HTTPException(status_code=404, detail="Forecast data not found.")
    
    df = pd.read_csv(DATA_FP)
    if not {"sku_id","region_id"}.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Invalid data format.")
    
    uniq = df[["sku_id","region_id"]].drop_duplicates().sort_values(["sku_id","region_id"]) 
    return [Pair(sku_id=r["sku_id"], region_id=r["region_id"]) for _, r in uniq.iterrows()]

# Backward compatibility
@app.get("/meta/pairs", response_model=List[Pair])
def get_pairs_legacy():
    """Legacy pairs endpoint for backward compatibility."""
    return get_pairs()
