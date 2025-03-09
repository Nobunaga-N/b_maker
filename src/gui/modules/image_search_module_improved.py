# src/gui/modules/image_search_module_improved.py
"""
Модуль содержит улучшенный класс диалога для настройки модуля поиска изображений.
Использует отдельные подмодули для IF Result, ELIF и IF Not Result.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame, QSplitter, QToolButton, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QIcon, QFont, QAction

import os
from typing import Dict, List, Any, Optional

from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.gui.modules.if_result_module import IfResultModuleDialog
from src.gui.modules.elif_module import ElifModuleDialog
from src.gui.modules.if_not_result_module import IfNotResultModuleDialog
from src.gui.modules.canvas_module import ModuleItem
from src.utils.style_constants import FULL_DIALOG_STYLE


class ScriptItemWidget(ModuleItem):
    """
    Виджет элемента скрипта поиска изображений.
    Наследуется от ModuleItem для сохранения обратной совместимости.
    """
    pass


class ImageSearchModuleDialog(QDialog):
    """
    Улучшенный диалог для настройки модуля поиска изображений.
    Позволяет пользователю настроить поиск одного или нескольких изображений
    и задать логику обработки результатов поиска с помощью холста и подмодулей.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля поиска изображений")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setModal(True)
        self.resize(900, 700)

        # Данные для холста скрипта
        self.script_items = []  # Элементы скрипта

        # Состояние полноэкранного режима
        self.is_fullscreen = False
        self.normal_geometry = None

        # Настройка интерфейса
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Используем полный стиль для диалога с таблицами и табами
        self.setStyleSheet(FULL_DIALOG_STYLE)

        # Заголовок с кнопкой полноэкранного режима
        title_layout = QHBoxLayout()
        title_label = QLabel("Настройка модуля поиска изображений")
        title_label.setStyleSheet("color: #FFA500; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title_label)

        layout.addLayout(title_layout)

        # Используем сплиттер для разделения настроек изображений и холста
        splitter = QSplitter(Qt.Orientation.Vertical)

        # === Верхняя часть: Настройки изображений и таймаута ===
        image_settings_widget = QWidget()
        image_settings_layout = QVBoxLayout(image_settings_widget)

        # Выбор изображения
        image_group = QGroupBox("Выбор изображения и настройка таймаута")
        image_layout = QVBoxLayout(image_group)

        # Основное изображение
        hbox = QHBoxLayout()
        img_label = QLabel("Изображение:")
        self.image_name = QLineEdit()
        self.image_name.setPlaceholderText("Введите имя изображения (например, victory.png)")
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_image)
        hbox.addWidget(img_label)
        hbox.addWidget(self.image_name, 1)
        hbox.addWidget(browse_btn)
        image_layout.addLayout(hbox)

        # Настройка таймаута
        hbox2 = QHBoxLayout()
        timeout_label = QLabel("Таймаут (ожидание изображения):")
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 3600)
        self.timeout_input.setValue(120)  # По умолчанию 120 секунд (2 минуты)
        self.timeout_input.setSuffix(" сек")
        self.timeout_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        hbox2.addWidget(timeout_label)
        hbox2.addWidget(self.timeout_input)
        hbox2.addStretch(1)
        image_layout.addLayout(hbox2)

        # Добавление дополнительных изображений
        hbox_add = QHBoxLayout()
        add_img_label = QLabel("Дополнительное изображение:")
        self.additional_image = QLineEdit()
        self.additional_image.setPlaceholderText("Имя дополнительного изображения")
        add_img_btn = QPushButton("Добавить")
        add_img_btn.clicked.connect(self.add_additional_image)
        browse_additional_btn = QPushButton("Обзор...")
        browse_additional_btn.clicked.connect(self.browse_additional_image)
        hbox_add.addWidget(add_img_label)
        hbox_add.addWidget(self.additional_image, 1)
        hbox_add.addWidget(browse_additional_btn)
        hbox_add.addWidget(add_img_btn)
        image_layout.addLayout(hbox_add)

        # Список добавленных изображений
        img_list_label = QLabel("Список изображений для поиска:")
        image_layout.addWidget(img_list_label)

        self.images_list = QTableWidget(0, 2)
        self.images_list.setHorizontalHeaderLabels(["Имя изображения", ""])
        self.images_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.images_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.images_list.setColumnWidth(1, 100)
        image_layout.addWidget(self.images_list)

        image_settings_layout.addWidget(image_group)
        splitter.addWidget(image_settings_widget)

        # === Нижняя часть: Холст скрипта и панель инструментов ===
        script_widget = QWidget()
        script_layout = QVBoxLayout(script_widget)

        # Панель инструментов для холста
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)

        # Заголовок для холста
        canvas_label = QLabel("Рабочий холст для скрипта поиска изображений")
        canvas_label.setStyleSheet("color: #FFA500; font-size: 14px; font-weight: bold;")
        toolbar_layout.addWidget(canvas_label)

        toolbar_layout.addStretch(1)  # Растягиваем между заголовком и кнопками

        # Кнопки для добавления элементов скрипта
        add_if_result_btn = QPushButton("Добавить IF Result")
        add_if_result_btn.setIcon(QIcon("assets/icons/checkmark-black.svg"))
        add_if_result_btn.clicked.connect(self.add_if_result_block)

        add_elif_btn = QPushButton("Добавить ELIF")
        add_elif_btn.setIcon(QIcon("assets/icons/elif-black.svg"))
        add_elif_btn.clicked.connect(self.add_elif_block)

        add_if_not_result_btn = QPushButton("Добавить IF Not Result")
        add_if_not_result_btn.setIcon(QIcon("assets/icons/close-black.svg"))
        add_if_not_result_btn.clicked.connect(self.add_if_not_result_block)

        toolbar_layout.addWidget(add_if_result_btn)
        toolbar_layout.addWidget(add_elif_btn)
        toolbar_layout.addWidget(add_if_not_result_btn)

        script_layout.addLayout(toolbar_layout)

        # Холст для скрипта
        self.script_canvas = QWidget()
        self.script_canvas_layout = QVBoxLayout(self.script_canvas)
        self.script_canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.script_canvas_layout.setSpacing(5)
        self.script_canvas_layout.addStretch()  # Добавляем растяжку внизу

        # Заворачиваем холст в скролл область
        scroll_area = QFrame()
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self.script_canvas)

        script_layout.addWidget(scroll_area, 1)  # Растягиваем холст

        splitter.addWidget(script_widget)

        # Устанавливаем начальное соотношение сплиттера (1:2)
        splitter.setSizes([200, 400])

        layout.addWidget(splitter, 1)  # Растягиваем сплиттер

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

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

        # Добавление изображения в таблицу
        row_position = self.images_list.rowCount()
        self.images_list.insertRow(row_position)
        self.images_list.setItem(row_position, 0, QTableWidgetItem(image_name))

        # Кнопка удаления
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.remove_image(row_position))
        self.images_list.setCellWidget(row_position, 1, delete_btn)

        self.additional_image.clear()

    def remove_image(self, row):
        """Удаляет изображение из списка"""
        self.images_list.removeRow(row)

        # Обновляем индексы кнопок удаления
        for i in range(row, self.images_list.rowCount()):
            delete_btn = self.images_list.cellWidget(i, 1)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(lambda checked=False, r=i: self.remove_image(r))

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

        # Создаем виджет элемента скрипта
        item_widget = ScriptItemWidget(item_index, item_type, description)

        # Если есть дополнительные данные, сохраняем их
        if data:
            item_widget.set_data(data)

        # Подключаем сигналы
        item_widget.deleteRequested.connect(self.delete_script_item)
        item_widget.editRequested.connect(self.edit_script_item)
        item_widget.moveUpRequested.connect(self.move_script_item_up)
        item_widget.moveDownRequested.connect(self.move_script_item_down)

        # Добавляем в список и на холст
        self.script_items.append(item_widget)

        # Добавляем перед растяжкой на холсте
        self.script_canvas_layout.insertWidget(self.script_canvas_layout.count() - 1, item_widget)

        # Возвращаем индекс добавленного элемента
        return item_index

    def delete_script_item(self, index: int):
        """Удаляет элемент с указанным индексом из холста скрипта"""
        if 0 <= index < len(self.script_items):
            # Получаем виджет элемента
            item_widget = self.script_items[index]

            # Спрашиваем подтверждение
            item_type = item_widget.module_type
            reply = QMessageBox.question(
                self,
                "Удаление элемента",
                f"Вы уверены, что хотите удалить элемент '{item_type}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Удаляем из холста и списка
                self.script_canvas_layout.removeWidget(item_widget)
                item_widget.deleteLater()
                self.script_items.pop(index)

                # Обновляем индексы оставшихся элементов
                for i, item in enumerate(self.script_items):
                    item.index = i

    def move_script_item_up(self, index: int):
        """Перемещает элемент скрипта вверх"""
        if 0 < index < len(self.script_items):
            # Запоминаем элементы для обмена
            current_item = self.script_items[index]
            prev_item = self.script_items[index - 1]

            # Меняем местами в списке
            self.script_items[index] = prev_item
            self.script_items[index - 1] = current_item

            # Обновляем индексы
            current_item.index = index - 1
            prev_item.index = index

            # Перерисовываем элементы на холсте
            self._redraw_script_items()

    def move_script_item_down(self, index: int):
        """Перемещает элемент скрипта вниз"""
        if 0 <= index < len(self.script_items) - 1:
            # Запоминаем элементы для обмена
            current_item = self.script_items[index]
            next_item = self.script_items[index + 1]

            # Меняем местами в списке
            self.script_items[index] = next_item
            self.script_items[index + 1] = current_item

            # Обновляем индексы
            current_item.index = index + 1
            next_item.index = index

            # Перерисовываем элементы на холсте
            self._redraw_script_items()

    def _redraw_script_items(self):
        """Перерисовывает все элементы на холсте скрипта"""
        # Удаляем все виджеты с холста
        for item in self.script_items:
            self.script_canvas_layout.removeWidget(item)

        # Добавляем виджеты обратно в правильном порядке
        for item in self.script_items:
            self.script_canvas_layout.insertWidget(self.script_canvas_layout.count() - 1, item)

    def add_if_result_block(self):
        """Добавляет блок IF Result на холст"""
        # Получаем список всех изображений
        images = self.get_all_images()
        if not images:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы одно изображение для поиска")
            return

        # Открываем диалог для настройки блока IF Result
        dialog = IfResultModuleDialog(images, self)

        # Смещаем диалог относительно родительского
        dialog_pos = self.mapToGlobal(self.rect().center())
        dialog.move(dialog_pos.x() - dialog.width() // 2 + 50, dialog_pos.y() - dialog.height() // 2 + 50)

        # Меняем стиль кнопок для визуального различия
        dialog.ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF8C00; /* более яркий оранжевый */
                    color: black;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFA54F;
                }
            """)

        # Добавляем указание в заголовок
        dialog.setWindowTitle("Подмодуль IF Result - настройка")

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
            if item.module_type == "IF Result":
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
        # Смещаем диалог относительно родительского
        dialog_pos = self.mapToGlobal(self.rect().center())
        dialog.move(dialog_pos.x() - dialog.width() // 2 + 50, dialog_pos.y() - dialog.height() // 2 + 50)

        # Меняем стиль кнопок для визуального различия
        dialog.ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF8C00; /* более яркий оранжевый */
                    color: black;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFA54F;
                }
            """)

        # Добавляем указание в заголовок
        dialog.setWindowTitle("Подмодуль Elif - настройка")
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
        # Смещаем диалог относительно родительского
        dialog_pos = self.mapToGlobal(self.rect().center())
        dialog.move(dialog_pos.x() - dialog.width() // 2 + 50, dialog_pos.y() - dialog.height() // 2 + 50)

        # Меняем стиль кнопок для визуального различия
        dialog.ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF8C00; /* более яркий оранжевый */
                    color: black;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFA54F;
                }
            """)

        # Добавляем указание в заголовок
        dialog.setWindowTitle("Подмодуль IF not Result - настройка")
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

    def edit_script_item(self, index: int):
        """Редактирует элемент с указанным индексом в холсте скрипта"""
        if 0 <= index < len(self.script_items):
            # Получаем виджет элемента
            item_widget = self.script_items[index]
            item_type = item_widget.module_type
            item_data = item_widget.get_data() or {}

            if item_type == "IF Result":
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
                    item_widget.description = description
                    item_widget.set_data(data)

                    # Принудительно перерисовываем элементы
                    self._redraw_script_items()

            elif item_type == "ELIF":
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
                    item_widget.description = description
                    item_widget.set_data(data)

                    # Принудительно перерисовываем элементы
                    self._redraw_script_items()

            elif item_type == "IF Not Result":
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
                    item_widget.description = description
                    item_widget.set_data(data)

                    # Принудительно перерисовываем элементы
                    self._redraw_script_items()

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
            item_data = item.get_data()
            if item_data:
                result["script_items"].append({
                    "type": item.module_type,
                    "data": item_data
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

        # Загружаем элементы скрипта
        if "script_items" in data:
            for item_data in data["script_items"]:
                item_type = item_data.get("type")
                item_info = item_data.get("data", {})

                if item_type == "IF Result":
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

                elif item_type == "ELIF":
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

                elif item_type == "IF Not Result":
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