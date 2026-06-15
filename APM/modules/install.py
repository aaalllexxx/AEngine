__help__ = "Установка программных модулей"
__module_type__ = "МОДУЛИ"
import os
from rich import print
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
    # Разбираем флаг области видимости ДО определения источника,
    # иначе `apm install sec -g` примет "-g" за источник.
    global_install = "-g" in arg
    if global_install:
        arg.remove("-g")

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
    
    # Локальная область — модули проекта (<cwd>/.apm/installed),
    # глобальная (-g) — рядом с APM (APM/installed), доступна из любого проекта.
    if global_install:
        path = os.path.join(base_dir, "installed")
    else:
        path = os.path.join(os.getcwd(), ".apm", "installed")

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
        # При глобальной установке файлы модуля НЕ копируются в текущий проект —
        # глобально регистрируется только команда (доступная из любого проекта).
        if global_install:
            print("[cyan][i] Глобальная установка: команда доступна из любого проекта "
                  "(файлы в текущий проект не копируются).[/cyan]")
        else:
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

        system_requirements = manifest.get("dependencies", {}).get("system", [])
        if system_requirements:
            print("[yellow][!] Требуются ручные системные шаги:[/yellow]")
            for item in system_requirements:
                print(f"[yellow]    - {item}[/yellow]")
    
    print("[green][+] Модуль установлен[/green]")
