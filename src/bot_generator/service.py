from typing import List, Tuple, Dict, Optional, Union, Any
import logging
import datetime
from src.bot_generator.code_generator import BotCodeGenerator
from src.bot_generator.bot_runner import BotRunner
from src.bot_generator.scheduler import BotScheduler
from src.bot_generator.image_processor import ImageProcessor



class BotMakerService:
    """
    Сервисный класс для интеграции всех компонентов и взаимодействия с UI.
    """

    def __init__(self, templates_dir: str = "templates", logger=None):
        """
        Инициализирует сервис BOT Maker.

        Args:
            templates_dir: Путь к директории с шаблонами.
            logger: Объект логгера.
        """
        self.logger = logger or logging.getLogger("BotMakerService")

        # Инициализируем компоненты
        self.code_generator = BotCodeGenerator(templates_dir)
        self.bot_runner = BotRunner(logger)
        self.scheduler = BotScheduler(self.bot_runner, logger)
        self.image_processor = ImageProcessor(logger=logger)

        # Запускаем планировщик
        self.scheduler.start_scheduler()

        self.logger.info("Сервис BOT Maker инициализирован")

    def generate_and_save_bot_code(self, bot_name: str, bot_config: Dict[str, Any]) -> str:
        """
        Генерирует и сохраняет код бота.

        Args:
            bot_name: Имя бота.
            bot_config: Конфигурация бота.

        Returns:
            Путь к сгенерированному файлу бота.
        """
        try:
            # Генерируем код
            code = self.code_generator.generate_bot_code(bot_config)

            # Сохраняем код
            file_path = self.code_generator.save_generated_code(bot_name, code)

            self.logger.info(f"Код для бота {bot_name} сгенерирован и сохранен в {file_path}")

            return file_path

        except Exception as e:
            self.logger.error(f"Ошибка при генерации кода для бота {bot_name}: {str(e)}")
            raise

    def add_bot_to_queue(self, bot_name: str, bot_path: str, emulator_id: str,
                         scheduled_time: Optional[datetime] = None,
                         cycles: int = 0, max_work_time: int = 0,
                         params: Dict[str, Any] = None) -> str:
        """
        Добавляет бота в очередь для выполнения.

        Args:
            bot_name: Имя бота.
            bot_path: Путь к файлу бота.
            emulator_id: ID эмулятора.
            scheduled_time: Время запуска. Если None, бот будет запущен при первой возможности.
            cycles: Количество циклов выполнения (0 = бесконечно).
            max_work_time: Максимальное время работы в минутах (0 = неограниченно).
            params: Дополнительные параметры для передачи боту.

        Returns:
            ID задачи в очереди.
        """
        bot_config = {
            "name": bot_name,
            "path": bot_path,
            "emulator_id": emulator_id,
            "cycles": cycles,
            "max_work_time": max_work_time,
            "params": params or {}
        }

        return self.scheduler.add_to_queue(bot_config, scheduled_time)

    def remove_bot_from_queue(self, task_id: str) -> bool:
        """
        Удаляет бота из очереди.

        Args:
            task_id: ID задачи для удаления.

        Returns:
            True, если задача найдена и удалена, иначе False.
        """
        return self.scheduler.remove_from_queue(task_id)

    def get_queue(self) -> List[Dict[str, Any]]:
        """
        Возвращает список задач в очереди.

        Returns:
            Список конфигураций задач.
        """
        return self.scheduler.get_queue()

    def get_running_bots(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает информацию о работающих ботах.

        Returns:
            Словарь {bot_id: status_info}
        """
        return self.bot_runner.get_all_bots_status()

    def stop_bot(self, bot_id: str) -> bool:
        """
        Останавливает работу бота.

        Args:
            bot_id: ID бота.

        Returns:
            True, если бот успешно остановлен, иначе False.
        """
        return self.bot_runner.stop_bot(bot_id)

    def shutdown(self):
        """
        Завершает работу сервиса.
        """
        # Останавливаем планировщик
        self.scheduler.stop_scheduler()

        # Останавливаем всех ботов
        for bot_id in list(self.bot_runner.running_bots.keys()):
            self.bot_runner.stop_bot(bot_id)

        self.logger.info("Сервис BOT Maker остановлен")