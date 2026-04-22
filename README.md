# AEngine - Полнофункциональная Экосистема для Разработки Web и Desktop Приложений

<div align="center">

![Version](https://img.shields.io/badge/version-2.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
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
- 📱 **Android сборка** — build app для создания APK с автоматической обработкой зависимостей


---

## 🏗️ Архитектура

```
AEngine/
├── AEngineApps/          # Основной фреймворк
│   ├── app.py            # Класс App (ядро приложения)
│   ├── screen.py         # Базовый класс Screen
│   ├── api.py            # Класс API для REST
│   ├── service.py        # Класс Service для микросервисов
│   ├── async_app.py      # Асинхронная версия App
│   ├── async_screen.py   # Асинхронная версия Screen
│   ├── global_storage.py # Глобальное хранилище (Singleton)
│   └── json_dict.py      # Обертка над JSON файлами
│
├── APM/                  # Менеджер пакетов
│   ├── apm.py            # Главный CLI скрипт
│   ├── modules/          # Команды APM
│   │   ├── create.py     # Создание проектов
│   │   ├── install.py    # Установка модулей
│   │   ├── build.py      # Сборка в .exe
│   │   └── ...
│   ├── scripts/          # Установочные скрипты
│   └── examples/         # Шаблоны проектов
│
├── tests/                # Тесты
├── docs/                 # Документация (будет создана)
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile            # Docker образ
├── nginx.conf            # Nginx конфигурация
├── QUICK_START.md        # Быстрый старт
├── PRODUCTION_GUIDE.md   # Руководство по production
└── CHANGELOG.md          # История изменений
```

---

## 🚀 Быстрый старт

### Android APK сборка

**AEngine теперь поддерживает сборку Android APK!**

```bash
# 1. Загрузить зависимости (один раз)
python3 APM/scripts/predownload_deps.py

# 2. Запустить проактивный мониторинг (Терминал 1)
bash proactive_monitor.sh

# 3. Запустить сборку APK (Терминал 2)
apm build app
```

📖 **Подробнее:** [НАЧНИТЕ_ОТСЮДА.md](НАЧНИТЕ_ОТСЮДА.md) • [ФИНАЛЬНЫЙ_СТАТУС.md](ФИНАЛЬНЫЙ_СТАТУС.md)

### Веб-приложения

### Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (для установки модулей)

### Установка

#### 1. Клонирование репозитория

AEngine использует Git submodules для AEngineApps и APM. Клонируйте с автоматической инициализацией submodules:

```bash
# Клонирование с submodules
git clone --recursive https://github.com/yourusername/AEngine.git
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
| `apm build` | Собрать в .exe (PyInstaller) или APK (buildozer) |
| `apm build app` | Собрать Android APK |
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
- [Диагностика](scripts/diagnostics/README.md) — скрипты для проверки системы






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

📁 [Больше примеров в папке examples/](examples/)

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

# Запуск контейнера
docker run -p 5000:5000 aengine-app
```

### Docker Compose

```bash
# Запуск с Nginx и PostgreSQL
docker-compose up -d
```

### Nginx + Gunicorn

```bash
# Установка зависимостей
pip install gunicorn

# Запуск с Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app.flask_app
```

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
pytest --cov=AEngineApps --cov=APM

# Запуск конкретного теста
pytest tests/test_async_app.py
```

### Структура тестов

```
tests/
├── conftest.py              # Фикстуры pytest
├── test_app.py              # Тесты App
├── test_screen.py           # Тесты Screen
├── test_api.py              # Тесты API
├── test_service.py          # Тесты Service
├── test_async_app.py        # Тесты AsyncApp
└── test_apm.py              # Тесты APM
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

- **Версия:** 2.2
- **Язык:** Python 3.8+
- **Фреймворк:** Flask (обертка)
- **Строк кода:** ~15,000+
- **Модулей:** 50+
- **Тестов:** 100+

---

## 🗺️ Roadmap

### v2.3 (Q2 2026)
- [ ] GraphQL поддержка
- [ ] WebSocket интеграция
- [ ] Встроенный ORM
- [ ] CLI генератор CRUD
- [ ] Плагин для VS Code

### v3.0 (Q4 2026)
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
- **GitHub:** https://github.com/yourusername/AEngine
- **Документация:** https://aengine.dev/docs
- **Telegram:** @aengine_community

---

<div align="center">

**Сделано с ❤️ командой AEngine**

[⬆ Наверх](#aengine---полнофункциональная-экосистема-для-разработки-web-и-desktop-приложений)

</div>
