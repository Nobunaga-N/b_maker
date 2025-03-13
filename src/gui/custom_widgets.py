from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QFrame,  QFormLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

import os
import json
from typing import Dict, List, Any, Optional

from src.utils.style_constants import (
    MODULE_ITEM_STYLE, TOOL_BUTTON_STYLE, ACTIVITY_CANVAS_STYLE,
    ACTIVITY_DIALOG_STYLE, ACTIVITY_MODULE_TITLE_STYLE, MODULE_BUTTON_STYLE,
    HEADER_LAYOUT_STYLE, MODULE_FRAME_STYLE, MODULE_NUMBER_STYLE, MODULE_TYPE_STYLE,
    MODULE_DESC_STYLE, BUTTON_CONTAINER_STYLE
)
from src.utils.ui_factory import (
    create_tool_button, create_accent_button, create_dark_button,
    create_group_box, create_double_spinbox_without_buttons,
    create_text_label, create_spinbox_without_buttons, create_button,
    create_frame, create_title_label, create_input_field, create_combobox
)
from src.utils.resources import Resources
from src.gui.modules.canvas_module import CanvasModule, ModuleItem
from src.utils.module_handler import ModuleHandler
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog, TimeSleepModuleDialog
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog


class ModuleListItem:
    """
    Class for representing a module in the module list.
    Used by CreateBotPage to store module information.
    """

    def __init__(self, module_type: str, display_text: str, data: Dict[str, Any]):
        self.module_type = module_type
        self.display_text = display_text
        self.data = data


