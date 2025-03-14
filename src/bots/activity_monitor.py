# src/bots/activity_monitor.py - новый файл

import asyncio
import logging
from typing import Dict, Any, Optional, Callable

from src.adb.bot_adb_controller import BotADBController


class ActivityMonitor:
    """
    Монитор активности игры. Отслеживает состояние игры и реагирует на вылеты.
    """

    def __init__(self, adb_controller: BotADBController, logger: Optional[logging.Logger] = None):
        self.adb_controller = adb_controller
        self.logger = logger
        self.monitored_activities = {}  # {device_id: {package_name, callback, ...}}
        self.running = False
        self.monitoring_task = None

    async def start_monitoring(self) -> bool:
        """
        Запускает мониторинг активности игр.

        Returns:
            True, если мониторинг успешно запущен
        """
        if self.running:
            return False

        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        if self.logger:
            self.logger.info("Мониторинг активности игр запущен")
        return True

    async def stop_monitoring(self) -> bool:
        """
        Останавливает мониторинг активности игр.

        Returns:
            True, если мониторинг успешно остановлен
        """
        if not self.running:
            return False

        self.running = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        if self.logger:
            self.logger.info("Мониторинг активности игр остановлен")
        return True

    async def register_activity(self, device_id: str, package_name: str,
                                crash_callback: Callable[[str, str, bool], None],
                                config: Dict[str, Any]) -> bool:
        """
        Регистрирует активность для мониторинга.

        Args:
            device_id: ID устройства
            package_name: Имя пакета приложения
            crash_callback: Функция обратного вызова при обнаружении вылета
            config: Конфигурация мониторинга

        Returns:
            True, если активность успешно зарегистрирована
        """
        self.monitored_activities[device_id] = {
            "package_name": package_name,
            "callback": crash_callback,
            "config": config,
            "last_check": asyncio.get_event_loop().time()
        }

        if self.logger:
            self.logger.info(f"Активность {package_name} на устройстве {device_id} зарегистрирована для мониторинга")
        return True

    async def unregister_activity(self, device_id: str) -> bool:
        """
        Отменяет регистрацию активности.

        Args:
            device_id: ID устройства

        Returns:
            True, если регистрация успешно отменена
        """
        if device_id in self.monitored_activities:
            del self.monitored_activities[device_id]

            if self.logger:
                self.logger.info(f"Активность на устройстве {device_id} снята с мониторинга")
            return True
        return False

    async def _monitoring_loop(self):
        """
        Основной цикл мониторинга активности.
        """
        while self.running:
            try:
                current_time = asyncio.get_event_loop().time()

                for device_id, activity_info in list(self.monitored_activities.items()):
                    # Проверяем активность с заданным интервалом
                    check_interval = activity_info["config"].get("check_interval", 5.0)

                    if current_time - activity_info["last_check"] >= check_interval:
                        # Проверяем активность приложения
                        package_name = activity_info["package_name"]
                        is_running = await self.adb_controller.is_app_running_async(device_id, package_name)

                        # Обновляем время последней проверки
                        activity_info["last_check"] = current_time

                        if not is_running:
                            # Обнаружен вылет игры
                            if self.logger:
                                self.logger.warning(f"Обнаружен вылет {package_name} на устройстве {device_id}")

                            # Проверяем лог на наличие ошибок
                            crashed, crash_info = await self.adb_controller.detect_app_crashes_async(
                                device_id, package_name
                            )

                            # Вызываем колбэк с информацией о вылете
                            await activity_info["callback"](device_id, package_name, crashed)

                # Пауза между циклами проверки
                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                # Мониторинг отменен
                break
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(5.0)  # Пауза перед повторной попыткой