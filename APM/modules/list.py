__help__ = "Просмотр списка зарегистрированных проектов"
__module_type__ = "НАВИГАЦИЯ"

import json
import os
from rich import print


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm list")
        return
    
    try:
        with open(gconf_path, encoding="utf-8") as f:
            g_config = json.loads(f.read() or "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        g_config = {}
    
    projects = g_config.get("projects", [])
    
    if not projects:
        print("[yellow]Нет зарегистрированных проектов.[/yellow]")
        print("[yellow]Создайте проект: apm create[/yellow]")
        return
    
    print("[green bold]Зарегистрированные проекты:[/green bold]\n")
    for i, proj in enumerate(projects, 1):
        name = proj.get("name", "???")
        path = proj.get("path", "???")
        exists = os.path.isdir(path)
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        print(f"  {status} {i}) [bold]{name}[/bold]")
        print(f"       [dim]{path}[/dim]")
    
    print(f"\n[dim]Всего проектов: {len(projects)}[/dim]")
