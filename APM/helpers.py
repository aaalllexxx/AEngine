import os
import sys
import json
import io
import ast
import pathlib
import posixpath
import tempfile
import subprocess
import urllib.parse
import urllib.request
import zipfile
import tarfile
import cursor
from rich import print
from json_dict import JsonDict
from win2lin import System
import shutil
import errno
import stat
import readchar


def register_project(gconf_path, name, path):
    """Регистрирует проект в глобальном конфиге APM (без дубликатов)."""
    try:
        with open(gconf_path, encoding="utf-8") as f:
            g_config = json.loads(f.read() or "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        g_config = {}
    
    projects = g_config.get("projects", [])
    if not any(p.get("path") == path for p in projects):
        projects.append({"name": name, "path": path})
        g_config["projects"] = projects
        try:
            with open(gconf_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(g_config, indent=4, ensure_ascii=False))
        except OSError as e:
            print(f"[yellow][!] Не удалось зарегистрировать проект: {e}[/yellow]")


KNOWN_REPOS = {
    "aengineapps": "https://github.com/aaalllexxx/AEngineApps.git",
    "apm": "https://github.com/aaalllexxx/APM.git",
    "sec": "https://github.com/aaalllexxx/sec.git",
}

ARCHIVE_EXTENSIONS = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz")
MANIFEST_NAME = "apm-module.json"
IGNORED_BUILD_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", "htmlcov", 
    ".venv", "venv", "env", "node_modules", "dist", "build", ".next", 
    ".nuxt", ".idea", ".vscode", ".DS_Store", "target", "out", "bower_components",
    "logs", "data", "temp", "tmp"
}
STD_LIB_MODULES = set(getattr(sys, "stdlib_module_names", set()))
TOP_LEVEL_PACKAGE_DIRS = {"AEngineApps", "services", "templates", "APM"}


def normalize_repo_url(value):
    if not value:
        return ""

    candidate = value.strip()
    alias = KNOWN_REPOS.get(candidate.lower())
    if alias:
        return alias

    if candidate.startswith("https://github.com/") or candidate.startswith("http://github.com/"):
        return candidate if candidate.endswith(".git") else candidate + ".git"

    if candidate.startswith("github.com/"):
        return "https://" + (candidate if candidate.endswith(".git") else candidate + ".git")

    parts = [part for part in candidate.split("/") if part]
    if len(parts) == 2:
        return f"https://github.com/{parts[0]}/{parts[1].removesuffix('.git')}.git"

    return candidate


def is_probable_local_path(value):
    if not value:
        return False
    candidate = value.strip()
    if candidate.startswith(("http://", "https://", "github.com/")):
        return False
    if candidate.lower() in KNOWN_REPOS:
        return False
    if candidate.startswith((".", "/", "~")):
        return True
    if os.name == "nt" and len(candidate) > 2 and candidate[1] == ":":
        return True
    return os.path.exists(os.path.expanduser(candidate))


def expand_local_path(value):
    return os.path.abspath(os.path.expanduser(value))


def _github_archive_candidates(url):
    normalized = normalize_repo_url(url)
    parsed = urllib.parse.urlparse(normalized)
    path = parsed.path.strip("/")
    if not path.endswith(".git"):
        return []

    owner_repo = path[:-4]
    if owner_repo.count("/") != 1:
        return []

    owner, repo = owner_repo.split("/")
    return [
        f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip",
        f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip",
    ]


