#!/bin/bash
# APM Runner for Linux/macOS
# Автоматически использует venv если он есть

VENV_PYTHON="$HOME/.config/apm/venv/bin/python3"

if [ -x "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" "$HOME/.config/apm/apm.py" "$@"
else
    python3 "$HOME/.config/apm/apm.py" "$@"
fi

if [ -f "/tmp/apm_goto.tmp" ]; then
    cd "$(cat /tmp/apm_goto.tmp)" || true
    rm -f /tmp/apm_goto.tmp
fi
