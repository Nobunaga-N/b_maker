# src/gui/create_bot_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QScrollArea, QTabWidget, QSplitter, QTableWidget,
    QTableWidgetItem, QToolBar, QToolButton, QMessageBox, QFileDialog,
    QHeaderView, QSpinBox, QDialog, QTextEdit, QCheckBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QAction

import os
import json
from typing import Dict, List, Any, Optional

from src.utils.file_manager import create_bot_environment
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog, TimeSleepModuleDialog
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog
from src.gui.custom_widgets import ActivityModuleDialog, ModuleListItem


class ModuleListItem:
    """
    Класс для представления модуля в списке модулей.
    """

    def __init__(self, module_type: str, display_text: str, data: Dict[str, Any]):
        self.module_type = module_type
        self.display_text = display_text
        self.data = data


class CreateBotPage(QWidget):
    """
    Страница для создания и редактирования ботов.
    """
    # Сигнал, который будет испускаться при создании или сохранении бота
    botCreated = pyqtSignal(str, str)  # имя_бота, игра

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("createBotPage")
        self.modules_data = []  # List for storing module data
        self.current_bot_path = None  # Path to the currently edited bot
        self.setup_ui()
        self.load_games()

        # Add Activity module by default
        self.add_default_activity_module()

    def add_default_activity_module(self):
        """Adds a default Activity module at index 0"""
        # Default Activity data
        data = {
            "type": "activity",
            "enabled": True,
            "action": "continue_bot",
            "line_range": "",
            "game": "",
            "activity": "",
            "startup_delay": 1.0,
            "continue_options": []
        }

        # Create description
        description = "Статус: Включен, Действие: continue_bot"

        # Always add at the beginning
        self.modules_table.insertRow(0)

        # Fill table cells
        self.modules_table.setItem(0, 0, QTableWidgetItem("0"))  # Row number
        self.modules_table.setItem(0, 1, QTableWidgetItem("Activity"))
        self.modules_table.setItem(0, 2, QTableWidgetItem(description))

        # Add action buttons
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)

        edit_btn = QPushButton("Изменить")
        edit_btn.clicked.connect(lambda: self.edit_module(0))
        actions_layout.addWidget(edit_btn)

        self.modules_table.setCellWidget(0, 3, actions_widget)

        # Add to data list
        self.modules_data.insert(0, ModuleListItem("Activity", description, data))

    def _create_button_data(self, row):
        """Создает данные о типе строки для последующего воссоздания кнопок"""
        # Если ячейка с кнопками еще не существует, вернем None
        if row < 0 or row >= self.modules_table.rowCount():
            return None

        # Просто возвращаем тип модуля, который используется для определения нужных кнопок
        return self.modules_data[row].module_type if row < len(self.modules_data) else None

    def _recreate_action_buttons(self, row, module_type):
        """Пересоздает кнопки действий для указанной строки"""
        if row < 0 or row >= self.modules_table.rowCount() or not module_type:
            return

        # Удаляем старый виджет с кнопками, если он существует
        old_widget = self.modules_table.cellWidget(row, 3)
        if old_widget:
            old_widget.deleteLater()

        # Создаем новый виджет с кнопками
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)

        # Создаем кнопку редактирования с правильным захватом row
        edit_btn = QPushButton("Изменить")
        row_for_lambda = row  # Создаем копию переменной для захвата текущего значения
        edit_btn.clicked.connect(lambda checked=False, r=row_for_lambda: self.edit_module(r))
        actions_layout.addWidget(edit_btn)

        # Устанавливаем виджет в ячейку таблицы
        self.modules_table.setCellWidget(row, 3, actions_widget)

    def setup_ui(self):
        """Настраивает интерфейс страницы создания бота"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок и информация о боте
        title_layout = QHBoxLayout()

        title_label = QLabel("Редактор ботов")
        title_label.setStyleSheet("color: #FFA500; font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)

        # Добавление растягивающегося спейсера
        title_layout.addStretch()

        # Кнопки для сохранения/загрузки
        self.btn_save = QPushButton("Сохранить бота")
        self.btn_save.setIcon(QIcon("assets/icons/save.svg"))
        self.btn_save.clicked.connect(self.save_bot)
        title_layout.addWidget(self.btn_save)

        self.btn_test = QPushButton("Тест бота")
        self.btn_test.setIcon(QIcon("assets/icons/test.svg"))
        self.btn_test.clicked.connect(self.test_bot)
        title_layout.addWidget(self.btn_test)

        main_layout.addLayout(title_layout)

        # Информация о боте - название и игра
        bot_info_frame = QFrame()
        bot_info_frame.setStyleSheet("""
            background-color: #1E1E1E; 
            border-radius: 8px; 
            padding: 10px;
            border: 1px solid #444;
        """)
        bot_info_layout = QHBoxLayout(bot_info_frame)

        # Название бота
        bot_name_layout = QHBoxLayout()
        bot_name_label = QLabel("Название бота:")
        bot_name_label.setStyleSheet("color: white;")
        self.bot_name_input = QLineEdit()
        self.bot_name_input.setPlaceholderText("Введите название бота")
        self.bot_name_input.setStyleSheet("""
            background-color: #2C2C2C; 
            color: white; 
            padding: 8px;
            border: 1px solid #444;
            border-radius: 4px;
        """)
        bot_name_layout.addWidget(bot_name_label)
        bot_name_layout.addWidget(self.bot_name_input, 1)

        # Выбор игры
        game_layout = QHBoxLayout()
        game_label = QLabel("Игра:")
        game_label.setStyleSheet("color: white;")
        self.game_combo = QComboBox()
        self.game_combo.setStyleSheet("""
            background-color: #2C2C2C; 
            color: white; 
            padding: 8px;
            border: 1px solid #444;
            border-radius: 4px;
        """)
        game_layout.addWidget(game_label)
        game_layout.addWidget(self.game_combo, 1)

        bot_info_layout.addLayout(bot_name_layout, 2)
        bot_info_layout.addLayout(game_layout, 1)

        main_layout.addWidget(bot_info_frame)

        # Создаем сплиттер для разделения панели модулей и холста
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список доступных модулей
        modules_panel = QFrame()
        modules_panel.setStyleSheet("""
            background-color: #1E1E1E; 
            border-radius: 8px;
            border: 1px solid #444;
        """)
        modules_layout = QVBoxLayout(modules_panel)

        modules_title = QLabel("Доступные модули")
        modules_title.setStyleSheet("color: #FFA500; font-size: 16px; font-weight: bold;")
        modules_layout.addWidget(modules_title)

        # Модули
        self.btn_add_click = QPushButton("Добавить клик")
        self.btn_add_click.setIcon(QIcon("assets/icons/click-white.svg"))
        self.btn_add_click.clicked.connect(self.add_click_module)
        modules_layout.addWidget(self.btn_add_click)

        self.btn_add_swipe = QPushButton("Добавить свайп")
        self.btn_add_swipe.setIcon(QIcon("assets/icons/swipe.svg"))
        self.btn_add_swipe.clicked.connect(self.add_swipe_module)
        modules_layout.addWidget(self.btn_add_swipe)

        self.btn_add_image_search = QPushButton("Поиск по картинке")
        self.btn_add_image_search.setIcon(QIcon("assets/icons/search.svg"))
        self.btn_add_image_search.clicked.connect(self.add_image_search_module)
        modules_layout.addWidget(self.btn_add_image_search)

        self.btn_add_time_sleep = QPushButton("Добавить паузу")
        self.btn_add_time_sleep.setIcon(QIcon("assets/icons/pause-white.svg"))
        self.btn_add_time_sleep.clicked.connect(self.add_time_sleep_module)
        modules_layout.addWidget(self.btn_add_time_sleep)

        self.btn_add_activity = QPushButton("Настройка Activity")
        self.btn_add_activity.setIcon(QIcon("assets/icons/activity.svg"))
        self.btn_add_activity.clicked.connect(self.add_activity_module)
        modules_layout.addWidget(self.btn_add_activity)

        modules_layout.addStretch()

        # Правая панель - рабочий холст со списком модулей
        canvas_panel = QFrame()
        canvas_panel.setStyleSheet("""
            background-color: #1E1E1E; 
            border-radius: 8px;
            border: 1px solid #444;
        """)
        canvas_layout = QVBoxLayout(canvas_panel)

        canvas_title = QLabel("Рабочий холст")
        canvas_title.setStyleSheet("color: #FFA500; font-size: 16px; font-weight: bold;")
        canvas_layout.addWidget(canvas_title)

        # Таблица модулей (холст)
        self.modules_table = QTableWidget(0, 4)  # строки, столбцы (№, Тип, Описание, Действия)
        self.modules_table.setHorizontalHeaderLabels(["№", "Тип модуля", "Описание", "Действия"])
        self.modules_table.setStyleSheet("""
            QTableWidget {
                background-color: #2C2C2C;
                color: white;
                gridline-color: #444;
                border: none;
            }
            QHeaderView::section {
                background-color: #3A3A3A;
                color: #FFA500;
                padding: 5px;
                border: 1px solid #444;
            }
            QTableWidget::item:selected {
                background-color: #FFA500;
                color: white;
            }
        """)
        self.modules_table.verticalHeader().setVisible(False)
        self.modules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.modules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.modules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.modules_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.modules_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.modules_table.setColumnWidth(0, 40)  # № строки
        self.modules_table.setColumnWidth(1, 150)  # Тип модуля
        self.modules_table.setColumnWidth(3, 120)  # Кнопки действий

        canvas_layout.addWidget(self.modules_table)

        # Кнопки для управления порядком модулей
        buttons_layout = QHBoxLayout()

        self.btn_move_up = QPushButton("Вверх")
        self.btn_move_up.setIcon(QIcon("assets/icons/up.svg"))
        self.btn_move_up.clicked.connect(self.move_module_up)

        self.btn_move_down = QPushButton("Вниз")
        self.btn_move_down.setIcon(QIcon("assets/icons/down.svg"))
        self.btn_move_down.clicked.connect(self.move_module_down)

        self.btn_delete_module = QPushButton("Удалить")
        self.btn_delete_module.setIcon(QIcon("assets/icons/delete.svg"))
        self.btn_delete_module.clicked.connect(self.delete_selected_module)

        buttons_layout.addWidget(self.btn_move_up)
        buttons_layout.addWidget(self.btn_move_down)
        buttons_layout.addWidget(self.btn_delete_module)
        buttons_layout.addStretch(1)

        canvas_layout.addLayout(buttons_layout)

        # Добавляем панели в сплиттер
        splitter.addWidget(modules_panel)
        splitter.addWidget(canvas_panel)

        # Устанавливаем пропорции сплиттера (30% : 70%)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter, 1)  # Растягиваем по вертикали

    def add_time_sleep_module(self):
        """Добавляет модуль time.sleep в холст"""
        dialog = TimeSleepModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Формируем описание для отображения
            description = f"Пауза {data['delay']} сек"
            if data.get('description'):
                description += f" - {data['description']}"

            # Добавляем модуль в таблицу
            self.add_module_to_table("Пауза", description, data)

    def load_games(self):
        """Загружает список игр из настроек"""
        try:
            self.game_combo.clear()

            # Сначала добавляем вариант "Выберите игру"
            self.game_combo.addItem("Выберите игру")

            # Попытка загрузить игры из конфига
            games = []
            if os.path.exists('config/games_activities.json'):
                with open('config/games_activities.json', 'r', encoding='utf-8') as f:
                    games_activities = json.load(f)
                    games = list(games_activities.keys())

            # Если игр нет в конфиге, добавляем дефолтные
            if not games:
                games = ["Game 1", "Game 2", "Game 3"]

            # Добавляем игры в комбобокс
            self.game_combo.addItems(games)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить список игр: {str(e)}")

    def add_click_module(self):
        """Добавляет модуль клика в холст"""
        dialog = ClickModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Преобразуем данные (например, x и y в int, sleep в float)
            try:
                # Создаем данные модуля
                module_data = {
                    "type": "click",
                    "x": int(data.get("x", 0)),
                    "y": int(data.get("y", 0)),
                    "description": data.get("description", ""),
                    "console_description": data.get("console_description", ""),
                    "sleep": float(data.get("sleep", 0.0))
                }

                # Добавляем модуль в таблицу
                self.add_module_to_table(
                    "Клик",
                    f"({module_data['x']}, {module_data['y']}) {module_data['description']}",
                    module_data
                )

            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", f"Некорректные данные: {str(e)}")

    def add_swipe_module(self):
        """Добавляет модуль свайпа в холст"""
        dialog = SwipeModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            try:
                # Формируем описание
                description = f"({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']}) {data['description']}"

                # Добавляем модуль в таблицу
                self.add_module_to_table("Свайп", description, data)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при добавлении модуля свайпа: {str(e)}")

    def add_image_search_module(self):
        """Добавляет модуль поиска изображения в холст"""
        dialog = ImageSearchModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Формируем строку описания
            images_str = ", ".join(data.get("images", []))
            description = f"Поиск: {images_str} (таймаут: {data.get('timeout', 120)} сек)"

            # Добавляем детали о количестве блоков скрипта
            script_items = data.get("script_items", [])
            if script_items:
                if_result_count = sum(1 for item in script_items if item.get("type") == "if_result")
                elif_count = sum(1 for item in script_items if item.get("type") == "elif")
                if_not_result_count = sum(1 for item in script_items if item.get("type") == "if_not_result")

                blocks_info = []
                if if_result_count:
                    blocks_info.append(f"{if_result_count} IF Result")
                if elif_count:
                    blocks_info.append(f"{elif_count} ELIF")
                if if_not_result_count:
                    blocks_info.append(f"{if_not_result_count} IF Not Result")

                if blocks_info:
                    description += f" | Блоки: {', '.join(blocks_info)}"

            # Добавляем модуль в таблицу
            self.add_module_to_table("Поиск картинки", description, data)

    def add_activity_module(self):
        """Adds or configures the Activity module"""
        dialog = ActivityModuleDialog(self)

        # If there is an existing Activity module, load its data
        activity_index = -1
        for i, module in enumerate(self.modules_data):
            if module.module_type == "Activity":
                activity_index = i
                # Fill dialog with existing data
                data = module.data

                # Fill dialog fields with existing data
                if "enabled" in data:
                    dialog.enable_check.setChecked(bool(data["enabled"]))

                if "line_range" in data:
                    dialog.line_range_input.setText(data["line_range"])

                if "game" in data and data["game"]:
                    game_index = dialog.game_combo.findText(data["game"])
                    if game_index >= 0:
                        dialog.game_combo.setCurrentIndex(game_index)

                if "activity" in data:
                    dialog.activity_info.setText(data["activity"])

                if "startup_delay" in data:
                    dialog.time_sleep_input.setValue(float(data["startup_delay"]))

                # Set action combobox
                action = data.get("action", "continue_bot")
                index = 0
                if action == "activity.running.clear(0)":
                    index = 1
                elif action == "activity.running.clear(1)":
                    index = 2
                dialog.action_combo.setCurrentIndex(index)

                # Load continue_bot options if they exist
                if "continue_options" in data and data["action"] == "continue_bot":
                    dialog.continue_canvas.clear()
                    for module_item in data["continue_options"]:
                        module_type = module_item.get("type", "")
                        description = module_item.get("description", "")
                        module_data = module_item.get("data", {})
                        dialog.continue_canvas.add_module(module_type, description, module_data)

                break

        if dialog.exec():
            data = dialog.get_data()

            if activity_index >= 0:
                # Update existing Activity module
                status = "Включен" if data["enabled"] else "Отключен"
                description = f"Статус: {status}, Действие: {data['action']}"

                # Update data in table
                self.modules_table.item(activity_index, 1).setText("Activity")
                self.modules_table.item(activity_index, 2).setText(description)

                # Update data in module list
                self.modules_data[activity_index] = ModuleListItem("Activity", description, data)
            else:
                # Create new Activity module
                status = "Включен" if data["enabled"] else "Отключен"
                description = f"Статус: {status}, Действие: {data['action']}"

                # Always add at the beginning
                self.modules_table.insertRow(0)

                # Fill table cells
                self.modules_table.setItem(0, 0, QTableWidgetItem("0"))  # Row number
                self.modules_table.setItem(0, 1, QTableWidgetItem("Activity"))
                self.modules_table.setItem(0, 2, QTableWidgetItem(description))

                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(2)

                edit_btn = QPushButton("Изменить")
                edit_btn.clicked.connect(lambda: self.edit_module(0))
                actions_layout.addWidget(edit_btn)

                self.modules_table.setCellWidget(0, 3, actions_widget)

                # Add to data list
                self.modules_data.insert(0, ModuleListItem("Activity", description, data))

                # Renumber rows
                self.renumber_rows()

    def add_module_to_table(self, module_type: str, description: str, data: Dict[str, Any]):
        """Adds a module to the table on the canvas"""
        # If it's an Activity module, it should always be at row 0
        if module_type == "Activity":
            row = 0
        else:
            # For other modules, add them after the existing modules
            row = self.modules_table.rowCount()
            self.modules_table.insertRow(row)

        # Fill table cells
        self.modules_table.setItem(row, 0, QTableWidgetItem(str(row)))  # Row number
        self.modules_table.setItem(row, 1, QTableWidgetItem(module_type))
        self.modules_table.setItem(row, 2, QTableWidgetItem(description))

        # Add action buttons
        self._recreate_action_buttons(row, module_type)

        # Add to data list
        if module_type == "Activity":
            # For Activity, insert at the beginning
            if len(self.modules_data) > 0 and self.modules_data[0].module_type == "Activity":
                # Replace existing Activity module
                self.modules_data[0] = ModuleListItem(module_type, description, data)
            else:
                # Insert new Activity module
                self.modules_data.insert(0, ModuleListItem(module_type, description, data))
        else:
            # For other modules, append to list
            self.modules_data.append(ModuleListItem(module_type, description, data))

        # Select the added row
        self.modules_table.selectRow(row)

    def edit_module(self, row: int):
        """Edits a module in the table"""
        try:
            # Check if row is in valid range
            if row < 0 or row >= len(self.modules_data):
                QMessageBox.warning(self, "Ошибка", f"Неверный индекс строки: {row}")
                return

            module = self.modules_data[row]
            module_type = module.module_type

            if module_type == "Activity":
                dialog = ActivityModuleDialog(self)

                # Fill dialog with existing data
                data = module.data

                # Enable/disable checkbox
                if "enabled" in data:
                    dialog.enable_check.setChecked(bool(data["enabled"]))

                # Line range input
                if "line_range" in data:
                    dialog.line_range_input.setText(data["line_range"])

                # Game selection
                if "game" in data and data["game"]:
                    game_index = dialog.game_combo.findText(data["game"])
                    if game_index >= 0:
                        dialog.game_combo.setCurrentIndex(game_index)

                # Activity text
                if "activity" in data:
                    dialog.activity_info.setText(data["activity"])

                # Startup delay
                if "startup_delay" in data:
                    dialog.time_sleep_input.setValue(float(data["startup_delay"]))

                # Action selection
                action = data.get("action", "continue_bot")
                index = 0
                if action == "activity.running.clear(0)":
                    index = 1
                elif action == "activity.running.clear(1)":
                    index = 2
                dialog.action_combo.setCurrentIndex(index)

                # Load continue options if they exist
                if "continue_options" in data and isinstance(data["continue_options"],
                                                             list) and action == "continue_bot":
                    dialog.continue_canvas.clear()
                    for module_item in data["continue_options"]:
                        module_type = module_item.get("type", "")
                        description = module_item.get("description", "")
                        module_data = module_item.get("data", {})
                        dialog.continue_canvas.add_module(module_type, description, module_data)

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Update module data
                    module.data.update(new_data)

                    # Update display in table
                    status = "Включен" if new_data["enabled"] else "Отключен"
                    new_description = f"Статус: {status}, Действие: {new_data['action']}"
                    module.display_text = new_description

                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Клик":
                dialog = ClickModuleDialog(self)

                # Fill dialog with current data
                data = module.data
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
                    module.data.update({
                        "x": int(new_data["x"]),
                        "y": int(new_data["y"]),
                        "description": new_data["description"],
                        "console_description": new_data["console_description"],
                        "sleep": float(new_data["sleep"])
                    })

                    # Update display in table
                    new_description = f"({module.data['x']}, {module.data['y']}) {module.data['description']}"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Свайп":
                dialog = SwipeModuleDialog(self)

                # Fill dialog with current data
                data = module.data
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
                    module.data.update(new_data)

                    # Update display in table
                    new_description = f"({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']}) {data['description']}"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Пауза":
                dialog = TimeSleepModuleDialog(self)

                # Заполняем диалог текущими данными
                data = module.data
                if isinstance(data.get("delay"), (int, float)):
                    dialog.delay_input.setValue(float(data.get("delay", 1.0)))
                if data.get("description") is not None:
                    dialog.description_input.setText(str(data.get("description", "")))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Обновляем данные модуля
                    module.data.update(new_data)

                    # Обновляем отображение в таблице
                    description = f"Пауза {new_data['delay']} сек"
                    if new_data.get('description'):
                        description += f" - {new_data['description']}"

                    module.display_text = description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(description)

            elif module_type == "Поиск картинки":
                dialog = ImageSearchModuleDialog(self)

                # Fill dialog with current data - with checks for existence of data
                data = module.data
                if data.get("images") and len(data.get("images", [])) > 0:
                    dialog.image_name.setText(data["images"][0])
                    # Add additional images starting from the second one
                    for i in range(1, len(data["images"])):
                        dialog.additional_image.setText(data["images"][i])
                        dialog.add_additional_image()
                if isinstance(data.get("timeout"), (int, float)):
                    dialog.timeout_input.setValue(int(data.get("timeout", 60)))

                # Load script_items into dialog - this is a critical part
                if "script_items" in data and data["script_items"]:
                    for item in data["script_items"]:
                        item_type = item.get("type")
                        item_data = item.get("data", {})

                        # Depends on script item type
                        description = ""
                        if item_type == "IF Result":
                            selected_image = "любое изображение"
                            if item_data.get("image"):
                                selected_image = item_data["image"]
                            description = f"Если найдено {selected_image}"
                            # Can add additional description if needed
                        elif item_type == "ELIF":
                            selected_image = item_data.get("image", "неизвестное изображение")
                            description = f"ELIF: Если найдено {selected_image}"
                        elif item_type == "IF Not Result":
                            description = "Если изображение не найдено"

                        # Add item to dialog canvas
                        dialog.add_script_item(item_type, description, item_data)

                # Fill settings for if image is found
                if_result = data.get("if_result", {})
                if if_result.get("log_event") is not None:
                    dialog.log_event_if_found.setText(str(if_result.get("log_event", "")))

                # Fill settings for if image is not found
                if_not_result = data.get("if_not_result", {})
                if if_not_result.get("log_event") is not None:
                    dialog.log_event_if_not_found.setText(str(if_not_result.get("log_event", "")))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Update module data
                    module.data.update(new_data)

                    # Update display in table
                    images_str = ", ".join(new_data["images"])
                    new_description = f"Поиск: {images_str} (таймаут: {new_data['timeout']} сек)"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

        except Exception as e:
            import traceback
            error_info = traceback.format_exc()
            QMessageBox.critical(self, "Ошибка редактирования",
                                 f"Произошла ошибка при редактировании модуля:\n{str(e)}\n\nПодробности:\n{error_info}")

    def move_module_up(self):
        """Moves the selected module up in the list"""
        selected_rows = self.modules_table.selectedIndexes()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # Check if this is not the first row (except Activity) or if it's Activity
        if current_row <= 0 or (current_row == 1 and self.modules_data[0].module_type == "Activity"):
            return

        # If first module is Activity, account for this when moving
        if self.modules_data[0].module_type == "Activity" and current_row == 1:
            return  # Can't swap with Activity

        try:
            # Swap in data list
            self.modules_data[current_row], self.modules_data[current_row - 1] = \
                self.modules_data[current_row - 1], self.modules_data[current_row]

            # Remember button data for both rows
            current_row_button_data = self._create_button_data(current_row)
            above_row_button_data = self._create_button_data(current_row - 1)

            # Update table
            for col in range(1, 3):  # Type and Description
                current_item = self.modules_table.takeItem(current_row, col)
                above_item = self.modules_table.takeItem(current_row - 1, col)
                if current_item and above_item:
                    self.modules_table.setItem(current_row - 1, col, current_item)
                    self.modules_table.setItem(current_row, col, above_item)

            # Recreate buttons instead of directly moving widgets
            self._recreate_action_buttons(current_row, above_row_button_data)
            self._recreate_action_buttons(current_row - 1, current_row_button_data)

            # Renumber rows
            self.renumber_rows()

            # Select moved row
            self.modules_table.selectRow(current_row - 1)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении модуля: {str(e)}")

    def move_module_down(self):
        """Moves the selected module down in the list"""
        selected_rows = self.modules_table.selectedIndexes()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # Check if this is not the last row
        if current_row >= self.modules_table.rowCount() - 1:
            return

        # If first module is Activity and selected, can't move it down
        if self.modules_data[0].module_type == "Activity" and current_row == 0:
            return

        try:
            # Swap in data list
            self.modules_data[current_row], self.modules_data[current_row + 1] = \
                self.modules_data[current_row + 1], self.modules_data[current_row]

            # Remember button data for both rows
            current_row_button_data = self._create_button_data(current_row)
            below_row_button_data = self._create_button_data(current_row + 1)

            # Update table
            for col in range(1, 3):  # Type and Description
                current_item = self.modules_table.takeItem(current_row, col)
                below_item = self.modules_table.takeItem(current_row + 1, col)
                if current_item and below_item:
                    self.modules_table.setItem(current_row + 1, col, current_item)
                    self.modules_table.setItem(current_row, col, below_item)

            # Recreate buttons instead of directly moving widgets
            self._recreate_action_buttons(current_row, below_row_button_data)
            self._recreate_action_buttons(current_row + 1, current_row_button_data)

            # Renumber rows
            self.renumber_rows()

            # Select moved row
            self.modules_table.selectRow(current_row + 1)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении модуля: {str(e)}")

    def delete_selected_module(self):
        """Deletes the selected module from the table"""
        selected_rows = self.modules_table.selectedItems()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # If this is Activity and module is in row 0, just reset its settings
        if current_row == 0 and self.modules_data[0].module_type == "Activity":
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Модуль Activity нельзя удалить, но можно отключить. Хотите отключить этот модуль?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Disable Activity module
                self.modules_data[0].data["enabled"] = False
                status = "Отключен"
                new_description = f"Статус: {status}, Действие: {self.modules_data[0].data['action']}"
                self.modules_data[0].display_text = new_description
                self.modules_table.item(0, 2).setText(new_description)

            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить выбранный модуль?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove row from table
            self.modules_table.removeRow(current_row)

            # Remove module data
            del self.modules_data[current_row]

            # Renumber rows
            self.renumber_rows()

    def renumber_rows(self):
        """Обновляет нумерацию строк в таблице"""
        for row in range(self.modules_table.rowCount()):
            self.modules_table.item(row, 0).setText(str(row))

    def save_bot(self):
        """Сохраняет бота"""
        bot_name = self.bot_name_input.text().strip()
        game_index = self.game_combo.currentIndex()

        if not bot_name:
            QMessageBox.warning(self, "Ошибка", "Введите название бота")
            return

        if game_index <= 0:  # 0 - это "Выберите игру"
            QMessageBox.warning(self, "Ошибка", "Выберите игру")
            return

        if not self.modules_data:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один модуль")
            return

        try:
            # Получаем название игры
            game_name = self.game_combo.currentText()

            # Создаем или обновляем окружение для бота
            if not self.current_bot_path:
                create_bot_environment(bot_name)
                self.current_bot_path = os.path.join("bots", bot_name)

            # Сохраняем данные модулей в JSON
            bot_config = {
                "name": bot_name,
                "game": game_name,
                "modules": [module.data for module in self.modules_data]
            }

            # Создаем директорию, если её нет
            os.makedirs(self.current_bot_path, exist_ok=True)

            # Сохраняем конфигурацию
            config_path = os.path.join(self.current_bot_path, "config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(bot_config, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успех", f"Бот '{bot_name}' успешно сохранен!")

            # Испускаем сигнал о создании бота
            self.botCreated.emit(bot_name, game_name)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить бота: {str(e)}")

    def test_bot(self):
        """Запускает тестовый запуск бота"""
        if not self.modules_data:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один модуль для тестирования")
            return

        # Здесь будет реализована логика тестового запуска бота
        QMessageBox.information(self, "Тест", "Функция тестирования будет доступна в будущих версиях.")

    def load_bot(self, bot_path: str):
        """Loads an existing bot for editing"""
        try:
            config_path = os.path.join(bot_path, "config.json")

            if not os.path.exists(config_path):
                QMessageBox.warning(self, "Ошибка", "Файл конфигурации бота не найден")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                bot_config = json.load(f)

            # Clear current data
            self.modules_table.setRowCount(0)
            self.modules_data.clear()

            # Set name and game
            bot_name = bot_config.get("name", "")
            game_name = bot_config.get("game", "")

            self.bot_name_input.setText(bot_name)

            # Set game in combobox
            game_index = self.game_combo.findText(game_name)
            if game_index >= 0:
                self.game_combo.setCurrentIndex(game_index)

            # Load modules
            activity_found = False
            modules = bot_config.get("modules", [])

            for module_data in modules:
                module_type = module_data.get("type", "")

                if module_type == "activity":
                    # Add Activity module at the beginning
                    activity_found = True
                    status = "Включен" if module_data.get("enabled", False) else "Отключен"
                    description = f"Статус: {status}, Действие: {module_data.get('action', '')}"

                    # Activity is always added at the beginning
                    self.modules_table.insertRow(0)
                    self.modules_table.setItem(0, 0, QTableWidgetItem("0"))
                    self.modules_table.setItem(0, 1, QTableWidgetItem("Activity"))
                    self.modules_table.setItem(0, 2, QTableWidgetItem(description))

                    # Add action buttons
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(0, 0, 0, 0)
                    actions_layout.setSpacing(2)

                    edit_btn = QPushButton("Изменить")
                    edit_btn.clicked.connect(lambda: self.edit_module(0))
                    actions_layout.addWidget(edit_btn)

                    self.modules_table.setCellWidget(0, 3, actions_widget)

                    # Add to data list
                    self.modules_data.insert(0, ModuleListItem("Activity", description, module_data))
                elif module_type == "click":
                    # Add click module
                    description = f"({module_data['x']}, {module_data['y']}) {module_data.get('description', '')}"
                    self.add_module_to_table("Клик", description, module_data)
                elif module_type == "swipe":
                    # Add swipe module
                    description = f"({module_data['x1']}, {module_data['y1']}) → ({module_data['x2']}, {module_data['y2']}) {module_data.get('description', '')}"
                    self.add_module_to_table("Свайп", description, module_data)
                elif module_type == "image_search":
                    # Add image search module
                    images_str = ", ".join(module_data.get("images", []))
                    description = f"Поиск: {images_str} (таймаут: {module_data.get('timeout', 0)} сек)"
                    self.add_module_to_table("Поиск картинки", description, module_data)

                elif module_type == "time_sleep":
                    # Добавляем модуль time.sleep
                    description = f"Пауза {module_data.get('delay', 1.0)} сек"
                    if module_data.get('description'):
                        description += f" - {module_data['description']}"
                    self.add_module_to_table("Пауза", description, module_data)

            # If no Activity module was found, add it
            if not activity_found:
                self.add_default_activity_module()

            # Renumber rows
            self.renumber_rows()

            # Remember path to current bot
            self.current_bot_path = bot_path

            return True

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить бота: {str(e)}")
            return False