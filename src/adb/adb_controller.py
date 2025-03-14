# src/adb/adb_controller.py
import os
import logging
import subprocess
import tempfile
import time
import asyncio
import threading
from io import BytesIO
from typing import Optional, List, Dict, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from ppadb.client import Client as AdbClient
from ppadb.device import Device

from src.utils.exceptions import ADBConnectionError, ADBCommandError, EmulatorError


class ADBController:
    """
    Расширенный класс для работы с ADB, управления эмуляторами LDP Player 9.
    Использует библиотеку ppadb для взаимодействия с ADB.
    Реализует методы для получения списка эмуляторов, запуска/остановки,
    выполнения действий, получения скриншотов и управления приложениями.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5037,
                 logger: Optional[logging.Logger] = None,
                 max_workers: int = 10) -> None:
        """
        Инициализирует ADB клиент.

        Args:
            host: Адрес ADB-сервера.
            port: Порт ADB-сервера.
            logger: Объект логирования.
            max_workers: Максимальное количество потоков для параллельного выполнения.
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._devices_cache = {}  # Кэш устройств для быстрого доступа
        self._cache_lock = threading.Lock()  # Блокировка для синхронизации доступа к кэшу
        self._devices_status = {}  # Статус устройств (активно, занято и т.д.)
        self._screenshot_cache = {}  # Кэш скриншотов для повторного использования

        try:
            self.client = AdbClient(host=host, port=port)
            if self.logger:
                self.logger.info("ADB клиент успешно инициализирован")
        except Exception as e:
            error_msg = f"Ошибка инициализации ADB клиента: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBConnectionError(error_msg)

    def get_device(self, device_id: str) -> Device:
        """
        Возвращает устройство по его ID.
        Использует кэш для ускорения работы.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            Устройство ADB.

        Raises:
            ADBConnectionError: Если устройство не найдено.
        """
        try:
            # Проверяем кэш
            with self._cache_lock:
                if device_id in self._devices_cache:
                    # Проверяем, не протухло ли соединение
                    try:
                        # Быстрая проверка соединения
                        device = self._devices_cache[device_id]
                        device.shell('echo 1')
                        return device
                    except:
                        # Соединение недействительно, удаляем из кэша
                        del self._devices_cache[device_id]

            # Получаем устройство заново
            device = self.client.device(device_id)
            if not device:
                raise ADBConnectionError(f"Устройство с ID {device_id} не найдено")

            # Сохраняем в кэш
            with self._cache_lock:
                self._devices_cache[device_id] = device

            return device

        except ADBConnectionError:
            # Пробрасываем ошибку подключения
            raise
        except Exception as e:
            error_msg = f"Ошибка получения устройства {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBConnectionError(error_msg)

    def send_command(self, device_id: str, command: str) -> str:
        """
        Отправляет ADB-команду на указанное устройство.

        Args:
            device_id: Идентификатор устройства.
            command: Команда для отправки.

        Returns:
            Результат выполнения команды.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            device = self.get_device(device_id)
            output = device.shell(command)
            if self.logger:
                self.logger.debug(f"Команда '{command}' отправлена на устройство {device_id}")
            return output
        except ADBConnectionError as e:
            # Пробрасываем ошибку подключения
            raise
        except Exception as e:
            error_msg = f"Ошибка отправки команды '{command}' на устройство {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def send_command_async(self, device_id: str, command: str) -> str:
        """
        Асинхронно отправляет ADB-команду на указанное устройство.

        Args:
            device_id: Идентификатор устройства.
            command: Команда для отправки.

        Returns:
            Результат выполнения команды.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.send_command, device_id, command
        )

    def get_device_list(self) -> List[str]:
        """
        Возвращает список идентификаторов подключенных устройств.

        Returns:
            Список ID устройств.
        """
        try:
            devices = self.client.devices()
            if self.logger:
                self.logger.debug(f"Получен список устройств: {len(devices)} устройств")
            return [device.serial for device in devices]
        except Exception as e:
            error_msg = f"Ошибка получения списка устройств: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return []

    async def get_device_list_async(self) -> List[str]:
        """
        Асинхронно возвращает список идентификаторов подключенных устройств.

        Returns:
            Список ID устройств.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_device_list
        )

    def check_device_status(self, device_id: str) -> bool:
        """
        Проверяет доступность устройства.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            True, если устройство доступно, иначе False.
        """
        try:
            device = self.get_device(device_id)
            # Простая проверка - запрос состояния батареи
            device.shell('dumpsys battery')
            if self.logger:
                self.logger.debug(f"Устройство {device_id} доступно")
            return True
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Устройство {device_id} недоступно: {e}")
            return False

    async def check_device_status_async(self, device_id: str) -> bool:
        """
        Асинхронно проверяет доступность устройства.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            True, если устройство доступно, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.check_device_status, device_id
        )

    def get_screenshot(self, device_id: str, use_cache: bool = False,
                       cache_timeout: int = 5) -> Image.Image:
        """
        Получает скриншот с устройства и возвращает его как объект PIL.Image.
        Оптимизирован для работы без сохранения на диск.

        Args:
            device_id: Идентификатор устройства.
            use_cache: Использовать кэш для ускорения.
            cache_timeout: Время жизни кэша в секундах.

        Returns:
            Объект PIL.Image со скриншотом экрана.

        Raises:
            ADBCommandError: Если произошла ошибка при получении скриншота.
        """
        try:
            # Проверяем кэш, если разрешено
            if use_cache and device_id in self._screenshot_cache:
                cache_data = self._screenshot_cache[device_id]
                if time.time() - cache_data['timestamp'] < cache_timeout:
                    if self.logger:
                        self.logger.debug(f"Использован кэшированный скриншот для {device_id}")
                    return cache_data['image']

            # Получаем устройство
            device = self.get_device(device_id)

            # Получаем скриншот напрямую в память
            screenshot = device.screencap()

            # Конвертируем в PIL.Image
            image = Image.open(BytesIO(screenshot))

            # Сохраняем в кэш, если разрешено
            if use_cache:
                self._screenshot_cache[device_id] = {
                    'image': image,
                    'timestamp': time.time()
                }

            if self.logger:
                self.logger.debug(f"Получен скриншот с устройства {device_id}")

            return image

        except ADBConnectionError:
            # Пробрасываем ошибку подключения
            raise
        except Exception as e:
            error_msg = f"Ошибка получения скриншота с устройства {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def get_screenshot_async(self, device_id: str, use_cache: bool = False,
                                   cache_timeout: int = 5) -> Image.Image:
        """
        Асинхронно получает скриншот с устройства.

        Args:
            device_id: Идентификатор устройства.
            use_cache: Использовать кэш для ускорения.
            cache_timeout: Время жизни кэша в секундах.

        Returns:
            Объект PIL.Image со скриншотом экрана.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_screenshot, device_id, use_cache, cache_timeout
        )

    def tap(self, device_id: str, x: int, y: int) -> None:
        """
        Эмулирует нажатие на экран по указанным координатам.

        Args:
            device_id: Идентификатор устройства.
            x: Координата X.
            y: Координата Y.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            command = f'input tap {x} {y}'
            self.send_command(device_id, command)
            if self.logger:
                self.logger.debug(f"Выполнен клик по координатам ({x}, {y}) на устройстве {device_id}")
        except Exception as e:
            error_msg = f"Ошибка клика по координатам ({x}, {y}) на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def tap_async(self, device_id: str, x: int, y: int) -> None:
        """
        Асинхронно эмулирует нажатие на экран по указанным координатам.

        Args:
            device_id: Идентификатор устройства.
            x: Координата X.
            y: Координата Y.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.tap, device_id, x, y
        )

    def swipe(self, device_id: str, x1: int, y1: int, x2: int, y2: int,
              duration: int = 300) -> None:
        """
        Эмулирует свайп от одной точки экрана к другой.

        Args:
            device_id: Идентификатор устройства.
            x1: Начальная координата X.
            y1: Начальная координата Y.
            x2: Конечная координата X.
            y2: Конечная координата Y.
            duration: Длительность свайпа в миллисекундах.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            command = f'input swipe {x1} {y1} {x2} {y2} {duration}'
            self.send_command(device_id, command)
            if self.logger:
                self.logger.debug(
                    f"Выполнен свайп от ({x1}, {y1}) к ({x2}, {y2}) "
                    f"на устройстве {device_id}"
                )
        except Exception as e:
            error_msg = f"Ошибка свайпа на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def swipe_async(self, device_id: str, x1: int, y1: int, x2: int, y2: int,
                          duration: int = 300) -> None:
        """
        Асинхронно эмулирует свайп от одной точки экрана к другой.

        Args:
            device_id: Идентификатор устройства.
            x1: Начальная координата X.
            y1: Начальная координата Y.
            x2: Конечная координата X.
            y2: Конечная координата Y.
            duration: Длительность свайпа в миллисекундах.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.swipe, device_id, x1, y1, x2, y2, duration
        )

    def launch_app(self, device_id: str, package_name: str, activity_name: str = None) -> bool:
        """
        Запускает приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.
            activity_name: Имя активности (опционально).

        Returns:
            True, если приложение успешно запущено, иначе False.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            if activity_name:
                command = f'am start -n {package_name}/{activity_name}'
            else:
                command = f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1'

            output = self.send_command(device_id, command)

            # Проверяем успешность запуска по выводу команды
            success = "Starting" in output or "Success" in output

            if self.logger:
                self.logger.debug(
                    f"Запуск приложения {package_name} на устройстве {device_id}: {'успешно' if success else 'неудачно'}")

            # Даем приложению время на запуск
            time.sleep(1)

            return success
        except Exception as e:
            error_msg = f"Ошибка запуска приложения {package_name} на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def launch_app_async(self, device_id: str, package_name: str,
                               activity_name: str = None) -> bool:
        """
        Асинхронно запускает приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.
            activity_name: Имя активности (опционально).

        Returns:
            True, если приложение успешно запущено, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.launch_app, device_id, package_name, activity_name
        )

    def stop_app(self, device_id: str, package_name: str) -> bool:
        """
        Останавливает приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            True, если приложение успешно остановлено, иначе False.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            command = f'am force-stop {package_name}'
            output = self.send_command(device_id, command)

            # В случае успеха команда не выводит сообщений
            success = output.strip() == ""

            if self.logger:
                self.logger.debug(
                    f"Остановка приложения {package_name} на устройстве {device_id}: {'успешно' if success else 'неудачно'}")

            return success
        except Exception as e:
            error_msg = f"Ошибка остановки приложения {package_name} на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def stop_app_async(self, device_id: str, package_name: str) -> bool:
        """
        Асинхронно останавливает приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            True, если приложение успешно остановлено, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.stop_app, device_id, package_name
        )

    def check_app_running(self, device_id: str, package_name: str) -> bool:
        """
        Проверяет, запущено ли приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            True, если приложение запущено, иначе False.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            # Получаем список запущенных процессов
            command = 'ps'
            output = self.send_command(device_id, command)

            # Проверяем наличие пакета в списке
            running = package_name in output

            if self.logger:
                self.logger.debug(
                    f"Проверка работы приложения {package_name} на устройстве {device_id}: {'запущено' if running else 'не запущено'}")

            return running
        except Exception as e:
            error_msg = f"Ошибка проверки запущенного приложения {package_name} на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def check_app_running_async(self, device_id: str, package_name: str) -> bool:
        """
        Асинхронно проверяет, запущено ли приложение на устройстве.

        Args:
            device_id: Идентификатор устройства.
            package_name: Имя пакета приложения.

        Returns:
            True, если приложение запущено, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.check_app_running, device_id, package_name
        )

    def get_current_activity(self, device_id: str) -> str:
        """
        Получает имя текущей активности (верхней в стеке).

        Args:
            device_id: Идентификатор устройства.

        Returns:
            Строка с именем активности.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            command = 'dumpsys window windows | grep -E "mCurrentFocus|mFocusedApp"'
            output = self.send_command(device_id, command)

            # Парсим вывод команды для получения имени активности
            activity = "unknown"
            for line in output.split('\n'):
                if "mCurrentFocus" in line:
                    # Ищем имя пакета и активности в строке
                    parts = line.split()
                    for part in parts:
                        if '/' in part:
                            activity = part.strip()
                            break

            if self.logger:
                self.logger.debug(f"Текущая активность на устройстве {device_id}: {activity}")

            return activity
        except Exception as e:
            error_msg = f"Ошибка получения текущей активности на устройстве {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise ADBCommandError(error_msg)

    async def get_current_activity_async(self, device_id: str) -> str:
        """
        Асинхронно получает имя текущей активности.

        Args:
            device_id: Идентификатор устройства.

        Returns:
            Строка с именем активности.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_current_activity, device_id
        )

    def restart_emulator(self, device_id: str) -> bool:
        """
        Перезапускает эмулятор.

        Args:
            device_id: Идентификатор устройства (эмулятора).

        Returns:
            True, если перезапуск выполнен успешно, иначе False.

        Raises:
            EmulatorError: Если произошла ошибка при перезапуске эмулятора.
        """
        try:
            # Получаем текущий статус устройства
            if not self.check_device_status(device_id):
                if self.logger:
                    self.logger.warning(f"Устройство {device_id} недоступно для перезапуска")
                return False

            # Отправляем команду перезагрузки
            try:
                self.send_command(device_id, "reboot")
                if self.logger:
                    self.logger.info(f"Отправлена команда перезагрузки для устройства {device_id}")
            except:
                # Если не сработало через ADB, используем внешнюю команду LDPlayer
                # Нужно реализовать в зависимости от типа эмулятора
                # Например, для LDPlayer может быть такая команда:
                # subprocess.run(["ldconsole", "reboot", "--index", device_id], shell=True)
                if self.logger:
                    self.logger.warning(f"Не удалось перезапустить устройство {device_id} через ADB")
                return False

            # Ожидаем отключения устройства
            for _ in range(10):  # Ждем до 10 секунд
                if not self.check_device_status(device_id):
                    break
                time.sleep(1)

            # Ожидаем подключения устройства
            for _ in range(60):  # Ждем до 60 секунд
                if self.check_device_status(device_id):
                    if self.logger:
                        self.logger.info(f"Устройство {device_id} успешно перезапущено")
                    return True
                time.sleep(1)

            if self.logger:
                self.logger.error(f"Тайм-аут ожидания подключения устройства {device_id} после перезапуска")
            return False

        except Exception as e:
            error_msg = f"Ошибка перезапуска устройства {device_id}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise EmulatorError(error_msg)

    async def restart_emulator_async(self, device_id: str) -> bool:
        """
        Асинхронно перезапускает эмулятор.

        Args:
            device_id: Идентификатор устройства (эмулятора).

        Returns:
            True, если перезапуск выполнен успешно, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.restart_emulator, device_id
        )

    def execute_ldplayer_command(self, command: str) -> str:
        """
        Выполняет команду для LDPlayer через ldconsole.

        Args:
            command: Команда для выполнения.

        Returns:
            Вывод команды.

        Raises:
            EmulatorError: Если произошла ошибка при выполнении команды.
        """
        try:
            # Путь к ldconsole.exe в зависимости от системы
            ldconsole_path = "ldconsole"  # по умолчанию в PATH

            # На Windows может потребоваться полный путь
            # ldconsole_path = r"C:\Program Files\LDPlayer\ldconsole.exe"

            # Выполняем команду
            full_command = f"{ldconsole_path} {command}"
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate()

            if process.returncode != 0:
                if self.logger:
                    self.logger.error(f"Ошибка выполнения команды LDPlayer: {error}")
                raise EmulatorError(f"Ошибка выполнения команды LDPlayer: {error}")

            if self.logger:
                self.logger.debug(f"Выполнена команда LDPlayer: {command}")

            return output

        except Exception as e:
            error_msg = f"Ошибка выполнения команды LDPlayer: {e}"
            if self.logger:
                self.logger.error(error_msg)
            raise EmulatorError(error_msg)

    async def execute_ldplayer_command_async(self, command: str) -> str:
        """
        Асинхронно выполняет команду для LDPlayer через ldconsole.

        Args:
            command: Команда для выполнения.

        Returns:
            Вывод команды.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.execute_ldplayer_command, command
        )

    def get_ldplayer_list(self) -> List[str]:
        """
        Получает список запущенных эмуляторов LDPlayer.

        Returns:
            Список идентификаторов эмуляторов.
        """
        try:
            output = self.execute_ldplayer_command("list")

            # Парсим вывод команды
            emulators = []
            for line in output.split('\n'):
                if line.strip() and not line.startswith("Index"):
                    try:
                        # Формат вывода: Index Title
                        parts = line.split(maxsplit=1)
                        if parts and parts[0].isdigit():
                            emulators.append(parts[0])
                    except:
                        continue

            if self.logger:
                self.logger.debug(f"Получен список эмуляторов LDPlayer: {emulators}")

            return emulators

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка получения списка эмуляторов LDPlayer: {e}")
            return []

    async def get_ldplayer_list_async(self) -> List[str]:
        """
        Асинхронно получает список запущенных эмуляторов LDPlayer.

        Returns:
            Список идентификаторов эмуляторов.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_ldplayer_list
        )

    def start_ldplayer(self, emu_id: str) -> bool:
        """
        Запускает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если запуск выполнен успешно, иначе False.
        """
        try:
            # Проверяем, не запущен ли уже эмулятор
            ldplayer_list = self.get_ldplayer_list()
            if emu_id in ldplayer_list:
                if self.logger:
                    self.logger.debug(f"Эмулятор LDPlayer {emu_id} уже запущен")
                return True

            # Запускаем эмулятор
            output = self.execute_ldplayer_command(f"launch --index {emu_id}")

            # Ждем запуска и подключения к ADB
            for _ in range(60):  # Ждем до 60 секунд
                ldplayer_list = self.get_ldplayer_list()
                if emu_id in ldplayer_list:
                    time.sleep(5)  # Даем эмулятору дополнительное время на инициализацию
                    if self.logger:
                        self.logger.info(f"Эмулятор LDPlayer {emu_id} успешно запущен")
                    return True
                time.sleep(1)

            if self.logger:
                self.logger.error(f"Тайм-аут ожидания запуска эмулятора LDPlayer {emu_id}")
            return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка запуска эмулятора LDPlayer {emu_id}: {e}")
            return False

    async def start_ldplayer_async(self, emu_id: str) -> bool:
        """
        Асинхронно запускает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если запуск выполнен успешно, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.start_ldplayer, emu_id
        )

    def stop_ldplayer(self, emu_id: str) -> bool:
        """
        Останавливает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если остановка выполнена успешно, иначе False.
        """
        try:
            # Проверяем, запущен ли эмулятор
            ldplayer_list = self.get_ldplayer_list()
            if emu_id not in ldplayer_list:
                if self.logger:
                    self.logger.debug(f"Эмулятор LDPlayer {emu_id} не запущен")
                return True

            # Останавливаем эмулятор
            output = self.execute_ldplayer_command(f"quit --index {emu_id}")

            # Ждем остановки
            for _ in range(30):  # Ждем до 30 секунд
                ldplayer_list = self.get_ldplayer_list()
                if emu_id not in ldplayer_list:
                    if self.logger:
                        self.logger.info(f"Эмулятор LDPlayer {emu_id} успешно остановлен")
                    return True
                time.sleep(1)

            if self.logger:
                self.logger.error(f"Тайм-аут ожидания остановки эмулятора LDPlayer {emu_id}")
            return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка остановки эмулятора LDPlayer {emu_id}: {e}")
            return False

    async def stop_ldplayer_async(self, emu_id: str) -> bool:
        """
        Асинхронно останавливает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если остановка выполнена успешно, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.stop_ldplayer, emu_id
        )

    def reboot_ldplayer(self, emu_id: str) -> bool:
        """
        Перезапускает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если перезапуск выполнен успешно, иначе False.
        """
        try:
            # Останавливаем эмулятор
            if not self.stop_ldplayer(emu_id):
                if self.logger:
                    self.logger.error(f"Не удалось остановить эмулятор LDPlayer {emu_id} для перезапуска")
                return False

            # Запускаем эмулятор
            if not self.start_ldplayer(emu_id):
                if self.logger:
                    self.logger.error(f"Не удалось запустить эмулятор LDPlayer {emu_id} после остановки")
                return False

            if self.logger:
                self.logger.info(f"Эмулятор LDPlayer {emu_id} успешно перезапущен")
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка перезапуска эмулятора LDPlayer {emu_id}: {e}")
            return False

    async def reboot_ldplayer_async(self, emu_id: str) -> bool:
        """
        Асинхронно перезапускает эмулятор LDPlayer.

        Args:
            emu_id: Идентификатор эмулятора.

        Returns:
            True, если перезапуск выполнен успешно, иначе False.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.reboot_ldplayer, emu_id
        )

    def clear_cache(self, device_id: str = None) -> None:
        """
        Очищает кэш устройств и скриншотов.

        Args:
            device_id: Идентификатор устройства для очистки конкретного кэша
                       (если None, очищает весь кэш).
        """
        with self._cache_lock:
            if device_id:
                # Очищаем кэш для конкретного устройства
                if device_id in self._devices_cache:
                    del self._devices_cache[device_id]
                if device_id in self._screenshot_cache:
                    del self._screenshot_cache[device_id]
                if device_id in self._devices_status:
                    del self._devices_status[device_id]
            else:
                # Очищаем весь кэш
                self._devices_cache.clear()
                self._screenshot_cache.clear()
                self._devices_status.clear()

        if self.logger:
            self.logger.debug(f"Кэш очищен для {'устройства ' + device_id if device_id else 'всех устройств'}")

    def __del__(self):
        """
        Освобождает ресурсы при уничтожении объекта.
        """
        # Закрываем пул потоков
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

        # Очищаем кэш
        self.clear_cache()