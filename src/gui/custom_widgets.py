from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

import os
import json
from typing import Dict, List, Any, Optional

from src.gui.modules.canvas_module import CanvasModule, ModuleItem
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog
from src.utils.style_constants import FULL_DIALOG_STYLE
from src.utils.ui_factory import create_spinbox_without_buttons, create_double_spinbox_without_buttons

class ModuleListItem:
    """
    Class for representing a module in the module list.
    Used by CreateBotPage to store module information.
    """

    def __init__(self, module_type: str, display_text: str, data: Dict[str, Any]):
        self.module_type = module_type
        self.display_text = display_text
        self.data = data

class ActivityCanvasModule(CanvasModule):
    """
    Canvas module for creating logic for activity handling.
    Inherits from the base CanvasModule and adds specific functionality
    for activity submodules.
    """

    def __init__(self, parent=None):
        super().__init__("Редактор логики обработки вылета игры", parent)

    def create_tool_buttons(self, layout):
        """Creates tool buttons for the activity canvas"""
        # Close game button
        self.btn_close_game = QPushButton("close.game")
        self.btn_close_game.setIcon(QIcon("assets/icons/delete.svg"))
        self.btn_close_game.clicked.connect(self.add_close_game_module)
        layout.addWidget(self.btn_close_game)

        # Restart emulator button
        self.btn_restart_emulator = QPushButton("restart.emulator")
        self.btn_restart_emulator.setIcon(QIcon("assets/icons/activity.svg"))
        self.btn_restart_emulator.clicked.connect(self.add_restart_emulator_module)
        layout.addWidget(self.btn_restart_emulator)

        # Start game button
        self.btn_start_game = QPushButton("start.game")
        self.btn_start_game.setIcon(QIcon("assets/icons/create.svg"))
        self.btn_start_game.clicked.connect(self.add_start_game_module)
        layout.addWidget(self.btn_start_game)

        # Time sleep button
        self.btn_time_sleep = QPushButton("time.sleep")
        self.btn_time_sleep.clicked.connect(self.add_time_sleep_module)
        layout.addWidget(self.btn_time_sleep)

        # Restart from button
        self.btn_restart_from = QPushButton("restart.from")
        self.btn_restart_from.clicked.connect(self.add_restart_from_module)
        layout.addWidget(self.btn_restart_from)

        # Restart from last button
        self.btn_restart_from_last = QPushButton("restart.from.last")
        self.btn_restart_from_last.clicked.connect(self.add_restart_from_last_module)
        layout.addWidget(self.btn_restart_from_last)

        # Click button
        self.btn_click = QPushButton("Клик")
        self.btn_click.setIcon(QIcon("assets/icons/click.svg"))
        self.btn_click.clicked.connect(self.add_click_module)
        layout.addWidget(self.btn_click)

        # Swipe button
        self.btn_swipe = QPushButton("Свайп")
        self.btn_swipe.setIcon(QIcon("assets/icons/swipe.svg"))
        self.btn_swipe.clicked.connect(self.add_swipe_module)
        layout.addWidget(self.btn_swipe)

        # Image search button
        self.btn_image_search = QPushButton("Поиск по картинке")
        self.btn_image_search.setIcon(QIcon("assets/icons/search.svg"))
        self.btn_image_search.clicked.connect(self.add_image_search_module)
        layout.addWidget(self.btn_image_search)

        layout.addStretch(1)  # Add stretch at the end

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
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)
        dialog.resize(300, 150)

        layout = QVBoxLayout(dialog)

        # Spinner for time
        input_layout = QHBoxLayout()
        time_label = QLabel("Время задержки (сек):")
        time_spinner = QDoubleSpinBox()
        time_spinner.setRange(0.1, 300.0)
        time_spinner.setValue(1.0)
        time_spinner.setDecimals(1)
        time_spinner.setSingleStep(0.1)
        time_spinner.setSuffix(" сек")
        time_spinner.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)  # Отключаем кнопки

        input_layout.addWidget(time_label)
        input_layout.addWidget(time_spinner)

        layout.addLayout(input_layout)

        # Buttons
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
            description = f"Пауза {time_value} сек (time.sleep)"
            data = {"type": "time_sleep", "time": time_value}
            self.add_module("time.sleep", description, data)

    def add_restart_from_module(self):
        """Adds a restart.from module to the canvas"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Перезапуск со строки")
        dialog.setModal(True)
        dialog.resize(300, 150)

        layout = QVBoxLayout(dialog)

        # Spinner for line number
        input_layout = QHBoxLayout()
        line_label = QLabel("Номер строки:")
        line_spinner = QSpinBox()
        line_spinner.setRange(1, 999)
        line_spinner.setValue(1)
        line_spinner.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Отключаем кнопки

        input_layout.addWidget(line_label)
        input_layout.addWidget(line_spinner)

        layout.addLayout(input_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("ОК")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)

        layout.addLayout(buttons_layout)

        if dialog.exec():
            line_number = line_spinner.value()
            description = f"Перезапуск со строки {line_number} (restart.from)"
            data = {"type": "restart_from", "line": line_number}
            self.add_module("restart.from", description, data)

    def add_restart_from_last_module(self):
        """Adds a restart.from.last module to the canvas"""
        description = "Перезапуск с последней позиции (restart.from.last)"
        data = {"type": "restart_from_last"}
        self.add_module("restart.from.last", description, data)

    def add_click_module(self):
        """Adds a click module to the canvas"""
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
        """Adds a swipe module to the canvas"""
        dialog = SwipeModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            description = f"Свайп ({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']})"
            if data.get('description'):
                description += f" - {data['description']}"
            if data.get('sleep') > 0:
                description += f" с задержкой {data['sleep']} сек"

            self.add_module("Свайп", description, data)

    def add_image_search_module(self):
        """Adds an image search module to the canvas"""
        dialog = ImageSearchModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Create description for the module
            images_str = ", ".join(data.get("images", []))
            description = f"Поиск изображений: {images_str} (таймаут: {data.get('timeout', 120)} сек)"

            self.add_module("Поиск картинки", description, data)

    def edit_module(self, index: int):
        """Edits a module on the canvas"""
        if 0 <= index < len(self.modules):
            module = self.modules[index]
            module_type = module.module_type
            data = module.get_data()

            if module_type == "Клик":
                dialog = ClickModuleDialog(self)

                # Fill dialog with current data
                if isinstance(data.get("x"), (int, float)):
                    dialog.x_input.setValue(int(data.get("x", 0)))
                if isinstance(data.get("y"), (int, float)):
                    dialog.y_input.setValue(int(data.get("y", 0)))
                if data.get("description") is not None:
                    dialog.description_input.setText(str(data.get("description", "")))
                if data.get("console_description") is not None:
                    dialog.console_description_input.setText(str(data.get("console_description", "")))
                if isinstance(data.get("sleep"), (int, float)):
                    dialog.sleep_input.setValue(float(data.get("sleep", 0.0)))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Update module data
                    for key, value in new_data.items():
                        data[key] = value

                    # Update description
                    description = f"Клик по координатам ({data['x']}, {data['y']})"
                    if data.get('description'):
                        description += f" - {data['description']}"
                    if data.get('sleep') > 0:
                        description += f" с задержкой {data['sleep']} сек"

                    module.description = description
                    module.set_data(data)

                    # Redraw modules
                    self._redraw_modules()

                    # Emit signals
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            elif module_type == "Свайп":
                dialog = SwipeModuleDialog(self)

                # Fill dialog with current data
                if isinstance(data.get("x1"), (int, float)):
                    dialog.start_x_input.setValue(int(data.get("x1", 0)))
                if isinstance(data.get("y1"), (int, float)):
                    dialog.start_y_input.setValue(int(data.get("y1", 0)))
                if isinstance(data.get("x2"), (int, float)):
                    dialog.end_x_input.setValue(int(data.get("x2", 0)))
                if isinstance(data.get("y2"), (int, float)):
                    dialog.end_y_input.setValue(int(data.get("y2", 0)))
                if data.get("description") is not None:
                    dialog.description_input.setText(str(data.get("description", "")))
                if data.get("console_description") is not None:
                    dialog.console_description_input.setText(str(data.get("console_description", "")))
                if isinstance(data.get("sleep"), (int, float)):
                    dialog.sleep_input.setValue(float(data.get("sleep", 0.0)))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Update module data
                    for key, value in new_data.items():
                        data[key] = value

                    # Update description
                    description = f"Свайп ({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']})"
                    if data.get('description'):
                        description += f" - {data['description']}"
                    if data.get('sleep') > 0:
                        description += f" с задержкой {data['sleep']} сек"

                    module.description = description
                    module.set_data(data)

                    # Redraw modules
                    self._redraw_modules()

                    # Emit signals
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            elif module_type == "Поиск картинки":
                dialog = ImageSearchModuleDialog(self)

                # Load existing data into dialog
                # This is just a placeholder - actual implementation would need to populate the
                # dialog with existing image search configuration
                if dialog.exec():
                    new_data = dialog.get_data()

                    # Create description for the module
                    images_str = ", ".join(new_data.get("images", []))
                    description = f"Поиск изображений: {images_str} (таймаут: {new_data.get('timeout', 120)} сек)"

                    module.description = description
                    module.set_data(new_data)

                    # Redraw modules
                    self._redraw_modules()

                    # Emit signals
                    self.moduleEdited.emit(index, module_type, description, new_data)
                    self.canvasChanged.emit()

            elif module_type == "time.sleep":
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox

                dialog = QDialog(self)
                dialog.setWindowTitle("Изменить паузу")
                dialog.setModal(True)
                dialog.resize(300, 150)

                layout = QVBoxLayout(dialog)

                # Spinner for time
                input_layout = QHBoxLayout()
                time_label = QLabel("Время задержки (сек):")
                time_spinner = QDoubleSpinBox()
                time_spinner.setRange(0.1, 300.0)
                time_spinner.setValue(data.get("time", 1.0))
                time_spinner.setDecimals(1)
                time_spinner.setSingleStep(0.1)
                time_spinner.setSuffix(" сек")

                input_layout.addWidget(time_label)
                input_layout.addWidget(time_spinner)

                layout.addLayout(input_layout)

                # Buttons
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
                    description = f"Пауза {time_value} сек (time.sleep)"
                    data["time"] = time_value

                    module.description = description
                    module.set_data(data)

                    # Redraw modules
                    self._redraw_modules()

                    # Emit signals
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            elif module_type == "restart.from":
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox

                dialog = QDialog(self)
                dialog.setWindowTitle("Изменить перезапуск со строки")
                dialog.setModal(True)
                dialog.resize(300, 150)

                layout = QVBoxLayout(dialog)

                # Spinner for line number
                input_layout = QHBoxLayout()
                line_label = QLabel("Номер строки:")
                line_spinner = QSpinBox()
                line_spinner.setRange(1, 999)
                line_spinner.setValue(data.get("line", 1))

                input_layout.addWidget(line_label)
                input_layout.addWidget(line_spinner)

                layout.addLayout(input_layout)

                # Buttons
                buttons_layout = QHBoxLayout()
                cancel_btn = QPushButton("Отмена")
                ok_btn = QPushButton("ОК")

                cancel_btn.clicked.connect(dialog.reject)
                ok_btn.clicked.connect(dialog.accept)

                buttons_layout.addWidget(cancel_btn)
                buttons_layout.addWidget(ok_btn)

                layout.addLayout(buttons_layout)

                if dialog.exec():
                    line_number = line_spinner.value()
                    description = f"Перезапуск со строки {line_number} (restart.from)"
                    data["line"] = line_number

                    module.description = description
                    module.set_data(data)

                    # Redraw modules
                    self._redraw_modules()

                    # Emit signals
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()


class ActivityModuleDialog(QDialog):
    """
    Dialog for configuring the activity module.
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
        layout.setSpacing(10)

        # Apply general style
        self.setStyleSheet(FULL_DIALOG_STYLE)

        title_label = QLabel("Настройка проверки активности игры")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFA500; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Launch parameters group
        launch_group = QGroupBox("Параметры запуска")
        launch_layout = QVBoxLayout(launch_group)

        # Game selection
        game_layout = QHBoxLayout()
        game_label = QLabel("Игра:")
        self.game_combo = QComboBox()
        self.game_combo.currentIndexChanged.connect(self.update_activity_info)
        game_layout.addWidget(game_label)
        game_layout.addWidget(self.game_combo, 1)
        launch_layout.addLayout(game_layout)

        # Activity info
        activity_layout = QHBoxLayout()
        activity_label = QLabel("Активность:")
        self.activity_info = QLineEdit()
        self.activity_info.setReadOnly(True)
        self.activity_info.setStyleSheet("background-color: #444;")
        activity_layout.addWidget(activity_label)
        activity_layout.addWidget(self.activity_info, 1)
        launch_layout.addLayout(activity_layout)

        # Time sleep before script start
        time_sleep_layout = QHBoxLayout()
        time_sleep_label = QLabel("Задержка перед запуском (сек):")
        self.time_sleep_input = QDoubleSpinBox()
        self.time_sleep_input.setRange(0.0, 300.0)
        self.time_sleep_input.setValue(1.0)
        self.time_sleep_input.setSingleStep(0.1)
        self.time_sleep_input.setDecimals(1)
        self.time_sleep_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)  # Отключаем кнопки
        time_sleep_layout.addWidget(time_sleep_label)
        time_sleep_layout.addWidget(self.time_sleep_input)
        launch_layout.addLayout(time_sleep_layout)

        layout.addWidget(launch_group)

        # Module status group
        status_group = QGroupBox("Статус модуля")
        status_layout = QVBoxLayout(status_group)

        # Enable activity check
        enable_layout = QHBoxLayout()
        self.enable_check = QCheckBox("Включить постоянную проверку активности")
        self.enable_check.setChecked(True)
        enable_layout.addWidget(self.enable_check)
        status_layout.addLayout(enable_layout)

        # Line range input
        line_range_layout = QHBoxLayout()
        line_range_label = QLabel("Диапазон строк (например, 1-50,60-100):")
        self.line_range_input = QLineEdit()
        line_range_layout.addWidget(line_range_label)
        line_range_layout.addWidget(self.line_range_input, 1)
        status_layout.addLayout(line_range_layout)

        layout.addWidget(status_group)

        # Action on game crash
        action_group = QGroupBox("Действие при вылете игры")
        action_layout = QVBoxLayout(action_group)

        # Action selection
        action_combo_layout = QHBoxLayout()
        action_label = QLabel("Действие:")
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "continue_bot - Перезапустить игру и продолжить",
            "activity.running.clear(0) - Закрыть эмулятор",
            "activity.running.clear(1) - Закрыть эмулятор и запустить следующий"
        ])
        self.action_combo.currentIndexChanged.connect(self.update_ui_based_on_action)
        action_combo_layout.addWidget(action_label)
        action_combo_layout.addWidget(self.action_combo, 1)
        action_layout.addLayout(action_combo_layout)

        # Canvas for continue_bot
        self.continue_canvas = ActivityCanvasModule(self)
        self.continue_canvas.setVisible(True)  # Initially visible
        action_layout.addWidget(self.continue_canvas)

        layout.addWidget(action_group)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
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