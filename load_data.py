import pandas as pd
from sqlalchemy import create_engine

# Connection to your ERP database
engine = create_engine(
    "postgresql://postgres:Shrig%40123@localhost:5432/synchain_erp")

# Load a sample of the dataset (first 2000 rows)
df = pd.read_csv("data/DataCoSupplyChainDataset.csv",
                 encoding="latin1", nrows=2000)

# Dump as a staging table first (raw, unprocessed) — we'll clean/split it next
df.to_sql("raw_dataco_orders", engine, if_exists="replace", index=False)

print(f"Loaded {len(df)} rows into raw_dataco_orders table.")
