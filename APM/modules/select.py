__help__ = "Выбор проекта в качестве глобального"
__module_type__ = "ПРОЕКТЫ"

import os
from json_dict import JsonDict
from rich import print


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm select")
        return
    if os.path.isdir(".apm"):
        if not os.path.exists(".apm/run.json"):
            print("[red][-] Файл .apm/run.json не найден. Запустите 'apm init' сначала.[/red]")
            return
        try:
            config = JsonDict(gconf_path)
            local_config = JsonDict(".apm/run.json")
            config.project_name = local_config.project_name
            config.main_file = local_config.main_file
            print("[green][+] Проект помечен основным[/green]")
        except Exception as e:
            print(f"[red][-] Ошибка при чтении конфигурации: {e}[/red]")
    else:
        print("[red][-] Текущая директория не является проектом AEngine.[/red]")
        print("[red][-] Используйте 'apm init' для инициализации.[/red]")