# src/gui/dialog_modules.py
"""
Модуль содержит базовые диалоги для настройки модулей ботов.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QFormLayout
)
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional

from src.utils.style_constants import MODULE_DIALOG_STYLE, MODULE_BUTTON_STYLE, FORM_GROUP_STYLE
from src.utils.ui_factory import (
    create_input_field,
    create_spinbox_without_buttons, create_double_spinbox_without_buttons,
    create_group_box
)
from src.utils.resources import Resources


class BaseModuleDialog(QDialog):
    """
    Базовый класс для диалогов модулей.
    Предоставляет общую структуру и стилизацию для всех диалогов настройки модулей.
    """

    def __init__(self, parent=None, title="Настройка модуля", width=350, height=300):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(width, height)
        self.setStyleSheet(MODULE_DIALOG_STYLE)
        self.setup_base_ui()

    def setup_base_ui(self):
        """Настраивает базовый интерфейс диалога"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

    def create_form_group(self, title: str) -> tuple:
        """Создает группу с FormLayout для компактного размещения элементов формы"""
        group = create_group_box(title)
        form_layout = QFormLayout(group)
        form_layout.setContentsMargins(6, 12, 6, 6)  # Увеличиваем верхний отступ для заголовка
        form_layout.setSpacing(4)
        self.main_layout.addWidget(group)
        return group, form_layout

    def add_buttons(self):
        """Добавляет стандартные кнопки Отмена/Подтвердить"""
        buttons_layout = QHBoxLayout()

        # Создаем кнопки напрямую с правильным стилем
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")

        # Применяем нужный стиль для сохранения оранжевого цвета #FFA500
        self.btn_cancel.setStyleSheet(MODULE_BUTTON_STYLE)
        self.btn_confirm.setStyleSheet(MODULE_BUTTON_STYLE)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)

        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)

        self.main_layout.addLayout(buttons_layout)

    def get_data(self) -> Dict[str, Any]:
        """
        Базовый метод для получения данных из диалога.
        Должен быть переопределен в дочерних классах.
        """
        return {}

    def load_data(self, data: Dict[str, Any]):
        """
        Базовый метод для загрузки данных в диалог.
        Должен быть переопределен в дочерних классах.
        """
        pass


class ClickModuleDialog(BaseModuleDialog):
    """
    Оптимизированный диалог для настройки модуля клика.
    """

    def __init__(self, parent=None):
        super().__init__(parent, "Настройка клика", 350, 300)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        # Группа координат
        coords_group, coords_layout = self.create_form_group("Координаты клика")

        # Координата X
        self.x_input = create_spinbox_without_buttons(0, 5000, 0)
        coords_layout.addRow("Координата X:", self.x_input)

        # Координата Y
        self.y_input = create_spinbox_without_buttons(0, 5000, 0)
        coords_layout.addRow("Координата Y:", self.y_input)

        # Группа описаний
        desc_group, desc_layout = self.create_form_group("Описания")

        self.description_input = create_input_field("Описание для отображения на холсте")
        desc_layout.addRow("Описание:", self.description_input)

        self.console_description_input = create_input_field("Описание для вывода в консоль")
        desc_layout.addRow("Описание для консоли:", self.console_description_input)

        # Группа задержки
        delay_group, delay_layout = self.create_form_group("Задержка")

        self.sleep_input = create_double_spinbox_without_buttons(0.0, 300.0, 0.0, 1, " сек")
        delay_layout.addRow("Время задержки после клика:", self.sleep_input)

        # Добавляем кнопки
        self.add_buttons()

    def get_data(self) -> Dict[str, Any]:
        """
        Возвращает данные, введенные пользователем.
        """
        return {
            "type": "click",
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.value()
        }

    def load_data(self, data: Dict[str, Any]):
        """
        Загружает данные для редактирования.
        """
        if isinstance(data.get("x"), (int, float)):
            self.x_input.setValue(int(data.get("x", 0)))
        if isinstance(data.get("y"), (int, float)):
            self.y_input.setValue(int(data.get("y", 0)))
        if data.get("description") is not None:
            self.description_input.setText(str(data.get("description", "")))
        if data.get("console_description") is not None:
            self.console_description_input.setText(str(data.get("console_description", "")))
        if isinstance(data.get("sleep"), (int, float)):
            self.sleep_input.setValue(float(data.get("sleep", 0.0)))


