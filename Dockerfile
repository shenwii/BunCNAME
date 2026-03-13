FROM python:3-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY records.json .

# Environment variables defaults
ENV PORKBUN_API_KEY=""
ENV PORKBUN_SECRET_KEY=""
ENV ADGUARD_HOME_URL=""
ENV ADGUARD_HOME_USERNAME=""
ENV ADGUARD_HOME_PASSWORD=""
ENV SYNC_INTERVAL="30"
ENV CONFIG_PATH="records.json"

# Run the application
CMD ["python", "main.py"]
