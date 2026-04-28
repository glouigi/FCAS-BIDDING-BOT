# ⚡ FCAS Bidding Bot — Frequency Control Ancillary Services

## ML Price Forecasting → Optimal 10-Band Bid Generation across all 10 NEM FCAS Markets

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](FCAS_Bidding_Bot.ipynb)
[![AEMO](https://img.shields.io/badge/Data-AEMO_DISPATCHPRICE-0078d4)](https://nemweb.com.au)
[![Framework](https://img.shields.io/badge/Master_ML%2FDL-12_Steps-c084fc)](FCAS_Bidding_Bot.ipynb)
[![Streamlit](https://img.shields.io/badge/Streamlit-Bid_Dashboard-ff4b4b?logo=streamlit)](app.py)
____________________________________________

<div align="right">
  <b>Giorgio Ramirez Quiroz</b><br>
  Electrical Engineer | Power Systems & Data Analytics<br>
  
  [![GitHub](https://img.shields.io/badge/github-%23121011.svg?logo=github&logoColor=white)](https://github.com/glouigi)
  [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/giorgio-ramirez-quiroz)
  [![Gmail Badge](https://img.shields.io/badge/-Gmail-c14438?&logo=Gmail&logoColor=white)](mailto:g.ramirezqui@gmail.com)
</div>

## 📋 Project Description

End-to-end machine learning pipeline for forecasting **Frequency Control Ancillary Services
(FCAS) prices** across all **10 NEM FCAS markets** — including the new **Very Fast (1-second)**
services introduced in October 2023 — and generating **AEMO-format 10 price-quantity bid
bands (BP1–BP10)** for a utility-scale Battery Energy Storage System (BESS).

The NEM's FCAS markets pay generators and loads to keep grid frequency at 50 Hz.
BESS are ideal FCAS providers: sub-second response, bidirectional operation, and the
ability to stack FCAS revenue on top of energy arbitrage. This project forecasts FCAS
clearing prices using XGBoost + LightGBM ensemble models, then constructs optimised bid
schedules that BESS operators can submit directly to AEMO via the NEM Dispatch Bidding API.

### Pipeline Overview

```
AEMO DISPATCHPRICE + TRADINGPRICE (30-min, 2 years)
         │
         ▼  STEP 2 — Data: NEMOSIS download (10 FCAS prices + energy + demand),
         │              integrity checks, caching, synthetic fallback
         │
         ▼  STEP 3 — EDA: diurnal patterns (10 services), VF vs Fast comparison,
         │              cross-service correlation, ACF, spike frequency, drift test
         │
         ▼  STEP 4 — Validation: temporal split, test set locked
         │
         ▼  STEPS 5–6 — Features: 70+ features per service
         │              (own-price lags, rolling stats, EWMA, cyclical encoding,
         │               energy price features, demand features, cross-service
         │               correlation features, regime flags)
         │              + RobustScaler pipeline fitted on TRAIN only
         │
         ▼  STEP 7 — Baselines: seasonal naive (lag 48), rolling mean
         │
         ▼  STEPS 8–9 — ML: per-service XGBoost + LightGBM
         │              inverse-MAE weighted ensemble
         │              Optuna TPE hyperparameter optimisation (optional)
         │
         ▼  STEP 10 — Evaluation: SHAP (R1S Very Fast focus), error-by-hour,
         │              one-time locked test set evaluation across 10 services
         │
         ▼  STEP 11 — Forecast: Seasonal Anchor method (full target month)
         │
         ▼  STEP 11b — Bid Generation: AEMO-format 10 price-quantity bands
         │              (BP1–BP10) per service per interval
         │              Respects: power limit, SoC, FCAS trapezium constraints
         │
         ▼  STEP 12 — Dashboard: 10-service prices, bid allocation,
         │              cumulative revenue, SoC, KPI summary
         │
         ▼  CSV Exports: per-service bid band files + combined + forecast + revenue
```

### Why This Approach

| Design Decision | Reason |
|----------------|--------|
| **10 FCAS markets (incl. VF 1-sec)** | Complete market coverage since Oct 2023 — VF services are highest $/MW for BESS |
| **Per-service models** | Each FCAS market has distinct price dynamics — shared model loses signal |
| **Cross-service features** | R1S ↔ R6S correlation, Raise/Lower ratio — captures market stress |
| **10-band bid output (BP1–BP10)** | Exact AEMO NEMDE bid format — submit directly via Bidding API |
| **Percentile-based band pricing** | Adapts to service-specific volatility — avoids flat bid inefficiency |
| **Weighted MW allocation** | 50% in low bands (guaranteed enablement) + 20% in spike bands (premium capture) |
| **Seasonal Anchor forecast** | Prevents recursive collapse over monthly horizon — preserves diurnal FCAS patterns |
| **Heuristic + LP dispatch** | Greedy allocation by price rank, constrained by SoC and trapezium |

---

## 🔊 NEM FCAS Markets — 10 Services

Since **9 October 2023**, the NEM operates **10 FCAS markets** — 8 contingency + 2 regulation.
The two **Very Fast (1-second)** services were added to address declining system inertia
as synchronous generators retire and inverter-based resources grow.

### Contingency Services (8 markets)

Respond **automatically** to sudden frequency disturbances (e.g. generator trip):

| # | Service | Short | Response | Direction | AEMO Column | Category |
|---|---------|-------|----------|-----------|-------------|----------|
| 1 | Very Fast Raise | **R1S** | **1 second** | Raise ↑ | `RAISE1SECRRP` | **Very Fast** |
| 2 | Fast Raise | R6S | 6 seconds | Raise ↑ | `RAISE6SECRRP` | Fast |
| 3 | Slow Raise | R60S | 60 seconds | Raise ↑ | `RAISE60SECRRP` | Slow |
| 4 | Delayed Raise | R5M | 5 minutes | Raise ↑ | `RAISE5MINRRP` | Delayed |
| 5 | Very Fast Lower | **L1S** | **1 second** | Lower ↓ | `LOWER1SECRRP` | **Very Fast** |
| 6 | Fast Lower | L6S | 6 seconds | Lower ↓ | `LOWER6SECRRP` | Fast |
| 7 | Slow Lower | L60S | 60 seconds | Lower ↓ | `LOWER60SECRRP` | Slow |
| 8 | Delayed Lower | L5M | 5 minutes | Lower ↓ | `LOWER5MINRRP` | Delayed |

### Regulation Services (2 markets)

**Continuously** track minor frequency deviations during normal operation:

| # | Service | Short | Direction | AEMO Column |
|---|---------|-------|-----------|-------------|
| 9 | Regulation Raise | RREG | Raise ↑ | `RAISEREGRRP` |
| 10 | Regulation Lower | LREG | Lower ↓ | `LOWERREGRRP` |

### Why Very Fast (R1S/L1S) Matters for BESS

| Aspect | Detail |
|--------|--------|
| **Response speed** | BESS responds in milliseconds — far faster than the 1-sec requirement |
| **Higher prices** | Fewer registered providers → scarcer supply → premium pricing |
| **System benefit** | Reduces the volume of Fast (R6S) FCAS needed → cheaper grid operation |
| **Market caps removed** | R1S cap (500 MW) removed 17 Feb 2025 · L1S cap (225 MW) removed 9 Sep 2024 |
| **Revenue uplift** | R1S adds **$15–40k/MW/year** on top of R6S revenue |

---

## 🎯 AEMO Bid Format — 10 Price-Quantity Bands (BP1–BP10)

Each FCAS bid submitted to AEMO consists of **exactly 10 price-quantity band pairs**.
NEMDE (the NEM Dispatch Engine) dispatches from the **cheapest band first**.

### Bid Band Structure (example: R1S at a single interval)

```
Band    Price ($/MWh)    Qty (MW)     Strategy
─────   ─────────────    ────────     ──────────────────────────────────
BP1     $0.00            20.0 MW      Floor — guaranteed enablement
BP2     $1.50            15.0 MW      Near-floor — very high enablement
BP3     $3.20            15.0 MW      Low cost — high enablement
BP4     $6.80            10.0 MW      Below median — selective
BP5     $12.40            8.0 MW      ≈ Forecast price — market clearing
BP6     $18.50            8.0 MW      Above median — higher margin
BP7     $28.00            7.0 MW      Premium zone
BP8     $45.00            7.0 MW      Spike capture — moderate
BP9     $85.00            5.0 MW      Spike capture — aggressive
BP10    $300.00           5.0 MW      Extreme spike — MPC approach
─────                   ────────
Total                   100.0 MW      = MaxAvailability for this service
```

### Bid Construction Mathematics

**Price bands** derived from forecast distribution percentiles:

```
λ_b = F⁻¹(p_b)     where p_b ∈ {0, 10, 20, 35, 50, 65, 80, 90, 95, 99}
```

**Quantity allocation** weights (sum = 1.0):

```
BP1–BP3:  50% of MaxAvail  →  high-confidence enablement
BP4–BP7:  30% of MaxAvail  →  selective dispatch at forecast price
BP8–BP10: 20% of MaxAvail  →  spike premium capture
```

**Constraints enforced per interval:**

- Prices monotonically ascending: λ₁ ≤ λ₂ ≤ … ≤ λ₁₀
- Quantities sum to MaxAvailability: Σ q_b = MaxAvail_s
- Price range: $0 to $16,600/MWh (Market Price Cap)
- Raise services limited by discharge headroom (SoC → E_min)
- Lower services limited by charge headroom (E_max → SoC)
- Total raise + lower + energy dispatch ≤ P_max (power limit)

---

## 🌏 NEM Regions Supported

| Region | State | FCAS Characteristics |
|--------|-------|---------------------|
| **SA1** | South Australia | Highest FCAS value · Most volatile frequency · Fastest BESS payback |
| **VIC1** | Victoria | Strong VF FCAS demand · Evening ramp stress · Interconnector effects |
| **NSW1** | New South Wales | Largest load · Moderate FCAS prices · Growing BESS fleet |
| **QLD1** | Queensland | Afternoon peaks · Solar ramp FCAS demand · Island risk premiums |
| **TAS1** | Tasmania | Hydro-dominated · Basslink contingency drives FCAS · Lowest volatility |

---

## 🔋 BESS Asset Configuration

Designed for **any utility-scale BESS** connected to the NEM. All parameters configurable in notebook cell 1:

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Technology | LFP | — | Lithium Iron Phosphate |
| Power | 100 MW | 10–500 MW | Rated charge/discharge power |
| Energy | 200 MWh | 20–2000 MWh | Nominal capacity |
| Duration | 2 h | 0.5–8 h | E/P ratio |
| Round-trip eff. | 90.25% | — | η_c × η_d = 0.95² |
| SoC window | 10–90% | 5–95% | Usable SoC range |
| Cycle life | 4,000 EFC | — | LFP at 80% DoD |
| CAPEX | $220/kWh | — | → $44M for 200 MWh |
| Cycle cost | ~$5.5/MWh | — | Marginal degradation |
| Break-even spread | ~$11.6/MWh | — | Min spread to profit |

---

## 📈 Expected Results

| Metric | Typical Value | KPI Target |
|--------|--------------|------------|
| FCAS forecast MAE (per service) | $3–15/MWh | < seasonal naive |
| R1S (Very Fast) MAE | $5–12/MWh | Best improvement vs baseline |
| RREG (Regulation) MAE | $3–8/MWh | Most predictable service |
| vs seasonal naive improvement | −25–45% MAE | Beat baseline for all 10 services |
| FCAS revenue share | 60–80% of total | ≥ 30% uplift vs energy-only |
| Total monthly revenue (SA1, 100MW) | $120k–350k | > $0 |
| Bid band feasibility | 100% | Zero constraint violations |
| Annualised $/MW/yr (FCAS only) | $15k–60k | Revenue stacking target |

---

## 🚀 Quick Start

```bash
# 1 — Clone
git clone https://github.com/YOUR_USERNAME/fcas-bidding-bot.git
cd fcas-bidding-bot

# 2 — Install
pip install -r requirements.txt

# 3 — Run notebook
jupyter lab FCAS_Bidding_Bot.ipynb
```

In cell 1, set your target:
```python
TARGET_YEAR   = 2025    # ← any year
TARGET_MONTH  = 1       # ← 1=Jan … 12=Dec
NEM_REGION    = 'SA1'   # ← SA1 | VIC1 | NSW1 | QLD1 | TAS1
TARGET_WEEK   = None    # ← None=full month, or 1-5 for specific week

# Enable/disable individual FCAS services:
FCAS_SERVICES = {
    'RAISE1SEC': True,   # R1S — Very Fast (1 sec) ← NEW Oct 2023
    'RAISE6SEC': True,   # R6S — Fast (6 sec)
    'RAISE60SEC': True,  # R60S — Slow (60 sec)
    'RAISE5MIN': True,   # R5M — Delayed (5 min)
    'RAISEREG':  True,   # RREG — Regulation
    'LOWER1SEC': True,   # L1S — Very Fast (1 sec) ← NEW Oct 2023
    'LOWER6SEC': True,   # L6S — Fast (6 sec)
    'LOWER60SEC': True,  # L60S — Slow (60 sec)
    'LOWER5MIN': True,   # L5M — Delayed (5 min)
    'LOWERREG':  True,   # LREG — Regulation
}
```
`Kernel → Restart & Run All`

---

## 🔄 Re-Forecast and Bid Generation

```python
# Re-forecast any month (models stay in memory, ~2-5 min):
r = quick_forecast(2025, 3)                          # March 2025 full month
r = quick_forecast(2025, 6, target_week=2)           # June 2025 week 2 only
r = quick_forecast(2025, 1, plot_date='2025-01-15')  # with specific day detail

# Plot any day (shows all 10 services + bid bands):
plot_day_detail('2025-01-15')  # prices, allocation, revenue, bid sample

# Access bid bands programmatically:
r['bid_bands']['RAISE1SEC']  # DataFrame with BP1–BP10 for R1S
r['revenue']                  # Revenue breakdown per service per interval
r['max_avail']                # MW allocated per service per interval
```

---

## 📤 Output Files — AEMO-Ready Bid Bands

The notebook exports **AEMO-format bid band files** ready for submission via the
NEM Dispatch Bidding API:

```
outputs/
│
├── bid_bands_R1S_SA1_202501.csv     ← Very Fast Raise: BP1–BP10 × 48 intervals/day
├── bid_bands_R6S_SA1_202501.csv     ← Fast Raise
├── bid_bands_R60S_SA1_202501.csv    ← Slow Raise
├── bid_bands_R5M_SA1_202501.csv     ← Delayed Raise
├── bid_bands_RREG_SA1_202501.csv    ← Regulation Raise
├── bid_bands_L1S_SA1_202501.csv     ← Very Fast Lower
├── bid_bands_L6S_SA1_202501.csv     ← Fast Lower
├── bid_bands_L60S_SA1_202501.csv    ← Slow Lower
├── bid_bands_L5M_SA1_202501.csv     ← Delayed Lower
├── bid_bands_LREG_SA1_202501.csv    ← Regulation Lower
│
├── bid_bands_ALL_SERVICES.csv        ← Combined: all 10 services in one file
├── fcas_price_forecast_10svc.csv     ← Price forecasts (10 services + energy)
├── fcas_revenue_10svc.csv            ← Revenue breakdown per service
├── max_availability.csv              ← MW allocated per service per interval
├── soc_trace.csv                     ← Battery state of charge
└── dashboard_fcas10.png              ← 6-panel dashboard image
```

Each **per-service bid band CSV** contains:

| Column | Description |
|--------|-------------|
| `BP1_price` … `BP10_price` | Band prices in $/MWh (ascending) |
| `BP1_qty` … `BP10_qty` | Band quantities in MW |
| `MaxAvail` | Total MW available for this service at this interval |
| `ForecastPrice` | ML-forecast clearing price for this service |

---

## 🌐 Bid Dashboard Web App

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
# All machines on local network: http://SERVER-IP:8501
```

See **DEPLOY.md** for full deployment options:
- Option A: Local network server (trading desk)
- Option B: Streamlit Community Cloud (free, internet)
- Option C: Docker (AWS / Azure / GCP)

---

## 📁 Repository Structure

```
fcas-bidding-bot/
│
├── FCAS_Bidding_Bot.ipynb           ← Main ML pipeline (12 steps, 10 FCAS services)
├── app.py                            ← Streamlit bid dashboard
│
├── data/                             ← NEMOSIS cache + synthetic data (auto-created)
├── outputs/                          ← Bid band CSVs, forecasts, dashboard images
├── models/                           ← Saved per-service models (after running notebook)
├── images/                           ← EDA plots, SHAP, error analysis
│
├── DEPLOY.md                         ← Deployment guide (3 options)
├── README.md                         ← This file
├── requirements.txt
├── environment.yml
├── .github/workflows/ci.yml
├── .gitignore
└── LICENSE
```

---

## 🏗️ Master ML/DL Framework — 12 Steps, 5 Phases

| Phase | Steps | What It Does |
|-------|-------|-------------|
| **Phase 0 — Foundations** | Step 1 | Problem formulation · Success criteria · BESS config · 10 bid band setup |
| **Phase 1 — Data** | Step 2 | NEMOSIS download (DISPATCHPRICE 10 FCAS + TRADINGPRICE energy) · Integrity |
| | Step 3 | EDA: diurnal patterns (10 svc), VF vs Fast, correlation, ACF, drift |
| | Step 4 | Temporal split · Test set LOCKED · TimeSeriesSplit CV |
| **Phase 2 — Representation** | Steps 5–6 | 70+ features/service · Cross-service VF↔Fast · RobustScaler · NaN-safe |
| **Phase 3 — Modelling** | Step 7 | Baselines: seasonal naive, rolling mean — per service |
| | Steps 8–9 | XGBoost + LightGBM per service · inverse-MAE ensemble · Optuna HPO |
| **Phase 4 — Evaluation** | Step 10 | SHAP (R1S focus) · error-by-hour · one-time test set (10 services) |
| **Phase 5 — Production** | Step 11 | Seasonal Anchor forecast · 10-band bid generation (BP1–BP10) |
| | Step 12 | 6-panel dashboard · CSV exports · bid band files · re-forecast function |

---

## ⚙️ Dependencies

| Package | Purpose |
|---------|---------|
| `numpy` `pandas` `scipy` | Core data processing |
| `scikit-learn` | RobustScaler pipeline, metrics, TimeSeriesSplit |
| `xgboost` `lightgbm` | Per-service FCAS price forecast models |
| `optuna` | Hyperparameter optimisation (optional) |
| `shap` | Feature interpretability (optional) |
| `nemosis` | Real AEMO NEM data download |
| `matplotlib` | Notebook plots (dark theme) |
| `plotly` `streamlit` | Interactive bid dashboard web app |

---

## 📡 Data Sources

| Source | Table | Resolution | Content |
|--------|-------|------------|---------|
| **AEMO NEMWEB** | `DISPATCHPRICE` | 5-min → resampled 30-min | 10 FCAS clearing prices (incl. R1S/L1S) |
| **AEMO NEMWEB** | `TRADINGPRICE` | 30-min | Energy RRP + total demand |
| **Synthetic fallback** | — | 30-min | High-fidelity simulated FCAS from energy signal |

- **Library**: NEMOSIS — `pip install nemosis` — open-source AEMO data downloader
- **License**: CC BY 4.0 — free to use with attribution
- **AEMO Bidding API**: `RAISE1SEC` / `LOWER1SEC` service types (JSON or FTP)

---

## 📚 References

1. AEMO. *National Electricity Market Data Model*. 2024.
2. AEMO. *Very Fast FCAS Market Transition*. 2023–2025.
3. AEMC. *Fast Frequency Response Market Ancillary Service — Final Determination*. July 2021.
4. AEMO. *Market Ancillary Service Specification (MASS) v8.0*. October 2023.
5. AEMO. *Guide to Energy and FCAS Offers* — 10 price-quantity band format.
6. AEMO. *Frequency Monitoring Quarterly Reports* — VF FCAS cap removal timeline.
7. Chen & Guestrin. XGBoost. *KDD* 2016.
8. Ke et al. LightGBM. *NeurIPS* 2017.
9. Akiba et al. Optuna. *KDD* 2019.
10. Lundberg & Lee. SHAP. *NeurIPS* 2017.
