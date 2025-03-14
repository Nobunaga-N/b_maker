# src/bots/bot_executor.py
import os
import time
import logging
import threading
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from datetime import datetime

from src.adb.adb_controller import ADBController
from src.utils.image_processor import ImageProcessor
from src.utils.exceptions import BotExecutionError, ADBCommandError, ImageProcessingError


class BotExecutor:
    """
    Исполнитель скриптов ботов.
    Отвечает за интерпретацию модулей бота в последовательные команды,
    выполнение действий на эмуляторе через ADB, обработку условий и циклов.
    """

    def __init__(self, adb_controller: ADBController, logger: Optional[logging.Logger] = None):
        """
        Инициализирует исполнитель скриптов ботов.

        Args:
            adb_controller: Контроллер ADB для взаимодействия с эмуляторами.
            logger: Объект логирования.
        """
        self.adb_controller = adb_controller
        self.logger = logger
        self.image_processor = ImageProcessor(logger=logger)

        # Состояние выполнения
        self.running = threading.Event()
        self.paused = threading.Event()
        self.stop_requested = threading.Event()

        # Информация о текущем выполнении
        self.current_bot = None
        self.current_device = None
        self.current_module_index = 0
        self.cycle_count = 0
        self.start_time = None
        self.last_position = None

        # Функция для уведомления о прогрессе
        self.progress_callback = None

        # Статистика выполнения
        self.statistics = {
            'cycles_completed': 0,
            'actions_executed': 0,
            'clicks_performed': 0,
            'swipes_performed': 0,
            'images_found': 0,
            'images_not_found': 0,
            'errors': 0,
            'execution_time': 0,
        }

    def _log_debug(self, message: str) -> None:
        """Вспомогательный метод для логирования отладочных сообщений."""
        if self.logger:
            self.logger.debug(message)

    def _log_info(self, message: str) -> None:
        """Вспомогательный метод для логирования информационных сообщений."""
        if self.logger:
            self.logger.info(message)

    def _log_error(self, message: str) -> None:
        """Вспомогательный метод для логирования ошибок."""
        if self.logger:
            self.logger.error(message)

    def _log_warning(self, message: str) -> None:
        """Вспомогательный метод для логирования предупреждений."""
        if self.logger:
            self.logger.warning(message)

    def load_bot_config(self, bot_path: str) -> Dict[str, Any]:
        """
        Загружает конфигурацию бота из JSON-файла.

        Args:
            bot_path: Путь к директории бота.

        Returns:
            Словарь с конфигурацией бота.

        Raises:
            BotExecutionError: Если произошла ошибка при загрузке конфигурации.
        """
        try:
            config_path = os.path.join(bot_path, "config.json")

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self._log_debug(f"Конфигурация бота загружена: {config_path}")
            return config

        except Exception as e:
            error_msg = f"Ошибка загрузки конфигурации бота: {e}"
            self._log_error(error_msg)
            raise BotExecutionError(error_msg)

    def execute_bot(self, bot_name: str, device_id: str,
                    max_cycles: int = 0, max_time: int = 0,
                    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """
        Выполняет скрипт бота на указанном устройстве.

        Args:
            bot_name: Имя бота для выполнения.
            device_id: Идентификатор устройства (эмулятора).
            max_cycles: Максимальное количество циклов выполнения (0 = бесконечно).
            max_time: Максимальное время выполнения в минутах (0 = без ограничения).
            progress_callback: Функция обратного вызова для отображения прогресса.

        Raises:
            BotExecutionError: Если произошла ошибка при выполнении бота.
        """
        try:
            # Проверяем готовность к запуску
            if self.running.is_set():
                raise BotExecutionError(f"Бот уже выполняется: {self.current_bot}")

            # Загружаем конфигурацию бота
            bot_path = os.path.join("bots", bot_name)
            self.current_bot = bot_name
            self.current_device = device_id
            self.current_module_index = 0
            self.cycle_count = 0
            self.start_time = time.time()
            self.last_position = None
            self.progress_callback = progress_callback

            # Сбрасываем статистику
            self.statistics = {
                'cycles_completed': 0,
                'actions_executed': 0,
                'clicks_performed': 0,
                'swipes_performed': 0,
                'images_found': 0,
                'images_not_found': 0,
                'errors': 0,
                'execution_time': 0,
            }

            # Загружаем конфигурацию бота
            config = self.load_bot_config(bot_path)

            # Проверяем соединение с устройством
            if not self.adb_controller.check_device_status(device_id):
                raise BotExecutionError(f"Устройство {device_id} недоступно")

            # Устанавливаем флаги для выполнения
            self.running.set()
            self.paused.clear()
            self.stop_requested.clear()

            # Получаем модули из конфигурации
            modules = config.get("modules", [])
            game = config.get("game", "")

            if not modules:
                raise BotExecutionError(f"Бот {bot_name} не содержит модулей")

            self._log_info(f"Запуск бота {bot_name} на устройстве {device_id}")
            self._log_info(f"Максимальное количество циклов: {max_cycles if max_cycles > 0 else 'бесконечно'}")
            self._log_info(f"Максимальное время выполнения: {max_time if max_time > 0 else 'без ограничения'} минут")

            # Выполняем цикл бота
            try:
                # Проверяем необходимость активности
                activity_module = None
                for module in modules:
                    if module.get("type") == "activity" and module.get("enabled", False):
                        activity_module = module
                        break

                # Если есть модуль активности, запускаем игру
                if activity_module:
                    package_name = activity_module.get("activity", "")
                    if package_name:
                        self._log_info(f"Запуск игры {game} ({package_name})")
                        try:
                            self.adb_controller.launch_app(device_id, package_name)
                            delay = activity_module.get("startup_delay", 1.0)
                            if delay > 0:
                                self._log_debug(f"Ожидание {delay} сек после запуска игры")
                                time.sleep(delay)
                        except Exception as e:
                            self._log_warning(f"Ошибка запуска игры: {e}")

                # Основной цикл выполнения
                while self.running.is_set() and not self.stop_requested.is_set():
                    # Проверяем, не превышено ли максимальное количество циклов
                    if max_cycles > 0 and self.cycle_count >= max_cycles:
                        self._log_info(f"Достигнуто максимальное количество циклов ({max_cycles})")
                        break

                    # Проверяем, не превышено ли максимальное время выполнения
                    if max_time > 0:
                        elapsed_minutes = (time.time() - self.start_time) / 60
                        if elapsed_minutes >= max_time:
                            self._log_info(f"Достигнуто максимальное время выполнения ({max_time} минут)")
                            break

                    # Выполняем один цикл
                    self._execute_cycle(modules, device_id, bot_path, activity_module)

                    # Увеличиваем счетчик циклов
                    self.cycle_count += 1
                    self.statistics['cycles_completed'] = self.cycle_count

                    # Обновляем статистику времени выполнения
                    self.statistics['execution_time'] = time.time() - self.start_time

                    # Вызываем callback для отображения прогресса
                    if self.progress_callback:
                        self.progress_callback(self.get_progress_info())

                    self._log_info(f"Завершен цикл {self.cycle_count}")

            except Exception as e:
                self._log_error(f"Ошибка выполнения бота: {e}")
                self.statistics['errors'] += 1
                raise

            finally:
                # Сбрасываем флаг выполнения
                self.running.clear()

                # Обновляем статистику
                self.statistics['execution_time'] = time.time() - self.start_time

                # Вызываем callback для отображения итогового прогресса
                if self.progress_callback:
                    self.progress_callback(self.get_progress_info())

                self._log_info(f"Завершение выполнения бота {bot_name}")

        except Exception as e:
            error_msg = f"Ошибка выполнения бота {bot_name} на устройстве {device_id}: {e}"
            self._log_error(error_msg)

            # Сбрасываем флаг выполнения
            self.running.clear()

            raise BotExecutionError(error_msg)

    async def execute_bot_async(self, bot_name: str, device_id: str,
                                max_cycles: int = 0, max_time: int = 0,
                                progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """
        Асинхронно выполняет скрипт бота на указанном устройстве.

        Args:
            bot_name: Имя бота для выполнения.
            device_id: Идентификатор устройства (эмулятора).
            max_cycles: Максимальное количество циклов выполнения (0 = бесконечно).
            max_time: Максимальное время выполнения в минутах (0 = без ограничения).
            progress_callback: Функция обратного вызова для отображения прогресса.
        """
        # Создаем новую задачу в событийном цикле
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,  # Используем потоки по умолчанию
            self.execute_bot, bot_name, device_id, max_cycles, max_time, progress_callback
        )

    def _execute_cycle(self, modules: List[Dict[str, Any]], device_id: str,
                       bot_path: str, activity_module: Optional[Dict[str, Any]]) -> None:
        """
        Выполняет один цикл бота.

        Args:
            modules: Список модулей для выполнения.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.
            activity_module: Модуль проверки активности (если есть).

        Raises:
            BotExecutionError: Если произошла ошибка при выполнении цикла.
        """
        try:
            # Сбрасываем индекс текущего модуля
            self.current_module_index = 0

            # Выполняем модули по порядку
            while self.current_module_index < len(
                    modules) and self.running.is_set() and not self.stop_requested.is_set():
                # Если пауза, ждем ее снятия
                if self.paused.is_set():
                    time.sleep(0.1)
                    continue

                # Получаем текущий модуль
                module = modules[self.current_module_index]

                # Проверяем активность, если есть соответствующий модуль
                if activity_module and activity_module.get("enabled", False):
                    # Проверяем, входит ли текущий индекс в диапазон для проверки
                    line_range = activity_module.get("line_range", "")
                    if self._is_in_line_range(self.current_module_index, line_range):
                        self._check_activity(activity_module, device_id)

                # Выполняем текущий модуль
                self._execute_module(module, device_id, bot_path)

                # Переходим к следующему модулю
                self.current_module_index += 1

                # Обновляем статистику
                self.statistics['actions_executed'] += 1

                # Сохраняем последнюю позицию
                self.last_position = self.current_module_index

        except Exception as e:
            error_msg = f"Ошибка выполнения цикла бота: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _is_in_line_range(self, line: int, line_range: str) -> bool:
        """
        Проверяет, входит ли строка в указанный диапазон.

        Args:
            line: Номер строки для проверки.
            line_range: Строка с диапазоном строк (например, "1-5,10-15").

        Returns:
            True, если строка входит в диапазон, иначе False.
        """
        if not line_range:
            return True  # Если диапазон не указан, проверяем все строки

        try:
            for range_part in line_range.split(','):
                range_part = range_part.strip()

                if '-' in range_part:
                    # Диапазон строк
                    start, end = map(int, range_part.split('-'))
                    if start <= line <= end:
                        return True
                elif range_part.isdigit():
                    # Одиночная строка
                    if line == int(range_part):
                        return True

            return False

        except Exception as e:
            self._log_warning(f"Ошибка проверки диапазона строк '{line_range}': {e}")
            return True  # В случае ошибки проверяем все строки

    def _check_activity(self, activity_module: Dict[str, Any], device_id: str) -> None:
        """
        Проверяет активность игры и выполняет необходимые действия, если игра вылетела.

        Args:
            activity_module: Модуль проверки активности.
            device_id: Идентификатор устройства.

        Raises:
            BotExecutionError: Если произошла ошибка при проверке активности.
        """
        try:
            # Проверяем активность игры
            package_name = activity_module.get("activity", "")
            if not package_name:
                return  # Нет имени пакета, не можем проверить активность

            # Проверяем, запущено ли приложение
            is_running = self.adb_controller.check_app_running(device_id, package_name)

            if is_running:
                # Игра запущена, все в порядке
                return

            # Игра не запущена, выполняем действия в зависимости от настроек
            self._log_warning(f"Игра {package_name} не активна на устройстве {device_id}")

            action = activity_module.get("action", "continue_bot")

            if action == "activity.running.clear(0)":
                # Остановить выполнение бота
                self._log_info("Остановка выполнения бота по причине неактивности игры")
                self.running.clear()
                return

            elif action == "activity.running.clear(1)":
                # Остановить выполнение бота и запустить следующий
                self._log_info("Остановка выполнения бота и запуск следующего по причине неактивности игры")
                self.running.clear()
                # TODO: Добавить логику запуска следующего бота
                return

            elif action == "continue_bot":
                # Перезапустить игру и продолжить выполнение
                self._log_info("Перезапуск игры и продолжение выполнения бота")

                # Получаем опции продолжения
                continue_options = activity_module.get("continue_options", [])

                # Выполняем опции продолжения
                for option in continue_options:
                    option_type = option.get("type", "")

                    if option_type == "close_game":
                        # Закрываем игру
                        self._log_info(f"Закрытие игры {package_name}")
                        self.adb_controller.stop_app(device_id, package_name)

                    elif option_type == "restart_emulator":
                        # Перезапускаем эмулятор
                        self._log_info(f"Перезапуск эмулятора {device_id}")
                        self.adb_controller.reboot_ldplayer(device_id)

                    elif option_type == "start_game":
                        # Запускаем игру
                        self._log_info(f"Запуск игры {package_name}")
                        self.adb_controller.launch_app(device_id, package_name)

                    elif option_type == "time_sleep":
                        # Пауза
                        sleep_time = option.get("data", {}).get("time", 1.0)
                        self._log_info(f"Пауза {sleep_time} сек")
                        time.sleep(sleep_time)

                    elif option_type == "restart_from":
                        # Перезапуск с указанной строки
                        line = option.get("data", {}).get("line", 0)
                        if 0 <= line < len(self.modules):
                            self._log_info(f"Перезапуск с позиции {line}")
                            self.current_module_index = line

                    elif option_type == "restart_from_last":
                        # Перезапуск с последней позиции
                        if self.last_position is not None:
                            self._log_info(f"Перезапуск с последней позиции {self.last_position}")
                            self.current_module_index = self.last_position

                # Даем время на запуск игры
                delay = activity_module.get("startup_delay", 1.0)
                if delay > 0:
                    self._log_debug(f"Ожидание {delay} сек после перезапуска игры")
                    time.sleep(delay)

                return

        except Exception as e:
            error_msg = f"Ошибка проверки активности: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _execute_module(self, module: Dict[str, Any], device_id: str, bot_path: str) -> None:
        """
        Выполняет отдельный модуль бота.

        Args:
            module: Модуль для выполнения.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.

        Raises:
            BotExecutionError: Если произошла ошибка при выполнении модуля.
        """
        try:
            module_type = module.get("type", "")

            # Выводим информацию о текущем модуле
            self._log_debug(f"Выполнение модуля типа '{module_type}'")

            if module_type == "click":
                # Выполняем клик
                self._execute_click_module(module, device_id)

            elif module_type == "swipe":
                # Выполняем свайп
                self._execute_swipe_module(module, device_id)

            elif module_type == "time_sleep":
                # Выполняем паузу
                self._execute_sleep_module(module)

            elif module_type == "image_search":
                # Выполняем поиск изображения
                self._execute_image_search_module(module, device_id, bot_path)

            elif module_type == "activity":
                # Модуль активности обрабатывается отдельно
                pass

            else:
                self._log_warning(f"Неизвестный тип модуля: {module_type}")

        except Exception as e:
            error_msg = f"Ошибка выполнения модуля '{module.get('type', 'unknown')}': {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _execute_click_module(self, module: Dict[str, Any], device_id: str) -> None:
        """
        Выполняет модуль клика.

        Args:
            module: Модуль клика.
            device_id: Идентификатор устройства.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            # Получаем параметры клика
            x = module.get("x", 0)
            y = module.get("y", 0)
            sleep_time = module.get("sleep", 0.0)
            description = module.get("description", "")
            console_description = module.get("console_description", "")

            # Выводим информацию
            message = console_description or f"Клик по координатам ({x}, {y})"
            if description:
                message += f" - {description}"
            self._log_info(message)

            # Выполняем клик
            self.adb_controller.tap(device_id, x, y)

            # Обновляем статистику
            self.statistics['clicks_performed'] += 1

            # Задержка после клика
            if sleep_time > 0:
                self._log_debug(f"Пауза {sleep_time} сек после клика")
                time.sleep(sleep_time)

        except Exception as e:
            error_msg = f"Ошибка выполнения клика: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise ADBCommandError(error_msg)

    def _execute_swipe_module(self, module: Dict[str, Any], device_id: str) -> None:
        """
        Выполняет модуль свайпа.

        Args:
            module: Модуль свайпа.
            device_id: Идентификатор устройства.

        Raises:
            ADBCommandError: Если произошла ошибка при выполнении команды.
        """
        try:
            # Получаем параметры свайпа
            x1 = module.get("x1", 0)
            y1 = module.get("y1", 0)
            x2 = module.get("x2", 0)
            y2 = module.get("y2", 0)
            sleep_time = module.get("sleep", 0.0)
            description = module.get("description", "")
            console_description = module.get("console_description", "")

            # Выводим информацию
            message = console_description or f"Свайп от ({x1}, {y1}) к ({x2}, {y2})"
            if description:
                message += f" - {description}"
            self._log_info(message)

            # Выполняем свайп
            self.adb_controller.swipe(device_id, x1, y1, x2, y2)

            # Обновляем статистику
            self.statistics['swipes_performed'] += 1

            # Задержка после свайпа
            if sleep_time > 0:
                self._log_debug(f"Пауза {sleep_time} сек после свайпа")
                time.sleep(sleep_time)

        except Exception as e:
            error_msg = f"Ошибка выполнения свайпа: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise ADBCommandError(error_msg)

    def _execute_sleep_module(self, module: Dict[str, Any]) -> None:
        """
        Выполняет модуль паузы.

        Args:
            module: Модуль паузы.
        """
        try:
            # Получаем параметры паузы
            sleep_time = module.get("delay", 1.0)
            description = module.get("description", "")

            # Выводим информацию
            message = f"Пауза {sleep_time} сек"
            if description:
                message += f" - {description}"
            self._log_info(message)

            # Выполняем паузу
            time.sleep(sleep_time)

        except Exception as e:
            error_msg = f"Ошибка выполнения паузы: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _execute_image_search_module(self, module: Dict[str, Any], device_id: str, bot_path: str) -> None:
        """
        Выполняет модуль поиска изображения.

        Args:
            module: Модуль поиска изображения.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.

        Raises:
            ImageProcessingError: Если произошла ошибка при обработке изображений.
        """
        try:
            # Получаем параметры поиска
            images = module.get("images", [])
            timeout = module.get("timeout", 10)
            script_items = module.get("script_items", [])

            if not images:
                self._log_warning("Нет изображений для поиска")
                return

            # Формируем полные пути к изображениям
            image_paths = []
            for image_name in images:
                image_path = os.path.join(bot_path, "images", image_name)
                if os.path.exists(image_path):
                    image_paths.append(image_path)
                else:
                    self._log_warning(f"Изображение не найдено: {image_path}")

            if not image_paths:
                self._log_warning("Ни одно изображение не найдено на диске")
                return

            # Выводим информацию
            self._log_info(f"Поиск изображений: {', '.join(images)} с таймаутом {timeout} сек")

            # Функция для получения скриншота
            def get_screenshot():
                return self.adb_controller.get_screenshot(device_id)

            # Ищем изображения
            found_image, result = self.image_processor.wait_for_any_template(
                get_screenshot, image_paths, timeout=timeout
            )

            # Обрабатываем результат поиска
            if found_image:
                # Изображение найдено
                self._log_info(f"Изображение найдено: {os.path.basename(found_image)}")
                self.statistics['images_found'] += 1

                # Сохраняем координаты для get_coords
                self._found_coords = (result['center_x'], result['center_y'])

                # Выполняем блоки IF Result и ELIF
                self._execute_image_search_result_blocks(script_items, found_image, device_id, bot_path)

            else:
                # Изображение не найдено
                self._log_info("Изображение не найдено")
                self.statistics['images_not_found'] += 1

                # Выполняем блоки IF Not Result
                self._execute_image_search_not_result_blocks(script_items, device_id, bot_path)

        except Exception as e:
            error_msg = f"Ошибка выполнения поиска изображения: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise ImageProcessingError(error_msg)

    def _execute_image_search_result_blocks(self, script_items: List[Dict[str, Any]],
                                            found_image: str, device_id: str, bot_path: str) -> None:
        """
        Выполняет блоки IF Result и ELIF для найденного изображения.

        Args:
            script_items: Список блоков скрипта.
            found_image: Путь к найденному изображению.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.
        """
        try:
            # Ищем блоки IF Result и ELIF
            found_image_basename = os.path.basename(found_image)
            executed_block = False

            for item in script_items:
                item_type = item.get("type", "")
                item_data = item.get("data", {})

                if item_type == "if_result":
                    # Блок IF Result
                    image = item_data.get("image")

                    # Проверяем, подходит ли блок для найденного изображения
                    if image is None or image == found_image_basename:
                        # Выводим сообщение в консоль
                        log_event = item_data.get("log_event", "")
                        if log_event:
                            self._log_info(log_event)

                        # Выполняем действия блока
                        self._execute_image_search_actions(item_data, device_id, bot_path)

                        executed_block = True
                        break

                elif item_type == "elif" and not executed_block:
                    # Блок ELIF (выполняется только если не выполнен IF Result)
                    image = item_data.get("image")

                    if image == found_image_basename:
                        # Выводим сообщение в консоль
                        log_event = item_data.get("log_event", "")
                        if log_event:
                            self._log_info(log_event)

                        # Выполняем действия блока
                        self._execute_image_search_actions(item_data, device_id, bot_path)

                        executed_block = True
                        break

        except Exception as e:
            error_msg = f"Ошибка выполнения блоков результата поиска изображения: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _execute_image_search_not_result_blocks(self, script_items: List[Dict[str, Any]],
                                                device_id: str, bot_path: str) -> None:
        """
        Выполняет блоки IF Not Result для случая, когда изображение не найдено.

        Args:
            script_items: Список блоков скрипта.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.
        """
        try:
            # Ищем блоки IF Not Result
            for item in script_items:
                item_type = item.get("type", "")
                item_data = item.get("data", {})

                if item_type == "if_not_result":
                    # Выводим сообщение в консоль
                    log_event = item_data.get("log_event", "")
                    if log_event:
                        self._log_info(log_event)

                    # Выполняем действия блока
                    self._execute_image_search_actions(item_data, device_id, bot_path)

                    break

        except Exception as e:
            error_msg = f"Ошибка выполнения блоков для случая, когда изображение не найдено: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def _execute_image_search_actions(self, block_data: Dict[str, Any], device_id: str, bot_path: str) -> None:
        """
        Выполняет действия блока поиска изображения.

        Args:
            block_data: Данные блока.
            device_id: Идентификатор устройства.
            bot_path: Путь к директории бота.
        """
        try:
            # Проверяем наличие действий
            actions = block_data.get("actions", [])

            # Флаги для специальных действий
            do_get_coords = block_data.get("get_coords", False)
            do_continue = block_data.get("continue", False)
            do_stop_bot = block_data.get("stop_bot", False)

            # Выполняем get_coords, если указано
            if do_get_coords and hasattr(self, '_found_coords'):
                x, y = self._found_coords
                self._log_info(f"Клик по координатам найденного изображения ({x}, {y})")
                self.adb_controller.tap(device_id, x, y)
                self.statistics['clicks_performed'] += 1

            # Выполняем действия из списка
            for action in actions:
                action_type = action.get("type", "")
                action_data = action.get("data", {})

                if action_type == "Клик":
                    # Выполняем клик
                    click_module = {
                        "type": "click",
                        "x": action_data.get("x", 0),
                        "y": action_data.get("y", 0),
                        "sleep": action_data.get("sleep", 0.0),
                        "description": action_data.get("description", ""),
                        "console_description": action_data.get("console_description", "")
                    }
                    self._execute_click_module(click_module, device_id)

                elif action_type == "Свайп":
                    # Выполняем свайп
                    swipe_module = {
                        "type": "swipe",
                        "x1": action_data.get("x1", 0),
                        "y1": action_data.get("y1", 0),
                        "x2": action_data.get("x2", 0),
                        "y2": action_data.get("y2", 0),
                        "sleep": action_data.get("sleep", 0.0),
                        "description": action_data.get("description", ""),
                        "console_description": action_data.get("console_description", "")
                    }
                    self._execute_swipe_module(swipe_module, device_id)

                elif action_type == "get_coords":
                    # Выполняем клик по координатам найденного изображения
                    if hasattr(self, '_found_coords'):
                        x, y = self._found_coords
                        self._log_info(f"Клик по координатам найденного изображения ({x}, {y})")
                        self.adb_controller.tap(device_id, x, y)
                        self.statistics['clicks_performed'] += 1

                elif action_type == "time_sleep":
                    # Выполняем паузу
                    sleep_module = {
                        "type": "time_sleep",
                        "delay": action_data.get("time", 1.0),
                        "description": "Пауза в блоке поиска изображения"
                    }
                    self._execute_sleep_module(sleep_module)

            # Выполняем continue, если указано
            if do_continue:
                self._log_info("Продолжение выполнения скрипта (continue)")
                # Ничего не делаем, просто продолжаем выполнение

            # Выполняем stop_bot, если указано
            if do_stop_bot:
                self._log_info("Остановка выполнения бота (running.clear())")
                self.running.clear()

        except Exception as e:
            error_msg = f"Ошибка выполнения действий блока поиска изображения: {e}"
            self._log_error(error_msg)
            self.statistics['errors'] += 1
            raise BotExecutionError(error_msg)

    def pause(self) -> None:
        """
        Приостанавливает выполнение бота.
        """
        if self.running.is_set() and not self.paused.is_set():
            self._log_info(f"Приостановка выполнения бота {self.current_bot}")
            self.paused.set()

    def resume(self) -> None:
        """
        Возобновляет выполнение бота.
        """
        if self.running.is_set() and self.paused.is_set():
            self._log_info(f"Возобновление выполнения бота {self.current_bot}")
            self.paused.clear()

    def stop(self) -> None:
        """
        Останавливает выполнение бота.
        """
        if self.running.is_set():
            self._log_info(f"Остановка выполнения бота {self.current_bot}")
            self.stop_requested.set()

    def is_running(self) -> bool:
        """
        Проверяет, выполняется ли бот в данный момент.

        Returns:
            True, если бот выполняется, иначе False.
        """
        return self.running.is_set()

    def is_paused(self) -> bool:
        """
        Проверяет, приостановлен ли бот в данный момент.

        Returns:
            True, если бот приостановлен, иначе False.
        """
        return self.paused.is_set()

    def get_progress_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о прогрессе выполнения бота.

        Returns:
            Словарь с информацией о прогрессе.
        """
        progress = {
            'bot_name': self.current_bot,
            'device_id': self.current_device,
            'current_module': self.current_module_index,
            'cycle_count': self.cycle_count,
            'running': self.running.is_set(),
            'paused': self.paused.is_set(),
            'start_time': self.start_time,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0,
            'statistics': self.statistics.copy(),
            'timestamp': datetime.now().isoformat()
        }

        return progress

    def __del__(self):
        """
        Освобождает ресурсы при уничтожении объекта.
        """
        # Останавливаем выполнение, если оно запущено
        if hasattr(self, 'running') and self.running.is_set():
            self.stop()