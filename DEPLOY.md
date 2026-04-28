# 🚀 Deployment Guide — FCAS Bidding Bot

Three deployment options for the FCAS Bidding Bot web app.

---

## Option 1: Local / LAN

```bash
# Install dependencies
pip install -r requirements.txt

# Run the notebook first to generate models and outputs
jupyter nbconvert --execute FCAS_Bidding_Bot.ipynb

# Launch web app
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Access:
#   Local:  http://localhost:8501
#   LAN:    http://<your-ip>:8501
```

---

## Option 2: Streamlit Community Cloud

1. Push to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/FCAS_Bidding_Bot.git
   git branch -M main
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo → set `app.py` as main file
4. Deploy

> **Note:** You must include pre-computed CSV outputs in `outputs/` for the app to work
> on Streamlit Cloud (no notebook execution on the server).

---

## Option 3: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

Build and run:
```bash
docker build -t fcas-bidding-bot .
docker run -p 8501:8501 fcas-bidding-bot
```

---

## Pre-requisites

Before deploying, ensure you have:
1. Run the notebook to generate `outputs/` and `models/` directories
2. All CSV files in `outputs/` (forecast, bids, revenue, soc)
3. Trained models in `models/fcas_models.pkl`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_SERVER_PORT` | 8501 | Web app port |
| `STREAMLIT_SERVER_ADDRESS` | 0.0.0.0 | Bind address |
