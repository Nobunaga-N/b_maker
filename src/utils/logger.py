# b_maker/src/utils/logger.py
import logging
from logging import Logger

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> Logger:
    """
    Настраивает и возвращает объект логгера.

    :param name: Имя логгера.
    :param log_file: Путь к файлу логов.
    :param level: Уровень логирования.
    :return: Настроенный логгер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Обработчик записи в файл
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
