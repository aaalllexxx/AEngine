# Руководство разработчика AEngine

Полное руководство для разработчиков, желающих внести вклад в проект AEngine.

## Содержание

- [Начало работы](#начало-работы)
- [Структура проекта](#структура-проекта)
- [Стандарты кодирования](#стандарты-кодирования)
- [Разработка компонентов](#разработка-компонентов)
- [Тестирование](#тестирование)
- [Отладка](#отладка)
- [Документация](#документация)
- [Pull Request процесс](#pull-request-процесс)

---

## Начало работы

### Настройка окружения разработки

#### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/AEngine.git
cd AEngine
```

#### 2. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Установка зависимостей

```bash
# Основные зависимости
pip install -r AEngineApps/requirements.txt
pip install -r APM/requirements.txt

# Зависимости для разработки
pip install pytest pytest-cov black flake8 mypy
```

#### 4. Установка APM в режиме разработки

```bash
cd APM/scripts
# Windows
setup.bat

# Linux/macOS
chmod +x setup.sh
./setup.sh
```

---

## Структура проекта

### Основные директории

```
AEngine/
├── AEngineApps/          # Фреймворк
│   ├── app.py            # Класс App
│   ├── screen.py         # Класс Screen
│   ├── api.py            # Класс API
│   ├── service.py        # Класс Service
│   ├── async_app.py      # Асинхронная версия
│   ├── async_screen.py   # Асинхронная версия
│   ├── global_storage.py # Singleton хранилище
│   └── json_dict.py      # JSON обертка
│
├── APM/                  # Package Manager
│   ├── apm.py            # CLI entry point
│   ├── modules/          # Команды
│   │   ├── create.py
│   │   ├── install.py
│   │   ├── build.py
│   │   └── ...
│   ├── helpers.py        # Вспомогательные функции
│   └── scripts/          # Установочные скрипты
│
├── sec/                  # Security Module
│   ├── intrusions.py     # IDS/IPS
│   ├── code_signer.py    # Подпись кода
│   ├── os_protect.py     # Защита ОС
│   ├── net_analyzer.py   # Анализ сети
│   ├── sys_protect.py    # Системная защита
│   ├── cluster.py        # Кластеризация
│   ├── auto_cluster.py   # Локальный кластер
│   ├── dashboard.py      # Админ-панель
│   └── logs.py           # Анализ логов
│
└── tests/                # Тесты
    ├── conftest.py
    ├── test_app.py
    ├── test_screen.py
    └── ...
```

### Файлы конфигурации

- `.gitignore` — игнорируемые файлы
- `pytest.ini` — конфигурация pytest
- `setup.py` — установочный скрипт (если есть)
- `requirements.txt` — зависимости

---

## Стандарты кодирования

### Python Style Guide

Мы стремимся следовать **PEP 8**, но пока не применяем его строго. Это цель для будущих версий.

**Рекомендации (не строгие требования):**

#### Форматирование

```python
# Используем 4 пробела для отступов
def my_function():
    pass

# Максимальная длина строки: 100 символов
# (не 79, как в PEP 8, для удобства)

# Пустые строки
class MyClass:
    """Docstring класса."""
    
    def __init__(self):
        """Docstring метода."""
        pass
    
    def method(self):
        """Еще один метод."""
        pass
```

#### Именование

```python
# Классы: PascalCase
class MyScreen(Screen):
    pass

# Функции и методы: snake_case
def get_user_data():
    pass

# Константы: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100

# Приватные методы: _leading_underscore
def _internal_method():
    pass

# Переменные: snake_case
user_name = "John"
```

#### Импорты

```python
# Порядок импортов:
# 1. Стандартная библиотека
import os
import sys
from typing import List, Dict

# 2. Сторонние библиотеки
import flask
from flask import request, jsonify

# 3. Локальные импорты
from AEngineApps.screen import Screen
from AEngineApps.api import API
```

### Docstrings

Используем **Google Style** docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """Краткое описание функции.
    
    Более подробное описание того, что делает функция,
    если необходимо.
    
    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра
    
    Returns:
        Описание возвращаемого значения
    
    Raises:
        ValueError: Когда param2 отрицательный
    
    Example:
        >>> complex_function("test", 5)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be positive")
    return True
```

### Type Hints

Используем type hints везде, где возможно:

```python
from typing import List, Dict, Optional, Union, Callable

def process_data(
    data: List[Dict[str, str]],
    callback: Optional[Callable] = None
) -> Union[str, None]:
    """Обрабатывает данные."""
    if callback:
        callback(data)
    return "processed"
```

### Проверка кода (опционально)

Эти инструменты помогут улучшить качество кода, но их использование не обязательно:

```bash
# Black для автоформатирования (опционально)
black AEngineApps/ APM/ sec/

# Flake8 для проверки стиля (опционально)
flake8 AEngineApps/ APM/ sec/ --max-line-length=100

# MyPy для проверки типов (опционально)
mypy AEngineApps/ --ignore-missing-imports
```

**Примечание:** В будущих версиях планируется строгое соблюдение PEP 8.

---

## Разработка компонентов

### Добавление нового Screen класса

```python
# AEngineApps/screen.py

class NewFeatureScreen(Screen):
    """Новая функциональность.
    
    Attributes:
        route: URL маршрут
        methods: Разрешенные HTTP методы
    """
    
    route = "/new-feature"
    methods = ["GET", "POST"]
    
    def run(self) -> str:
        """Обрабатывает запрос.
        
        Returns:
            HTML ответ
        """
        if self.request.method == "POST":
            # Обработка POST
            data = self.request.form
            return self.json({"status": "success"})
        
        # Обработка GET
        return self.render("new_feature.html")
```

### Добавление команды APM

```python
# APM/modules/my_command.py

"""
Модуль для новой команды APM.
"""

def execute(args):
    """Выполняет команду.
    
    Args:
        args: Аргументы командной строки (argparse.Namespace)
    """
    print("Executing my_command...")
    # Ваша логика здесь

def setup_parser(subparsers):
    """Настраивает парсер аргументов.
    
    Args:
        subparsers: Subparsers объект argparse
    """
    parser = subparsers.add_parser(
        'my_command',
        help='Описание команды'
    )
    parser.add_argument(
        '--option',
        help='Опция команды'
    )
```

### Добавление детектора безопасности

```python
# sec/my_detector.py

from AEngineApps.intrusions import BaseDetector, _get_all_input_values
from flask import request
from urllib.parse import unquote

class MyCustomDetector(BaseDetector):
    """Детектор для специфической атаки.
    
    Обнаруживает паттерны атаки в входных данных.
    """
    
    # Паттерны для обнаружения
    PATTERNS = [
        "malicious_pattern",
        "another_pattern"
    ]
    
    def run(self):
        """Выполняет проверку запроса."""
        for value in _get_all_input_values():
            decoded = unquote(value).lower()
            
            for pattern in self.PATTERNS:
                if pattern in decoded:
                    self.log(
                        f"MyCustomDetector: Detected {pattern} "
                        f"in {request.url}"
                    )
                    self.trigger_response()
                    return
```

---

## Тестирование

### Структура тестов

```python
# tests/test_my_feature.py

import pytest
from AEngineApps.app import App
from AEngineApps.screen import Screen

class TestMyFeature:
    """Тесты для новой функциональности."""
    
    @pytest.fixture
    def app(self):
        """Создает тестовое приложение."""
        app = App("TestApp", debug=True)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Создает тестовый клиент."""
        return app.flask_app.test_client()
    
    def test_basic_functionality(self, client):
        """Тестирует базовую функциональность."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_post_request(self, client):
        """Тестирует POST запрос."""
        response = client.post('/api/test', json={"key": "value"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
```

### Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_app.py

# С покрытием
pytest --cov=AEngineApps --cov=APM --cov=sec

# С подробным выводом
pytest -v

# Остановка на первой ошибке
pytest -x
```

### Покрытие кода

```bash
# Генерация отчета покрытия
pytest --cov=AEngineApps --cov-report=html

# Открыть отчет
# Windows
start htmlcov/index.html

# Linux/macOS
open htmlcov/index.html
```

---

## Отладка

### Использование отладчика

```python
# Встроенный отладчик Python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # Точка останова
    y = x * 2
    return y
```

### Логирование

```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

### Отладка Flask приложений

```python
# Включить режим отладки
app = App("MyApp", debug=True)

# Или через конфигурацию
app.config["debug"] = True
```

---

## Документация

### Документирование кода

Каждый модуль, класс и функция должны иметь docstring:

```python
"""
Модуль для работы с пользователями.

Этот модуль предоставляет функции для создания,
обновления и удаления пользователей.
"""

class UserManager:
    """Менеджер пользователей.
    
    Управляет жизненным циклом пользователей в системе.
    
    Attributes:
        database: Подключение к базе данных
        cache: Кеш пользователей
    """
    
    def __init__(self, database):
        """Инициализирует менеджер.
        
        Args:
            database: Объект подключения к БД
        """
        self.database = database
        self.cache = {}
```

### Обновление документации

При добавлении новой функциональности обновите:

1. **README.md** — если это крупная функция
2. **API_REFERENCE.md** — для новых классов/методов
3. **ARCHITECTURE.md** — для архитектурных изменений
4. **CHANGELOG.md** — всегда добавляйте запись

---

## Pull Request процесс

### 1. Создание ветки

```bash
# Создайте ветку от main
git checkout -b feature/my-new-feature

# Или для исправления
git checkout -b fix/bug-description
```

### 2. Разработка

- Пишите чистый код
- Добавляйте тесты
- Обновляйте документацию
- Делайте частые коммиты

```bash
git add .
git commit -m "feat: Add new feature X"
```

### 3. Conventional Commits

Используем формат:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Новая функция
- `fix`: Исправление бага
- `docs`: Документация
- `style`: Форматирование
- `refactor`: Рефакторинг
- `test`: Тесты
- `chore`: Рутинные задачи

**Примеры:**

```bash
git commit -m "feat(app): Add support for async screens"
git commit -m "fix(security): Fix SQL injection in detector"
git commit -m "docs(readme): Update installation instructions"
```

### 4. Проверка перед отправкой

```bash
# Форматирование
black .

# Проверка стиля
flake8 .

# Тесты
pytest

# Проверка типов
mypy AEngineApps/
```

### 5. Push и создание PR

```bash
git push origin feature/my-new-feature
```

Затем на GitHub:
1. Создайте Pull Request
2. Заполните описание
3. Свяжите с issue (если есть)
4. Дождитесь review

### 6. Code Review

Ожидайте комментарии от мейнтейнеров:
- Отвечайте на вопросы
- Вносите исправления
- Обновляйте PR

```bash
# Внесите изменения
git add .
git commit -m "fix: Address review comments"
git push origin feature/my-new-feature
```

---

## Полезные команды

### Git

```bash
# Обновить main
git checkout main
git pull origin main

# Rebase вашей ветки
git checkout feature/my-feature
git rebase main

# Squash коммитов
git rebase -i HEAD~3

# Отменить последний коммит
git reset --soft HEAD~1
```

### Python

```bash
# Создать requirements.txt
pip freeze > requirements.txt

# Установить из requirements.txt
pip install -r requirements.txt

# Обновить все пакеты
pip list --outdated
pip install --upgrade package_name
```

### APM

```bash
# Создать тестовый проект
apm create

# Запустить проект
apm run

# Собрать проект
apm build
```

---

## Ресурсы

### Документация

- [Python Documentation](https://docs.python.org/3/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)

### Инструменты

- [Black](https://black.readthedocs.io/) — форматирование
- [Flake8](https://flake8.pycqa.org/) — линтер
- [MyPy](https://mypy.readthedocs.io/) — проверка типов
- [pytest](https://docs.pytest.org/) — тестирование

### Сообщество

- GitHub Issues — для багов и предложений
- GitHub Discussions — для вопросов
- Telegram — @aengine_community

---

## Заключение

Спасибо за интерес к разработке AEngine! Ваш вклад делает проект лучше.

Если у вас есть вопросы:
- Создайте issue на GitHub
- Напишите в Telegram
- Отправьте email: dev@aengine.dev

Удачи в разработке! 🚀
