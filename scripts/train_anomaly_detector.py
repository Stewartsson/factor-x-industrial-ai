import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import os

def run_ai_anomaly_detection():
    print("Loading factory baseline data...")
    # Load the baseline data we generated
    df = pd.read_csv('../data/baseline.csv')
    
    # We will focus on Motor 3, which we simulated as the degrading motor
    features = ['m3_energy_kwh', 'm3_temp_c', 'm3_vibration_mms']
    X = df[features]
    
    print("Training Unsupervised AI (Isolation Forest) on Motor-03 telemetry...")
    # Train Isolation Forest
    # Contamination is the expected proportion of outliers (we simulated it having issues, let's say 5% of the time it's critically bad)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    
    # Fit and Predict (-1 for anomaly, 1 for normal)
    df['anomaly_score'] = model.fit_predict(X)
    
    # Filter anomalies
    anomalies = df[df['anomaly_score'] == -1]
    print(f"\n--- AI DETECTION RESULTS ---")
    print(f"Total hours analyzed: {len(df)}")
    print(f"Anomalies detected: {len(anomalies)}")
    
    # Let's see what the average stats are for normal vs anomaly
    normal_stats = df[df['anomaly_score'] == 1][features].mean()
    anomaly_stats = anomalies[features].mean()
    
    print("\nAverage Metrics (Normal Operation):")
    print(f"Energy: {normal_stats['m3_energy_kwh']:.2f} kWh, Temp: {normal_stats['m3_temp_c']:.2f}°C, Vib: {normal_stats['m3_vibration_mms']:.2f} mm/s")
    
    print("\nAverage Metrics (AI Flagged Anomalies):")
    print(f"Energy: {anomaly_stats['m3_energy_kwh']:.2f} kWh, Temp: {anomaly_stats['m3_temp_c']:.2f}°C, Vib: {anomaly_stats['m3_vibration_mms']:.2f} mm/s")
    
    # Plotting the results
    print("\nGenerating AI Visualization...")
    plt.figure(figsize=(12, 6))
    
    # Plot normal points in blue
    plt.scatter(df.index[df['anomaly_score'] == 1], df['m3_temp_c'][df['anomaly_score'] == 1], 
                c='blue', label='Normal', alpha=0.5, s=20)
    
    # Plot anomalies in red
    plt.scatter(df.index[df['anomaly_score'] == -1], df['m3_temp_c'][df['anomaly_score'] == -1], 
                c='red', label='AI Detected Anomaly', edgecolors='black', s=50)
    
    plt.title("FACTOR-X AI: Motor-03 Temperature Anomaly Detection")
    plt.xlabel("Operating Hour (720 hrs / 30 days)")
    plt.ylabel("Motor Temperature (°C)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Ensure plots directory exists
    os.makedirs('../docs/plots', exist_ok=True)
    plot_path = '../docs/plots/anomaly_detection.png'
    plt.savefig(plot_path)
    print(f"Saved anomaly visualization to: {plot_path}")
    
    # Save anomalies to a separate CSV for the dashboard/report to use
    anomalies.to_csv('../data/ai_detected_anomalies.csv', index=False)
    print("Saved anomaly data to data/ai_detected_anomalies.csv")

if __name__ == "__main__":
    run_ai_anomaly_detection()
