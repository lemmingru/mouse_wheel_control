#!/usr/bin/env python3
"""
Утилита для открытия Mission Control при нажатии на колесо мыши
"""

import sys
import subprocess
import signal
import time
from Quartz import (
    CGEventTapCreate,
    kCGHIDEventTap,
    kCGEventTapOptionListenOnly,
    kCGEventOtherMouseDown,
    CGEventMaskBit,
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopRemoveSource,
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
        self.last_click_time = 0
        self.debounce_interval = 0.5  # 500ms между нажатиями
        
    def open_mission_control(self):
        """Открывает Mission Control через AppleScript"""
        try:
            # Используем AppleScript для эмуляции нажатия F3 (код 160)
            script = 'tell application "System Events" to key code 160'
            subprocess.run(["osascript", "-e", script], check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при открытии Mission Control: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
    
    def event_callback(self, proxy, event_type, event, refcon):
        """Обработчик событий мыши"""
        if event_type == kCGEventOtherMouseDown:
            # Получаем номер кнопки мыши
            button_number = CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber)
            if button_number == 2:  # Средняя кнопка мыши (колесо)
                # Debouncing: игнорируем слишком частые нажатия
                current_time = time.time()
                if current_time - self.last_click_time >= self.debounce_interval:
                    self.last_click_time = current_time
                    self.open_mission_control()

        return event
    
    def setup_event_tap(self):
        """Настройка перехвата событий мыши"""
        self.event_tap = CGEventTapCreate(
            kCGHIDEventTap,  # Перехватываем события на уровне HID
            0,  # Приоритет
            kCGEventTapOptionListenOnly,  # Только прослушивание
            CGEventMaskBit(kCGEventOtherMouseDown),  # Только события средней кнопки мыши
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
        if self.run_loop_source:
            CFRunLoopRemoveSource(
                CFRunLoopGetCurrent(),
                self.run_loop_source,
                kCFRunLoopDefaultMode
            )
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

