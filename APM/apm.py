"""APM — AEngine Package Manager."""

from argparse import ArgumentParser
import os
import sys
import json
import importlib
import importlib.util

def get_config_dir():
    """Get platform-specific config directory"""
    return os.path.dirname(os.path.abspath(__file__)) + os.sep

sys.dont_write_bytecode = True
base_dir = get_config_dir()
gconf_path = os.path.join(base_dir, "global_config.json")
module_path = "modules"
install_module_path = "installed"

if not os.path.exists(gconf_path):
    with open(gconf_path, "w") as file:
        file.write("{}")


def _read_json_file(path, default=None):
    default = {} if default is None else default
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _manifest_path(module_dir):
    return os.path.join(module_dir, "apm-module.json")


def _local_installed_dir():
    """Локальная область видимости: модули проекта в <cwd>/.apm/installed/."""
    return os.path.join(os.getcwd(), ".apm", "installed")


def _global_installed_dir():
    """Глобальная область видимости: модули рядом с APM (APM/installed/)."""
    return os.path.join(base_dir, install_module_path)


# Области видимости в порядке приоритета (локальная перекрывает глобальную).
INSTALLED_SCOPES = (
    ("local", _local_installed_dir, "ЛОКАЛЬНЫЕ ПЛАГИНЫ"),
    ("global", _global_installed_dir, "ГЛОБАЛЬНЫЕ ПЛАГИНЫ"),
)


def _iter_installed_module_dirs():
    """Перебирает установленные модули: сначала локальные, затем глобальные.

    Возвращает кортежи (scope, module_type, module_name, module_dir).
    Вызывающий код сам решает, пропускать ли дубликаты по имени
    (локальный модуль имеет приоритет над глобальным).
    """
    for scope, dir_fn, module_type in INSTALLED_SCOPES:
        root = dir_fn()
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            mod_dir = os.path.join(root, name)
            if os.path.isdir(mod_dir):
                yield scope, module_type, name, mod_dir


def _find_installed_module_dir(module_name):
    """Ищет каталог установленного модуля сначала локально, затем глобально."""
    for _, dir_fn, _ in INSTALLED_SCOPES:
        candidate = os.path.join(dir_fn(), module_name)
        if os.path.isdir(candidate):
            return candidate
    return None


def _load_installed_aliases():
    """Собирает alias'ы из локальных и глобальных модулей (локальные в приоритете)."""
    aliases = {}
    for _, _, name, mod_dir in _iter_installed_module_dirs():
        manifest = _read_json_file(_manifest_path(mod_dir), default={})
        for item in manifest.get("aliases", []):
            if not isinstance(item, dict):
                continue
            alias_name = item.get("name")
            subcommand = item.get("subcommand") or item.get("command")
            if not alias_name or not subcommand:
                continue
            if alias_name in aliases:  # локальный alias уже найден — он главнее
                continue
            aliases[alias_name] = {
                "module": item.get("module") or name,
                "subcommand": subcommand,
                "help": item.get("help") or f"Alias для `apm {name} {subcommand}`",
            }
    return aliases


def _run_installed_module_command(module_name, command_args):
    module_dir = _find_installed_module_dir(module_name)
    if module_dir is None:
        print(f"Команда '{module_name}' не найдена.")
        print("  Используйте 'apm --help' для списка доступных команд.")
        sys.exit(1)

    if len(command_args) < 2:
        module_file = os.path.join(module_dir, "init.py")
        if not os.path.exists(module_file):
            module_file = os.path.join(module_dir, "__init__.py")
    else:
        module_file = os.path.join(module_dir, command_args[1] + ".py")

    if not os.path.exists(module_file):
        print(f"Команда '{module_name}' не найдена.")
        print("  Используйте 'apm --help' для списка доступных команд.")
        sys.exit(1)

    added_path = False
    if module_dir not in sys.path:
        sys.path.append(module_dir)
        added_path = True

    try:
        module = _load_module_from_file(f"{module_name}.subcommand", module_file)
        if hasattr(module, "run"):
            module.run(base_dir, gconf_path=gconf_path, args=command_args[2:] if len(command_args) > 1 else [])
        else:
            print(f"[!] В модуле {module_file} не найдена функция run()")
    finally:
        if added_path and module_dir in sys.path:
            sys.path.remove(module_dir)

def get_commands():
    """Загружает доступные команды и группирует их."""
    commands = {}
    
    # 1. Загрузка встроенных модулей (APM/modules/)
    modules_dir = os.path.join(base_dir, "modules")
    if os.path.isdir(modules_dir):
        for prog_name in os.listdir(modules_dir):
            if prog_name.startswith("__") or not prog_name.endswith(".py"):
                continue
            name = prog_name.split(".")[0]
            try:
                mod = importlib.import_module(f"{module_path}.{name}")
                desc = getattr(mod, "__help__", "")
                mod_type = getattr(mod, "__module_type__", "ПРОЧЕЕ")
                commands[name] = {"help": desc, "type": mod_type}
            except Exception as e:
                commands[name] = {"help": f"[ошибка загрузки: {e}]", "type": "ОШИБКИ"}

    # 2. Загрузка установленных пользовательских модулей:
    #    сначала локальные (.apm/installed/), затем глобальные (APM/installed/).
    #    Приоритет: встроенные > локальные > глобальные (дубли по имени пропускаются).
    for scope, default_type, name, mod_dir in _iter_installed_module_dirs():
        # Пропускаем, если такой модуль уже зарегистрирован (встроенный/локальный главнее)
        if name in commands:
            continue

        # Ищем точку входа (init.py или __init__.py)
        entry_file = os.path.join(mod_dir, "init.py")
        if not os.path.exists(entry_file):
            entry_file = os.path.join(mod_dir, "__init__.py")

        if os.path.exists(entry_file):
            try:
                added_path = False
                if mod_dir not in sys.path:
                    sys.path.append(mod_dir)
                    added_path = True
                mod = _load_module_from_file(f"{scope}_{name}", entry_file)
                desc = getattr(mod, "__help__", f"Модуль {name} ({scope})")
                mod_type = getattr(mod, "__module_type__", default_type)
                commands[name] = {"help": desc, "type": mod_type}
            except Exception as e:
                commands[name] = {"help": f"[ошибка модуля {scope}: {e}]", "type": "ОШИБКИ"}
            finally:
                if added_path and mod_dir in sys.path:
                    sys.path.remove(mod_dir)

    for alias_name, alias_data in _load_installed_aliases().items():
        if alias_name in commands:
            continue
        commands[alias_name] = {
            "help": alias_data["help"],
            "type": "ALIASES",
        }

    return commands


