# src/gui/modules/image_search_module_improved.py - оптимизированная версия
"""
Модуль содержит улучшенный класс диалога для настройки модуля поиска изображений.
Использует отдельные подмодули для IF Result, ELIF и IF Not Result.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout,QPushButton, QHBoxLayout, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox,
    QWidget, QFrame, QSplitter, QScrollArea, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import os
from typing import Dict, List, Any, Optional

from src.gui.modules.if_result_module import IfResultModuleDialog
from src.gui.modules.elif_module import ElifModuleDialog
from src.gui.modules.if_not_result_module import IfNotResultModuleDialog
from src.utils.style_constants import (
    SCRIPT_CANVAS_STYLE
)
from src.utils.resources import Resources
from src.utils.ui_factory import (
    create_script_button, create_group_box, create_input_field,
    create_spinbox_without_buttons, create_title_label,
    create_script_item_widget, add_script_item_buttons
)


class ScriptItemWidget(QFrame):
    """
    Виджет элемента скрипта поиска изображений.
    Упрощенная версия, использующая UI-фабрику для создания компонентов.
    """
    pass


class ImageSearchModuleDialog(QDialog):
    """
    Улучшенный диалог для настройки модуля поиска изображений.
    Более компактный, эстетичный и функциональный интерфейс.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля поиска изображений")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setModal(True)
        self.resize(900, 700)

        # Данные для холста скрипта
        self.script_items = []  # Элементы скрипта
        self.deleted_items = {}  # Для безопасного управления удалёнными элементами

        # Настройка интерфейса
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Улучшенный стиль для диалога
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
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
                selection-background-color: #FFA500;
            }
            QComboBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
                selection-background-color: #FFA500;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555;
                selection-background-color: #FFA500;
            }
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 3px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
            QTableWidget {
                background-color: #2A2A2A;
                color: white;
                gridline-color: #444;
                border: none;
            }
            QHeaderView::section {
                background-color: #333;
                color: #FFA500;
                padding: 4px;
                border: 1px solid #444;
            }
            QToolTip {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #FFA500;
                padding: 2px;
                opacity: 200;
            }
            /* Для ScrollArea */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2A2A2A;
                width: 12px;
                margin: 0px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #FFA500;
            }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
                height: 0px;
            }
        """)

        # Заголовок
        title_label = create_title_label("Настройка модуля поиска изображений", 16)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Используем сплиттер для разделения настроек изображений и холста
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)  # Запрещаем сжимать разделы до нуля

        # === Верхняя часть: Настройки изображений и таймаута ===
        self.setup_image_settings(splitter)

        # === Нижняя часть: Холст скрипта и панель инструментов ===
        self.setup_script_canvas(splitter)

        # Устанавливаем начальное соотношение сплиттера (2:3)
        splitter.setSizes([250, 400])

        layout.addWidget(splitter, 1)  # Растягиваем сплиттер на всю доступную высоту

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addStretch(1)  # Добавляем растяжку слева
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

    def setup_image_settings(self, parent):
        """Настраивает верхнюю часть диалога с настройками изображений"""
        image_settings_widget = QWidget()
        image_settings_layout = QVBoxLayout(image_settings_widget)
        image_settings_layout.setContentsMargins(0, 0, 0, 0)
        image_settings_layout.setSpacing(8)

        # Группа настроек изображений
        image_group = create_group_box("Настройка изображений для поиска")
        image_layout = QFormLayout(image_group)  # Используем FormLayout для компактности
        image_layout.setContentsMargins(8, 16, 8, 8)  # Увеличиваем верхний отступ для заголовка
        image_layout.setSpacing(6)

        # Основное изображение с кнопкой обзора в одной строке
        img_layout = QHBoxLayout()
        self.image_name = create_input_field("Введите имя изображения (например, victory.png)")
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_image)
        browse_btn.setFixedWidth(80)  # Делаем кнопку компактнее
        img_layout.addWidget(self.image_name)
        img_layout.addWidget(browse_btn)
        image_layout.addRow("Изображение:", img_layout)

        # Настройка таймаута
        self.timeout_input = create_spinbox_without_buttons(1, 3600, 120, " сек")
        image_layout.addRow("Таймаут ожидания:", self.timeout_input)

        # Добавление дополнительных изображений
        add_img_layout = QHBoxLayout()
        self.additional_image = create_input_field("Имя дополнительного изображения")
        add_img_btn = QPushButton("Добавить")
        add_img_btn.clicked.connect(self.add_additional_image)
        add_img_btn.setFixedWidth(80)  # Делаем кнопку компактнее
        browse_additional_btn = QPushButton("Обзор...")
        browse_additional_btn.clicked.connect(self.browse_additional_image)
        browse_additional_btn.setFixedWidth(80)  # Делаем кнопку компактнее
        add_img_layout.addWidget(self.additional_image)
        add_img_layout.addWidget(browse_additional_btn)
        add_img_layout.addWidget(add_img_btn)
        image_layout.addRow("Дополнительное:", add_img_layout)

        image_settings_layout.addWidget(image_group)

        # Список добавленных изображений
        images_list_group = create_group_box("Список изображений для поиска")
        images_list_layout = QVBoxLayout(images_list_group)
        images_list_layout.setContentsMargins(8, 16, 8, 8)  # Увеличиваем верхний отступ для заголовка

        self.images_list = QTableWidget(0, 2)
        self.images_list.setHorizontalHeaderLabels(["Имя изображения", ""])
        self.images_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.images_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.images_list.setColumnWidth(1, 80)  # Ширина столбца с кнопкой
        self.images_list.verticalHeader().setVisible(False)  # Скрываем вертикальные заголовки
        images_list_layout.addWidget(self.images_list)

        image_settings_layout.addWidget(images_list_group)
        parent.addWidget(image_settings_widget)

    def setup_script_canvas(self, parent):
        """Настраивает нижнюю часть диалога с холстом скрипта"""
        script_widget = QWidget()
        script_layout = QVBoxLayout(script_widget)
        script_layout.setContentsMargins(0, 0, 0, 0)
        script_layout.setSpacing(8)

        # Заголовок и панель инструментов для скрипта
        script_header = create_group_box("Настройка логики поиска изображений")
        script_header_layout = QVBoxLayout(script_header)
        script_header_layout.setContentsMargins(8, 16, 8, 8)  # Увеличиваем верхний отступ для заголовка

        script_info = QLabel(
            "Выберите действия, которые будут выполнены в зависимости от результата поиска изображений")
        script_info.setWordWrap(True)
        script_header_layout.addWidget(script_info)

        # Панель с кнопками для добавления блоков скрипта
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        add_if_result_btn = create_script_button(
            "IF Result",
            "Добавить блок, который выполняется, если изображение найдено",
            "checkmark-black",
            self.add_if_result_block
        )

        add_elif_btn = create_script_button(
            "ELIF",
            "Добавить блок, который выполняется, если найдено другое изображение",
            "elif-black",
            self.add_elif_block
        )

        add_if_not_result_btn = create_script_button(
            "IF Not Result",
            "Добавить блок, который выполняется, если изображение не найдено",
            "close-black",
            self.add_if_not_result_block
        )

        buttons_layout.addWidget(add_if_result_btn)
        buttons_layout.addWidget(add_elif_btn)
        buttons_layout.addWidget(add_if_not_result_btn)
        buttons_layout.addStretch(1)  # Добавляем растяжку справа

        script_header_layout.addLayout(buttons_layout)
        script_layout.addWidget(script_header)

        # Скролл-область для холста скрипта
        script_canvas_container = QScrollArea()
        script_canvas_container.setWidgetResizable(True)
        script_canvas_container.setFrameShape(QFrame.Shape.NoFrame)  # Убираем рамку

        self.script_canvas = QWidget()
        self.script_canvas.setStyleSheet(SCRIPT_CANVAS_STYLE)
        self.script_canvas_layout = QVBoxLayout(self.script_canvas)
        self.script_canvas_layout.setContentsMargins(8, 8, 8, 8)
        self.script_canvas_layout.setSpacing(6)
        self.script_canvas_layout.addStretch()  # Добавляем растяжку внизу

        script_canvas_container.setWidget(self.script_canvas)
        script_layout.addWidget(script_canvas_container)

        parent.addWidget(script_widget)

    def browse_image(self):
        """Открывает диалог выбора основного изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Получаем только имя файла
            file_name = os.path.basename(file_path)
            self.image_name.setText(file_name)

    def browse_additional_image(self):
        """Открывает диалог выбора дополнительного изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать дополнительное изображение", "", "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Получаем только имя файла
            file_name = os.path.basename(file_path)
            self.additional_image.setText(file_name)

    def add_additional_image(self):
        """Добавляет дополнительное изображение в список"""
        image_name = self.additional_image.text().strip()
        if not image_name:
            return

        # Проверка, есть ли уже такое изображение в списке
        for row in range(self.images_list.rowCount()):
            if self.images_list.item(row, 0).text() == image_name:
                QMessageBox.warning(self, "Предупреждение", f"Изображение '{image_name}' уже добавлено в список.")
                self.additional_image.clear()
                return

        # Функция-замыкание для создания функции удаления с сохранением индекса строки
        def create_delete_function(row_to_delete):
            return lambda: self.remove_image(row_to_delete)

        # Добавление изображения в таблицу
        row_position = self.images_list.rowCount()
        self.images_list.insertRow(row_position)
        self.images_list.setItem(row_position, 0, QTableWidgetItem(image_name))

        # Кнопка удаления
        delete_btn = QPushButton("Удалить")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border-radius: 3px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)

        delete_btn.clicked.connect(create_delete_function(row_position))
        self.images_list.setCellWidget(row_position, 1, delete_btn)

        self.additional_image.clear()

    def remove_image(self, row):
        """Удаляет изображение из списка"""
        if row < 0 or row >= self.images_list.rowCount():
            return

        # Функция-замыкание для создания новой функции удаления с обновлённым индексом
        def create_delete_function(new_row):
            return lambda: self.remove_image(new_row)

        self.images_list.removeRow(row)

        # Обновляем индексы кнопок удаления
        for i in range(self.images_list.rowCount()):
            delete_btn = self.images_list.cellWidget(i, 1)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(create_delete_function(i))

    def get_all_images(self):
        """Возвращает список всех изображений (основное + дополнительные)"""
        images = []

        # Добавляем основное изображение
        main_image = self.image_name.text().strip()
        if main_image:
            images.append(main_image)

        # Добавляем дополнительные изображения
        for row in range(self.images_list.rowCount()):
            image = self.images_list.item(row, 0).text()
            if image and image not in images:
                images.append(image)

        return images

    def add_script_item(self, item_type: str, description: str, data: Dict[str, Any] = None):
        """Добавляет элемент в холст скрипта"""
        item_index = len(self.script_items)

        # Создаем виджет элемента скрипта с использованием фабрики UI
        item_widget = create_script_item_widget(item_index, item_type, description, data or {}, self.script_canvas)

        # Создаем и добавляем кнопки управления
        edit_callback = lambda: self.edit_script_item(item_index)
        delete_callback = lambda: self.delete_script_item(item_index)
        move_up_callback = lambda: self.move_script_item_up(item_index)
        move_down_callback = lambda: self.move_script_item_down(item_index)

        buttons = add_script_item_buttons(
            item_widget,
            edit_callback,
            delete_callback,
            move_up_callback,
            move_down_callback
        )

        # Добавляем в список и на холст
        self.script_items.append(item_widget)

        # Добавляем перед растяжкой на холсте
        self.script_canvas_layout.insertWidget(self.script_canvas_layout.count() - 1, item_widget)

        # Возвращаем индекс добавленного элемента
        return item_index

    def delete_script_item(self, index: int):
        """Удаляет элемент с указанным индексом из холста скрипта"""
        if not (0 <= index < len(self.script_items)):
            return

        # Получаем виджет элемента
        item_widget = self.script_items[index]

        # Спрашиваем подтверждение
        item_type = item_widget.item_type
        reply = QMessageBox.question(
            self,
            "Удаление элемента",
            f"Вы уверены, что хотите удалить элемент '{item_type}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем из холста и списка
            self.script_canvas_layout.removeWidget(item_widget)
            # Сохраняем ссылку для предотвращения утечек памяти
            self.deleted_items[id(item_widget)] = item_widget
            # Скрываем элемент
            item_widget.hide()
            # Удаляем из списка элементов
            self.script_items.pop(index)

            # Обновляем индексы и перерисовываем
            self._update_script_items_indices()

    def move_script_item_up(self, index: int):
        """Перемещает элемент скрипта вверх"""
        if not (0 < index < len(self.script_items)):
            return

        # Меняем местами элементы в списке
        self.script_items[index - 1], self.script_items[index] = self.script_items[index], self.script_items[index - 1]

        # Обновляем индексы и перерисовываем
        self._update_script_items_indices()

    def move_script_item_down(self, index: int):
        """Перемещает элемент скрипта вниз"""
        if not (0 <= index < len(self.script_items) - 1):
            return

        # Меняем местами элементы в списке
        self.script_items[index], self.script_items[index + 1] = self.script_items[index + 1], self.script_items[index]

        # Обновляем индексы и перерисовываем
        self._update_script_items_indices()

    def _update_script_items_indices(self):
        """Обновляет индексы всех элементов скрипта и перерисовывает их"""
        # Сначала удаляем все виджеты с холста
        for item in self.script_items:
            self.script_canvas_layout.removeWidget(item)

        # Затем обновляем индексы и добавляем обратно в правильном порядке
        for i, item in enumerate(self.script_items):
            item.item_index = i
            item.index_label.setText(f"{i + 1}.")

            # Добавляем элемент на холст
            self.script_canvas_layout.insertWidget(self.script_canvas_layout.count() - 1, item)

        # Пересоздаем обработчики событий для кнопок
        self._reconnect_script_item_buttons()

    def _reconnect_script_item_buttons(self):
        """Пересоздает обработчики для кнопок всех элементов скрипта"""
        for i, item in enumerate(self.script_items):
            # Находим кнопки в основном layout, а затем в header_layout
            header_layout = item.layout().itemAt(0).layout()

            # Кнопки находятся на позициях с 3 по 6 (включительно)
            # 3 - moveUp, 4 - moveDown, 5 - edit, 6 - delete
            move_up_btn = header_layout.itemAt(3).widget()
            move_down_btn = header_layout.itemAt(4).widget()
            edit_btn = header_layout.itemAt(5).widget()
            delete_btn = header_layout.itemAt(6).widget()

            # Отключаем старые обработчики
            move_up_btn.clicked.disconnect()
            move_down_btn.clicked.disconnect()
            edit_btn.clicked.disconnect()
            delete_btn.clicked.disconnect()

            # Создаем новые обработчики с обновленным индексом
            move_up_btn.clicked.connect(lambda checked=False, idx=i: self.move_script_item_up(idx))
            move_down_btn.clicked.connect(lambda checked=False, idx=i: self.move_script_item_down(idx))
            edit_btn.clicked.connect(lambda checked=False, idx=i: self.edit_script_item(idx))
            delete_btn.clicked.connect(lambda checked=False, idx=i: self.delete_script_item(idx))

    def edit_script_item(self, index: int):
        """Редактирует элемент с указанным индексом в холсте скрипта"""
        if not (0 <= index < len(self.script_items)):
            return

        # Получаем виджет элемента
        item_widget = self.script_items[index]
        item_type = item_widget.item_type
        item_data = item_widget.item_data

        if item_type == "IF Result":
            self._edit_if_result_item(index, item_widget, item_data)
        elif item_type == "ELIF":
            self._edit_elif_item(index, item_widget, item_data)
        elif item_type == "IF Not Result":
            self._edit_if_not_result_item(index, item_widget, item_data)

    def _edit_if_result_item(self, index, item_widget, item_data):
        """Редактирует элемент IF Result"""
        # Получаем список всех изображений
        images = self.get_all_images()
        if not images:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы одно изображение для поиска")
            return

        # Открываем диалог для редактирования
        dialog = IfResultModuleDialog(images, self)
        dialog.load_data(item_data)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            selected_image = "любое изображение"
            if data.get("image"):
                selected_image = data["image"]

            description = f"Если найдено {selected_image}"

            # Собираем действия для описания
            actions = []
            if data.get("get_coords"):
                actions.append("get_coords")
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Обновляем данные и описание
            item_widget.item_data = data
            item_widget.item_description = description
            item_widget.desc_label.setText(description)

    def _edit_elif_item(self, index, item_widget, item_data):
        """Редактирует элемент ELIF"""
        # Получаем список всех изображений
        images = self.get_all_images()
        if not images:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы одно изображение для поиска")
            return

        # Открываем диалог для редактирования
        dialog = ElifModuleDialog(images, self)
        dialog.load_data(item_data)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            selected_image = data.get("image", "неизвестное изображение")
            description = f"ELIF: Если найдено {selected_image}"

            # Собираем действия для описания
            actions = []
            if data.get("get_coords"):
                actions.append("get_coords")
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Обновляем данные и описание
            item_widget.item_data = data
            item_widget.item_description = description
            item_widget.desc_label.setText(description)

    def _edit_if_not_result_item(self, index, item_widget, item_data):
        """Редактирует элемент IF Not Result"""
        # Открываем диалог для редактирования
        dialog = IfNotResultModuleDialog(self)
        dialog.load_data(item_data)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            description = "Если изображение не найдено"

            # Собираем действия для описания
            actions = []
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Обновляем данные и описание
            item_widget.item_data = data
            item_widget.item_description = description
            item_widget.desc_label.setText(description)

    def add_if_result_block(self):
        """Добавляет блок IF Result на холст"""
        # Получаем список всех изображений
        images = self.get_all_images()
        if not images:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы одно изображение для поиска")
            return

        # Открываем диалог для настройки блока IF Result
        dialog = IfResultModuleDialog(images, self)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            selected_image = "любое изображение"
            if data.get("image"):
                selected_image = data["image"]

            description = f"Если найдено {selected_image}"

            # Собираем действия для описания
            actions = []
            if data.get("get_coords"):
                actions.append("get_coords")
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Добавляем блок на холст
            self.add_script_item("IF Result", description, data)

    def add_elif_block(self):
        """Добавляет блок ELIF на холст"""
        # Проверяем наличие IF Result блока перед добавлением ELIF
        has_if_result = False
        for item in self.script_items:
            if item.item_type == "IF Result":
                has_if_result = True
                break

        if not has_if_result:
            QMessageBox.warning(self, "Внимание", "Перед добавлением ELIF необходимо добавить блок IF Result")
            return

        # Получаем список всех изображений
        images = self.get_all_images()
        if not images:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы одно изображение для поиска")
            return

        # Открываем диалог для настройки блока ELIF
        dialog = ElifModuleDialog(images, self)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            selected_image = data.get("image", "неизвестное изображение")
            description = f"ELIF: Если найдено {selected_image}"

            # Собираем действия для описания
            actions = []
            if data.get("get_coords"):
                actions.append("get_coords")
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Добавляем блок на холст
            self.add_script_item("ELIF", description, data)

    def add_if_not_result_block(self):
        """Добавляет блок IF Not Result на холст"""
        # Открываем диалог для настройки блока IF Not Result
        dialog = IfNotResultModuleDialog(self)

        if dialog.exec():
            data = dialog.get_data()
            if not data:
                return

            # Формируем описание блока
            description = "Если изображение не найдено"

            # Собираем действия для описания
            actions = []
            if data.get("continue"):
                actions.append("continue")
            if data.get("stop_bot"):
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if "actions" in data and data["actions"]:
                action_count = len(data["actions"])
                description += f" + {action_count} действий"

            # Добавляем блок на холст
            self.add_script_item("IF Not Result", description, data)

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные модуля поиска изображений"""
        # Собираем основные данные
        result = {
            "type": "image_search",
            "images": self.get_all_images(),
            "timeout": self.timeout_input.value(),
            "script_items": []
        }

        # Собираем данные из элементов скрипта
        for item in self.script_items:
            result["script_items"].append({
                "type": item.item_type,
                "data": item.item_data
            })

        return result

    def load_data(self, data: Dict[str, Any]):
        """Загружает данные для редактирования"""
        if not data:
            return

        # Загружаем основное изображение (первое из списка)
        if "images" in data and data["images"]:
            self.image_name.setText(data["images"][0])

            # Загружаем дополнительные изображения
            for i in range(1, len(data["images"])):
                self.additional_image.setText(data["images"][i])
                self.add_additional_image()

        # Загружаем таймаут
        if "timeout" in data:
            self.timeout_input.setValue(data["timeout"])

        # Очищаем холст скрипта
        for item in self.script_items:
            self.script_canvas_layout.removeWidget(item)
            item.hide()
        self.script_items.clear()

        # Загружаем элементы скрипта
        if "script_items" in data:
            for item_data in data["script_items"]:
                item_type = item_data.get("type")
                item_info = item_data.get("data", {})

                if item_type == "IF Result":
                    self._load_if_result_item(item_type, item_info)
                elif item_type == "ELIF":
                    self._load_elif_item(item_type, item_info)
                elif item_type == "IF Not Result":
                    self._load_if_not_result_item(item_type, item_info)

    def _load_if_result_item(self, item_type, item_info):
        """Загружает элемент IF Result из данных"""
        # Формируем описание блока
        selected_image = "любое изображение"
        if item_info.get("image"):
            selected_image = item_info["image"]

        description = f"Если найдено {selected_image}"

        # Собираем действия для описания
        actions = []
        if item_info.get("get_coords"):
            actions.append("get_coords")
        if item_info.get("continue"):
            actions.append("continue")
        if item_info.get("stop_bot"):
            actions.append("running.clear()")

        if actions:
            description += f" → {', '.join(actions)}"

        # Добавляем информацию о дополнительных действиях
        if "actions" in item_info and item_info["actions"]:
            action_count = len(item_info["actions"])
            description += f" + {action_count} действий"

        # Добавляем на холст
        self.add_script_item("IF Result", description, item_info)

    def _load_elif_item(self, item_type, item_info):
        """Загружает элемент ELIF из данных"""
        # Формируем описание блока
        selected_image = item_info.get("image", "неизвестное изображение")
        description = f"ELIF: Если найдено {selected_image}"

        # Собираем действия для описания
        actions = []
        if item_info.get("get_coords"):
            actions.append("get_coords")
        if item_info.get("continue"):
            actions.append("continue")
        if item_info.get("stop_bot"):
            actions.append("running.clear()")

        if actions:
            description += f" → {', '.join(actions)}"

        # Добавляем информацию о дополнительных действиях
        if "actions" in item_info and item_info["actions"]:
            action_count = len(item_info["actions"])
            description += f" + {action_count} действий"

        # Добавляем на холст
        self.add_script_item("ELIF", description, item_info)

    def _load_if_not_result_item(self, item_type, item_info):
        """Загружает элемент IF Not Result из данных"""
        # Формируем описание блока
        description = "Если изображение не найдено"

        # Собираем действия для описания
        actions = []
        if item_info.get("continue"):
            actions.append("continue")
        if item_info.get("stop_bot"):
            actions.append("running.clear()")

        if actions:
            description += f" → {', '.join(actions)}"

        # Добавляем информацию о дополнительных действиях
        if "actions" in item_info and item_info["actions"]:
            action_count = len(item_info["actions"])
            description += f" + {action_count} действий"

        # Добавляем на холст
        self.add_script_item("IF Not Result", description, item_info)

    def __del__(self):
        """Безопасное освобождение ресурсов при уничтожении объекта"""
        try:
            # Очищаем словарь удаленных элементов
            if hasattr(self, 'deleted_items'):
                for item in self.deleted_items.values():
                    if item:
                        item.deleteLater()
                self.deleted_items.clear()
        except Exception:
            # Игнорируем любые исключения при уничтожении объекта
            pass