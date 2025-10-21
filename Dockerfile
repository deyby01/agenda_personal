# ============================================
# Dockerfile - Enterprise Production Ready
# ============================================

FROM python:3.11-slim

LABEL maintainer="Deyby Camacho <piedrahitadeyby@gmail.com>"
LABEL version="2.0.0"
LABEL description="Django Enterprise API with microservices architecture"

# Configurar variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=proyecto_agenda.settings

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Copiar y instalar dependencias Python
COPY requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/docker.txt

# Copiar código de la aplicación
COPY . .

# Cambiar ownership a usuario django
RUN chown -R django:django /app

# Cambiar a usuario no-root
USER django

# Exponer puerto 8000
EXPOSE 8000

# Healthcheck para monitoreo
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
