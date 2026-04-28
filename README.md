# ⚡ FCAS Bidding Bot v2

**ML-optimized FCAS bid strategy — All 10 NEM markets (incl. Very Fast 1-sec) + AEMO 10-Band Bid Output**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](FCAS_Bidding_Bot.ipynb)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-ff4b4b?logo=streamlit)](app.py)
[![Framework](https://img.shields.io/badge/Master_ML%2FDL-12_Steps-c084fc)](FCAS_Bidding_Bot.ipynb)

---

## 📋 What This Does

Forecasts prices across all **10 NEM FCAS markets** and generates **AEMO-format 10 price-quantity bid bands (BP1–BP10)** per service per trading interval for a BESS.

### 10 FCAS Markets (since Oct 2023)

| # | Service | Response | Category | AEMO ID |
|---|---------|----------|----------|---------|
| 1 | R1S — Very Fast Raise | **1 second** | Contingency | RAISE1SEC |
| 2 | R6S — Fast Raise | 6 seconds | Contingency | RAISE6SEC |
| 3 | R60S — Slow Raise | 60 seconds | Contingency | RAISE60SEC |
| 4 | R5M — Delayed Raise | 5 minutes | Contingency | RAISE5MIN |
| 5 | RREG — Regulation Raise | Continuous | Regulation | RAISEREG |
| 6 | L1S — Very Fast Lower | **1 second** | Contingency | LOWER1SEC |
| 7 | L6S — Fast Lower | 6 seconds | Contingency | LOWER6SEC |
| 8 | L60S — Slow Lower | 60 seconds | Contingency | LOWER60SEC |
| 9 | L5M — Delayed Lower | 5 minutes | Contingency | LOWER5MIN |
| 10 | LREG — Regulation Lower | Continuous | Regulation | LOWERREG |

### Output: AEMO 10-Band Bid Schedule

Each output CSV contains per-service, per-interval:
- `BP1_price` through `BP10_price` ($/MWh, ascending)
- `BP1_qty` through `BP10_qty` (MW per band)
- `MaxAvail` (total MW available)
- `ForecastPrice` (ML forecast clearing price)

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/FCAS_Bidding_Bot.git
cd FCAS_Bidding_Bot
pip install -r requirements.txt
jupyter notebook FCAS_Bidding_Bot.ipynb
```

## 🔄 Re-run

```python
r = quick_forecast(2025, 6)
r = quick_forecast(2025, 3, plot_date='2025-03-15')
plot_day_detail('2025-01-15')  # shows 10-service bids for any day
```

## 📁 Key Outputs

```
outputs/
├── bid_bands_R1S_SA1_202501.csv     ← Very Fast Raise bid bands
├── bid_bands_R6S_SA1_202501.csv     ← Fast Raise bid bands
├── ...                               ← (one file per service)
├── bid_bands_ALL_SERVICES.csv        ← combined 10-service bands
├── fcas_price_forecast_10svc.csv     ← forecasts
├── fcas_revenue_10svc.csv            ← revenue
└── dashboard_fcas10.png              ← 6-panel dashboard
```

## 📄 License

MIT
