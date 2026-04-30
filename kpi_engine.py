def calculate_vpp_performance(actual_consumption, actual_price, smf=None, optimization_ratio=0.15):
    """
    VPP performansını SMF (Sistem Marjinal Fiyatı) duyarlı olarak hesaplar.
    
    actual_consumption: IoT'den gelen gerçekleşen tüketim (kWh)
    actual_price: EPİAŞ'tan gelen PTF (TL/MWh)
    smf: EPİAŞ'tan gelen SMF (TL/MWh) - Eğer yoksa PTF'e eşitlenir.
    optimization_ratio: VPP'nin yük kaydırma yeteneği (Varsayılan %15 esneklik)
    """
    
    # 1. Birim Dönüşümü (TL/MWh -> TL/kWh)
    ptf_kwh = actual_price / 1000
    # SMF verisi gelmemişse veya 0 ise PTF'i baz al
    smf_kwh = (smf / 1000) if (smf is not None and smf > 0) else ptf_kwh

    # 2. Etkin Maliyet Belirleme
    # Arbitraj mantığı: Eğer SMF > PTF ise, sistemde enerji açığı vardır ve 
    # dengesizlik maliyeti SMF üzerinden binmiş olabilir.
    effective_unit_cost = max(ptf_kwh, smf_kwh)

    # 3. Baseline (Müdahale Edilmeseydi Ne Olurdu?)
    # VPP müdahale etmeseydi tüketim daha yüksek olacaktı.
    baseline_consumption = actual_consumption / (1 - optimization_ratio)
    
    # 4. Maliyet Hesaplamaları
    baseline_cost = baseline_consumption * effective_unit_cost
    actual_cost = actual_consumption * effective_unit_cost
    
    # 5. Tasarruf ve Performans Metrikleri
    net_savings = baseline_cost - actual_cost
    # Arbitraj Kazancı: SMF ve PTF arasındaki makasın VPP tarafından kullanılması
    arbitrage_gain = (baseline_consumption - actual_consumption) * (smf_kwh - ptf_kwh) if smf_kwh > ptf_kwh else 0
    
    savings_percent = (net_savings / baseline_cost) * 100 if baseline_cost > 0 else 0
    
    return {
        "savings": round(net_savings, 2),
        "savings_ratio_percent": round(savings_percent, 2),
        "arbitrage_impact": round(arbitrage_gain, 2),
        "effective_price_kwh": round(effective_unit_cost, 4),
        "market_status": "Dengesizlik Riski (Yüksek Maliyet)" if smf_kwh > ptf_kwh else "Dengeli Piyasa"
    }