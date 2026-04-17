FROM python:3.11

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mostrador.py .
COPY templates.py .

EXPOSE 8002

CMD ["uvicorn", "mostrador:app", "--host", "0.0.0.0", "--port", "8002"]