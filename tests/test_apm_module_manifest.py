import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APM_PY = ROOT / "APM" / "apm.py"


def _create_demo_module(tmp_path):
    module_dir = tmp_path / "demo_module"
    (module_dir / "AEngineApps").mkdir(parents=True)
    (module_dir / "services").mkdir()
    (module_dir / "APM" / "modules").mkdir(parents=True)

    (module_dir / "init.py").write_text(
        "__help__ = 'Demo module'\n"
        "__module_type__ = 'ЛОКАЛЬНЫЕ ПЛАГИНЫ'\n"
        "def run(base_dir, gconf_path='', args=None):\n"
        "    return None\n",
        encoding="utf-8",
    )
    (module_dir / "sign.py").write_text(
        "from pathlib import Path\n"
        "def run(base_dir, gconf_path='', args=None):\n"
        "    Path('alias-ran.txt').write_text('ok', encoding='utf-8')\n",
        encoding="utf-8",
    )
    (module_dir / "AEngineApps" / "demo_feature.py").write_text(
        "VALUE = 'feature'\n",
        encoding="utf-8",
    )
    (module_dir / "services" / "demo_service.py").write_text(
        "class DemoService:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (module_dir / "APM" / "modules" / "demo_extra.py").write_text(
        "__help__ = 'extra'\n",
        encoding="utf-8",
    )
    (module_dir / "helper.py").write_text(
        "from rich import print\n",
        encoding="utf-8",
    )
    return module_dir


def test_build_module_archive_writes_full_manifest(tmp_path):
    module_dir = _create_demo_module(tmp_path)
    archive_path = tmp_path / "demo_module.apm.zip"

    result = subprocess.run(
        [sys.executable, str(APM_PY), "build", "module", str(module_dir), "--output", str(archive_path), "--no-input"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert archive_path.exists()
    assert (module_dir / "apm-module.json").exists()

    import zipfile

    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("apm-module.json").decode("utf-8"))

    assert manifest["format"] == 2
    assert "demo_feature.py" in manifest["contents"]["aengine_apps"]
    assert "demo_service.py" in manifest["contents"]["services"]
    assert "demo_extra.py" in manifest["contents"]["apm_modules"]
    assert manifest["aliases"] == []
    assert manifest["dependencies"]["python"] == []


def test_build_module_archive_supports_auto_flags(tmp_path):
    module_dir = _create_demo_module(tmp_path)
    archive_path = tmp_path / "demo_module_auto.apm.zip"

    result = subprocess.run(
        [
            sys.executable,
            str(APM_PY),
            "build",
            "module",
            str(module_dir),
            "--output",
            str(archive_path),
            "--no-input",
            "--auto",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    import zipfile

    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("apm-module.json").decode("utf-8"))

    assert any(item["name"] == "sign" and item["subcommand"] == "sign" for item in manifest["aliases"])
    assert "rich" in manifest["dependencies"]["python"]


def test_install_archive_registers_aliases_and_assembles_files(tmp_path):
    module_dir = _create_demo_module(tmp_path)
    (module_dir / "apm-module.json").write_text(
        json.dumps(
            {
                "name": "demo_module",
                "format": 2,
                "aliases": [
                    {
                        "name": "sign",
                        "module": "demo_module",
                        "subcommand": "sign",
                        "help": "Alias для `apm demo_module sign`",
                    }
                ],
                "dependencies": {
                    "python": [],
                    "system": [],
                    "local_modules": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    archive_path = tmp_path / "demo_module.apm.zip"
    project_dir = tmp_path / "project"
    (project_dir / "AEngineApps").mkdir(parents=True)

    build_result = subprocess.run(
        [sys.executable, str(APM_PY), "build", "module", str(module_dir), "--output", str(archive_path), "--no-input"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build_result.returncode == 0, build_result.stderr

    install_result = subprocess.run(
        [sys.executable, str(APM_PY), "install", str(archive_path), "-l"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert install_result.returncode == 0, install_result.stderr

    help_result = subprocess.run(
        [sys.executable, str(APM_PY), "--help"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "sign" in help_result.stdout
    assert "Alias" in help_result.stdout or "ALIASES" in help_result.stdout

    alias_result = subprocess.run(
        [sys.executable, str(APM_PY), "sign"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert alias_result.returncode == 0, alias_result.stderr
    assert (project_dir / "alias-ran.txt").exists()
    assert (project_dir / "AEngineApps" / "demo_feature.py").exists()
    assert (project_dir / "services" / "demo_service.py").exists()
    assert (project_dir / ".apm" / "modules" / "demo_module" / "demo_extra.py").exists()
