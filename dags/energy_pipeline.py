from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import random

# Proje yolları
sys.path.append('/app') 
from database import SessionLocal
from crud import create_meter_reading

default_args = {
    'owner': 'vpp_architect',
    'start_date': datetime(2026, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --- GÖREV 1: Fiyat Verisi (PTF) ---
def fetch_ptf_price(**kwargs):
    current_hour = datetime.now().hour
    if 17 <= current_hour <= 22:
        price = random.uniform(2500.0, 3000.0)
    elif 0 <= current_hour <= 6:
        price = random.uniform(1000.0, 1500.0)
    else:
        price = random.uniform(1800.0, 2200.0)
    
    # Veriyi XCom'a gönderir
    return round(price, 2)

# --- GÖREV 2: IoT Sensör Verisi (Lokal OSB) ---
def fetch_iot_consumption(**kwargs):
    current_hour = datetime.now().hour
    # Aydın OSB Aydınlatma Grubu Simülasyonu
    base_load = 120.0 if (current_hour >= 19 or current_hour <= 6) else 10.0
    consumption = base_load + random.uniform(-2.0, 2.0)
    
    return round(consumption, 2)

# --- GÖREV 3: Verileri Birleştir ve DB'ye Kaydet ---
def merge_and_store(ti, **kwargs):
    # XCom üzerinden diğer görevlerin çıktılarını çek
    price = ti.xcom_pull(task_ids='get_ptf_price')
    consumption = ti.xcom_pull(task_ids='get_iot_load')
    
    db = SessionLocal()
    try:
        create_meter_reading(
            db=db,
            timestamp=datetime.now(),
            meter_id="AYDIN_OSB_LIGHT_01",
            consumption=consumption,
            price=price
        )
        print(f"BAŞARI: PTF({price}) ve IoT({consumption}) verileri birleştirildi.")
    finally:
        db.close()

# --- DAG TANIMI ---
with DAG('vpp_osb_modular_pipeline_v36', 
         default_args=default_args, 
         # Her dakika çalışması için (Minute, Hour, Day, Month, Weekday)
         schedule_interval=timedelta(minutes=1), 
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='get_ptf_price',
        python_callable=fetch_ptf_price
    )

    t2 = PythonOperator(
        task_id='get_iot_load',
        python_callable=fetch_iot_consumption
    )

    t3 = PythonOperator(
        task_id='save_to_postgresql',
        python_callable=merge_and_store
    )

    # Akış Şeması: Fiyat ve Yük aynı anda çekilir, bitince DB'ye kaydedilir.
    [t1, t2] >> t3