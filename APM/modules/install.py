__help__ = "Установка программных модулей"
__module_type__ = "МОДУЛИ"
import os
from rich import print
from rich.table import Table
from rich.panel import Panel
from helpers import (
    assemble_module_package,
    clear_dir,
    detect_module_name_from_source,
    input,
    install_module_source,
    install_python_dependencies,
    is_probable_local_path,
    load_module_manifest,
    normalize_repo_url,
)

import subprocess

def _process_install_commands(commands, title, warning=None):
    if not commands:
        return True

    print(f"\n[bold cyan]--- {title} ---[/bold cyan]")
    if warning:
        print(f"[bold red]{warning}[/bold red]")

    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Команда", style="white", overflow="fold")
    
    for i, cmd in enumerate(commands, 1):
        table.add_row(str(i), cmd)
    
    print(table)
    
    print("\n[bold yellow]Выберите действие:[/bold yellow]")
    print("  [green][A][/green] - Выполнить ВСЕ команды")
    print("  [cyan][S][/cyan] - Выполнять пошагово (с подтверждением)")
    print("  [red][C][/red] - Пропустить / Отмена")
    
    choice = (input("Ваш выбор [A/s/c]:") or "s").strip().lower()
    
    if choice in {"c", "n", "no"}:
        print(f"[yellow][!] {title} пропущены.[/yellow]")
        return True
    
    run_all = choice in {"a", "all", "в", "все"}
    
    for i, cmd in enumerate(commands, 1):
        should_run = True
        if not run_all:
            confirm = (input(f"[{i}/{len(commands)}] Выполнить '{cmd}'? [Y/n/skip/abort]:") or "y").strip().lower()
            if confirm == "abort":
                print("[red][-] Установка прервана пользователем.[/red]")
                return False
            if confirm in {"n", "skip"}:
                print(f"[yellow][!] Пропущено: {cmd}[/yellow]")
                should_run = False
        
        if should_run:
            print(f"[blue][*] ({i}/{len(commands)}) Выполнение: {cmd}[/blue]")
            try:
                subprocess.run(cmd, shell=True, check=True)
                print("[green][+] Готово[/green]")
            except Exception as e:
                print(f"[red][-] Ошибка при выполнении: {e}[/red]")
                cont = (input("Продолжить установку дальше? [Y/n]:") or "y").strip().lower()
                if cont not in {"y", "yes", "д", "да"}:
                    print("[red][-] Установка прервана.[/red]")
                    return False
    return True

def run(base_dir, *args, **kwargs):
    arg:list = kwargs["args"]
    if "-h" in arg:
        print(
            "Usage: apm install <source>\n"
            "    source: локальная папка | архив .zip/.tar.* | github url | owner repo | shorthand вроде sec\n"
            "    -u - Обновить указанный модуль\n"
            "    -g - Установить модуль глобально"
        )
        return
    update = "-u" in arg
    if update:
        arg.remove("-u")
    local_only = "-l" in arg or "--local" in arg
    if "-l" in arg:
        arg.remove("-l")
    if "--local" in arg:
        arg.remove("--local")

    if "--path" in arg:
        try:
            source = arg[arg.index("--path") + 1]
        except (IndexError, ValueError):
            print("[red][-] Не указан путь после --path.[/red]")
            return
    elif "--url" in arg:
        try:
            source = arg[arg.index("--url") + 1]
        except (IndexError, ValueError):
            print("[red][-] Не указан URL после --url.[/red]")
            return
    elif len(arg) >= 2:
        source = arg[-1]
    else:
        source = ""
    
    if not source and len(arg) >= 3:
        source = f"{arg[-2]}/{arg[-1]}"
    if not source:
        print("[red][-] Не указан источник модуля.[/red]")
        print("[yellow]Использование: apm install <path|archive|url|owner repo>[/yellow]")
        return

    if local_only and not is_probable_local_path(source):
        print("[red][-] Флаг -l/--local требует локальную папку или архив.[/red]")
        return

    name = detect_module_name_from_source(source)
    if not name:
        print("[red][-] Не удалось определить имя модуля из источника.[/red]")
        return
    
    path = os.path.join(".apm", "installed")
    if "-g" in arg:
        arg.remove("-g")
        path = os.path.join(base_dir, "installed")
    
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            print(f"[red][-] Не удалось создать директорию: {e}[/red]")
            return
    
    try:
        module_dir = os.path.join(path, name)
        if update and os.path.exists(module_dir):
            clear_dir(module_dir)
        print(f"[green][+] Загрузка модуля '{name}'...[/green]")
        local_source = os.path.join(os.path.dirname(base_dir.rstrip(os.sep)), name)
        install_module_source(source, module_dir, local_source=local_source)
    except Exception as e:
        pretty_source = normalize_repo_url(source) if not is_probable_local_path(source) else source
        print(f"[red][-] Ошибка загрузки: {pretty_source}[/red]")
        print(f"[red]    {e}[/red]")
        print(f"[red]    Убедитесь, что путь/архив/URL верный и есть доступ к источнику.[/red]")
        return
    
    try:
        git_dir = os.path.join(path, name, ".git")
        if os.path.exists(git_dir):
            clear_dir(git_dir)
    except Exception as e:
        print(f"[yellow][!] Не удалось удалить .git: {e}[/yellow]")

    manifest = load_module_manifest(module_dir)
    if manifest:
        copied = assemble_module_package(module_dir, os.getcwd(), manifest)
        if copied:
            print(f"[green][+] Файлы модуля собраны в проект: {len(copied)}[/green]")

        installed, failed = install_python_dependencies(manifest.get("dependencies", {}).get("python", []))
        if installed:
            print(f"[green][+] Установлены Python-зависимости: {', '.join(installed)}[/green]")
        for item in failed:
            print(f"[yellow][!] Не удалось установить зависимость {item['dependency']}[/yellow]")
            if item["error"]:
                print(f"[yellow]    {item['error']}[/yellow]")
            answer = (input("Продолжить установку модуля без этой зависимости? [Y/n]:") or "y").strip().lower()
            if answer not in {"", "y", "yes", "д", "да"}:
                print("[red][-] Установка прервана пользователем.[/red]")
                return

        if not _process_install_commands(
            manifest.get("dependencies", {}).get("system", []),
            "Системные шаги / зависимости"
        ):
            return

        if not _process_install_commands(
            manifest.get("install_commands", []),
            "Команды установки модуля",
            warning="[!] ВНИМАНИЕ: Проверьте команды перед запуском. Они могут изменить вашу систему."
        ):
            return
    
    print("[green][+] Модуль установлен[/green]")
