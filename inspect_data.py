import pandas as pd

df = pd.read_csv("data/DataCoSupplyChainDataset.csv",
                 encoding="latin1", nrows=5)
print(df.columns.tolist())
print(df.head())
