# ingestion/ingest.py
import polars as pl
import duckdb

def load_inventory_csv(path: str) -> pl.DataFrame:
    df = pl.read_csv(path, try_parse_dates=True)
    # Normalize column names
    df = df.rename({
        "Product ID": "product_id",
        "Stock Quantity": "stock_qty",
        "Daily Sales": "daily_sales",
        "Category": "category",
        "Date": "date"
    })
    return df

def save_to_duckdb(df: pl.DataFrame, db_path="data/inventory.duckdb"):
    con = duckdb.connect(db_path)
    con.execute("CREATE TABLE IF NOT EXISTS inventory AS SELECT * FROM df")
    con.execute("INSERT INTO inventory SELECT * FROM df")
    con.close()

if __name__ == "__main__":
    df = load_inventory_csv("data/raw/retail_inventory.csv")
    save_to_duckdb(df)
    print(f"Loaded {len(df)} rows into DuckDB")