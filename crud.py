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

def get_last_24h_prices(db: Session):
    """DB'deki son 24 saatlik PTF (price) değerlerini getirir."""
    one_day_ago = datetime.now() - timedelta(days=1)
    return db.query(models.MeterReading)\
        .filter(models.MeterReading.timestamp >= one_day_ago)\
        .order_by(models.MeterReading.timestamp.asc())\
        .all()

def save_ml_forecast(db: Session, timestamp: datetime, predicted_val: float, expected_price: float):
    """ML modelinden gelen tahmin çıktılarını DB'ye yazar."""
    db_forecast = models.Forecast(
        timestamp=timestamp,
        predicted_consumption=predicted_val,
        expected_price=expected_price
    )
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast

def get_tomorrow_forecasts_from_db(db: Session):
    """DB'den yarın için kaydedilmiş tahmin çıktılarını çeker."""
    tomorrow = datetime.now().date() + timedelta(days=1)
    return db.query(models.Forecast)\
        .filter(models.Forecast.timestamp >= datetime.combine(tomorrow, datetime.min.time()))\
        .order_by(models.Forecast.timestamp.asc())\
        .all()
