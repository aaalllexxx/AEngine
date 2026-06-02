# 🛡️ AEngine Security Demo

Интерактивное SPA-приложение для демонстрации возможностей модуля безопасности **AEngine `sec`**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)

> ✅ **Стенд использует НАСТОЯЩИЙ модуль `sec`.** Полезные нагрузки атак
> прогоняются через реальные детекторы IPS/IDS (`SQLiDetector`, `XSSDetector`,
> `LFIDetector`, `RCEDetector`, `SignatureDetector`), ограничение частоты — через
> реальный `RateLimiter`, а маскирование данных — через реальный middleware `DLP`.
> Логика защиты в стенде не дублируется: на экране вы видите результат самого `sec`.

---

## 📋 Содержание

- [Обзор](#-обзор)
- [Архитектура](#-архитектура)
- [Быстрый старт](#-быстрый-старт)
- [Docker](#-docker)
- [API-справочник](#-api-справочник)
- [Структура проекта](#-структура-проекта)
- [Скриншоты](#-скриншоты)

---

## 🔍 Обзор

Приложение предоставляет **три интерактивных вкладки**:

| Вкладка | Описание |
|---------|----------|
| ⚔️ **Attack Simulator** | Запуск симулированных атак (SQLi, XSS, LFI, RCE, DDoS, DLP, APT chain) и просмотр результатов детектирования в реальном времени |
| 🏗️ **Architecture** | Интерактивная SVG-схема конвейера безопасности с анимацией потока данных и описанием каждого компонента |
| 📊 **Metrics Dashboard** | Дашборд метрик: счётчики, donut-диаграмма, timeline графики, stress-test сравнение, журнал событий |

### Демонстрируемые компоненты `sec`

- **IPS / IDS** — система обнаружения/предотвращения вторжений
- **SQLiDetector** — обнаружение SQL-инъекций
- **XSSDetector** — обнаружение Cross-Site Scripting
- **LFIDetector** — обнаружение Local/Remote File Inclusion
- **RCEDetector** — обнаружение Remote Code Execution
- **SignatureDetector** — сигнатурный анализ (109 сигнатур из OWASP Core Rule Set)
- **RuleDetector** — правиловый анализ (пользовательские правила)
- **RateLimiter** — ограничитель частоты запросов (sliding window)
- **DLP** — предотвращение утечек данных (email, телефоны, паспорта)

Компоненты ниже показаны на вкладке «Архитектура» (с примерами API и кода):

- **OSProtection** — мониторинг ресурсов ОС
- **AdvancedSystemProtection** — фоновый сканер процессов и конфигурации
- **Code Signer**, **HA Cluster** — контроль целостности кода и отказоустойчивость

---

## 🏗️ Архитектура

```
┌──────────────────────────────────────────────────────────┐
│                    Browser (SPA)                         │
│  ┌─────────────┬─────────────────┬────────────────────┐  │
│  │   Attacks    │  Architecture   │     Metrics        │  │
│  │  (attacks.js)│(architecture.js)│   (metrics.js)     │  │
│  └──────┬───────┴────────┬────────┴─────────┬─────────┘  │
│         └────────────────┼──────────────────┘            │
│                          │ fetch API                     │
└──────────────────────────┼───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│                     Flask / AEngineApps                   │
│  ┌───────────────────────┼────────────────────────────┐  │
│  │              API Endpoints (app.py)                │  │
│  │  /api/attacks/catalog  /api/attack/run             │  │
│  │  /api/attack/flood     /api/attack/dlp-test        │  │
│  │  /api/attack/chain     /api/metrics/*              │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────┼────────────────────────────┐  │
│  │          sec module (РЕАЛЬНЫЙ код)                  │  │
│  │  Detectors → RateLimiter → DLP  (через request ctx)│  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │       GlobalStorage (metrics, logs, state)         │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10+
- Модули `AEngineApps` и `sec` в PYTHONPATH или в родительском каталоге

> ℹ️ **Зависимости (`flask`, `psutil`, `pywebview`, `rich`).** `pywebview` обязателен:
> фреймворк `AEngineApps` импортирует `webview` на уровне модуля, поэтому он нужен
> даже несмотря на то, что стенд работает в web-режиме и окно webview не открывает.
> `rich` тоже обязателен: модуль `sec` тянет его при импорте (`sec/logging.py`).

### Установка и запуск

```bash
# Из корня проекта AEngine:
cd security-demo

# Установка зависимостей
pip install -r requirements.txt

# Запуск
python app.py
```

> 🔄 **Авто-установка.** При прямом запуске (`python app.py`) стенд сам доустановит
> недостающие зависимости из `requirements.txt` — свежий клон поднимается «из коробки».
> Отключить можно переменной `AENGINE_NO_AUTO_INSTALL=1` (в Docker она выставлена,
> т.к. зависимости уже установлены на этапе сборки образа).

Приложение запустится на **http://localhost:5050**

### Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `HOST` | `0.0.0.0` | Интерфейс прослушивания |
| `PORT` | `5050` | Порт сервера |
| `DEBUG` | `false` | Режим отладки Flask (`true`/`1`/`yes` для включения) |
| `SECRET_KEY` | `security-demo-secret-key` | Секретный ключ сессий |
| `AENGINE_NO_AUTO_INSTALL` | `false` | `1`/`true`/`yes` — отключить авто-установку зависимостей при запуске |

---

## 🐳 Docker

### Сборка и запуск через docker-compose

```bash
cd security-demo
docker-compose up --build
```

### Только сборка образа

```bash
cd security-demo
docker build -t aengine-security-demo .
docker run -p 5050:5050 \
  -v $(pwd)/../AEngineApps:/app/AEngineApps:ro \
  -v $(pwd)/../sec:/app/sec:ro \
  aengine-security-demo
```

Healthcheck проверяет `/health` каждые 30 секунд.

---

## 📡 API-справочник

### Атаки

| Метод | Путь | Тело запроса | Описание |
|-------|------|--------------|----------|
| `GET` | `/api/attacks/catalog` | — | Каталог всех типов атак с пейлоадами |
| `POST` | `/api/attack/run` | `{attack_type, payload}` | Прогон payload через реальный детектор `sec` |
| `POST` | `/api/attack/flood` | `{count, interval_ms}` | DDoS-симуляция через реальный `RateLimiter` |
| `GET` | `/api/attack/dlp-test` | — | Прогон ответа через реальный DLP middleware |
| `POST` | `/api/attack/chain` | `{}` | APT-цепочка (LFI→RCE→Exfil) |

`attack_type` — один из: `sqli`, `xss`, `lfi`, `rce`, `cve`.

### Метрики

| Метод | Путь | Тело запроса | Описание |
|-------|------|--------------|----------|
| `GET` | `/api/metrics/summary` | — | Сводка: `total_attacks`, `blocked`, `passed`, `by_type`, `block_rate` |
| `GET` | `/api/metrics/system` | — | Системные метрики: `cpu_percent`, `ram_percent`, `connections`, `disk_percent` |
| `GET` | `/api/metrics/logs?limit=N` | — | Журнал событий (по умолчанию 100) |
| `POST` | `/api/metrics/stress-test` | `{with_rate_limiter, requests}` | Сравнительный нагрузочный тест (визуализация) |
| `POST` | `/api/metrics/reset` | `{}` | Сброс всех метрик |
| `GET` | `/health` | — | Health-check для Docker/балансировщиков |

### Пример запроса

```bash
# Получить каталог атак
curl http://localhost:5050/api/attacks/catalog

# Запустить SQL-инъекцию (вернёт blocked=true, detector=SQLiDetector)
curl -X POST http://localhost:5050/api/attack/run \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "sqli", "payload": "1 OR 1=1 --"}'

# DLP-тест (вернёт ответ с удалёнными email/телефонами/паспортами)
curl http://localhost:5050/api/attack/dlp-test

# Нагрузочный тест
curl -X POST http://localhost:5050/api/metrics/stress-test \
  -H "Content-Type: application/json" \
  -d '{"with_rate_limiter": true, "requests": 300}'
```

---

## 📁 Структура проекта

```
security-demo/
├── app.py                      # Бэкенд: API-эндпоинты, инициализация sec
├── requirements.txt            # Python-зависимости
├── Dockerfile                  # Docker-образ
├── docker-compose.yml          # Оркестрация с монтированием модулей
├── README.md                   # Документация (этот файл)
├── templates/
│   └── index.html              # SPA-шаблон (единственная HTML-страница)
└── static/
    ├── css/
    │   └── style.css           # Тёмная тема, адаптивная вёрстка
    └── js/
        ├── app.js              # SPA-роутер, API-хелперы, утилиты
        ├── attacks.js          # Вкладка «Attack Simulator»
        ├── architecture.js     # Вкладка «Architecture» (SVG-схема)
        └── metrics.js          # Вкладка «Metrics Dashboard» (Canvas-графики)
```

---

## 🖥️ Технологии

- **Backend**: Python, Flask, AEngineApps framework, sec module
- **Frontend**: Vanilla JS (ES6+), CSS3 Custom Properties, Canvas API, SVG
- **Без внешних библиотек** — никаких React, jQuery, Bootstrap, Chart.js
- **Docker**: Python 3.11-slim, healthcheck, volume mounts

---

## 📝 Лицензия

Часть проекта AEngine. Распространяется под лицензией MIT.
