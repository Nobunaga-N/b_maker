# src/adb/bot_adb_controller.py - новый класс, объединяющий функциональность

import asyncio
from typing import List, Dict, Optional, Tuple, Set
from src.adb.enhanced_adb_controller import EnhancedADBController
from src.utils.logger import setup_logger


class BotADBController(EnhancedADBController):
    """
    Специализированный контроллер ADB для работы с ботами.
    Объединяет возможности EnhancedADBController с функциями для управления очередью ботов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_bots = {}  # {device_id: {"bot_name": name, "status": status, "start_time": time}}
        self.queue_lock = asyncio.Lock()  # Для синхронизации доступа к очереди ботов

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
                await self.register_bot_on_device(device_id, bot_name, "", "")

            return allocated_devices