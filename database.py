from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

def init_db():
    Base.metadata.create_all(bind=engine)