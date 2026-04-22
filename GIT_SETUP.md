# Настройка Git Submodules для AEngine

Это руководство поможет вам настроить AEngineApps и APM как Git submodules.

## Что такое Git Submodules?

Git submodules позволяют включать один Git репозиторий в другой как подкаталог. Это идеально для AEngine, где:
- **AEngineApps** — отдельный репозиторий фреймворка
- **APM** — отдельный репозиторий package manager
- **AEngine** — основной репозиторий, объединяющий все компоненты

## Первоначальная настройка

### Шаг 1: Создайте отдельные репозитории

Сначала создайте репозитории на GitHub для каждого компонента:

1. **AEngineApps**: `https://github.com/yourusername/AEngineApps`
2. **APM**: `https://github.com/yourusername/APM`
3. **AEngine**: `https://github.com/yourusername/AEngine` (основной)

### Шаг 2: Подготовьте существующие папки

Если у вас уже есть папки AEngineApps и APM с кодом:

```bash
cd c:/Users/Администратор/Desktop/AEngine

# Создайте резервные копии
mkdir ../backup
xcopy AEngineApps ../backup/AEngineApps /E /I /H
xcopy APM ../backup/APM /E /I /H

# Удалите существующие папки (они будут заменены submodules)
rmdir /S /Q AEngineApps
rmdir /S /Q APM
```

### Шаг 3: Инициализируйте Git репозитории для компонентов

#### Для AEngineApps:

```bash
cd ../backup/AEngineApps
git init
git add .
git commit -m "Initial commit: AEngineApps framework"
git branch -M main
git remote add origin https://github.com/yourusername/AEngineApps.git
git push -u origin main
```

#### Для APM:

```bash
cd ../APM
git init
git add .
git commit -m "Initial commit: APM package manager"
git branch -M main
git remote add origin https://github.com/yourusername/APM.git
git push -u origin main
```

### Шаг 4: Добавьте submodules в основной репозиторий

```bash
cd c:/Users/Администратор/Desktop/AEngine

# Инициализируйте основной репозиторий (если еще не сделано)
git init
git add .gitignore .gitmodules
git commit -m "Add gitignore and gitmodules configuration"

# Добавьте submodules
git submodule add https://github.com/yourusername/AEngineApps.git AEngineApps
git submodule add https://github.com/yourusername/APM.git APM

# Зафиксируйте изменения
git add .
git commit -m "Add AEngineApps and APM as submodules"

# Отправьте в удаленный репозиторий
git remote add origin https://github.com/yourusername/AEngine.git
git push -u origin main
```

## Клонирование проекта с submodules

### Вариант 1: Клонирование с автоматической инициализацией

```bash
git clone --recursive https://github.com/yourusername/AEngine.git
```

### Вариант 2: Клонирование с ручной инициализацией

```bash
git clone https://github.com/yourusername/AEngine.git
cd AEngine
git submodule init
git submodule update
```

### Вариант 3: Одна команда для обновления

```bash
git clone https://github.com/yourusername/AEngine.git
cd AEngine
git submodule update --init --recursive
```

## Работа с submodules

### Обновление всех submodules до последней версии

```bash
git submodule update --remote --merge
```

### Обновление конкретного submodule

```bash
cd AEngineApps
git pull origin main
cd ..
git add AEngineApps
git commit -m "Update AEngineApps to latest version"
git push
```

### Проверка статуса submodules

```bash
git submodule status
```

### Внесение изменений в submodule

```bash
# Перейдите в submodule
cd AEngineApps

# Создайте ветку
git checkout -b feature/new-feature

# Внесите изменения
# ... редактируйте файлы ...

# Зафиксируйте изменения
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Вернитесь в основной репозиторий
cd ..

# Обновите ссылку на submodule
git add AEngineApps
git commit -m "Update AEngineApps submodule"
git push
```

## Автоматизация

### Скрипт для инициализации (init_submodules.bat)

Создайте файл `init_submodules.bat`:

```batch
@echo off
echo Initializing Git submodules...
git submodule init
git submodule update --recursive
echo Done!
pause
```

### Скрипт для обновления (update_submodules.bat)

Создайте файл `update_submodules.bat`:

```batch
@echo off
echo Updating all submodules to latest version...
git submodule update --remote --merge
echo Done!
pause
```

## Структура проекта после настройки

```
AEngine/                          # Основной репозиторий
├── .git/                         # Git основного репозитория
├── .gitignore                    # Игнорируемые файлы
├── .gitmodules                   # Конфигурация submodules
├── AEngineApps/                  # Submodule (отдельный репозиторий)
│   └── .git                      # Ссылка на submodule
├── APM/                          # Submodule (отдельный репозиторий)
│   └── .git                      # Ссылка на submodule
├── sec/                          # Часть основного репозитория
├── README.md
├── ARCHITECTURE.md
└── ...
```

## Важные замечания

### 1. Submodules указывают на конкретный commit

Когда вы добавляете submodule, основной репозиторий запоминает конкретный commit submodule. Это означает:
- Другие разработчики получат ту же версию
- Нужно явно обновлять submodules командой `git submodule update --remote`

### 2. Работа в команде

Когда коллега клонирует репозиторий:

```bash
git clone https://github.com/yourusername/AEngine.git
cd AEngine
git submodule update --init --recursive
```

Когда вы обновили submodule, коллеги должны выполнить:

```bash
git pull
git submodule update --recursive
```

### 3. Изменения в submodules

Если вы изменили код в AEngineApps или APM:

1. Зафиксируйте изменения в submodule
2. Push в репозиторий submodule
3. Вернитесь в основной репозиторий
4. Зафиксируйте обновленную ссылку на submodule
5. Push в основной репозиторий

## Альтернатива: Git Subtree

Если submodules кажутся сложными, рассмотрите Git Subtree:

```bash
# Добавить subtree
git subtree add --prefix AEngineApps https://github.com/yourusername/AEngineApps.git main --squash

# Обновить subtree
git subtree pull --prefix AEngineApps https://github.com/yourusername/AEngineApps.git main --squash

# Отправить изменения обратно
git subtree push --prefix AEngineApps https://github.com/yourusername/AEngineApps.git main
```

**Преимущества subtree:**
- Проще для пользователей (не нужно инициализировать)
- Код включен в основной репозиторий

**Недостатки subtree:**
- Больший размер репозитория
- Сложнее синхронизировать изменения

## Рекомендации

Для AEngine рекомендуется использовать **submodules**, потому что:

1. AEngineApps и APM — независимые компоненты
2. Они могут использоваться отдельно
3. Разные версии для разных проектов
4. Чистая история изменений для каждого компонента

## Troubleshooting

### Проблема: Submodule не обновляется

```bash
git submodule deinit -f AEngineApps
git rm -f AEngineApps
git submodule add https://github.com/yourusername/AEngineApps.git AEngineApps
```

### Проблема: Конфликты при обновлении

```bash
cd AEngineApps
git fetch origin
git reset --hard origin/main
cd ..
git submodule update --recursive
```

### Проблема: Пустые папки submodules

```bash
git submodule update --init --recursive --force
```

## Дополнительные ресурсы

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub Submodules Guide](https://github.blog/2016-02-01-working-with-submodules/)
- [Atlassian Submodules Tutorial](https://www.atlassian.com/git/tutorials/git-submodule)

---

**Следующие шаги:**

1. Создайте репозитории на GitHub
2. Выполните команды из раздела "Первоначальная настройка"
3. Обновите URL в `.gitmodules` на реальные
4. Протестируйте клонирование проекта
