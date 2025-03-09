# src/gui/modules/if_result_module.py
"""
Модуль для подмодуля IF Result, используемого в модуле поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.gui.modules.canvas_module import CanvasModule
from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog


class IfResultCanvas(CanvasModule):
    """
    Холст для создания логики IF Result.
    Наследуется от универсального холста и добавляет специфические модули.
    """

    def __init__(self, parent=None):
        super().__init__("Редактор логики IF Result", parent)

    def create_tool_buttons(self, layout):
        """Создает кнопки инструментов для холста IF Result"""
        # Кнопка добавления клика
        self.btn_add_click = QPushButton("Добавить клик")
        self.btn_add_click.setIcon(QIcon("assets/icons/pointer-arrow-icon.svg"))
        self.btn_add_click.clicked.connect(self.add_click_module)
        layout.addWidget(self.btn_add_click)

        # Кнопка добавления свайпа
        self.btn_add_swipe = QPushButton("Добавить свайп")
        self.btn_add_swipe.setIcon(QIcon("assets/icons/swipe-black.svg"))
        self.btn_add_swipe.clicked.connect(self.add_swipe_module)
        layout.addWidget(self.btn_add_swipe)

        # Кнопка добавления get_coords
        self.btn_add_get_coords = QPushButton("get_coords")
        self.btn_add_get_coords.setIcon(QIcon("assets/icons/get-coords.svg"))
        self.btn_add_get_coords.clicked.connect(self.add_get_coords_module)
        layout.addWidget(self.btn_add_get_coords)

        # Кнопка добавления паузы
        self.btn_add_sleep = QPushButton("time_sleep")
        self.btn_add_sleep.setIcon(QIcon("assets/icons/pause-black.svg"))
        self.btn_add_sleep.clicked.connect(self.add_sleep_module)
        layout.addWidget(self.btn_add_sleep)

        # Кнопка добавления continue
        self.btn_add_continue = QPushButton("continue")
        self.btn_add_continue.setIcon(QIcon("assets/icons/continue-black.svg"))
        self.btn_add_continue.clicked.connect(self.add_continue_module)
        layout.addWidget(self.btn_add_continue)

        # Кнопка добавления running.clear()
        self.btn_add_running_clear = QPushButton("running.clear()")
        self.btn_add_running_clear.setIcon(QIcon("assets/icons/stop-black.svg"))
        self.btn_add_running_clear.clicked.connect(self.add_running_clear_module)
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
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)
        dialog.resize(300, 150)

        layout = QVBoxLayout(dialog)

        # Спиннер для времени
        input_layout = QHBoxLayout()
        time_label = QLabel("Время задержки (сек):")
        time_spinner = QDoubleSpinBox()
        time_spinner.setRange(0.1, 60.0)
        time_spinner.setValue(1.0)
        time_spinner.setDecimals(1)
        time_spinner.setSingleStep(0.1)
        time_spinner.setSuffix(" сек")

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
            data = {"type": "sleep", "time": time_value}
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

    def edit_module(self, index: int):
        from PyQt6.QtWidgets import QLabel
        """Редактирует модуль на холсте"""
        if 0 <= index < len(self.modules):
            module = self.modules[index]
            module_type = module.module_type
            data = module.get_data()

            if module_type == "Клик":
                dialog = ClickModuleDialog(self)

                # Заполняем диалог текущими данными
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
                    for key, value in new_data.items():
                        data[key] = value

                    # Обновляем отображение
                    description = f"Клик по координатам ({data['x']}, {data['y']})"
                    if data.get('description'):
                        description += f" - {data['description']}"
                    if data.get('sleep') > 0:
                        description += f" с задержкой {data['sleep']} сек"

                    module.description = description
                    module.set_data(data)

                    # Обновляем текст в виджете
                    for i in range(module.layout().count()):
                        item = module.layout().itemAt(i)
                        if item.widget() and isinstance(item.widget(), QLabel):
                            item.widget().setText(description)
                            break

                    # Принудительно перерисовываем модули
                    self._redraw_modules()

                    # Испускаем сигнал об изменении
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            elif module_type == "Свайп":
                dialog = SwipeModuleDialog(self)

                # Заполняем диалог текущими данными
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
                    for key, value in new_data.items():
                        data[key] = value

                    # Обновляем отображение
                    description = f"Свайп ({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']})"
                    if data.get('description'):
                        description += f" - {data['description']}"
                    if data.get('sleep') > 0:
                        description += f" с задержкой {data['sleep']} сек"

                    module.description = description
                    module.set_data(data)

                    # Обновляем текст в виджете
                    for i in range(module.layout().count()):
                        item = module.layout().itemAt(i)
                        if item.widget() and isinstance(item.widget(), QLabel):
                            item.widget().setText(description)
                            break

                    # Принудительно перерисовываем модули
                    self._redraw_modules()

                    # Испускаем сигнал об изменении
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            elif module_type == "Пауза":
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox

                dialog = QDialog(self)
                dialog.setWindowTitle("Редактировать паузу")
                dialog.setModal(True)
                dialog.resize(300, 150)

                layout = QVBoxLayout(dialog)

                # Спиннер для времени
                input_layout = QHBoxLayout()
                time_label = QLabel("Время задержки (сек):")
                time_spinner = QDoubleSpinBox()
                time_spinner.setRange(0.1, 60.0)
                time_spinner.setValue(data.get("time", 1.0))
                time_spinner.setDecimals(1)
                time_spinner.setSingleStep(0.1)
                time_spinner.setSuffix(" сек")

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
                    data["time"] = time_value

                    module.description = description
                    module.set_data(data)

                    # Обновляем текст в виджете
                    for i in range(module.layout().count()):
                        item = module.layout().itemAt(i)
                        if item.widget() and isinstance(item.widget(), QLabel):
                            item.widget().setText(description)
                            break

                    # Принудительно перерисовываем модули
                    self._redraw_modules()

                    # Испускаем сигнал об изменении
                    self.moduleEdited.emit(index, module_type, description, data)
                    self.canvasChanged.emit()

            # Остальные типы модулей (get_coords, continue, running.clear())
            # не требуют сложного редактирования, у них нет настраиваемых параметров


class IfResultModuleDialog(QDialog):
    """
    Диалог для настройки подмодуля IF Result.
    Позволяет выбрать изображение, настроить сообщение и действия.
    """

    def __init__(self, images_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка блока IF Result")
        self.setModal(True)
        self.resize(800, 600)

        self.images_list = images_list  # Список доступных изображений
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        # Применяем специальный стиль для вложенного диалога
        self.setStyleSheet("""
                        QDialog {
                            background-color: #1A1A1A; /* Немного темнее фон */
                            border: 2px solid #FF8C00; /* Оранжевая рамка */
                        }
                        QPushButton {
                            background-color: #FF8C00;
                            color: black;
                            border-radius: 4px;
                            padding: 8px 16px;
                            font-weight: bold;
                        }
                        QGroupBox {
                            border: 1px solid #FF8C00;
                        }
                    """)

        # Добавляем WindowMinMaxButtonsHint для стандартных кнопок окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)

        # --- 1. Настройки изображения и основных параметров ---
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout(settings_group)

        # Выбор изображения
        image_layout = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        self.image_combo = QComboBox()
        self.image_combo.addItem("Любое найденное изображение")
        self.image_combo.addItems(self.images_list)

        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_combo, 1)
        settings_layout.addLayout(image_layout)

        # Сообщение в консоль
        log_layout = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        self.log_input = QLineEdit()
        self.log_input.setText("Изображение найдено!")
        self.log_input.setPlaceholderText("Например: Изображение победы найдено!")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_input, 1)
        settings_layout.addLayout(log_layout)

        layout.addWidget(settings_group)

        # --- 2. Холст для дополнительных действий ---
        action_group = QGroupBox("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)

        self.canvas = IfResultCanvas(self)
        action_layout.addWidget(self.canvas)

        layout.addWidget(action_group)

        # --- 3. Кнопки диалога ---
        buttons_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn = QPushButton("Подтвердить")

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.ok_btn)

        layout.addLayout(buttons_layout)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        image = None
        if self.image_combo.currentIndex() > 0:
            image = self.image_combo.currentText()

        data = {
            "type": "if_result",
            "image": image,
            "log_event": self.log_input.text(),
            "actions": self.canvas.get_modules_data()
        }

        return data

    def load_data(self, data):
        """Загружает данные для редактирования"""
        # Изображение
        if data.get("image"):
            index = self.image_combo.findText(data["image"])
            if index >= 0:
                self.image_combo.setCurrentIndex(index)

        # Сообщение в консоль
        if "log_event" in data:
            self.log_input.setText(data["log_event"])

        # Загружаем действия в холст
        if "actions" in data:
            self.canvas.load_modules_data(data["actions"])