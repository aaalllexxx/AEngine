__help__ = "Сборка модулей и артефактов"
__module_type__ = "МОДУЛИ"

import os
from rich import print

from helpers import build_module_archive, expand_local_path, input


def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg or "--help" in arg:
        print(
            "Usage: apm build module [source_dir] [--output file.zip] [--no-input] "
            "[--auto] [--auto-aliases] [--auto-deps] [--auto-services]"
        )
        return

    if len(arg) < 2 or arg[1] != "module":
        print("[yellow]Доступно: apm build module[/yellow]")
        return

    source_dir = None
    output_path = None
    interactive = "--no-input" not in arg
    auto_all = "--auto" in arg
    auto_aliases = auto_all or "--auto-aliases" in arg
    auto_dependencies = auto_all or "--auto-deps" in arg
    auto_services = auto_all or "--auto-services" in arg

    positional = []
    skip_next = False
    for idx, item in enumerate(arg[2:], start=2):
        if skip_next:
            skip_next = False
            continue
        if item == "--no-input":
            continue
        if item in {"--auto", "--auto-aliases", "--auto-deps", "--auto-services"}:
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
            auto_services=auto_services,
        )
    except Exception as exc:
        print(f"[red][-] Ошибка сборки модуля: {exc}[/red]")
        return

    print(f"[green][+] Архив модуля создан: {archive_path}[/green]")
