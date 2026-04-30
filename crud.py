from sqlalchemy.orm import Session
from database import SessionLocal, MeterData
from datetime import datetime

# Veritabanına yeni bir ölçüm verisi kaydetme fonksiyonu
def create_meter_reading(db: Session, timestamp: datetime, meter_id: str, consumption: float, price: float):
    db_item = MeterData(
        timestamp=timestamp,
        meter_id=meter_id,
        consumption=consumption,
        price=price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Veritabanından son verileri çekme (Örn: Dashboard için)
def get_recent_readings(db: Session, limit: int = 10):
    return db.query(MeterData).order_by(MeterData.timestamp.desc()).limit(limit).all()