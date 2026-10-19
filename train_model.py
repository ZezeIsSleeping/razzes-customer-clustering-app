import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from app.database import SessionLocal, engine, Base
from app.models import ClusterDefinition

# 1. Pastiin folder app/ml udah ada
os.makedirs("app/ml", exist_ok=True)

# 2. Baca dataset (sesuaikan nama file CSV dataset kamu)
df = pd.read_csv("Mall_Customers.csv")

# 3. Pilih fitur utama untuk clustering
X = df[["Annual Income (k$)", "Spending Score (1-100)"]]

# 4. Feature Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Latih Model K-Means
kmeans = KMeans(n_clusters=5, random_state=42)
kmeans.fit(X_scaled)

# 6. Simpan Model dan Scaler ke folder app/ml
joblib.dump(kmeans, "app/ml/kmeans_model.pkl")
joblib.dump(scaler, "app/ml/scaler.pkl")
print("Model K-Means dan Scaler berhasil disimpan di app/ml/")

# 7. Isi data awal tabel cluster_definitions di Database
Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(ClusterDefinition).count() == 0:
    definitions = [
        ClusterDefinition(cluster_label=0, cluster_name="Sensible", description="Pendapatan rendah, skor belanja rendah"),
        ClusterDefinition(cluster_label=1, cluster_name="Careless", description="Pendapatan rendah, skor belanja tinggi"),
        ClusterDefinition(cluster_label=2, cluster_name="Target / High Value", description="Pendapatan tinggi, skor belanja tinggi"),
        ClusterDefinition(cluster_label=3, cluster_name="Frugal", description="Pendapatan tinggi, skor belanja rendah"),
        ClusterDefinition(cluster_label=4, cluster_name="Standard", description="Pendapatan rata-rata, skor belanja rata-rata"),
    ]
    db.add_all(definitions)
    db.commit()
    print("Data awal cluster_definitions berhasil diinput ke database!")

db.close()