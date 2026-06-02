FROM python:3.11-slim

LABEL maintainer="AEngine Team"
LABEL description="AEngine Security Demo — интерактивная демонстрация модуля безопасности"

WORKDIR /app

# psutil и pywebview ставятся из готовых wheel'ов на debian-slim — сборочные
# инструменты не нужны (в отличие от alpine, где требовалась компиляция).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем AEngineApps и sec из родительского контекста (см. docker-compose)
# Эти модули монтируются через volumes в docker-compose.yml

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
# Зависимости уже установлены на этапе сборки — отключаем авто-установку в рантайме.
ENV AENGINE_NO_AUTO_INSTALL=1

EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050/health')" || exit 1

CMD ["python", "main.py"]