def download_repo_snapshot(url, target_dir):
    """Download a GitHub repo snapshot into target_dir without requiring git."""
    target_dir = os.path.abspath(target_dir)
    if os.path.exists(target_dir):
        clear_dir(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    last_error = None
    for archive_url in _github_archive_candidates(url):
        try:
            with urllib.request.urlopen(archive_url, timeout=60) as response:
                payload = response.read()
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                names = [name for name in archive.namelist() if name and not name.endswith("/")]
                top_level = names[0].split("/")[0] if names else ""
                temp_root = tempfile.mkdtemp(prefix="apm-repo-")
                try:
                    archive.extractall(temp_root)
                    extracted_root = os.path.join(temp_root, top_level)
                    if not os.path.isdir(extracted_root):
                        raise FileNotFoundError(f"Archive root not found for {archive_url}")

                    for entry in os.listdir(extracted_root):
                        src = os.path.join(extracted_root, entry)
                        dst = os.path.join(target_dir, entry)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                    return target_dir
                finally:
                    shutil.rmtree(temp_root, ignore_errors=True)
        except Exception as exc:
            last_error = exc
            continue

    if os.path.isdir(target_dir) and not os.listdir(target_dir):
        os.rmdir(target_dir)
    raise RuntimeError(f"Не удалось загрузить репозиторий {url}: {last_error}")


def copy_repo_snapshot(source_dir, target_dir):
    """Copy a local repository snapshot into target_dir without VCS artifacts."""
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(source_dir)
    if os.path.exists(target_dir):
        clear_dir(target_dir)
    shutil.copytree(
        source_dir,
        target_dir,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache", "htmlcov", ".venv"),
    )


def _copy_content(source_dir, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    for entry in os.listdir(source_dir):
        src = os.path.join(source_dir, entry)
        dst = os.path.join(target_dir, entry)
        if os.path.isdir(src):
            shutil.copytree(
                src,
                dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache", "htmlcov", ".venv"),
            )
        else:
            shutil.copy2(src, dst)


def _pick_module_root(extracted_root):
    manifest_path = os.path.join(extracted_root, "apm-module.json")
    if os.path.exists(manifest_path):
        return extracted_root

    entries = [os.path.join(extracted_root, entry) for entry in os.listdir(extracted_root)]
    dirs = [entry for entry in entries if os.path.isdir(entry)]
    files = [entry for entry in entries if os.path.isfile(entry)]

    if len(dirs) == 1 and not files:
        return dirs[0]

    return extracted_root


def extract_module_archive(archive_path, target_dir):
    archive_path = expand_local_path(archive_path)
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(archive_path)

    temp_root = tempfile.mkdtemp(prefix="apm-archive-")
    try:
        lower_path = archive_path.lower()
        if lower_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(temp_root)
        elif lower_path.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz")):
            with tarfile.open(archive_path) as archive:
                archive.extractall(temp_root)
        else:
            raise RuntimeError(f"Неподдерживаемый формат архива: {archive_path}")

        module_root = _pick_module_root(temp_root)
        if os.path.exists(target_dir):
            clear_dir(target_dir)
        os.makedirs(target_dir, exist_ok=True)
        _copy_content(module_root, target_dir)
        return target_dir
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def detect_module_name_from_source(source):
    if not source:
        return ""
    if is_probable_local_path(source):
        path = expand_local_path(source)
        name = os.path.basename(path.rstrip("/\\"))
        for ext in ARCHIVE_EXTENSIONS:
            if name.lower().endswith(ext):
                base_name = name[: -len(ext)]
                if base_name.endswith(".apm"):
                    base_name = base_name[:-4]
                return base_name
        return name

    normalized = normalize_repo_url(source)
    return normalized.split("/")[-1].replace(".git", "")


def materialize_repo_snapshot(url, target_dir, local_source=None):
    if local_source and os.path.isdir(local_source):
        copy_repo_snapshot(local_source, target_dir)
        return target_dir
    return download_repo_snapshot(url, target_dir)


def install_module_source(source, target_dir, local_source=None):
    if is_probable_local_path(source):
        path = expand_local_path(source)
        if os.path.isdir(path):
            copy_repo_snapshot(path, target_dir)
            return target_dir
        if os.path.isfile(path):
            return extract_module_archive(path, target_dir)
        raise FileNotFoundError(path)

    normalized = normalize_repo_url(source)
    return materialize_repo_snapshot(normalized, target_dir, local_source=local_source)


def build_module_archive(source_dir, output_path, interactive=True, auto_aliases=False, auto_dependencies=False, auto_services=False):
    source_dir = expand_local_path(source_dir)
    output_path = expand_local_path(output_path)
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(source_dir)

    manifest = build_module_manifest(
        source_dir,
        interactive=interactive,
        auto_aliases=auto_aliases,
        auto_dependencies=auto_dependencies,
        auto_services=auto_services,
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(os.path.join(source_dir, MANIFEST_NAME), "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
        manifest_file.write("\n")

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

        # Лимит размера файла для включения в сборку (50МБ)
        MAX_FILE_SIZE = 50 * 1024 * 1024 

        for root, dirnames, filenames in os.walk(source_dir):
            rel_root = os.path.relpath(root, source_dir)
            if rel_root == ".":
                rel_root = ""

            # Убираем рекурсию в нежелательные папки на корню
            dirnames[:] = [
                dirname for dirname in dirnames
                if dirname not in IGNORED_BUILD_DIRS and not dirname.startswith(".")
            ]

            for filename in filenames:
                if filename.endswith((".pyc", ".pyo")) or filename in {".coverage", MANIFEST_NAME}:
                    continue
                
                # Исключаем архивы (чтобы не было рекурсии архива в архиве)
                if filename.endswith((".zip", ".tar.gz", ".apm.zip")):
                    continue

                src = os.path.join(root, filename)
                rel_path = posixpath.join(rel_root.replace("\\", "/"), filename) if rel_root else filename
                
                # Пропускаем целевой файл, если он вдруг в источнике
                if os.path.abspath(src) == os.path.abspath(output_path):
                    continue
                
                try:
                    if os.path.getsize(src) > MAX_FILE_SIZE:
                        print(f"[yellow][!] Файл слишком велик и будет пропущен: {rel_path} ({os.path.getsize(src)//(1024*1024)}MB)[/yellow]")
                        continue
                except OSError:
                    continue

                archive.write(src, rel_path)

    return output_path


def _safe_read_json(path, default=None):
    default = {} if default is None else default
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def load_module_manifest(module_dir):
    return _safe_read_json(os.path.join(module_dir, MANIFEST_NAME), default={})


def _walk_relative_files(base_dir):
    items = []
    if not os.path.isdir(base_dir):
        return items
    for root, dirnames, filenames in os.walk(base_dir):
        rel_root = os.path.relpath(root, base_dir)
        if rel_root == ".":
            rel_root = ""
        dirnames[:] = [dirname for dirname in dirnames if dirname not in IGNORED_BUILD_DIRS]
        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")) or filename in {".coverage"}:
                continue
            rel_path = posixpath.join(rel_root.replace("\\", "/"), filename) if rel_root else filename
            items.append(rel_path)
    return sorted(items)


def _find_python_files(source_dir):
    py_files = []
    for root, dirnames, filenames in os.walk(source_dir):
        rel_root = os.path.relpath(root, source_dir)
        if rel_root == ".":
            rel_root = ""
        dirnames[:] = [dirname for dirname in dirnames if dirname not in IGNORED_BUILD_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                py_files.append(os.path.join(root, filename))
    return py_files


def _top_level_local_names(source_dir):
    local_names = {os.path.basename(source_dir.rstrip("/\\"))}
    for entry in os.listdir(source_dir):
        entry_path = os.path.join(source_dir, entry)
        if os.path.isdir(entry_path):
            local_names.add(entry)
        elif entry.endswith(".py"):
            local_names.add(entry[:-3])
    return local_names


def _detect_command_modules(source_dir):
    commands = []
    for entry in sorted(os.listdir(source_dir)):
        if not entry.endswith(".py"):
            continue
        if entry.startswith("__"):
            continue
        entry_path = os.path.join(source_dir, entry)
        try:
            with open(entry_path, encoding="utf-8") as file:
                tree = ast.parse(file.read(), filename=entry_path)
        except (OSError, SyntaxError):
            continue
        has_run = any(isinstance(node, ast.FunctionDef) and node.name == "run" for node in tree.body)
        if has_run:
            commands.append(entry[:-3])
    return commands


def detect_python_dependencies(source_dir):
    dependencies = set()
    local_names = _top_level_local_names(source_dir)
    for py_file in _find_python_files(source_dir):
        try:
            with open(py_file, encoding="utf-8") as file:
                tree = ast.parse(file.read(), filename=py_file)
        except (OSError, SyntaxError):
            continue

        for node in ast.walk(tree):
            root_name = None
            if isinstance(node, ast.Import):
                for imported in node.names:
                    root_name = imported.name.split(".")[0]
                    if root_name and root_name not in STD_LIB_MODULES and root_name not in local_names:
                        dependencies.add(root_name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0 or not node.module:
                    continue
                root_name = node.module.split(".")[0]
                if root_name and root_name not in STD_LIB_MODULES and root_name not in local_names:
                    dependencies.add(root_name)

    requirements_path = os.path.join(source_dir, "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, encoding="utf-8") as file:
            for line in file:
                candidate = line.strip()
                if not candidate or candidate.startswith("#"):
                    continue
                dependencies.add(candidate)

    return sorted(dependencies)


def _normalize_aliases(module_name, alias_map):
    aliases = []
    if isinstance(alias_map, dict):
        items = alias_map.items()
    else:
        items = []
        for item in alias_map or []:
            if isinstance(item, dict) and item.get("name"):
                items.append((item["name"], item))

    for alias_name, payload in items:
        if isinstance(payload, str):
            subcommand = payload
            help_text = f"Alias для `apm {module_name} {subcommand}`"
        else:
            subcommand = payload.get("subcommand") or payload.get("command")
            help_text = payload.get("help") or f"Alias для `apm {module_name} {subcommand}`"
        if not alias_name or not subcommand:
            continue
        aliases.append(
            {
                "name": alias_name,
                "module": module_name,
                "subcommand": subcommand,
                "help": help_text,
            }
        )
    return aliases


def _auto_aliases(module_name, commands):
    aliases = []
    for command in commands:
        if command in {"init", module_name}:
            continue
        aliases.append(
            {
                "name": command,
                "module": module_name,
                "subcommand": command,
                "help": f"Alias для `apm {module_name} {command}`",
            }
        )
    return aliases


def _merge_unique_strings(base_items, extra_items):
    result = []
    seen = set()
    for item in list(base_items or []) + list(extra_items or []):
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _prompt_review_list(title, current_items, prompt_text):
    """
    Displays current items and allowed editing (+/-).
    Returns the final list.
    """
    items = list(current_items or [])
    while True:
        print(f"\n[bold cyan]--- {title} ---[/bold cyan]")
        if not items:
            print("  [dim]Список пуст[/dim]")
        else:
            for item in sorted(items):
                print(f"  [green]•[/green] {item}")
        
        print(f"\n[dim]Введите имя для добавления, -имя для удаления. Пустая строка для подтверждения.[/dim]")
        value = input(prompt_text).strip()
        if not value:
            break
        
        if value.startswith("-"):
            to_remove = value[1:].strip()
            if to_remove in items:
                items.remove(to_remove)
                print(f"[red][-] Удалено: {to_remove}[/red]")
            else:
                print(f"[yellow][!] Не найдено: {to_remove}[/yellow]")
        else:
            to_add = value.strip("+ ").strip()
            if to_add and to_add not in items:
                items.append(to_add)
                print(f"[green][+] Добавлено: {to_add}[/green]")
    return sorted(items)


def _prompt_manifest_enhancements(manifest):
    # 1. Review Aliases
    aliases = list(manifest.get("aliases", []))
    while True:
        print(f"\n[bold cyan]--- Список Alias'ов модуля ---[/bold cyan]")
        if not aliases:
            print("  [dim]Alias'ы не обнаружены[/dim]")
        else:
            for al in sorted(aliases, key=lambda x: x["name"]):
                print(f"  [green]•[/green] [bold]{al['name']}[/bold] -> {al['subcommand']}")
        
        print(f"\n[dim]Формат: alias=subcommand для добавления, -alias для удаления. Пустая строка для подтверждения.[/dim]")
        value = input("alias ->").strip()
        if not value:
            break
        
        if value.startswith("-"):
            name_to_remove = value[1:].strip()
            new_aliases = [a for a in aliases if a["name"] != name_to_remove]
            if len(new_aliases) < len(aliases):
                aliases = new_aliases
                print(f"[red][-] Удален alias: {name_to_remove}[/red]")
            else:
                print(f"[yellow][!] Alias не найден: {name_to_remove}[/yellow]")
        elif "=" in value:
            parts = [p.strip() for p in value.split("=", 1)]
            if len(parts) == 2:
                name, sub = parts
                # Удаляем старый если есть с таким же именем
                aliases = [a for a in aliases if a["name"] != name]
                aliases.append({
                    "name": name,
                    "module": manifest["name"],
                    "subcommand": sub,
                    "help": f"Alias для `apm {manifest['name']} {sub}`"
                })
                print(f"[green][+] Добавлен alias: {name} -> {sub}[/green]")
        else:
            print("[yellow][!] Используйте формат name=subcommand или -name[/yellow]")

    manifest["aliases"] = aliases

    # 2. Review Python Deps
    manifest["dependencies"]["python"] = _prompt_review_list(
        "Python-зависимости",
        manifest["dependencies"]["python"],
        "python dep ->"
    )

    # 3. Review System Steps
    manifest["dependencies"]["system"] = _prompt_review_list(
        "Системные зависимости / ручные шаги",
        manifest["dependencies"]["system"],
        "system step ->"
    )


def build_module_manifest(source_dir, interactive=True, auto_aliases=False, auto_dependencies=False, auto_services=False):
    source_dir = expand_local_path(source_dir)
    module_name = os.path.basename(source_dir.rstrip("/\\"))
    manifest_path = os.path.join(source_dir, MANIFEST_NAME)
    existing_manifest = _safe_read_json(manifest_path, default={})

    commands = _detect_command_modules(source_dir)
    explicit_aliases = _normalize_aliases(module_name, existing_manifest.get("aliases", []))
    auto_detected_aliases = _auto_aliases(module_name, commands) if auto_aliases else []
    python_dependencies = detect_python_dependencies(source_dir) if auto_dependencies else []

    manifest = {
        "name": module_name,
        "format": 2,
        "source": "apm build module",
        "package": {
            "root": ".",
            "aengine_apps_dir": "AEngineApps",
            "services_dir": "services",
            "apm_modules_dir": "APM/modules",
            "templates_dir": "templates",
            "local_module_dir": ".",
        },
        "contents": {
            "aengine_apps": _walk_relative_files(os.path.join(source_dir, "AEngineApps")) if auto_services or interactive else existing_manifest.get("contents", {}).get("aengine_apps", []),
            "services": _walk_relative_files(os.path.join(source_dir, "services")) if auto_services or interactive else existing_manifest.get("contents", {}).get("services", []),
            "apm_modules": _walk_relative_files(os.path.join(source_dir, "APM", "modules")) if auto_services or interactive else existing_manifest.get("contents", {}).get("apm_modules", []),
            "templates": _walk_relative_files(os.path.join(source_dir, "templates")) if auto_services or interactive else existing_manifest.get("contents", {}).get("templates", []),
            "local_modules": _walk_relative_files(source_dir),
        },
        "commands": commands,
        "aliases": explicit_aliases if explicit_aliases else auto_detected_aliases,
        "dependencies": {
            "python": python_dependencies,
            "system": existing_manifest.get("dependencies", {}).get("system", []),
            "local_modules": existing_manifest.get("dependencies", {}).get("local_modules", []),
        },
        "install_commands": existing_manifest.get("install_commands", []),
        "notes": existing_manifest.get("notes", []),
        "install": {
            "copy_to_project": True,
            "create_missing_dirs": ["AEngineApps", "services", ".apm", ".apm/installed", ".apm/modules"],
        },
    }

    if existing_manifest:
        manifest["commands"] = existing_manifest.get("commands", manifest["commands"])
        manifest["aliases"] = explicit_aliases or manifest["aliases"]
        manifest["dependencies"]["python"] = _merge_unique_strings(
            manifest["dependencies"]["python"],
            existing_manifest.get("dependencies", {}).get("python", []),
        )
        manifest["notes"] = existing_manifest.get("notes", manifest["notes"])
        manifest["install"].update(existing_manifest.get("install", {}))
        manifest["package"].update(existing_manifest.get("package", {}))
        manifest["contents"].update(existing_manifest.get("contents", {}))

    if interactive:
        _prompt_manifest_enhancements(manifest)

    return manifest


def _copy_manifest_files(module_dir, project_root, source_prefix, target_root, files):
    if not files:
        return []
    copied = []
    for rel_path in files:
        source_path = os.path.join(module_dir, source_prefix, rel_path) if source_prefix else os.path.join(module_dir, rel_path)
        target_path = os.path.join(project_root, target_root, rel_path)
        if not os.path.exists(source_path):
            continue
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied.append(target_path)
    return copied


def assemble_module_package(module_dir, project_root, manifest):
    if not manifest or not manifest.get("install", {}).get("copy_to_project", True):
        return []

    project_root = expand_local_path(project_root)
    copied = []
    for rel_dir in manifest.get("install", {}).get("create_missing_dirs", []):
        os.makedirs(os.path.join(project_root, rel_dir), exist_ok=True)

    contents = manifest.get("contents", {})
    copied.extend(_copy_manifest_files(module_dir, project_root, "AEngineApps", "AEngineApps", contents.get("aengine_apps", [])))
    copied.extend(_copy_manifest_files(module_dir, project_root, "services", "services", contents.get("services", [])))
    copied.extend(
        _copy_manifest_files(
            module_dir,
            project_root,
            os.path.join("APM", "modules"),
            os.path.join(".apm", "modules", manifest.get("name", "module")),
            contents.get("apm_modules", []),
        )
    )
    copied.extend(_copy_manifest_files(module_dir, project_root, "templates", "templates", contents.get("templates", [])))
    return copied


def install_python_dependencies(dependencies):
    installed = []
    failed = []
    for dependency in dependencies or []:
        dependency = dependency.strip()
        if not dependency:
            continue
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dependency],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            installed.append(dependency)
        else:
            failed.append(
                {
                    "dependency": dependency,
                    "error": (result.stderr or result.stdout or "").strip(),
                }
            )
    return installed, failed


def clear_dir(path):
    if not os.path.exists(path):
        return
    try:
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, ignore_errors=False, onexc=handle_remove_readonly)
        else:
            shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly_legacy)
    except Exception as e:
        print(f"[red][-] Ошибка при удалении '{path}': {e}[/red]")
        raise


def handle_remove_readonly(func, path, exc):
  excvalue = exc
  if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      raise


def handle_remove_readonly_legacy(func, path, exc_info):
  excvalue = exc_info[1]
  if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      raise excvalue


standard_input = input

def input(msg):
    print(f"[green bold]{msg}\n-> [/green bold]", end="")
    return standard_input()


def _render_list(items, index, title=None):
    """Отрисовка списка с выделенным элементом"""
    System.clear()
    if title:
        print(title)
    for i, item in enumerate(items):
        if i == index:
            print(f"[green]> {item}[/green]")
        else:
            print(f"  [white]{item}[/white]")


class FileInput:
    @classmethod
    def select_file(cls):
        path = ""
        index = 0
        try:
            cursor.hide()
            while True:
                content = [".."] + os.listdir(path if path else None)
                if index >= len(content):
                    index = 0
                
                System.clear()
                print(f"Выберите файл [green bold](esc - отмена)[/green bold]:\n")
                for i, file in enumerate(content):
                    if i == index:
                        print(f"[green]> {file}[/green]")
                    else:
                        print(f"  [white]{file}[/white]")
                print(f"\n[bold red]{os.path.join(path, content[index]) if path else content[index]}[/bold red]")

                key = readchar.readkey()
                
                if key == readchar.key.UP:
                    index = (index - 1) % len(content)
                elif key == readchar.key.DOWN:
                    index = (index + 1) % len(content)
                elif key == readchar.key.ENTER or key == readchar.key.CR:
                    current = content[index]
                    if current == "..":
                        index = 0
                        path = os.path.dirname(path.rstrip("/\\"))
                    elif os.path.isfile(os.path.join(path, current) if path else current):
                        cursor.show()
                        return os.path.join(path, current) if path else current
                    else:
                        path = os.path.join(path, current) if path else current
                        index = 0
                elif key == readchar.key.ESC:
                    cursor.show()
                    return None
        except KeyboardInterrupt:
            cursor.show()
            return None


class ConfigInput:
    config = {}

    @classmethod
    def __input_options(cls, variants):
        index = 0
        while True:
            _render_list(
                [str(v) for v in variants], 
                index,
                "[green bold]Выберите опцию:[/green bold]\n"
            )
            
            key = readchar.readkey()
            
            if key == readchar.key.UP:
                index = (index - 1) % len(variants)
            elif key == readchar.key.DOWN:
                index = (index + 1) % len(variants)
            elif key == readchar.key.ENTER or key == readchar.key.CR:
                return variants[index]
            elif key == readchar.key.ESC:
                return None

    @classmethod
    def __input_dict(cls):
        System.clear()
        d = {}
        route = input("Введите ключ (s для сохранения, e для выхода):")
        while not route:
            route = input("Необходим ключ (s для сохранения, e для выхода):")
        
        if route == "e":
            return None
        
        if route == "s":
            return d
        
        screen = input("Введите значение (e для выхода):")
        while not screen:
            screen = input("Необходимо значение (e для выхода):")

        while route not in ["s", "e"] and screen not in ["s", "e"]:
            System.clear()
            d[route] = screen
            for k, v in d.items():
                print(f"[green]{k}[/green]: [blue]{v}[/blue]")
            
            route = input("Введите ключ (s для сохранения, e для выхода):")
            while not route:
                route = input("Необходим ключ (s для сохранения, e для выхода):")

            if route == "e":
                return None
            
            if route == "s":
                return d
            
            screen = input("Введите значение (e для выхода):")
            while not screen:
                screen = input("Необходимо значение (e для выхода):")
        return None



    @classmethod
    def input(cls, key, data):
        try:
            if data["type"] == "int":
                raw = input("Введите целое число:")
                try:
                    cls.config[key] = int(raw) if raw else data["default"]
                except ValueError:
                    print(f"[red][-] '{raw}' не является числом, используется значение по умолчанию.[/red]")
                    cls.config[key] = data["default"]
            elif data["type"] == "str":
                cls.config[key] = input("Введите строку:") or data["default"]
            elif data["type"] == "bool":
                cls.config[key] = cls.__input_options([True, False]) or data["default"]
            elif data["type"] == "select":
                cls.config[key] = cls.__input_options(data["options"]) or data["default"]
            elif data["type"] == "dict":
                if data.get("default") == "auto":
                    mode = cls.__input_options(["Автоматическая", "Ручная"])
                    if mode == "Автоматическая":
                        cls.config[key] = "auto"
                    elif mode == "Ручная":
                        result = cls.__input_dict()
                        cls.config[key] = result if result else data["default"]
                    else:
                        pass
                else:
                    cls.config[key] = cls.__input_dict() or data["default"]
            else:
                print(f"[yellow][!] Неизвестный тип '{data['type']}' для '{key}', пропускаю.[/yellow]")
        except KeyboardInterrupt:
            print("\n[yellow][!] Ввод отменён.[/yellow]")

    @classmethod
    def start(cls, template, existing=None):
        template = JsonDict(template)
        cls.config = dict(existing) if existing else {}
        for tmpl in template.keys():
            if template[tmpl].get("required") and tmpl not in cls.config:
                cls.config[tmpl] = template[tmpl]["default"]
        index = 0
        
        while True:
            System.clear()
            print("[green bold]Выберите настройку [blue bold](Ctrl+S - сохранить, esc - выйти)[/blue bold]:[/green bold]\n")
            for k, v in template.dictionary.items():
                ki = template.keys().index(k)
                conf = cls.config.get(k)
                if ki == index:
                    print(f"{ki + 1}) [white]> {k}: [blue]{conf if conf is not None else v['default']}[/blue] -> {v.get('help') or 'Неизвестно'}[/white]")
                else:
                    print(f"{ki + 1}) [red]{k}: {conf if conf is not None else v['default']}[/red]")
            print()

            key = readchar.readkey()
            
            if key == readchar.key.UP:
                index = (index - 1) % len(template.keys())
            elif key == readchar.key.DOWN:
                index = (index + 1) % len(template.keys())
            elif key == readchar.key.ENTER or key == readchar.key.CR:
                i = template.keys()[index]
                cursor.show()
                cls.input(i, template[i])
            elif key == readchar.key.CTRL_S:
                return cls.config
            elif key == readchar.key.ESC:
                print("[yellow][!] Выход без сохранения.[/yellow]")
                return None
