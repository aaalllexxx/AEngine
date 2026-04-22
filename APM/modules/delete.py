__help__ = "Удаление проекта"
__module_type__ = "ПРОЕКТЫ"
import os
import shutil
from helpers import input
from rich import print
from helpers import clear_dir

def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm delete")
        return
    if os.path.isdir(".apm"):
        dir_name = os.getcwd()
        ans = input(f"Удалить проект '{os.path.basename(dir_name)}'? Это действие нельзя отменить. [д/н]")
        if "д" not in ans and "y" not in ans:
            print("[yellow][!] Удаление отменено.[/yellow]")
            return
        os.chdir(os.path.dirname(dir_name))
        try:
            clear_dir(dir_name)
            print("[green][+] Проект удалён.[/green]")
        except PermissionError:
            print("[red][-] Не получилось удалить все файлы.\nВозможно что-то придется удалить вручную.[/red]")
        except OSError as e:
            print(f"[red][-] Ошибка при удалении: {e}[/red]")
    else:
        print("[red][-] Текущая директория не является проектом AEngine.[/red]")
        print("[red][-] Используйте 'apm init' для инициализации.[/red]")