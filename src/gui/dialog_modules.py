# src/gui/dialog_modules.py
"""
Модуль содержит базовые диалоги для настройки модулей ботов.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from typing import Dict, Any

from src.utils.style_constants import DIALOG_STYLE


# Скопируйте сюда классы ClickModuleDialog и SwipeModuleDialog из custom_widgets.py
class ClickModuleDialog(QDialog):
    """
    Диалог для настройки модуля клика.
    Позволяет задать координаты, описание и время задержки после клика.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля клика")
        self.setModal(True)
        self.resize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Используем стиль из констант
        self.setStyleSheet(DIALOG_STYLE)

        coords_group = QGroupBox("Координаты клика")
        coords_layout = QVBoxLayout(coords_group)

        # Координата X с использованием QSpinBox
        x_layout = QHBoxLayout()
        x_label = QLabel("Координата X:")
        self.x_input = QSpinBox()
        self.x_input.setRange(0, 5000)
        self.x_input.setSingleStep(1)
        self.x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_input)
        coords_layout.addLayout(x_layout)

        # Координата Y с использованием QSpinBox
        y_layout = QHBoxLayout()
        y_label = QLabel("Координата Y:")
        self.y_input = QSpinBox()
        self.y_input.setRange(0, 5000)
        self.y_input.setSingleStep(1)
        self.y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_input)
        coords_layout.addLayout(y_layout)

        layout.addWidget(coords_group)

        # Описания
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QVBoxLayout(descriptions_group)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addWidget(QLabel("Описание:"))
        descriptions_layout.addWidget(self.description_input)

        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addWidget(QLabel("Описание для консоли:"))
        descriptions_layout.addWidget(self.console_description_input)

        layout.addWidget(descriptions_group)

        # Задержка
        delay_group = QGroupBox("Задержка")
        delay_layout = QHBoxLayout(delay_group)

        delay_label = QLabel("Время задержки после клика:")
        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 60.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        self.sleep_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.sleep_input)

        layout.addWidget(delay_group)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)

        layout.addLayout(buttons_layout)

    def get_data(self) -> Dict[str, Any]:
        """
        Возвращает данные, введенные пользователем.
        """
        return {
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.value()
        }


class SwipeModuleDialog(QDialog):
    """
    Диалог для настройки модуля свайпа.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля свайпа")
        self.setModal(True)
        self.resize(450, 400)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога свайпа"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Применяем стиль из констант
        self.setStyleSheet(DIALOG_STYLE)

        # Координаты начала свайпа
        start_group = QGroupBox("Начальные координаты")
        start_layout = QVBoxLayout(start_group)

        hbox_start_x = QHBoxLayout()
        x_label = QLabel("Координата X:")
        self.start_x_input = QSpinBox()
        self.start_x_input.setRange(0, 5000)
        self.start_x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        hbox_start_x.addWidget(x_label)
        hbox_start_x.addWidget(self.start_x_input)

        hbox_start_y = QHBoxLayout()
        y_label = QLabel("Координата Y:")
        self.start_y_input = QSpinBox()
        self.start_y_input.setRange(0, 5000)
        self.start_y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        hbox_start_y.addWidget(y_label)
        hbox_start_y.addWidget(self.start_y_input)

        start_layout.addLayout(hbox_start_x)
        start_layout.addLayout(hbox_start_y)
        layout.addWidget(start_group)

        # Координаты конца свайпа
        end_group = QGroupBox("Конечные координаты")
        end_layout = QVBoxLayout(end_group)

        hbox_end_x = QHBoxLayout()
        end_x_label = QLabel("Координата X:")
        self.end_x_input = QSpinBox()
        self.end_x_input.setRange(0, 5000)
        self.end_x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        hbox_end_x.addWidget(end_x_label)
        hbox_end_x.addWidget(self.end_x_input)

        hbox_end_y = QHBoxLayout()
        end_y_label = QLabel("Координата Y:")
        self.end_y_input = QSpinBox()
        self.end_y_input.setRange(0, 5000)
        self.end_y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        hbox_end_y.addWidget(end_y_label)
        hbox_end_y.addWidget(self.end_y_input)

        end_layout.addLayout(hbox_end_x)
        end_layout.addLayout(hbox_end_y)
        layout.addWidget(end_group)

        # Описания
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QVBoxLayout(descriptions_group)

        desc_label = QLabel("Описание:")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addWidget(desc_label)
        descriptions_layout.addWidget(self.description_input)

        console_desc_label = QLabel("Описание для консоли:")
        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addWidget(console_desc_label)
        descriptions_layout.addWidget(self.console_description_input)

        layout.addWidget(descriptions_group)

        # Задержка
        delay_group = QGroupBox("Задержка")
        delay_layout = QHBoxLayout(delay_group)

        sleep_label = QLabel("Время задержки после свайпа:")
        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 60.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        self.sleep_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        delay_layout.addWidget(sleep_label)
        delay_layout.addWidget(self.sleep_input)

        layout.addWidget(delay_group)

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        return {
            "type": "swipe",
            "x1": self.start_x_input.value(),
            "y1": self.start_y_input.value(),
            "x2": self.end_x_input.value(),
            "y2": self.end_y_input.value(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.value()
        }