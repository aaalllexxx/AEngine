__help__ = "удаляет загруженный модуль"
__module_type__ = "МОДУЛИ"
import os
from helpers import clear_dir
from rich import print

def run(base_dir, *args, **kwargs):
    arg: list = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm remove <flags> <name>\n    -g - Удаление глобального модуля")
        return
    
    if len(arg) < 2:
        print("[red][-] Не указано имя модуля.[/red]")
        print("[yellow]Использование: apm remove <name>[/yellow]")
        return
    
    module = arg[-1]
    path = ".apm/installed"
    if "-g" in arg:
        arg.pop(arg.index("-g"))
        path = os.path.join(base_dir, "installed")
    elif not os.path.exists(".apm"):
        print("[red][-] Директория не является проектом apm[/red]")
        return
    
    module_path = os.path.join(path, module)
    if not os.path.exists(module_path):
        print(f"[red][-] Модуль '{module}' не найден[/red]")
        return
    
    try:
        clear_dir(module_path)
        print("[green][+] Модуль удален[/green]")
    except OSError as e:
        print(f"[red][-] Ошибка при удалении модуля: {e}[/red]")