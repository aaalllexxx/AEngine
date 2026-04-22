__help__ = "Обновить менеджер проектов apm"
__module_type__ = "ПРОЧЕЕ"
import os
import subprocess
from rich import print
from git import Repo, exc
from helpers import clear_dir
from win2lin import System

def run(base_dir, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm update")
        return
    print("[green bold][+] Начало установки исходников...[/green bold]")
    link = "https://github.com/aaalllexxx/APM/"
    config_dir = System.get_config_dir()
    apm_dir = config_dir

    if not os.path.exists(apm_dir):
        print(f"[red][-] Директория APM не найдена: {apm_dir}[/red]")
        return

    for file in os.listdir(apm_dir):
        fl = os.path.join(apm_dir, file)
        try:
            if os.path.isfile(fl) and "apm" not in file:
                os.remove(fl)
            elif os.path.isdir(fl) and "installed" not in file:
                clear_dir(fl)
        except Exception as e:
            print(f"[yellow][!] Не удалось удалить {fl}: {e}[/yellow]")

    sources_dir = os.path.join(apm_dir, "sources")
    if os.path.exists(sources_dir):
        try:
            clear_dir(sources_dir)
        except Exception:
            pass

    try:
        Repo.clone_from(link, sources_dir)
    except exc.GitError as e:
        print(f"[red][-] Ошибка загрузки исходников: {e}[/red]")
        print("[red]    Проверьте подключение к интернету.[/red]")
        return
    
    print("[green bold][+] Исходники установлены [/green bold]")
    print("[green bold][+] Запуск скрипта обновления [/green bold]")
    
    setup_bat = os.path.join(apm_dir, "sources", "scripts", "setup.bat")
    setup_sh = os.path.join(apm_dir, "sources", "scripts", "setup.sh")
    
    try:
        System.run(
            f'cmd.exe /c start "" "{setup_bat}"',
            f'bash "{setup_sh}"'
        )
    except Exception as e:
        print(f"[red][-] Ошибка запуска скрипта обновления: {e}[/red]")
        return
    
    print("[green bold][+] Готово. Дождитесь выполнения скрипта. [/green bold]")