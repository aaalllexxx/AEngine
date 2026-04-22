#!/bin/bash
# APM Uninstaller for Linux/macOS

set -e

APM_DIR="$HOME/.config/apm"

echo "[+] Uninstalling APM..."

# Remove config directory
if [ -d "$APM_DIR" ]; then
    rm -rf "$APM_DIR"
    echo "[+] Removed $APM_DIR"
fi

# Remove symlink
if [ -L /usr/local/bin/apm ]; then
    if [ -w /usr/local/bin ]; then
        rm -f /usr/local/bin/apm
    else
        sudo rm -f /usr/local/bin/apm
    fi
    echo "[+] Removed /usr/local/bin/apm"
fi

echo "[+] APM uninstalled successfully!"
