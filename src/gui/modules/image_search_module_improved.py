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
    SCRIPT_CANVAS_STYLE, COMPACT_IMAGE_SETTINGS_STYLE,
    COLOR_BG_DARK_2, COLOR_TEXT, COLOR_PRIMARY, COLOR_BORDER, IMAGE_SEARCH_DIALOG_STYLE
)
from src.utils.resources import Resources
from src.utils.ui_factory import (
    create_script_button, create_group_box, create_input_field,
    create_spinbox_without_buttons, create_title_label,
    create_script_item_widget, add_script_item_buttons,
    create_multiple_file_dialog, create_button, create_delete_button
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
        self.resize(1100, 800)  # Увеличиваем размер окна

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
        self.setStyleSheet(IMAGE_SEARCH_DIALOG_STYLE)

        # Заголовок
        title_label = create_title_label("Настройка модуля поиска изображений", 16)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Используем горизонтальный layout для списка изображений (слева) и настроек (справа)
        main_content_layout = QHBoxLayout()

        # === Левая часть: Список изображений ===
        self.setup_images_list_panel(main_content_layout)

        # === Правая часть: Настройки изображений и холст скрипта ===
        right_panel = QVBoxLayout()

        # Раздел настроек изображений
        self.setup_compact_image_settings(right_panel)

        # Холст скрипта занимает оставшееся пространство
        self.setup_script_canvas(right_panel)

        main_content_layout.addLayout(right_panel, 2)  # Правая часть занимает 2/3 ширины

        layout.addLayout(main_content_layout, 1)  # Растягиваем по высоте

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

    def setup_images_list_panel(self, parent_layout):
        """Настраивает панель со списком изображений"""
        # Группа со списком изображений
        images_list_group = create_group_box("Список изображений для поиска")
        images_list_layout = QVBoxLayout(images_list_group)
        images_list_layout.setContentsMargins(8, 16, 8, 8)

        # Таблица с изображениями
        self.images_list = QTableWidget(0, 2)
        self.images_list.setHorizontalHeaderLabels(["Имя изображения", ""])
        self.images_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.images_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.images_list.setColumnWidth(1, 80)  # Ширина столбца с кнопкой удаления
        self.images_list.verticalHeader().setVisible(False)

        # Увеличиваем высоту строк для лучшей читаемости
        self.images_list.verticalHeader().setDefaultSectionSize(30)

        images_list_layout.addWidget(self.images_list)

        parent_layout.addWidget(images_list_group, 1)  # Левая часть занимает 1/3 ширины

    def setup_compact_image_settings(self, parent_layout):
        """Настраивает компактную панель настроек изображений"""
        image_settings_group = create_group_box("Настройка изображений для поиска")
        image_settings_group.setStyleSheet(COMPACT_IMAGE_SETTINGS_STYLE)
        image_settings_layout = QVBoxLayout(image_settings_group)
        image_settings_layout.setContentsMargins(8, 16, 8, 8)
        image_settings_layout.setSpacing(6)

        # Основное изображение с кнопкой "Обзор" в одной строке
        img_layout = QHBoxLayout()
        img_layout.setSpacing(5)

        # Метка и поле ввода
        img_label = QLabel("Изображение:")
        img_label.setFixedWidth(80)
        self.image_name = create_input_field("Введите имя изображения (например, victory.png)")

        # Обработка ручного ввода по нажатию Enter
        self.image_name.returnPressed.connect(self.add_image_from_input)

        # Кнопка "Обзор"
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_multiple_images)
        browse_btn.setFixedWidth(80)

        img_layout.addWidget(img_label)
        img_layout.addWidget(self.image_name, 1)  # 1 - коэффициент растяжения
        img_layout.addWidget(browse_btn)

        image_settings_layout.addLayout(img_layout)

        # Настройка таймаута
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Таймаут ожидания:")
        timeout_label.setFixedWidth(120)
        self.timeout_input = create_spinbox_without_buttons(1, 3600, 120, " сек")

        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input, 1)

        image_settings_layout.addLayout(timeout_layout)

        parent_layout.addWidget(image_settings_group)

    def browse_multiple_images(self):
        """Открывает диалог выбора нескольких изображений и сразу добавляет их в список"""
        files = create_multiple_file_dialog("Выбрать изображения", "Изображения (*.png *.jpg *.jpeg)")

        if files:
            # Добавляем все выбранные файлы сразу в список
            for file_path in files:
                # Получаем только имя файла
                file_name = os.path.basename(file_path)
                self.add_image_to_list(file_name)

            # Очищаем поле ввода после добавления
            self.image_name.clear()

    def add_image_from_input(self):
        """Добавляет изображение из поля ввода в список"""
        image_name = self.image_name.text().strip()
        if image_name:
            self.add_image_to_list(image_name)
            self.image_name.clear()

    def add_image_to_list(self, image_name):
        """Добавляет изображение в список"""
        # Проверка, есть ли уже такое изображение в списке
        for row in range(self.images_list.rowCount()):
            if self.images_list.item(row, 0).text() == image_name:
                QMessageBox.warning(self, "Предупреждение", f"Изображение '{image_name}' уже добавлено в список.")
                return

        # Функция-замыкание для создания функции удаления с сохранением индекса строки
        def create_delete_function(row_to_delete):
            return lambda: self.remove_image(row_to_delete)

        # Добавление изображения в таблицу
        row_position = self.images_list.rowCount()
        self.images_list.insertRow(row_position)
        self.images_list.setItem(row_position, 0, QTableWidgetItem(image_name))

        # Кнопка удаления
        delete_btn = create_delete_button("Удалить")

        delete_btn.clicked.connect(create_delete_function(row_position))
        self.images_list.setCellWidget(row_position, 1, delete_btn)

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
        """Возвращает список всех изображений из таблицы"""
        images = []

        # Собираем изображения из таблицы
        for row in range(self.images_list.rowCount()):
            image = self.images_list.item(row, 0).text()
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

        # Загружаем таймаут
        if "timeout" in data:
            self.timeout_input.setValue(data["timeout"])

        # Загружаем изображения
        if "images" in data and data["images"]:
            for image in data["images"]:
                self.add_image_to_list(image)

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