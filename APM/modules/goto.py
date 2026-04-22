__help__ = "Перейти в директорию проекта"
__module_type__ = "НАВИГАЦИЯ"

import json
import os
import tempfile
import readchar
from rich import print
from win2lin import System


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm goto")
        return
    
    # Загружаем список проектов из глобальной конфигурации
    try:
        with open(gconf_path, encoding="utf-8") as f:
            g_config = json.loads(f.read() or "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        g_config = {}
    
    projects = g_config.get("projects", [])
    
    # Убираем несуществующие проекты
    projects = [p for p in projects if os.path.isdir(p.get("path", ""))]
    
    if not projects:
        print("[red][-] Нет зарегистрированных проектов.[/red]")
        print("[yellow]Создайте проект: apm create[/yellow]")
        return
    
    # Выбор проекта в keyboard режиме
    index = 0
    while True:
        System.clear()
        print("[green bold]Выберите проект [blue bold](enter - перейти, esc - отмена)[/blue bold]:[/green bold]\n")
        for i, proj in enumerate(projects):
            name = proj.get("name", "???")
            path = proj.get("path", "???")
            if i == index:
                print(f"[green]> {name}[/green]  [dim]{path}[/dim]")
            else:
                print(f"  [white]{name}[/white]  [dim]{path}[/dim]")
        
        key = readchar.readkey()
        
        if key == readchar.key.UP:
            index = (index - 1) % len(projects)
        elif key == readchar.key.DOWN:
            index = (index + 1) % len(projects)
        elif key == readchar.key.ENTER or key == readchar.key.CR:
            selected = projects[index]
            target_path = selected["path"]
            
            # Записываем путь во временный файл для apm.bat / apm.sh
            tmp = os.path.join(tempfile.gettempdir(), "apm_goto.tmp")
            enc = "oem" if os.name == "nt" else "utf-8"
            with open(tmp, "w", encoding=enc) as f:
                f.write(target_path)
            
            System.clear()
            print(f"[green][+] Переход в проект '{selected['name']}'[/green]")
            return
        elif key == readchar.key.ESC:
            System.clear()
            return
