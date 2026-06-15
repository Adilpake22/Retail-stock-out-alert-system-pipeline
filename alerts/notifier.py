# alerts/notifier.py
import smtplib, os
from slack_sdk import WebClient
from email.mime.text import MIMEText
import polars as pl

def send_slack_alert(alerts_df: pl.DataFrame):
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    for row in alerts_df.iter_rows(named=True):
        msg = (f"🚨 *{row['alert_level']}* | Product: `{row['product_id']}`\n"
               f"   Stock: {row['stock_qty']} units | "
               f"DOI: {row['days_of_inventory']:.1f} days")
        client.chat_postMessage(channel="#inventory-alerts", text=msg)

def send_email_alert(alerts_df: pl.DataFrame, to_email: str):
    body = alerts_df.select(
        ["product_id", "stock_qty", "days_of_inventory", "alert_level"]
    ).to_pandas().to_html()

    msg = MIMEText(body, "html")
    msg["Subject"] = f"⚠️ Stock-Out Alert — {len(alerts_df)} products at risk"
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = to_email

    with smtplib.SMTP(os.environ["SMTP_HOST"], 587) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)