class SwipeModuleDialog(BaseModuleDialog):
    """
    Оптимизированный диалог для настройки модуля свайпа.
    """

    def __init__(self, parent=None):
        super().__init__(parent, "Настройка свайпа", 350, 350)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога свайпа"""
        # Координаты начала свайпа
        start_group, start_layout = self.create_form_group("Начальные координаты")

        # X
        self.start_x_input = create_spinbox_without_buttons(0, 5000, 0)
        start_layout.addRow("Координата X:", self.start_x_input)

        # Y
        self.start_y_input = create_spinbox_without_buttons(0, 5000, 0)
        start_layout.addRow("Координата Y:", self.start_y_input)

        # Координаты конца свайпа
        end_group, end_layout = self.create_form_group("Конечные координаты")

        # X
        self.end_x_input = create_spinbox_without_buttons(0, 5000, 0)
        end_layout.addRow("Координата X:", self.end_x_input)

        # Y
        self.end_y_input = create_spinbox_without_buttons(0, 5000, 0)
        end_layout.addRow("Координата Y:", self.end_y_input)

        # Описания
        desc_group, desc_layout = self.create_form_group("Описания")

        self.description_input = create_input_field("Описание для отображения на холсте")
        desc_layout.addRow("Описание:", self.description_input)

        self.console_description_input = create_input_field("Описание для вывода в консоль")
        desc_layout.addRow("Описание для консоли:", self.console_description_input)

        # Задержка
        delay_group, delay_layout = self.create_form_group("Задержка")

        self.sleep_input = create_double_spinbox_without_buttons(0.0, 300.0, 0.0, 1, " сек")
        delay_layout.addRow("Время задержки после свайпа:", self.sleep_input)

        # Кнопки
        self.add_buttons()

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

    def load_data(self, data: Dict[str, Any]):
        """
        Загружает данные для редактирования.
        """
        if isinstance(data.get("x1"), (int, float)):
            self.start_x_input.setValue(int(data.get("x1", 0)))
        if isinstance(data.get("y1"), (int, float)):
            self.start_y_input.setValue(int(data.get("y1", 0)))
        if isinstance(data.get("x2"), (int, float)):
            self.end_x_input.setValue(int(data.get("x2", 0)))
        if isinstance(data.get("y2"), (int, float)):
            self.end_y_input.setValue(int(data.get("y2", 0)))
        if data.get("description") is not None:
            self.description_input.setText(str(data.get("description", "")))
        if data.get("console_description") is not None:
            self.console_description_input.setText(str(data.get("console_description", "")))
        if isinstance(data.get("sleep"), (int, float)):
            self.sleep_input.setValue(float(data.get("sleep", 0.0)))


class TimeSleepModuleDialog(BaseModuleDialog):
    """
    Оптимизированный диалог для настройки модуля паузы.
    """

    def __init__(self, parent=None):
        super().__init__(parent, "Настройка паузы", 300, 180)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        # Группа параметров паузы
        delay_group, delay_layout = self.create_form_group("Параметры паузы")

        # Время задержки
        self.delay_input = create_double_spinbox_without_buttons(0.1, 300.0, 1.0, 1, " сек")
        delay_layout.addRow("Время задержки:", self.delay_input)

        # Описание
        self.description_input = create_input_field("Необязательное описание паузы")
        delay_layout.addRow("Описание:", self.description_input)

        # Кнопки
        self.add_buttons()

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