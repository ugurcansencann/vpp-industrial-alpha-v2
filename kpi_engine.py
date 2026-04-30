# app/kpi_engine.py (Yeni bir dosya olarak düşünebilirsin)

def calculate_vpp_performance(actual_consumption, actual_price, optimization_ratio=0.15):
    """
    VPP performansını hesaplar. 
    optimization_ratio: VPP'nin yük kaydırma yeteneği (Örn: %15 esneklik)
    """
    # Müdahale edilmeseydi tüketim muhtemelen daha yüksek olacaktı (Basit bir varsayımla)
    baseline_consumption = actual_consumption / (1 - optimization_ratio)
    
    baseline_cost = baseline_consumption * actual_price
    actual_cost = actual_consumption * actual_price
    
    savings = baseline_cost - actual_cost
    savings_percent = (savings / baseline_cost) * 100
    
    return {
        "baseline_cost_tl": round(baseline_cost, 2),
        "actual_vpp_cost_tl": round(actual_cost, 2),
        "net_savings_tl": round(savings, 2),
        "savings_ratio_percent": round(savings_percent, 2)
    }