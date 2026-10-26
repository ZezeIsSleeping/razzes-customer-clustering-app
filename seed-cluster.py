from app.database import SessionLocal
from app.models import ClusterDefinition

db = SessionLocal()
clusters = [
    ClusterDefinition(cluster_label=0, cluster_name="Sensible Customers", description="Pendapatan rendah, pengeluaran rendah."),
    ClusterDefinition(cluster_label=1, cluster_name="Standard Customers", description="Pendapatan sedang, pengeluaran sedang."),
    ClusterDefinition(cluster_label=2, cluster_name="Target Customers", description="Pendapatan tinggi, pengeluaran tinggi."),
    ClusterDefinition(cluster_label=3, cluster_name="Careless Customers", description="Pendapatan rendah, pengeluaran tinggi."),
    ClusterDefinition(cluster_label=4, cluster_name="Conservative Customers", description="Pendapatan tinggi, pengeluaran rendah."),
]

for c in clusters:
    db.merge(c)
db.commit()
db.close()
print("Berhasil seeding cluster_definitions!")