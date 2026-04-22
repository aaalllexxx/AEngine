__help__ = "Создание файла конфигураций для проекта"
__module_type__ = "ПРОЕКТЫ"

import json
import os
from rich import print
from helpers import ConfigInput
from win2lin import System

def run(base_dir, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm config")
        return
    
    if not os.path.isdir(".apm"):
        print("[red][-] Текущая директория не является проектом AEngine.[/red]")
        print("[red][-] Используйте 'apm init' для инициализации.[/red]")
        return
    
    template_path = os.path.join(base_dir, "config_template.json")
    if not os.path.exists(template_path):
        print(f"[red][-] Шаблон конфигурации не найден: {template_path}[/red]")
        return
    
    existing = {}
    if os.path.exists("config.json"):
        try:
            with open("config.json", encoding="utf-8") as f:
                existing = json.loads(f.read())
        except (json.JSONDecodeError, OSError):
            pass
    
    try:
        config = ConfigInput.start(template_path, existing)
        if config:
            with open("config.json", "w", encoding="utf-8") as file:
                file.write(json.dumps(config, indent=4, ensure_ascii=False))
            System.clear()
            print("[green][+] Файл создан[/green]")
        else:
            System.clear()
            print("[yellow][!] Конфигурация не была сохранена.[/yellow]")
    except KeyboardInterrupt:
        System.clear()
        print("[red][-] Завершаю работу...[/red]")
    except Exception as e:
        System.clear()
        print(f"[red][-] Ошибка: {e}[/red]")