# label_clusters.py
import pandas as pd

rfm = pd.read_csv("rfm_with_clusters.csv")

# Map numeric clusters to business-friendly segments
mapping = {
    0: "Champions",
    1: "Loyal Customers",
    2: "Potential Loyalists",
    3: "At-Risk / Lost Customers"
}

rfm['Segment'] = rfm['KM_Cluster'].map(mapping)

rfm.to_csv("rfm_with_clusters_labeled.csv", index=False)
print("Cluster labels added successfully and saved to rfm_with_clusters_labeled.csv")

