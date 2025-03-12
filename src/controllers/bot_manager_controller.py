# src/controllers/bot_manager_controller.py
"""
Модуль содержит класс BotManagerController, который управляет
взаимодействием между UI менеджера ботов и бизнес-логикой.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from src.utils.resources import Resources
from src.utils.file_manager import (
    create_bot_environment, load_bot_config, export_bot,
    import_bot, delete_bot, save_bot_config
)


class BotManagerController(QObject):
    """
    Контроллер для управления менеджером ботов.
    Обрабатывает действия пользователя и управляет бизнес-логикой.
    """
    # Сигналы для обновления UI
    botsLoaded = pyqtSignal(list)  # Список ботов загружен
    botDeleted = pyqtSignal(str)  # Бот удален (имя бота)
    botAdded = pyqtSignal(str, str)  # Бот добавлен (имя бота, игра)
    botExported = pyqtSignal(str, str)  # Бот экспортирован (имя бота, путь)
    botImported = pyqtSignal(str, str)  # Бот импортирован (имя бота, игра)

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.logger = logger
        self.active_bots = {}  # Словарь активных ботов {имя_бота: данные}

    def log_info(self, message: str):
        """Вспомогательный метод для логирования информации"""
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def log_error(self, message: str):
        """Вспомогательный метод для логирования ошибок"""
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def load_all_bots(self) -> List[Tuple[str, str]]:
        """
        Загружает список всех доступных ботов.

        Returns:
            Список кортежей (имя_бота, игра)
        """
        try:
            self.log_info("Загрузка списка ботов")

            # Получаем список директорий ботов
            bot_names = Resources.list_bots()
            bots_data = []

            # Загружаем данные о каждом боте
            for bot_name in bot_names:
                bot_config = load_bot_config(bot_name)
                if bot_config:
                    game_name = bot_config.get("game", "")
                    bots_data.append((bot_name, game_name))
                else:
                    # Если конфиг не загрузился, добавляем бота без игры
                    bots_data.append((bot_name, ""))

            # Испускаем сигнал об успешной загрузке
            self.botsLoaded.emit(bots_data)
            return bots_data

        except Exception as e:
            self.log_error(f"Ошибка загрузки ботов: {str(e)}")
            return []

    def delete_bot(self, bot_name: str) -> bool:
        """
        Удаляет бота.

        Args:
            bot_name: Имя бота для удаления

        Returns:
            True в случае успеха, иначе False
        """
        try:
            self.log_info(f"Удаление бота '{bot_name}'")

            # Проверяем, не запущен ли бот
            if bot_name in self.active_bots:
                self.log_error(f"Невозможно удалить бота '{bot_name}', так как он запущен")
                return False

            # Удаляем бота
            if delete_bot(bot_name):
                self.log_info(f"Бот '{bot_name}' успешно удален")
                # Испускаем сигнал
                self.botDeleted.emit(bot_name)
                return True
            else:
                self.log_error(f"Не удалось удалить бота '{bot_name}'")
                return False

        except Exception as e:
            self.log_error(f"Ошибка при удалении бота '{bot_name}': {str(e)}")
            return False

    def export_bot(self, bot_name: str, target_path: str) -> bool:
        """
        Экспортирует бота в указанный путь.

        Args:
            bot_name: Имя бота для экспорта
            target_path: Путь для сохранения экспорта

        Returns:
            True в случае успеха, иначе False
        """
        try:
            self.log_info(f"Экспорт бота '{bot_name}' в '{target_path}'")

            # Экспортируем бота
            if export_bot(bot_name, target_path):
                self.log_info(f"Бот '{bot_name}' успешно экспортирован")
                # Испускаем сигнал
                self.botExported.emit(bot_name, target_path)
                return True
            else:
                self.log_error(f"Не удалось экспортировать бота '{bot_name}'")
                return False

        except Exception as e:
            self.log_error(f"Ошибка при экспорте бота '{bot_name}': {str(e)}")
            return False

    def import_bot(self, source_path: str, new_name: Optional[str] = None) -> bool:
        """
        Импортирует бота из указанного пути.

        Args:
            source_path: Путь к файлу импорта
            new_name: Новое имя для импортируемого бота (опционально)

        Returns:
            True в случае успеха, иначе False
        """
        try:
            self.log_info(f"Импорт бота из '{source_path}'")

            # Импортируем бота
            success, bot_name = import_bot(source_path, new_name)

            if success:
                self.log_info(f"Бот '{bot_name}' успешно импортирован")

                # Загружаем конфигурацию для получения имени игры
                bot_config = load_bot_config(bot_name)
                game_name = bot_config.get("game", "") if bot_config else ""

                # Испускаем сигнал
                self.botImported.emit(bot_name, game_name)
                return True
            else:
                self.log_error(f"Не удалось импортировать бота: {bot_name}")
                return False

        except Exception as e:
            self.log_error(f"Ошибка при импорте бота: {str(e)}")
            return False

    def start_bot(self, bot_name: str, params: Dict[str, Any] = None) -> bool:
        """
        Запускает бота с указанными параметрами.

        Args:
            bot_name: Имя бота для запуска
            params: Параметры запуска (опционально)

        Returns:
            True в случае успеха, иначе False
        """
        try:
            self.log_info(f"Запуск бота '{bot_name}'")

            # Проверяем существование бота
            if not Resources.bot_exists(bot_name):
                self.log_error(f"Бот '{bot_name}' не существует")
                return False

            # Загружаем конфигурацию бота
            bot_config = load_bot_config(bot_name)
            if not bot_config:
                self.log_error(f"Не удалось загрузить конфигурацию бота '{bot_name}'")
                return False

            # Соединяем параметры конфигурации и переданные параметры
            if params:
                # В реальной реализации здесь будет логика запуска бота с параметрами
                self.log_info(f"Параметры запуска бота '{bot_name}': {params}")

            # Добавляем бота в список активных
            self.active_bots[bot_name] = {
                "config": bot_config,
                "params": params or {},
                "status": "running"
            }

            self.log_info(f"Бот '{bot_name}' успешно запущен")
            return True

        except Exception as e:
            self.log_error(f"Ошибка при запуске бота '{bot_name}': {str(e)}")
            return False

    def stop_bot(self, bot_name: str) -> bool:
        """
        Останавливает бота.

        Args:
            bot_name: Имя бота для остановки

        Returns:
            True в случае успеха, иначе False
        """
        try:
            self.log_info(f"Остановка бота '{bot_name}'")

            # Проверяем, запущен ли бот
            if bot_name not in self.active_bots:
                self.log_error(f"Бот '{bot_name}' не запущен")
                return False

            # Останавливаем бота
            # В реальной реализации здесь будет логика остановки бота

            # Удаляем бота из списка активных
            del self.active_bots[bot_name]

            self.log_info(f"Бот '{bot_name}' успешно остановлен")
            return True

        except Exception as e:
            self.log_error(f"Ошибка при остановке бота '{bot_name}': {str(e)}")
            return False

    def get_bot_status(self, bot_name: str) -> Optional[str]:
        """
        Возвращает статус бота.

        Args:
            bot_name: Имя бота

        Returns:
            Строка со статусом или None, если бот не запущен
        """
        if bot_name in self.active_bots:
            return self.active_bots[bot_name].get("status", "unknown")
        return None

    def parse_emulators_string(self, emulators_str: str) -> List[int]:
        """
        Парсит строку с указанием эмуляторов и возвращает список их ID.

        Args:
            emulators_str: Строка вида "0:5,7,9:10"

        Returns:
            Список ID эмуляторов
        """
        emu_list = []
        try:
            if not emulators_str.strip():
                return []

            raw_parts = emulators_str.strip().split(",")
            for part in raw_parts:
                if ":" in part:
                    start, end = part.split(":")
                    try:
                        start_i = int(start)
                        end_i = int(end)
                        if start_i <= end_i:
                            for e in range(start_i, end_i + 1):
                                emu_list.append(e)
                    except:
                        pass
                else:
                    try:
                        emu_list.append(int(part))
                    except:
                        pass
        except Exception as e:
            self.log_error(f"Ошибка при парсинге строки эмуляторов: {e}")

        return emu_list