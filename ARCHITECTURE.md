# Архитектура AEngine

## Содержание

- [Обзор архитектуры](#обзор-архитектуры)
- [Компоненты системы](#компоненты-системы)
- [Паттерны проектирования](#паттерны-проектирования)
- [Потоки данных](#потоки-данных)
- [Безопасность](#безопасность)
- [Масштабирование](#масштабирование)

---

## Обзор архитектуры

AEngine — это репозиторий-агрегатор, объединяющий независимые компоненты экосистемы для разработки веб-приложений на Python.

```
┌─────────────────────────────────────────────────────────┐
│                    AEngine Repository                   │
│              (Документация + Git Submodules)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ AEngineApps  │  │     APM      │                     │
│  │  Framework   │  │   Manager    │                     │
│  │ (submodule)  │  │ (submodule)  │                     │
│  └──────────────┘  └──────────────┘                     │
│         │                 │                             │
│         │                 │                             │
│         │          ┌──────▼──────┐                      │
│         │          │ Устанавливает                      │
│         │          │   модули    │                     │
│         │          └──────┬──────┘                      │
│         │                 │                             │
│         │          ┌──────▼──────┐                      │
│         │          │     sec     │  (опциональный       │
│         │          │  (модуль)   │   пользовательский   │
│         │          └─────────────┘   модуль)            │
│         │                                               │
│  ┌──────▼──────┐                                        │
│  │    Flask    │                                        │
│  │   (Core)    │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

### Принципы архитектуры

1. **Модульность** — независимые компоненты, устанавливайте только нужное
2. **Separation of Concerns** — каждый компонент отвечает за свою область
3. **Dependency Inversion** — зависимости направлены от конкретного к абстрактному
4. **Open/Closed Principle** — открыто для расширения, закрыто для модификации
5. **Single Responsibility** — один класс = одна ответственность
6. **Interface Segregation** — минимальные интерфейсы

### Структура экосистемы

- **AEngine** — репозиторий-агрегатор с документацией и примерами
- **AEngineApps** — независимый фреймворк (git submodule)
- **APM** — независимый менеджер пакетов (git submodule)

---

## Компоненты системы

### 1. AEngineApps Framework

#### 1.1 Класс App (app.py)

Центральный компонент фреймворка, управляющий жизненным циклом приложения.

**Архитектурная роль:** Facade + Factory

```python
class App:
    """
    Фасад над Flask приложением с расширенной функциональностью.
    
    Ответственности:
    - Управление маршрутами (routing)
    - Lifecycle hooks (before/after request, start/stop)
    - Конфигурация приложения
    - Регистрация сервисов
    - Запуск приложения (web/webview)
    """
```

**Внутренняя структура:**

```
App
├── flask_app (Flask instance)
├── config (dict)
├── _screens (list)
├── _services (list)
├── _before_request_funcs (list)
├── _after_request_funcs (list)
├── _on_start_funcs (list)
└── _on_stop_funcs (list)
```

**Жизненный цикл запроса:**

```
1. HTTP Request
   ↓
2. before_request hooks
   ↓
3. Route matching
   ↓
4. Screen.run() execution
   ↓
5. after_request hooks
   ↓
6. HTTP Response
```

#### 1.2 Класс Screen (screen.py)

Базовый класс для всех контроллеров/страниц.

**Архитектурная роль:** Template Method + Strategy

```python
class Screen:
    """
    Абстрактный базовый класс для контроллеров.
    
    Паттерн: Template Method
    - run() — абстрактный метод (должен быть переопределен)
    - render(), redirect(), json() — конкретные методы
    
    Ответственности:
    - Обработка HTTP запросов
    - Рендеринг шаблонов
    - Работа с сессиями
    - Доступ к request/response
    """
```

**Иерархия наследования:**

```
Screen (базовый)
├── API (для REST API)
├── AsyncScreen (асинхронный)
└── CustomScreen (пользовательские)
```

#### 1.3 Класс API (api.py)

Специализированный класс для REST API.

**Архитектурная роль:** Strategy + Adapter

```python
class API(Screen):
    """
    Адаптер Screen для REST API.
    
    Особенности:
    - Автоматическая маршрутизация по HTTP методам
    - Автоматическая сериализация в JSON
    - Валидация входных данных
    - Обработка ошибок
    """
```

**Маршрутизация запросов:**

```
HTTP GET    → api.get()
HTTP POST   → api.post()
HTTP PUT    → api.put()
HTTP DELETE → api.delete()
HTTP PATCH  → api.patch()
```

#### 1.4 Класс Service (service.py)

Микросервисная архитектура с изоляцией.

**Архитектурная роль:** Module + Namespace

```python
class Service:
    """
    Изолированный модуль с собственными маршрутами и middleware.
    
    Основан на Flask Blueprints.
    
    Ответственности:
    - Группировка связанных Screen
    - Изоляция middleware
    - URL префиксы
    - Модульность
    """
```

**Структура сервиса:**

```
Service
├── name (str)
├── prefix (str)
├── blueprint (Flask Blueprint)
├── screens (list)
├── before_request_funcs (list)
└── after_request_funcs (list)
```

#### 1.5 GlobalStorage (global_storage.py)

Глобальное хранилище данных.

**Архитектурная роль:** Singleton

```python
class GlobalStorage:
    """
    Singleton для обмена данными между модулями.
    
    Решает проблему:
    - Циклических импортов
    - Глобального состояния
    - Обмена данными между сервисами
    """
    _instance = None
    _data = {}
```

#### 1.6 JsonDict (json_dict.py)

Обертка над JSON файлами.

**Архитектурная роль:** Proxy + Lazy Loading

```python
class JsonDict:
    """
    Прокси для работы с JSON файлами как с объектами.
    
    Особенности:
    - Ленивая загрузка
    - Автосохранение (dirty flag)
    - Атрибутный доступ
    - Безопасная работа с файлами
    """
```

### 2. APM (Package Manager)

#### 2.1 Архитектура APM

**Паттерн:** Command + Plugin

```
apm.py (CLI Entry Point)
├── argparse (парсинг команд)
├── modules/ (команды)
│   ├── create.py
│   ├── install.py
│   ├── build.py
│   └── ...
└── config.json (глобальная конфигурация)
```

**Система плагинов:**

```python
# Динамическая загрузка команд
def load_subcommands():
    """
    Сканирует установленные модули на наличие
    subcommands и регистрирует их в APM.
    
    Пример: sec модуль добавляет команды:
    - apm sec init
    - apm sec sign
    - apm sec remove
    """
```

#### 2.2 Управление проектами

**Структура проекта:**

```
project/
├── .apm/                  # Метаданные APM
│   ├── project.json       # Информация о проекте
│   └── modules/           # Установленные модули
├── AEngineApps/           # Фреймворк (копия)
├── screens/               # Контроллеры
├── templates/             # HTML шаблоны
├── static/                # Статические файлы
├── config.json            # Конфигурация
└── main.py                # Точка входа
```

### 3. sec (Опциональный модуль безопасности)

**Важно:** sec — это пользовательский модуль, устанавливаемый через APM. Он не входит в ядро экосистемы.

#### 3.1 Архитектура безопасности

**Многоуровневая защита:**

```
┌─────────────────────────────────────┐
│     Application Layer (L7)          │
│  IDS/IPS, Rate Limiting, CORS       │
├─────────────────────────────────────┤
│     Transport Layer (L4)            │
│  SYN Flood Detection, Connection    │
│  Monitoring                         │
├─────────────────────────────────────┤
│     Host Layer                      │
│  Process Monitoring, Resource       │
│  Control, Integrity Checking        │
└─────────────────────────────────────┘
```
AEngine/                  # Репозиторий-агрегатор
├── AEngineApps/          # Git submodule - независимый фреймворк
│   ├── app.py            # Класс App (ядро приложения)
│   ├── screen.py         # Базовый класс Screen
│   ├── api.py            # Класс API для REST
│   ├── service.py        # Класс Service для микросервисов
│   ├── async_app.py      # Асинхронная версия App
│   ├── async_screen.py   # Асинхронная версия Screen
│   ├── global_storage.py # Глобальное хранилище (Singleton)
│   └── json_dict.py      # Обертка над JSON файлами
│
├── APM/                  # Git submodule - независимый менеджер пакетов
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
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile            # Docker образ
├── nginx.conf            # Nginx конфигурация
├── README.md             # Главная документация
├── ARCHITECTURE.md       # Архитектура экосистемы
├── QUICK_START.md        # Быстрый старт
├── PRODUCTION_GUIDE.md   # Руководство по production
├── DEVELOPER_GUIDE.md    # Руководство разработчика
├── API_REFERENCE.md      # Справочник API
├── GIT_SETUP.md          # Настройка Git submodules
└── CHANGELOG.md          # История изменений
```


#### 3.3 Кластеризация

**Паттерн:** Active-Passive Failover

```
┌──────────────┐         ┌──────────────┐
│   Master     │ ◄─────► │   Slave 1    │
│  (Active)    │ Heartbeat│  (Passive)   │
│  Port 5000   │         │  Port 5001   │
└──────────────┘         └──────────────┘
       │                        │
       │ Master Down?           │
       │                        │
       └────────────────────────┘
              Failover
       ┌────────────────────────┐
       │    Slave 1 → Master    │
       │    (Active)            │
       └────────────────────────┘
```

---

## Паттерны проектирования

### Используемые паттерны

| Паттерн | Где используется | Зачем |
|---------|------------------|-------|
| **Singleton** | GlobalStorage | Единственный экземпляр хранилища |
| **Factory** | App.add_screen() | Создание Screen экземпляров |
| **Facade** | App | Упрощение работы с Flask |
| **Template Method** | Screen.run() | Определение скелета алгоритма |
| **Strategy** | API HTTP methods | Выбор стратегии обработки |
| **Observer** | IDS callbacks | Уведомление о событиях |
| **Chain of Responsibility** | IDS detectors | Цепочка обработчиков |
| **Proxy** | JsonDict | Прокси для JSON файлов |
| **Command** | APM commands | Инкапсуляция команд |
| **Plugin** | APM subcommands | Расширяемость |
| **Adapter** | API over Screen | Адаптация интерфейса |

---

## Потоки данных

### 1. Обработка HTTP запроса

```
Client Request
   ↓
Nginx (reverse proxy)
   ↓
Gunicorn (WSGI server)
   ↓
Flask Application
   ↓
App.before_request hooks
   ↓
Security checks (IDS/IPS, Rate Limit)
   ↓
Route matching
   ↓
Screen instantiation
   ↓
Screen.run() execution
   ↓
Response generation
   ↓
App.after_request hooks
   ↓
Client Response
```

### 2. Автоматическая маршрутизация

```
App.load_config()
   ↓
Read config.json
   ↓
routers == "auto"?
   ↓ Yes
Scan screen_path directory
   ↓
Import all .py files
   ↓
Find Screen subclasses
   ↓
Check for 'route' attribute
   ↓
Register route → Screen mapping
   ↓
Flask route registration
```

### 3. Установка модуля (APM)

```
apm install <git_url>
   ↓
Clone repository
   ↓
Check for module.json
   ↓
Read dependencies
   ↓
Install dependencies (pip)
   ↓
Copy files to project
   ↓
Register in .apm/modules/
   ↓
Load subcommands (if any)
   ↓
Success
```

---

## Безопасность

### Уровни защиты

#### L7 (Application Layer)

- **IDS/IPS** — обнаружение и блокировка атак
- **Rate Limiting** — защита от DDoS
- **CORS** — контроль кросс-доменных запросов
- **Session Management** — безопасные сессии
- **Input Validation** — валидация входных данных

#### L4 (Transport Layer)

- **SYN Flood Detection** — обнаружение SYN атак
- **Connection Monitoring** — мониторинг соединений
- **IP Blacklisting** — блокировка подозрительных IP

#### Host Layer

- **Process Monitoring** — контроль процессов
- **Resource Control** — ограничение ресурсов
- **Integrity Checking** — проверка целостности кода
- **Privilege Control** — контроль привилегий

### Модель угроз

| Угроза | Вектор атаки | Защита |
|--------|--------------|--------|
| SQL Injection | Параметры запроса | SQLiDetector |
| XSS | Пользовательский ввод | XSSDetector |
| RCE | Загрузка файлов | RCEDetector |
| LFI/RFI | Path traversal | LFIDetector |
| DDoS | Множество запросов | RateLimiter |
| Brute Force | Повторные попытки | RateLimiter |
| Code Injection | Модификация файлов | CodeSigner |
| Privilege Escalation | Запуск от root | OSProtect |

---

## Масштабирование

### Горизонтальное масштабирование

```
                Load Balancer (Nginx)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   Instance 1      Instance 2      Instance 3
   (Port 5000)     (Port 5001)     (Port 5002)
        │               │               │
        └───────────────┴───────────────┘
                        │
                Shared Database
```

### Вертикальное масштабирование

- **Gunicorn workers** — несколько процессов
- **Async support** — AsyncApp для I/O операций
- **Caching** — Redis/Memcached
- **Database pooling** — пул соединений

### Кластеризация

#### Межсерверная (cluster.py)

```python
# Master node
master = create_cluster_node(
    node_id="master",
    role="master",
    port=8888
)

# Slave nodes
slave1 = create_cluster_node(
    node_id="slave1",
    role="slave",
    master_ip="192.168.1.100",
    master_port=8888
)
```

#### Локальная (auto_cluster.py)

```python
# Один сервер, несколько портов
cluster = LocalCluster(app, ports=[5000, 5001, 5002])
cluster.run()
```

---

## Производительность

### Оптимизации

1. **Lazy Loading** — загрузка по требованию
2. **Caching** — кеширование результатов
3. **Connection Pooling** — переиспользование соединений
4. **Static File Serving** — Nginx для статики
5. **Async I/O** — асинхронные операции
6. **Database Indexing** — индексы БД
7. **Query Optimization** — оптимизация запросов

### Метрики

- **Response Time** — время ответа < 100ms
- **Throughput** — 1000+ req/sec
- **CPU Usage** — < 80%
- **Memory Usage** — < 80%
- **Error Rate** — < 0.1%

---

## Расширяемость

### Точки расширения

1. **Custom Screen** — наследование от Screen
2. **Custom Detector** — наследование от BaseDetector
3. **APM Subcommands** — плагины для APM
4. **Middleware** — before/after request hooks
5. **Services** — микросервисная архитектура

### Пример расширения

```python
# Кастомный детектор
class CustomDetector(BaseDetector):
    def run(self):
        # Ваша логика
        pass

# Кастомная команда APM
# APM/modules/custom.py
def execute(args):
    # Ваша логика
    pass
```

---

## Заключение

Архитектура AEngine построена на принципах модульности и независимости компонентов:

- **Модульность** — независимые проекты (AEngineApps, APM)
- **Гибкость** — устанавливайте только то, что нужно
- **Тестируемость** — изолированные компоненты
- **Масштабируемость** — от прототипа до production
- **Производительность** — оптимизации и кеширование

### Ключевые моменты

1. **AEngine** — это репозиторий-агрегатор с документацией, а не монолитный фреймворк
2. **AEngineApps и APM** — независимые проекты, подключенные как git submodules
3. **PEP 8** — цель для будущих версий, пока не строго соблюдается

Система спроектирована для роста и адаптации к меняющимся требованиям.
