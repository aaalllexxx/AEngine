# Руководство по сборке Android APK

## Проблема с таймаутами при сборке

При сборке Android APK через Buildozer часто возникают проблемы с таймаутами при загрузке зависимостей (Python, Android NDK, SDK). Это особенно актуально при медленном интернет-соединении или проблемах с доступом к серверам.

## Решение 1: Предварительная загрузка зависимостей

### Автоматическая загрузка через APM

При запуске `apm build app` и выборе платформы Android, APM автоматически предложит предварительно загрузить зависимости:

```bash
cd your_project
apm build app
# Выберите: 2. Android (.apk)
# Ответьте: Y на вопрос о предварительной загрузке
```

### Ручная загрузка

Вы также можете запустить скрипт предварительной загрузки отдельно:

```bash
# Linux/WSL
python3 ~/.config/apm/scripts/predownload_deps.py

# Windows (если используете Python напрямую)
python %APPDATA%\apm\scripts\predownload_deps.py
```

### Что загружается

Скрипт загружает следующие компоненты:

1. **Python 3.11.5** (~25 MB) - исходники Python для компиляции под Android
2. **Android NDK r25b** (~1 GB) - Native Development Kit для компиляции нативного кода
3. **Android SDK Tools** (~150 MB) - инструменты командной строки Android SDK

Все файлы сохраняются в `~/.buildozer/android/packages/` и проверяются по SHA256 хешу.

### Преимущества

- **Retry-логика**: автоматические повторные попытки при сбоях
- **Проверка целостности**: SHA256 хеш-суммы для всех файлов
- **Прогресс-бар**: визуальное отображение процесса загрузки
- **Экспоненциальная задержка**: умные паузы между повторными попытками

## Решение 2: Оптимизированный buildozer.spec для webview

### Использование шаблона

APM теперь предлагает оптимизированный шаблон `buildozer.spec` для AEngine приложений с webview:

```bash
cd your_project
apm build app
# Выберите: 2. Android (.apk)
# Ответьте: Y на вопрос об использовании шаблона
```

### Ключевые настройки для webview

Шаблон автоматически настраивает:

```ini
# Использование webview bootstrap вместо SDL2
p4a.bootstrap = webview

# Порт для Flask сервера
p4a.port = 5000

# Минимальные зависимости для Flask
requirements = python3,flask,jinja2,markupsafe,werkzeug,click,itsdangerous

# Включение HTML/CSS/JS файлов
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js
```

### Ручное создание buildozer.spec

Если вы хотите создать `buildozer.spec` вручную:

```bash
# Скопировать шаблон
cp ~/.config/apm/examples/buildozer_webview.spec ./buildozer.spec

# Отредактировать параметры
nano buildozer.spec
```

Обязательно измените:
- `title` - название приложения
- `package.name` - имя пакета (только латиница, без пробелов)
- `package.domain` - домен (например, com.yourcompany)

## Решение 3: Сборка в WSL (для Windows)

### Почему WSL?

Buildozer не работает на Windows напрямую. Используйте WSL (Windows Subsystem for Linux):

```powershell
# Установка WSL (PowerShell от администратора)
wsl --install --web-download

# После перезагрузки, установка Ubuntu
wsl --install -d Ubuntu
```

### Автоматическая настройка через APM

```bash
# В Windows PowerShell
cd C:\path\to\your\project
apm build app
# Выберите: 2. Android (.apk)
# Ответьте: y на вопрос о настройке WSL
```

### Ручная сборка в WSL

```bash
# Запуск WSL
wsl

# Переход в проект (Windows диски монтируются в /mnt/)
cd /mnt/c/Users/YourName/Desktop/your_project

# Сборка
apm build app
```

## Полный процесс сборки

### Шаг 1: Подготовка проекта

```bash
cd your_aengine_project

# Убедитесь, что есть main.py и config.json
ls -la
```

### Шаг 2: Предварительная загрузка (опционально)

```bash
python3 ~/.config/apm/scripts/predownload_deps.py
```

### Шаг 3: Запуск сборки

```bash
apm build app
# Выберите: 2. Android (.apk)
# Следуйте инструкциям
```

### Шаг 4: Получение APK

После успешной сборки APK будет в:
```
your_project/bin/yourapp-1.0.0-debug.apk
```

## Устранение проблем

### Ошибка: Connection timed out

**Решение**: Используйте предварительную загрузку зависимостей или VPN.

### Ошибка: fatal: not a git repository

**Решение**: Buildozer требует git. Инициализируйте репозиторий:
```bash
git init
git add .
git commit -m "Initial commit"
```

### Ошибка: Permission denied (NTFS в WSL)

**Решение**: APM автоматически копирует проект во временную директорию на Linux файловой системе.

### Ошибка: No module named 'buildozer'

**Решение**: Установите buildozer:
```bash
pip install buildozer
```

### Ошибка: Java not found

**Решение**: Установите OpenJDK:
```bash
# Ubuntu/Debian
sudo apt-get install openjdk-17-jdk

# Arch Linux
sudo pacman -S jdk-openjdk
```

## Оптимизация размера APK

### 1. Минимизация зависимостей

В `buildozer.spec` указывайте только необходимые пакеты:
```ini
# Плохо (включает ненужное)
requirements = python3,flask,numpy,pandas,matplotlib

# Хорошо (только необходимое)
requirements = python3,flask,jinja2,markupsafe,werkzeug
```

### 2. Исключение файлов

```ini
source.exclude_dirs = tests, docs, .git, __pycache__, venv
source.exclude_patterns = *.pyc, *.pyo, *.md, LICENSE
```

### 3. Использование ProGuard (опционально)

```ini
android.gradle_dependencies = com.android.tools.build:gradle:7.0.0
android.enable_androidx = True
```

## Дополнительные ресурсы

- [Buildozer документация](https://buildozer.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [AEngine документация](README.md)
- [Примеры проектов](APM/examples/)

## Поддержка

При возникновении проблем:
1. Проверьте логи в `.buildozer/android/platform/build-*/`
2. Используйте `log_level = 2` в `buildozer.spec`
3. Создайте issue на GitHub с полным логом ошибки
