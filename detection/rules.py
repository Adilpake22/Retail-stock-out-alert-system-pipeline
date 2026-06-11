
import polars as pl
from dataclasses import dataclass

@dataclass
class AlertConfig:
    critical_doi: int = 3    # < 3 days → CRITICAL
    warning_doi:  int = 7    # < 7 days → WARNING
    reorder_doi:  int = 14   # < 14 days → REORDER

def detect_stockouts(df: pl.DataFrame,
                     cfg: AlertConfig = AlertConfig()) -> pl.DataFrame:
    return df.with_columns([
        pl.when(pl.col("days_of_inventory") < cfg.critical_doi)
          .then(pl.lit("CRITICAL"))
          .when(pl.col("days_of_inventory") < cfg.warning_doi)
          .then(pl.lit("WARNING"))
          .when(pl.col("days_of_inventory") < cfg.reorder_doi)
          .then(pl.lit("REORDER"))
          .otherwise(pl.lit("OK"))
          .alias("alert_level")
    ]).filter(pl.col("alert_level") != "OK")