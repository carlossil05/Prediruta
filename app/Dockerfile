FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación, artefactos y modelos
COPY . .

# Exponer el puerto por defecto (8501 local / $PORT en Railway)
EXPOSE 8501

# Lanza la API en segundo plano y Streamlit
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run front/front_streamlit.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]