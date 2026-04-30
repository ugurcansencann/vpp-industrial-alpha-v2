import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_energy_data(days=7):
    start_date = datetime(2026, 4, 1)
    data = []
    
    for i in range(24 * days):
        current_time = start_date + timedelta(hours=i)
        hour = current_time.hour
        
        # Basit bir tüketim mantığı: Akşam saatlerinde (18-22) artan tüketim
        base_consumption = 50 + 20 * np.sin(2 * np.pi * (hour - 6) / 24)
        consumption = base_consumption + np.random.normal(0, 5)
        
        # Fiyat mantığı: Gündüz pahalı, gece ucuz
        price = 1500 + 1000 * np.sin(2 * np.pi * (hour - 12) / 24)
        
        data.append([current_time, "SAYAC_001", round(consumption, 2), round(price, 2)])

    df = pd.DataFrame(data, columns=["timestamp", "meter_id", "consumption", "price"])
    df.to_csv("meter_data.csv", index=False)
    print("meter_data.csv oluşturuldu!")

if __name__ == "__main__":
    generate_energy_data()