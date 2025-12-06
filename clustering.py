# clustering.py (updated for 4 clusters)
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Load RFM features
rfm = pd.read_csv("rfm_features.csv")
X = rfm[['Recency_log','Frequency','Monetary_log']].fillna(0).values

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---- FORCE k=4 ----
k = 4
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
rfm['KM_Cluster'] = kmeans.fit_predict(X_scaled)

# Add PCA for visualization
pca = PCA(n_components=2, random_state=42)
proj = pca.fit_transform(X_scaled)
rfm['PC1'], rfm['PC2'] = proj[:,0], proj[:,1]

# Calculate cluster summary (for interpretation)
cluster_summary = rfm.groupby('KM_Cluster').agg({
    'Monetary': 'mean',
    'Frequency': 'mean',
    'Recency': 'mean',
    'CustomerID': 'count'
}).rename(columns={'CustomerID': 'CustomerCount'})

cluster_summary.to_csv("cluster_summary.csv")

# Save updated file
rfm.to_csv("rfm_with_clusters.csv", index=False)

print("\nClustering Completed with k=4!")
print("\nCluster summary:\n", cluster_summary)
