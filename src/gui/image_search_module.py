# src/gui/image_search_module.py
"""
Модуль содержит класс диалога для настройки модуля поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame, QSplitter, QToolButton, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction

import os
from typing import Dict, List, Any, Optional

from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog
from src.utils.style_constants import FULL_DIALOG_STYLE


class ScriptItemWidget(QFrame):
    """
    Виджет элемента скрипта поиска изображений.
    Представляет один элемент в холсте скрипта (if, elif, else и др.)
    """
    deleteRequested = pyqtSignal(int)  # Сигнал для запроса удаления (с индексом)
    editRequested = pyqtSignal(int)  # Сигнал для запроса редактирования (с индексом)

    def __init__(self, index: int, item_type: str, description: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.item_type = item_type
        self.description = description
        self.data = {}  # Для хранения дополнительных данных

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс элемента скрипта"""
        # Устанавливаем стиль рамки
        self.setStyleSheet("""
            ScriptItemWidget {
                background-color: #2C2C2C;
                border: 1px solid #555;
                border-radius: 4px;
                margin: 2px;
            }
            QLabel {
                color: white;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                color: white;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Создаем лейбл с типом элемента (жирный)
        type_label = QLabel(self.item_type)
        type_label.setStyleSheet("font-weight: bold; color: #FFA500;")

        # Создаем лейбл с описанием
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)

        # Создаем кнопки для управления элементом
        edit_btn = QToolButton()
        edit_btn.setIcon(QIcon("assets/icons/edit.svg"))
        edit_btn.setToolTip("Редактировать")
        edit_btn.clicked.connect(lambda: self.editRequested.emit(self.index))

        delete_btn = QToolButton()
        delete_btn.setIcon(QIcon("assets/icons/delete.svg"))
        delete_btn.setToolTip("Удалить")
        delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self.index))

        # Добавляем элементы в layout
        layout.addWidget(type_label)
        layout.addWidget(desc_label, 1)  # Растягиваем описание
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

    def set_data(self, data: Dict[str, Any]):
        """Устанавливает дополнительные данные для элемента"""
        self.data = data


class ImageSearchModuleDialog(QDialog):
    """
    Диалог для настройки модуля поиска изображений.
    Позволяет пользователю настроить поиск одного или нескольких изображений
    и задать логику обработки результатов поиска с помощью холста.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля поиска изображений")
        self.setModal(True)
        self.resize(900, 700)

        # Данные для холста скрипта
        self.script_items = []  # Элементы скрипта

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Используем полный стиль для диалога с таблицами и табами
        self.setStyleSheet(FULL_DIALOG_STYLE)

        # Заголовок
        title_label = QLabel("Настройка модуля поиска изображений")
        title_label.setStyleSheet("color: #FFA500; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

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
        add_if_result_btn.setIcon(QIcon("assets/icons/create.svg"))
        add_if_result_btn.clicked.connect(self.add_if_result_block)

        add_elif_btn = QPushButton("Добавить ELIF")
        add_elif_btn.setIcon(QIcon("assets/icons/create.svg"))
        add_elif_btn.clicked.connect(self.add_elif_block)

        add_if_not_result_btn = QPushButton("Добавить IF Not Result")
        add_if_not_result_btn.setIcon(QIcon("assets/icons/create.svg"))
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
                item_widget.deleteLater()
                self.script_items.pop(index)

                # Обновляем индексы оставшихся элементов
                for i, item in enumerate(self.script_items):
                    item.index = i

    def edit_script_item(self, index: int):
        """Редактирует элемент с указанным индексом в холсте скрипта"""
        if 0 <= index < len(self.script_items):
            # Получаем виджет элемента
            item_widget = self.script_items[index]
            item_type = item_widget.item_type

            # В зависимости от типа открываем нужный диалог редактирования
            if item_type == "IF Result":
                self.edit_if_result_block(index)
            elif item_type == "ELIF":
                self.edit_elif_block(index)
            elif item_type == "IF Not Result":
                self.edit_if_not_result_block(index)

    def add_if_result_block(self):
        """Добавляет блок IF Result на холст"""
        # Открываем диалог для настройки блока IF Result
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка блока IF Result")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # Выбор конкретного изображения для этого блока
        hbox_image = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        image_combo = QComboBox()
        image_combo.addItem("Любое найденное изображение")

        # Добавляем все доступные изображения
        main_image = self.image_name.text().strip()
        if main_image:
            image_combo.addItem(main_image)

        for row in range(self.images_list.rowCount()):
            image_name = self.images_list.item(row, 0).text()
            if image_name not in [main_image]:  # Избегаем дубликатов
                image_combo.addItem(image_name)

        hbox_image.addWidget(image_label)
        hbox_image.addWidget(image_combo)
        layout.addLayout(hbox_image)

        # Настройка сообщения в консоль
        hbox_log = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        log_input = QLineEdit()
        log_input.setText("Изображение найдено!")
        log_input.setPlaceholderText("Например: Победа найдена!")
        hbox_log.addWidget(log_label)
        hbox_log.addWidget(log_input)
        layout.addLayout(hbox_log)

        # Чекбоксы для действий
        actions_group = QGroupBox("Выберите действия:")
        actions_layout = QVBoxLayout(actions_group)

        get_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
        get_coords_check.setToolTip("Кликнуть в центр найденного изображения")

        continue_check = QCheckBox("Продолжить выполнение (continue)")
        continue_check.setChecked(True)

        stop_bot_check = QCheckBox("Остановить бота (running.clear())")

        actions_layout.addWidget(get_coords_check)
        actions_layout.addWidget(continue_check)
        actions_layout.addWidget(stop_bot_check)

        layout.addWidget(actions_group)

        # Чекбокс для дополнительных действий
        add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        layout.addWidget(add_actions_check)

        # Фрейм для дополнительных действий
        actions_frame = QFrame()
        actions_frame.setVisible(False)  # По умолчанию скрыт
        actions_layout = QVBoxLayout(actions_frame)

        # Таблица для дополнительных действий
        actions_table = QTableWidget(0, 3)
        actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        actions_table.setColumnWidth(0, 120)
        actions_table.setColumnWidth(2, 80)

        # Кнопки для добавления действий
        add_actions_buttons = QHBoxLayout()
        add_click_btn = QPushButton("Добавить клик")
        add_swipe_btn = QPushButton("Добавить свайп")
        add_sleep_btn = QPushButton("Добавить паузу")

        # Функции для добавления действий в таблицу
        def add_click_to_table():
            click_dialog = ClickModuleDialog(dialog)
            if click_dialog.exec():
                data = click_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_swipe_to_table():
            swipe_dialog = SwipeModuleDialog(dialog)
            if swipe_dialog.exec():
                data = swipe_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_sleep_to_table():
            sleep_dialog = QDialog(dialog)
            sleep_dialog.setWindowTitle("Добавить паузу")
            sleep_dialog.setModal(True)

            sleep_layout = QVBoxLayout(sleep_dialog)

            # Спиннер для времени
            hbox = QHBoxLayout()
            label = QLabel("Время паузы (секунды):")
            spinner = QDoubleSpinBox()
            spinner.setRange(0.1, 60.0)
            spinner.setValue(1.0)
            spinner.setDecimals(1)
            spinner.setSingleStep(0.1)
            spinner.setSuffix(" сек")

            hbox.addWidget(label)
            hbox.addWidget(spinner)
            sleep_layout.addLayout(hbox)

            # Кнопки
            buttons = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("OK")

            cancel_btn.clicked.connect(sleep_dialog.reject)
            ok_btn.clicked.connect(sleep_dialog.accept)

            buttons.addWidget(cancel_btn)
            buttons.addWidget(ok_btn)
            sleep_layout.addLayout(buttons)

            if sleep_dialog.exec():
                sleep_time = spinner.value()

                row = actions_table.rowCount()
                actions_table.insertRow(row)

                actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        # Подключаем функции к кнопкам
        add_click_btn.clicked.connect(add_click_to_table)
        add_swipe_btn.clicked.connect(add_swipe_to_table)
        add_sleep_btn.clicked.connect(add_sleep_to_table)

        add_actions_buttons.addWidget(add_click_btn)
        add_actions_buttons.addWidget(add_swipe_btn)
        add_actions_buttons.addWidget(add_sleep_btn)

        actions_layout.addLayout(add_actions_buttons)
        actions_layout.addWidget(actions_table)

        layout.addWidget(actions_frame)

        # Показываем/скрываем фрейм дополнительных действий
        add_actions_check.stateChanged.connect(lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

        # Кнопки диалога
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("Добавить")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        layout.addLayout(buttons_layout)

        # Если диалог принят, добавляем блок на холст
        if dialog.exec():
            # Формируем описание блока
            selected_image = "любое изображение"
            if image_combo.currentIndex() > 0:
                selected_image = image_combo.currentText()

            description = f"Если найдено {selected_image}"

            # Собираем действия
            actions = []
            if get_coords_check.isChecked():
                actions.append("get_coords")
            if continue_check.isChecked():
                actions.append("continue")
            if stop_bot_check.isChecked():
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                description += f" + {actions_table.rowCount()} действий"

            # Собираем данные для блока
            data = {
                "type": "if_result",
                "image": None if image_combo.currentIndex() == 0 else image_combo.currentText(),
                "log_event": log_input.text().strip(),
                "get_coords": get_coords_check.isChecked(),
                "continue": continue_check.isChecked(),
                "stop_bot": stop_bot_check.isChecked(),
                "additional_actions": []
            }

            # Если есть дополнительные действия, добавляем их
            if add_actions_check.isChecked():
                for row in range(actions_table.rowCount()):
                    action_type = actions_table.item(row, 0).text()
                    action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                    if action_type == "Клик":
                        data["additional_actions"].append({
                            "type": "click",
                            "x": action_data["x"],
                            "y": action_data["y"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Свайп":
                        data["additional_actions"].append({
                            "type": "swipe",
                            "x1": action_data["x1"],
                            "y1": action_data["y1"],
                            "x2": action_data["x2"],
                            "y2": action_data["y2"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Пауза":
                        data["additional_actions"].append({
                            "type": "sleep",
                            "time": action_data["time"]
                        })

                    # Добавляем блок на холст
                self.add_script_item("IF Result", description, data)

    def add_if_not_result_block(self):
        """Добавляет блок IF Not Result на холст"""
        # Открываем диалог для настройки блока IF Not Result
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка блока IF Not Result")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # Настройка сообщения в консоль
        hbox_log = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        log_input = QLineEdit()
        log_input.setText("Изображение не найдено!")
        log_input.setPlaceholderText("Например: Изображение не найдено!")
        hbox_log.addWidget(log_label)
        hbox_log.addWidget(log_input)
        layout.addLayout(hbox_log)

        # Чекбоксы для действий
        actions_group = QGroupBox("Выберите действия:")
        actions_layout = QVBoxLayout(actions_group)

        continue_check = QCheckBox("Продолжить выполнение (continue)")
        continue_check.setChecked(True)

        stop_bot_check = QCheckBox("Остановить бота (running.clear())")

        actions_layout.addWidget(continue_check)
        actions_layout.addWidget(stop_bot_check)

        layout.addWidget(actions_group)

        # Чекбокс для дополнительных действий
        add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        layout.addWidget(add_actions_check)

        # Фрейм для дополнительных действий
        actions_frame = QFrame()
        actions_frame.setVisible(False)  # По умолчанию скрыт
        actions_layout = QVBoxLayout(actions_frame)

        # Таблица для дополнительных действий
        actions_table = QTableWidget(0, 3)
        actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        actions_table.setColumnWidth(0, 120)
        actions_table.setColumnWidth(2, 80)

        # Кнопки для добавления действий
        add_actions_buttons = QHBoxLayout()
        add_click_btn = QPushButton("Добавить клик")
        add_swipe_btn = QPushButton("Добавить свайп")
        add_sleep_btn = QPushButton("Добавить паузу")

        # Функции для добавления действий в таблицу
        def add_click_to_table():
            click_dialog = ClickModuleDialog(dialog)
            if click_dialog.exec():
                data = click_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_swipe_to_table():
            swipe_dialog = SwipeModuleDialog(dialog)
            if swipe_dialog.exec():
                data = swipe_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_sleep_to_table():
            sleep_dialog = QDialog(dialog)
            sleep_dialog.setWindowTitle("Добавить паузу")
            sleep_dialog.setModal(True)

            sleep_layout = QVBoxLayout(sleep_dialog)

            # Спиннер для времени
            hbox = QHBoxLayout()
            label = QLabel("Время паузы (секунды):")
            spinner = QDoubleSpinBox()
            spinner.setRange(0.1, 60.0)
            spinner.setValue(1.0)
            spinner.setDecimals(1)
            spinner.setSingleStep(0.1)
            spinner.setSuffix(" сек")

            hbox.addWidget(label)
            hbox.addWidget(spinner)
            sleep_layout.addLayout(hbox)

            # Кнопки
            buttons = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("OK")

            cancel_btn.clicked.connect(sleep_dialog.reject)
            ok_btn.clicked.connect(sleep_dialog.accept)

            buttons.addWidget(cancel_btn)
            buttons.addWidget(ok_btn)
            sleep_layout.addLayout(buttons)

            if sleep_dialog.exec():
                sleep_time = spinner.value()

                row = actions_table.rowCount()
                actions_table.insertRow(row)

                actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                del_btn.clicked.connect(lambda: actions_table.removeRow(row))
                actions_table.setCellWidget(row, 2, del_btn)

        # Подключаем функции к кнопкам
        add_click_btn.clicked.connect(add_click_to_table)
        add_swipe_btn.clicked.connect(add_swipe_to_table)
        add_sleep_btn.clicked.connect(add_sleep_to_table)

        add_actions_buttons.addWidget(add_click_btn)
        add_actions_buttons.addWidget(add_swipe_btn)
        add_actions_buttons.addWidget(add_sleep_btn)

        actions_layout.addLayout(add_actions_buttons)
        actions_layout.addWidget(actions_table)

        layout.addWidget(actions_frame)

        # Показываем/скрываем фрейм дополнительных действий
        add_actions_check.stateChanged.connect(lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

        # Кнопки диалога
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("Добавить")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        layout.addLayout(buttons_layout)

        # Если диалог принят, добавляем блок на холст
        if dialog.exec():
            # Формируем описание блока
            description = "Если изображение не найдено"

            # Собираем действия
            actions = []
            if continue_check.isChecked():
                actions.append("continue")
            if stop_bot_check.isChecked():
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                description += f" + {actions_table.rowCount()} действий"

            # Собираем данные для блока
            data = {
                "type": "if_not_result",
                "log_event": log_input.text().strip(),
                "continue": continue_check.isChecked(),
                "stop_bot": stop_bot_check.isChecked(),
                "additional_actions": []
            }

            # Если есть дополнительные действия, добавляем их
            if add_actions_check.isChecked():
                for row in range(actions_table.rowCount()):
                    action_type = actions_table.item(row, 0).text()
                    action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                    if action_type == "Клик":
                        data["additional_actions"].append({
                            "type": "click",
                            "x": action_data["x"],
                            "y": action_data["y"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Свайп":
                        data["additional_actions"].append({
                            "type": "swipe",
                            "x1": action_data["x1"],
                            "y1": action_data["y1"],
                            "x2": action_data["x2"],
                            "y2": action_data["y2"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Пауза":
                        data["additional_actions"].append({
                            "type": "sleep",
                            "time": action_data["time"]
                        })

            # Добавляем блок на холст
            self.add_script_item("IF Not Result", description, data)

    def edit_if_result_block(self, index: int):
        """Редактирует блок IF Result на холсте"""
        # Находим элемент
        if 0 <= index < len(self.script_items):
            item = self.script_items[index]
            if item.item_type != "IF Result":
                return

            # Создаем диалог редактирования с теми же полями, что и при добавлении
            # Но заполняем данными из существующего блока
            data = item.data

            # Открываем диалог для редактирования блока
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактирование блока IF Result")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # Выбор конкретного изображения для этого блока
            hbox_image = QHBoxLayout()
            image_label = QLabel("Изображение для проверки:")
            image_combo = QComboBox()
            image_combo.addItem("Любое найденное изображение")

            # Добавляем все доступные изображения
            main_image = self.image_name.text().strip()
            if main_image:
                image_combo.addItem(main_image)

            for row in range(self.images_list.rowCount()):
                image_name = self.images_list.item(row, 0).text()
                if image_name not in [main_image]:  # Избегаем дубликатов
                    image_combo.addItem(image_name)

            # Устанавливаем выбранное изображение
            if data.get("image"):
                index = image_combo.findText(data["image"])
                if index >= 0:
                    image_combo.setCurrentIndex(index)

            hbox_image.addWidget(image_label)
            hbox_image.addWidget(image_combo)
            layout.addLayout(hbox_image)

            # Настройка сообщения в консоль
            hbox_log = QHBoxLayout()
            log_label = QLabel("Сообщение в консоль:")
            log_input = QLineEdit()
            log_input.setText(data.get("log_event", "Изображение найдено!"))
            log_input.setPlaceholderText("Например: Победа найдена!")
            hbox_log.addWidget(log_label)
            hbox_log.addWidget(log_input)
            layout.addLayout(hbox_log)

            # Чекбоксы для действий
            actions_group = QGroupBox("Выберите действия:")
            actions_layout = QVBoxLayout(actions_group)

            get_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
            get_coords_check.setToolTip("Кликнуть в центр найденного изображения")
            get_coords_check.setChecked(data.get("get_coords", False))

            continue_check = QCheckBox("Продолжить выполнение (continue)")
            continue_check.setChecked(data.get("continue", True))

            stop_bot_check = QCheckBox("Остановить бота (running.clear())")
            stop_bot_check.setChecked(data.get("stop_bot", False))

            actions_layout.addWidget(get_coords_check)
            actions_layout.addWidget(continue_check)
            actions_layout.addWidget(stop_bot_check)

            layout.addWidget(actions_group)

            # Чекбокс для дополнительных действий
            add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
            add_actions_check.setChecked(len(data.get("additional_actions", [])) > 0)
            layout.addWidget(add_actions_check)

            # Фрейм для дополнительных действий
            actions_frame = QFrame()
            actions_frame.setVisible(add_actions_check.isChecked())  # Показываем в зависимости от наличия действий
            actions_layout = QVBoxLayout(actions_frame)

            # Таблица для дополнительных действий
            actions_table = QTableWidget(0, 3)
            actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
            actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            actions_table.setColumnWidth(0, 120)
            actions_table.setColumnWidth(2, 80)

            # Заполняем таблицу существующими действиями
            for action_data in data.get("additional_actions", []):
                row = actions_table.rowCount()
                actions_table.insertRow(row)

                action_type = action_data.get("type", "")
                if action_type == "click":
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {action_data.get('x', 0)}, Y: {action_data.get('y', 0)}"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "swipe":
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({action_data.get('x1', 0)}, {action_data.get('y1', 0)}) "
                    desc += f"до ({action_data.get('x2', 0)}, {action_data.get('y2', 0)})"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "sleep":
                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {action_data.get('time', 1.0)} секунд"))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row  # Захватываем текущее значение row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

            # Кнопки для добавления действий
            add_actions_buttons = QHBoxLayout()
            add_click_btn = QPushButton("Добавить клик")
            add_swipe_btn = QPushButton("Добавить свайп")
            add_sleep_btn = QPushButton("Добавить паузу")

            # Функции для добавления действий в таблицу
            def add_click_to_table():
                click_dialog = ClickModuleDialog(dialog)
                if click_dialog.exec():
                    data = click_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_swipe_to_table():
                swipe_dialog = SwipeModuleDialog(dialog)
                if swipe_dialog.exec():
                    data = swipe_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_sleep_to_table():
                sleep_dialog = QDialog(dialog)
                sleep_dialog.setWindowTitle("Добавить паузу")
                sleep_dialog.setModal(True)

                sleep_layout = QVBoxLayout(sleep_dialog)

                # Спиннер для времени
                hbox = QHBoxLayout()
                label = QLabel("Время паузы (секунды):")
                spinner = QDoubleSpinBox()
                spinner.setRange(0.1, 60.0)
                spinner.setValue(1.0)
                spinner.setDecimals(1)
                spinner.setSingleStep(0.1)
                spinner.setSuffix(" сек")

                hbox.addWidget(label)
                hbox.addWidget(spinner)
                sleep_layout.addLayout(hbox)

                # Кнопки
                buttons = QHBoxLayout()
                cancel_btn = QPushButton("Отмена")
                ok_btn = QPushButton("OK")

                cancel_btn.clicked.connect(sleep_dialog.reject)
                ok_btn.clicked.connect(sleep_dialog.accept)

                buttons.addWidget(cancel_btn)
                buttons.addWidget(ok_btn)
                sleep_layout.addLayout(buttons)

                if sleep_dialog.exec():
                    sleep_time = spinner.value()

                    row = actions_table.rowCount()
                    actions_table.insertRow(row)

                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            # Подключаем функции к кнопкам
            add_click_btn.clicked.connect(add_click_to_table)
            add_swipe_btn.clicked.connect(add_swipe_to_table)
            add_sleep_btn.clicked.connect(add_sleep_to_table)

            add_actions_buttons.addWidget(add_click_btn)
            add_actions_buttons.addWidget(add_swipe_btn)
            add_actions_buttons.addWidget(add_sleep_btn)

            actions_layout.addLayout(add_actions_buttons)
            actions_layout.addWidget(actions_table)

            layout.addWidget(actions_frame)

            # Показываем/скрываем фрейм дополнительных действий
            add_actions_check.stateChanged.connect(
                lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

            # Кнопки диалога
            buttons_layout = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("Сохранить")

            cancel_btn.clicked.connect(dialog.reject)
            ok_btn.clicked.connect(dialog.accept)

            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            layout.addLayout(buttons_layout)

            # Если диалог принят, обновляем блок
            if dialog.exec():
                # Формируем описание блока
                selected_image = "любое изображение"
                if image_combo.currentIndex() > 0:
                    selected_image = image_combo.currentText()

                description = f"Если найдено {selected_image}"

                # Собираем действия
                actions = []
                if get_coords_check.isChecked():
                    actions.append("get_coords")
                if continue_check.isChecked():
                    actions.append("continue")
                if stop_bot_check.isChecked():
                    actions.append("running.clear()")

                if actions:
                    description += f" → {', '.join(actions)}"

                # Добавляем информацию о дополнительных действиях
                if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                    description += f" + {actions_table.rowCount()} действий"

                # Обновляем данные блока
                new_data = {
                    "type": "if_result",
                    "image": None if image_combo.currentIndex() == 0 else image_combo.currentText(),
                    "log_event": log_input.text().strip(),
                    "get_coords": get_coords_check.isChecked(),
                    "continue": continue_check.isChecked(),
                    "stop_bot": stop_bot_check.isChecked(),
                    "additional_actions": []
                }

                # Если есть дополнительные действия, добавляем их
                if add_actions_check.isChecked():
                    for row in range(actions_table.rowCount()):
                        action_type = actions_table.item(row, 0).text()
                        action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                        if action_type == "Клик":
                            new_data["additional_actions"].append({
                                "type": "click",
                                "x": action_data["x"],
                                "y": action_data["y"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Свайп":
                            new_data["additional_actions"].append({
                                "type": "swipe",
                                "x1": action_data["x1"],
                                "y1": action_data["y1"],
                                "x2": action_data["x2"],
                                "y2": action_data["y2"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Пауза":
                            new_data["additional_actions"].append({
                                "type": "sleep",
                                "time": action_data["time"]
                            })

                # Обновляем данные и текст элемента
                item.description = description
                item.data = new_data

                # Обновляем виджет на холсте
                old_widget = item
                item_index = item.index

                # Удаляем старый виджет
                self.script_canvas_layout.removeWidget(old_widget)
                old_widget.deleteLater()

                # Создаем новый виджет
                new_widget = ScriptItemWidget(item_index, "IF Result", description)
                new_widget.set_data(new_data)
                new_widget.deleteRequested.connect(self.delete_script_item)
                new_widget.editRequested.connect(self.edit_script_item)

                # Обновляем запись в списке
                self.script_items[item_index] = new_widget

                # Добавляем на холст
                self.script_canvas_layout.insertWidget(item_index, new_widget)

    def edit_if_not_result_block(self, index: int):
        """Редактирует блок IF Not Result на холсте"""
        # Находим элемент
        if 0 <= index < len(self.script_items):
            item = self.script_items[index]
            if item.item_type != "IF Not Result":
                return

            # Получаем данные блока
            data = item.data

            # Открываем диалог для редактирования блока
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактирование блока IF Not Result")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # Настройка сообщения в консоль
            hbox_log = QHBoxLayout()
            log_label = QLabel("Сообщение в консоль:")
            log_input = QLineEdit()
            log_input.setText(data.get("log_event", "Изображение не найдено!"))
            log_input.setPlaceholderText("Например: Изображение не найдено!")
            hbox_log.addWidget(log_label)
            hbox_log.addWidget(log_input)
            layout.addLayout(hbox_log)

            # Чекбоксы для действий
            actions_group = QGroupBox("Выберите действия:")
            actions_layout = QVBoxLayout(actions_group)

            continue_check = QCheckBox("Продолжить выполнение (continue)")
            continue_check.setChecked(data.get("continue", True))

            stop_bot_check = QCheckBox("Остановить бота (running.clear())")
            stop_bot_check.setChecked(data.get("stop_bot", False))

            actions_layout.addWidget(continue_check)
            actions_layout.addWidget(stop_bot_check)

            layout.addWidget(actions_group)

            # Чекбокс для дополнительных действий
            add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
            add_actions_check.setChecked(len(data.get("additional_actions", [])) > 0)
            layout.addWidget(add_actions_check)

            # Фрейм для дополнительных действий
            actions_frame = QFrame()
            actions_frame.setVisible(add_actions_check.isChecked())  # Показываем в зависимости от наличия действий
            actions_layout = QVBoxLayout(actions_frame)

            # Таблица для дополнительных действий
            actions_table = QTableWidget(0, 3)
            actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
            actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            actions_table.setColumnWidth(0, 120)
            actions_table.setColumnWidth(2, 80)

            # Заполняем таблицу существующими действиями
            for action_data in data.get("additional_actions", []):
                row = actions_table.rowCount()
                actions_table.insertRow(row)

                action_type = action_data.get("type", "")
                if action_type == "click":
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {action_data.get('x', 0)}, Y: {action_data.get('y', 0)}"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "swipe":
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({action_data.get('x1', 0)}, {action_data.get('y1', 0)}) "
                    desc += f"до ({action_data.get('x2', 0)}, {action_data.get('y2', 0)})"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "sleep":
                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {action_data.get('time', 1.0)} секунд"))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row  # Захватываем текущее значение row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

            # Кнопки для добавления действий
            add_actions_buttons = QHBoxLayout()
            add_click_btn = QPushButton("Добавить клик")
            add_swipe_btn = QPushButton("Добавить свайп")
            add_sleep_btn = QPushButton("Добавить паузу")

            # Функции для добавления действий в таблицу
            def add_click_to_table():
                click_dialog = ClickModuleDialog(dialog)
                if click_dialog.exec():
                    data = click_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_swipe_to_table():
                swipe_dialog = SwipeModuleDialog(dialog)
                if swipe_dialog.exec():
                    data = swipe_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_sleep_to_table():
                sleep_dialog = QDialog(dialog)
                sleep_dialog.setWindowTitle("Добавить паузу")
                sleep_dialog.setModal(True)

                sleep_layout = QVBoxLayout(sleep_dialog)

                # Спиннер для времени
                hbox = QHBoxLayout()
                label = QLabel("Время паузы (секунды):")
                spinner = QDoubleSpinBox()
                spinner.setRange(0.1, 60.0)
                spinner.setValue(1.0)
                spinner.setDecimals(1)
                spinner.setSingleStep(0.1)
                spinner.setSuffix(" сек")

                hbox.addWidget(label)
                hbox.addWidget(spinner)
                sleep_layout.addLayout(hbox)

                # Кнопки
                buttons = QHBoxLayout()
                cancel_btn = QPushButton("Отмена")
                ok_btn = QPushButton("OK")

                cancel_btn.clicked.connect(sleep_dialog.reject)
                ok_btn.clicked.connect(sleep_dialog.accept)

                buttons.addWidget(cancel_btn)
                buttons.addWidget(ok_btn)
                sleep_layout.addLayout(buttons)

                if sleep_dialog.exec():
                    sleep_time = spinner.value()

                    row = actions_table.rowCount()
                    actions_table.insertRow(row)

                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                    # Сохраняем данные с помощью setData
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row  # Захватываем текущее значение row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            # Подключаем функции к кнопкам
            add_click_btn.clicked.connect(add_click_to_table)
            add_swipe_btn.clicked.connect(add_swipe_to_table)
            add_sleep_btn.clicked.connect(add_sleep_to_table)

            add_actions_buttons.addWidget(add_click_btn)
            add_actions_buttons.addWidget(add_swipe_btn)
            add_actions_buttons.addWidget(add_sleep_btn)

            actions_layout.addLayout(add_actions_buttons)
            actions_layout.addWidget(actions_table)

            layout.addWidget(actions_frame)

            # Показываем/скрываем фрейм дополнительных действий
            add_actions_check.stateChanged.connect(
                lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

            # Кнопки диалога
            buttons_layout = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("Сохранить")

            cancel_btn.clicked.connect(dialog.reject)
            ok_btn.clicked.connect(dialog.accept)

            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            layout.addLayout(buttons_layout)

            # Если диалог принят, обновляем блок
            if dialog.exec():
                # Формируем описание блока
                description = "Если изображение не найдено"

                # Собираем действия
                actions = []
                if continue_check.isChecked():
                    actions.append("continue")
                if stop_bot_check.isChecked():
                    actions.append("running.clear()")

                if actions:
                    description += f" → {', '.join(actions)}"

                # Добавляем информацию о дополнительных действиях
                if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                    description += f" + {actions_table.rowCount()} действий"

                # Обновляем данные блока
                new_data = {
                    "type": "if_not_result",
                    "log_event": log_input.text().strip(),
                    "continue": continue_check.isChecked(),
                    "stop_bot": stop_bot_check.isChecked(),
                    "additional_actions": []
                }

                # Если есть дополнительные действия, добавляем их
                if add_actions_check.isChecked():
                    for row in range(actions_table.rowCount()):
                        action_type = actions_table.item(row, 0).text()
                        action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                        if action_type == "Клик":
                            new_data["additional_actions"].append({
                                "type": "click",
                                "x": action_data["x"],
                                "y": action_data["y"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Свайп":
                            new_data["additional_actions"].append({
                                "type": "swipe",
                                "x1": action_data["x1"],
                                "y1": action_data["y1"],
                                "x2": action_data["x2"],
                                "y2": action_data["y2"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Пауза":
                            new_data["additional_actions"].append({
                                "type": "sleep",
                                "time": action_data["time"]
                            })

                # Обновляем данные и текст элемента
                item.description = description
                item.data = new_data

                # Обновляем виджет на холсте
                old_widget = item
                item_index = item.index

                # Удаляем старый виджет
                self.script_canvas_layout.removeWidget(old_widget)
                old_widget.deleteLater()

                # Создаем новый виджет
                new_widget = ScriptItemWidget(item_index, "IF Not Result", description)
                new_widget.set_data(new_data)
                new_widget.deleteRequested.connect(self.delete_script_item)
                new_widget.editRequested.connect(self.edit_script_item)

                # Обновляем запись в списке
                self.script_items[item_index] = new_widget

                # Добавляем на холст
                self.script_canvas_layout.insertWidget(item_index, new_widget)

    def add_elif_block(self):
        """Добавляет блок ELIF на холст"""
        # Открываем диалог для настройки блока ELIF
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка блока ELIF")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # Выбор конкретного изображения для ELIF
        hbox_image = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        image_combo = QComboBox()

        # Добавляем все доступные изображения
        main_image = self.image_name.text().strip()
        if main_image:
            image_combo.addItem(main_image)

        for row in range(self.images_list.rowCount()):
            image_name = self.images_list.item(row, 0).text()
            image_combo.addItem(image_name)

        hbox_image.addWidget(image_label)
        hbox_image.addWidget(image_combo)
        layout.addLayout(hbox_image)

        # Настройка сообщения в консоль
        hbox_log = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        log_input = QLineEdit()
        log_input.setText("Найдено другое изображение!")
        log_input.setPlaceholderText("Например: Найдено изображение поражения!")
        hbox_log.addWidget(log_label)
        hbox_log.addWidget(log_input)
        layout.addLayout(hbox_log)

        # Чекбоксы для действий
        actions_group = QGroupBox("Выберите действия:")
        actions_layout = QVBoxLayout(actions_group)

        get_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
        get_coords_check.setToolTip("Кликнуть в центр найденного изображения")

        continue_check = QCheckBox("Продолжить выполнение (continue)")
        continue_check.setChecked(True)

        stop_bot_check = QCheckBox("Остановить бота (running.clear())")

        actions_layout.addWidget(get_coords_check)
        actions_layout.addWidget(continue_check)
        actions_layout.addWidget(stop_bot_check)

        layout.addWidget(actions_group)

        # Чекбокс для дополнительных действий
        add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        layout.addWidget(add_actions_check)

        # Фрейм для дополнительных действий
        actions_frame = QFrame()
        actions_frame.setVisible(False)  # По умолчанию скрыт
        actions_layout = QVBoxLayout(actions_frame)

        # Таблица для дополнительных действий
        actions_table = QTableWidget(0, 3)
        actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        actions_table.setColumnWidth(0, 120)
        actions_table.setColumnWidth(2, 80)

        # Кнопки для добавления действий
        add_actions_buttons = QHBoxLayout()
        add_click_btn = QPushButton("Добавить клик")
        add_swipe_btn = QPushButton("Добавить свайп")
        add_sleep_btn = QPushButton("Добавить паузу")

        # Функции для добавления действий в таблицу (аналогично IF Result)
        def add_click_to_table():
            click_dialog = ClickModuleDialog(dialog)
            if click_dialog.exec():
                data = click_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_swipe_to_table():
            swipe_dialog = SwipeModuleDialog(dialog)
            if swipe_dialog.exec():
                data = swipe_dialog.get_data()
                row = actions_table.rowCount()
                actions_table.insertRow(row)
                actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                if data['description']:
                    desc += f", {data['description']}"
                actions_table.setItem(row, 1, QTableWidgetItem(desc))
                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, data)
                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

        def add_sleep_to_table():
            sleep_dialog = QDialog(dialog)
            sleep_dialog.setWindowTitle("Добавить паузу")
            sleep_dialog.setModal(True)

            sleep_layout = QVBoxLayout(sleep_dialog)

            # Спиннер для времени
            hbox = QHBoxLayout()
            label = QLabel("Время паузы (секунды):")
            spinner = QDoubleSpinBox()
            spinner.setRange(0.1, 60.0)
            spinner.setValue(1.0)
            spinner.setDecimals(1)
            spinner.setSingleStep(0.1)
            spinner.setSuffix(" сек")

            hbox.addWidget(label)
            hbox.addWidget(spinner)
            sleep_layout.addLayout(hbox)

            # Кнопки
            buttons = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("OK")

            cancel_btn.clicked.connect(sleep_dialog.reject)
            ok_btn.clicked.connect(sleep_dialog.accept)

            buttons.addWidget(cancel_btn)
            buttons.addWidget(ok_btn)
            sleep_layout.addLayout(buttons)

            if sleep_dialog.exec():
                sleep_time = spinner.value()

                row = actions_table.rowCount()
                actions_table.insertRow(row)

                actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                # Сохраняем данные с помощью setData
                item = actions_table.item(row, 0)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

        # Подключаем функции к кнопкам
        add_click_btn.clicked.connect(add_click_to_table)
        add_swipe_btn.clicked.connect(add_swipe_to_table)
        add_sleep_btn.clicked.connect(add_sleep_to_table)

        add_actions_buttons.addWidget(add_click_btn)
        add_actions_buttons.addWidget(add_swipe_btn)
        add_actions_buttons.addWidget(add_sleep_btn)

        actions_layout.addLayout(add_actions_buttons)
        actions_layout.addWidget(actions_table)

        layout.addWidget(actions_frame)

        # Показываем/скрываем фрейм дополнительных действий
        add_actions_check.stateChanged.connect(lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

        # Кнопки диалога
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("Добавить")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        layout.addLayout(buttons_layout)

        # Если диалог принят, добавляем блок на холст
        if dialog.exec():
            # Проверяем, что выбрано изображение
            selected_image = image_combo.currentText()
            if not selected_image:
                QMessageBox.warning(self, "Внимание", "Необходимо выбрать изображение для блока ELIF.")
                return

            # Формируем описание блока
            description = f"ELIF: Если найдено {selected_image}"

            # Собираем действия
            actions = []
            if get_coords_check.isChecked():
                actions.append("get_coords")
            if continue_check.isChecked():
                actions.append("continue")
            if stop_bot_check.isChecked():
                actions.append("running.clear()")

            if actions:
                description += f" → {', '.join(actions)}"

            # Добавляем информацию о дополнительных действиях
            if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                description += f" + {actions_table.rowCount()} действий"

            # Собираем данные для блока
            data = {
                "type": "elif",
                "image": selected_image,
                "log_event": log_input.text().strip(),
                "get_coords": get_coords_check.isChecked(),
                "continue": continue_check.isChecked(),
                "stop_bot": stop_bot_check.isChecked(),
                "additional_actions": []
            }

            # Если есть дополнительные действия, добавляем их
            if add_actions_check.isChecked():
                for row in range(actions_table.rowCount()):
                    action_type = actions_table.item(row, 0).text()
                    action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                    if action_type == "Клик":
                        data["additional_actions"].append({
                            "type": "click",
                            "x": action_data["x"],
                            "y": action_data["y"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Свайп":
                        data["additional_actions"].append({
                            "type": "swipe",
                            "x1": action_data["x1"],
                            "y1": action_data["y1"],
                            "x2": action_data["x2"],
                            "y2": action_data["y2"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Пауза":
                        data["additional_actions"].append({
                            "type": "sleep",
                            "time": action_data["time"]
                        })

            # Добавляем блок на холст
            self.add_script_item("ELIF", description, data)

    def edit_elif_block(self, index: int):
        """Редактирует блок ELIF на холсте"""
        # Находим элемент
        if 0 <= index < len(self.script_items):
            item = self.script_items[index]
            if item.item_type != "ELIF":
                return

            # Получаем данные блока
            data = item.data

            # Открываем диалог для редактирования блока
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактирование блока ELIF")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # Выбор конкретного изображения для этого блока
            hbox_image = QHBoxLayout()
            image_label = QLabel("Изображение для проверки:")
            image_combo = QComboBox()

            # Добавляем все доступные изображения
            main_image = self.image_name.text().strip()
            if main_image:
                image_combo.addItem(main_image)

            for row in range(self.images_list.rowCount()):
                image_name = self.images_list.item(row, 0).text()
                image_combo.addItem(image_name)

            # Устанавливаем выбранное изображение
            if data.get("image"):
                index = image_combo.findText(data["image"])
                if index >= 0:
                    image_combo.setCurrentIndex(index)

            hbox_image.addWidget(image_label)
            hbox_image.addWidget(image_combo)
            layout.addLayout(hbox_image)

            # Настройка сообщения в консоль
            hbox_log = QHBoxLayout()
            log_label = QLabel("Сообщение в консоль:")
            log_input = QLineEdit()
            log_input.setText(data.get("log_event", "Найдено другое изображение!"))
            log_input.setPlaceholderText("Например: Найдено изображение поражения!")
            hbox_log.addWidget(log_label)
            hbox_log.addWidget(log_input)
            layout.addLayout(hbox_log)

            # Чекбоксы для действий
            actions_group = QGroupBox("Выберите действия:")
            actions_layout = QVBoxLayout(actions_group)

            get_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
            get_coords_check.setToolTip("Кликнуть в центр найденного изображения")
            get_coords_check.setChecked(data.get("get_coords", False))

            continue_check = QCheckBox("Продолжить выполнение (continue)")
            continue_check.setChecked(data.get("continue", True))

            stop_bot_check = QCheckBox("Остановить бота (running.clear())")
            stop_bot_check.setChecked(data.get("stop_bot", False))

            actions_layout.addWidget(get_coords_check)
            actions_layout.addWidget(continue_check)
            actions_layout.addWidget(stop_bot_check)

            layout.addWidget(actions_group)

            # Чекбокс для дополнительных действий
            add_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
            add_actions_check.setChecked(len(data.get("additional_actions", [])) > 0)
            layout.addWidget(add_actions_check)

            # Фрейм для дополнительных действий
            actions_frame = QFrame()
            actions_frame.setVisible(add_actions_check.isChecked())  # Показываем в зависимости от наличия действий
            actions_layout = QVBoxLayout(actions_frame)

            # Таблица для дополнительных действий
            actions_table = QTableWidget(0, 3)
            actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
            actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            actions_table.setColumnWidth(0, 120)
            actions_table.setColumnWidth(2, 80)

            # Заполняем таблицу существующими действиями (код аналогичен edit_if_result_block)
            for action_data in data.get("additional_actions", []):
                row = actions_table.rowCount()
                actions_table.insertRow(row)

                action_type = action_data.get("type", "")
                if action_type == "click":
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {action_data.get('x', 0)}, Y: {action_data.get('y', 0)}"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "swipe":
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({action_data.get('x1', 0)}, {action_data.get('y1', 0)}) "
                    desc += f"до ({action_data.get('x2', 0)}, {action_data.get('y2', 0)})"
                    if action_data.get("sleep"):
                        desc += f", Задержка: {action_data.get('sleep')}с"
                    if action_data.get("description"):
                        desc += f", {action_data.get('description', '')}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)
                elif action_type == "sleep":
                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {action_data.get('time', 1.0)} секунд"))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, action_data)

                # Кнопка удаления
                del_btn = QPushButton("Удалить")
                row_for_deletion = row  # Захватываем текущее значение row
                del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                actions_table.setCellWidget(row, 2, del_btn)

            # Кнопки для добавления действий (код аналогичен edit_if_result_block)
            add_actions_buttons = QHBoxLayout()
            add_click_btn = QPushButton("Добавить клик")
            add_swipe_btn = QPushButton("Добавить свайп")
            add_sleep_btn = QPushButton("Добавить паузу")

            # Функции для добавления действий в таблицу
            def add_click_to_table():
                click_dialog = ClickModuleDialog(dialog)
                if click_dialog.exec():
                    data = click_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Клик"))
                    desc = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_swipe_to_table():
                swipe_dialog = SwipeModuleDialog(dialog)
                if swipe_dialog.exec():
                    data = swipe_dialog.get_data()
                    row = actions_table.rowCount()
                    actions_table.insertRow(row)
                    actions_table.setItem(row, 0, QTableWidgetItem("Свайп"))
                    desc = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
                    if data['description']:
                        desc += f", {data['description']}"
                    actions_table.setItem(row, 1, QTableWidgetItem(desc))
                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            def add_sleep_to_table():
                sleep_dialog = QDialog(dialog)
                sleep_dialog.setWindowTitle("Добавить паузу")
                sleep_dialog.setModal(True)

                sleep_layout = QVBoxLayout(sleep_dialog)

                # Спиннер для времени
                hbox = QHBoxLayout()
                label = QLabel("Время паузы (секунды):")
                spinner = QDoubleSpinBox()
                spinner.setRange(0.1, 60.0)
                spinner.setValue(1.0)
                spinner.setDecimals(1)
                spinner.setSingleStep(0.1)
                spinner.setSuffix(" сек")

                hbox.addWidget(label)
                hbox.addWidget(spinner)
                sleep_layout.addLayout(hbox)

                # Кнопки
                buttons = QHBoxLayout()
                cancel_btn = QPushButton("Отмена")
                ok_btn = QPushButton("OK")

                cancel_btn.clicked.connect(sleep_dialog.reject)
                ok_btn.clicked.connect(sleep_dialog.accept)

                buttons.addWidget(cancel_btn)
                buttons.addWidget(ok_btn)
                sleep_layout.addLayout(buttons)

                if sleep_dialog.exec():
                    sleep_time = spinner.value()

                    row = actions_table.rowCount()
                    actions_table.insertRow(row)

                    actions_table.setItem(row, 0, QTableWidgetItem("Пауза"))
                    actions_table.setItem(row, 1, QTableWidgetItem(f"Пауза {sleep_time} секунд"))

                    # Сохраняем данные
                    item = actions_table.item(row, 0)
                    item.setData(Qt.ItemDataRole.UserRole, {"type": "sleep", "time": sleep_time})

                    # Кнопка удаления
                    del_btn = QPushButton("Удалить")
                    row_for_deletion = row
                    del_btn.clicked.connect(lambda checked=False, r=row_for_deletion: actions_table.removeRow(r))
                    actions_table.setCellWidget(row, 2, del_btn)

            # Подключаем функции к кнопкам
            add_click_btn.clicked.connect(add_click_to_table)
            add_swipe_btn.clicked.connect(add_swipe_to_table)
            add_sleep_btn.clicked.connect(add_sleep_to_table)

            add_actions_buttons.addWidget(add_click_btn)
            add_actions_buttons.addWidget(add_swipe_btn)
            add_actions_buttons.addWidget(add_sleep_btn)

            actions_layout.addLayout(add_actions_buttons)
            actions_layout.addWidget(actions_table)

            layout.addWidget(actions_frame)

            # Показываем/скрываем фрейм дополнительных действий
            add_actions_check.stateChanged.connect(
                lambda state: actions_frame.setVisible(state == Qt.CheckState.Checked))

            # Кнопки диалога
            buttons_layout = QHBoxLayout()
            cancel_btn = QPushButton("Отмена")
            ok_btn = QPushButton("Сохранить")

            cancel_btn.clicked.connect(dialog.reject)
            ok_btn.clicked.connect(dialog.accept)

            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(ok_btn)
            layout.addLayout(buttons_layout)

            # Если диалог принят, обновляем блок
            if dialog.exec():
                # Формируем описание блока
                selected_image = image_combo.currentText()
                description = f"ELIF: Если найдено {selected_image}"

                # Собираем действия
                actions = []
                if get_coords_check.isChecked():
                    actions.append("get_coords")
                if continue_check.isChecked():
                    actions.append("continue")
                if stop_bot_check.isChecked():
                    actions.append("running.clear()")

                if actions:
                    description += f" → {', '.join(actions)}"

                # Добавляем информацию о дополнительных действиях
                if add_actions_check.isChecked() and actions_table.rowCount() > 0:
                    description += f" + {actions_table.rowCount()} действий"

                # Обновляем данные блока
                new_data = {
                    "type": "elif",
                    "image": image_combo.currentText(),
                    "log_event": log_input.text().strip(),
                    "get_coords": get_coords_check.isChecked(),
                    "continue": continue_check.isChecked(),
                    "stop_bot": stop_bot_check.isChecked(),
                    "additional_actions": []
                }

                # Если есть дополнительные действия, добавляем их
                if add_actions_check.isChecked():
                    for row in range(actions_table.rowCount()):
                        action_type = actions_table.item(row, 0).text()
                        action_data = actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                        if action_type == "Клик":
                            new_data["additional_actions"].append({
                                "type": "click",
                                "x": action_data["x"],
                                "y": action_data["y"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Свайп":
                            new_data["additional_actions"].append({
                                "type": "swipe",
                                "x1": action_data["x1"],
                                "y1": action_data["y1"],
                                "x2": action_data["x2"],
                                "y2": action_data["y2"],
                                "description": action_data["description"],
                                "sleep": action_data["sleep"]
                            })
                        elif action_type == "Пауза":
                            new_data["additional_actions"].append({
                                "type": "sleep",
                                "time": action_data["time"]
                            })

                # Обновляем данные и текст элемента
                item.description = description
                item.data = new_data

                # Обновляем виджет на холсте
                old_widget = item
                item_index = item.index

                # Удаляем старый виджет
                self.script_canvas_layout.removeWidget(old_widget)
                old_widget.deleteLater()

                # Создаем новый виджет
                new_widget = ScriptItemWidget(item_index, "ELIF", description)
                new_widget.set_data(new_data)
                new_widget.deleteRequested.connect(self.delete_script_item)
                new_widget.editRequested.connect(self.edit_script_item)

                # Обновляем запись в списке
                self.script_items[item_index] = new_widget

                # Добавляем на холст
                self.script_canvas_layout.insertWidget(item_index, new_widget)

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные модуля поиска изображений"""
        # Собираем основные данные
        result = {
            "type": "image_search",
            "image": self.image_name.text().strip(),
            "timeout": self.timeout_input.value(),
            "script_items": []
        }

        # Добавляем дополнительные изображения, если они есть
        additional_images = []
        for row in range(self.images_list.rowCount()):
            image_name = self.images_list.item(row, 0).text()
            additional_images.append(image_name)

        if additional_images:
            result["additional_images"] = additional_images

        # Собираем данные из элементов скрипта
        for item in self.script_items:
            result["script_items"].append({
                "type": item.item_type,
                "data": item.data
            })

        return result