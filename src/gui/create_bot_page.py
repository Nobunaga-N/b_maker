# src/gui/create_bot_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QScrollArea, QTabWidget, QSplitter, QTableWidget,
    QTableWidgetItem, QToolBar, QToolButton, QMessageBox, QFileDialog,
    QHeaderView, QSpinBox, QDialog, QTextEdit, QCheckBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QAction, QBrush

import os
import json
from typing import Dict, List, Any, Optional

from src.utils.file_manager import create_bot_environment
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog, TimeSleepModuleDialog
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog
from src.gui.custom_widgets import ActivityModuleDialog, ModuleListItem
from src.utils.resources import Resources
from src.utils.style_constants import (
    MAIN_FRAME_STYLE, BASE_TABLE_STYLE, CREATE_BOT_STYLE, DARK_BUTTON_STYLE
)
from src.utils.ui_factory import (
    create_title_label, create_accent_button, create_dark_button,
    create_input_field, create_frame, create_spinbox_without_buttons,
    create_double_spinbox_without_buttons, create_group_box, create_table
)


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
        self.setup_connections()
        self.load_games()

        # Add Activity module by default
        self.add_default_activity_module()

    def setup_connections(self):
        """Устанавливает соединения сигналов и слотов"""
        # Кнопки для добавления модулей
        self.btn_add_click.clicked.connect(self.add_click_module)
        self.btn_add_swipe.clicked.connect(self.add_swipe_module)
        self.btn_add_image_search.clicked.connect(self.add_image_search_module)
        self.btn_add_time_sleep.clicked.connect(self.add_time_sleep_module)
        self.btn_add_activity.clicked.connect(self.add_activity_module)

        # Кнопки управления модулями
        self.btn_move_up.clicked.connect(self.move_module_up)
        self.btn_move_down.clicked.connect(self.move_module_down)
        self.btn_delete_module.clicked.connect(self.delete_selected_module)

        # Кнопки сохранения/тестирования
        self.btn_save.clicked.connect(self.save_bot)
        self.btn_test.clicked.connect(self.test_bot)

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
        self.add_action_buttons_to_row(0, "Activity")

        # Add to data list
        self.modules_data.insert(0, ModuleListItem("Activity", description, data))

    def create_bot_button(self, text, icon_path=None):
        """Создает кнопку с темным фоном, белым текстом и белой рамкой"""
        return create_dark_button(text, icon_path)

    def add_action_buttons_to_row(self, row, module_type):
        """Создает и добавляет кнопки действий для указанной строки"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)

        # Создаем кнопку редактирования с нужным стилем
        edit_btn = create_dark_button("Изменить")

        # Используем замыкание для сохранения текущего row
        def create_edit_callback(r):
            return lambda: self.edit_module(r)

        # Привязываем callback
        edit_callback = create_edit_callback(row)
        edit_btn.clicked.connect(edit_callback)
        actions_layout.addWidget(edit_btn)

        # Устанавливаем виджет в ячейку таблицы
        self.modules_table.setCellWidget(row, 3, actions_widget)

    def setup_ui(self):
        """Настраивает интерфейс страницы создания бота"""
        # Применяем стиль к странице
        self.setStyleSheet(CREATE_BOT_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок и информация о боте
        self.setup_header(main_layout)

        # Информация о боте
        self.setup_bot_info(main_layout)

        # Создаем сплиттер для разделения панели модулей и холста
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список доступных модулей
        self.setup_modules_panel(splitter)

        # Правая панель - рабочий холст со списком модулей
        self.setup_canvas_panel(splitter)

        # Устанавливаем пропорции сплиттера (30% : 70%)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter, 1)  # Растягиваем по вертикали

    def setup_header(self, main_layout):
        """Настраивает заголовок и кнопки сохранения/тестирования"""
        title_layout = QHBoxLayout()

        title_label = create_title_label("Редактор ботов", 24)
        title_layout.addWidget(title_label)

        title_layout.addStretch()  # Растягивающийся спейсер

        # Кнопки для сохранения/загрузки
        self.btn_save = self.create_bot_button("Сохранить бота", Resources.get_icon_path("save"))
        self.btn_test = self.create_bot_button("Тест бота", Resources.get_icon_path("test"))

        title_layout.addWidget(self.btn_save)
        title_layout.addWidget(self.btn_test)

        main_layout.addLayout(title_layout)

    def setup_bot_info(self, main_layout):
        """Настраивает поля для ввода информации о боте"""
        bot_info_frame = QFrame()
        bot_info_frame.setStyleSheet(MAIN_FRAME_STYLE)
        bot_info_layout = QHBoxLayout(bot_info_frame)

        # Название бота
        bot_name_layout = QHBoxLayout()
        bot_name_label = QLabel("Название бота:")
        bot_name_label.setStyleSheet("color: white;")
        self.bot_name_input = create_input_field("Введите название бота")
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

    def setup_modules_panel(self, splitter):
        """Настраивает панель с доступными модулями"""
        modules_panel = create_frame()
        modules_layout = QVBoxLayout(modules_panel)

        modules_title = create_title_label("Доступные модули", 16)
        modules_layout.addWidget(modules_title)

        # Создаем кнопки модулей с иконками
        self.btn_add_click = self.create_bot_button("Добавить клик", Resources.get_icon_path("click-white"))
        modules_layout.addWidget(self.btn_add_click)

        self.btn_add_swipe = self.create_bot_button("Добавить свайп", Resources.get_icon_path("swipe"))
        modules_layout.addWidget(self.btn_add_swipe)

        self.btn_add_image_search = self.create_bot_button("Поиск по картинке", Resources.get_icon_path("search"))
        modules_layout.addWidget(self.btn_add_image_search)

        self.btn_add_time_sleep = self.create_bot_button("Добавить паузу", Resources.get_icon_path("pause-white"))
        modules_layout.addWidget(self.btn_add_time_sleep)

        self.btn_add_activity = self.create_bot_button("Настройка Activity", Resources.get_icon_path("activity"))
        modules_layout.addWidget(self.btn_add_activity)

        modules_layout.addStretch()
        splitter.addWidget(modules_panel)

    def setup_canvas_panel(self, splitter):
        """Настраивает холст с таблицей модулей"""
        canvas_panel = QFrame()
        canvas_panel.setStyleSheet(MAIN_FRAME_STYLE)
        canvas_layout = QVBoxLayout(canvas_panel)

        canvas_title = create_title_label("Рабочий холст", 16)
        canvas_layout.addWidget(canvas_title)

        # Таблица модулей (холст)
        self.modules_table = create_table(["№", "Тип модуля", "Описание", "Действия"])
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

        self.btn_move_up = self.create_bot_button("Вверх", Resources.get_icon_path("up"))
        self.btn_move_down = self.create_bot_button("Вниз", Resources.get_icon_path("down"))
        self.btn_delete_module = self.create_bot_button("Удалить", Resources.get_icon_path("delete"))

        buttons_layout.addWidget(self.btn_move_up)
        buttons_layout.addWidget(self.btn_move_down)
        buttons_layout.addWidget(self.btn_delete_module)
        buttons_layout.addStretch(1)

        canvas_layout.addLayout(buttons_layout)
        splitter.addWidget(canvas_panel)

    def load_games(self):
        """Загружает список игр из настроек"""
        try:
            self.game_combo.clear()

            # Сначала добавляем вариант "Выберите игру"
            self.game_combo.addItem("Выберите игру")

            # Попытка загрузить игры из конфига
            games = []
            config_path = Resources.get_config_path("games_activities")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
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
                self.load_activity_dialog(dialog, data)
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
                self.add_action_buttons_to_row(0, "Activity")

                # Add to data list
                self.modules_data.insert(0, ModuleListItem("Activity", description, data))

                # Renumber rows
                self.renumber_rows()

    def load_activity_dialog(self, dialog, data):
        """Заполняет диалог активности данными из модуля"""
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
        self.add_action_buttons_to_row(row, module_type)

        # Add to data list
        if module_type == "Activity" and len(self.modules_data) > 0 and self.modules_data[0].module_type == "Activity":
            # Replace existing Activity module
            self.modules_data[0] = ModuleListItem(module_type, description, data)
        elif module_type == "Activity":
            # Insert new Activity module
            self.modules_data.insert(0, ModuleListItem(module_type, description, data))
        else:
            # For other modules, append to list
            self.modules_data.append(ModuleListItem(module_type, description, data))

        # Select the added row
        self.modules_table.selectRow(row)

    def edit_module(self, index: int):
        """Редактирует модуль на основе его типа"""
        try:
            # Проверка валидности индекса
            if index < 0 or index >= len(self.modules_data):
                QMessageBox.warning(self, "Ошибка", f"Неверный индекс строки: {index}")
                return

            module = self.modules_data[index]
            module_type = module.module_type
            module_data = module.data

            # Маппинг типов модулей на соответствующие диалоги и функции обновления
            module_editors = {
                "Activity": self._edit_activity_module,
                "Клик": self._edit_generic_module_with_dialog,
                "Свайп": self._edit_generic_module_with_dialog,
                "Пауза": self._edit_generic_module_with_dialog,
                "Поиск картинки": self._edit_image_search_module
            }

            # Дополнительные аргументы для различных типов модулей
            dialog_classes = {
                "Клик": ClickModuleDialog,
                "Свайп": SwipeModuleDialog,
                "Пауза": TimeSleepModuleDialog
            }

            # Вызываем соответствующий метод редактирования
            if module_type in module_editors:
                if module_type == "Activity":
                    module_editors[module_type](index, module, module_data)
                elif module_type in dialog_classes:
                    module_editors[module_type](index, module, module_data, dialog_classes[module_type])
                else:
                    module_editors[module_type](index, module, module_data)
            else:
                QMessageBox.warning(self, "Ошибка", f"Неизвестный тип модуля: {module_type}")

        except Exception as e:
            import traceback
            error_info = traceback.format_exc()
            QMessageBox.critical(self, "Ошибка редактирования",
                                 f"Произошла ошибка при редактировании модуля:\n{str(e)}\n\nПодробности:\n{error_info}")

    def _edit_generic_module_with_dialog(self, index, module, module_data, dialog_class):
        """Общий метод для редактирования модулей с помощью диалога"""
        dialog = dialog_class(self)
        dialog.load_data(module_data)

        if dialog.exec():
            new_data = dialog.get_data()

            # Обновляем данные модуля
            module.data.update(new_data)

            # Формируем описание на основе типа модуля
            if module.module_type == "Клик":
                description = f"({module.data['x']}, {module.data['y']})"
                if module.data.get('description'):
                    description += f" - {module.data['description']}"
                if module.data.get('sleep', 0) > 0:
                    description += f" с задержкой {module.data['sleep']} сек"

            elif module.module_type == "Свайп":
                description = f"({module.data['x1']}, {module.data['y1']}) → ({module.data['x2']}, {module.data['y2']})"
                if module.data.get('description'):
                    description += f" - {module.data['description']}"
                if module.data.get('sleep', 0) > 0:
                    description += f" с задержкой {module.data['sleep']} сек"

            elif module.module_type == "Пауза":
                description = f"Пауза {new_data['delay']} сек"
                if new_data.get('description'):
                    description += f" - {new_data['description']}"
            else:
                description = "Модуль обновлен"

            # Обновляем отображение
            module.display_text = description
            item = self.modules_table.item(index, 2)
            if item:
                item.setText(description)

    def _edit_activity_module(self, index, module, module_data):
        """Редактирует модуль активности"""
        dialog = ActivityModuleDialog(self)
        self.load_activity_dialog(dialog, module_data)

        if dialog.exec():
            new_data = dialog.get_data()

            # Обновляем данные модуля
            module.data.update(new_data)

            # Обновляем отображение в таблице
            status = "Включен" if new_data["enabled"] else "Отключен"
            new_description = f"Статус: {status}, Действие: {new_data['action']}"
            module.display_text = new_description

            # Обновляем ячейку в таблице
            item = self.modules_table.item(index, 2)
            if item:
                item.setText(new_description)

    def _edit_image_search_module(self, index, module, module_data):
        """Редактирует модуль поиска картинки"""
        dialog = ImageSearchModuleDialog(self)
        dialog.load_data(module_data)

        if dialog.exec():
            new_data = dialog.get_data()

            # Обновляем данные модуля
            module.data.update(new_data)

            # Формируем описание модуля
            images_str = ", ".join(new_data.get("images", []))
            new_description = f"Поиск: {images_str} (таймаут: {new_data.get('timeout', 120)} сек)"

            # Добавляем информацию о блоках скрипта
            script_items = new_data.get("script_items", [])
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
                    new_description += f" | Блоки: {', '.join(blocks_info)}"

            # Обновляем отображение
            module.display_text = new_description
            item = self.modules_table.item(index, 2)
            if item:
                item.setText(new_description)

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

            # Update table display
            for col in range(1, 3):  # Type and Description
                current_item = self.modules_table.takeItem(current_row, col)
                above_item = self.modules_table.takeItem(current_row - 1, col)
                if current_item and above_item:
                    self.modules_table.setItem(current_row - 1, col, current_item)
                    self.modules_table.setItem(current_row, col, above_item)

            # Update action buttons
            self.add_action_buttons_to_row(current_row, self.modules_data[current_row].module_type)
            self.add_action_buttons_to_row(current_row - 1, self.modules_data[current_row - 1].module_type)

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

            # Update table display
            for col in range(1, 3):  # Type and Description
                current_item = self.modules_table.takeItem(current_row, col)
                below_item = self.modules_table.takeItem(current_row + 1, col)
                if current_item and below_item:
                    self.modules_table.setItem(current_row + 1, col, current_item)
                    self.modules_table.setItem(current_row, col, below_item)

            # Update action buttons
            self.add_action_buttons_to_row(current_row, self.modules_data[current_row].module_type)
            self.add_action_buttons_to_row(current_row + 1, self.modules_data[current_row + 1].module_type)

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
                    self.add_action_buttons_to_row(0, "Activity")

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