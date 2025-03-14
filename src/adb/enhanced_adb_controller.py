# src/adb/enhanced_adb_controller.py
import os
import logging
import subprocess
import asyncio
import time
from typing import List, Dict, Optional, Tuple, Union, Set
from concurrent.futures import ThreadPoolExecutor
import io
from PIL import Image

from src.adb.adb_controller import ADBController
from src.utils.exceptions import ADBConnectionError, ADBCommandError, EmulatorError


class EnhancedADBController(ADBController):
    """
    Расширенный контроллер ADB с дополнительными возможностями для управления эмуляторами.
    Реализует асинхронное управление несколькими эмуляторами, обнаружение вылетов игр
    и оптимизированную работу с изображениями в памяти.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5037,
                 logger: Optional[logging.Logger] = None,
                 max_workers: int = 10):
        """
        Инициализирует расширенный контроллер ADB.

        Args:
            host: Адрес ADB-сервера.
            port: Порт ADB-сервера.
            logger: Объект логирования.
            max_workers: Максимальное количество потоков.
        """
        super().__init__(host, port, logger, max_workers)

        # Дополнительные атрибуты для расширенной функциональности
        self._running_packages = {}  # {device_id: {package_name: timestamp}}
        self._device_status = {}  # {device_id: "ready"|"busy"|"offline"|"unauthorized"}
        self._device_game_map = {}  # {device_id: {"game": game_name, "package": package_name}}
        self._running_bots = {}  # {device_id: bot_name}

        # Расширенное кэширование для улучшения производительности
        self._device_info_cache = {}  # {device_id: {key: value}} - кэш информации об устройствах
        self._last_activity_check = {}  # {device_id: timestamp} - последняя проверка активности

        # Настройки для оптимизации взаимодействия
        self.activity_check_interval = 5  # Интервал проверки активности в секундах
        self.reconnect_attempts = 3  # Количество попыток переподключения
        self.reconnect_delay = 1  # Задержка между попытками в секундах

    async def initialize_async(self):
        """
        Асинхронная инициализация контроллера.
        Проверяет доступность сервера ADB и подключенные устройства.

        Returns:
            bool: True, если инициализация прошла успешно.
        """
        try:
            # Проверка статуса ADB-сервера
            devices = await self.get_device_list_async()
            self._log_info(f"ADB-сервер доступен. Подключено устройств: {len(devices)}")

            # Обновляем статус всех устройств
            for device_id in devices:
                await self.update_device_status_async(device_id)

            return True
        except Exception as e:
            self._log_error(f"Ошибка инициализации ADB-контроллера: {e}")
            return False

    async def update_device_status_async(self, device_id: str) -> str:
        """
        Асинхронно обновляет и возвращает статус устройства.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            str: Статус устройства ("ready", "busy", "offline", "unauthorized").
        """
        try:
            # Проверяем доступность устройства
            is_available = await self.check_device_status_async(device_id)

            if not is_available:
                self._device_status[device_id] = "offline"
                return "offline"

            # Проверяем авторизацию
            try:
                await self.send_command_async(device_id, "shell echo 'auth_check'")
                if device_id in self._running_bots:
                    self._device_status[device_id] = "busy"
                    return "busy"
                else:
                    self._device_status[device_id] = "ready"
                    return "ready"
            except ADBCommandError:
                self._device_status[device_id] = "unauthorized"
                return "unauthorized"

        except Exception as e:
            self._log_error(f"Ошибка при обновлении статуса устройства {device_id}: {e}")
            self._device_status[device_id] = "offline"
            return "offline"

    async def get_all_devices_status_async(self) -> Dict[str, str]:
        """
        Асинхронно получает статус всех подключенных устройств.

        Returns:
            Dict[str, str]: Словарь {device_id: status}
        """
        devices = await self.get_device_list_async()
        status_dict = {}

        # Используем gather для параллельной проверки всех устройств
        status_tasks = [self.update_device_status_async(device_id) for device_id in devices]
        statuses = await asyncio.gather(*status_tasks)

        # Формируем словарь результатов
        for device_id, status in zip(devices, statuses):
            status_dict[device_id] = status

        return status_dict

    async def is_app_running_async(self, device_id: str, package_name: str) -> bool:
        """
        Асинхронно проверяет, запущено ли приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            bool: True, если приложение запущено.
        """
        # Проверяем cached данные, если проверка была недавно
        current_time = time.time()
        device_key = f"{device_id}_{package_name}"

        if (device_key in self._last_activity_check and
                current_time - self._last_activity_check[device_key] < self.activity_check_interval):
            # Используем кэшированный результат
            return device_key in self._running_packages

        try:
            # Проверяем активность приложения через dumpsys
            cmd = f"dumpsys activity activities | grep -E 'mResumedActivity|mFocusedActivity' | grep {package_name}"
            result = await self.send_command_async(device_id, cmd)

            is_running = package_name in result

            # Обновляем кэш
            self._last_activity_check[device_key] = current_time
            if is_running:
                if device_id not in self._running_packages:
                    self._running_packages[device_id] = {}
                self._running_packages[device_id][package_name] = current_time
            elif device_id in self._running_packages and package_name in self._running_packages[device_id]:
                del self._running_packages[device_id][package_name]

            return is_running

        except Exception as e:
            self._log_warning(f"Ошибка при проверке активности {package_name} на устройстве {device_id}: {e}")
            return False

    async def detect_app_crashes_async(self, device_id: str, package_name: str) -> Tuple[bool, str]:
        """
        Асинхронно обнаруживает вылеты приложения.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            Tuple[bool, str]: (Произошел ли вылет, Информация о вылете)
        """
        try:
            # Проверяем, запущено ли приложение
            is_running = await self.is_app_running_async(device_id, package_name)

            if not is_running:
                # Проверяем логи на наличие ошибок для этого пакета
                log_cmd = f"logcat -d -t 100 | grep -E 'AndroidRuntime.*{package_name}|FATAL.*{package_name}'"
                crash_log = await self.send_command_async(device_id, log_cmd)

                if crash_log and "FATAL EXCEPTION" in crash_log:
                    self._log_warning(f"Обнаружен вылет приложения {package_name} на устройстве {device_id}")
                    return True, crash_log

                # Приложение не запущено, но нет логов о вылете - возможно оно не было запущено или было закрыто
                return False, "App not running but no crash detected"

            # Приложение запущено, всё в порядке
            return False, "App is running"

        except Exception as e:
            self._log_warning(f"Ошибка при проверке вылетов {package_name} на устройстве {device_id}: {e}")
            return False, f"Error checking crashes: {e}"

    async def get_device_info_async(self, device_id: str, force_refresh: bool = False) -> Dict[str, str]:
        """
        Асинхронно получает полную информацию об устройстве.

        Args:
            device_id: Идентификатор устройства.
            force_refresh: Принудительно обновить кэш.

        Returns:
            Dict[str, str]: Словарь с информацией об устройстве.
        """
        # Проверяем кэш, если не требуется принудительное обновление
        if not force_refresh and device_id in self._device_info_cache:
            return self._device_info_cache[device_id]

        try:
            device_info = {}

            # Получаем информацию о модели устройства
            try:
                model = await self.send_command_async(device_id, "getprop ro.product.model")
                device_info["model"] = model.strip()
            except Exception:
                device_info["model"] = "Unknown"

            # Получаем версию Android
            try:
                android_version = await self.send_command_async(device_id, "getprop ro.build.version.release")
                device_info["android_version"] = android_version.strip()
            except Exception:
                device_info["android_version"] = "Unknown"

            # Получаем разрешение экрана
            try:
                wm_size = await self.send_command_async(device_id, "wm size")
                if "Physical size:" in wm_size:
                    size_part = wm_size.split("Physical size:")[1].strip()
                    device_info["screen_resolution"] = size_part
                else:
                    device_info["screen_resolution"] = "Unknown"
            except Exception:
                device_info["screen_resolution"] = "Unknown"

            # Статус устройства
            device_info["status"] = await self.update_device_status_async(device_id)

            # Сохраняем в кэш
            self._device_info_cache[device_id] = device_info

            return device_info

        except Exception as e:
            self._log_error(f"Ошибка при получении информации об устройстве {device_id}: {e}")
            return {"error": str(e)}

    async def install_app_async(self, device_id: str, apk_path: str) -> bool:
        """
        Асинхронно устанавливает приложение на устройство.

        Args:
            device_id: Идентификатор устройства.
            apk_path: Путь к APK-файлу.

        Returns:
            bool: True, если установка успешна.
        """
        try:
            if not os.path.exists(apk_path):
                self._log_error(f"APK файл не найден: {apk_path}")
                return False

            # Устанавливаем приложение через ADB
            loop = asyncio.get_event_loop()
            install_command = f"adb -s {device_id} install -r {apk_path}"

            process = await asyncio.create_subprocess_shell(
                install_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode() + stderr.decode()

            if "Success" in output:
                self._log_info(f"APK успешно установлен на устройство {device_id}")
                return True
            else:
                self._log_error(f"Ошибка установки APK на устройство {device_id}: {output}")
                return False

        except Exception as e:
            self._log_error(f"Ошибка при установке приложения на устройство {device_id}: {e}")
            return False

    async def get_installed_packages_async(self, device_id: str) -> List[str]:
        """
        Асинхронно получает список установленных пакетов на устройстве.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            List[str]: Список имен пакетов.
        """
        try:
            # Получаем список пакетов через команду pm list packages
            cmd = "pm list packages"
            output = await self.send_command_async(device_id, cmd)

            packages = []
            for line in output.splitlines():
                if line.startswith("package:"):
                    package_name = line[8:].strip()
                    packages.append(package_name)

            return packages

        except Exception as e:
            self._log_error(f"Ошибка при получении списка пакетов на устройстве {device_id}: {e}")
            return []

    async def clear_app_data_async(self, device_id: str, package_name: str) -> bool:
        """
        Асинхронно очищает данные приложения.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            bool: True, если очистка успешна.
        """
        try:
            # Очищаем данные приложения через pm clear
            cmd = f"pm clear {package_name}"
            output = await self.send_command_async(device_id, cmd)

            success = "Success" in output
            if success:
                self._log_info(f"Данные приложения {package_name} успешно очищены на устройстве {device_id}")
            else:
                self._log_warning(f"Не удалось очистить данные приложения {package_name} на устройстве {device_id}")

            return success

        except Exception as e:
            self._log_error(f"Ошибка при очистке данных приложения {package_name} на устройстве {device_id}: {e}")
            return False

    async def get_running_activities_async(self, device_id: str) -> Dict[str, str]:
        """
        Асинхронно получает список запущенных активностей на устройстве.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            Dict[str, str]: Словарь {package_name: activity_name}
        """
        try:
            # Получаем запущенные активности через dumpsys
            cmd = "dumpsys activity activities | grep -E 'mResumedActivity|mFocusedActivity'"
            output = await self.send_command_async(device_id, cmd)

            activities = {}
            for line in output.splitlines():
                if "}" in line and "/" in line:
                    # Парсим строку вида: "mResumedActivity: ActivityRecord{...} com.package.name/.ActivityName ...}"
                    parts = line.split()
                    for part in parts:
                        if "/" in part:
                            package_activity = part.strip()
                            if " " in package_activity:
                                package_activity = package_activity.split()[0]

                            if "/" in package_activity:
                                package, activity = package_activity.split("/", 1)
                                activities[package] = activity

            return activities

        except Exception as e:
            self._log_error(f"Ошибка при получении запущенных активностей на устройстве {device_id}: {e}")
            return {}

    async def execute_tap_sequence_async(self, device_id: str, tap_sequence: List[Tuple[int, int, float]]) -> bool:
        """
        Асинхронно выполняет последовательность кликов с задержками.

        Args:
            device_id: Идентификатор устройства.
            tap_sequence: Список кортежей (x, y, delay_after) - координаты и задержка после клика.

        Returns:
            bool: True, если последовательность выполнена успешно.
        """
        try:
            for i, (x, y, delay) in enumerate(tap_sequence):
                self._log_debug(f"Выполнение клика {i + 1}/{len(tap_sequence)} по координатам ({x}, {y})")

                # Выполняем клик
                await self.tap_async(device_id, x, y)

                # Задержка после клика
                if delay > 0:
                    await asyncio.sleep(delay)

            return True

        except Exception as e:
            self._log_error(f"Ошибка при выполнении последовательности кликов на устройстве {device_id}: {e}")
            return False

    async def execute_swipe_sequence_async(self, device_id: str,
                                           swipe_sequence: List[Tuple[int, int, int, int, int, float]]) -> bool:
        """
        Асинхронно выполняет последовательность свайпов с задержками.

        Args:
            device_id: Идентификатор устройства.
            swipe_sequence: Список кортежей (x1, y1, x2, y2, duration, delay_after).

        Returns:
            bool: True, если последовательность выполнена успешно.
        """
        try:
            for i, (x1, y1, x2, y2, duration, delay) in enumerate(swipe_sequence):
                self._log_debug(f"Выполнение свайпа {i + 1}/{len(swipe_sequence)} от ({x1}, {y1}) к ({x2}, {y2})")

                # Выполняем свайп
                await self.swipe_async(device_id, x1, y1, x2, y2, duration)

                # Задержка после свайпа
                if delay > 0:
                    await asyncio.sleep(delay)

            return True

        except Exception as e:
            self._log_error(f"Ошибка при выполнении последовательности свайпов на устройстве {device_id}: {e}")
            return False

    async def get_screenshot_to_memory_async(self, device_id: str, use_cache: bool = False,
                                             cache_timeout: int = 5) -> Optional[bytes]:
        """
        Асинхронно получает скриншот устройства в память без сохранения на диск.

        Args:
            device_id: Идентификатор устройства.
            use_cache: Использовать кэш, если доступен.
            cache_timeout: Срок действия кэша в секундах.

        Returns:
            Optional[bytes]: Данные скриншота в формате bytes или None при ошибке.
        """
        try:
            # Проверяем кэш, если разрешено
            current_time = time.time()
            if use_cache and device_id in self._screenshot_cache:
                cache_data = self._screenshot_cache[device_id]
                if current_time - cache_data['timestamp'] < cache_timeout:
                    self._log_debug(f"Использован кэшированный скриншот для {device_id}")
                    return cache_data['data']

            # Получаем скриншот в память
            loop = asyncio.get_event_loop()
            screenshot_data = await loop.run_in_executor(
                self.executor,
                lambda: self.get_device(device_id).screencap()
            )

            # Сохраняем в кэш, если разрешено
            if use_cache:
                self._screenshot_cache[device_id] = {
                    'data': screenshot_data,
                    'timestamp': current_time
                }

            return screenshot_data

        except Exception as e:
            self._log_error(f"Ошибка при получении скриншота в память для устройства {device_id}: {e}")
            return None

    async def get_screenshot_as_pil_async(self, device_id: str, use_cache: bool = False,
                                          cache_timeout: int = 5) -> Optional[Image.Image]:
        """
        Асинхронно получает скриншот как объект PIL.Image.

        Args:
            device_id: Идентификатор устройства.
            use_cache: Использовать кэш, если доступен.
            cache_timeout: Срок действия кэша в секундах.

        Returns:
            Optional[Image.Image]: Объект PIL.Image или None при ошибке.
        """
        try:
            # Получаем скриншот в память
            screenshot_data = await self.get_screenshot_to_memory_async(
                device_id, use_cache, cache_timeout
            )

            if screenshot_data:
                # Конвертируем в PIL.Image
                image = Image.open(io.BytesIO(screenshot_data))
                return image

            return None

        except Exception as e:
            self._log_error(f"Ошибка при получении скриншота как PIL.Image для устройства {device_id}: {e}")
            return None

    async def start_ldplayer_multi_async(self, emu_ids: List[str]) -> List[str]:
        """
        Асинхронно запускает несколько эмуляторов LDPlayer параллельно.

        Args:
            emu_ids: Список идентификаторов эмуляторов.

        Returns:
            List[str]: Список успешно запущенных эмуляторов.
        """
        try:
            # Создаем список задач для запуска эмуляторов
            tasks = []
            for emu_id in emu_ids:
                tasks.append(self.start_ldplayer_async(emu_id))

            # Запускаем все задачи параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Формируем список успешно запущенных эмуляторов
            successful_emu_ids = []
            for emu_id, result in zip(emu_ids, results):
                if isinstance(result, Exception):
                    self._log_error(f"Ошибка запуска эмулятора {emu_id}: {result}")
                elif result:
                    successful_emu_ids.append(emu_id)

            return successful_emu_ids

        except Exception as e:
            self._log_error(f"Ошибка при запуске нескольких эмуляторов: {e}")
            return []

    async def stop_ldplayer_multi_async(self, emu_ids: List[str]) -> List[str]:
        """
        Асинхронно останавливает несколько эмуляторов LDPlayer параллельно.

        Args:
            emu_ids: Список идентификаторов эмуляторов.

        Returns:
            List[str]: Список успешно остановленных эмуляторов.
        """
        try:
            # Создаем список задач для остановки эмуляторов
            tasks = []
            for emu_id in emu_ids:
                tasks.append(self.stop_ldplayer_async(emu_id))

            # Запускаем все задачи параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Формируем список успешно остановленных эмуляторов
            successful_emu_ids = []
            for emu_id, result in zip(emu_ids, results):
                if isinstance(result, Exception):
                    self._log_error(f"Ошибка остановки эмулятора {emu_id}: {result}")
                elif result:
                    successful_emu_ids.append(emu_id)

            return successful_emu_ids

        except Exception as e:
            self._log_error(f"Ошибка при остановке нескольких эмуляторов: {e}")
            return []

    async def wait_for_package_activity_async(self, device_id: str, package_name: str,
                                              timeout: int = 30) -> bool:
        """
        Асинхронно ожидает запуска приложения на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.
            timeout: Максимальное время ожидания в секундах.

        Returns:
            bool: True, если приложение запущено в течение таймаута.
        """
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Проверяем, запущено ли приложение
                is_running = await self.is_app_running_async(device_id, package_name)

                if is_running:
                    self._log_info(f"Приложение {package_name} запущено на устройстве {device_id}")
                    return True

                # Ждем 1 секунду перед следующей проверкой
                await asyncio.sleep(1)

            self._log_warning(f"Тайм-аут ожидания запуска приложения {package_name} на устройстве {device_id}")
            return False

        except Exception as e:
            self._log_error(f"Ошибка при ожидании запуска приложения {package_name} на устройстве {device_id}: {e}")
            return False

    async def parse_emulators_string(self, emulators_str: str) -> List[str]:
        """
        Асинхронно парсит строку с указанием эмуляторов и возвращает список их ID.

        Args:
            emulators_str: Строка вида "0:5,7,9:10"

        Returns:
            List[str]: Список ID эмуляторов
        """
        try:
            emu_list = []

            if not emulators_str.strip():
                return []

            # Обрабатываем части, разделенные запятыми
            parts = emulators_str.strip().split(",")
            for part in parts:
                part = part.strip()

                if ":" in part:
                    # Обрабатываем диапазон (например, "0:5")
                    start, end = part.split(":")
                    try:
                        start_i = int(start)
                        end_i = int(end)
                        if start_i <= end_i:
                            for e in range(start_i, end_i + 1):
                                emu_list.append(str(e))
                    except ValueError:
                        self._log_warning(f"Неверный формат диапазона: {part}")
                else:
                    # Обрабатываем одиночный ID
                    try:
                        emu_id = int(part)
                        emu_list.append(str(emu_id))
                    except ValueError:
                        self._log_warning(f"Неверный формат ID эмулятора: {part}")

            return emu_list

        except Exception as e:
            self._log_error(f"Ошибка при парсинге строки эмуляторов '{emulators_str}': {e}")
            return []

    async def register_bot_on_device(self, device_id: str, bot_name: str,
                                     game_name: str, package_name: str) -> bool:
        """
        Асинхронно регистрирует бота на устройстве.

        Args:
            device_id: Идентификатор устройства.
            bot_name: Имя бота.
            game_name: Название игры.
            package_name: Имя пакета игры.

        Returns:
            bool: True, если регистрация успешна.
        """
        try:
            self._running_bots[device_id] = bot_name
            self._device_game_map[device_id] = {
                "game": game_name,
                "package": package_name
            }
            self._device_status[device_id] = "busy"

            self._log_info(f"Бот '{bot_name}' для игры '{game_name}' запущен на устройстве {device_id}")
            return True

        except Exception as e:
            self._log_error(f"Ошибка при регистрации бота '{bot_name}' на устройстве {device_id}: {e}")
            return False

    async def unregister_bot_from_device(self, device_id: str) -> bool:
        """
        Асинхронно отменяет регистрацию бота на устройстве.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            bool: True, если отмена регистрации успешна.
        """
        try:
            if device_id in self._running_bots:
                bot_name = self._running_bots[device_id]
                del self._running_bots[device_id]

                if device_id in self._device_game_map:
                    del self._device_game_map[device_id]

                self._device_status[device_id] = "ready"

                self._log_info(f"Бот '{bot_name}' остановлен на устройстве {device_id}")
                return True

            return False

        except Exception as e:
            self._log_error(f"Ошибка при отмене регистрации бота на устройстве {device_id}: {e}")
            return False

    async def get_free_devices_async(self, min_count: int = 1,
                                     exclude_devices: Optional[List[str]] = None) -> List[str]:
        """
        Асинхронно получает список свободных устройств.

        Args:
            min_count: Минимальное количество устройств.
            exclude_devices: Список устройств для исключения.

        Returns:
            List[str]: Список ID свободных устройств.
        """
        try:
            # Обновляем статусы всех устройств
            statuses = await self.get_all_devices_status_async()

            # Исключаем указанные устройства
            excluded = set(exclude_devices or [])

            # Формируем список свободных устройств
            free_devices = []
            for device_id, status in statuses.items():
                if device_id not in excluded and status == "ready":
                    free_devices.append(device_id)

                    # Если нашли достаточное количество устройств, выходим
                    if len(free_devices) >= min_count:
                        break

            return free_devices

        except Exception as e:
            self._log_error(f"Ошибка при получении списка свободных устройств: {e}")
            return []