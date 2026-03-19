# ⚡ AEngine Quick Start

## 🚀 Установка

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

### main.py
```python
from AEngineApps.async_app import AsyncApp
from AEngineApps.async_screen import AsyncScreen

class HomeScreen(AsyncScreen):
    route = "/"
    
    async def run(self):
        return await self.render("index.html", title="Hello AEngine!")

app = AsyncApp("MyApp")
app.load_config("config.json")
app.add_screen("/", HomeScreen)

if __name__ == "__main__":
    app.run()
```

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

- **Простые проекты?** Используйте синхронный `App` (см. AEngineApps/readme.md)
- **Production?** Читайте PRODUCTION_GUIDE.md
- **Безопасность?** Установите `apm install sec`

**Всё! Вы готовы к разработке.**
