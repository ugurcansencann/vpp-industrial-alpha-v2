from fastapi import FastAPI
import joblib
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from fastapi.responses import HTMLResponse # En üste ekle
from database import engine, Base, SessionLocal, MeterData, init_db
import redis
import json
from kpi_engine import calculate_vpp_performance
import subprocess # Terminal komutu çalıştırmak için

def init_db():
    Base.metadata.create_all(bind=engine)

init_db()
app = FastAPI(title="Wattica VPP-Optima API")

# Redis bağlantısı
cache = redis.Redis(host='redis', port=6379, db=0)

@app.post("/retrain")
def retrain_model():
    try:
        # train_model.py dosyasını sistem içinde çalıştırır
        result = subprocess.run(["python", "train_model.py"], capture_output=True, text=True)
        # Yeni eğitilen modeli tekrar yükle
        global model
        model = joblib.load("consumption_model.pkl")
        # Redis'i temizle (Eski tahminler silinsin)
        cache.flushdb() 
        return {"status": "success", "message": "Model başarıyla yeniden eğitildi ve güncellendi!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/db-test")
def test_db():
    try:
        with engine.connect() as connection:
            return {"status": "success", "message": "PostgreSQL bağlantısı sapasağlam!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/history")
def get_history():
    db = SessionLocal()
    try:
        # DB'deki son 10 kaydı getir
        data = db.query(MeterData).order_by(MeterData.timestamp.desc()).limit(10).all()
        return data
    finally:
        db.close()

# En alta, uvicorn.run'dan hemen önce ekle:
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
    
# 1. Modeli Yükle
model = joblib.load("consumption_model.pkl")

@app.get("/")
def home():
    return {"message": "VPP-Optima Akıllı Enerji Yönetim Sistemine Hoş Geldiniz!"}

@app.get("/optimize")
def get_optimization(hour: int, day_of_week: int, current_price: float):
    cache_key = f"pred_{hour}_{day_of_week}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print("Veri Redis'ten (Cache) getirildi!")
        return json.loads(cached_data)

    # --- BÖLÜM 1: TAHMİN ---
    input_data = pd.DataFrame([[hour, day_of_week]], columns=['hour', 'day_of_week'])
    predicted_load = model.predict(input_data)[0]
    
    # --- BÖLÜM 2: OPTİMİZASYON (PuLP) ---
    # Senaryo: Fiyat yüksekse tüketimi %20 kısabiliriz (Esneklik kapasitesi)
    # Hedef: Maliyeti minimize etmek
    
    prob = LpProblem("Maliyet_Minimizasyonu", LpMinimize)
    
    # Değişken: Gerçekleşecek Tüketim (Tahmin edilenin %80'i ile %100'ü arasında değişebilir)
    # Yani cihazları biraz kısma esnekliğimiz var.
    consumption_var = LpVariable("Gercek_Tuketim", lowBound=predicted_load * 0.8, upBound=predicted_load)
    
    # Amaç Fonksiyonu: Tüketim * Mevcut Fiyat
    prob += consumption_var * current_price
    
    # Çöz
    prob.solve()
    
    optimized_load = value(consumption_var)
    savings = (predicted_load - optimized_load) * current_price
    
    result = {
        "status": "Success",
        "analysis": {
            "predicted_base_load": round(predicted_load, 2),
            "optimized_load": round(optimized_load, 2),
            "flexibility_used": "20%" if optimized_load < predicted_load else "0%",
            "potential_savings_tl": round(savings, 2)
        },
        "market_info": {
            "current_price": current_price,
            "hour": hour
        }
    }
    # Sonucu Redis'e kaydet (1 saat boyunca sakla)
    cache.setex(cache_key, 3600, json.dumps(result))
    return result 

@app.get("/vpp-performance/{meter_id}")
def get_vpp_metrics(meter_id: str, db: Session = Depends(get_db)):
    # 1. DB'den son okumayı getir
    reading = crud.get_last_reading(db, meter_id) # CRUD'da bu fonksiyonun olduğunu varsayıyoruz
    
    if not reading:
        return {"error": "Veri bulunamadı"}

    # 2. KPI motorunu çalıştır
    metrics = calculate_vpp_performance(
        actual_consumption=reading.consumption,
        actual_price=reading.price
    )
    
    # 3. Sonuçları birleştirip döndür
    return {
        "meter_id": meter_id,
        "timestamp": reading.timestamp,
        "current_values": {
            "consumption": reading.consumption,
            "price": reading.price
        },
        "kpi_metrics": metrics
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)