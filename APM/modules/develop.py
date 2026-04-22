__help__ = "Создание шаблонов модулей и экранов"
__module_type__ = "МОДУЛИ"
from rich import print
from helpers import input
import os

TEMPLATES = {
    "module": {
        "description": "Модуль APM",
        "content": '''__help__ = "{name}"
__module_type__ = "МОДУЛИ"
from rich import print


def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm {name}")
        return
    
    print("[green][+] {name} работает[/green]")
'''
    },
    "screen": {
        "description": "Экран AEngineApps",
        "content": '''from AEngineApps.screen import Screen


class {name}(Screen):
    """Экран {name}."""
    
    route = "/{route}"
    methods = ["GET"]
    
    def run(self, *args, **kwargs):
        return self.render("{template}", title="{name}")
'''
    },
    "api": {
        "description": "REST API Эндпоинт",
        "content": '''from AEngineApps.api import API


class {name}(API):
    """API {name}."""
    
    route = "/api/{route}"
    methods = ["GET", "POST"]
    
    def get(self, *args, **kwargs):
        """Обработка GET запроса."""
        return {"status": "ok", "message": "API {name} working"}
        
    def post(self, *args, **kwargs):
        """Обработка POST запроса."""
        data = self.request.json
        return {"received": data}, 201
'''
    },
    "service": {
        "description": "Сервис (Blueprint) AEngineApps",
        "content": '''from AEngineApps.service import Service

# Создание сервиса {name}
# Регистрация в app.py: app.register_service({var_name})
{var_name} = Service("{name_lower}", prefix="/{name_lower}")

# Пример регистрации вложенных компонентов:
# from screens.{name_lower} import {name}Screen
# {var_name}.add_screen("/", {name}Screen)
'''
    }
}


def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg or not arg:
        print("Usage: apm develop <шаблон>")
        print("  module  - создать модуль APM")
        print("  screen  - создать экран AEngineApps")
        print("  api     - создать REST API эндпоинт")
        print("  service - создать сервис AEngineApps")
        return
    
    if "module" in arg:
        name = input("Введите название модуля:")
        if not name or not name.strip():
            print("[red][-] Название не может быть пустым.[/red]")
            return
        content = TEMPLATES["module"]["content"].replace("{name}", name)
        with open(f"{name}.py", "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[green][+] Модуль '{name}.py' создан[/green]")
    
    elif "api" in arg:
        name = input("Введите название API класса (например, UserAPI):")
        if not name or not name.strip():
            print("[red][-] Название не может быть пустым.[/red]")
            return
        
        route = input(f"Маршрут (по умолчанию /{name.lower().replace('api', '')}):")
        if not route:
            route = name.lower().replace('api', '')
        route = route.lstrip("/")
        
        content = TEMPLATES["api"]["content"].replace("{name}", name).replace("{route}", route)
        
        # Сохраняем в screens или api если есть
        target_dir = "api" if os.path.isdir("api") else ("screens" if os.path.isdir("screens") else ".")
        filepath = os.path.join(target_dir, f"{name}.py")
        
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[green][+] API '{filepath}' создан[/green]")

    elif "service" in arg:
        name = input("Введите название сервиса (например, Auth):")
        if not name or not name.strip():
            print("[red][-] Название не может быть пустым.[/red]")
            return
        
        name_lower = name.lower()
        var_name = f"{name_lower}_service"
        
        content = TEMPLATES["service"]["content"].replace("{name}", name).replace("{name_lower}", name_lower).replace("{var_name}", var_name)
        
        target_dir = "services" if os.path.isdir("services") else "."
        filepath = os.path.join(target_dir, f"{name_lower}.py")
        
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[green][+] Сервис '{filepath}' создан[/green]")

    elif "screen" in arg:
        name = input("Введите название экрана (напр. HomeScreen):")
        if not name or not name.strip():
            print("[red][-] Название не может быть пустым.[/red]")
            return
        
        route = input(f"Маршрут (по умолчанию /{name.lower().replace('screen', '')}):")
        if not route:
            route = name.lower().replace('screen', '')
        route = route.lstrip("/")
        
        template_name = name.lower() + ".html"
        
        content = TEMPLATES["screen"]["content"]
        content = content.replace("{name}", name)
        content = content.replace("{route}", route)
        content = content.replace("{template}", template_name)
        
        # Создаём файл экрана
        screen_dir = "screens"
        if os.path.isdir(screen_dir):
            filepath = os.path.join(screen_dir, f"{name}.py")
        else:
            filepath = f"{name}.py"
        
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[green][+] Экран '{filepath}' создан[/green]")
        
        # Создаём HTML шаблон если есть templates/
        templates_dir = "templates"
        if os.path.isdir(templates_dir):
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)
                
            html_path = os.path.join(templates_dir, template_name)
            if not os.path.exists(html_path):
                html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
</head>
<body>
    <h1>{name}</h1>
</body>
</html>'''
                with open(html_path, "w", encoding="utf-8") as file:
                    file.write(html)
                print(f"[green][+] Шаблон '{html_path}' создан[/green]")
    else:
        print("[yellow]Доступные шаблоны: module, screen, api, service[/yellow]")
        print("[dim]Пример: apm develop api[/dim]")
