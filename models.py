from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class MeterReading(Base):
    __tablename__ = "meter_readings"
    
    # extend_existing: Tabloyu yeniden tanımlar.
    # ix_meter_readings_id hatasını aşmak için manuel kontrol ekliyoruz.
    __table_args__ = {'extend_existing': True} 

    # index=True yerine sadece primary_key=True bırakmak genellikle yeterlidir 
    # çünkü primary key otomatik olarak benzersiz bir indeks oluşturur.
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    # Bu iki kolonun Float olduğundan emin olun
    consumption = Column(Float, nullable=False) 
    price = Column(Float, nullable=False)
    meter_id = Column(String, nullable=False)
    smf = Column(Float, nullable=True)
    yal = Column(Float, nullable=True)
    yat = Column(Float, nullable=True)