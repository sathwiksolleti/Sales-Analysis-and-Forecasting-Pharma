class Settings:
    def __init__(self):
        self.frequency = "W"
        self.horizon = 12
        self.country = "IN"
        self.use_lgbm = True
        # Data source configuration
        self.use_sample = False  # set to False to read your CSV
        self.csv_path = "data/raw/"
        # Performance/quick mode
        self.quick_mode = True
        self.max_groups = 3
        self.quick_horizon = 4
        self.light_features = True
        # Map your CSV columns to internal schema
        # Update values on the right to match your file headers
        self.column_map = {
            "date": "date",
            "sku_id": "sku_id",
            "region_id": "region_id",
            "channel_id": "channel_id",  # optional
            "units": "units",
            "price": "price",            # optional
            "discount": "discount",      # optional
            "promo_flag": "promo_flag",  # optional
            "stockout_flag": "stockout_flag"  # optional
        }

settings = Settings()
