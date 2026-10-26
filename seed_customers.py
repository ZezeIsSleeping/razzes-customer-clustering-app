import random
import pandas as pd
from app.database import SessionLocal
from app.models import CustomerSegment
from main import predict_cluster, kmeans_model

def seed_data(total_records=100):
    db = SessionLocal()
    genders = ["Male", "Female"]

    print(f"Sedang menggenerate {total_records} data pelanggan...")

    for i in range(total_records):
        gender = random.choice(genders)
        age = random.randint(18, 70)
        # Income dalam k$ (range dataset standar 15 - 137)
        annual_income = random.randint(15, 137)
        # Spending Score (range 1 - 100)
        spending_score = random.randint(1, 100)

        # Prediksi cluster menggunakan model K-Means
        if kmeans_model:
            cluster_label = predict_cluster(age, annual_income, spending_score)
        else:
            cluster_label = 0

        customer = CustomerSegment(
            gender=gender,
            age=age,
            annual_income=annual_income,
            spending_score=spending_score,
            cluster_label=cluster_label
        )
        db.add(customer)

    db.commit()
    db.close()
    print(f"Berhasil menambahkan {total_records} data pelanggan ke database!")

if __name__ == "__main__":
    seed_data(100)  # Ubah angka ini jika ingin jumlah data yang lebih banyak