FROM arm64v8/python:3.11-slim
WORKDIR /app
COPY modules/echo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY modules/echo/main.py .
COPY modules/echo/module.yaml .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
