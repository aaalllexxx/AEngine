import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APM_PY = ROOT / "APM" / "apm.py"
SEC_DIR = ROOT / "sec"


def _prepare_project(tmp_path):
    project_dir = tmp_path / "project"
    installed_dir = project_dir / ".apm" / "installed"
    sec_target = installed_dir / "sec"
    (project_dir / "AEngineApps").mkdir(parents=True)
    installed_dir.mkdir(parents=True)
    shutil.copytree(SEC_DIR, sec_target)
    return project_dir


def test_apm_help_loads_local_sec_plugin(tmp_path):
    project_dir = _prepare_project(tmp_path)

    result = subprocess.run(
        [sys.executable, str(APM_PY), "--help"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "sec" in result.stdout
    assert "ошибка локального модуля" not in result.stdout.lower()


def test_sec_logs_init_creates_logs_directory(tmp_path):
    project_dir = _prepare_project(tmp_path)

    result = subprocess.run(
        [sys.executable, str(APM_PY), "sec", "logs", "init"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (project_dir / "logs").is_dir()


def test_sec_intrusion_alias_dispatches_to_init(tmp_path):
    project_dir = _prepare_project(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    script = """
from sec import intrusion
calls = []

def fake_run(*args, **kwargs):
    calls.append(kwargs.get("args"))

intrusion.sec_init.run = fake_run
intrusion.run(base_dir='.', args=['init'])
assert calls == [['--modules', 'intrusion']]
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=project_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
