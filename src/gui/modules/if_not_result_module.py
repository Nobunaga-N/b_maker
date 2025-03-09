# src/gui/modules/if_not_result_module.py
"""
Модуль для подмодуля IF Not Result, используемого в модуле поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.gui.modules.if_result_module import IfResultCanvas


class IfNotResultModuleDialog(QDialog):
    """
    Диалог для настройки подмодуля IF Not Result.
    Позволяет настроить сообщение и действия, когда изображения не найдены.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка блока IF Not Result")
        self.setModal(True)
        self.resize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)

        # --- 1. Настройки основных параметров ---
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout(settings_group)

        # Сообщение в консоль
        log_layout = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        self.log_input = QLineEdit()
        self.log_input.setText("Изображение не найдено!")
        self.log_input.setPlaceholderText("Например: Изображения не обнаружены!")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_input, 1)
        settings_layout.addLayout(log_layout)

        # Чекбоксы для действий
        self.continue_check = QCheckBox("Продолжить выполнение (continue)")
        self.continue_check.setChecked(True)
        self.stop_bot_check = QCheckBox("Остановить бота (running.clear())")

        settings_layout.addWidget(self.continue_check)
        settings_layout.addWidget(self.stop_bot_check)

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
        data = {
            "type": "if_not_result",
            "log_event": self.log_input.text(),
            "continue": self.continue_check.isChecked(),
            "stop_bot": self.stop_bot_check.isChecked(),
            "actions": self.canvas.get_modules_data()
        }

        return data

    def load_data(self, data):
        """Загружает данные для редактирования"""
        # Сообщение в консоль
        if "log_event" in data:
            self.log_input.setText(data["log_event"])

        # Чекбоксы
        self.continue_check.setChecked(data.get("continue", True))
        self.stop_bot_check.setChecked(data.get("stop_bot", False))

        # Загружаем действия в холст
        if "actions" in data:
            self.canvas.load_modules_data(data["actions"])