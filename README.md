# AEngine - Полнофункциональная Экосистема для Разработки Web и Desktop Приложений

<div align="center">

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%20--%203.14-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Современный, объектно-ориентированный фреймворк для создания защищенных веб-приложений с встроенным менеджером пакетов и модулем безопасности**

[Быстрый старт](#-быстрый-старт) • [Документация](#-документация) • [Примеры](#-примеры) • [Безопасность](#-безопасность) • [Развертывание](#-развертывание)

</div>

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Ключевые возможности](#-ключевые-возможности)
- [Архитектура](#-архитектура)
- [Быстрый старт](#-быстрый-старт)
- [Компоненты экосистемы](#-компоненты-экосистемы)
- [Документация](#-документация)
- [Примеры использования](#-примеры-использования)
- [Безопасность](#-безопасность)
- [Развертывание](#-развертывание)
- [Тестирование](#-тестирование)
- [Участие в разработке](#-участие-в-разработке)
- [Лицензия](#-лицензия)

---

## 🎯 О проекте

**AEngine** — это репозиторий-агрегатор и документация для экосистемы разработки современных веб-приложений на Python.

### Компоненты экосистемы

- **AEngineApps** — легковесный OOP-фреймворк без декораторов (независимый проект)
- **APM** (AEngine Package Manager) — мощный менеджер проектов и модулей (независимый проект)
- **sec** — модуль комплексной безопасности (IDS/IPS, DLP, кластеризация, dashboard)


### Философия проекта

1. **Чистая архитектура** — полный отказ от декораторов Flask в пользу классов
2. **Безопасность** — возможность установки дополнительных модулей безопасности
3. **Простота использования** — интуитивный API и автоматизация рутинных задач
4. **Масштабируемость** — от прототипа до production с кластеризацией
5. **Кроссплатформенность** — Windows, Linux, macOS
6. **Модульность** — независимые компоненты, устанавливайте только то, что нужно

---

## ✨ Ключевые возможности

### AEngineApps Framework

- ✅ **Объектно-ориентированная архитектура** — классы Screen вместо декораторов
- ✅ **Автоматическая маршрутизация** — сканирование папки screens/
- ✅ **REST API из коробки** — класс API с автоматической сериализацией JSON
- ✅ **Микросервисная архитектура** — изолированные Service с собственными middleware
- ✅ **WebView и Web режимы** — десктопные и веб-приложения из одного кода
- ✅ **Асинхронная поддержка** — async/await для высоконагруженных приложений
- ✅ **Lifecycle hooks** — before_request, after_request, on_start, on_stop
- ✅ **Глобальное хранилище** — GlobalStorage для обмена данными между модулями
- ✅ **JSON конфигурация** — JsonDict для удобной работы с настройками

### APM (Package Manager)

- 📦 **Управление проектами** — create, init, delete, run, config
- 🔄 **Управление модулями** — install, remove, update из Git
- 🧭 **Навигация** — list, goto, select для быстрого переключения
- 🛠️ **Генераторы кода** — develop module/screen для шаблонов
- 📚 **Автодокументация** — docs для быстрого доступа
- 🔌 **Система плагинов** — расширение APM через subcommands
- 🚀 **Автообновление** — upgrade для фреймворка, update для APM


---

## 🏗️ Архитектура

```
AEngine/
├── AEngineApps/          # Основной фреймворк (submodule)
│   ├── __init__.py       # Инициализация пакета
│   ├── app.py            # Класс App (ядро приложения)
│   ├── screen.py         # Базовый класс Screen
│   ├── api.py            # Класс API для REST
│   ├── service.py        # Класс Service для микросервисов
│   ├── global_storage.py # Глобальное хранилище (Singleton)
│   └── json_dict.py      # Обертка над JSON файлами
│
├── APM/                  # Менеджер пакетов (submodule)
│   ├── modules/          # Команды APM
│   │   ├── create.py     # Создание проектов
│   │   ├── install.py    # Установка модулей
│   │   └── ...
│   └── scripts/          # Установочные скрипты
│
├── sec/                  # Модуль безопасности (submodule)
│   ├── intrusions.py     # IDS/IPS система
│   ├── dlp.py            # Data Loss Prevention
│   ├── cluster.py        # Кластеризация
│   ├── dashboard.py      # Security Dashboard
│   ├── auth.py           # Аутентификация
│   └── AEngineApps/      # Интеграция с фреймворком
│
├── tests/                # Тесты (105 тестов)
├── main.py               # Единая точка входа
├── .dockerignore         # Docker ignore
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile            # Docker образ
├── nginx.conf            # Nginx конфигурация
├── QUICK_START.md        # Быстрый старт
├── PRODUCTION_GUIDE.md   # Руководство по production
└── CHANGELOG.md          # История изменений
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (для установки модулей)

### Установка

#### 1. Клонирование репозитория

AEngine использует Git submodules для AEngineApps, APM и sec. Клонируйте с автоматической инициализацией submodules:

```bash
# Клонирование с submodules
git clone --recursive https://github.com/aaalllexxx/AEngine.git
cd AEngine
```

Если вы уже клонировали без `--recursive`, инициализируйте submodules:

```bash
# Windows
init_submodules.bat

# Linux/macOS
chmod +x init_submodules.sh
./init_submodules.sh

# Или вручную
git submodule update --init --recursive
```

📖 **Подробнее о Git submodules:** см. [GIT_SETUP.md](GIT_SETUP.md)

#### 2. Установка APM (Package Manager)

**Windows:**
```cmd
cd APM\scripts
setup.bat
```

**Linux/macOS:**
```bash
cd APM/scripts
chmod +x setup.sh
./setup.sh
```

После установки команда `apm` будет доступна глобально.

#### 3. Создание первого проекта

```bash
# Создать новый проект
apm create

# Следуйте интерактивным подсказкам:
# - Введите имя проекта: MyFirstApp
# - Выберите путь: ./MyFirstApp
# - Выберите режим: web
```

#### 4. Запуск проекта

```bash
cd MyFirstApp
apm run
```

Откройте браузер: `http://localhost:5000`

### Первое приложение (Hello World)

**main.py:**
```python
from AEngineApps.app import App

app = App("HelloWorld")
app.load_config("config.json")

if __name__ == "__main__":
    app.run()
```

**screens/home.py:**
```python
from AEngineApps.screen import Screen

class HomeScreen(Screen):
    route = "/"
    methods = ["GET"]
    
    def run(self):
        return self.render("index.html", message="Hello, AEngine!")
```

**templates/index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello AEngine</title>
</head>
<body>
    <h1>{{ message }}</h1>
</body>
</html>
```

**config.json:**
```json
{
    "debug": true,
    "view": "web",
    "host": "127.0.0.1",
    "port": 5000,
    "screen_path": "screens",
    "routers": "auto"
}
```

---

## 🧩 Компоненты экосистемы

### 1. AEngineApps Framework

Легковесный фреймворк для создания веб-приложений с чистой OOP архитектурой.

**Основные классы:**
- `App` — ядро приложения, управление маршрутами и lifecycle
- `Screen` — базовый класс для контроллеров/страниц
- `API` — специализированный класс для REST API
- `Service` — микросервисная архитектура с изоляцией
- `GlobalStorage` — глобальное хранилище (Singleton)
- `JsonDict` — удобная работа с JSON файлами

📖 [Полная документация AEngineApps](AEngineApps/readme.md)

### 2. APM (AEngine Package Manager)

Мощный CLI инструмент для управления проектами и модулями.

**Основные команды:**

| Команда | Описание |
|---------|----------|
| `apm create` | Создать новый проект |
| `apm init` | Инициализировать существующую папку |
| `apm run` | Запустить проект |
| `apm install <url>` | Установить модуль из Git |
| `apm list` | Показать все проекты |
| `apm goto` | Перейти в папку проекта |
| `apm config` | Настроить config.json |
| `apm build` | Собрать в .exe (PyInstaller) |
| `apm upgrade` | Обновить фреймворк |
| `apm update` | Обновить APM |

📖 [Полная документация APM](APM/readme.md)


---

## 📚 Документация

### Основная документация

- [Быстрый старт](QUICK_START.md) — начало работы за 5 минут
- [Руководство по production](PRODUCTION_GUIDE.md) — развертывание в production
- [История изменений](CHANGELOG.md) — все версии и обновления

### Документация компонентов

- [AEngineApps Framework](AEngineApps/readme.md) — полное руководство по фреймворку
- [APM Package Manager](APM/readme.md) — все команды и возможности

### Дополнительная документация

- [Архитектура проекта](ARCHITECTURE.md) — детальное описание архитектуры
- [API Reference](API_REFERENCE.md) — справочник по всем классам и методам
- [Руководство разработчика](DEVELOPER_GUIDE.md) — как участвовать в разработке
- [Security Demo](security-demo/README.md) — интерактивный демо-стенд модуля безопасности

---

## 💡 Примеры использования

### Пример 1: Простое веб-приложение

```python
from AEngineApps.app import App
from AEngineApps.screen import Screen

class HomeScreen(Screen):
    route = "/"
    
    def run(self):
        return self.render("index.html")

class AboutScreen(Screen):
    route = "/about"
    
    def run(self):
        return self.render("about.html")

app = App("SimpleApp")
app.load_config("config.json")
app.run()
```

### Пример 2: REST API

```python
from AEngineApps.app import App
from AEngineApps.api import API

class UsersAPI(API):
    route = "/api/users"
    methods = ["GET", "POST"]
    
    def get(self):
        # GET /api/users?limit=10
        limit = self.get_arg("limit", int, 10)
        users = database.get_users(limit)
        return {"users": users}
    
    def post(self):
        # POST /api/users с JSON телом
        ok, missing = self.require_keys(["name", "email"])
        if not ok:
            return {"error": f"Missing: {missing}"}, 400
        
        data = self.request.json
        user_id = database.create_user(data)
        return {"id": user_id, "status": "created"}, 201

app = App("API_App")
app.load_config("config.json")
app.run()
```

### Пример 3: Микросервисная архитектура

```python
from AEngineApps.app import App
from AEngineApps.service import Service
from AEngineApps.api import API

# Сервис аутентификации
auth_service = Service("auth", prefix="/api/auth")

class LoginAPI(API):
    methods = ["POST"]
    
    def post(self):
        ok, missing = self.require_keys(["username", "password"])
        if not ok:
            return {"error": "Invalid credentials"}, 400
        
        token = auth.generate_token(self.request.json)
        return {"token": token}

auth_service.add_screen("/login", LoginAPI)

# Главное приложение
app = App("MicroserviceApp")
app.register_service(auth_service)
app.run()
```

### Пример 4: Асинхронное приложение

```python
from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen
import asyncio

class AsyncHomeScreen(AsyncScreen):
    route = "/"
    
    async def run(self):
        # Асинхронные операции
        data = await fetch_data_from_api()
        result = await process_data(data)
        return self.render("index.html", result=result)

app = AsyncApp("AsyncApp")
app.load_config("config.json")
app.run()
```

📁 [Интерактивный демо-стенд модуля безопасности](security-demo/README.md)

---

## 🔒 Безопасность

AEngine поддерживает установку дополнительных модулей безопасности через APM. Вы можете создавать собственные модули или использовать готовые решения из сообщества.

### Отчеты о безопасности

Если вы обнаружили уязвимость в AEngine, пожалуйста, сообщите об этом по адресу: security@aengine.dev

---

## 🚢 Развертывание

### Docker

```bash
# Сборка образа
docker build -t aengine-app .

# Запуск контейнера (порт 8000)
docker run -p 8000:8000 aengine-app
```

### Docker Compose

```bash
# Запуск с Nginx, Redis и PostgreSQL
docker-compose up -d
```

### Hypercorn (production)

`main.py` экспортирует ASGI-приложение `asgi_app` (WSGI→ASGI адаптер) — именно
оно запускается в Docker:

```bash
# Установка зависимостей
pip install hypercorn asgiref

# Запуск
hypercorn main:asgi_app --bind 0.0.0.0:8000 --workers 4
```

> Альтернатива (WSGI): `gunicorn -w 4 -b 0.0.0.0:8000 "main:app.flask"` на Linux.

### Systemd Service (Linux)

```ini
[Unit]
Description=AEngine Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

📖 [Полное руководство по развертыванию](PRODUCTION_GUIDE.md)

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Установка pytest
pip install pytest pytest-cov

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=AEngineApps --cov=APM --cov=sec

# Запуск конкретного теста
pytest tests/test_app.py
```

### Структура тестов

```
tests/
├── conftest.py              # Фикстуры pytest
├── test_app.py              # App, Screen, API, Service, GlobalStorage, JsonDict
├── test_async_app.py        # Асинхронные приложения
├── test_main.py             # Точка входа main.py
└── test_security.py         # Модуль sec: DLP, детекторы IDS/IPS, ClusterNode
```

---

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта!

### Как внести вклад

1. Fork репозитория
2. Создайте ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Правила разработки

- Стремитесь следовать PEP 8 для Python кода (пока не строго)
- Пишите docstrings для всех публичных методов
- Добавляйте тесты для новой функциональности
- Обновляйте документацию
- Используйте осмысленные commit сообщения

📖 [Руководство разработчика](DEVELOPER_GUIDE.md)

---

## 📊 Статистика проекта

- **Версия:** 3.2.1
- **Язык:** Python 3.8+
- **Фреймворк:** Flask (обертка)
- **Строк кода:** ~15,000+
- **Модулей:** 50+
- **Тестов:** 105

---

## 🛡️ Security Demo

Интерактивный демо-стенд ([security-demo/](security-demo/)) для демонстрации
возможностей модуля безопасности `sec`. **Прогоняет атаки через настоящий код
`sec`** — детекторы IPS/IDS, `RateLimiter` и DLP-middleware, а не имитацию.

### Запуск

```bash
# Локально (откроется на http://127.0.0.1:5050)
python security-demo/app.py

# Docker
cd security-demo && docker-compose up --build
```

### Возможности
- **Attack Simulator** — запуск 8 типов атак (SQLi, XSS, LFI, RCE, DDoS, CVE, DLP, APT chain) с живой реакцией IPS/IDS
- **Architecture Viewer** — интерактивная SVG-схема модуля sec
- **Metrics Dashboard** — мониторинг блокировок, системных метрик, нагрузочные тесты

Подробнее: см. [security-demo/README.md](security-demo/README.md)

---

## 🗺️ Roadmap

### v3.3 (Q4 2026)
- [ ] GraphQL поддержка
- [ ] WebSocket интеграция
- [ ] Встроенный ORM
- [ ] CLI генератор CRUD
- [ ] Плагин для VS Code

### v4.0 (Q1 2027)
- [ ] Полная переработка на FastAPI
- [ ] Нативная async поддержка
- [ ] Встроенный API Gateway
- [ ] Kubernetes интеграция
- [ ] Мониторинг и трейсинг (OpenTelemetry)

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

---

## 🙏 Благодарности

- Flask — за отличный микрофреймворк
- pywebview — за кроссплатформенные webview
- psutil — за мониторинг системы
- Все контрибьюторы проекта

---

## 📞 Контакты

- **Email:** support@aengine.dev
- **GitHub:** https://github.com/aaalllexxx/AEngine
- **Документация:** https://aengine.dev/docs
- **Telegram:** @aengine_community

---

<div align="center">

**Сделано с ❤️ командой AEngine**

[⬆ Наверх](#aengine---полнофункциональная-экосистема-для-разработки-web-и-desktop-приложений)

</div>
