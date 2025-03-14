# src/adb/bot_adb_controller.py
import asyncio
import logging
import time
from typing import List, Dict, Optional, Tuple, Set, Any, Union
from datetime import datetime

from src.adb.enhanced_adb_controller import EnhancedADBController
from src.utils.exceptions import ADBConnectionError, ADBCommandError, EmulatorError


class BotADBController(EnhancedADBController):
    """
    Специализированный контроллер ADB для работы с ботами.
    Объединяет возможности EnhancedADBController с функциями для управления очередью ботов,
    обеспечивает асинхронное управление несколькими эмуляторами.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5037,
                 logger: Optional[logging.Logger] = None,
                 max_workers: int = 10):
        """
        Инициализирует контроллер ADB для ботов.

        Args:
            host: Адрес ADB-сервера.
            port: Порт ADB-сервера.
            logger: Объект логирования.
            max_workers: Максимальное количество потоков для параллельного выполнения.
        """
        super().__init__(host, port, logger, max_workers)

        # Структуры данных для управления ботами и эмуляторами
        self.active_bots = {}  # {bot_name: {"devices": [device_ids], "status": status, "start_time": time}}
        self.device_bot_map = {}  # {device_id: bot_name} - для определения, какой бот запущен на устройстве
        self.queued_bots = []  # Очередь ботов, ожидающих запуска
        self.queue_lock = asyncio.Lock()  # Для синхронизации доступа к очереди ботов

        # Статистика работы ботов
        self.bot_stats = {}  # {bot_name: {"runs": count, "total_time": seconds, "last_run": timestamp}}

    async def initialize_controller(self) -> bool:
        """
        Полная инициализация контроллера: проверка сервера ADB, поиск устройств,
        подготовка к работе.

        Returns:
            True если инициализация успешна, False в противном случае
        """
        try:
            # Инициализируем базовый контроллер
            await self.initialize_async()

            # Получаем актуальный список доступных эмуляторов
            emulators = await self.get_ldplayer_list_async()

            if self.logger:
                self.logger.info(f"BotADBController инициализирован. Доступные эмуляторы: {emulators}")

            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка инициализации BotADBController: {e}")
            return False

    async def allocate_devices_for_bot(self, bot_name: str, emulators: List[str],
                                       thread_count: int) -> List[str]:
        """
        Выделяет устройства для запуска бота с учетом ограничения по потокам.

        Args:
            bot_name: Имя бота
            emulators: Список ID эмуляторов
            thread_count: Максимальное количество потоков (устройств)

        Returns:
            Список ID устройств, выделенных для бота
        """
        async with self.queue_lock:
            # Получаем статусы всех устройств
            device_statuses = await self.get_all_devices_status_async()

            # Фильтруем только доступные устройства из запрошенного списка
            available_devices = []
            for emu_id in emulators:
                if emu_id in device_statuses and device_statuses[emu_id] == "ready":
                    available_devices.append(emu_id)

            # Ограничиваем количество устройств согласно thread_count
            allocated_devices = available_devices[:thread_count]

            # Регистрируем бота на этих устройствах
            for device_id in allocated_devices:
                await self.register_bot_on_device(device_id, bot_name)

            if self.logger:
                self.logger.info(f"Для бота {bot_name} выделены устройства: {allocated_devices}")

            return allocated_devices

    async def register_bot_on_device(self, device_id: str, bot_name: str,
                                     game_name: str = "", package_name: str = "") -> bool:
        """
        Регистрирует бота на устройстве, помечая устройство как занятое.

        Args:
            device_id: Идентификатор устройства
            bot_name: Имя бота
            game_name: Название игры (опционально)
            package_name: Имя пакета игры (опционально)

        Returns:
            True если регистрация успешна
        """
        try:
            # Обновляем соответствие устройство-бот
            self.device_bot_map[device_id] = bot_name

            # Обновляем статус устройства
            self._device_status[device_id] = "busy"

            # Если это первое устройство для бота, инициализируем его запись
            if bot_name not in self.active_bots:
                self.active_bots[bot_name] = {
                    "devices": [device_id],
                    "status": "running",
                    "start_time": time.time(),
                    "game_name": game_name,
                    "package_name": package_name
                }
            else:
                # Добавляем устройство к списку устройств бота
                self.active_bots[bot_name]["devices"].append(device_id)

            # Обновляем информацию об устройстве
            self._device_game_map[device_id] = {
                "game": game_name,
                "package": package_name
            }

            if self.logger:
                self.logger.info(f"Бот {bot_name} зарегистрирован на устройстве {device_id}")

            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при регистрации бота {bot_name} на устройстве {device_id}: {e}")
            return False

    async def unregister_bot_from_device(self, device_id: str) -> bool:
        """
        Отменяет регистрацию бота с устройства, помечая устройство как свободное.

        Args:
            device_id: Идентификатор устройства

        Returns:
            True если отмена регистрации успешна
        """
        try:
            # Проверяем, есть ли устройство в карте устройство-бот
            if device_id not in self.device_bot_map:
                return False

            bot_name = self.device_bot_map[device_id]

            # Удаляем устройство из карты
            del self.device_bot_map[device_id]

            # Устанавливаем статус устройства как готовый
            self._device_status[device_id] = "ready"

            # Удаляем устройство из списка устройств бота
            if bot_name in self.active_bots:
                if device_id in self.active_bots[bot_name]["devices"]:
                    self.active_bots[bot_name]["devices"].remove(device_id)

                # Если у бота не осталось устройств, удаляем его из активных
                if not self.active_bots[bot_name]["devices"]:
                    # Обновляем статистику бота перед удалением
                    run_time = time.time() - self.active_bots[bot_name]["start_time"]
                    if bot_name not in self.bot_stats:
                        self.bot_stats[bot_name] = {"runs": 0, "total_time": 0, "last_run": None}

                    self.bot_stats[bot_name]["runs"] += 1
                    self.bot_stats[bot_name]["total_time"] += run_time
                    self.bot_stats[bot_name]["last_run"] = datetime.now().isoformat()

                    # Удаляем бота из активных
                    del self.active_bots[bot_name]

            # Очищаем информацию об игре на устройстве
            if device_id in self._device_game_map:
                del self._device_game_map[device_id]

            if self.logger:
                self.logger.info(f"Бот {bot_name} отменен на устройстве {device_id}")

            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при отмене регистрации бота на устройстве {device_id}: {e}")
            return False

    async def add_bot_to_queue(self, bot_name: str, params: Dict[str, Any]) -> bool:
        """
        Добавляет бота в очередь для последующего запуска.

        Args:
            bot_name: Имя бота
            params: Параметры запуска бота

        Returns:
            True если бот успешно добавлен в очередь
        """
        async with self.queue_lock:
            # Создаем запись для бота в очереди
            bot_queue_item = {
                "bot_name": bot_name,
                "params": params,
                "queued_time": time.time(),
                "priority": params.get("priority", 0)
            }

            # Добавляем в очередь с учетом приоритета
            inserted = False
            for i, item in enumerate(self.queued_bots):
                if item["priority"] < bot_queue_item["priority"]:
                    self.queued_bots.insert(i, bot_queue_item)
                    inserted = True
                    break

            if not inserted:
                self.queued_bots.append(bot_queue_item)

            if self.logger:
                self.logger.info(f"Бот {bot_name} добавлен в очередь")

            return True

    async def remove_bot_from_queue(self, bot_name: str) -> bool:
        """
        Удаляет бота из очереди.

        Args:
            bot_name: Имя бота

        Returns:
            True если бот успешно удален из очереди
        """
        async with self.queue_lock:
            initial_length = len(self.queued_bots)

            # Фильтруем очередь, оставляя только записи с другими именами ботов
            self.queued_bots = [item for item in self.queued_bots if item["bot_name"] != bot_name]

            # Если длина изменилась, значит бот был удален
            if len(self.queued_bots) < initial_length:
                if self.logger:
                    self.logger.info(f"Бот {bot_name} удален из очереди")
                return True

            return False

    async def get_next_bot_from_queue(self) -> Optional[Dict[str, Any]]:
        """
        Получает следующего бота из очереди для запуска.

        Returns:
            Словарь с данными бота или None, если очередь пуста
        """
        async with self.queue_lock:
            if not self.queued_bots:
                return None

            # Берем первого бота из очереди (с наивысшим приоритетом)
            next_bot = self.queued_bots.pop(0)

            if self.logger:
                self.logger.info(f"Бот {next_bot['bot_name']} извлечен из очереди для запуска")

            return next_bot

    async def get_active_bots(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает копию списка активных ботов и их статусов.

        Returns:
            Словарь {имя_бота: информация_о_боте}
        """
        # Создаем копию для безопасного доступа
        return self.active_bots.copy()

    async def get_queue_status(self) -> List[Dict[str, Any]]:
        """
        Возвращает текущее состояние очереди ботов.

        Returns:
            Список ботов в очереди с их параметрами
        """
        async with self.queue_lock:
            # Создаем копию для безопасного доступа
            return self.queued_bots.copy()

    async def get_bot_status(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о состоянии бота.

        Args:
            bot_name: Имя бота

        Returns:
            Словарь с информацией о боте или None, если бот не найден
        """
        # Сначала проверяем активные боты
        if bot_name in self.active_bots:
            status = self.active_bots[bot_name].copy()
            status["type"] = "active"
            return status

        # Затем проверяем очередь
        async with self.queue_lock:
            for item in self.queued_bots:
                if item["bot_name"] == bot_name:
                    status = item.copy()
                    status["type"] = "queued"
                    return status

        # Проверяем статистику завершенных ботов
        if bot_name in self.bot_stats:
            status = self.bot_stats[bot_name].copy()
            status["type"] = "completed"
            return status

        return None

    async def stop_bot(self, bot_name: str) -> bool:
        """
        Останавливает выполнение бота на всех его устройствах.

        Args:
            bot_name: Имя бота для остановки

        Returns:
            True если остановка успешна, False если бот не найден
        """
        # Проверяем, запущен ли бот
        if bot_name not in self.active_bots:
            # Также проверяем, есть ли бот в очереди
            async with self.queue_lock:
                for i, item in enumerate(self.queued_bots):
                    if item["bot_name"] == bot_name:
                        self.queued_bots.pop(i)
                        if self.logger:
                            self.logger.info(f"Бот {bot_name} удален из очереди")
                        return True
            return False

        # Получаем список устройств бота
        devices = self.active_bots[bot_name]["devices"].copy()

        # Отменяем регистрацию бота на всех его устройствах
        success = True
        for device_id in devices:
            if not await self.unregister_bot_from_device(device_id):
                success = False

        if self.logger:
            self.logger.info(f"Бот {bot_name} остановлен на устройствах {devices}")

        return success

    async def stop_all_bots(self) -> bool:
        """
        Останавливает все активные боты и очищает очередь.

        Returns:
            True если операция успешна
        """
        try:
            # Получаем список всех активных ботов
            active_bots = list(self.active_bots.keys())

            # Останавливаем каждого бота
            for bot_name in active_bots:
                await self.stop_bot(bot_name)

            # Очищаем очередь
            async with self.queue_lock:
                self.queued_bots = []

            if self.logger:
                self.logger.info("Все боты остановлены, очередь очищена")

            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при остановке всех ботов: {e}")
            return False

    async def get_device_bot(self, device_id: str) -> Optional[str]:
        """
        Возвращает имя бота, запущенного на устройстве.

        Args:
            device_id: Идентификатор устройства

        Returns:
            Имя бота или None, если на устройстве не запущен бот
        """
        return self.device_bot_map.get(device_id)

    async def get_bot_devices(self, bot_name: str) -> List[str]:
        """
        Возвращает список устройств, на которых запущен указанный бот.

        Args:
            bot_name: Имя бота

        Returns:
            Список идентификаторов устройств
        """
        if bot_name in self.active_bots:
            return self.active_bots[bot_name]["devices"].copy()
        return []

    async def check_and_start_queued_bots(self) -> int:
        """
        Проверяет очередь ботов и запускает те, которые могут быть запущены.

        Returns:
            Количество запущенных ботов
        """
        launched_count = 0

        # Получаем доступные устройства
        device_statuses = await self.get_all_devices_status_async()
        available_devices = [id for id, status in device_statuses.items() if status == "ready"]

        if not available_devices:
            return 0

        # Проверяем очередь ботов на наличие тех, которые можно запустить
        async with self.queue_lock:
            if not self.queued_bots:
                return 0

            # Анализируем текущее время для проверки запланированных ботов
            current_time = time.time()

            for i in range(len(self.queued_bots)):
                if i >= len(self.queued_bots):  # Защита от изменения размера списка
                    break

                bot_info = self.queued_bots[i]
                params = bot_info["params"]

                # Проверяем, должен ли бот быть запущен по расписанию
                if params.get("use_schedule", False):
                    scheduled_time = params.get("scheduled_time")
                    if scheduled_time:
                        try:
                            # Преобразуем строку времени в timestamp
                            scheduled_dt = datetime.strptime(scheduled_time, "%d.%m.%Y %H:%M")
                            scheduled_timestamp = scheduled_dt.timestamp()

                            # Если еще не время, пропускаем этот бот
                            if current_time < scheduled_timestamp:
                                continue
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Ошибка при проверке расписания бота {bot_info['bot_name']}: {e}")

                # Проверяем, есть ли доступные эмуляторы для этого бота
                emulators_str = params.get("emulators", "")
                thread_count = params.get("threads", 1)

                # Парсим строку с эмуляторами
                requested_emulators = await self.parse_emulators_string(emulators_str)

                # Пересечение запрошенных эмуляторов и доступных
                usable_emulators = [emu for emu in requested_emulators if emu in available_devices]

                # Если нет доступных эмуляторов, пропускаем этот бот
                if not usable_emulators:
                    continue

                # Здесь мы можем запустить бота, так как есть доступные эмуляторы
                bot_name = bot_info["bot_name"]

                # Извлекаем бота из очереди
                self.queued_bots.pop(i)

                # Выделяем устройства для бота
                allocated_devices = usable_emulators[:thread_count]

                # Запускаем бота, в реальной реализации здесь будет вызов bot_executor
                # для каждого выделенного устройства
                for device_id in allocated_devices:
                    await self.register_bot_on_device(device_id, bot_name)
                    # Отмечаем устройство как занятое
                    available_devices.remove(device_id)

                launched_count += 1

                # Если больше нет доступных устройств, выходим из цикла
                if not available_devices:
                    break

        return launched_count

    async def cleanup_crashed_devices(self) -> int:
        """
        Проверяет и очищает статусы устройств, которые вылетели или недоступны.

        Returns:
            Количество очищенных устройств
        """
        cleaned_count = 0

        # Получаем все устройства, отмеченные как занятые
        busy_devices = [device_id for device_id, status in self._device_status.items()
                        if status == "busy"]

        for device_id in busy_devices:
            # Проверяем фактический статус устройства
            is_available = await self.check_device_status_async(device_id)

            if not is_available:
                # Устройство недоступно, очищаем его статус
                if device_id in self.device_bot_map:
                    bot_name = self.device_bot_map[device_id]
                    await self.unregister_bot_from_device(device_id)
                    if self.logger:
                        self.logger.warning(
                            f"Устройство {device_id} недоступно, бот {bot_name} отменен на этом устройстве")

                # Отмечаем устройство как offline
                self._device_status[device_id] = "offline"
                cleaned_count += 1

        return cleaned_count

    async def reorder_queue(self, bot_name: str, new_position: int) -> bool:
        """
        Изменяет позицию бота в очереди.

        Args:
            bot_name: Имя бота
            new_position: Новая позиция (начиная с 0)

        Returns:
            True если позиция изменена успешно
        """
        async with self.queue_lock:
            # Ищем бота в очереди
            bot_idx = -1
            for i, item in enumerate(self.queued_bots):
                if item["bot_name"] == bot_name:
                    bot_idx = i
                    break

            if bot_idx == -1:
                return False  # Бот не найден

            if bot_idx == new_position:
                return True  # Позиция не изменилась

            # Убеждаемся, что новая позиция в пределах очереди
            if new_position < 0 or new_position >= len(self.queued_bots):
                return False

            # Извлекаем бота из очереди
            bot = self.queued_bots.pop(bot_idx)

            # Вставляем на новую позицию
            self.queued_bots.insert(new_position, bot)

            if self.logger:
                self.logger.info(f"Бот {bot_name} перемещен на позицию {new_position}")

            return True

    async def get_bot_stats(self, bot_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Возвращает статистику выполнения ботов.

        Args:
            bot_name: Имя бота или None для получения статистики всех ботов

        Returns:
            Словарь со статистикой
        """
        if bot_name:
            # Возвращаем статистику конкретного бота
            return self.bot_stats.get(bot_name, {"runs": 0, "total_time": 0, "last_run": None})
        else:
            # Возвращаем статистику всех ботов
            return self.bot_stats.copy()

    async def clear_bot_stats(self, bot_name: Optional[str] = None) -> bool:
        """
        Очищает статистику выполнения ботов.

        Args:
            bot_name: Имя бота или None для очистки статистики всех ботов

        Returns:
            True если операция успешна
        """
        if bot_name:
            # Очищаем статистику конкретного бота
            if bot_name in self.bot_stats:
                del self.bot_stats[bot_name]
        else:
            # Очищаем статистику всех ботов
            self.bot_stats.clear()

        return True