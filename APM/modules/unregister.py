__help__ = "Удаление проекта из реестра APM"
__module_type__ = "ПРОЧЕЕ"

import json
import os
import readchar
from rich import print
from win2lin import System


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm unregister")
        return
    
    try:
        with open(gconf_path, encoding="utf-8") as f:
            g_config = json.loads(f.read() or "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        g_config = {}
    
    projects = g_config.get("projects", [])
    
    if not projects:
        print("[yellow]Нет зарегистрированных проектов.[/yellow]")
        return
    
    # Keyboard выбор проекта
    index = 0
    while True:
        System.clear()
        print("[green bold]Какой проект убрать из реестра? [blue](enter - удалить, esc - отмена)[/blue]:[/green bold]\n")
        for i, proj in enumerate(projects):
            name = proj.get("name", "???")
            path = proj.get("path", "???")
            exists = os.path.isdir(path)
            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
            if i == index:
                print(f"[green]> {status} {name}[/green]  [dim]{path}[/dim]")
            else:
                print(f"  {status} [white]{name}[/white]  [dim]{path}[/dim]")
        
        key = readchar.readkey()
        
        if key == readchar.key.UP:
            index = (index - 1) % len(projects)
        elif key == readchar.key.DOWN:
            index = (index + 1) % len(projects)
        elif key == readchar.key.ENTER or key == readchar.key.CR:
            removed = projects.pop(index)
            g_config["projects"] = projects
            try:
                with open(gconf_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(g_config, indent=4, ensure_ascii=False))
                System.clear()
                print(f"[green][+] Проект '{removed['name']}' убран из реестра.[/green]")
                print("[dim]Файлы проекта не удалены.[/dim]")
            except OSError as e:
                System.clear()
                print(f"[red][-] Ошибка сохранения: {e}[/red]")
            return
        elif key == readchar.key.ESC:
            System.clear()
            return
