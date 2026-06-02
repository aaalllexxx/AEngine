# Changelog

All notable changes to AEngine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2026-06-03

### Changed
- 🏗️ **Архитектура security-demo переписана по структуре AEngineApps и
  использует модуль `sec` строго по документации.** Прежний бэкенд имитировал
  работу `sec` хаками (ручное создание детекторов, `unittest.mock.patch` для
  подмены времени `RateLimiter`, прогон в искусственном request-контексте).
  Теперь:
  - стенд разложен по структуре фреймворка: `main.py` (`App` + `load_config`),
    `config.json`, экраны `Screen`/`API` в `screens/`, состояние — в `GlobalStorage`
    (`state.py`); единый монолит `app.py` удалён;
  - компоненты `sec` привязываются к приложению штатно (`IPS(app)` + детекторы,
    `DLP(app, mode=Agressive)`, `RateLimiter(app, ...)`), как в разделе
    «Полный пример интеграции» из `sec/README.md`;
  - payload'ы прогоняются **настоящими HTTP-запросами** через защищённые
    приложения (`flask.test_client()`): IPS блокирует на `before_request`
    (`abort 400`), DLP маскирует на `after_request`, RateLimiter отдаёт `429` —
    стенд лишь читает реальный результат, логику защиты не дублирует;
  - реалистичная двухслойная защита: прикладной IPS (SQLi/XSS/LFI/RCE) + DLP и
    отдельный сигнатурный WAF-слой (OWASP CRS, `SignatureDetector`) для CVE;
    демонстрация RateLimiter вынесена в изолированную «лабораторию».
- 🐳 Точка входа Docker-образа стенда переключена на `python main.py`.

### Added
- 🧪 Интеграционные тесты стенда (`tests/test_demo_app.py`): блокировка SQLi/CVE
  реальными IPS/WAF, маскирование ПДн через DLP, срабатывание RateLimiter на
  потоке, полная APT-цепочка. Всего тестов: **115** (было 107).

## [3.2.1] - 2026-06-03

### Fixed
- 🐞 **Восстановлена зависимость `pywebview` в `security-demo/requirements.txt`.**
  В 3.2.0 она была ошибочно удалена с формулировкой «стенд работает в web-режиме».
  Однако `AEngineApps` импортирует `webview` на уровне модуля
  (`AEngineApps/app.py`), поэтому даже в web-режиме `from AEngineApps import App`
  падает с `ModuleNotFoundError: No module named 'webview'`, если pywebview не
  установлен. На свежей машине `pip install -r requirements.txt && python app.py`
  не запускался — теперь запускается.
- 🐞 **Добавлена зависимость `rich` в `security-demo/requirements.txt`.** Стенд
  импортирует `sec.intrusions`/`sec.dlp`, а `sec/__init__.py` загружает весь пакет,
  включая `sec/logging.py` (`from rich import print`). Без `rich` контейнер падал с
  `ModuleNotFoundError: No module named 'rich'`. Полнота списка зависимостей
  проверена в чистом venv (только `requirements.txt`) — стенд импортируется и
  отвечает на всех эндпоинтах.

### Added
- 🔄 **Авто-установка зависимостей** в `security-demo/app.py`: при прямом запуске
  стенд сам доустанавливает недостающие пакеты из `requirements.txt`
  (`flask`, `psutil`, `pywebview`, `rich`). Отключается `AENGINE_NO_AUTO_INSTALL=1`.
- 🧪 Регрессионные тесты зависимостей стенда (`tests/test_demo_deps.py`): проверяют,
  что `flask`/`psutil`/`pywebview`/`rich` объявлены в `requirements.txt` и что
  `AEngineApps` тянет `webview`, а `sec` — `rich` при импорте. Всего тестов: **107**
  (было 101).

### Changed
- 🐳 Базовый образ демо-стенда переведён с `python:3.11-alpine` на
  `python:3.11-slim`: `psutil` и `pywebview` ставятся из готовых wheel'ов без
  сборочных инструментов (ранее именно компиляция на Alpine и была источником
  проблем). В Docker выставлена `AENGINE_NO_AUTO_INSTALL=1` — зависимости
  устанавливаются на этапе сборки образа.
- 📝 `security-demo/README.md`: добавлены разделы о зависимостях и авто-установке,
  исправлено описание healthcheck (`/health`).

