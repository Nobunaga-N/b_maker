# src/gui/image_search_module.py
"""
Модуль содержит класс диалога для настройки модуля поиска изображений.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import os
from typing import Dict, List, Any, Optional

from src.gui.dialog_modules import ClickModuleDialog, SwipeModuleDialog

from src.utils.style_constants import FULL_DIALOG_STYLE


class ImageSearchModuleDialog(QDialog):
    """
    Диалог для настройки модуля поиска изображений.
    Позволяет пользователю настроить поиск одного или нескольких изображений
    и задать логику обработки результатов поиска.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля поиска изображений")
        self.setModal(True)
        self.resize(700, 550)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Используем полный стиль для диалога с таблицами и табами
        self.setStyleSheet(FULL_DIALOG_STYLE)

        # Выбор изображения
        image_group = QGroupBox("Выбор изображения")
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
        timeout_label = QLabel("Таймаут (ожидание появления изображения):")
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 3600)
        self.timeout_input.setValue(120)  # По умолчанию 120 секунд (2 минуты)
        self.timeout_input.setSuffix(" сек")
        hbox2.addWidget(timeout_label)
        hbox2.addWidget(self.timeout_input)
        hbox2.addStretch(1)
        image_layout.addLayout(hbox2)

        # Настройка time.sleep после нахождения картинки
        hbox3 = QHBoxLayout()
        sleep_label = QLabel("Задержка после нахождения (time.sleep):")
        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0, 60)
        self.sleep_input.setValue(0.0)  # По умолчанию без задержки
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        hbox3.addWidget(sleep_label)
        hbox3.addWidget(self.sleep_input)
        hbox3.addStretch(1)
        image_layout.addLayout(hbox3)

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

        layout.addWidget(image_group)

        # Вкладки для "if result" и "if not result" и "elif" подходов
        tabs = QTabWidget()

        # Вкладка "if result"
        if_result_tab = QWidget()
        if_result_layout = QVBoxLayout(if_result_tab)

        found_label = QLabel("Действия, если изображение найдено:")
        found_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        if_result_layout.addWidget(found_label)

        # Выбор конкретного изображения, для которого задаются действия
        hbox_image_selector = QHBoxLayout()
        image_selector_label = QLabel("Выберите изображение:")
        self.image_selector_combo = QComboBox()
        self.image_selector_combo.addItem("Любое найденное изображение")
        hbox_image_selector.addWidget(image_selector_label)
        hbox_image_selector.addWidget(self.image_selector_combo, 1)
        if_result_layout.addLayout(hbox_image_selector)

        # Сообщение в консоль
        log_label = QLabel("Сообщение в консоль:")
        self.log_event_if_found = QLineEdit()
        self.log_event_if_found.setPlaceholderText("Сообщение для вывода в консоль (например, 'Победа найдена!')")
        self.log_event_if_found.setText("Изображение найдено!")
        if_result_layout.addWidget(log_label)
        if_result_layout.addWidget(self.log_event_if_found)

        # Группа действий
        actions_group = QGroupBox("Выберите действия:")
        actions_layout = QVBoxLayout(actions_group)

        self.click_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
        self.click_coords_check.setToolTip("Кликнуть в центр найденного изображения")

        self.additional_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        self.additional_actions_check.setToolTip("Добавить дополнительные действия после нахождения изображения")
        self.additional_actions_check.stateChanged.connect(self.toggle_additional_actions)

        # Контейнер для дополнительных действий
        self.additional_actions_container = QFrame()
        additional_actions_layout = QVBoxLayout(self.additional_actions_container)
        additional_actions_layout.setContentsMargins(20, 5, 5, 5)

        # Таблица для дополнительных действий
        self.additional_actions_table = QTableWidget(0, 3)
        self.additional_actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        self.additional_actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.additional_actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.additional_actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.additional_actions_table.setColumnWidth(0, 120)
        self.additional_actions_table.setColumnWidth(2, 100)

        # Кнопки для добавления действий
        add_actions_layout = QHBoxLayout()
        self.add_click_btn = QPushButton("Добавить клик")
        self.add_swipe_btn = QPushButton("Добавить свайп")
        self.add_sleep_btn = QPushButton("Добавить паузу")

        # Подключаем сигналы кнопок
        self.add_click_btn.clicked.connect(self.add_click_action)
        self.add_swipe_btn.clicked.connect(self.add_swipe_action)
        self.add_sleep_btn.clicked.connect(self.add_sleep_action)

        add_actions_layout.addWidget(self.add_click_btn)
        add_actions_layout.addWidget(self.add_swipe_btn)
        add_actions_layout.addWidget(self.add_sleep_btn)

        additional_actions_layout.addLayout(add_actions_layout)
        additional_actions_layout.addWidget(self.additional_actions_table)

        self.additional_actions_container.setVisible(False)  # По умолчанию скрыт

        self.continue_check = QCheckBox("Продолжить выполнение (continue)")
        self.continue_check.setToolTip("Продолжить выполнение модулей на основном холсте")
        self.continue_check.setChecked(True)  # По умолчанию включено

        self.stop_bot_check = QCheckBox("Остановить бота (running.clear())")
        self.stop_bot_check.setToolTip("Экстренно остановить выполнение бота")

        actions_layout.addWidget(self.click_coords_check)
        actions_layout.addWidget(self.additional_actions_check)
        actions_layout.addWidget(self.additional_actions_container)
        actions_layout.addWidget(self.continue_check)
        actions_layout.addWidget(self.stop_bot_check)

        if_result_layout.addWidget(actions_group)

        # Добавляем кнопку для добавления блока else-if
        self.add_elif_btn = QPushButton("Добавить блок ELIF для другого изображения")
        self.add_elif_btn.clicked.connect(self.add_elif_block)
        if_result_layout.addWidget(self.add_elif_btn)

        tabs.addTab(if_result_tab, "Если изображение найдено")

        # Вкладка "if not result"
        if_not_result_tab = QWidget()
        if_not_layout = QVBoxLayout(if_not_result_tab)

        not_found_label = QLabel("Действия, если изображение не найдено:")
        not_found_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        if_not_layout.addWidget(not_found_label)

        # Сообщение в консоль
        nf_log_label = QLabel("Сообщение в консоль:")
        self.log_event_if_not_found = QLineEdit()
        self.log_event_if_not_found.setPlaceholderText(
            "Сообщение для вывода в консоль (например, 'Изображение не найдено!')")
        self.log_event_if_not_found.setText("Изображение не найдено!")
        if_not_layout.addWidget(nf_log_label)
        if_not_layout.addWidget(self.log_event_if_not_found)

        # Группа действий для случая "картинка не найдена"
        not_found_group = QGroupBox("Выберите действия:")
        not_found_layout = QVBoxLayout(not_found_group)

        self.not_found_additional_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        self.not_found_additional_actions_check.setToolTip(
            "Добавить дополнительные действия, если изображение не найдено")
        self.not_found_additional_actions_check.stateChanged.connect(self.toggle_not_found_additional_actions)

        # Контейнер для дополнительных действий при ненахождении
        self.not_found_actions_container = QFrame()
        not_found_actions_layout = QVBoxLayout(self.not_found_actions_container)
        not_found_actions_layout.setContentsMargins(20, 5, 5, 5)

        # Таблица для дополнительных действий
        self.not_found_actions_table = QTableWidget(0, 3)
        self.not_found_actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        self.not_found_actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.not_found_actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.not_found_actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.not_found_actions_table.setColumnWidth(0, 120)
        self.not_found_actions_table.setColumnWidth(2, 100)

        # Кнопки для добавления действий
        not_found_add_actions_layout = QHBoxLayout()
        self.not_found_add_click_btn = QPushButton("Добавить клик")
        self.not_found_add_swipe_btn = QPushButton("Добавить свайп")
        self.not_found_add_sleep_btn = QPushButton("Добавить паузу")

        # Подключаем сигналы кнопок
        self.not_found_add_click_btn.clicked.connect(lambda: self.add_click_action(for_not_found=True))
        self.not_found_add_swipe_btn.clicked.connect(lambda: self.add_swipe_action(for_not_found=True))
        self.not_found_add_sleep_btn.clicked.connect(lambda: self.add_sleep_action(for_not_found=True))

        not_found_add_actions_layout.addWidget(self.not_found_add_click_btn)
        not_found_add_actions_layout.addWidget(self.not_found_add_swipe_btn)
        not_found_add_actions_layout.addWidget(self.not_found_add_sleep_btn)

        not_found_actions_layout.addLayout(not_found_add_actions_layout)
        not_found_actions_layout.addWidget(self.not_found_actions_table)

        self.not_found_actions_container.setVisible(False)  # По умолчанию скрыт

        self.continue_not_found_check = QCheckBox("Продолжить выполнение (continue)")
        self.continue_not_found_check.setToolTip("Продолжить выполнение модулей на основном холсте")
        self.continue_not_found_check.setChecked(True)  # По умолчанию включено

        self.stop_not_found_check = QCheckBox("Остановить бота (running.clear())")
        self.stop_not_found_check.setToolTip("Экстренно остановить выполнение бота")

        not_found_layout.addWidget(self.not_found_additional_actions_check)
        not_found_layout.addWidget(self.not_found_actions_container)
        not_found_layout.addWidget(self.continue_not_found_check)
        not_found_layout.addWidget(self.stop_not_found_check)

        if_not_layout.addWidget(not_found_group)
        tabs.addTab(if_not_result_tab, "Если изображение не найдено")

        # Добавляем вкладки для ELIF блоков (добавятся динамически)
        self.elif_tabs = []  # Для хранения вкладок ELIF

        layout.addWidget(tabs)
        self.tabs = tabs  # Сохраняем ссылку на TabWidget

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

        # Инициализируем данные для сохранения для блоков ELIF
        self.elif_blocks_data = []

    def remove_action(self, row, for_not_found=False):
        """Удаляет действие из таблицы"""
        table = self.not_found_actions_table if for_not_found else self.additional_actions_table
        table.removeRow(row)

    def add_elif_click_action(self, elif_id):
        """Добавляет действие клика в таблицу действий блока ELIF"""
        # Находим нужный блок ELIF
        elif_block = None
        for block in self.elif_tabs:
            if block["id"] == elif_id:
                elif_block = block
                break

        if not elif_block:
            return

        dialog = ClickModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Получаем таблицу из блока ELIF
            table = elif_block["actions_table"]

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Клик"))
            description = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
            if data['description']:
                description += f", {data['description']}"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_elif_action(elif_id, row))
            table.setCellWidget(row, 2, delete_btn)

    def add_elif_swipe_action(self, elif_id):
        """Добавляет действие свайпа в таблицу действий блока ELIF"""
        # Находим нужный блок ELIF
        elif_block = None
        for block in self.elif_tabs:
            if block["id"] == elif_id:
                elif_block = block
                break

        if not elif_block:
            return

        dialog = SwipeModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Получаем таблицу из блока ELIF
            table = elif_block["actions_table"]

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Свайп"))
            description = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
            if data['description']:
                description += f", {data['description']}"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_elif_action(elif_id, row))
            table.setCellWidget(row, 2, delete_btn)

    def add_elif_sleep_action(self, elif_id):
        """Добавляет действие паузы в таблицу действий блока ELIF"""
        # Находим нужный блок ELIF
        elif_block = None
        for block in self.elif_tabs:
            if block["id"] == elif_id:
                elif_block = block
                break

        if not elif_block:
            return

        # Создаем простой диалог для ввода времени паузы
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

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
        layout.addLayout(hbox)

        # Кнопки
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("OK")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)

        # Если диалог принят, добавляем паузу
        if dialog.exec():
            sleep_time = spinner.value()

            # Получаем таблицу из блока ELIF
            table = elif_block["actions_table"]

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Пауза"))
            description = f"Пауза {sleep_time} секунд"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента
            data = {"type": "sleep", "time": sleep_time}
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_elif_action(elif_id, row))
            table.setCellWidget(row, 2, delete_btn)

    def remove_elif_action(self, elif_id, row):
        """Удаляет действие из таблицы блока ELIF"""
        # Находим нужный блок ELIF
        elif_block = None
        for block in self.elif_tabs:
            if block["id"] == elif_id:
                elif_block = block
                break

        if not elif_block:
            return

        # Удаляем строку из таблицы
        table = elif_block["actions_table"]
        table.removeRow(row)

    def remove_elif_block(self, elif_id):
        """Удаляет блок ELIF"""
        # Находим нужный блок ELIF
        elif_index = -1
        for i, block in enumerate(self.elif_tabs):
            if block["id"] == elif_id:
                elif_index = i
                break

        if elif_index == -1:
            return

        # Спрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            "Удаление блока ELIF",
            "Вы уверены, что хотите удалить этот блок ELIF?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем вкладку
            block = self.elif_tabs[elif_index]
            tab_index = block["tab_index"]
            self.tabs.removeTab(tab_index)

            # Удаляем данные блока из списка
            self.elif_tabs.pop(elif_index)

            # Обновляем индексы вкладок для оставшихся блоков ELIF
            for i, block in enumerate(self.elif_tabs):
                block["tab_index"] = self.tabs.indexOf(block["tab_widget"])

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        images = [self.image_name.text().strip()]

        # Добавляем остальные изображения из таблицы
        for row in range(self.images_list.rowCount()):
            img_name = self.images_list.item(row, 0).text()
            if img_name not in images:  # Избегаем дубликатов
                images.append(img_name)

        # Получаем выбранное изображение для if_result
        selected_image = None
        if self.image_selector_combo.currentIndex() > 0:  # Если выбрано конкретное изображение
            selected_image = self.image_selector_combo.currentText()

        # Собираем действия для if_result
        if_result_actions = []
        if self.additional_actions_check.isChecked():
            for row in range(self.additional_actions_table.rowCount()):
                action_type = self.additional_actions_table.item(row, 0).text()
                action_data = self.additional_actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                if action_type == "Клик":
                    if_result_actions.append({
                        "type": "click",
                        "x": action_data["x"],
                        "y": action_data["y"],
                        "description": action_data["description"],
                        "sleep": action_data["sleep"]
                    })
                elif action_type == "Свайп":
                    if_result_actions.append({
                        "type": "swipe",
                        "x1": action_data["x1"],
                        "y1": action_data["y1"],
                        "x2": action_data["x2"],
                        "y2": action_data["y2"],
                        "description": action_data["description"],
                        "sleep": action_data["sleep"]
                    })
                elif action_type == "Пауза":
                    if_result_actions.append({
                        "type": "sleep",
                        "time": action_data["time"]
                    })

        # Собираем действия для if_not_result
        if_not_result_actions = []
        if self.not_found_additional_actions_check.isChecked():
            for row in range(self.not_found_actions_table.rowCount()):
                action_type = self.not_found_actions_table.item(row, 0).text()
                action_data = self.not_found_actions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

                if action_type == "Клик":
                    if_not_result_actions.append({
                        "type": "click",
                        "x": action_data["x"],
                        "y": action_data["y"],
                        "description": action_data["description"],
                        "sleep": action_data["sleep"]
                    })
                elif action_type == "Свайп":
                    if_not_result_actions.append({
                        "type": "swipe",
                        "x1": action_data["x1"],
                        "y1": action_data["y1"],
                        "x2": action_data["x2"],
                        "y2": action_data["y2"],
                        "description": action_data["description"],
                        "sleep": action_data["sleep"]
                    })
                elif action_type == "Пауза":
                    if_not_result_actions.append({
                        "type": "sleep",
                        "time": action_data["time"]
                    })

        # Собираем данные блоков ELIF
        elif_blocks = []
        for block in self.elif_tabs:
            # Получаем выбранное изображение для блока ELIF
            elif_image = block["image_combo"].currentText()

            # Собираем действия для блока ELIF
            elif_actions = []
            if block["additional_actions_check"].isChecked():
                for row in range(block["actions_table"].rowCount()):
                    action_type = block["actions_table"].item(row, 0).text()
                    action_data = block["actions_table"].item(row, 0).data(Qt.ItemDataRole.UserRole)

                    if action_type == "Клик":
                        elif_actions.append({
                            "type": "click",
                            "x": action_data["x"],
                            "y": action_data["y"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Свайп":
                        elif_actions.append({
                            "type": "swipe",
                            "x1": action_data["x1"],
                            "y1": action_data["y1"],
                            "x2": action_data["x2"],
                            "y2": action_data["y2"],
                            "description": action_data["description"],
                            "sleep": action_data["sleep"]
                        })
                    elif action_type == "Пауза":
                        elif_actions.append({
                            "type": "sleep",
                            "time": action_data["time"]
                        })

            elif_blocks.append({
                "image": elif_image,
                "log_event": block["log_input"].text().strip(),
                "get_coords": block["click_coords_check"].isChecked(),
                "actions": elif_actions,
                "continue": block["continue_check"].isChecked(),
                "stop_bot": block["stop_bot_check"].isChecked()
            })

        result = {
            "type": "image_search",
            "images": images,
            "timeout": self.timeout_input.value(),
            "sleep_after_find": self.sleep_input.value(),
            "if_result": {
                "image": selected_image,  # None или имя конкретного изображения
                "log_event": self.log_event_if_found.text().strip(),
                "get_coords": self.click_coords_check.isChecked(),
                "actions": if_result_actions,
                "continue": self.continue_check.isChecked(),
                "stop_bot": self.stop_bot_check.isChecked()
            },
            "if_not_result": {
                "log_event": self.log_event_if_not_found.text().strip(),
                "actions": if_not_result_actions,
                "continue": self.continue_not_found_check.isChecked(),
                "stop_bot": self.stop_not_found_check.isChecked()
            }
        }

        # Добавляем блоки ELIF только если они есть
        if elif_blocks:
            result["elif_blocks"] = elif_blocks

        return result

    def add_elif_block(self):
        """Добавляет новый блок ELIF для другого изображения"""
        # Создаем новую вкладку для блока ELIF
        elif_tab = QWidget()
        elif_layout = QVBoxLayout(elif_tab)

        elif_label = QLabel("Действия, если найдено другое изображение:")
        elif_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        elif_layout.addWidget(elif_label)

        # Выбор конкретного изображения для ELIF
        hbox_elif_image = QHBoxLayout()
        elif_image_label = QLabel("Выберите изображение:")
        elif_image_combo = QComboBox()

        # Заполняем комбобокс доступными изображениями
        main_image = self.image_name.text().strip()
        if main_image:
            elif_image_combo.addItem(main_image)

        for row in range(self.images_list.rowCount()):
            image_name = self.images_list.item(row, 0).text()
            if image_name != main_image:  # Избегаем дубликатов
                elif_image_combo.addItem(image_name)

        hbox_elif_image.addWidget(elif_image_label)
        hbox_elif_image.addWidget(elif_image_combo, 1)
        elif_layout.addLayout(hbox_elif_image)

        # Сообщение в консоль
        elif_log_label = QLabel("Сообщение в консоль:")
        elif_log_input = QLineEdit()
        elif_log_input.setPlaceholderText("Сообщение для вывода в консоль")
        elif_log_input.setText(f"Найдено изображение {elif_image_combo.currentText()}!")
        elif_layout.addWidget(elif_log_label)
        elif_layout.addWidget(elif_log_input)

        # Группа действий для ELIF
        elif_actions_group = QGroupBox("Выберите действия:")
        elif_actions_layout = QVBoxLayout(elif_actions_group)

        elif_click_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")

        elif_additional_actions_check = QCheckBox("Добавить дополнительные действия (клики/свайпы)")
        elif_additional_actions_check.setToolTip("Добавить дополнительные действия после нахождения изображения")

        # Контейнер для дополнительных действий ELIF
        elif_actions_container = QFrame()
        elif_actions_layout = QVBoxLayout(elif_actions_container)
        elif_actions_layout.setContentsMargins(20, 5, 5, 5)

        # Таблица для дополнительных действий ELIF
        elif_actions_table = QTableWidget(0, 3)
        elif_actions_table.setHorizontalHeaderLabels(["Тип", "Параметры", ""])
        elif_actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        elif_actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        elif_actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        elif_actions_table.setColumnWidth(0, 120)
        elif_actions_table.setColumnWidth(2, 100)

        # Кнопки для добавления действий ELIF
        elif_add_actions_layout = QHBoxLayout()
        elif_add_click_btn = QPushButton("Добавить клик")
        elif_add_swipe_btn = QPushButton("Добавить свайп")
        elif_add_sleep_btn = QPushButton("Добавить паузу")

        # Идентификатор для блока ELIF
        elif_id = len(self.elif_tabs)

        # Подключаем сигналы кнопок с передачей идентификатора блока
        elif_add_click_btn.clicked.connect(lambda: self.add_elif_click_action(elif_id))
        elif_add_swipe_btn.clicked.connect(lambda: self.add_elif_swipe_action(elif_id))
        elif_add_sleep_btn.clicked.connect(lambda: self.add_elif_sleep_action(elif_id))

        elif_add_actions_layout.addWidget(elif_add_click_btn)
        elif_add_actions_layout.addWidget(elif_add_swipe_btn)
        elif_add_actions_layout.addWidget(elif_add_sleep_btn)

        elif_actions_layout.addLayout(elif_add_actions_layout)
        elif_actions_layout.addWidget(elif_actions_table)

        elif_actions_container.setVisible(False)  # По умолчанию скрыт
        elif_additional_actions_check.stateChanged.connect(
            lambda state: elif_actions_container.setVisible(state == Qt.CheckState.Checked))

        elif_continue_check = QCheckBox("Продолжить выполнение (continue)")
        elif_continue_check.setToolTip("Продолжить выполнение модулей на основном холсте")
        elif_continue_check.setChecked(True)  # По умолчанию включено

        elif_stop_bot_check = QCheckBox("Остановить бота (running.clear())")
        elif_stop_bot_check.setToolTip("Экстренно остановить выполнение бота")

        elif_actions_layout.addWidget(elif_click_coords_check)
        elif_actions_layout.addWidget(elif_additional_actions_check)
        elif_actions_layout.addWidget(elif_actions_container)
        elif_actions_layout.addWidget(elif_continue_check)
        elif_actions_layout.addWidget(elif_stop_bot_check)

        elif_layout.addWidget(elif_actions_group)

        # Добавляем кнопку удаления блока ELIF
        remove_elif_btn = QPushButton("Удалить этот блок ELIF")
        remove_elif_btn.clicked.connect(lambda: self.remove_elif_block(elif_id))
        elif_layout.addWidget(remove_elif_btn)

        # Добавляем вкладку в TabWidget
        tab_title = f"ELIF для {elif_image_combo.currentText()}"
        tab_index = self.tabs.addTab(elif_tab, tab_title)

        # Сохраняем данные блока ELIF
        elif_block_data = {
            "id": elif_id,
            "tab_index": tab_index,
            "tab_widget": elif_tab,
            "image_combo": elif_image_combo,
            "log_input": elif_log_input,
            "click_coords_check": elif_click_coords_check,
            "additional_actions_check": elif_additional_actions_check,
            "actions_container": elif_actions_container,
            "actions_table": elif_actions_table,
            "continue_check": elif_continue_check,
            "stop_bot_check": elif_stop_bot_check
        }

        self.elif_tabs.append(elif_block_data)

    def toggle_additional_actions(self, state):
        """Показывает или скрывает контейнер для дополнительных действий"""
        self.additional_actions_container.setVisible(state == Qt.CheckState.Checked)

    def toggle_not_found_additional_actions(self, state):
        """Показывает или скрывает контейнер для дополнительных действий при ненахождении"""
        self.not_found_actions_container.setVisible(state == Qt.CheckState.Checked)

    def browse_image(self):
        """Открывает диалог выбора основного изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Получаем только имя файла
            file_name = os.path.basename(file_path)
            self.image_name.setText(file_name)

            # Добавляем изображение в выпадающий список
            if self.image_selector_combo.findText(file_name) == -1:
                self.image_selector_combo.addItem(file_name)

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

        # Добавляем изображение в выпадающий список
        if self.image_selector_combo.findText(image_name) == -1:
            self.image_selector_combo.addItem(image_name)

        self.additional_image.clear()

    def remove_image(self, row):
        """Удаляет изображение из списка"""
        image_name = self.images_list.item(row, 0).text()

        # Удаляем из таблицы
        self.images_list.removeRow(row)

        # Проверяем, осталось ли это изображение в других строках таблицы
        image_exists = False
        for r in range(self.images_list.rowCount()):
            if self.images_list.item(r, 0).text() == image_name:
                image_exists = True
                break

        # Если это основное изображение и его больше нет в таблице, удаляем из комбобокса
        if not image_exists and image_name != self.image_name.text():
            index = self.image_selector_combo.findText(image_name)
            if index > 0:  # Не удаляем "Любое найденное изображение"
                self.image_selector_combo.removeItem(index)

    def add_click_action(self, for_not_found=False):
        """Добавляет действие клика в таблицу дополнительных действий"""
        dialog = ClickModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Определяем, в какую таблицу добавлять
            table = self.not_found_actions_table if for_not_found else self.additional_actions_table

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Клик"))
            description = f"X: {data['x']}, Y: {data['y']}, Задержка: {data['sleep']}с"
            if data['description']:
                description += f", {data['description']}"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента (Python не позволяет это сделать напрямую,
            # но можно использовать функцию setData с пользовательской ролью)
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_action(row, for_not_found))
            table.setCellWidget(row, 2, delete_btn)

    def add_swipe_action(self, for_not_found=False):
        """Добавляет действие свайпа в таблицу дополнительных действий"""
        dialog = SwipeModuleDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Определяем, в какую таблицу добавлять
            table = self.not_found_actions_table if for_not_found else self.additional_actions_table

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Свайп"))
            description = f"От ({data['x1']}, {data['y1']}) до ({data['x2']}, {data['y2']}), Задержка: {data['sleep']}с"
            if data['description']:
                description += f", {data['description']}"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_action(row, for_not_found))
            table.setCellWidget(row, 2, delete_btn)

    def add_sleep_action(self, for_not_found=False):
        """Добавляет действие паузы (time.sleep) в таблицу дополнительных действий"""
        # Создаем простой диалог для ввода времени паузы
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить паузу")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

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
        layout.addLayout(hbox)

        # Кнопки
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        ok_btn = QPushButton("OK")

        cancel_btn.clicked.connect(dialog.reject)
        ok_btn.clicked.connect(dialog.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)

        # Если диалог принят, добавляем паузу
        if dialog.exec():
            sleep_time = spinner.value()

            # Определяем, в какую таблицу добавлять
            table = self.not_found_actions_table if for_not_found else self.additional_actions_table

            # Добавляем в таблицу
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(row, 0, QTableWidgetItem("Пауза"))
            description = f"Пауза {sleep_time} секунд"
            table.setItem(row, 1, QTableWidgetItem(description))

            # Сохраняем данные в тег элемента
            data = {"type": "sleep", "time": sleep_time}
            item = table.item(row, 0)
            item.setData(Qt.ItemDataRole.UserRole, data)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda: self.remove_action(row, for_not_found))
            table.setCellWidget(row, 2, delete_btn)