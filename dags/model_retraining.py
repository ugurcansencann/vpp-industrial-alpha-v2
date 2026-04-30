import sys
import os
sys.path.append('/app')

# Şimdi import yapabilirsiniz
from database import SessionLocal

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Root dizindeki train_model.py'yi görebilmesi için path ekliyoruz
sys.path.append('/app') 
from train_model import run_ml_pipeline as run_retraining_pipeline

default_args = {
    'owner': 'ugurcan',
    'depends_on_past': False,
    'start_date': datetime(2026, 4, 30),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'vpp_model_retraining_pipeline',
    default_args=default_args,
    description='Son 30 veri ile tüketim tahmin modelini günceller',
    schedule_interval='@hourly', # Her saat başı çalışır
    catchup=False
) as dag:

    retrain_task = PythonOperator(
        task_id='retrain_consumption_model',
        python_callable=run_retraining_pipeline,
        op_kwargs={'limit': 30} # Fonksiyona gidecek parametre
    )

    retrain_task