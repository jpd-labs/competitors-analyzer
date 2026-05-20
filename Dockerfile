FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY .streamlit/config.toml .streamlit/config.toml   # ← añadir esta línea

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]   # ← simplificar, el config.toml ya tiene todo