## [3.2.0] - 2026-06-01

### Changed
- 🛡️ **Security Demo теперь использует НАСТОЯЩИЙ модуль `sec`.** Бэкенд стенда
  (`security-demo/app.py`) полностью переписан: вместо повторной реализации логики
  защиты полезные нагрузки прогоняются через реальные компоненты `sec`.
  - `/api/attack/run` — реальные детекторы IPS/IDS (`SQLiDetector`, `XSSDetector`,
    `LFIDetector`, `RCEDetector`, `SignatureDetector`) в контексте Flask-запроса;
  - `/api/attack/flood` — реальный `RateLimiter` со скользящим окном (модельное время);
  - `/api/attack/dlp-test` — реальный DLP-middleware (`after_request`) на отдельном приложении;
  - `/api/attack/chain` — APT-цепочка на реальных детекторах и DLP-фильтрах.
- Детектор `RCEDetector` (submodule `sec`) усилен: детерминированное обнаружение
  подстановки команд (`$(...)`, обратные кавычки) и инъекции команд независимо от
  окружения. Подробности — в `sec/changelog.md` (2.7.0).

### Added
- Эндпоинт `/health` в демо-стенде для Docker/балансировщиков.
- Конфигурация демо-стенда через переменные окружения `HOST` / `PORT` / `DEBUG` / `SECRET_KEY`.
- Регрессионные тесты детекторов в контексте запроса (`tests/test_security.py`) —
  всего тестов: **101** (было 95).

### Fixed
- Удалена лишняя зависимость `pywebview` из `security-demo/requirements.txt`
  (ломала сборку Docker-образа на Alpine; стенд работает в web-режиме).
- Healthcheck демо-стенда переключён на `/health` (Dockerfile, docker-compose).
- Документация приведена в соответствие с кодом:
  - `security-demo/README.md` — исправлены тело запросов API (`attack_type`),
    список полей метрик, переменные окружения;
  - корневой `README.md` — корректная команда запуска (`hypercorn main:asgi_app`,
    порт 8000), удалены ссылки на несуществующую папку `examples/`, обновлены
    версия (3.2.0) и число тестов (101).

## [2.2.0] - 2026-06-01

### Added
- 🛡️ Security Demo Application (`security-demo/`) — интерактивное SPA для демонстрации возможностей модуля безопасности
  - Вкладка "Attack Simulator": 8 типов атак (SQLi, XSS, LFI, RCE, DDoS, CVE, DLP, Attack Chain) с живой реакцией IPS/IDS
  - Вкладка "Architecture": интерактивная SVG-схема архитектуры модуля sec
  - Вкладка "Metrics Dashboard": мониторинг в реальном времени (Canvas-графики, логи событий, нагрузочные тесты)
- Docker-контейнеризация демо-приложения (порт 5050)

### Verified
- ✅ Все модули проходят проверку импортов (18/18 компонентов)
- ✅ 95 тестов pytest — все passed
- ✅ APM CLI полностью функционален
- ✅ Модуль sec: IPS/IDS, RateLimiter, DLP, OSProtection, SystemProtection — работают корректно

---

## [v3.1.0] - 2026-05-31

### 🔒 Security
- Удалены захардкоженные учётные данные из sec_config.py
- Исправлена уязвимость Path Traversal в ClusterNode (tar.extractall)
- Устранена Command Injection в auth.py (shell=True → shell=False)
- Сравнение паролей через hmac.compare_digest (timing-safe)
- Безопасный импорт psutil с graceful degradation

### 🏗️ Architecture
- Устранено дублирование кода между sec/ и sec/AEngineApps/
- Добавлена потокобезопасность в GlobalStorage (RLock)
- Оптимизирован JsonDict с batch_update() context manager
- Создан main.py — единая точка входа приложения
- Добавлен __init__.py для AEngineApps и sec/AEngineApps

### 🐛 Bug Fixes
- Исправлены ложные срабатывания XSS Detector
- Исправлен ReDoS в DLP PhoneFilter
- Устранена утечка файловых дескрипторов в App
- Исправлен __all__ в ClusterNode
- Удалён BOM из APM/requirements.txt

