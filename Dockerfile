# Usa una imagen base de Python 3.12.3 slim
FROM python:3.12.3-slim

# Evitar que Python genere archivos .pyc y para que el buffer sea inmediato
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requerimientos y luego instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# Exponer el puerto en el que se ejecutará la aplicación (por defecto 8000)
EXPOSE 8000

# Comando para iniciar el servidor Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
