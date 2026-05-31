# ⚡ AEngine Quick Start

## 🚀 Установка

### 1. Клонирование

```bash
git clone --recursive https://github.com/aaalllexxx/AEngine.git
cd AEngine
```

### 2. Установка APM

```bash
cd APM/scripts
setup.bat  # Windows
# или
./setup.sh  # Linux/Mac
```

## 📝 Создание проекта

```bash
apm create myproject
cd myproject
```

## 💻 Ваше первое приложение

### main.py (синхронный вариант)
```python
from AEngineApps.app import App
from AEngineApps.screen import Screen

class HomeScreen(Screen):
    route = "/"
    
    def run(self):
        return self.render("index.html", title="Hello AEngine!")

app = App("MyApp")
app.load_config("config.json")
app.add_screen("/", HomeScreen)

if __name__ == "__main__":
    app.run()
```

> **Примечание:** В корне проекта AEngine уже есть готовый [`main.py`](main.py) — единая точка входа приложения.

### config.json
```json
{
  "host": "127.0.0.1",
  "port": 5000,
  "debug": true,
  "view": "web"
}
```

### templates/index.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Ваше первое AEngine приложение работает!</p>
</body>
</html>
```

## ▶️ Запуск

```bash
python main.py
```

Откройте http://127.0.0.1:5000

## 🎯 Что дальше?

- **Production?** Читайте [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
- **Полный API?** Читайте [API_REFERENCE.md](API_REFERENCE.md)
- **Безопасность?** Установите `apm install sec`
- **Архитектура?** Читайте [ARCHITECTURE.md](ARCHITECTURE.md)

**Всё! Вы готовы к разработке.**
