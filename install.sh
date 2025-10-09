#!/bin/bash

# Скрипт установки утилиты Mouse Wheel Mission Control

set -e

echo "🚀 Установка утилиты Mouse Wheel Mission Control..."

# Проверяем, что мы находимся в правильной директории
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Ошибка: pyproject.toml не найден. Запустите скрипт из корневой директории проекта."
    exit 1
fi

# Проверяем наличие UV
if ! command -v uv &> /dev/null; then
    echo "❌ UV не установлен. Установите UV: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
uv sync

# Проверяем, что виртуальное окружение создано
if [ ! -d ".venv" ]; then
    echo "❌ Ошибка: Виртуальное окружение не создано"
    exit 1
fi

# Создаем директорию для LaunchAgents если её нет
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

# Копируем plist файл с подстановкой путей
echo "📋 Копирование конфигурации LaunchAgent..."
PROJECT_PATH=$(pwd)
sed "s|PROJECT_PATH|$PROJECT_PATH|g" com.user.mousewheelcontrol.plist.template > "$LAUNCH_AGENTS_DIR/com.user.mousewheelcontrol.plist"

# Загружаем службу
echo "🔄 Загрузка службы..."
launchctl bootout gui/$(id -u) "$LAUNCH_AGENTS_DIR/com.user.mousewheelcontrol.plist" 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$LAUNCH_AGENTS_DIR/com.user.mousewheelcontrol.plist"

# Проверяем статус службы
echo "✅ Проверка статуса службы..."
if launchctl list | grep -q "com.user.mousewheelcontrol"; then
    echo "✅ Служба успешно загружена!"
else
    echo "⚠️  Служба загружена, но может потребоваться перезагрузка системы"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📝 Важные замечания:"
echo "1. При первом запуске macOS может запросить разрешение на 'Универсальный доступ'"
echo "2. Перейдите в Системные настройки → Конфиденциальность и безопасность → Универсальный доступ"
echo "3. Добавьте Terminal (или Python) в список разрешенных приложений"
echo "4. Утилита будет автоматически запускаться при входе в систему"
echo ""
echo "🔧 Управление службой:"
echo "• Остановить: launchctl unload ~/Library/LaunchAgents/com.user.mousewheelcontrol.plist"
echo "• Запустить: launchctl load ~/Library/LaunchAgents/com.user.mousewheelcontrol.plist"
echo "• Логи: tail -f /tmp/mousewheelcontrol.log"
echo ""
echo "🖱️  Теперь нажмите на колесо мыши для открытия Mission Control!"

