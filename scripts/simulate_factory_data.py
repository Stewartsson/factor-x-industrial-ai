import csv
import random
import math
from datetime import datetime, timedelta

def simulate_factory_data():
    start_time = datetime(2023, 10, 1, 0, 0, 0)
    hours_in_month = 720
    
    baseline_data = []
    optimized_data = []
    
    total_baseline_energy = 0
    total_optimized_energy = 0
    total_production = 0
    
    for hour in range(hours_in_month):
        timestamp = start_time + timedelta(hours=hour)
        
        # Factory runs mostly 8 AM to 8 PM, 2 shifts.
        is_working_hour = 8 <= timestamp.hour < 20
        
        # Base production unit
        if is_working_hour:
            prod_units = random.randint(10, 15)
        else:
            prod_units = random.randint(0, 2) # Minimal production night shift
            
        total_production += prod_units
        
        # Motor 1: Healthy motor
        m1_base = 15 if is_working_hour else 2
        m1_energy = m1_base + random.uniform(-1, 1) + (prod_units * 1.5)
        m1_temp = 45 + random.uniform(-2, 2) + (prod_units * 0.5)
        m1_vib = 1.2 + random.uniform(-0.1, 0.1)
        
        # Motor 2: Slightly inefficient
        m2_base = 18 if is_working_hour else 3
        m2_energy = m2_base + random.uniform(-1, 1) + (prod_units * 1.6)
        m2_temp = 55 + random.uniform(-3, 3) + (prod_units * 0.6)
        m2_vib = 2.5 + random.uniform(-0.2, 0.2)
        
        # Motor 3: Degrading motor (High friction, high idle energy)
        # This is where the AI finds the anomaly
        m3_base = 25 if is_working_hour else 12 # High idle power (Anomaly)
        m3_energy_baseline = m3_base + random.uniform(-2, 2) + (prod_units * 2.2)
        m3_temp = 75 + random.uniform(-5, 5) + (prod_units * 1.2) # High temp
        m3_vib = 4.8 + random.uniform(-0.5, 0.5) # High vibration
        
        # Calculate Total Baseline Energy for the hour
        total_energy_base = m1_energy + m2_energy + m3_energy_baseline + random.uniform(5, 10) # other loads
        total_baseline_energy += total_energy_base
        
        baseline_data.append([
            timestamp.isoformat(), prod_units, 
            m1_energy, m1_temp, m1_vib,
            m2_energy, m2_temp, m2_vib,
            m3_energy_baseline, m3_temp, m3_vib,
            total_energy_base
        ])
        
        # --- APPLY OPTIMIZATION INTERVENTION ---
        # 1. Motor 3 is serviced (bearing replaced, friction reduced) -> energy curve matches M1
        m3_base_opt = 15 if is_working_hour else 2
        m3_energy_opt = m3_base_opt + random.uniform(-1, 1) + (prod_units * 1.5)
        m3_temp_opt = 46 + random.uniform(-2, 2) + (prod_units * 0.5)
        m3_vib_opt = 1.3 + random.uniform(-0.1, 0.1)
        
        # 2. Smart Load Shifting (shifting some peak loads to night when grid is cheaper, but here we just reduce peak idling)
        total_energy_opt = m1_energy + m2_energy + m3_energy_opt + random.uniform(4, 8) 
        total_optimized_energy += total_energy_opt
        
        optimized_data.append([
            timestamp.isoformat(), prod_units, 
            m1_energy, m1_temp, m1_vib,
            m2_energy, m2_temp, m2_vib,
            m3_energy_opt, m3_temp_opt, m3_vib_opt,
            total_energy_opt
        ])
        
    # Write to CSV
    headers = [
        "timestamp", "production_units", 
        "m1_energy_kwh", "m1_temp_c", "m1_vibration_mms",
        "m2_energy_kwh", "m2_temp_c", "m2_vibration_mms",
        "m3_energy_kwh", "m3_temp_c", "m3_vibration_mms",
        "total_energy_kwh"
    ]
    
    with open("../data/baseline.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(baseline_data)
        
    with open("../data/optimized.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(optimized_data)
        
    # Calculate metrics
    sec_baseline = total_baseline_energy / total_production
    sec_optimized = total_optimized_energy / total_production
    improvement_pct = ((sec_baseline - sec_optimized) / sec_baseline) * 100
    
    print("--- FACTOR-X AI ENGINE REPORT ---")
    print(f"Total Production (Units): {total_production}")
    print(f"Baseline Energy: {total_baseline_energy:.2f} kWh")
    print(f"Optimized Energy: {total_optimized_energy:.2f} kWh")
    print(f"Baseline SEC: {sec_baseline:.2f} kWh/unit")
    print(f"Optimized SEC: {sec_optimized:.2f} kWh/unit")
    print(f"Energy Reduction: {improvement_pct:.2f}%")
    print("---------------------------------")

if __name__ == "__main__":
    simulate_factory_data()
