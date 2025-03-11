# src/gui/modules/if_result_module.py - оптимизированная версия
"""
Модуль для подмодуля IF Result, используемого в модуле поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt

from src.gui.modules.canvas_module import CanvasModule
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.utils.resources import Resources
from src.utils.ui_factory import (
    create_script_button, create_group_box, create_input_field
)
from src.gui.modules.script_block_base import ScriptBlockDialog
from src.utils.style_constants import (
    SCRIPT_SUBMODULE_BUTTON_STYLE,SCRIPT_SUBMODULE_CANVAS_STYLE, SCRIPT_DIALOG_BLUE_STYLE
)


class IfResultCanvas(CanvasModule):
    """
    Холст для создания логики IF Result.
    Наследуется от универсального холста и добавляет специфические модули.
    """

    def __init__(self, parent=None):
        super().__init__("Редактор логики IF Result", parent)
        self.setStyleSheet(SCRIPT_SUBMODULE_CANVAS_STYLE)  # Применяем новый стиль


    def create_tool_buttons(self, layout):
        """Создает кнопки инструментов для холста IF Result"""
        # Кнопка добавления клика
        self.btn_add_click = create_script_button(
            "Добавить клик",
            "Добавить клик по координатам",
            "pointer-arrow-icon",
            self.add_click_module
        )
        self.btn_add_click.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_click)

        # Кнопка добавления свайпа
        self.btn_add_swipe = create_script_button(
            "Добавить свайп",
            "Добавить свайп по координатам",
            "swipe-black",
            self.add_swipe_module
        )
        self.btn_add_swipe.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_swipe)

        # Кнопка добавления get_coords
        self.btn_add_get_coords = create_script_button(
            "get_coords",
            "Клик по найденным координатам",
            "get-coords",
            self.add_get_coords_module
        )
        self.btn_add_get_coords.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_get_coords)

        # Кнопка добавления паузы
        self.btn_add_sleep = create_script_button(
            "time_sleep",
            "Добавить паузу",
            "pause-black",
            self.add_sleep_module
        )
        self.btn_add_sleep.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_sleep)

        # Кнопка добавления continue
        self.btn_add_continue = create_script_button(
            "continue",
            "Продолжить выполнение",
            "continue-black",
            self.add_continue_module
        )
        self.btn_add_continue.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_continue)

        # Кнопка добавления running.clear()
        self.btn_add_running_clear = create_script_button(
            "running.clear()",
            "Остановить выполнение бота",
            "stop-black",
            self.add_running_clear_module
        )
        self.btn_add_running_clear.setStyleSheet(SCRIPT_SUBMODULE_BUTTON_STYLE)
        layout.addWidget(self.btn_add_running_clear)

        layout.addStretch(1)  # Растягивающееся пространство в конце

    def add_click_module(self):
        """Добавляет модуль клика на холст"""
        dialog = ClickModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            description = f"Клик по координатам ({data['x']}, {data['y']})"
            if data.get('description'):
                description += f" - {data['description']}"
            if data.get('sleep') > 0:
                description += f" с задержкой {data['sleep']} сек"

            self.add_module("Клик", description, data)

    def add_swipe_module(self):
        """Добавляет модуль свайпа на холст"""
        dialog = SwipeModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            description = f"Свайп ({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']})"
            if data.get('description'):
                description += f" - {data['description']}"
            if data.get('sleep') > 0:
                description += f" с задержкой {data['sleep']} сек"

            self.add_module("Свайп", description, data)

    def add_get_coords_module(self):
        """Добавляет модуль get_coords на холст"""
        description = "Клик по координатам найденного изображения"
        data = {"type": "get_coords"}
        self.add_module("get_coords", description, data)

    def add_sleep_module(self):
        """Добавляет модуль паузы на холст"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)
        dialog.resize(300, 150)
        dialog.setStyleSheet(SCRIPT_DIALOG_BLUE_STYLE)

        layout = QVBoxLayout(dialog)

        # Спиннер для времени
        input_layout = QHBoxLayout()
        time_label = QLabel("Время задержки (сек):")
        time_spinner = QDoubleSpinBox()
        time_spinner.setRange(0.1, 300.0)
        time_spinner.setValue(1.0)
        time_spinner.setDecimals(1)
        time_spinner.setSingleStep(0.1)
        time_spinner.setSuffix(" сек")
        time_spinner.setStyleSheet("""
            background-color: #283A5A;
            color: white;
            border: 1px solid #4C7BD9;
        """)

        input_layout.addWidget(time_label)
        input_layout.addWidget(time_spinner)

        layout.addLayout(input_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("ОК")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)

        layout.addLayout(buttons_layout)

        if dialog.exec():
            time_value = time_spinner.value()
            description = f"Пауза {time_value} сек"
            data = {"type": "time_sleep", "time": time_value}
            self.add_module("Пауза", description, data)

    def add_continue_module(self):
        """Добавляет модуль continue на холст"""
        description = "Продолжить выполнение скрипта (continue)"
        data = {"type": "continue"}
        self.add_module("continue", description, data)

    def add_running_clear_module(self):
        """Добавляет модуль running.clear() на холст"""
        description = "Остановить выполнение бота (running.clear())"
        data = {"type": "running_clear"}
        self.add_module("running.clear()", description, data)


class IfResultModuleDialog(ScriptBlockDialog):
    """
    Диалог для настройки подмодуля IF Result.
    Позволяет выбрать изображение, настроить сообщение и действия.
    """

    def __init__(self, images_list, parent=None):
        self.images_list = images_list  # Список доступных изображений
        super().__init__("Настройка блока IF Result", parent)

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        # Инициализируем базовый layout напрямую
        self.layout = QVBoxLayout(self)

        # --- 1. Настройки изображения и основных параметров ---
        settings_group, settings_layout = self.setup_settings_group()

        # Выбор изображения
        image_layout = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        self.image_combo = QComboBox()
        self.image_combo.addItem("Любое найденное изображение")
        self.image_combo.addItems(self.images_list)

        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_combo, 1)

        # Вставляем выбор изображения перед сообщением в консоль
        settings_layout.insertLayout(0, image_layout)

        # --- 2. Холст для дополнительных действий ---
        self.setup_canvas()

        # --- 3. Кнопки диалога (добавляем в конце) ---
        self.setup_buttons()

    def setup_canvas(self):
        """Создает холст для действий"""
        action_group = create_group_box("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)

        self.canvas = IfResultCanvas(self)
        action_layout.addWidget(self.canvas)

        self.layout.addWidget(action_group)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        image = None
        if self.image_combo.currentIndex() > 0:
            image = self.image_combo.currentText()

        data = super().get_data()
        data.update({
            "type": "if_result",
            "image": image
        })

        return data

    def load_data(self, data):
        """Загружает данные для редактирования"""
        super().load_data(data)

        # Изображение
        if data.get("image"):
            index = self.image_combo.findText(data["image"])
            if index >= 0:
                self.image_combo.setCurrentIndex(index)