def print_help(commands):
    """Красивый вывод help с группировкой."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        
        console.print("\n  [bold green]AEngine Package Manager[/bold green] [dim]v2.0[/dim]\n")
        
        # Динамическая группировка команд
        groups_data = {}
        for cmd, data in commands.items():
            mod_type = data["type"].upper()
            if mod_type not in groups_data:
                groups_data[mod_type] = []
            groups_data[mod_type].append((cmd, data["help"]))
            
        # Цвета для популярных групп, остальные случайные из палитры
        color_map = {
            "ПРОЕКТЫ": "cyan",
            "НАВИГАЦИЯ": "green",
            "МОДУЛИ": "yellow",
            "ПРОЧЕЕ": "magenta",
            "ОШИБКИ": "red"
        }
        fallback_colors = ["blue", "dark_orange", "purple", "dark_sea_green", "steel_blue"]
        
        # Сортировка групп: Проекты, Навигация, Модули... Ошибки в конце
        order_priority = {"ПРОЕКТЫ": 0, "НАВИГАЦИЯ": 1, "МОДУЛИ": 2, "ПРОЧЕЕ": 98, "ОШИБКИ": 99}
        sorted_groups = sorted(groups_data.keys(), key=lambda k: order_priority.get(k, 50))
        
        color_idx = 0
        for group_name in sorted_groups:
            cmd_list = groups_data[group_name]
            
            color = color_map.get(group_name)
            if not color:
                color = fallback_colors[color_idx % len(fallback_colors)]
                color_idx += 1
                
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column(style=f"bold {color}", width=14)
            table.add_column(style="white")
            
            for cmd, desc in sorted(cmd_list):
                table.add_row(cmd, desc)
                
            console.print(Panel(table, title=f"[bold {color}]{group_name}[/bold {color}]", title_align="left", expand=False))
            console.print()
            
    except ImportError:
        # Fallback без rich
        print("\nИспользование: apm <опции> <флаги>\n")
        print("Доступные опции:")
        for name, data in commands.items():
            print(f"    {name} - {data['help']} ({data['type']})")


def _load_module_from_file(name, filepath):
    """Загружает Python-модуль из файла через importlib (без deprecated load_module)."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось загрузить спецификацию модуля: {filepath}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    try:
        executable = sys.argv[1]
        args = sys.argv[1:]
        aliases = _load_installed_aliases()
        
        if executable in ("-h", "--help", "help"):
            print_help(get_commands())
        else:
            if executable in aliases:
                alias_data = aliases[executable]
                try:
                    alias_args = [alias_data["module"], alias_data["subcommand"], *args[1:]]
                    _run_installed_module_command(alias_data["module"], alias_args)
                except ModuleNotFoundError as inner_e:
                    import traceback
                    print(f"[!] Ошибка зависимости при загрузке alias '{executable}': отсутствует модуль '{inner_e.name}'")
                    traceback.print_exc()
                except Exception:
                    import traceback
                    print(f"[!] Ошибка при выполнении alias '{executable}':")
                    traceback.print_exc()
                sys.exit(0)
            try:
                importlib.import_module(f"{module_path}.{executable}").run(base_dir, gconf_path, args=args)
            except ModuleNotFoundError as e:
                # Ключевая проверка: если e.name совпадает с запрашиваемым модулем —
                # значит сам модуль не найден. Если e.name другое — ошибка внутри модуля
                # (не хватает зависимости).
                expected_module = f"{module_path}.{executable}"
                if e.name == expected_module or e.name == executable:
                    # Модуль APM не найден — пробуем как установленный (локальный/глобальный)
                    try:
                        _run_installed_module_command(executable, args)
                    
                    except ModuleNotFoundError as inner_e:
                        import traceback
                        print(f"[!] Ошибка зависимости при загрузке '{executable}': отсутствует модуль '{inner_e.name}'")
                        traceback.print_exc()
                    except Exception:
                        import traceback
                        print(f"[!] Ошибка при выполнении команды '{executable}':")
                        traceback.print_exc()
                else:
                    # Модуль APM найден, но внутри него ошибка импорта — показываем реальную ошибку
                    import traceback
                    print(f"[!] Ошибка при выполнении '{executable}': отсутствует модуль '{e.name}'")
                    print(f"    Установите его: pip install {e.name}")
                    traceback.print_exc()

            except AttributeError:
                print(f"Команда '{executable}' пока не реализована.") 
            except Exception:
                import traceback
                print(f"[!] Ошибка при выполнении команды '{executable}':")
                traceback.print_exc()
                
    except IndexError:
        print_help(get_commands())
