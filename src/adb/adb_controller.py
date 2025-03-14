"""
Модуль содержит класс ADBController для взаимодействия с эмуляторами через ADB.
Предоставляет функции для управления эмуляторами, получения скриншотов,
отправки событий и проверки активности приложений.
"""

import os
import time
import logging
import subprocess
import tempfile
import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional, Union, Any
from threading import Lock
from concurrent.futures import ThreadPoolExecutor


class ADBController:
    """
    Класс для взаимодействия с эмуляторами через ADB (Android Debug Bridge).
    Обеспечивает выполнение команд ADB, управление эмуляторами и получение информации.
    """

    def __init__(self, adb_path: Optional[str] = None, max_workers: int = 5, logger=None):
        """
        Инициализирует контроллер ADB.

        Args:
            adb_path: Путь к исполняемому файлу ADB. Если None, будет использован системный ADB.
            max_workers: Максимальное количество рабочих потоков для параллельного выполнения команд.
            logger: Объект логгера для записи отладочной информации.
        """
        self.adb_path = adb_path or "adb"
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger("ADBController")
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = Lock()  # Для потокобезопасных операций
        self.screenshots_cache = {}  # Кэш скриншотов {device_id: (timestamp, image)}
        self.cache_ttl = 0.5  # Время жизни кэша в секундах

        # Проверяем доступность ADB
        self._check_adb_available()

    def _check_adb_available(self) -> bool:
        """
        Проверяет доступность ADB.

        Returns:
            True, если ADB доступен, иначе генерирует исключение.

        Raises:
            RuntimeError: Если ADB недоступен.
        """
        try:
            result = self.execute_adb_command(["version"])
            self.logger.info(f"ADB доступен: {result}")
            return True
        except Exception as e:
            error_msg = f"ADB недоступен: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def execute_adb_command(self, command: List[str], device_id: Optional[str] = None,
                            timeout: int = 30) -> str:
        """
        Выполняет команду ADB.

        Args:
            command: Список аргументов команды ADB.
            device_id: ID устройства. Если указан, команда будет выполнена для этого устройства.
            timeout: Таймаут выполнения команды в секундах.

        Returns:
            Строка с выводом команды.

        Raises:
            subprocess.SubprocessError: При ошибке выполнения команды.
            TimeoutError: При превышении таймаута.
        """
        cmd = [self.adb_path]

        if device_id:
            cmd.extend(["-s", device_id])

        cmd.extend(command)

        self.logger.debug(f"Выполнение команды ADB: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(timeout=timeout)

            if process.returncode != 0:
                error_msg = f"Ошибка выполнения команды ADB: {stderr}"
                self.logger.error(error_msg)
                raise subprocess.SubprocessError(error_msg)

            return stdout.strip()
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = f"Таймаут выполнения команды ADB: {' '.join(cmd)}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)

    def get_devices(self) -> List[Dict[str, str]]:
        """
        Получает список подключенных устройств.

        Returns:
            Список устройств в формате [{"id": "emulator-5554", "state": "device", "type": "emulator"}]
        """
        result = self.execute_adb_command(["devices", "-l"])
        devices = []

        # Пропускаем первую строку "List of devices attached"
        for line in result.split('\n')[1:]:
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 2:
                device_id = parts[0]
                state = parts[1]

                # Определяем тип устройства
                device_type = "physical"
                if "emulator" in device_id:
                    device_type = "emulator"

                # Извлекаем дополнительную информацию
                device_info = {"id": device_id, "state": state, "type": device_type}

                for part in parts[2:]:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        device_info[key] = value

                devices.append(device_info)

        self.logger.info(f"Найдено {len(devices)} устройств: {devices}")
        return devices

    def get_emulators(self) -> List[Dict[str, str]]:
        """
        Получает список подключенных эмуляторов.

        Returns:
            Список эмуляторов из числа подключенных устройств.
        """
        devices = self.get_devices()
        emulators = [device for device in devices if device["type"] == "emulator"]
        self.logger.info(f"Найдено {len(emulators)} эмуляторов: {emulators}")
        return emulators

    def is_emulator_running(self, emulator_id: Union[str, int]) -> bool:
        """
        Проверяет, запущен ли эмулятор с указанным ID.

        Args:
            emulator_id: ID эмулятора (число или строка вида "emulator-5554").

        Returns:
            True, если эмулятор запущен, иначе False.
        """
        # Если передан числовой ID, преобразуем в формат "emulator-XXXX"
        if isinstance(emulator_id, int):
            emulator_id = f"emulator-{5554 + 2 * emulator_id}"

        emulators = self.get_emulators()
        return any(emulator["id"] == emulator_id for emulator in emulators)

    def get_running_activities(self, device_id: str) -> Dict[str, str]:
        """
        Получает список запущенных активностей (приложений) на устройстве.

        Args:
            device_id: ID устройства.

        Returns:
            Словарь {package_name: activity_name} запущенных активностей.
        """
        try:
            # Используем dumpsys для получения информации о запущенных активностях
            result = self.execute_adb_command(["shell", "dumpsys", "activity", "activities"], device_id)

            activities = {}
            for line in result.split('\n'):
                # Ищем строки вида "* TaskRecord{...} #N: ..."
                if "* TaskRecord" in line and "#" in line:
                    # Ищем активность в формате "packageName/activityName"
                    # Например: "com.android.launcher3/.Launcher"
                    for part in line.split():
                        if "/" in part and not part.startswith("u0"):
                            package_activity = part.strip()
                            if "}" in package_activity:
                                package_activity = package_activity.split("}", 1)[1]

                            # Разделяем пакет и активность
                            if "/" in package_activity:
                                package, activity = package_activity.split("/", 1)
                                # Если активность начинается с точки, добавляем имя пакета
                                if activity.startswith("."):
                                    activity = package + activity
                                activities[package] = activity

            self.logger.debug(f"Найденные активности на {device_id}: {activities}")
            return activities
        except Exception as e:
            self.logger.error(f"Ошибка при получении активностей: {str(e)}")
            return {}

    def is_activity_running(self, device_id: str, package_name: str) -> bool:
        """
        Проверяет, запущено ли приложение с указанным package_name.

        Args:
            device_id: ID устройства.
            package_name: Имя пакета приложения.

        Returns:
            True, если приложение запущено, иначе False.
        """
        activities = self.get_running_activities(device_id)
        return package_name in activities

    def start_activity(self, device_id: str, package_name: str, activity_name: Optional[str] = None) -> bool:
        """
        Запускает приложение на устройстве.

        Args:
            device_id: ID устройства.
            package_name: Имя пакета приложения.
            activity_name: Имя активности для запуска. Если None, будет запущена основная активность.

        Returns:
            True в случае успеха, иначе False.
        """
        try:
            if activity_name:
                # Если активность не начинается с пакета, добавляем имя пакета
                if not activity_name.startswith(package_name) and activity_name.startswith("."):
                    activity_name = package_name + activity_name

                # Запускаем конкретную активность
                result = self.execute_adb_command(
                    ["shell", "am", "start", "-n", f"{package_name}/{activity_name}"],
                    device_id
                )
            else:
                # Запускаем приложение по имени пакета
                result = self.execute_adb_command(
                    ["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"],
                    device_id
                )

            self.logger.info(f"Приложение {package_name} запущено на {device_id}: {result}")
            return "Starting" in result or "Events injected" in result
        except Exception as e:
            self.logger.error(f"Ошибка при запуске приложения {package_name}: {str(e)}")
            return False

    def stop_activity(self, device_id: str, package_name: str) -> bool:
        """
        Останавливает приложение на устройстве.

        Args:
            device_id: ID устройства.
            package_name: Имя пакета приложения.

        Returns:
            True в случае успеха, иначе False.
        """
        try:
            result = self.execute_adb_command(
                ["shell", "am", "force-stop", package_name],
                device_id
            )

            self.logger.info(f"Приложение {package_name} остановлено на {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при остановке приложения {package_name}: {str(e)}")
            return False

    def restart_activity(self, device_id: str, package_name: str, activity_name: Optional[str] = None) -> bool:
        """
        Перезапускает приложение на устройстве.

        Args:
            device_id: ID устройства.
            package_name: Имя пакета приложения.
            activity_name: Имя активности для запуска. Если None, будет запущена основная активность.

        Returns:
            True в случае успеха, иначе False.
        """
        # Останавливаем приложение
        if not self.stop_activity(device_id, package_name):
            return False

        # Добавляем небольшую паузу для корректного закрытия приложения
        time.sleep(1)

        # Запускаем приложение
        return self.start_activity(device_id, package_name, activity_name)

    def get_screenshot(self, device_id: str, use_cache: bool = True) -> np.ndarray:
        """
        Получает скриншот экрана устройства в виде массива numpy.

        Args:
            device_id: ID устройства.
            use_cache: Использовать кэш скриншотов (если возможно).

        Returns:
            Изображение в формате numpy.ndarray в формате BGR.

        Raises:
            RuntimeError: При ошибке получения скриншота.
        """
        # Проверяем кэш, если разрешено использовать
        if use_cache and device_id in self.screenshots_cache:
            timestamp, image = self.screenshots_cache[device_id]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.debug(f"Использован кэшированный скриншот для {device_id}")
                return image.copy()  # Возвращаем копию, чтобы избежать изменения кэша

        try:
            # Создаем временный файл для сохранения скриншота
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name

            # Получаем скриншот во временный файл
            self.execute_adb_command(
                ["shell", "screencap", "-p", "/sdcard/screenshot.png"],
                device_id
            )

            # Копируем файл с устройства
            self.execute_adb_command(
                ["pull", "/sdcard/screenshot.png", temp_path],
                device_id
            )

            # Удаляем файл с устройства
            self.execute_adb_command(
                ["shell", "rm", "/sdcard/screenshot.png"],
                device_id
            )

            # Читаем изображение
            image = cv2.imread(temp_path)

            # Удаляем временный файл
            os.unlink(temp_path)

            if image is None:
                raise RuntimeError(f"Не удалось прочитать скриншот с устройства {device_id}")

            # Обновляем кэш
            self.screenshots_cache[device_id] = (time.time(), image.copy())

            self.logger.debug(f"Получен скриншот для {device_id} размером {image.shape}")
            return image
        except Exception as e:
            error_msg = f"Ошибка при получении скриншота с устройства {device_id}: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def tap(self, device_id: str, x: int, y: int) -> bool:
        """
        Выполняет тап (клик) по экрану устройства.

        Args:
            device_id: ID устройства.
            x: X-координата.
            y: Y-координата.

        Returns:
            True в случае успеха, иначе False.
        """
        try:
            self.execute_adb_command(
                ["shell", "input", "tap", str(x), str(y)],
                device_id
            )

            self.logger.debug(f"Выполнен тап по координатам ({x}, {y}) на устройстве {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении тапа на устройстве {device_id}: {str(e)}")
            return False

    def swipe(self, device_id: str, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> bool:
        """
        Выполняет свайп на экране устройства.

        Args:
            device_id: ID устройства.
            x1: Начальная X-координата.
            y1: Начальная Y-координата.
            x2: Конечная X-координата.
            y2: Конечная Y-координата.
            duration_ms: Длительность свайпа в миллисекундах.

        Returns:
            True в случае успеха, иначе False.
        """
        try:
            self.execute_adb_command(
                ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)],
                device_id
            )

            self.logger.debug(
                f"Выполнен свайп от ({x1}, {y1}) до ({x2}, {y2}) "
                f"с длительностью {duration_ms}мс на устройстве {device_id}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении свайпа на устройстве {device_id}: {str(e)}")
            return False

    def start_emulator(self, emulator_id: int) -> bool:
        """
        Запускает эмулятор с указанным ID.

        Args:
            emulator_id: ID эмулятора (число).

        Returns:
            True, если эмулятор успешно запущен, иначе False.
        """
        try:
            # Формат эмулятора: emulator-5554, emulator-5556, etc.
            # ID 0 соответствует порту 5554, ID 1 - порту 5556 и т.д.
            port = 5554 + 2 * emulator_id

            # Проверяем, не запущен ли уже эмулятор
            if self.is_emulator_running(emulator_id):
                self.logger.info(f"Эмулятор {emulator_id} (порт {port}) уже запущен")
                return True

            # Запускаем эмулятор в отдельном процессе
            # Важно: здесь предполагается, что у вас есть команда emulator в PATH
            # Если вы используете LDP Player, команда будет другой
            command = ["emulator", "-port", str(port), "-avd", f"Pixel_API_30_{emulator_id}"]

            # Для LDP Player команда может быть такой:
            # command = ["ldconsole", "launch", "--index", str(emulator_id)]

            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Ждем запуска эмулятора
            start_time = time.time()
            while time.time() - start_time < 60:  # Ждем не более 60 секунд
                if self.is_emulator_running(emulator_id):
                    self.logger.info(f"Эмулятор {emulator_id} (порт {port}) успешно запущен")
                    return True
                time.sleep(2)

            self.logger.error(f"Таймаут при запуске эмулятора {emulator_id} (порт {port})")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при запуске эмулятора {emulator_id}: {str(e)}")
            return False

    def stop_emulator(self, emulator_id: Union[str, int]) -> bool:
        """
        Останавливает эмулятор с указанным ID.

        Args:
            emulator_id: ID эмулятора (число или строка вида "emulator-5554").

        Returns:
            True, если эмулятор успешно остановлен, иначе False.
        """
        try:
            # Если передан числовой ID, преобразуем в формат "emulator-XXXX"
            if isinstance(emulator_id, int):
                emulator_id = f"emulator-{5554 + 2 * emulator_id}"

            # Проверяем, запущен ли эмулятор
            if not self.is_emulator_running(emulator_id):
                self.logger.info(f"Эмулятор {emulator_id} не запущен")
                return True

            # Останавливаем эмулятор
            # Для стандартного эмулятора Android
            try:
                self.execute_adb_command(["emu", "kill"], emulator_id)
            except:
                # Если "emu kill" не работает, используем альтернативный способ
                # Для LDP Player можно использовать: ["ldconsole", "quit", "--index", str(emulator_id)]
                self.execute_adb_command(["shell", "reboot", "-p"], emulator_id)

            # Ждем остановки эмулятора
            start_time = time.time()
            while time.time() - start_time < 30:  # Ждем не более 30 секунд
                if not self.is_emulator_running(emulator_id):
                    self.logger.info(f"Эмулятор {emulator_id} успешно остановлен")
                    return True
                time.sleep(1)

            self.logger.error(f"Таймаут при остановке эмулятора {emulator_id}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при остановке эмулятора {emulator_id}: {str(e)}")
            return False

    def restart_emulator(self, emulator_id: Union[str, int]) -> bool:
        """
        Перезапускает эмулятор с указанным ID.

        Args:
            emulator_id: ID эмулятора (число или строка вида "emulator-5554").

        Returns:
            True, если эмулятор успешно перезапущен, иначе False.
        """
        # Получаем числовой ID, если передана строка
        if isinstance(emulator_id, str) and emulator_id.startswith("emulator-"):
            try:
                port = int(emulator_id.split("-")[1])
                num_id = (port - 5554) // 2
            except:
                self.logger.error(f"Не удалось получить числовой ID для эмулятора {emulator_id}")
                return False
        else:
            num_id = emulator_id

        # Останавливаем эмулятор
        if not self.stop_emulator(emulator_id):
            return False

        # Ждем, чтобы убедиться, что эмулятор полностью остановлен
        time.sleep(3)

        # Запускаем эмулятор
        return self.start_emulator(num_id)

    def execute_parallel_command(self, command_func, device_ids: List[str], *args, **kwargs) -> Dict[str, Any]:
        """
        Выполняет команду параллельно на нескольких устройствах.

        Args:
            command_func: Функция для выполнения (метод этого класса).
            device_ids: Список ID устройств.
            *args, **kwargs: Аргументы для функции.

        Returns:
            Словарь {device_id: результат}
        """
        results = {}

        # Создаем функцию для выполнения в потоке
        def execute_for_device(device_id):
            try:
                result = command_func(device_id, *args, **kwargs)
                return device_id, result
            except Exception as e:
                self.logger.error(f"Ошибка при выполнении команды для {device_id}: {str(e)}")
                return device_id, None

        # Запускаем задачи в пуле потоков
        futures = []
        for device_id in device_ids:
            futures.append(self.executor.submit(execute_for_device, device_id))

        # Собираем результаты
        for future in futures:
            try:
                device_id, result = future.result()
                results[device_id] = result
            except Exception as e:
                self.logger.error(f"Ошибка при получении результата: {str(e)}")

        return results

    def clear_cache(self, device_id: Optional[str] = None):
        """
        Очищает кэш скриншотов.

        Args:
            device_id: ID устройства для очистки. Если None, очищает весь кэш.
        """
        with self.lock:
            if device_id:
                if device_id in self.screenshots_cache:
                    del self.screenshots_cache[device_id]
                    self.logger.debug(f"Кэш скриншотов для {device_id} очищен")
            else:
                self.screenshots_cache.clear()
                self.logger.debug("Весь кэш скриншотов очищен")

    def __del__(self):
        """Освобождает ресурсы при уничтожении объекта."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)