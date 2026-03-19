фреймворк
# 🚀 AEngine Production Enterprise Guide

Руководство по использованию AEngine в production enterprise окружении.

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Async vs Sync](#async-vs-sync)
3. [Production Checklist](#production-checklist)
4. [Мониторинг и метрики](#мониторинг-и-метрики)
5. [Безопасность](#безопасность)
6. [Масштабирование](#масштабирование)
7. [CI/CD](#cicd)

---

## Быстрый старт

### Синхронное приложение (простые проекты)

```python
from AEngineApps.app import App

app = App("MyApp")
app.load_config("config.json")
app.run()
```

### Асинхронное приложение (production enterprise)

```python
from AEngineApps.async_app import AsyncApp

app = AsyncApp("MyApp")
app.load_config("config.json")

# Production features
app.enable_health_endpoint()
app.enable_metrics_endpoint()

app.run()
```

**Разница:** Просто замените `App` на `AsyncApp` и `Screen` на `AsyncScreen`. Добавьте `async/await` к методам.

---

## Async vs Sync

### Когда использовать Async (AsyncApp)?

✅ **Используйте AsyncApp если:**
- Высокая нагрузка (>1000 RPS)
- Много I/O операций (БД, API, файлы)
- Нужны WebSocket или SSE
- Enterprise production окружение
- Требуется горизонтальное масштабирование

❌ **Используйте обычный App если:**
- Простой проект или прототип
- Низкая нагрузка (<100 RPS)
- Нет опыта с async/await
- Desktop приложение (webview)

### Миграция с Sync на Async

**Было (Sync):**
```python
from AEngineApps.app import App
from AEngineApps.screen import Screen

class HomeScreen(Screen):
    route = "/"
    
    def run(self):
        data = db.query("SELECT * FROM users")
        return self.render("index.html", users=data)

app = App()
app.add_screen("/", HomeScreen)
app.run()
```

**Стало (Async):**
```python
from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen

class HomeScreen(AsyncScreen):
    route = "/"
    
    async def run(self):  # Добавили async
        data = await db.query("SELECT * FROM users")  # Добавили await
        return await self.render("index.html", users=data)  # Добавили await

app = AsyncApp()
app.add_screen("/", HomeScreen)
app.run()
```

**Изменения:** Добавили `async` перед `def` и `await` перед I/O операциями. Всё!

---

## Production Checklist

### ✅ Обязательно перед деплоем

- [ ] `debug = false` в config.json
- [ ] Установлен `secret_key` (минимум 32 символа)
- [ ] Настроен HTTPS (SSL/TLS сертификат)
- [ ] Включен health check endpoint
- [ ] Настроен мониторинг (Prometheus/Grafana)
- [ ] Логирование в файл (не в stdout)
- [ ] Настроен reverse proxy (Nginx/Caddy)
- [ ] Ограничение rate limit (sec модуль)
- [ ] Backup стратегия для БД
- [ ] Документация API (Swagger/OpenAPI)

### config.json для production

```json
{
  "debug": false,
  "host": "0.0.0.0",
  "port": 8000,
  "secret_key": "your-super-secret-key-min-32-chars",
  "view": "web",
  "workers": 4,
  "max_requests": 1000,
  "timeout": 30,
  "ssl_cert": "/path/to/cert.pem",
  "ssl_key": "/path/to/key.pem"
}
```

---

## Мониторинг и метрики

### Health Checks

```python
from AEngineApps.async_app import AsyncApp

app = AsyncApp()

# Добавляем проверки
@app.add_health_check
async def check_database():
    try:
        await db.ping()
        return (True, "Database OK")
    except Exception as e:
        return (False, f"Database error: {e}")

@app.add_health_check
def check_redis():
    try:
        redis.ping()
        return (True, "Redis OK")
    except:
        return (False, "Redis unavailable")

# Включаем endpoint
app.enable_health_endpoint("/health")  # GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "checks": [
    {"healthy": true, "message": "Database OK"},
    {"healthy": true, "message": "Redis OK"}
  ],
  "metrics": {
    "requests": 15234,
    "errors": 12
  }
}
```

### Prometheus метрики

```python
app.enable_metrics_endpoint("/metrics")  # GET /metrics
```

**Интеграция с Prometheus:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'aengine_app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## Безопасность

### Базовая защита (sec модуль)

```python
from AEngineApps.async_app import AsyncApp
from sec.intrusions import IPS, SQLiDetector, XSSDetector, RateLimiter
from sec.sys_protect import AdvancedSystemProtection

app = AsyncApp()

# 1. Rate limiting (анти-DDoS)
RateLimiter(app, max_requests=100, window=60)

# 2. IPS (блокировка атак)
ips = IPS(app)
ips.add_detector(SQLiDetector)
ips.add_detector(XSSDetector)

# 3. Системная защита
AdvancedSystemProtection(app)

app.run()
```

### HTTPS (обязательно для production)

**Вариант 1: Nginx reverse proxy (рекомендуется)**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Вариант 2: Встроенный SSL (для тестирования)**
```python
app.quart.run(
    host="0.0.0.0",
    port=443,
    certfile="cert.pem",
    keyfile="key.pem"
)
```

---

## Масштабирование

### Горизонтальное (несколько серверов)

**Docker Compose:**
```yaml
version: '3.8'
services:
  app:
    image: myapp:latest
    deploy:
      replicas: 4
    ports:
      - "8000-8003:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

### Вертикальное (один сервер, много процессов)

**Используйте LocalCluster из sec модуля:**
```python
from AEngineApps.async_app import AsyncApp
from sec.auto_cluster import LocalCluster

app = AsyncApp()

# Запускает 4 процесса на портах 8000-8003
cluster = LocalCluster(app, ports=[8000, 8001, 8002, 8003])
cluster.run()
```

**Или Gunicorn:**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app.quart
```

---

## CI/CD

### GitHub Actions пример

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app
            git pull
            docker-compose up -d --build
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

---

## 🎯 Рекомендации

### Для малых проектов (<1000 пользователей)
- Используйте обычный `App` (синхронный)
- Один сервер с Nginx
- Базовая защита из sec модуля
- SQLite или PostgreSQL

### Для средних проектов (1000-10000 пользователей)
- Используйте `AsyncApp`
- LocalCluster (4-8 процессов)
- Полная защита sec модуля
- PostgreSQL + Redis
- Health checks + метрики

### Для крупных проектов (>10000 пользователей)
- `AsyncApp` + Docker + Kubernetes
- Горизонтальное масштабирование (10+ серверов)
- Load balancer (Nginx/HAProxy)
- PostgreSQL cluster + Redis cluster
- Полный мониторинг (Prometheus + Grafana + ELK)
- CDN для статики

---

## 📞 Поддержка

- GitHub Issues: https://github.com/yourusername/AEngine/issues
- Документация: https://aengine.readthedocs.io
- Telegram: @aengine_support

**Помните: Удобство пользователя = Простота + Мощность**
