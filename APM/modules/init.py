__help__ = "Регистрация проекта в качестве проекта AEngine"
__module_type__ = "ПРОЕКТЫ"

import json
import os
import cursor
from win2lin import System
from helpers import input, FileInput, register_project
from rich import print


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm init")
        return
    
    if os.path.exists(".apm/run.json"):
        print("[yellow][!] Проект уже инициализирован. Перезаписать конфигурацию? [д/н][/yellow]")
        ans = input("")
        if "д" not in ans and "y" not in ans:
            return
    
    project_name = input("Введите название проекта:")
    if not project_name or not project_name.strip():
        print("[red][-] Название проекта не может быть пустым.[/red]")
        cursor.show()
        return
    
    print()
    
    answer = input("Сменить главный файл проекта с main.py? [д/н]")
    
    if "д" in answer or "y" in answer:
        launch_file = FileInput.select_file()
        if not launch_file:
            print("[yellow][!] Файл не выбран, используется main.py[/yellow]")
            launch_file = "main.py"
    else:
        launch_file = "main.py"
        
    data = {
        "project_name": project_name,
        "main_file": os.path.abspath(launch_file)
    }
    
    try:
        if not os.path.exists(".apm"):
            os.mkdir(".apm")
            
        if not os.path.exists(".apm/installed"):
            os.mkdir(".apm/installed")
            
        with open(".apm/run.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
    except OSError as e:
        print(f"[red][-] Ошибка при сохранении конфигурации: {e}[/red]")
        cursor.show()
        return
    
    # Регистрация проекта в глобальном конфиге
    register_project(gconf_path, project_name, os.getcwd())
    
    System.clear()
    print("[green bold]Проект инициализирован.[/green bold]")
    cursor.show()