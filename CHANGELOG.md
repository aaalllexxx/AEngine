# Changelog

All notable changes to AEngine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### [3.1.0] - Planned
- [ ] GraphQL support module
- [ ] WebSocket integration
- [ ] ORM wrapper (SQLAlchemy)
- [ ] Admin panel generator
- [ ] Internationalization (i18n)

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
