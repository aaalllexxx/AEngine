#!/bin/bash

echo "========================================"
echo "  AEngine - Автоматический установщик"
echo "========================================"
echo ""

# Определение ОС
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "[ОШИБКА] Неподдерживаемая ОС: $OSTYPE"
    exit 1
fi

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "[ВНИМАНИЕ] Для установки Python и Git могут потребоваться права sudo."
    echo "Скрипт запросит пароль при необходимости."
    echo ""
fi

# Проверка Python
echo "[1/5] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python не найден. Установка Python..."
    
    if [ "$OS" == "linux" ]; then
        # Определение дистрибутива Linux
        if [ -f /etc/debian_version ]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif [ -f /etc/redhat-release ]; then
            sudo yum install -y python3 python3-pip
        elif [ -f /etc/arch-release ]; then
            sudo pacman -S --noconfirm python python-pip
        else
            echo "[ОШИБКА] Неподдерживаемый дистрибутив Linux"
            exit 1
        fi
    elif [ "$OS" == "macos" ]; then
        # Проверка Homebrew
        if ! command -v brew &> /dev/null; then
            echo "Установка Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3
    fi
    
    echo "Python успешно установлен!"
else
    echo "Python уже установлен: $(python3 --version)"
fi
echo ""

# Проверка Git
echo "[2/5] Проверка Git..."
if ! command -v git &> /dev/null; then
    echo "Git не найден. Установка Git..."
    
    if [ "$OS" == "linux" ]; then
        if [ -f /etc/debian_version ]; then
            sudo apt-get install -y git
        elif [ -f /etc/redhat-release ]; then
            sudo yum install -y git
        elif [ -f /etc/arch-release ]; then
            sudo pacman -S --noconfirm git
        fi
    elif [ "$OS" == "macos" ]; then
        brew install git
    fi
    
    echo "Git успешно установлен!"
else
    echo "Git уже установлен: $(git --version)"
fi
echo ""

# Обновление pip
echo "[3/5] Обновление pip..."
python3 -m pip install --upgrade pip --quiet
echo "pip обновлен."
echo ""

# Установка зависимостей
echo "[4/5] Установка зависимостей Python..."
if [ -f "APM/requirements.txt" ]; then
    python3 -m pip install -r APM/requirements.txt --quiet
    echo "Зависимости установлены."
else
    echo "[ПРЕДУПРЕЖДЕНИЕ] Файл APM/requirements.txt не найден."
fi
echo ""

# Установка APM
echo "[5/5] Установка APM (Package Manager)..."
if [ -f "APM/scripts/setup.sh" ]; then
    cd APM/scripts
    chmod +x setup.sh
    ./setup.sh
    cd ../..
    echo "APM установлен."
else
    echo "[ПРЕДУПРЕЖДЕНИЕ] Скрипт установки APM не найден."
fi
echo ""

echo "========================================"
echo "  Установка завершена!"
echo "========================================"
echo ""
echo "Теперь вы можете использовать команду 'apm' для управления проектами."
echo ""
echo "Примеры команд:"
echo "  apm create          - Создать новый проект"
echo "  apm list            - Показать все проекты"
echo "  apm docs            - Открыть документацию"
echo ""
