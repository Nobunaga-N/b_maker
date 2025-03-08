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
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.gui.image_search_module import ImageSearchModuleDialog
from src.gui.custom_widgets import ActivityModuleDialog


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
        self.modules_data = []  # Список для хранения данных модулей
        self.current_bot_path = None  # Путь к текущему редактируемому боту
        self.setup_ui()
        self.load_games()

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
        self.btn_add_click.setIcon(QIcon("assets/icons/click.svg"))
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
                background-color: #FF5722;
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
        """Добавляет или настраивает модуль проверки Activity"""
        dialog = ActivityModuleDialog(self)

        # Если есть существующий модуль Activity, загружаем его данные
        activity_index = -1
        for i, module in enumerate(self.modules_data):
            if module.module_type == "Activity":
                activity_index = i
                # Заполняем диалог существующими данными
                # Реализация заполнения полей диалога...
                break

        if dialog.exec():
            data = dialog.get_data()

            if activity_index >= 0:
                # Обновляем существующий модуль
                status = "Включен" if data["enabled"] else "Отключен"
                description = f"Статус: {status}, Действие: {data['action']}"

                # Обновляем данные в таблице
                self.modules_table.item(activity_index, 1).setText("Activity")
                self.modules_table.item(activity_index, 2).setText(description)

                # Обновляем данные в списке модулей
                self.modules_data[activity_index] = ModuleListItem("Activity", description, data)
            else:
                # Создаем новый модуль Activity
                status = "Включен" if data["enabled"] else "Отключен"
                description = f"Статус: {status}, Действие: {data['action']}"

                # Добавляем модуль в таблицу (всегда в начало)
                row = self.modules_table.rowCount()
                self.modules_table.insertRow(0)  # Вставляем в начало

                # Заполняем ячейки таблицы
                self.modules_table.setItem(0, 0, QTableWidgetItem("0"))  # Номер строки
                self.modules_table.setItem(0, 1, QTableWidgetItem("Activity"))
                self.modules_table.setItem(0, 2, QTableWidgetItem(description))

                # Добавляем кнопки действий
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(2)

                edit_btn = QPushButton("Изменить")
                edit_btn.clicked.connect(lambda: self.edit_module(0))
                actions_layout.addWidget(edit_btn)

                self.modules_table.setCellWidget(0, 3, actions_widget)

                # Добавляем в список данных
                self.modules_data.insert(0, ModuleListItem("Activity", description, data))

                # Перенумеровываем строки
                self.renumber_rows()

    def add_module_to_table(self, module_type: str, description: str, data: Dict[str, Any]):
        """Добавляет модуль в таблицу на холсте"""
        row = self.modules_table.rowCount()
        self.modules_table.insertRow(row)

        # Заполняем ячейки таблицы
        self.modules_table.setItem(row, 0, QTableWidgetItem(str(row)))  # Номер строки
        self.modules_table.setItem(row, 1, QTableWidgetItem(module_type))
        self.modules_table.setItem(row, 2, QTableWidgetItem(description))

        # Добавляем кнопки действий
        self._recreate_action_buttons(row, module_type)

        # Добавляем в список данных
        self.modules_data.append(ModuleListItem(module_type, description, data))

        # Выделяем добавленную строку
        self.modules_table.selectRow(row)

    def edit_module(self, row: int):
        """Редактирует модуль в таблице"""
        try:
            # Проверяем, что row в допустимом диапазоне
            if row < 0 or row >= len(self.modules_data):
                QMessageBox.warning(self, "Ошибка", f"Неверный индекс строки: {row}")
                return

            module = self.modules_data[row]
            module_type = module.module_type

            if module_type == "Клик":
                dialog = ClickModuleDialog(self)

                # Заполняем диалог текущими данными
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

                    # Обновляем данные модуля
                    module.data.update({
                        "x": int(new_data["x"]),
                        "y": int(new_data["y"]),
                        "description": new_data["description"],
                        "console_description": new_data["console_description"],
                        "sleep": float(new_data["sleep"])
                    })

                    # Обновляем отображение в таблице
                    new_description = f"({module.data['x']}, {module.data['y']}) {module.data['description']}"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Свайп":
                dialog = SwipeModuleDialog(self)

                # Заполняем диалог текущими данными
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

                    # Обновляем данные модуля
                    module.data.update(new_data)

                    # Обновляем отображение в таблице
                    new_description = f"({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']}) {data['description']}"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Поиск картинки":
                dialog = ImageSearchModuleDialog(self)

                # Заполняем диалог текущими данными - с проверками на существование данных
                data = module.data
                if data.get("images") and len(data.get("images", [])) > 0:
                    dialog.image_name.setText(data["images"][0])
                    # Добавляем дополнительные изображения начиная со второго
                    for i in range(1, len(data["images"])):
                        dialog.additional_image.setText(data["images"][i])
                        dialog.add_additional_image()
                if isinstance(data.get("timeout"), (int, float)):
                    dialog.timeout_input.setValue(int(data.get("timeout", 60)))

                # Заполняем настройки для случая, если изображение найдено
                if_result = data.get("if_result", {})
                if if_result.get("log_event") is not None:
                    dialog.log_event_if_found.setText(str(if_result.get("log_event", "")))
                dialog.click_coords_check.setChecked(bool(if_result.get("get_coords", False)))
                dialog.continue_check.setChecked(bool(if_result.get("continue", False)))
                dialog.stop_bot_check.setChecked(bool(if_result.get("stop_bot", False)))

                # Заполняем настройки для случая, если изображение не найдено
                if_not_result = data.get("if_not_result", {})
                if if_not_result.get("log_event") is not None:
                    dialog.log_event_if_not_found.setText(str(if_not_result.get("log_event", "")))
                dialog.continue_not_found_check.setChecked(bool(if_not_result.get("continue", False)))
                dialog.stop_not_found_check.setChecked(bool(if_not_result.get("stop_bot", False)))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Обновляем данные модуля
                    module.data.update(new_data)

                    # Обновляем отображение в таблице
                    images_str = ", ".join(new_data["images"])
                    new_description = f"Поиск: {images_str} (таймаут: {new_data['timeout']} сек)"
                    module.display_text = new_description
                    item = self.modules_table.item(row, 2)
                    if item:
                        item.setText(new_description)

            elif module_type == "Activity":
                dialog = ActivityModuleDialog(self)

                # Заполняем диалог текущими данными
                data = module.data
                dialog.enable_check.setChecked(bool(data.get("enabled", True)))

                # Выбираем действие в комбобоксе
                action = data.get("action", "continue_bot")
                index = 0
                if action == "activity.running.clear(0)":
                    index = 1
                elif action == "activity.running.clear(1)":
                    index = 2
                dialog.action_combo.setCurrentIndex(index)

                # Заполняем опции для continue_bot
                options = data.get("options", {})
                dialog.restart_emulator_check.setChecked(bool(options.get("restart_emulator", False)))
                dialog.close_game_check.setChecked(bool(options.get("close_game", False)))
                dialog.start_game_check.setChecked(bool(options.get("start_game", True)))
                dialog.restart_from_last_check.setChecked(bool(options.get("restart_from_last", False)))

                if options.get("restart_from_line") is not None:
                    dialog.restart_from_check.setChecked(True)
                    dialog.restart_from_line.setValue(int(options.get("restart_from_line", 1)))

                if dialog.exec():
                    new_data = dialog.get_data()

                    # Обновляем данные модуля
                    module.data.update(new_data)

                    # Обновляем отображение в таблице
                    status = "Включен" if new_data["enabled"] else "Отключен"
                    new_description = f"Статус: {status}, Действие: {new_data['action']}"
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
        """Перемещает выбранный модуль вверх по списку"""
        selected_rows = self.modules_table.selectedIndexes()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # Проверяем, не первая ли это строка (не считая Activity)
        if current_row <= 0 or (current_row == 1 and self.modules_data[0].module_type == "Activity"):
            return

        # Если первый модуль - Activity, то нужно учесть это при перемещении
        if self.modules_data[0].module_type == "Activity" and current_row == 1:
            return  # Нельзя поменять местами с Activity

        try:
            # Меняем местами в списке данных
            self.modules_data[current_row], self.modules_data[current_row - 1] = \
                self.modules_data[current_row - 1], self.modules_data[current_row]

            # Запоминаем содержимое виджетов-кнопок для обоих строк
            current_row_button_data = self._create_button_data(current_row)
            above_row_button_data = self._create_button_data(current_row - 1)

            # Обновляем таблицу
            for col in range(1, 3):  # Тип и Описание
                current_item = self.modules_table.takeItem(current_row, col)
                above_item = self.modules_table.takeItem(current_row - 1, col)
                if current_item and above_item:
                    self.modules_table.setItem(current_row - 1, col, current_item)
                    self.modules_table.setItem(current_row, col, above_item)

            # Пересоздаем кнопки, вместо прямого перемещения виджетов
            self._recreate_action_buttons(current_row, above_row_button_data)
            self._recreate_action_buttons(current_row - 1, current_row_button_data)

            # Перенумеровываем строки
            self.renumber_rows()

            # Выделяем перемещенную строку
            self.modules_table.selectRow(current_row - 1)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении модуля: {str(e)}")

    def move_module_down(self):
        """Перемещает выбранный модуль вниз по списку"""
        selected_rows = self.modules_table.selectedIndexes()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # Проверяем, не последняя ли это строка
        if current_row >= self.modules_table.rowCount() - 1:
            return

        # Если первый модуль - Activity, и выбрана эта строка, нельзя двигать её вниз
        if self.modules_data[0].module_type == "Activity" and current_row == 0:
            return

        try:
            # Меняем местами в списке данных
            self.modules_data[current_row], self.modules_data[current_row + 1] = \
                self.modules_data[current_row + 1], self.modules_data[current_row]

            # Запоминаем содержимое виджетов-кнопок для обоих строк
            current_row_button_data = self._create_button_data(current_row)
            below_row_button_data = self._create_button_data(current_row + 1)

            # Обновляем таблицу
            for col in range(1, 3):  # Тип и Описание
                current_item = self.modules_table.takeItem(current_row, col)
                below_item = self.modules_table.takeItem(current_row + 1, col)
                if current_item and below_item:
                    self.modules_table.setItem(current_row + 1, col, current_item)
                    self.modules_table.setItem(current_row, col, below_item)

            # Пересоздаем кнопки, вместо прямого перемещения виджетов
            self._recreate_action_buttons(current_row, below_row_button_data)
            self._recreate_action_buttons(current_row + 1, current_row_button_data)

            # Перенумеровываем строки
            self.renumber_rows()

            # Выделяем перемещенную строку
            self.modules_table.selectRow(current_row + 1)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении модуля: {str(e)}")

    def delete_selected_module(self):
        """Удаляет выбранный модуль из таблицы"""
        selected_rows = self.modules_table.selectedItems()
        if not selected_rows:
            return

        current_row = selected_rows[0].row()

        # Если это Activity и модуль находится в строке 0, просто сбрасываем его настройки
        if current_row == 0 and self.modules_data[0].module_type == "Activity":
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Модуль Activity нельзя удалить, но можно отключить. Хотите отключить этот модуль?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Отключаем модуль Activity
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
            # Удаляем строку из таблицы
            self.modules_table.removeRow(current_row)

            # Удаляем данные модуля
            del self.modules_data[current_row]

            # Перенумеровываем строки
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
        """Загружает существующего бота для редактирования"""
        try:
            config_path = os.path.join(bot_path, "config.json")

            if not os.path.exists(config_path):
                QMessageBox.warning(self, "Ошибка", "Файл конфигурации бота не найден")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                bot_config = json.load(f)

            # Очищаем текущие данные
            self.modules_table.setRowCount(0)
            self.modules_data.clear()

            # Устанавливаем название и игру
            bot_name = bot_config.get("name", "")
            game_name = bot_config.get("game", "")

            self.bot_name_input.setText(bot_name)

            # Устанавливаем игру в комбобокс
            game_index = self.game_combo.findText(game_name)
            if game_index >= 0:
                self.game_combo.setCurrentIndex(game_index)

            # Загружаем модули
            modules = bot_config.get("modules", [])

            for module_data in modules:
                module_type = module_data.get("type", "")

                if module_type == "click":
                    # Добавляем модуль клика
                    description = f"({module_data['x']}, {module_data['y']}) {module_data.get('description', '')}"
                    self.add_module_to_table("Клик", description, module_data)

                elif module_type == "swipe":
                    # Добавляем модуль свайпа
                    description = f"({module_data['x1']}, {module_data['y1']}) → ({module_data['x2']}, {module_data['y2']}) {module_data.get('description', '')}"
                    self.add_module_to_table("Свайп", description, module_data)

                elif module_type == "image_search":
                    # Добавляем модуль поиска изображения
                    images_str = ", ".join(module_data.get("images", []))
                    description = f"Поиск: {images_str} (таймаут: {module_data.get('timeout', 0)} сек)"
                    self.add_module_to_table("Поиск картинки", description, module_data)

                elif module_type == "activity":
                    # Добавляем модуль Activity
                    status = "Включен" if module_data.get("enabled", False) else "Отключен"
                    description = f"Статус: {status}, Действие: {module_data.get('action', '')}"

                    # Activity всегда добавляем в начало
                    self.modules_table.insertRow(0)
                    self.modules_table.setItem(0, 0, QTableWidgetItem("0"))
                    self.modules_table.setItem(0, 1, QTableWidgetItem("Activity"))
                    self.modules_table.setItem(0, 2, QTableWidgetItem(description))

                    # Добавляем кнопки действий
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(0, 0, 0, 0)
                    actions_layout.setSpacing(2)

                    edit_btn = QPushButton("Изменить")
                    edit_btn.clicked.connect(lambda: self.edit_module(0))
                    actions_layout.addWidget(edit_btn)

                    self.modules_table.setCellWidget(0, 3, actions_widget)

                    # Добавляем в список данных
                    self.modules_data.insert(0, ModuleListItem("Activity", description, module_data))

            # Перенумеровываем строки
            self.renumber_rows()

            # Запоминаем путь к текущему боту
            self.current_bot_path = bot_path

            return True

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить бота: {str(e)}")
            return False