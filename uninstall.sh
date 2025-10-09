#!/bin/bash

# Скрипт удаления утилиты Mouse Wheel Mission Control

set -e

echo "🗑️  Удаление утилиты Mouse Wheel Mission Control..."

# Останавливаем службу
echo "⏹️  Остановка службы..."
launchctl unload "$HOME/Library/LaunchAgents/com.user.mousewheelcontrol.plist" 2>/dev/null || true

# Удаляем plist файл
echo "📋 Удаление конфигурации LaunchAgent..."
rm -f "$HOME/Library/LaunchAgents/com.user.mousewheelcontrol.plist"

# Удаляем логи
echo "🧹 Очистка логов..."
rm -f /tmp/mousewheelcontrol.log
rm -f /tmp/mousewheelcontrol.error.log

# Проверяем, что служба удалена
if ! launchctl list | grep -q "com.user.mousewheelcontrol"; then
    echo "✅ Служба успешно удалена!"
else
    echo "⚠️  Служба может быть еще активна. Попробуйте перезагрузить систему."
fi

echo ""
echo "🎉 Удаление завершено!"
echo ""
echo "📝 Дополнительные действия:"
echo "• Если вы хотите полностью удалить проект, удалите директорию:"
echo "  rm -rf $(pwd)"
echo "• Если вы хотите удалить виртуальное окружение UV:"
echo "  rm -rf .venv"

