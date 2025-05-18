FROM python:3.12-slim

ENV PYTHONPATH=/app
# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos y el código de la aplicación
COPY requirements.txt requirements.txt
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
