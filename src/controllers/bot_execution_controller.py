# src/controllers/bot_execution_controller.py - новый файл

import asyncio
import logging
import threading
from typing import Dict, List, Any, Optional, Callable

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from src.adb.bot_adb_controller import BotADBController
from src.bots.bot_scheduler import BotScheduler
from src.bots.activity_monitor import ActivityMonitor
from src.utils.exceptions import BotExecutionError


class BotExecutionController(QObject):
    """
    Контроллер выполнения ботов. Связывает UI с модулями бизнес-логики.
    """

    # Сигналы для обновления UI
    botStarted = pyqtSignal(str, list)  # (bot_name, device_ids)
    botStopped = pyqtSignal(str)  # bot_name
    botProgress = pyqtSignal(str, dict)  # (bot_name, progress_info)
    botError = pyqtSignal(str, str)  # (bot_name, error_message)
    deviceStatusChanged = pyqtSignal(str, str)  # (device_id, status)

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.logger = logger

        # Создаем экземпляры основных классов
        self.adb_controller = BotADBController(logger=logger)
        self.bot_scheduler = BotScheduler(self.adb_controller, logger)
        self.activity_monitor = ActivityMonitor(self.adb_controller, logger)

        # Инициализируем асинхронную среду
        self.loop = asyncio.new_event_loop()
        self.async_thread = None

        # Таймер для обновления статусов эмуляторов
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_emulator_statuses)

        # Флаг для контроля завершения работы
        self.running = False

    def start(self):
        """
        Запускает контроллер и инициализирует компоненты.
        """
        if self.running:
            return

        self.running = True

        # Запускаем асинхронную среду в отдельном потоке
        self.async_thread = threading.Thread(target=self._run_async_loop)
        self.async_thread.daemon = True
        self.async_thread.start()

        # Запускаем таймер обновления статусов
        self.status_timer.start(2000)  # Обновление каждые 2 секунды

        if self.logger:
            self.logger.info("Контроллер выполнения ботов запущен")

    def stop(self):
        """
        Останавливает контроллер и освобождает ресурсы.
        """
        if not self.running:
            return

        self.running = False

        # Останавливаем таймер
        self.status_timer.stop()

        # Останавливаем асинхронную среду
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._stop_all_services(), self.loop)

        # Ждем завершения потока
        if self.async_thread and self.async_thread.is_alive():
            self.async_thread.join(timeout=5)

        if self.logger:
            self.logger.info("Контроллер выполнения ботов остановлен")

    def _run_async_loop(self):
        """
        Запускает цикл асинхронных событий в отдельном потоке.
        """
        asyncio.set_event_loop(self.loop)

        async def init_services():
            # Инициализируем ADB-контроллер
            await self.adb_controller.initialize_async()

            # Запускаем планировщик
            self.bot_scheduler.start_scheduler()

            # Запускаем мониторинг активностей
            await self.activity_monitor.start_monitoring()

        # Запускаем сервисы
        self.loop.run_until_complete(init_services())

        # Запускаем цикл обработки событий
        self.loop.run_forever()

    async def _stop_all_services(self):
        """
        Останавливает все запущенные сервисы.
        """
        # Останавливаем мониторинг активностей
        await self.activity_monitor.stop_monitoring()

        # Останавливаем планировщик
        self.bot_scheduler.stop_scheduler()

        # Останавливаем цикл обработки событий
        self.loop.stop()

    def update_emulator_statuses(self):
        """
        Обновляет статусы эмуляторов и отправляет сигналы с изменениями.
        """

        async def _update():
            try:
                # Получаем статусы устройств
                statuses = await self.adb_controller.get_all_devices_status_async()

                # Отправляем сигналы для каждого устройства
                for device_id, status in statuses.items():
                    self.deviceStatusChanged.emit(device_id, status)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка при обновлении статусов эмуляторов: {e}")

        # Запускаем асинхронную функцию в цикле событий
        asyncio.run_coroutine_threadsafe(_update(), self.loop)

    def start_bot(self, bot_name: str, params: Dict[str, Any]):
        """
        Добавляет бота в очередь на выполнение.

        Args:
            bot_name: Имя бота
            params: Параметры запуска
        """
        # Добавляем бота в очередь планировщика
        if self.bot_scheduler.add_bot_to_queue(bot_name, params):
            # Оповещаем UI о добавлении бота в очередь
            if self.logger:
                self.logger.info(f"Бот {bot_name} добавлен в очередь на выполнение")
        else:
            # Ошибка добавления в очередь
            self.botError.emit(bot_name, "Не удалось добавить бота в очередь")

    def stop_bot(self, bot_name: str):
        """
        Останавливает выполнение бота.

        Args:
            bot_name: Имя бота
        """
        # Проверяем, запущен ли бот
        if bot_name in self.bot_scheduler.active_bots:
            # Останавливаем бота
            self.bot_scheduler.active_bots[bot_name]["executor"].stop()

            # Оповещаем UI об остановке бота
            self.botStopped.emit(bot_name)

            if self.logger:
                self.logger.info(f"Бот {bot_name} остановлен")
        else:
            # Удаляем из очереди, если еще не запущен
            with self.bot_scheduler.queue_lock:
                self.bot_scheduler.queue = [
                    b for b in self.bot_scheduler.queue if b["bot_name"] != bot_name
                ]

            if self.logger:
                self.logger.info(f"Бот {bot_name} удален из очереди")

    def get_emulator_list(self):
        """
        Асинхронно получает список эмуляторов.
        """

        async def _get_emulators():
            try:
                # Получаем список эмуляторов LDPlayer
                return await self.adb_controller.get_ldplayer_list_async()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка при получении списка эмуляторов: {e}")
                return []

        # Запускаем асинхронную функцию и возвращаем Future
        return asyncio.run_coroutine_threadsafe(_get_emulators(), self.loop)

    def start_emulator(self, emu_id: str):
        """
        Запускает эмулятор LDPlayer.

        Args:
            emu_id: ID эмулятора
        """

        async def _start_emulator():
            try:
                # Запускаем эмулятор
                result = await self.adb_controller.start_ldplayer_async(emu_id)

                if result:
                    # Обновляем статус
                    status = await self.adb_controller.update_device_status_async(emu_id)
                    self.deviceStatusChanged.emit(emu_id, status)

                    if self.logger:
                        self.logger.info(f"Эмулятор {emu_id} запущен")
                else:
                    if self.logger:
                        self.logger.error(f"Не удалось запустить эмулятор {emu_id}")

                return result
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка при запуске эмулятора {emu_id}: {e}")
                return False

        # Запускаем асинхронную функцию и возвращаем Future
        return asyncio.run_coroutine_threadsafe(_start_emulator(), self.loop)

    def stop_emulator(self, emu_id: str):
        """
        Останавливает эмулятор LDPlayer.

        Args:
            emu_id: ID эмулятора
        """

        async def _stop_emulator():
            try:
                # Останавливаем эмулятор
                result = await self.adb_controller.stop_ldplayer_async(emu_id)

                if result:
                    # Обновляем статус
                    self.deviceStatusChanged.emit(emu_id, "offline")

                    if self.logger:
                        self.logger.info(f"Эмулятор {emu_id} остановлен")
                else:
                    if self.logger:
                        self.logger.error(f"Не удалось остановить эмулятор {emu_id}")

                return result
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка при остановке эмулятора {emu_id}: {e}")
                return False

        # Запускаем асинхронную функцию и возвращаем Future
        return asyncio.run_coroutine_threadsafe(_stop_emulator(), self.loop)

    def restart_emulator(self, emu_id: str):
        """
        Перезапускает эмулятор LDPlayer.

        Args:
            emu_id: ID эмулятора
        """

        async def _restart_emulator():
            try:
                # Перезапускаем эмулятор
                result = await self.adb_controller.reboot_ldplayer_async(emu_id)

                if result:
                    # Обновляем статус
                    status = await self.adb_controller.update_device_status_async(emu_id)
                    self.deviceStatusChanged.emit(emu_id, status)

                    if self.logger:
                        self.logger.info(f"Эмулятор {emu_id} перезапущен")
                else:
                    if self.logger:
                        self.logger.error(f"Не удалось перезапустить эмулятор {emu_id}")

                return result
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка при перезапуске эмулятора {emu_id}: {e}")
                return False

        # Запускаем асинхронную функцию и возвращаем Future
        return asyncio.run_coroutine_threadsafe(_restart_emulator(), self.loop)

    def open_emulator_console(self, emu_id: str):
        """
        Открывает консоль эмулятора LDPlayer.

        Args:
            emu_id: ID эмулятора
        """
        try:
            # Выполняем команду для открытия консоли
            command = f"quicklook --index {emu_id}"
            future = asyncio.run_coroutine_threadsafe(
                self.adb_controller.execute_ldplayer_command_async(command),
                self.loop
            )

            # Получаем результат с таймаутом
            result = future.result(timeout=5)

            if self.logger:
                self.logger.info(f"Открыта консоль эмулятора {emu_id}")

            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при открытии консоли эмулятора {emu_id}: {e}")
            return False