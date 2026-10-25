"""
DeliverIQ: Supply Chain Delivery Performance & Shipping Optimization
Automated Data Engineering Pipeline
"""

import os
import sqlite3
import pandas as pd
import numpy as np


def run_pipeline(
    raw_data_path="data/DataCoSupplyChainDataset.csv",
    clean_csv_path="data/cleaned_supply_chain_data.csv",
    db_path="deliveriq.db",
):
    print("=" * 60)
    print("DeliverIQ: Starting Data Pipeline...")
    print("=" * 60)

    # 1. Ingestion
    print(f"[1/5] Loading raw supply chain dataset from {raw_data_path}...")
    df = pd.read_csv(raw_data_path, encoding="latin1")
    print(f"      Loaded {df.shape[0]:,} rows and {df.shape[1]} columns.")

    # 2. Data Hygiene: Drop empty/sensitive columns
    print("[2/5] Dropping non-essential and sensitive PII columns...")
    cols_to_drop = [
        "Product Description",
        "Order Zipcode",
        "Product Image",
        "Customer Password",
        "Customer Email",
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # 3. Column Standardization (Snake_Case)
    print("[3/5] Standardizing column names to clean snake_case...")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[()]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )

    df = df.rename(
        columns={
            "order_date_dateorders": "order_date",
            "shipping_date_dateorders": "shipping_date",
            "days_for_shipping_real": "days_for_shipping_real",
            "days_for_shipment_scheduled": "days_for_shipment_scheduled",
        }
    )

    # 4. Datetime & Feature Engineering
    print("[4/5] Parsing dates and engineering delivery metrics...")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["shipping_date"] = pd.to_datetime(df["shipping_date"])

    # Core performance metric: delay duration
    df["shipping_delay_days"] = (
        df["days_for_shipping_real"] - df["days_for_shipment_scheduled"]
    )
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month

    # Delivery performance categorization
    conditions = [
        df["shipping_delay_days"] < 0,
        df["shipping_delay_days"] == 0,
        df["shipping_delay_days"] > 0,
    ]
    choices = ["Early Delivery", "On Time Delivery", "Late Delivery"]
    df["delivery_performance"] = np.select(conditions, choices, default="Unknown")

    # 5. Database & CSV Export
    print(f"[5/5] Exporting clean data to {clean_csv_path} and SQLite {db_path}...")
    os.makedirs(os.path.dirname(clean_csv_path), exist_ok=True)
    df.to_csv(clean_csv_path, index=False)

    conn = sqlite3.connect(db_path)
    df.to_sql("orders", conn, if_exists="replace", index=False)
    conn.close()

    print("=" * 60)
    print("Pipeline Execution Completed Successfully!")
    print(f"Total Processed Orders: {len(df):,}")
    print(
        f"Overall Late Delivery Rate: {df['late_delivery_risk'].mean() * 100:.2f}%"
    )
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
