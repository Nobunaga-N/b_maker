# src/bots/bot_scheduler.py - новый файл

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading

from src.bots.bot_executor import BotExecutor
from src.adb.bot_adb_controller import BotADBController
from src.utils.exceptions import BotExecutionError


class BotScheduler:
    """
    Планировщик ботов. Управляет очередью ботов, запускает их по расписанию и
    распределяет между эмуляторами.
    """

    def __init__(self, adb_controller: BotADBController, logger: Optional[logging.Logger] = None):
        self.adb_controller = adb_controller
        self.logger = logger
        self.queue = []  # Очередь ботов для запуска
        self.active_bots = {}  # Запущенные боты {bot_name: {"executor": executor, "devices": [...]}}
        self.queue_lock = threading.Lock()  # Блокировка для синхронизации доступа к очереди
        self.running = False  # Флаг работы планировщика
        self.scheduler_thread = None  # Поток планировщика

    def add_bot_to_queue(self, bot_name: str, params: Dict[str, Any]) -> bool:
        """
        Добавляет бота в очередь на выполнение.

        Args:
            bot_name: Имя бота
            params: Параметры запуска (эмуляторы, потоки, циклы, время работы и т.д.)

        Returns:
            True, если бот успешно добавлен в очередь
        """
        with self.queue_lock:
            # Добавляем бота в очередь с параметрами
            self.queue.append({
                "bot_name": bot_name,
                "params": params,
                "status": "queued",
                "added_time": time.time()
            })
            if self.logger:
                self.logger.info(f"Бот {bot_name} добавлен в очередь")
            return True

    def start_scheduler(self) -> bool:
        """
        Запускает планировщик в отдельном потоке.

        Returns:
            True, если планировщик успешно запущен
        """
        if self.running:
            return False

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

        if self.logger:
            self.logger.info("Планировщик ботов запущен")
        return True

    def stop_scheduler(self) -> bool:
        """
        Останавливает планировщик и все запущенные боты.

        Returns:
            True, если планировщик успешно остановлен
        """
        if not self.running:
            return False

        self.running = False

        # Останавливаем все запущенные боты
        for bot_name, bot_data in self.active_bots.items():
            bot_data["executor"].stop()

        # Ждем завершения потока планировщика
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        if self.logger:
            self.logger.info("Планировщик ботов остановлен")
        return True

    def _scheduler_loop(self):
        """
        Основной цикл планировщика. Проверяет очередь и запускает боты.
        """
        while self.running:
            try:
                # Проверяем очередь
                self._process_queue()

                # Проверяем статус запущенных ботов
                self._check_running_bots()

                # Небольшая пауза для экономии ресурсов
                time.sleep(1)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка в планировщике: {e}")

    def _process_queue(self):
        """
        Обрабатывает очередь ботов, запуская готовые к выполнению.
        """
        with self.queue_lock:
            # Копируем очередь, чтобы не изменять её во время итерации
            queue_copy = self.queue.copy()

        current_time = time.time()

        for bot_info in queue_copy:
            # Проверяем время запуска
            scheduled_time = bot_info["params"].get("scheduled_time")
            use_schedule = bot_info["params"].get("use_schedule", False)

            if use_schedule and scheduled_time:
                # Преобразуем строку времени в timestamp
                scheduled_dt = datetime.strptime(scheduled_time, "%d.%m.%Y %H:%M")
                scheduled_timestamp = scheduled_dt.timestamp()

                if current_time < scheduled_timestamp:
                    # Еще не время для запуска
                    continue

            # Запускаем бота
            self._start_bot(bot_info)

    def _start_bot(self, bot_info):
        """
        Запускает выполнение бота.

        Args:
            bot_info: Информация о боте для запуска
        """
        try:
            bot_name = bot_info["bot_name"]
            params = bot_info["params"]

            # Получаем список эмуляторов для запуска
            emulators = params.get("emulators", "")
            thread_count = params.get("threads", 1)
            max_cycles = params.get("cycles", 0)
            max_time = params.get("work_time", 0)

            # Парсим строку эмуляторов в список
            emulator_list = self.adb_controller.parse_emulators_string(emulators)

            # Получаем доступные эмуляторы
            # В реальной реализации используйте асинхронную версию
            # device_ids = await self.adb_controller.allocate_devices_for_bot(bot_name, emulator_list, thread_count)
            device_ids = emulator_list[:thread_count]  # Упрощенная версия

            if not device_ids:
                if self.logger:
                    self.logger.warning(f"Нет доступных эмуляторов для запуска бота {bot_name}")
                return

            # Создаем экземпляр исполнителя бота
            executor = BotExecutor(self.adb_controller, self.logger)

            # Запускаем бота на первом доступном устройстве
            # В реальной реализации надо запускать бота на всех выделенных устройствах
            executor.execute_bot(bot_name, device_ids[0], max_cycles, max_time)

            # Сохраняем информацию о запущенном боте
            self.active_bots[bot_name] = {
                "executor": executor,
                "devices": device_ids,
                "start_time": time.time(),
                "params": params
            }

            # Удаляем бота из очереди
            with self.queue_lock:
                self.queue = [b for b in self.queue if b["bot_name"] != bot_name]

            if self.logger:
                self.logger.info(f"Бот {bot_name} запущен на устройствах {device_ids}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при запуске бота {bot_info['bot_name']}: {e}")

    def _check_running_bots(self):
        """
        Проверяет статус запущенных ботов и обрабатывает завершенные.
        """
        completed_bots = []

        for bot_name, bot_data in self.active_bots.items():
            executor = bot_data["executor"]

            if not executor.is_running():
                # Бот завершил работу
                completed_bots.append(bot_name)

                if self.logger:
                    self.logger.info(f"Бот {bot_name} завершил работу")

                # Освобождаем устройства
                for device_id in bot_data["devices"]:
                    # В реальной реализации используйте асинхронную версию
                    # await self.adb_controller.unregister_bot_from_device(device_id)
                    pass

        # Удаляем завершенные боты из списка активных
        for bot_name in completed_bots:
            del self.active_bots[bot_name]

    async def change_bot_priority(self, bot_name: str, new_position: int) -> bool:
        """
        Изменяет приоритет бота в очереди.

        Args:
            bot_name: Имя бота
            new_position: Новая позиция в очереди (0 - самый высокий приоритет)

        Returns:
            True, если приоритет успешно изменен
        """
        async with self.queue_lock:
            # Находим бота в очереди
            bot_idx = -1
            for i, bot in enumerate(self.queue):
                if bot["bot_name"] == bot_name:
                    bot_idx = i
                    break

            if bot_idx == -1:
                return False  # Бот не найден

            if bot_idx == new_position:
                return True  # Позиция не изменилась

            # Извлекаем бота из очереди
            bot = self.queue.pop(bot_idx)

            # Вставляем в новую позицию
            new_position = max(0, min(new_position, len(self.queue)))
            self.queue.insert(new_position, bot)

            if self.logger:
                self.logger.info(f"Бот {bot_name} перемещен на позицию {new_position}")

            return True