class ModuleItem(QFrame):
    """
    Улучшенный элемент модуля с более компактным отображением.
    Представляет собой виджет с заголовком, описанием и кнопками управления.
    """
    editRequested = pyqtSignal(int)  # Сигнал для запроса редактирования (с индексом)
    deleteRequested = pyqtSignal(int)  # Сигнал для запроса удаления (с индексом)
    moveUpRequested = pyqtSignal(int)  # Сигнал для перемещения вверх
    moveDownRequested = pyqtSignal(int)  # Сигнал для перемещения вниз

    def __init__(self, index: int, module_type: str, description: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.module_type = module_type
        self.description = description
        self.data = {}  # Для хранения дополнительных данных
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс элемента модуля"""
        # Применяем стиль из констант
        self.setStyleSheet(MODULE_ITEM_STYLE)

        # Основной лейаут с уменьшенными отступами
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

        # Верхняя строка с типом модуля и кнопками
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)
        top_layout.setStyleSheet(HEADER_LAYOUT_STYLE)

        # Создаем номер модуля как атрибут для обновления
        self.number_label = create_text_label(f"{self.index + 1}.", MODULE_NUMBER_STYLE)
        top_layout.addWidget(self.number_label)

        # Тип модуля (жирный текст с оранжевым цветом)
        type_label = create_text_label(self.module_type, MODULE_TYPE_STYLE)
        top_layout.addWidget(type_label)

        top_layout.addStretch(1)  # Растягиваем пространство между типом и кнопками

        # Кнопки управления (компактные)
        self.move_up_btn = create_tool_button("↑", "Переместить вверх",
                                             lambda: self._move_up_requested())
        self.move_down_btn = create_tool_button("↓", "Переместить вниз",
                                               lambda: self._move_down_requested())
        self.edit_btn = create_tool_button("🖉", "Редактировать",
                                          lambda: self._edit_requested())
        self.delete_btn = create_tool_button("✕", "Удалить",
                                            lambda: self._delete_requested())

        top_layout.addWidget(self.move_up_btn)
        top_layout.addWidget(self.move_down_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(self.delete_btn)

        main_layout.addLayout(top_layout)

        # Описание модуля с меньшим шрифтом и многострочным режимом
        desc_label = create_text_label(self.description, MODULE_DESC_STYLE)
        desc_label.setWordWrap(True)
        desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(desc_label)

    def _move_up_requested(self):
        """Вспомогательный метод для эмиссии сигнала moveUpRequested"""
        self.moveUpRequested.emit(self.index)

    def _move_down_requested(self):
        """Вспомогательный метод для эмиссии сигнала moveDownRequested"""
        self.moveDownRequested.emit(self.index)

    def _edit_requested(self):
        """Вспомогательный метод для эмиссии сигнала editRequested"""
        self.editRequested.emit(self.index)

    def _delete_requested(self):
        """Вспомогательный метод для эмиссии сигнала deleteRequested"""
        self.deleteRequested.emit(self.index)

    def set_data(self, data: dict):
        """Устанавливает дополнительные данные для элемента"""
        self.data = data

    def get_data(self) -> dict:
        """Возвращает данные элемента"""
        return self.data

    def update_index(self, new_index: int):
        """Обновляет индекс модуля и его отображение"""
        self.index = new_index
        self.number_label.setText(f"{new_index + 1}.")


class ActivityCanvasModule(CanvasModule):
    """
    Улучшенный холст для создания логики обработки активности.
    Более компактный и организованный интерфейс с нумерацией модулей.
    """

    def __init__(self, parent=None):
        super().__init__("", parent)  # Убираем заголовок, т.к. он уже есть в диалоге
        self.setStyleSheet(ACTIVITY_CANVAS_STYLE)

    def create_tool_buttons(self, layout):
        """Creates tool buttons for the activity canvas"""
        # Создаем toolbar для кнопок
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(4)

        # Группа 1: Основные команды
        basic_group = create_group_box("Основные команды")
        basic_layout = QHBoxLayout(basic_group)
        basic_layout.setContentsMargins(4, 16, 4, 4)  # Увеличиваем верхний отступ для заголовка
        basic_layout.setSpacing(4)

        # Кнопки для первой группы
        self.btn_close_game = self._create_command_button("close.game", "Закрыть игру",
                                                         Resources.get_icon_path("stop-red"),
                                                         self.add_close_game_module)
        self.btn_restart_emulator = self._create_command_button("restart.emulator", "Перезапустить эмулятор",
                                                              Resources.get_icon_path("activity-blue"),
                                                              self.add_restart_emulator_module)
        self.btn_start_game = self._create_command_button("start.game", "Запустить игру",
                                                       Resources.get_icon_path("continue-green"),
                                                       self.add_start_game_module)

        basic_layout.addWidget(self.btn_close_game)
        basic_layout.addWidget(self.btn_restart_emulator)
        basic_layout.addWidget(self.btn_start_game)
        toolbar.addWidget(basic_group)

        # Группа 2: Управление выполнением
        flow_group = create_group_box("Управление выполнением")
        flow_layout = QHBoxLayout(flow_group)
        flow_layout.setContentsMargins(4, 16, 4, 4)  # Увеличиваем верхний отступ для заголовка
        flow_layout.setSpacing(4)

        # Кнопки для второй группы
        self.btn_time_sleep = self._create_command_button("time.sleep", "Пауза",
                                                        Resources.get_icon_path("pause-pink"),
                                                        self.add_time_sleep_module)
        self.btn_restart_from = self._create_command_button("restart.from", "Перезапуск с позиции",
                                                         Resources.get_icon_path("activity-blue"),
                                                         self.add_restart_from_module)
        self.btn_restart_from_last = self._create_command_button("restart.from.last", "Последняя позиция",
                                                              Resources.get_icon_path("activity-orange"),
                                                              self.add_restart_from_last_module)

        flow_layout.addWidget(self.btn_time_sleep)
        flow_layout.addWidget(self.btn_restart_from)
        flow_layout.addWidget(self.btn_restart_from_last)
        toolbar.addWidget(flow_group)

        # Группа 3: Действия
        actions_group = create_group_box("Действия")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setContentsMargins(4, 16, 4, 4)  # Увеличиваем верхний отступ для заголовка
        actions_layout.setSpacing(4)

        # Кнопки для третьей группы
        self.btn_click = self._create_command_button("Клик", "Клик по координатам",
                                                   Resources.get_icon_path("click-ping"),
                                                   self.add_click_module)
        self.btn_swipe = self._create_command_button("Свайп", "Свайп по координатам",
                                                   Resources.get_icon_path("swipe-blue"),
                                                   self.add_swipe_module)
        self.btn_image_search = self._create_command_button("Поиск", "Поиск по картинке",
                                                         Resources.get_icon_path("search-orange"),
                                                         self.add_image_search_module)

        actions_layout.addWidget(self.btn_click)
        actions_layout.addWidget(self.btn_swipe)
        actions_layout.addWidget(self.btn_image_search)
        toolbar.addWidget(actions_group)

        # Добавляем toolbar в основной layout
        layout.addLayout(toolbar)

    def _create_command_button(self, text, tooltip, icon_path, slot):
        """Создает компактную кнопку для панели инструментов"""
        return create_dark_button(text, icon_path, slot, tooltip)

    def add_module(self, module_type: str, description: str, data: dict = None):
        """Переопределяем метод для добавления нумерации модулей"""
        # Вызываем родительский метод для добавления модуля
        index = super().add_module(module_type, description, data)

        # Обновляем нумерацию всех модулей
        self._update_module_numbers()

        return index

    def _update_module_numbers(self):
        """Обновляет нумерацию всех модулей на холсте"""
        for i, module in enumerate(self.modules):
            # Обновляем индекс модуля
            module.update_index(i)

    def clear(self):
        """Очищает холст безопасным способом"""
        # Удаляем все модули с холста
        for module in self.modules:
            self.canvas_layout.removeWidget(module)
            # Скрываем модуль вместо удаления для безопасности
            module.hide()

        # Очищаем список модулей
        self.modules.clear()

        # Испускаем сигнал об изменении холста
        self.canvasChanged.emit()

    # Специализированные методы для добавления модулей с использованием ModuleHandler
    def add_close_game_module(self):
        """Adds a close.game module to the canvas"""
        description = "Закрыть игру (close.game)"
        data = {"type": "close_game"}
        self.add_module("close.game", description, data)

    def add_restart_emulator_module(self):
        """Adds a restart.emulator module to the canvas"""
        description = "Перезапустить эмулятор (restart.emulator)"
        data = {"type": "restart_emulator"}
        self.add_module("restart.emulator", description, data)

    def add_start_game_module(self):
        """Adds a start.game module to the canvas"""
        description = "Запустить игру (start.game)"
        data = {"type": "start_game"}
        self.add_module("start.game", description, data)

    def add_time_sleep_module(self):
        """Adds a time.sleep module to the canvas"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)
        dialog.resize(300, 120)
        dialog.setStyleSheet(ACTIVITY_DIALOG_STYLE)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Spinner for time
        input_layout = QHBoxLayout()
        time_label = create_text_label("Время задержки (сек):")
        time_spinner = create_double_spinbox_without_buttons(0.1, 300.0, 1.0, 1, " сек")

        input_layout.addWidget(time_label)
        input_layout.addWidget(time_spinner)
        layout.addLayout(input_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = create_button("Отмена", MODULE_BUTTON_STYLE)
        ok_btn = create_button("ОК", MODULE_BUTTON_STYLE)

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.setContentsMargins(0, 8, 0, 0)

        layout.addLayout(buttons_layout)

        if dialog.exec():
            time_value = time_spinner.value()
            description = ModuleHandler.format_module_description("time.sleep", {"time": time_value})
            data = {"type": "time_sleep", "time": time_value}
            self.add_module("time.sleep", description, data)

    def add_restart_from_module(self):
        """Adds a restart.from module to the canvas"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Перезапуск со строки")
        dialog.setModal(True)
        dialog.resize(300, 120)
        dialog.setStyleSheet(ACTIVITY_DIALOG_STYLE)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Spinner for line number
        input_layout = QHBoxLayout()
        line_label = create_text_label("Номер строки:")
        line_spinner = create_spinbox_without_buttons(1, 999, 1)

        input_layout.addWidget(line_label)
        input_layout.addWidget(line_spinner)
        layout.addLayout(input_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = create_button("Отмена", MODULE_BUTTON_STYLE)
        ok_btn = create_button("ОК", MODULE_BUTTON_STYLE)

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.setContentsMargins(0, 8, 0, 0)

        layout.addLayout(buttons_layout)

        if dialog.exec():
            line_number = line_spinner.value()
            description = ModuleHandler.format_module_description("restart.from", {"line": line_number})
            data = {"type": "restart_from", "line": line_number}
            self.add_module("restart.from", description, data)

    def add_restart_from_last_module(self):
        """Adds a restart.from.last module to the canvas"""
        description = ModuleHandler.format_module_description("restart.from.last", {})
        data = {"type": "restart_from_last"}
        self.add_module("restart.from.last", description, data)

    def add_click_module(self):
        """Adds a click module to the canvas using ModuleHandler"""
        self.add_module_with_dialog(ClickModuleDialog)

    def add_swipe_module(self):
        """Adds a swipe module to the canvas using ModuleHandler"""
        self.add_module_with_dialog(SwipeModuleDialog)

    def add_image_search_module(self):
        """Adds an image search module to the canvas using ModuleHandler"""
        self.add_module_with_dialog(ImageSearchModuleDialog)

    def add_get_coords_module(self):
        """Adds a get_coords module to the canvas"""
        description = ModuleHandler.format_module_description("get_coords", {})
        data = {"type": "get_coords"}
        self.add_module("get_coords", description, data)

    def add_continue_module(self):
        """Adds a continue module to the canvas"""
        description = ModuleHandler.format_module_description("continue", {})
        data = {"type": "continue"}
        self.add_module("continue", description, data)

    def add_running_clear_module(self):
        """Adds a running.clear() module to the canvas"""
        description = ModuleHandler.format_module_description("running.clear()", {})
        data = {"type": "running_clear"}
        self.add_module("running.clear()", description, data)


class ActivityModuleDialog(QDialog):
    """
    Диалог для настройки модуля проверки Activity.
    Улучшенная версия с более компактным и организованным интерфейсом.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля проверки Activity")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setModal(True)
        self.resize(800, 600)

        # State for fullscreen mode
        self.is_fullscreen = False
        self.normal_geometry = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI for the dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Уменьшаем промежутки между элементами

        # Apply general style
        self.setStyleSheet(ACTIVITY_DIALOG_STYLE)

        # Заголовок
        title_label = create_title_label("Настройка проверки активности игры", 18)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(ACTIVITY_MODULE_TITLE_STYLE)
        layout.addWidget(title_label)

        # Создаем компоновку с разделением на две колонки
        main_layout = QHBoxLayout()

        # Левая колонка - параметры
        left_column = QVBoxLayout()

        # Параметры запуска - группа
        launch_group = create_group_box("Параметры запуска")
        launch_layout = QFormLayout(launch_group)  # Используем FormLayout для компактности
        launch_layout.setContentsMargins(8, 12, 8, 8)
        launch_layout.setSpacing(6)

        # Игра
        self.game_combo = create_combobox()
        self.game_combo.currentIndexChanged.connect(self.update_activity_info)
        launch_layout.addRow("Игра:", self.game_combo)

        # Активность
        self.activity_info = create_input_field("", "", read_only=True)
        launch_layout.addRow("Активность:", self.activity_info)

        # Задержка
        self.time_sleep_input = create_double_spinbox_without_buttons(0.0, 300.0, 1.0, 1, " сек")
        launch_layout.addRow("Задержка перед запуском (сек):", self.time_sleep_input)

        left_column.addWidget(launch_group)

        # Статус модуля - группа
        status_group = create_group_box("Статус модуля")
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(8, 12, 8, 8)
        status_layout.setSpacing(6)

        # Включить проверку
        self.enable_check = QCheckBox("Включить постоянную проверку активности")
        self.enable_check.setChecked(True)
        self.enable_check.setStyleSheet("""
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
        """)
        status_layout.addWidget(self.enable_check)

        # Диапазон строк
        line_range_layout = QHBoxLayout()
        line_range_label = create_text_label("Диапазон строк:")
        self.line_range_input = create_input_field("Например: 1-50,60-100")
        line_range_layout.addWidget(line_range_label)
        line_range_layout.addWidget(self.line_range_input, 1)
        status_layout.addLayout(line_range_layout)

        left_column.addWidget(status_group)

        # Действие при вылете игры
        action_group = create_group_box("Действие при вылете игры")
        action_layout = QVBoxLayout(action_group)
        action_layout.setContentsMargins(8, 12, 8, 8)
        action_layout.setSpacing(6)

        # Выбор действия
        action_combo_layout = QHBoxLayout()
        action_label = create_text_label("Действие:")
        self.action_combo = create_combobox([
            "continue_bot - Перезапустить игру и продолжить",
            "activity.running.clear(0) - Закрыть эмулятор",
            "activity.running.clear(1) - Закрыть эмулятор и запустить следующий"
        ])
        self.action_combo.currentIndexChanged.connect(self.update_ui_based_on_action)
        action_combo_layout.addWidget(action_label)
        action_combo_layout.addWidget(self.action_combo, 1)
        action_layout.addLayout(action_combo_layout)

        left_column.addWidget(action_group)
        left_column.addStretch(1)  # Растягиваем пространство внизу

        # Добавляем левую колонку в основной макет
        main_layout.addLayout(left_column, 1)  # 1 - относительная ширина

        # Правая колонка - холст для настройки логики обработки вылета
        right_column = QVBoxLayout()

        # Canvas для continue_bot
        right_label = create_text_label("Редактор логики обработки вылета игры", "color: #FFA500; font-weight: bold;")
        right_column.addWidget(right_label)

        self.continue_canvas = ActivityCanvasModule(self)
        self.continue_canvas.setVisible(True)  # Initially visible
        right_column.addWidget(self.continue_canvas, 1)  # 1 - растягиваем по вертикали

        # Добавляем правую колонку в основной макет
        main_layout.addLayout(right_column, 2)  # 2 - относительная ширина (больше чем левая)

        # Добавляем основной макет в вертикальную компоновку
        layout.addLayout(main_layout, 1)  # 1 - растягиваем по вертикали

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_cancel = create_button("Отмена", MODULE_BUTTON_STYLE)
        self.btn_confirm = create_button("Подтвердить", MODULE_BUTTON_STYLE)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

        # Load games
        self.load_games()

        # Initialize UI based on initial action selection
        self.update_ui_based_on_action(0)

    def load_games(self):
        """Loads games from configuration"""
        try:
            # Add a default "Select game" option
            self.game_combo.addItem("Выберите игру")

            # Try to load games from config
            if os.path.exists('config/games_activities.json'):
                with open('config/games_activities.json', 'r', encoding='utf-8') as f:
                    games_activities = json.load(f)
                    for game in games_activities.keys():
                        self.game_combo.addItem(game)
        except Exception as e:
            print(f"Error loading games: {e}")

    def update_activity_info(self, index):
        """Updates activity info based on selected game"""
        if index <= 0:  # "Select game" or no selection
            self.activity_info.setText("")
            return

        try:
            game = self.game_combo.currentText()
            if os.path.exists('config/games_activities.json'):
                with open('config/games_activities.json', 'r', encoding='utf-8') as f:
                    games_activities = json.load(f)
                    if game in games_activities:
                        self.activity_info.setText(games_activities[game])
                    else:
                        self.activity_info.setText("")
        except Exception as e:
            print(f"Error updating activity info: {e}")
            self.activity_info.setText("")

    def update_ui_based_on_action(self, index):
        """Updates UI based on selected action"""
        self.continue_canvas.setVisible(index == 0)  # Only show canvas for continue_bot (index 0)
        # Добавляем сообщение, чтобы было понятно, что выбрано
        if index != 0:
            info_label = create_text_label("Для данного действия нет дополнительных настроек", "color: white; background-color: #2A2A2A; padding: 10px; border-radius: 5px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if not hasattr(self, 'info_label'):
                self.info_label = info_label
                self.continue_canvas.layout().addWidget(info_label)
            else:
                self.info_label.setVisible(index != 0)
        elif hasattr(self, 'info_label'):
            self.info_label.setVisible(False)

    def get_data(self) -> Dict[str, Any]:
        """Returns the data entered by the user"""
        action_index = self.action_combo.currentIndex()
        action_type = ["continue_bot", "activity.running.clear(0)", "activity.running.clear(1)"][action_index]

        data = {
            "type": "activity",
            "enabled": self.enable_check.isChecked(),
            "action": action_type,
            "line_range": self.line_range_input.text().strip(),
            "game": self.game_combo.currentText() if self.game_combo.currentIndex() > 0 else "",
            "activity": self.activity_info.text(),
            "startup_delay": self.time_sleep_input.value()
        }

        # Add continue_bot options if that action is selected
        if action_type == "continue_bot":
            data["continue_options"] = self.continue_canvas.get_modules_data()

        return data