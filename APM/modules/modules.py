__help__ = "Просмотреть список модулей проекта"
__module_type__ = "МОДУЛИ"
import os
from rich import print

def run(base_dir, *args, **kwargs):
    arg = kwargs["args"]
    module = None
    if "-h" in arg:
        print("Usage: apm modules <module_name: (optional)>")
        return
    if len(arg) >= 2:
        module = arg[-1]

    modules = []
    gmodules = []
    local_installed = os.path.join(".apm", "installed")
    global_installed = os.path.join(base_dir, "installed")

    if os.path.exists(local_installed):
        if module is None:
            modules = [
                file.replace(".py", "") for file in os.listdir(local_installed)
                if not file.startswith("__") and (file.endswith(".py") or os.path.isdir(os.path.join(local_installed, file)))
            ]
        else:
            module_dir = os.path.join(local_installed, module)
            if os.path.exists(module_dir):
                modules = [
                    file.replace(".py", "") for file in os.listdir(module_dir)
                    if not file.startswith("__") and (file.endswith(".py") or os.path.isdir(os.path.join(module_dir, file)))
                ]

    if os.path.exists(global_installed):
        if module is None:
            gmodules = [
                file.replace(".py", "") for file in os.listdir(global_installed)
                if not file.startswith("__") and (file.endswith(".py") or os.path.isdir(os.path.join(global_installed, file)))
            ]
        else:
            gmodule_dir = os.path.join(global_installed, module)
            if os.path.exists(gmodule_dir):
                gmodules = [
                    file.replace(".py", "") for file in os.listdir(gmodule_dir)
                    if not file.startswith("__") and (file.endswith(".py") or os.path.isdir(os.path.join(gmodule_dir, file)))
                ]

    print("[blue]Модули проекта:[/blue]")
    if modules:
        for mod in modules:
            print(f"[green] - {mod}[/green]")
    else:
        print("[red][-] Нет установленных модулей[/red]\n")
    print("[blue]Глобальные модули:[/blue]")
    if gmodules:
        for mod in gmodules:
            print(f"[green] - {mod}[/green]")
    else:
        print("[red][-] Нет установленных модулей[/red]\n")
