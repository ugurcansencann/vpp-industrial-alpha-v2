from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class MeterReading(Base):
    __tablename__ = "meter_readings"
    
    # extend_existing: Tabloyu yeniden tanımlar.
    # ix_meter_readings_id hatasını aşmak için manuel kontrol ekliyoruz.
    __table_args__ = {'extend_existing': True} 

    # index=True yerine sadece primary_key=True bırakmak genellikle yeterlidir 
    # çünkü primary key otomatik olarak benzersiz bir indeks oluşturur.
    id = Column(Integer, primary_key=True) 
    timestamp = Column(DateTime)
    meter_id = Column(String)
    consumption = Column(Float)
    price = Column(Float) 
    smf = Column(Float, nullable=True)
    yal = Column(Float, nullable=True)
    yat = Column(Float, nullable=True)