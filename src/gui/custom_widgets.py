# src/gui/custom_widgets.py
"""
Модуль содержит пользовательские виджеты для интерфейса приложения.
"""
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.gui.image_search_module import ImageSearchModuleDialog

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import os
from typing import Dict, List, Any, Optional

# Импортируем константы стилей
from src.utils.style_constants import (
    DIALOG_STYLE, CHECKBOX_STYLE, TAB_AND_TABLE_STYLE,
    SCROLLBAR_STYLE, COMBOBOX_STYLE, FULL_DIALOG_STYLE
)


class ActivityModuleDialog(QDialog):
    """
    Диалог для настройки модуля проверки Activity.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля проверки Activity")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога Activity"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Применяем общий стиль из констант
        self.setStyleSheet(FULL_DIALOG_STYLE)

        title_label = QLabel("Настройка проверки активности игры")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFA500; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Активация модуля
        enable_group = QGroupBox("Статус модуля")
        enable_layout = QVBoxLayout(enable_group)
        self.enable_check = QCheckBox("Включить проверку активности")
        self.enable_check.setChecked(True)
        enable_layout.addWidget(self.enable_check)
        layout.addWidget(enable_group)

        # Группа с настройками
        settings_group = QGroupBox("Настройки проверки активности")
        settings_layout = QVBoxLayout(settings_group)

        # Выпадающий список с опциями
        action_label = QLabel("Действие при вылете игры:")
        settings_layout.addWidget(action_label)

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "continue_bot - Перезапустить игру и продолжить",
            "activity.running.clear(0) - Закрыть эмулятор",
            "activity.running.clear(1) - Закрыть эмулятор и запустить следующий"
        ])
        settings_layout.addWidget(self.action_combo)

        # Опции для continue_bot
        self.continue_options_group = QGroupBox("Опции для continue_bot")
        continue_layout = QVBoxLayout(self.continue_options_group)

        self.restart_emulator_check = QCheckBox("Перезапустить эмулятор (restart.emulator)")
        self.close_game_check = QCheckBox("Закрыть игру (close.game)")
        self.start_game_check = QCheckBox("Запустить игру (start.game)")
        self.start_game_check.setChecked(True)  # По умолчанию включено

        hbox_restart = QHBoxLayout()
        self.restart_from_line = QSpinBox()
        self.restart_from_line.setRange(1, 999)
        self.restart_from_line.setEnabled(False)
        self.restart_from_check = QCheckBox("Перезапустить со строки:")
        self.restart_from_check.toggled.connect(self.restart_from_line.setEnabled)
        hbox_restart.addWidget(self.restart_from_check)
        hbox_restart.addWidget(self.restart_from_line)

        self.restart_from_last_check = QCheckBox("Перезапустить с последней позиции (restart.from.last)")

        continue_layout.addWidget(self.restart_emulator_check)
        continue_layout.addWidget(self.close_game_check)
        continue_layout.addWidget(self.start_game_check)
        continue_layout.addLayout(hbox_restart)
        continue_layout.addWidget(self.restart_from_last_check)

        settings_layout.addWidget(self.continue_options_group)

        # Обработка выбора действия
        self.action_combo.currentIndexChanged.connect(self.update_ui_based_on_action)

        layout.addWidget(settings_group)

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

        # Инициализация UI согласно начальному выбору
        self.update_ui_based_on_action(0)

    def update_ui_based_on_action(self, index: int):
        """
        Обновляет UI в зависимости от выбранного действия.

        Args:
            index: Индекс выбранного действия.
        """
        self.continue_options_group.setVisible(index == 0)  # Показываем опции только для continue_bot

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        action_index = self.action_combo.currentIndex()
        action_type = ["continue_bot", "activity.running.clear(0)", "activity.running.clear(1)"][action_index]

        data = {
            "type": "activity",
            "enabled": self.enable_check.isChecked(),
            "action": action_type,
        }

        # Добавляем опции для continue_bot
        if action_type == "continue_bot":
            data["options"] = {
                "restart_emulator": self.restart_emulator_check.isChecked(),
                "close_game": self.close_game_check.isChecked(),
                "start_game": self.start_game_check.isChecked(),
                "restart_from_last": self.restart_from_last_check.isChecked(),
            }

            if self.restart_from_check.isChecked():
                data["options"]["restart_from_line"] = self.restart_from_line.value()

        return data