# b_maker/src/gui/editor.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QListWidget, \
    QListWidgetItem, QHBoxLayout
import logging
from src.utils.file_manager import create_bot_environment
from src.gui.custom_widgets import ClickModuleDialog


class BotEditor(QMainWindow):
    """
    Редактор сценариев ботов.
    Позволяет создавать и редактировать скрипты ботов с помощью рабочего холста и встроенных модулей.
    """

    def __init__(self, logger: logging.Logger, parent=None) -> None:
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("Редактор ботов - b_maker")
        self.setGeometry(150, 150, 1000, 700)

        # Основной виджет и компоновка
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Элементы для создания нового бота
        top_layout = QHBoxLayout()
        self.label = QLabel("Название бота:")
        self.bot_name_input = QLineEdit()
        self.create_bot_button = QPushButton("Создать нового бота")
        self.create_bot_button.clicked.connect(self.create_bot)
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.bot_name_input)
        top_layout.addWidget(self.create_bot_button)

        main_layout.addLayout(top_layout)

        # Рабочий холст для добавления модулей (используем QListWidget для демонстрации последовательности модулей)
        self.modules_list = QListWidget()
        self.modules_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        main_layout.addWidget(self.modules_list)

        # Кнопки для управления модулями
        btn_layout = QHBoxLayout()
        self.btn_add_click = QPushButton("Добавить модуль клика")
        self.btn_remove_module = QPushButton("Удалить выбранный модуль")
        self.btn_generate_script = QPushButton("Сгенерировать скрипт")
        btn_layout.addWidget(self.btn_add_click)
        btn_layout.addWidget(self.btn_remove_module)
        btn_layout.addWidget(self.btn_generate_script)
        main_layout.addLayout(btn_layout)

        # Подключение сигналов
        self.btn_add_click.clicked.connect(self.add_click_module)
        self.btn_remove_module.clicked.connect(self.remove_module)
        self.btn_generate_script.clicked.connect(self.generate_script)

        # Хранение данных модулей
        self.modules_data = []

    def create_bot(self) -> None:
        """
        Создает нового бота, формируя необходимую файловую структуру.
        """
        bot_name = self.bot_name_input.text().strip()
        if not bot_name:
            QMessageBox.warning(self, "Внимание", "Введите название бота.")
            return
        try:
            create_bot_environment(bot_name)
            self.logger.info(f"Создан бот: {bot_name}")
            QMessageBox.information(self, "Успех", f"Бот '{bot_name}' успешно создан!")
        except Exception as e:
            self.logger.error(f"Ошибка при создании бота: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать бота: {e}")

    def add_click_module(self) -> None:
        """
        Добавляет модуль клика в рабочий холст.
        Открывает диалог для ввода параметров модуля.
        """
        dialog = ClickModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            # Преобразуем данные (например, x и y в int, sleep в float)
            try:
                module_data = {
                    "type": "click",
                    "x": int(data.get("x", 0)),
                    "y": int(data.get("y", 0)),
                    "description": data.get("description", ""),
                    "console_description": data.get("console_description", ""),
                    "sleep": float(data.get("sleep", 0.0))
                }
                self.modules_data.append(module_data)
                item_text = f"Клик: ({module_data['x']}, {module_data['y']}) - {module_data['description']}"
                self.modules_list.addItem(item_text)
                self.logger.info(f"Добавлен модуль клика: {item_text}")
            except Exception as e:
                self.logger.error(f"Ошибка обработки данных модуля клика: {e}")
                QMessageBox.critical(self, "Ошибка", f"Данные модуля введены некорректно: {e}")

    def remove_module(self) -> None:
        """
        Удаляет выбранный модуль с холста.
        """
        selected_items = self.modules_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите модуль для удаления.")
            return
        for item in selected_items:
            index = self.modules_list.row(item)
            self.modules_list.takeItem(index)
            del self.modules_data[index]
            self.logger.info(f"Удалён модуль с индекса {index}")

    def generate_script(self) -> None:
        """
        Генерирует скрипт на основе добавленных модулей.
        """
        from src.bots.script_generator import generate_script
        try:
            script = generate_script(self.modules_data)
            self.logger.info("Скрипт сгенерирован:\n" + script)
            # Здесь можно вывести сгенерированный скрипт в отдельном окне или сохранить в файл
            QMessageBox.information(self, "Скрипт сгенерирован", script)
        except Exception as e:
            self.logger.error(f"Ошибка генерации скрипта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать скрипт: {e}")