### 📦 Infrastructure
- Обновлены GitHub Actions до v4/v5
- CI/CD: добавлен submodules: recursive
- Dockerfile: исправлен HEALTHCHECK, CMD
- docker-compose: добавлены healthchecks для Redis/PostgreSQL
- Создан .dockerignore
- Улучшена конфигурация nginx

### 🧪 Tests
- Полностью переписаны тесты (95 тестов)
- Покрытие: App, Screen, API, Service, GlobalStorage, JsonDict, Security, main.py

---

## [3.0.0] - 2026-03-19

### 🚀 Major Release - Production Enterprise Ready

#### Added
- **AsyncApp** - Полная поддержка async/await для production enterprise
- **AsyncScreen** - Асинхронные экраны с идентичным API
- **Health Checks** - Встроенная система проверки здоровья приложения
- **Metrics Endpoint** - Prometheus-совместимые метрики
- **Docker Support** - Production-ready Dockerfile и docker-compose
- **CI/CD Pipeline** - Полный GitHub Actions workflow
- **Nginx Configuration** - Reverse proxy с SSL и rate limiting
- **Testing Infrastructure** - pytest с async поддержкой
- **Android Build Support** - Исправлена сборка APK через buildozer
- **NTFS Compatibility** - Решены проблемы копирования файлов в WSL

#### Changed
- **Requirements** - Quart добавлен в базовые зависимости
- **Build System** - Улучшена обработка ошибок при сборке Android
- **PowerShell Setup** - Исправлены проблемы с автодополнением
- **Модульность** - Async как основной функционал, но опциональный

#### Fixed
- Ошибки прав доступа при копировании из NTFS в WSL
- PowerShell syntax errors в setup.bat
- Buildozer.spec конфигурация для Flask приложений
- Android platform detection в app.py

#### Documentation
- **PRODUCTION_GUIDE.md** - Полное руководство для production
- **QUICK_START.md** - Быстрый старт для новичков
- **ARCHITECTURE.md** - Описание модульной архитектуры
- **.env.example** - Шаблон environment variables
- **API Documentation** - Полная документация API

#### Security
- Non-root Docker user
- Security headers в Nginx
- Rate limiting
- HTTPS enforcement
- Environment variables для секретов

---

## [2.2.0] - 2025-12-15

### Added
- **Code Signing** - Электронная подпись и защита целостности
- **Advanced System Protection** - Глубокое сканирование хоста
- **Local Clustering** - Multiprocessing кластер на одном сервере
- **Admin Dashboard** - Веб-панель безопасности

### Changed
- Улучшена производительность IDS/IPS
- Оптимизирован sec модуль

---

## [2.0.0] - 2025-06-01

### 🎉 Major Rewrite - Pure OOP

#### Added
- **Screen Class** - Чистый OOP без декораторов
- **Service Class** - Микросервисная архитектура
- **API Class** - REST API helper
- **GlobalStorage** - Singleton storage
- **JsonDict** - JSON helper с автосохранением
- **Auto-routing** - Автоматическое обнаружение экранов
- **APM v2** - Портативный package manager
- **sec Module** - Комплексная безопасность

#### Changed
- Полный отказ от декораторов Flask
- Новая архитектура на основе классов
- Улучшенная документация

#### Removed
- Старый декораторный API (breaking change)

---

## [1.5.0] - 2024-11-20

### Added
- Базовая поддержка webview
- Простой package manager
- Генераторы проектов

---

## [1.0.0] - 2024-08-15

### 🎊 Initial Release

#### Added
- Базовый Flask wrapper
- Простая маршрутизация
- Шаблоны проектов
- Документация

---

## Roadmap

### [3.2.0] - Planned
- [ ] Real-time monitoring dashboard
- [ ] Auto-scaling support
- [ ] Kubernetes manifests
- [ ] Performance profiler
- [ ] Load testing tools

### [4.0.0] - Future
- [ ] Plugin system
- [ ] Visual project builder
- [ ] Cloud deployment automation
- [ ] Marketplace for modules
- [ ] Enterprise support

---

## Migration Guides

- [v1.x → v2.0](docs/MIGRATION_v2.md) - Переход на OOP архитектуру
- [v2.x → v3.0](docs/MIGRATION_v3.md) - Добавление async поддержки

## Contributors

- **Alex** - Lead Developer
- Community contributors - See GitHub

## License

MIT License - see LICENSE file for details
