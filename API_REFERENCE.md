# API Reference - AEngine

Полный справочник по всем классам, методам и функциям AEngine.

## Содержание

- [AEngineApps Framework](#aengineapps-framework)
  - [Класс App](#класс-app)
  - [Класс Screen](#класс-screen)
  - [Класс API](#класс-api)
  - [Класс Service](#класс-service)
  - [Класс AsyncApp](#класс-asyncapp)
  - [Класс AsyncScreen](#класс-asyncscreen)
  - [Класс GlobalStorage](#класс-globalstorage)
  - [Класс JsonDict](#класс-jsondict)
- [Security Module (sec)](#security-module-sec)
- [APM Commands](#apm-commands)

### Класс GlobalStorage

Singleton для глобального хранилища данных.

#### Получение экземпляра

```python
from AEngineApps.global_storage import GlobalStorage

gs = GlobalStorage()  # Всегда возвращает один и тот же экземпляр
```

#### Методы

##### Установка значения (атрибут)

```python
gs.key = value
```

**Пример:**
```python
gs.database_url = "postgresql://localhost/mydb"
gs.api_key = "secret123"
```

##### Получение значения (атрибут)

```python
value = gs.key
```

**Пример:**
```python
db_url = gs.database_url
```

**Примечание:** Выбросит `AttributeError` если ключ не существует.

##### get()

```python
get(key: str, default: Any = None) -> Any
```

Безопасное получение значения с default.

**Параметры:**
- `key` (str) — имя ключа
- `default` (Any) — значение по умолчанию

**Пример:**
```python
api_key = gs.get("api_key", "default_key")
```

##### has()

```python
has(key: str) -> bool
```

Проверяет существование ключа.

**Параметры:**
- `key` (str) — имя ключа

**Возвращает:**
- `True` если ключ существует, иначе `False`

**Пример:**
```python
if gs.has("database_url"):
    connect_to_db(gs.database_url)
```

##### delete()

```python
delete(key: str) -> None
```

Удаляет ключ из хранилища.

**Параметры:**
- `key` (str) — имя ключа

**Пример:**
```python
gs.delete("temp_data")
```

##### clear()

```python
clear() -> None
```

Очищает все данные в хранилище.

**Пример:**
```python
gs.clear()
```

##### all()

```python
all() -> dict
```

Возвращает все данные в виде словаря.

**Возвращает:**
- Словарь со всеми данными

**Пример:**
```python
all_data = gs.all()
print(all_data)
```

---

### Класс JsonDict

Прокси для работы с JSON файлами как с объектами Python.

#### Конструктор

```python
JsonDict(file_path: str, encoding: str = "utf-8")
```

**Параметры:**
- `file_path` (str) — путь к JSON файлу
- `encoding` (str) — кодировка файла

**Пример:**
```python
from AEngineApps.json_dict import JsonDict

config = JsonDict("config.json")
```

#### Методы

##### Установка значения (атрибут)

```python
jd.key = value
```

Устанавливает значение и помечает файл как измененный.

**Пример:**
```python
config.port = 8080
config.debug = True
```

##### Получение значения (атрибут)

```python
value = jd.key
```

**Пример:**
```python
port = config.port
```

**Примечание:** Выбросит `AttributeError` если ключ не существует.

##### get()

```python
get(key: str, default: Any = None) -> Any
```

Безопасное получение значения.

**Параметры:**
- `key` (str) — имя ключа
- `default` (Any) — значение по умолчанию

**Пример:**
```python
port = config.get("port", 5000)
```

##### has()

```python
has(key: str) -> bool
```

Проверяет существование ключа.

**Пример:**
```python
if config.has("database"):
    print("Database configured")
```

##### Оператор in

```python
"key" in jd
```

Альтернативный способ проверки существования.

**Пример:**
```python
if "port" in config:
    print(f"Port: {config.port}")
```

##### update()

```python
update(data: dict) -> None
```

Массовое обновление ключей.

**Параметры:**
- `data` (dict) — словарь с новыми значениями

**Пример:**
```python
config.update({
    "host": "0.0.0.0",
    "port": 8080,
    "debug": False
})
```

##### delete_item()

```python
delete_item(key: str) -> None
```

Удаляет ключ из JSON.

**Параметры:**
- `key` (str) — имя ключа

**Пример:**
```python
config.delete_item("temp_setting")
```

##### keys()

```python
keys() -> List[str]
```

Возвращает список всех ключей.

**Пример:**
```python
for key in config.keys():
    print(key)
```

##### values()

```python
values() -> List[Any]
```

Возвращает список всех значений.

**Пример:**
```python
for value in config.values():
    print(value)
```

##### items()

```python
items() -> List[Tuple[str, Any]]
```

Возвращает пары (ключ, значение).

**Пример:**
```python
for key, value in config.items():
    print(f"{key}: {value}")
```

##### save()

```python
save() -> None
```

Принудительно сохраняет данные на диск.

**Пример:**
```python
config.port = 8080
config.save()  # Сохранить немедленно
```

**Примечание:** Обычно не требуется, так как сохранение происходит автоматически.

##### load()

```python
load() -> None
```

Перезагружает данные из файла.

**Пример:**
```python
config.load()  # Обновить из файла
```

##### push()

```python
push(data: dict) -> None
```

Заменяет весь файл новым словарем.

**Параметры:**
- `data` (dict) — новые данные

**Пример:**
```python
config.push({
    "host": "127.0.0.1",
    "port": 5000
})
```

---

### Класс AsyncApp

Асинхронная версия App для высоконагруженных приложений.

#### Конструктор

```python
AsyncApp(app_name: str = "AEngineApp", debug: bool = False)
```

Аналогичен App, но поддерживает async/await.

**Пример:**
```python
from AEngineApps.async_app import AsyncApp

app = AsyncApp("AsyncApp", debug=True)
```

#### Особенности

- Все методы аналогичны `App`
- Поддерживает `AsyncScreen` для асинхронных обработчиков
- Использует асинхронный WSGI сервер (например, Hypercorn)

**Пример использования:**
```python
from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen

class AsyncHomeScreen(AsyncScreen):
    route = "/"
    
    async def run(self):
        data = await fetch_from_api()
        return self.render("index.html", data=data)

app = AsyncApp("MyAsyncApp")
app.load_config("config.json")
app.run()
```

---

### Класс AsyncScreen

Асинхронная версия Screen.

#### Абстрактный метод

##### run()

```python
async def run(self, *args, **kwargs) -> Union[str, Response, tuple]
```

Асинхронный метод обработки запроса.

**Пример:**
```python
from AEngineApps.async_screen import AsyncScreen
import aiohttp

class AsyncAPIScreen(AsyncScreen):
    route = "/api/data"
    
    async def run(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.example.com/data") as resp:
                data = await resp.json()
        
        return self.json(data)
```

#### Все остальные методы

Все методы из `Screen` доступны и работают аналогично:
- `render()`
- `redirect()`
- `json()`
- `abort()`
- `flash()`
- `save_file()`

---

## Security Module (sec)

### IDS (Intrusion Detection System)

#### Конструктор

```python
from AEngineApps.intrusions import IDS

ids = IDS(app: App)
```

**Параметры:**
- `app` (App) — экземпляр приложения

#### Методы

##### add_detector()

```python
add_detector(detector_class: Type[BaseDetector]) -> None
```

Добавляет детектор атак.

**Параметры:**
- `detector_class` — класс детектора

**Пример:**
```python
from AEngineApps.intrusions import SQLiDetector, XSSDetector

ids.add_detector(SQLiDetector)
ids.add_detector(XSSDetector)
```

##### on_trigger()

```python
on_trigger(func: Callable) -> Callable
```

Регистрирует callback при обнаружении атаки.

**Пример:**
```python
@ids.on_trigger
def alert_admin():
    send_email("admin@example.com", "Attack detected!")
```

---

### IPS (Intrusion Prevention System)

Наследует IDS, но блокирует запросы при обнаружении атак.

```python
from AEngineApps.intrusions import IPS

ips = IPS(app)
ips.add_detector(SQLiDetector)
```

При обнаружении атаки возвращает HTTP 400.

---

### RateLimiter

Ограничение частоты запросов.

#### Конструктор

```python
from AEngineApps.intrusions import RateLimiter

limiter = RateLimiter(
    app: App,
    max_requests: int = 100,
    window: int = 60
)
```

**Параметры:**
- `app` (App) — экземпляр приложения
- `max_requests` (int) — максимум запросов
- `window` (int) — временное окно в секундах

**Пример:**
```python
# 100 запросов в минуту
limiter = RateLimiter(app, max_requests=100, window=60)
```

---

### Детекторы атак

#### SQLiDetector

Обнаруживает SQL инъекции.

```python
from AEngineApps.intrusions import SQLiDetector

ips.add_detector(SQLiDetector)
```

**Паттерны:**
- `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- `UNION`, `DROP`, `--`, `/**/`
- `'`, `"`, `;`

#### XSSDetector

Обнаруживает XSS атаки.

```python
from AEngineApps.intrusions import XSSDetector

ips.add_detector(XSSDetector)
```

**Паттерны:**
- `<script>`, `</script>`
- `javascript:`, `onerror=`, `onload=`
- `<iframe>`, `<object>`

#### RCEDetector

Обнаруживает попытки выполнения кода.

```python
from AEngineApps.intrusions import RCEDetector

ips.add_detector(RCEDetector)
```

**Паттерны:**
- `eval`, `exec`, `system`
- `bash`, `sh`, `cmd`
- `__import__`, `compile`

#### LFIDetector

Обнаруживает Local/Remote File Inclusion.

```python
from AEngineApps.intrusions import LFIDetector

ips.add_detector(LFIDetector)
```

**Паттерны:**
- `../`, `..\\`
- `/etc/passwd`, `C:\Windows`
- `%00`, `%2e%2e`

---

### Создание кастомного детектора

```python
from AEngineApps.intrusions import BaseDetector, _get_all_input_values
from flask import request

class CustomDetector(BaseDetector):
    def run(self):
        for value in _get_all_input_values():
            if "bad_pattern" in value.lower():
                self.log(f"Custom attack detected: {request.url}")
                self.trigger_response()
                break
```

---

## APM Commands

### Управление проектами

#### apm create

Создает новый проект AEngineApps.

```bash
apm create
```

Интерактивно запрашивает:
- Имя проекта
- Путь
- Режим (web/app)

#### apm init

Инициализирует существующую папку как проект.

```bash
cd my_project
apm init
```

#### apm delete

Удаляет проект с диска.

```bash
apm delete
```

#### apm run

Запускает проект.

```bash
apm run
```

#### apm config

Интерактивный конфигуратор.

```bash
apm config
```

---

### Управление модулями

#### apm install

Устанавливает модуль из Git.

```bash
# Локальная установка
apm install https://github.com/user/module

# Глобальная установка
apm install -g https://github.com/user/module
```

#### apm remove

Удаляет модуль.

```bash
apm remove
```

#### apm modules

Список установленных модулей.

```bash
apm modules
```

---

### Навигация

#### apm list

Список всех проектов.

```bash
apm list
```

#### apm goto

Переход в папку проекта.

```bash
apm goto
```

#### apm select

Выбор проекта по умолчанию.

```bash
apm select
```

---

### Разработка

#### apm develop module

Генерирует шаблон модуля APM.

```bash
apm develop module
```

#### apm develop screen

Генерирует Screen класс и HTML шаблон.

```bash
apm develop screen
```

---

### Сборка

#### apm build

Собирает проект в .exe (PyInstaller).

```bash
apm build
```

---

### Обновление

#### apm upgrade

Обновляет фреймворк AEngineApps в проекте.

```bash
apm upgrade
```

#### apm update

Обновляет сам APM.

```bash
apm update
```

---

### Безопасность (sec модуль)

#### apm sec init

Инициализирует модули безопасности.

```bash
# Все модули
apm sec init

# Конкретные модули
apm sec init --modules intrusion logs dashboard
```

#### apm sec sign

Подписывает код проекта.

```bash
apm sec sign
```

#### apm sec unsign

Снимает подпись.

```bash
apm sec unsign
```

#### apm sec add_admin

Создает администратора безопасности.

```bash
apm sec add_admin
```

#### apm sec remove

Удаляет модули безопасности.

```bash
apm sec remove
```

#### apm sec logs analyze

Анализирует логи на атаки.

```bash
apm sec logs analyze
```

---

## Заключение

Этот справочник покрывает все основные классы и методы AEngine. Для более подробной информации см.:

- [README.md](README.md) — обзор проекта
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура
- [AEngineApps/readme.md](AEngineApps/readme.md) — документация фреймворка
- [APM/readme.md](APM/readme.md) — документация APM
- [sec/README.md](sec/README.md) — документация sec модуля
## AEngineApps Framework

### Класс App

Основной класс приложения, управляющий жизненным циклом и маршрутизацией.

#### Конструктор

```python
App(app_name: str = "AEngineApp", debug: bool = False)
```

**Параметры:**
- `app_name` (str) — имя приложения
- `debug` (bool) — режим отладки

**Пример:**
```python
app = App("MyApp", debug=True)
```

#### Методы маршрутизации

##### add_screen()

```python
add_screen(path: str, screen_class: Type[Screen]) -> None
```

Регистрирует класс Screen для указанного URL пути.

**Параметры:**
- `path` (str) — URL путь (например, "/", "/users/<int:id>")
- `screen_class` (Type[Screen]) — класс, наследующий Screen

**Пример:**
```python
from AEngineApps.screen import Screen

class HomeScreen(Screen):
    route = "/"
    def run(self):
        return self.render("index.html")

app.add_screen("/", HomeScreen)
```

##### add_screens()

```python
add_screens(rules: Dict[str, Type[Screen]]) -> None
```

Массовая регистрация нескольких Screen классов.

**Параметры:**
- `rules` (dict) — словарь {путь: класс}

**Пример:**
```python
app.add_screens({
    "/": HomeScreen,
    "/about": AboutScreen,
    "/contact": ContactScreen
})
```

##### add_router()

```python
add_router(path: str, view_func: Callable, methods: List[str] = ["GET"]) -> None
```

Регистрирует обычную функцию как обработчик маршрута (legacy режим).

**Параметры:**
- `path` (str) — URL путь
- `view_func` (Callable) — функция-обработчик
- `methods` (list) — список HTTP методов

**Пример:**
```python
def old_handler():
    return "Legacy route"

app.add_router("/old", old_handler, methods=["GET", "POST"])
```

##### add_routers()

```python
add_routers(rules: Dict[str, Callable]) -> None
```

Массовая регистрация функций-обработчиков.

**Параметры:**
- `rules` (dict) — словарь {путь: функция}

#### Методы Lifecycle

##### before_request()

```python
before_request(func: Callable) -> Callable
```

Регистрирует функцию, вызываемую перед каждым HTTP запросом.

**Параметры:**
- `func` (Callable) — функция без параметров

**Возвращает:**
- Декорированную функцию

**Пример:**
```python
@app.before_request
def check_auth():
    if not is_authenticated():
        return redirect("/login")
```

**Примечание:** Если функция возвращает значение, запрос прерывается и это значение отправляется клиенту.

##### after_request()

```python
after_request(func: Callable[[Response], Response]) -> Callable
```

Регистрирует функцию, вызываемую после каждого HTTP запроса.

**Параметры:**
- `func` (Callable) — функция, принимающая и возвращающая Response

**Пример:**
```python
@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    return response
```

##### on_start()

```python
on_start(func: Callable) -> None
```

Регистрирует функцию, выполняемую один раз при старте приложения.

**Параметры:**
- `func` (Callable) — функция инициализации

**Пример:**
```python
def init_database():
    db.connect()
    print("Database connected")

app.on_start(init_database)
```

##### on_stop()

```python
on_stop(func: Callable) -> None
```

Регистрирует функцию, выполняемую при завершении приложения.

**Параметры:**
- `func` (Callable) — функция очистки

**Пример:**
```python
def cleanup():
    db.close()
    print("Database closed")

app.on_stop(cleanup)
```

#### Методы конфигурации

##### load_config()

```python
load_config(config_path: str, encoding: str = "utf-8") -> None
```

Загружает конфигурацию из JSON файла и применяет настройки.

**Параметры:**
- `config_path` (str) — путь к config.json
- `encoding` (str) — кодировка файла

**Пример config.json:**
```json
{
    "debug": true,
    "view": "web",
    "host": "127.0.0.1",
    "port": 5000,
    "screen_path": "screens",
    "routers": "auto",
    "services": "auto",
    "services_path": "services"
}
```

**Пример:**
```python
app.load_config("config.json")
```

##### enable_cors()

```python
enable_cors(
    origins: str = "*",
    methods: str = "*",
    headers: str = "*"
) -> None
```

Включает CORS (Cross-Origin Resource Sharing).

**Параметры:**
- `origins` (str) — разрешенные источники
- `methods` (str) — разрешенные HTTP методы
- `headers` (str) — разрешенные заголовки

**Пример:**
```python
app.enable_cors(
    origins="https://example.com",
    methods="GET,POST,PUT,DELETE",
    headers="Content-Type,Authorization"
)
```

##### set_error_page()

```python
set_error_page(code: int, screen_class: Type[Screen]) -> None
```

Устанавливает кастомную страницу ошибки.

**Параметры:**
- `code` (int) — HTTP код ошибки (404, 500, и т.д.)
- `screen_class` (Type[Screen]) — класс Screen для отображения

**Пример:**
```python
class NotFoundScreen(Screen):
    def run(self):
        return self.render("404.html"), 404

app.set_error_page(404, NotFoundScreen)
```

#### Методы управления сервисами

##### register_service()

```python
register_service(service: Service) -> None
```

Регистрирует микросервис в приложении.

**Параметры:**
- `service` (Service) — экземпляр Service

**Пример:**
```python
from AEngineApps.service import Service

auth_service = Service("auth", prefix="/api/auth")
app.register_service(auth_service)
```

#### Методы запуска

##### run()

```python
run(
    host: str = None,
    port: int = None,
    debug: bool = None,
    **kwargs
) -> None
```

Запускает приложение в режиме web или webview (зависит от конфигурации).

**Параметры:**
- `host` (str) — хост (по умолчанию из config)
- `port` (int) — порт (по умолчанию из config)
- `debug` (bool) — режим отладки (по умолчанию из config)
- `**kwargs` — дополнительные параметры Flask

**Пример:**
```python
app.run(host="0.0.0.0", port=8080, debug=True)
```

##### close()

```python
close() -> None
```

Принудительно закрывает окно webview (если открыто).

**Пример:**
```python
app.close()
```

#### Свойства

##### flask_app

```python
@property
flask_app -> Flask
```

Возвращает внутренний экземпляр Flask приложения.

**Пример:**
```python
flask_instance = app.flask_app
```

##### config

```python
@property
config -> dict
```

Возвращает словарь конфигурации приложения.

**Пример:**
```python
debug_mode = app.config.get("debug", False)
```

---

### Класс Screen

Базовый класс для всех контроллеров/страниц.

#### Атрибуты класса

```python
class MyScreen(Screen):
    route = "/path"           # Обязательный: URL маршрут
    methods = ["GET", "POST"] # Опциональный: HTTP методы
```

**Атрибуты:**
- `route` (str) — URL путь для автоматической маршрутизации
- `methods` (list) — список разрешенных HTTP методов (по умолчанию ["GET"])

#### Абстрактный метод

##### run()

```python
def run(self, *args, **kwargs) -> Union[str, Response, tuple]
```

Основной метод обработки запроса. Должен быть переопределен в наследниках.

**Параметры:**
- `*args` — позиционные параметры из URL
- `**kwargs` — именованные параметры из URL

**Возвращает:**
- `str` — HTML строка
- `Response` — Flask Response объект
- `tuple` — (содержимое, статус_код) или (содержимое, статус_код, заголовки)

**Пример:**
```python
class UserScreen(Screen):
    route = "/user/<int:user_id>"
    
    def run(self, user_id):
        user = database.get_user(user_id)
        return self.render("user.html", user=user)
```

#### Методы рендеринга

##### render()

```python
render(template_name: str, **context) -> str
```

Рендерит HTML шаблон с контекстом.

**Параметры:**
- `template_name` (str) — имя файла шаблона
- `**context` — переменные для шаблона

**Возвращает:**
- Отрендеренный HTML

**Пример:**
```python
def run(self):
    return self.render("index.html", title="Home", user="John")
```

##### redirect()

```python
redirect(location: str, code: int = 302) -> Response
```

Перенаправляет на другой URL.

**Параметры:**
- `location` (str) — URL для перенаправления
- `code` (int) — HTTP код (302 по умолчанию)

**Возвращает:**
- Flask Response с перенаправлением

**Пример:**
```python
def run(self):
    if not authenticated:
        return self.redirect("/login")
```

##### json()

```python
json(data: Union[dict, list], status: int = 200) -> Response
```

Возвращает JSON ответ.

**Параметры:**
- `data` (dict|list) — данные для сериализации
- `status` (int) — HTTP статус код

**Возвращает:**
- Flask Response с JSON

**Пример:**
```python
def run(self):
    return self.json({"status": "success", "data": [1, 2, 3]})
```

#### Методы работы с данными

##### abort()

```python
abort(code: int, description: str = None) -> NoReturn
```

Прерывает запрос с HTTP ошибкой.

**Параметры:**
- `code` (int) — HTTP код ошибки
- `description` (str) — описание ошибки

**Пример:**
```python
def run(self, user_id):
    user = database.get_user(user_id)
    if not user:
        self.abort(404, "User not found")
```

##### flash()

```python
flash(message: str, category: str = "info") -> None
```

Добавляет flash сообщение для следующего запроса.

**Параметры:**
- `message` (str) — текст сообщения
- `category` (str) — категория (info, success, warning, error)

**Пример:**
```python
def run(self):
    self.flash("Profile updated successfully", "success")
    return self.redirect("/profile")
```

##### save_file()

```python
save_file(field_name: str, save_path: str) -> bool
```

Сохраняет загруженный файл.

**Параметры:**
- `field_name` (str) — имя поля формы
- `save_path` (str) — путь для сохранения

**Возвращает:**
- `True` если успешно, `False` если ошибка

**Пример:**
```python
def run(self):
    if self.request.method == "POST":
        if self.save_file("avatar", "uploads/avatar.jpg"):
            return self.json({"status": "uploaded"})
    return self.render("upload.html")
```

#### Свойства

##### request

```python
@property
request -> Request
```

Возвращает текущий Flask Request объект.

**Пример:**
```python
def run(self):
    method = self.request.method
    data = self.request.json
    args = self.request.args
```

##### app

```python
@property
app -> App
```

Возвращает экземпляр App.

**Пример:**
```python
def run(self):
    debug = self.app.config.get("debug")
```

##### session

```python
@property
session -> dict
```

Возвращает Flask session объект.

**Пример:**
```python
def run(self):
    self.session["user_id"] = 123
    user_id = self.session.get("user_id")
```

##### client_ip

```python
@property
client_ip -> str
```

Возвращает IP адрес клиента (с учетом прокси).

**Пример:**
```python
def run(self):
    ip = self.client_ip
    log(f"Request from {ip}")
```

---

### Класс API

Специализированный класс для REST API, наследует Screen.

#### HTTP методы

Вместо переопределения `run()`, определите методы для конкретных HTTP операций:

##### get()

```python
def get(self, *args, **kwargs) -> Union[dict, list, tuple]
```

Обрабатывает GET запросы.

**Пример:**
```python
class UsersAPI(API):
    route = "/api/users"
    
    def get(self):
        users = database.get_all_users()
        return {"users": users}
```

##### post()

```python
def post(self, *args, **kwargs) -> Union[dict, list, tuple]
```

Обрабатывает POST запросы.

**Пример:**
```python
def post(self):
    data = self.request.json
    user_id = database.create_user(data)
    return {"id": user_id}, 201
```

##### put()

```python
def put(self, *args, **kwargs) -> Union[dict, list, tuple]
```

Обрабатывает PUT запросы.

##### delete()

```python
def delete(self, *args, **kwargs) -> Union[dict, list, tuple]
```

Обрабатывает DELETE запросы.

##### patch()

```python
def patch(self, *args, **kwargs) -> Union[dict, list, tuple]
```

Обрабатывает PATCH запросы.

#### Вспомогательные методы

##### require_keys()

```python
require_keys(keys: List[str]) -> Tuple[bool, str]
```

Проверяет наличие обязательных ключей в JSON запросе.

**Параметры:**
- `keys` (list) — список обязательных ключей

**Возвращает:**
- `(True, "")` если все ключи присутствуют
- `(False, "missing_key")` если ключ отсутствует

**Пример:**
```python
def post(self):
    ok, missing = self.require_keys(["name", "email", "password"])
    if not ok:
        return {"error": f"Missing field: {missing}"}, 400
    
    # Продолжаем обработку
    data = self.request.json
    return {"status": "created"}, 201
```

##### get_arg()

```python
get_arg(
    key: str,
    type_func: Callable = str,
    default: Any = None
) -> Any
```

Безопасно получает и преобразует query параметр.

**Параметры:**
- `key` (str) — имя параметра
- `type_func` (Callable) — функция преобразования типа
- `default` (Any) — значение по умолчанию

**Возвращает:**
- Преобразованное значение или default

**Пример:**
```python
def get(self):
    # GET /api/users?limit=10&offset=20
    limit = self.get_arg("limit", int, 10)
    offset = self.get_arg("offset", int, 0)
    
    users = database.get_users(limit=limit, offset=offset)
    return {"users": users}
```

---

### Класс Service

Микросервис с изолированными маршрутами и middleware.

#### Конструктор

```python
Service(name: str, prefix: str = "")
```

**Параметры:**
- `name` (str) — имя сервиса
- `prefix` (str) — URL префикс для всех маршрутов

**Пример:**
```python
auth_service = Service("auth", prefix="/api/auth")
```

#### Методы

##### add_screen()

```python
add_screen(path: str, screen_class: Type[Screen]) -> None
```

Добавляет Screen в сервис.

**Параметры:**
- `path` (str) — относительный путь (будет добавлен к prefix)
- `screen_class` (Type[Screen]) — класс Screen

**Пример:**
```python
class LoginAPI(API):
    methods = ["POST"]
    def post(self):
        return {"token": "abc123"}

auth_service.add_screen("/login", LoginAPI)
# Доступно по /api/auth/login
```

##### before_request()

```python
before_request(func: Callable) -> Callable
```

Middleware только для этого сервиса.

**Пример:**
```python
@auth_service.before_request
def check_api_key():
    if not valid_api_key():
        abort(401)
```

##### after_request()

```python
after_request(func: Callable) -> Callable
```

Post-processing только для этого сервиса.

**Пример:**
```python
@auth_service.after_request
def add_auth_headers(response):
    response.headers["X-Auth-Service"] = "v1"
    return response
```

---
