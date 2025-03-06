# b_maker/src/gui/manager.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, \
    QHBoxLayout
import logging
from PyQt6.QtGui import QFont, QIcon


class BotManager(QMainWindow):
    """
    Менеджер для управления ботами.
    Позволяет запускать, останавливать и редактировать ботов, а также управлять очередями и потоками.
    """

    def __init__(self, logger: logging.Logger, parent=None) -> None:
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("Менеджер ботов - b_maker")
        self.setGeometry(200, 200, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        self.title_label = QLabel("Менеджер ботов")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        main_layout.addWidget(self.title_label)

        # Список ботов
        self.bot_list = QListWidget()
        main_layout.addWidget(QLabel("Список ботов:"))
        main_layout.addWidget(self.bot_list)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton(" Запустить")
        self.btn_stop = QPushButton(" Остановить")
        self.btn_edit = QPushButton(" Редактировать")

        # Пример иконок
        self.btn_start.setIcon(QIcon("assets/icons/start_icon.png"))
        self.btn_stop.setIcon(QIcon("assets/icons/stop_icon.png"))
        self.btn_edit.setIcon(QIcon("assets/icons/edit_icon.png"))

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_edit)
        main_layout.addLayout(btn_layout)

        # Подключение сигналов
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_edit.clicked.connect(self.edit_bot)

        self.load_bots()

    def load_bots(self) -> None:
        """
        Загружает список существующих ботов.
        """
        try:
            # Пример статического списка
            bots = ["Бот_1", "Бот_2", "Бот_3"]
            self.bot_list.addItems(bots)
            self.logger.info("Список ботов загружен")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке ботов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список ботов: {e}")

    def start_bot(self) -> None:
        """
        Запускает выбранного бота.
        """
        selected_items = self.bot_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите бота для запуска.")
            return
        bot_name = selected_items[0].text()
        try:
            self.logger.info(f"Запуск бота: {bot_name}")
            QMessageBox.information(self, "Запуск", f"Бот '{bot_name}' запущен!")
        except Exception as e:
            self.logger.error(f"Ошибка при запуске бота {bot_name}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить бота {bot_name}: {e}")

    def stop_bot(self) -> None:
        """
        Останавливает выбранного бота.
        """
        selected_items = self.bot_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите бота для остановки.")
            return
        bot_name = selected_items[0].text()
        try:
            self.logger.info(f"Остановка бота: {bot_name}")
            QMessageBox.information(self, "Остановка", f"Бот '{bot_name}' остановлен!")
        except Exception as e:
            self.logger.error(f"Ошибка при остановке бота {bot_name}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось остановить бота {bot_name}: {e}")

    def edit_bot(self) -> None:
        """
        Открывает редактор для выбранного бота.
        """
        selected_items = self.bot_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите бота для редактирования.")
            return
        bot_name = selected_items[0].text()
        try:
            self.logger.info(f"Редактирование бота: {bot_name}")
            QMessageBox.information(self, "Редактирование", f"Открыт редактор для бота '{bot_name}'!")
        except Exception as e:
            self.logger.error(f"Ошибка при редактировании бота {bot_name}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть редактор для бота {bot_name}: {e}")
