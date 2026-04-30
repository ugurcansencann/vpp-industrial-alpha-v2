import pandas as pd
from sqlalchemy import create_all, create_engine
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# Veritabanı Bağlantı Bilgisi (Docker ortamına uygun)
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/vpp_db")

def train_baseline_model():
    # 1. Veriyi Veritabanından Çek (Artık CSV yok!)
    engine = create_engine(DB_URL)
    query = "SELECT timestamp, consumption, price FROM meter_readings"
    
    try:
        df = pd.read_sql(query, engine)
        if len(df) < 10:
            print("Eğitim için yeterli veri yok (En az 10 satır lazım).")
            return
    except Exception as e:
        print(f"Hata: Veritabanına bağlanılamadı. {e}")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 2. Gelişmiş Özellik Mühendisliği (Feature Engineering)
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    # Fiyatı da modele girdi olarak veriyoruz çünkü fiyat tüketime etki eder!
    df['price_norm'] = df['price'] / 1000 
    
    # X: Saat, Gün, Fiyat | y: Tüketim
    X = df[['hour', 'day_of_week', 'price_norm']]
    y = df['consumption']
    
    # 3. Modeli Eğit
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y) # Test split'i canlı eğitimde (MLOps) genelde tüm veriyle yaparız
    
    # 4. Modeli Kaydet
    joblib.dump(model, "consumption_model.pkl")
    print(f"Model {len(df)} satır veri ile güncellendi ve kaydedildi!")

if __name__ == "__main__":
    train_baseline_model()