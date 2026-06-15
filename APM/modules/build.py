__help__ = "Сборка модулей и деплой-артефактов"
__module_type__ = "МОДУЛИ"

import os
from rich import print

from helpers import (
    build_module_archive,
    expand_local_path,
    generate_docker_artifacts,
    input,
)


USAGE = (
    "Usage:\n"
    "  apm build module [source_dir] [--output file.zip] [--no-input] "
    "[--auto] [--auto-aliases] [--auto-deps]\n"
    "  apm build docker [project_dir] [--output dir] [--port N] [--force]"
)


def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg or "--help" in arg:
        print(USAGE)
        return

    if len(arg) < 2:
        print("[yellow]Доступно: apm build module | apm build docker[/yellow]")
        return

    sub = arg[1]
    if sub == "module":
        _build_module(arg)
    elif sub == "docker":
        _build_docker(arg)
    else:
        print("[yellow]Доступно: apm build module | apm build docker[/yellow]")


def _build_module(arg):
    source_dir = None
    output_path = None
    interactive = "--no-input" not in arg
    auto_all = "--auto" in arg
    auto_aliases = auto_all or "--auto-aliases" in arg
    auto_dependencies = auto_all or "--auto-deps" in arg

    positional = []
    skip_next = False
    for idx, item in enumerate(arg[2:], start=2):
        if skip_next:
            skip_next = False
            continue
        if item == "--no-input":
            continue
        if item in {"--auto", "--auto-aliases", "--auto-deps"}:
            continue
        if item == "--output":
            if idx + 1 >= len(arg):
                print("[red][-] Не указан путь после --output[/red]")
                return
            output_path = arg[idx + 1]
            skip_next = True
            continue
        positional.append(item)

    if positional:
        source_dir = positional[0]
    else:
        source_dir = input("Введите путь к папке модуля (по умолчанию текущая директория):") or "."

    source_dir = expand_local_path(source_dir)
    module_name = os.path.basename(source_dir.rstrip("/\\"))
    if not output_path:
        output_path = os.path.join(os.getcwd(), f"{module_name}.apm.zip")

    try:
        archive_path = build_module_archive(
            source_dir,
            output_path,
            interactive=interactive,
            auto_aliases=auto_aliases,
            auto_dependencies=auto_dependencies,
        )
    except Exception as exc:
        print(f"[red][-] Ошибка сборки модуля: {exc}[/red]")
        return

    print(f"[green][+] Архив модуля создан: {archive_path}[/green]")


def _build_docker(arg):
    """apm build docker — генерирует Dockerfile, docker-compose.yml и requirements.txt."""
    project_dir = None
    output_dir = None
    port = None
    force = "--force" in arg

    skip_next = False
    for idx, item in enumerate(arg[2:], start=2):
        if skip_next:
            skip_next = False
            continue
        if item == "--force":
            continue
        if item == "--output":
            if idx + 1 >= len(arg):
                print("[red][-] Не указан путь после --output[/red]")
                return
            output_dir = arg[idx + 1]
            skip_next = True
            continue
        if item == "--port":
            if idx + 1 >= len(arg):
                print("[red][-] Не указан порт после --port[/red]")
                return
            try:
                port = int(arg[idx + 1])
            except ValueError:
                print("[red][-] Порт должен быть числом[/red]")
                return
            skip_next = True
            continue
        if project_dir is None:
            project_dir = item

    project_dir = project_dir or "."

    try:
        created, skipped = generate_docker_artifacts(
            project_dir, output_dir=output_dir, force=force, port=port
        )
    except Exception as exc:
        print(f"[red][-] Ошибка генерации deploy-артефактов: {exc}[/red]")
        return

    for path in created:
        print(f"[green][+] Создан {path}[/green]")
    for path in skipped:
        print(f"[yellow][!] Пропущен (уже существует) {path} — используйте --force для перезаписи[/yellow]")
    if created:
        print("[green bold][+] Готово![/green bold] Для запуска: [cyan]docker compose up --build[/cyan]")
