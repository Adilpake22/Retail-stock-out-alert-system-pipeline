# dags/stockout_dag.py
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(schedule="0 6 * * *",          # Runs daily at 6 AM
     start_date=datetime(2025, 1, 1),
     catchup=False,
     tags=["retail", "inventory"])
def retail_stockout_pipeline():

    @task
    def ingest():
        from ingestion.ingest import load_inventory_csv, save_to_duckdb
        df = load_inventory_csv("data/raw/retail_inventory.csv")
        save_to_duckdb(df)
        return "done"

    @task
    def validate(_):
        from processing.validate import validate_inventory
        import duckdb, polars as pl
        df = pl.from_arrow(duckdb.connect("data/inventory.duckdb")
                           .execute("SELECT * FROM inventory").arrow())
        validate_inventory(df)

    @task
    def transform(_):
        from processing.transform import compute_metrics
        import duckdb, polars as pl
        df = pl.from_arrow(duckdb.connect("data/inventory.duckdb")
                           .execute("SELECT * FROM inventory").arrow())
        return compute_metrics(df).write_parquet("data/processed.parquet")

    @task
    def detect_and_alert(_):
        from detection.rules import detect_stockouts, AlertConfig
        from alerts.notifier import send_slack_alert, send_email_alert
        import polars as pl
        df = pl.read_parquet("data/processed.parquet")
        alerts = detect_stockouts(df, AlertConfig())
        if len(alerts) > 0:
            send_slack_alert(alerts)
            send_email_alert(alerts, "warehouse-team@company.com")
            print(f"🚨 Sent alerts for {len(alerts)} products")

    raw = ingest()
    validated = validate(raw)
    processed = transform(validated)
    detect_and_alert(processed)

retail_stockout_pipeline()