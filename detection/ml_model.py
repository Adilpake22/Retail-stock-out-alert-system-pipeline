# detection/ml_model.py
from prophet import Prophet
import pandas as pd

def predict_stockout_date(sales_history: pd.DataFrame,
                           product_id: str,
                           current_stock: int) -> int:
    """Returns predicted days until stock-out."""
    model = Prophet(daily_seasonality=True)
    model.fit(sales_history.rename(columns={"date": "ds", "sales": "y"}))

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    daily_demand = forecast["yhat"].tail(30).mean()
    return int(current_stock / max(daily_demand, 1))