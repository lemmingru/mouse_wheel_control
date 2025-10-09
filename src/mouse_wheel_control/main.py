#!/usr/bin/env python3
"""
Утилита для открытия Mission Control при нажатии на колесо мыши
"""

import sys
import subprocess
import signal
from Quartz import (
    CGEventTapCreate, 
    kCGHIDEventTap, 
    kCGEventTapOptionListenOnly,
    kCGEventOtherMouseDown,
    kCGEventMaskForAllEvents,
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    kCFRunLoopDefaultMode,
    CGEventTapEnable,
    CFRunLoopRun,
    CGEventGetIntegerValueField,
    kCGMouseEventButtonNumber
)


class MouseWheelMissionControl:
    def __init__(self):
        self.event_tap = None
        self.run_loop_source = None
        self.running = True
        
    def open_mission_control(self):
        """Открывает Mission Control через AppleScript"""
        try:
            # Используем AppleScript для эмуляции нажатия F3 (код 160)
            script = 'tell application "System Events" to key code 160'
            subprocess.run(["osascript", "-e", script], check=True)
            print("Mission Control открыт")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при открытии Mission Control: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
    
    def event_callback(self, proxy, event_type, event, refcon):
        """Обработчик событий мыши"""
        if event_type == kCGEventOtherMouseDown:
            # Получаем номер кнопки мыши
            button_number = CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber)
            if button_number == 2:  # Средняя кнопка мыши (колесо)
                print("Обнаружено нажатие на колесо мыши")
                self.open_mission_control()
        
        return event
    
    def setup_event_tap(self):
        """Настройка перехвата событий мыши"""
        self.event_tap = CGEventTapCreate(
            kCGHIDEventTap,  # Перехватываем события на уровне HID
            0,  # Приоритет
            kCGEventTapOptionListenOnly,  # Только прослушивание
            kCGEventMaskForAllEvents,  # Все события
            self.event_callback,  # Функция обратного вызова
            None
        )
        
        if not self.event_tap:
            print("Ошибка: Не удалось создать перехватчик событий")
            print("Убедитесь, что приложению предоставлены права 'Универсальный доступ'")
            print("в Системных настройках → Конфиденциальность и безопасность")
            return False
            
        return True
    
    def setup_run_loop(self):
        """Настройка run loop для непрерывной работы"""
        self.run_loop_source = CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        CFRunLoopAddSource(
            CFRunLoopGetCurrent(), 
            self.run_loop_source, 
            kCFRunLoopDefaultMode
        )
        CGEventTapEnable(self.event_tap, True)
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print(f"\nПолучен сигнал {signum}, завершение работы...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.event_tap:
            CGEventTapEnable(self.event_tap, False)
        print("Очистка ресурсов завершена")
    
    def run(self):
        """Основной цикл работы"""
        print("Запуск утилиты Mouse Wheel Mission Control...")
        print("Нажмите Ctrl+C для завершения работы")
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if not self.setup_event_tap():
            return False
            
        self.setup_run_loop()
        
        print("Утилита запущена. Нажмите на колесо мыши для открытия Mission Control")
        
        try:
            # Основной цикл
            CFRunLoopRun()
        except KeyboardInterrupt:
            print("\nПолучен сигнал прерывания")
        finally:
            self.cleanup()
        
        return True


def main():
    """Точка входа в программу"""
    app = MouseWheelMissionControl()
    success = app.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

