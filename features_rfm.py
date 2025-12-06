# features_rfm.py
import pandas as pd
import numpy as np

df = pd.read_csv("data_cleaned.csv", parse_dates=['InvoiceDate'])

snapshot = df['InvoiceDate'].max() + pd.Timedelta(days=1)

rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalPrice': 'sum'
}).reset_index().rename(columns={
    'InvoiceDate': 'Recency',
    'InvoiceNo': 'Frequency',
    'TotalPrice': 'Monetary'
})

# Additional features: Average Order Value (AOV)
aov = df.groupby('CustomerID')['TotalPrice'].mean().rename('AOV').reset_index()
rfm = rfm.merge(aov, on='CustomerID', how='left')

# Median inter-purchase days
def median_days_between(x):
    x = x.sort_values()
    diffs = x.diff().dt.days.dropna()
    return diffs.median() if not diffs.empty else np.nan

median_ip = df.groupby('CustomerID')['InvoiceDate'].apply(median_days_between).rename('MedianDaysBetween').reset_index()
rfm = rfm.merge(median_ip, on='CustomerID', how='left')

# Log transforms
rfm['Monetary_log'] = np.log1p(rfm['Monetary'])
rfm['Recency_log'] = np.log1p(rfm['Recency'])

rfm.to_csv("rfm_features.csv", index=False)
print("Saved RFM features to rfm_features.csv")
