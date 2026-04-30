from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from sqlalchemy.exc import OperationalError

# Veritabanı bağlantı adresi (Docker'da çalışacak olan PostgreSQL)
DATABASE_URL = "postgresql://user:password@db:5432/vpp_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı Tablosu (İlandaki Data Schema tasarımı tam olarak budur)
class MeterData(Base):
    __tablename__ = "meter_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    meter_id = Column(String)
    consumption = Column(Float)
    price = Column(Float)

def get_db_connection_with_retry(engine, retries=5, delay=3):
    for i in range(retries):
        try:
            connection = engine.connect()
            return connection
        except OperationalError:
            if i < retries - 1:
                print(f"Veritabanı hazır değil, {delay} saniye sonra tekrar deneniyor... ({i+1}/{retries})")
                time.sleep(delay)
            else:
                raise

def init_db():
    Base.metadata.create_all(bind=engine)