# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Generate the data and train the AI model during the build process!
RUN cd scripts && python simulate_factory_data.py
RUN cd scripts && python train_anomaly_detector.py

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
