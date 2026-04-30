from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models 

def get_readings(db: Session, limit: int = None, days: int = None):
    """Genel veri çekme fonksiyonu (Dashboard ve Analiz için)"""
    query = db.query(models.MeterReading).order_by(models.MeterReading.timestamp.desc())
    
    if days:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.MeterReading.timestamp >= start_date)
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

def create_meter_reading(db: Session, timestamp, meter_id, consumption, price, smf=None, yal=None, yat=None):
    """Yeni IoT veya Piyasa verisi kaydetme fonksiyonu"""
    db_reading = models.MeterReading(
        timestamp=timestamp,
        meter_id=meter_id,
        consumption=consumption,
        price=price,
        smf=smf,
        yal=yal,
        yat=yat
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_recent_readings(db: Session, limit: int = 10):
    """Dashboard'daki tablo için en güncel verileri getirir"""
    return db.query(models.MeterReading).order_by(models.MeterReading.timestamp.desc()).limit(limit).all()