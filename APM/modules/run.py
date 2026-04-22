__help__ = "Запуск проекта AEngine"
__module_type__ = "ПРОЕКТЫ"


import json
import os
import sys

from rich import print
from helpers import System, input, FileInput


def run(base_dir, gconf_path, *args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm run")
        return
    
    try:
        with open(gconf_path, encoding="utf-8") as file_config:
            g_config = json.loads(file_config.read() or "{}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[red][-] Ошибка чтения глобальной конфигурации: {e}[/red]")
        g_config = {}
                
    if os.path.exists(".apm/run.json"):
        try:
            with open(".apm/run.json", encoding="utf-8") as file:
                data = json.loads(file.read())
        except json.JSONDecodeError as e:
            print(f"[red][-] Ошибка чтения .apm/run.json: {e}[/red]")
            return
    
    elif g_config.get("project_name"):
        data = g_config
    
    else:
        print("[red][-] Текущая директория не является проектом AEngine.[/red]")
        print("[red][-] Используйте 'apm init' или 'apm select' в проекте.[/red]")
        return
    
    if "project_name" not in data:
        print("[red][-] В конфигурации не указано имя проекта (project_name).[/red]")
        return
    
    if "main_file" not in data:
        print("[red][-] В конфигурации не указан главный файл (main_file).[/red]")
        return

    print(f"[green][+] Запуск проекта '{data['project_name']}'...[/green]")
    try:
        interpreter = g_config.get("interpreter")
        
        # Проверяем, существует ли указанный интерпретатор
        if interpreter and not os.path.exists(interpreter):
            print(f"[yellow][!] Указанный интерпретатор не найден: {interpreter}[/yellow]")
            interpreter = None
            
        interpreter_win = interpreter or sys.executable or "python"

        # На Linux по умолчанию используем текущий интерпретатор, затем venv от apm
        apm_venv = os.path.expanduser("~/.config/apm/venv/bin/python3")
        interpreter_lin = interpreter or sys.executable or (apm_venv if os.path.exists(apm_venv) else "python3")
        
        main_file = data["main_file"]
        
        # Если путь абсолютный и файл не существует - пробуем найти его в текущей папке
        if os.path.isabs(main_file) and not os.path.exists(main_file):
            filename = os.path.basename(main_file)
            if os.path.exists(filename):
                main_file = filename
        
        # Настройка PYTHONPATH для нахождения AEngineApps (в корне проекта или выше)
        env = os.environ.copy()
        project_root = os.getcwd() # Текущая директория проекта (например, test/)
        parent_dir = os.path.dirname(project_root) # Корень AEngine (где лежит AEngineApps)
        
        # Добавляем в PYTHONPATH текущую директорию и ее родителя
        new_paths = [project_root, parent_dir]
        current_pythonpath = env.get("PYTHONPATH", "")
        if current_pythonpath:
            new_paths.append(current_pythonpath)
        
        env["PYTHONPATH"] = os.pathsep.join(new_paths)

        return_code = System.run(
            f'"{interpreter_win}" "{main_file}"',
            f'"{interpreter_lin}" "{main_file}"',
            env=env,
        )
        if return_code == 0:
            print(f"[green][+] Проект '{data['project_name']}' отработал успешно.[/green]")
        else:
            print(f"[red][-] Проект '{data['project_name']}' завершился с кодом {return_code}.[/red]")

    except KeyboardInterrupt:
        print(f"\n[yellow][!] Запуск проекта '{data.get('project_name', 'unknown')}' остановлен пользователем.[/yellow]")
    except FileNotFoundError:
        print("[red][-] Интерпретатор Python не найден.[/red]")
        ans = input("Выбрать другой интерпретатор? [д/н]")
        if "y" in ans or "д" in ans:
            selected = FileInput.select_file()
            if selected:
                interp = os.path.abspath(selected)
                g_config["interpreter"] = interp
                try:
                    with open(os.path.join(base_dir, "global_config.json"), "w", encoding="utf-8") as file_config:
                        file_config.write(json.dumps(g_config, indent=4, ensure_ascii=False))
                    print(f"[green][+] Интерпретатор сохранён: {interp}[/green]")
                except OSError as e:
                    print(f"[red][-] Не удалось сохранить конфигурацию: {e}[/red]")
            else:
                print("[yellow][!] Файл не выбран.[/yellow]")
    except Exception as e:
        print(f"[red][-] Ошибка при запуске проекта: {e}[/red]")
        ans = input("Выбрать другой интерпретатор? [д/н]")
        if "y" in ans or "д" in ans:
            selected = FileInput.select_file()
            if selected:
                interp = os.path.abspath(selected)
                g_config["interpreter"] = interp
                try:
                    with open(os.path.join(base_dir, "global_config.json"), "w", encoding="utf-8") as file_config:
                        file_config.write(json.dumps(g_config, indent=4, ensure_ascii=False))
                    print(f"[green][+] Интерпретатор сохранён: {interp}[/green]")
                except OSError as e:
                    print(f"[red][-] Не удалось сохранить конфигурацию: {e}[/red]")
            else:
                print("[yellow][!] Файл не выбран.[/yellow]")
