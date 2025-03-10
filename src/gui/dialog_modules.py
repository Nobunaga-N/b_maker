# src/gui/dialog_modules.py
"""
Модуль содержит базовые диалоги для настройки модулей ботов.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame, QScrollArea, QFormLayout, QToolButton
)
from PyQt6.QtCore import Qt
from typing import Dict, Any
from src.utils.style_constants import DIALOG_STYLE
from src.utils.ui_factory import create_spinbox_without_buttons, create_double_spinbox_without_buttons

# Улучшенные версии базовых диалогов для модулей

class ClickModuleDialog(QDialog):
    """
    Улучшенный компактный диалог для настройки модуля клика.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка клика")
        self.setModal(True)
        self.resize(350, 300)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Улучшенный стиль
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                color: white;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                color: #FFA500;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)

        # Группа координат (используем FormLayout для компактности)
        coords_group = QGroupBox("Координаты клика")
        coords_layout = QFormLayout(coords_group)
        coords_layout.setContentsMargins(6, 12, 6, 6)
        coords_layout.setSpacing(4)

        # Координата X
        self.x_input = QSpinBox()
        self.x_input.setRange(0, 5000)
        self.x_input.setSingleStep(1)
        self.x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        coords_layout.addRow("Координата X:", self.x_input)

        # Координата Y
        self.y_input = QSpinBox()
        self.y_input.setRange(0, 5000)
        self.y_input.setSingleStep(1)
        self.y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        coords_layout.addRow("Координата Y:", self.y_input)

        layout.addWidget(coords_group)

        # Группа описаний
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QFormLayout(descriptions_group)
        descriptions_layout.setContentsMargins(6, 12, 6, 6)
        descriptions_layout.setSpacing(4)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addRow("Описание:", self.description_input)

        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addRow("Описание для консоли:", self.console_description_input)

        layout.addWidget(descriptions_group)

        # Группа задержки
        delay_group = QGroupBox("Задержка")
        delay_layout = QFormLayout(delay_group)
        delay_layout.setContentsMargins(6, 12, 6, 6)
        delay_layout.setSpacing(4)

        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 300.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        self.sleep_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        delay_layout.addRow("Время задержки после клика:", self.sleep_input)

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
    Улучшенный компактный диалог для настройки модуля свайпа.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка свайпа")
        self.setModal(True)
        self.resize(350, 350)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога свайпа"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Улучшенный стиль (такой же, как у диалога клика)
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                color: white;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                color: #FFA500;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)

        # Координаты начала свайпа
        start_group = QGroupBox("Начальные координаты")
        start_layout = QFormLayout(start_group)
        start_layout.setContentsMargins(6, 12, 6, 6)
        start_layout.setSpacing(4)

        # X
        self.start_x_input = QSpinBox()
        self.start_x_input.setRange(0, 5000)
        self.start_x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        start_layout.addRow("Координата X:", self.start_x_input)

        # Y
        self.start_y_input = QSpinBox()
        self.start_y_input.setRange(0, 5000)
        self.start_y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        start_layout.addRow("Координата Y:", self.start_y_input)

        layout.addWidget(start_group)

        # Координаты конца свайпа
        end_group = QGroupBox("Конечные координаты")
        end_layout = QFormLayout(end_group)
        end_layout.setContentsMargins(6, 12, 6, 6)
        end_layout.setSpacing(4)

        # X
        self.end_x_input = QSpinBox()
        self.end_x_input.setRange(0, 5000)
        self.end_x_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        end_layout.addRow("Координата X:", self.end_x_input)

        # Y
        self.end_y_input = QSpinBox()
        self.end_y_input.setRange(0, 5000)
        self.end_y_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        end_layout.addRow("Координата Y:", self.end_y_input)

        layout.addWidget(end_group)

        # Описания
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QFormLayout(descriptions_group)
        descriptions_layout.setContentsMargins(6, 12, 6, 6)
        descriptions_layout.setSpacing(4)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addRow("Описание:", self.description_input)

        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addRow("Описание для консоли:", self.console_description_input)

        layout.addWidget(descriptions_group)

        # Задержка
        delay_group = QGroupBox("Задержка")
        delay_layout = QFormLayout(delay_group)
        delay_layout.setContentsMargins(6, 12, 6, 6)
        delay_layout.setSpacing(4)

        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 300.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        self.sleep_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        delay_layout.addRow("Время задержки после свайпа:", self.sleep_input)

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


class TimeSleepModuleDialog(QDialog):
    """
    Улучшенный компактный диалог для настройки модуля паузы.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка паузы")
        self.setModal(True)
        self.resize(300, 180)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Улучшенный стиль (такой же, как у других диалогов)
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                color: white;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                color: #FFA500;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 3px;
                min-height: 22px;
                max-height: 22px;
            }
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)

        # Группа параметров паузы
        delay_group = QGroupBox("Параметры паузы")
        delay_layout = QFormLayout(delay_group)
        delay_layout.setContentsMargins(6, 12, 6, 6)
        delay_layout.setSpacing(4)

        # Время задержки
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setRange(0.1, 300.0)
        self.delay_input.setValue(1.0)
        self.delay_input.setDecimals(1)
        self.delay_input.setSingleStep(0.1)
        self.delay_input.setSuffix(" сек")
        self.delay_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        delay_layout.addRow("Время задержки:", self.delay_input)

        # Описание
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Необязательное описание паузы")
        delay_layout.addRow("Описание:", self.description_input)

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
            "type": "time_sleep",
            "delay": self.delay_input.value(),
            "description": self.description_input.text().strip()
        }

    def load_data(self, data: Dict[str, Any]):
        """
        Загружает данные для редактирования.
        """
        if "delay" in data:
            self.delay_input.setValue(float(data["delay"]))
        if "description" in data:
            self.description_input.setText(data["description"])