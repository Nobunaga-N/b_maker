# b_maker/src/main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger


def main() -> None:
    # Создаём папку для логов, если её нет
    os.makedirs('logs', exist_ok=True)

    # Настройка логирования (пример)
    logger = setup_logger("b_maker_logger", "logs/b_maker.log")
    logger.info("Запуск приложения b_maker")

    # Инициализация приложения PyQt
    app = QApplication(sys.argv)

    # === ЗАГРУЗКА СТИЛЯ (QSS) ===
    style_path = "assets/styles/dark_orange.qss"
    print("Current working directory:", os.getcwd())
    print("Looking for style file at:", os.path.abspath(style_path))
    if os.path.exists(style_path):
        print("Style file found.")
    else:
        print("Style file NOT found.")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            qss = f.read()
            app.setStyleSheet(qss)
    else:
        logger.warning(f"Файл стилей не найден: {style_path}")

    # Создаём и показываем главное окно
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
