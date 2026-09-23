FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY loading-to-bq.py .

CMD ["python", "loading-to-bq.py"]