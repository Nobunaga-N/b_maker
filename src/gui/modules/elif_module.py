# src/gui/modules/elif_module.py
"""
Модуль для подмодуля ELIF, используемого в модуле поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.gui.modules.if_result_module import IfResultCanvas


class ElifModuleDialog(QDialog):
    """
    Диалог для настройки подмодуля ELIF.
    Позволяет выбрать конкретное изображение, настроить сообщение и действия.
    """

    def __init__(self, images_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка блока ELIF")
        self.setModal(True)
        self.resize(800, 600)

        self.images_list = images_list  # Список доступных изображений
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)

        # Добавляем WindowMinMaxButtonsHint для стандартных кнопок окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)

        # --- 1. Настройки изображения и основных параметров ---
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout(settings_group)

        # Выбор изображения (для ELIF обязательно выбрать конкретное изображение)
        image_layout = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        self.image_combo = QComboBox()
        self.image_combo.addItems(self.images_list)

        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_combo, 1)
        settings_layout.addLayout(image_layout)

        # Сообщение в консоль
        log_layout = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        self.log_input = QLineEdit()
        self.log_input.setText("Найдено другое изображение!")
        self.log_input.setPlaceholderText("Например: Найдено изображение поражения!")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_input, 1)
        settings_layout.addLayout(log_layout)

        layout.addWidget(settings_group)

        # --- 2. Холст для дополнительных действий ---
        action_group = QGroupBox("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)

        self.canvas = IfResultCanvas(self)  # Используем тот же холст, что и для IF Result
        action_layout.addWidget(self.canvas)

        layout.addWidget(action_group)

        # --- 3. Кнопки диалога ---
        buttons_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn = QPushButton("Подтвердить")

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.ok_btn)

        layout.addLayout(buttons_layout)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        # Для ELIF изображение обязательно
        if self.image_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать изображение для блока ELIF")
            return None

        image = self.image_combo.currentText()

        data = {
            "type": "elif",
            "image": image,
            "log_event": self.log_input.text(),
            "actions": self.canvas.get_modules_data()
        }

        return data

    def load_data(self, data):
        """Загружает данные для редактирования"""
        # Изображение
        if data.get("image"):
            index = self.image_combo.findText(data["image"])
            if index >= 0:
                self.image_combo.setCurrentIndex(index)

        # Сообщение в консоль
        if "log_event" in data:
            self.log_input.setText(data["log_event"])

        # Загружаем действия в холст
        if "actions" in data:
            self.canvas.load_modules_data(data["actions"])