# AEngine

Экосистема для разработки защищённых web/desktop-приложений на Python. Состоит из трёх компонентов:

| Компонент | Назначение |
|-----------|------------|
| **AEngineApps** | OOP-фреймворк на Flask + pywebview (sync) и Quart (async). Без декораторов — чистые классы. |
| **APM** | AEngine Package Manager — CLI для создания проектов, установки модулей и сборки артефактов деплоя. |
| **sec** | Модуль безопасности: IDS/IPS, защита ОС/сети/системы, подпись кода, админ-дашборд. |

---

## Структура репозитория

```
AEngine/
├── AEngineApps/     # фреймворк (App, Screen, API, Service + AsyncApp/AsyncScreen/AsyncAPI)
├── APM/             # пакетный менеджер (apm ...)
├── sec/             # модуль безопасности (apm sec init)
├── demo/            # демостенд: намеренно уязвимое приложение + sec
├── tests/           # тесты
└── README.md
```

---

## Быстрый старт

```bash
# 1. Установка APM (см. install.sh / install.bat)
bash install.sh            # или: install.bat на Windows

# 2. Новый проект
apm init                   # инициализирует .apm/ и структуру проекта

# 3. Запуск
python main.py
```

Минимальное приложение:

```python
from AEngineApps.app import App

app = App("MyApp")
app.load_config(app.project_root + "config.json")
app.run()
```

---

## AEngineApps — фреймворк

**Синхронный слой (Flask + pywebview):**

- `App` — приложение: роутинг, сервисы, middleware, hooks, авто-дискавери экранов/сервисов, запуск в окне (webview) или как web-сервер.
- `Screen` — базовый экран (`render`, `redirect`, `json`, `session`, …).
- `API(Screen)` — REST: HTTP-метод → методы `get/post/put/delete`, авто-JSON.
- `Service` — модуль-blueprint с собственным префиксом и middleware.

```python
class HomeScreen(Screen):
    route = "/"
    def run(self):
        return self.render("index.html", title="Главная")

class UserAPI(API):
    route = "/api/user"
    methods = ["GET", "POST"]
    def get(self):
        return {"name": "Alex"}            # авто-JSON
```

**Асинхронный слой (Quart) — для крупных нагруженных проектов:**

- `AsyncApp`, `AsyncScreen`, `AsyncAPI` — те же возможности, но `async/await`.
- Встроенные `/health` и `/metrics` (`app.enable_health_endpoint()`, `app.enable_metrics_endpoint()`).
- Потокобезопасный `GlobalStorage`, batch-режим записи в `JsonDict`.

Async-классы импортируются, только если установлен `quart` (иначе доступен лишь синхронный слой).

**Авто-конфигурация** через `config.json`:

```json
{
  "host": "127.0.0.1", "port": 5000, "view": "web",
  "routers": "auto", "screen_path": "screens",
  "services": "auto", "services_path": "services"
}
```

---

## APM — пакетный менеджер

```bash
apm --help                 # список команд (сгруппированы по типам)
apm init                   # инициализация проекта
apm develop module|screen  # генерация заготовок
apm install <источник>     # установка модуля (папка | архив | github | owner/repo | shorthand)
apm build module           # собрать модуль в .apm.zip
apm build docker           # сгенерировать Dockerfile + docker-compose.yml + requirements.txt
```

### Локальная и глобальная область видимости модулей

| Команда | Куда ставится | Где видна |
|---------|---------------|-----------|
| `apm install <src>`     | `<проект>/.apm/installed/` | в текущем проекте |
| `apm install <src> -g`  | `APM/installed/`           | из любого проекта (глобально) |

Приоритет при поиске команды: **встроенная → локальная → глобальная**. Команды и alias'ы обнаруживаются в обеих областях.

### `apm build docker`

Анализирует зависимости проекта и генерирует артефакты для развёртывания:

```bash
apm build docker [project_dir] [--output dir] [--port N] [--force]
```

Создаёт `requirements.txt` (по фактическим импортам), `Dockerfile` (порт берётся из `config.json`) и `docker-compose.yml`. Запуск: `docker compose up --build`.

---

## sec — модуль безопасности

Детекторы атак: **SQLi, XSS, RCE, LFI**, открытая база сигнатур (Log4Shell, Spring4Shell, Shellshock и др.), `RateLimiter`, контроль ресурсов ОС, анализ сети, сканер системы, подпись кода.

### Установка в проект

```bash
apm install sec            # поставить модуль sec (локально или -g глобально)
apm sec init               # развернуть модули безопасности в AEngineApps/ проекта
```

`apm sec init` копирует модули в `AEngineApps/`, создаёт `services/sec_dashboard.py` (авто-регистрация дашборда) и `sec_modules.json` (состояние модулей).

### Подключение — единая точка интеграции

```python
from AEngineApps.app import App
from AEngineApps.security import Security

app = App("MyApp")
app.load_config(app.project_root + "config.json")
Security(app).enable()     # вся защита подключена
app.run()
```

### Админ-дашборд и управление модулями

Дашборд доступен по адресу **`/sec-admin`** (логин/пароль задаются при `apm sec init`).

Вкладки: Обзор, Инциденты, Система, Сеть и **Модули** — на последней можно **включать/выключать модули безопасности на лету**:

- `intrusion` — блокировка атак применяется мгновенно (IPS отклоняет вредоносные запросы с HTTP 400);
- `os_protect` / `net_analyzer` / `sys_protect` — управляют тяжёлыми сканированиями (выполняются по запросу из дашборда).

Состояние сохраняется в `sec_modules.json` и переживает перезапуск.

---

## Демостенд (`demo/`)

Готовое AEngine-приложение с **намеренно внесёнными уязвимостями** (SQLi, XSS, RCE, LFI, сигнатуры) и подключённым sec.

```bash
cd demo
python main.py                       # http://127.0.0.1:5057  ·  дашборд: /sec-admin (admin/admin)
python attack_test.py                # авто-проверка: атаки при ВКЛ блокируются, при ВЫКЛ проходят
python attack_test.py --url http://127.0.0.1:5057   # проверка запущенного сервера
```

`attack_test.py` без аргументов поднимает приложение через Flask test client, прогоняет атаки с включённой и выключенной защитой и выдаёт вердикт — наглядное доказательство работоспособности sec.

---

## Развёртывание

```bash
apm build docker            # сгенерировать Dockerfile/compose/requirements
docker compose up --build
```

Для контейнера в `config.json` укажите `"host": "0.0.0.0"` и `"view": "web"`.

---

## Тестирование

```bash
python -m pytest            # модульные тесты (tests/)
python demo/attack_test.py  # проверка защиты на демостенде
```

---

## Лицензия

MIT.
