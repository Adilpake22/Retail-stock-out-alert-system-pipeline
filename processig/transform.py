
import polars as pl

def compute_metrics(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        # Days of stock remaining
        (pl.col("stock_qty") / pl.col("daily_sales").clip(1))
          .alias("days_of_inventory"),

        # 7-day average sales velocity
        pl.col("daily_sales")
          .rolling_mean(window_size=7, min_periods=1)
          .alias("sales_velocity_7d"),

        # Reorder flag
        (pl.col("stock_qty") < pl.col("daily_sales") * 7)
          .alias("needs_reorder")
    ])