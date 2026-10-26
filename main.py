import os
import joblib
import json
import numpy as np
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.models import CustomerSegment, ClusterDefinition

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Segmentation App")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

MODEL_PATH = "app/ml/kmeans_model.pkl"
SCALER_PATH = "app/ml/scaler.pkl"

kmeans_model = None
scaler = None

if os.path.exists(MODEL_PATH):
    try:
        kmeans_model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"[Warning] Gagal muat model: {e}")

if os.path.exists(SCALER_PATH):
    try:
        scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        print(f"[Warning] Gagal muat scaler: {e}")

def predict_cluster(age: int, annual_income: int, spending_score: int) -> int:
    features = np.array([[annual_income, spending_score]])
    if scaler:
        features = scaler.transform(features)
    cluster = kmeans_model.predict(features)[0]
    return int(cluster)

# 1. Dashboard Insight
@app.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    total_customers = db.query(CustomerSegment).count()
    clusters = db.query(ClusterDefinition).all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_customers": total_customers,
            "clusters": clusters
        }
    )

# 2. Form Input & Memproses Segmentasi
@app.get("/segment", response_class=HTMLResponse)
def get_segment_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="segment_form.html"
    )

@app.post("/segment")
def process_segment(
    gender: str = Form(...),
    age: int = Form(...),
    annual_income: int = Form(...),
    spending_score: int = Form(...),
    db: Session = Depends(get_db)
):
    cluster_label = predict_cluster(age, annual_income, spending_score) if kmeans_model else 0
    
    new_segment = CustomerSegment(
        gender=gender,
        age=age,
        annual_income=annual_income,
        spending_score=spending_score,
        cluster_label=cluster_label
    )
    db.add(new_segment)
    db.commit()
    db.refresh(new_segment)
    
    return RedirectResponse(url=f"/result/{new_segment.id}", status_code=303)

# 3. Hasil Segmentasi
@app.get("/result/{id}", response_class=HTMLResponse)
def get_result(id: int, request: Request, db: Session = Depends(get_db)):
    data = db.query(CustomerSegment).filter(CustomerSegment.id == id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    cluster_info = db.query(ClusterDefinition).filter(ClusterDefinition.cluster_label == data.cluster_label).first()
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "data": data,
            "cluster_info": cluster_info
        }
    )

# 4. Riwayat Segmentasi
@app.get("/history", response_class=HTMLResponse)
def get_history(request: Request, db: Session = Depends(get_db)):
    history_data = db.query(CustomerSegment).order_by(CustomerSegment.id.desc()).all()
    clusters = db.query(ClusterDefinition).all()
    cluster_map = {c.cluster_label: c.cluster_name for c in clusters}
    
    # Format list untuk kebutuhan Chart.js
    history_list = [
        {
            "id": item.id,
            "gender": item.gender,
            "age": item.age,
            "annual_income": item.annual_income,
            "spending_score": item.spending_score,
            "cluster_label": item.cluster_label,
            "cluster_name": cluster_map.get(item.cluster_label, f"Cluster {item.cluster_label}")
        }
        for item in history_data
    ]
    
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "history": history_data,
            "cluster_map": cluster_map,
            "history_json": json.dumps(history_list)
        }
    )

# 5. Form & Proses Update
@app.get("/update/{id}", response_class=HTMLResponse)
def get_update_form(id: int, request: Request, db: Session = Depends(get_db)):
    data = db.query(CustomerSegment).filter(CustomerSegment.id == id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    
    clusters = db.query(ClusterDefinition).all()
    cluster_map = {c.cluster_label: c.cluster_name for c in clusters}
    cluster_info = db.query(ClusterDefinition).filter(ClusterDefinition.cluster_label == data.cluster_label).first()
    
    return templates.TemplateResponse(
        request=request,
        name="update_form.html",
        context={
            "data": data,
            "cluster_map": cluster_map,
            "cluster_info": cluster_info
        }
    )

@app.post("/update/{id}")
def process_update(
    id: int,
    gender: str = Form(...),
    age: int = Form(...),
    annual_income: int = Form(...),
    spending_score: int = Form(...),
    db: Session = Depends(get_db)
):
    data = db.query(CustomerSegment).filter(CustomerSegment.id == id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    
    data.gender = gender
    data.age = age
    data.annual_income = annual_income
    data.spending_score = spending_score
    data.cluster_label = predict_cluster(age, annual_income, spending_score) if kmeans_model else data.cluster_label
    
    db.commit()
    return RedirectResponse(url=f"/result/{data.id}", status_code=303)

# 6. Delete Data
@app.post("/delete/{id}")
def delete_segment(id: int, db: Session = Depends(get_db)):
    data = db.query(CustomerSegment).filter(CustomerSegment.id == id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    db.delete(data)
    db.commit()
    return RedirectResponse(url="/history", status_code=303)