__help__ = "Создание шаблонов модулей и экранов"
__module_type__ = "МОДУЛИ"
from rich import print
from helpers import input
import os

TEMPLATES = {
    "module": {
        "description": "Модуль APM",
        "content": '''__help__ = "{name}"
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
    }
}


def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm develop <шаблон>")
        print("  module - создать модуль APM")
        print("  screen - создать экран AEngineApps")
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
    
    elif "screen" in arg:
        name = input("Введите название экрана (напр. HomeScreen):")
        if not name or not name.strip():
            print("[red][-] Название не может быть пустым.[/red]")
            return
        
        route = input(f"Маршрут (по умолчанию /{name.lower()}):")
        if not route:
            route = name.lower()
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
            html_path = os.path.join(templates_dir, template_name)
            if not os.path.exists(html_path):
                html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
    <link rel="stylesheet" href="{{{{ url_for('static', filename='style.css') }}}}">
</head>
<body>
    <h1>{name}</h1>
</body>
</html>'''
                with open(html_path, "w", encoding="utf-8") as file:
                    file.write(html)
                print(f"[green][+] Шаблон '{html_path}' создан[/green]")
    else:
        print("[yellow]Доступные шаблоны: module, screen[/yellow]")
        print("[dim]Пример: apm develop screen[/dim]")
