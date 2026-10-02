from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import json
import asyncio
import os

app = FastAPI(title="FACTOR-X Industrial API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Allow CORS for the local HTML dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data(filename):
    try:
        filepath = os.path.join(BASE_DIR, "data", filename)
        df = pd.read_csv(filepath)
        # For the chart, we only need daily aggregates to keep it fast
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily = df.groupby('date')['total_energy_kwh'].sum().reset_index()
        return {
            "labels": daily['date'].astype(str).tolist(),
            "data": daily['total_energy_kwh'].round(2).tolist(),
            "total": round(df['total_energy_kwh'].sum(), 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"status": "FACTOR-X API is running"}

@app.get("/api/energy/baseline")
def get_baseline_energy():
    return load_data("baseline.csv")

@app.get("/api/energy/optimized")
def get_optimized_energy():
    return load_data("optimized.csv")

@app.get("/api/anomalies")
def get_anomalies():
    try:
        filepath = os.path.join(BASE_DIR, "data", "ai_detected_anomalies.csv")
        df = pd.read_csv(filepath)
        # Return the latest 5 anomalies
        latest = df.tail(5)
        anomalies = []
        for _, row in latest.iterrows():
            anomalies.append({
                "timestamp": row['timestamp'],
                "motor": "Motor-03",
                "temp": round(row['m3_temp_c'], 1),
                "energy": round(row['m3_energy_kwh'], 1),
                "vibration": round(row['m3_vibration_mms'], 2)
            })
        return {"anomalies": anomalies}
    except:
        return {"anomalies": []}

@app.get("/api/metrics")
def get_metrics():
    baseline = load_data("baseline.csv")
    optimized = load_data("optimized.csv")
    
    # We know production is 4853 from our simulation
    total_prod = 4853
    
    if "error" in baseline:
        return {"error": "Data not found"}
        
    sec_base = baseline["total"] / total_prod
    sec_opt = optimized["total"] / total_prod
    
    reduction_pct = ((sec_base - sec_opt) / sec_base) * 100
    
    return {
        "total_energy_optimized": optimized["total"],
        "sec_optimized": round(sec_opt, 2),
        "reduction_pct": round(reduction_pct, 1),
        "co2_offset_tons": round((baseline["total"] - optimized["total"]) * 0.0007, 1) # 0.0007 tons/kWh average grid emission factor
    }

async def live_data_generator():
    try:
        base_path = os.path.join(BASE_DIR, "data", "baseline.csv")
        anom_path = os.path.join(BASE_DIR, "data", "ai_detected_anomalies.csv")
        
        df = pd.read_csv(base_path)
        anomalies_df = pd.read_csv(anom_path)
        anomaly_times = set(anomalies_df['timestamp'].tolist())
        
        while True:
            for _, row in df.iterrows():
                is_anomaly = row['timestamp'] in anomaly_times
                data_point = {
                    "timestamp": row['timestamp'],
                    "energy": round(row['total_energy_kwh'], 1),
                    "m3_temp": round(row['m3_temp_c'], 1),
                    "m3_vib": round(row['m3_vibration_mms'], 2),
                    "is_anomaly": is_anomaly
                }
                yield f"data: {json.dumps(data_point)}\n\n"
                await asyncio.sleep(0.5) # Simulate live data every 500ms
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/api/stream")
async def stream_live_data():
    return StreamingResponse(live_data_generator(), media_type="text/event-stream")

# Serve the dashboard files directly (makes Cloud Deployment 1-click)
dashboard_path = os.path.join(BASE_DIR, "dashboard")
app.mount("/", StaticFiles(directory=dashboard_path, html=True), name="dashboard")
