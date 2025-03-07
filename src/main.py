# src/main.py
"""
Главный модуль приложения b_maker для создания ботов мобильных игр.
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.utils.resources import Resources
from src.utils.exceptions import BotMakerError

# Константы
APP_NAME = "BOT Maker"
APP_VERSION = "0.1.0"
DEFAULT_STYLE = "dark_orange"


def setup_directories():
    """Создает необходимые директории для работы приложения"""
    # Создаем директории, если их нет
    Resources.ensure_dir_exists("logs")
    Resources.ensure_dir_exists("bots")
    Resources.ensure_dir_exists("config")
    Resources.ensure_dir_exists(Resources.ASSETS_DIR)
    Resources.ensure_dir_exists(Resources.ICONS_DIR)
    Resources.ensure_dir_exists(Resources.STYLES_DIR)


def setup_exception_hook(logger):
    """Настраивает глобальный обработчик исключений"""

    def exception_hook(exc_type, exc_value, exc_traceback):
        """Обрабатывает непойманные исключения"""
        # Выводим в лог
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        logger.error(f"Непойманное исключение:\n{tb_text}")

        # Выводим сообщение для пользователя
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText("Произошла непредвиденная ошибка")
        error_box.setInformativeText(str(exc_value))
        error_box.setDetailedText(tb_text)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.exec()

        # Вызываем стандартный обработчик
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # Устанавливаем обработчик
    sys.excepthook = exception_hook


def main() -> None:
    """Основная функция запуска приложения"""
    # Создаём необходимые директории
    setup_directories()

    # Настройка логирования
    logger = setup_logger("b_maker_logger", "logs/b_maker.log")
    logger.info(f"Запуск приложения {APP_NAME} v{APP_VERSION}")

    # Настройка обработчика исключений
    setup_exception_hook(logger)

    # Инициализация приложения PyQt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # Установка иконки приложения
    icon_path = Resources.get_icon_path("app_icon")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Загрузка стиля приложения
    style_path = Resources.get_style_path(DEFAULT_STYLE)
    if os.path.exists(style_path):
        logger.info(f"Загрузка стиля: {style_path}")
        with open(style_path, "r", encoding="utf-8") as f:
            qss = f.read()
            app.setStyleSheet(qss)
    else:
        logger.warning(f"Файл стилей не найден: {style_path}")

    try:
        # Создаём и показываем главное окно
        main_window = MainWindow(logger)
        main_window.show()

        # Запускаем цикл обработки событий
        sys.exit(app.exec())
    except BotMakerError as e:
        logger.error(f"Ошибка приложения: {e}")
        QMessageBox.critical(None, "Ошибка", f"Критическая ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        QMessageBox.critical(None, "Ошибка", f"Непредвиденная ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()