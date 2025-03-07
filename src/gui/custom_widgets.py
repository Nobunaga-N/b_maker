# b_maker/src/gui/custom_widgets.py
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import os
from typing import Dict, List, Any, Optional

# Обновление для класса ClickModuleDialog

class ClickModuleDialog(QDialog):
    """
    Диалог для настройки модуля клика.
    Позволяет задать координаты, описание и время задержки после клика.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля клика")
        self.setModal(True)
        self.resize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.setStyleSheet("""
            QDialog {
                background-color: #2C2C2C;
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
            QGroupBox {
                color: #FFA500;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        coords_group = QGroupBox("Координаты клика")
        coords_layout = QVBoxLayout(coords_group)

        # Координата X с использованием QSpinBox
        x_layout = QHBoxLayout()
        x_label = QLabel("Координата X:")
        self.x_input = QSpinBox()
        self.x_input.setRange(0, 5000)
        self.x_input.setSingleStep(1)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_input)
        coords_layout.addLayout(x_layout)

        # Координата Y с использованием QSpinBox
        y_layout = QHBoxLayout()
        y_label = QLabel("Координата Y:")
        self.y_input = QSpinBox()
        self.y_input.setRange(0, 5000)
        self.y_input.setSingleStep(1)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_input)
        coords_layout.addLayout(y_layout)

        layout.addWidget(coords_group)

        # Описания
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QVBoxLayout(descriptions_group)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addWidget(QLabel("Описание:"))
        descriptions_layout.addWidget(self.description_input)

        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addWidget(QLabel("Описание для консоли:"))
        descriptions_layout.addWidget(self.console_description_input)

        layout.addWidget(descriptions_group)

        # Задержка
        delay_group = QGroupBox("Задержка")
        delay_layout = QHBoxLayout(delay_group)

        delay_label = QLabel("Время задержки после клика:")
        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 60.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.sleep_input)

        layout.addWidget(delay_group)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)

        layout.addLayout(buttons_layout)

    def get_data(self) -> dict:
        """
        Возвращает данные, введенные пользователем.
        """
        return {
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.value()
        }


class SwipeModuleDialog(QDialog):
    """
    Диалог для настройки модуля свайпа.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля свайпа")
        self.setModal(True)
        self.resize(450, 400)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога свайпа"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Применяем общий стиль к диалогу
        self.setStyleSheet("""
            QDialog {
                background-color: #2C2C2C;
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
            QGroupBox {
                color: #FFA500;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        # Координаты начала свайпа
        start_group = QGroupBox("Начальные координаты")
        start_layout = QVBoxLayout(start_group)

        hbox_start_x = QHBoxLayout()
        x_label = QLabel("Координата X:")
        self.start_x_input = QSpinBox()
        self.start_x_input.setRange(0, 5000)
        hbox_start_x.addWidget(x_label)
        hbox_start_x.addWidget(self.start_x_input)

        hbox_start_y = QHBoxLayout()
        y_label = QLabel("Координата Y:")
        self.start_y_input = QSpinBox()
        self.start_y_input.setRange(0, 5000)
        hbox_start_y.addWidget(y_label)
        hbox_start_y.addWidget(self.start_y_input)

        start_layout.addLayout(hbox_start_x)
        start_layout.addLayout(hbox_start_y)
        layout.addWidget(start_group)

        # Координаты конца свайпа
        end_group = QGroupBox("Конечные координаты")
        end_layout = QVBoxLayout(end_group)

        hbox_end_x = QHBoxLayout()
        end_x_label = QLabel("Координата X:")
        self.end_x_input = QSpinBox()
        self.end_x_input.setRange(0, 5000)
        hbox_end_x.addWidget(end_x_label)
        hbox_end_x.addWidget(self.end_x_input)

        hbox_end_y = QHBoxLayout()
        end_y_label = QLabel("Координата Y:")
        self.end_y_input = QSpinBox()
        self.end_y_input.setRange(0, 5000)
        hbox_end_y.addWidget(end_y_label)
        hbox_end_y.addWidget(self.end_y_input)

        end_layout.addLayout(hbox_end_x)
        end_layout.addLayout(hbox_end_y)
        layout.addWidget(end_group)

        # Описания
        descriptions_group = QGroupBox("Описания")
        descriptions_layout = QVBoxLayout(descriptions_group)

        desc_label = QLabel("Описание:")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание для отображения на холсте")
        descriptions_layout.addWidget(desc_label)
        descriptions_layout.addWidget(self.description_input)

        console_desc_label = QLabel("Описание для консоли:")
        self.console_description_input = QLineEdit()
        self.console_description_input.setPlaceholderText("Описание для вывода в консоль")
        descriptions_layout.addWidget(console_desc_label)
        descriptions_layout.addWidget(self.console_description_input)

        layout.addWidget(descriptions_group)

        # Задержка
        delay_group = QGroupBox("Задержка")
        delay_layout = QHBoxLayout(delay_group)

        sleep_label = QLabel("Время задержки после свайпа:")
        self.sleep_input = QDoubleSpinBox()
        self.sleep_input.setRange(0.0, 60.0)
        self.sleep_input.setDecimals(1)
        self.sleep_input.setSingleStep(0.1)
        self.sleep_input.setSuffix(" сек")
        delay_layout.addWidget(sleep_label)
        delay_layout.addWidget(self.sleep_input)

        layout.addWidget(delay_group)

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        return {
            "type": "swipe",
            "x1": self.start_x_input.value(),
            "y1": self.start_y_input.value(),
            "x2": self.end_x_input.value(),
            "y2": self.end_y_input.value(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.value()
        }


class ImageSearchModuleDialog(QDialog):
    """
    Диалог для настройки модуля поиска изображений.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля поиска изображений")
        self.setModal(True)
        self.resize(650, 500)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Применяем общий стиль к диалогу
        self.setStyleSheet("""
            QDialog {
                background-color: #2C2C2C;
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
            QGroupBox {
                color: #FFA500;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555;
                background-color: #2C2C2C;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #555;
                background-color: #FF5722;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2C2C2C;
            }
            QTabBar::tab {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background-color: #FF5722;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QTableWidget {
                background-color: #3A3A3A;
                color: white;
                gridline-color: #555;
            }
            QHeaderView::section {
                background-color: #FF5722;
                color: white;
                padding: 4px;
                border: 1px solid #555;
            }
        """)

        # Выбор изображения
        image_group = QGroupBox("Выбор изображения")
        image_layout = QVBoxLayout(image_group)

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
        self.timeout_input.setValue(60)
        self.timeout_input.setSuffix(" сек")
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
        hbox_add.addWidget(add_img_label)
        hbox_add.addWidget(self.additional_image, 1)
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

        # Вкладки для "if result" и "if not result"
        tabs = QTabWidget()

        # Вкладка "if result"
        if_result_tab = QWidget()
        if_result_layout = QVBoxLayout(if_result_tab)

        found_label = QLabel("Действия, если изображение найдено:")
        found_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        if_result_layout.addWidget(found_label)

        log_label = QLabel("Сообщение в консоль:")
        self.log_event_if_found = QLineEdit()
        self.log_event_if_found.setPlaceholderText("Сообщение для вывода в консоль")
        if_result_layout.addWidget(log_label)
        if_result_layout.addWidget(self.log_event_if_found)

        actions_group = QGroupBox("Выберите действия:")
        actions_layout = QVBoxLayout(actions_group)

        self.click_coords_check = QCheckBox("Кликнуть по координатам найденного изображения (get_coords)")
        self.continue_check = QCheckBox("Продолжить выполнение (continue)")
        self.stop_bot_check = QCheckBox("Остановить бота (running.clear())")

        actions_layout.addWidget(self.click_coords_check)
        actions_layout.addWidget(self.continue_check)
        actions_layout.addWidget(self.stop_bot_check)

        if_result_layout.addWidget(actions_group)
        tabs.addTab(if_result_tab, "Если изображение найдено")

        # Вкладка "if not result"
        if_not_result_tab = QWidget()
        if_not_layout = QVBoxLayout(if_not_result_tab)

        not_found_label = QLabel("Действия, если изображение не найдено:")
        not_found_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        if_not_layout.addWidget(not_found_label)

        nf_log_label = QLabel("Сообщение в консоль:")
        self.log_event_if_not_found = QLineEdit()
        self.log_event_if_not_found.setPlaceholderText("Сообщение для вывода в консоль")
        if_not_layout.addWidget(nf_log_label)
        if_not_layout.addWidget(self.log_event_if_not_found)

        not_found_group = QGroupBox("Выберите действия:")
        not_found_layout = QVBoxLayout(not_found_group)

        self.continue_not_found_check = QCheckBox("Продолжить выполнение (continue)")
        self.stop_not_found_check = QCheckBox("Остановить бота (running.clear())")

        not_found_layout.addWidget(self.continue_not_found_check)
        not_found_layout.addWidget(self.stop_not_found_check)

        if_not_layout.addWidget(not_found_group)
        tabs.addTab(if_not_result_tab, "Если изображение не найдено")

        layout.addWidget(tabs)

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
        """Открывает диалог выбора изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Получаем только имя файла
            file_name = os.path.basename(file_path)
            self.image_name.setText(file_name)

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

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        images = [self.image_name.text().strip()]

        # Добавляем остальные изображения из таблицы
        for row in range(self.images_list.rowCount()):
            img_name = self.images_list.item(row, 0).text()
            if img_name not in images:  # Избегаем дубликатов
                images.append(img_name)

        return {
            "type": "image_search",
            "images": images,
            "timeout": self.timeout_input.value(),
            "if_result": {
                "log_event": self.log_event_if_found.text().strip(),
                "get_coords": self.click_coords_check.isChecked(),
                "continue": self.continue_check.isChecked(),
                "stop_bot": self.stop_bot_check.isChecked()
            },
            "if_not_result": {
                "log_event": self.log_event_if_not_found.text().strip(),
                "continue": self.continue_not_found_check.isChecked(),
                "stop_bot": self.stop_not_found_check.isChecked()
            }
        }


class ActivityModuleDialog(QDialog):
    """
    Диалог для настройки модуля проверки Activity.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля проверки Activity")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога Activity"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Применяем общий стиль к диалогу
        self.setStyleSheet("""
            QDialog {
                background-color: #2C2C2C;
                color: white;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
            QGroupBox {
                color: #FFA500;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555;
                background-color: #2C2C2C;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #555;
                background-color: #FF5722;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                min-width: 6em;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #555;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #555;
                selection-background-color: #FF5722;
                background-color: #2C2C2C;
                color: white;
            }
        """)

        title_label = QLabel("Настройка проверки активности игры")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFA500; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Активация модуля
        enable_group = QGroupBox("Статус модуля")
        enable_layout = QVBoxLayout(enable_group)
        self.enable_check = QCheckBox("Включить проверку активности")
        self.enable_check.setChecked(True)
        enable_layout.addWidget(self.enable_check)
        layout.addWidget(enable_group)

        # Группа с настройками
        settings_group = QGroupBox("Настройки проверки активности")
        settings_layout = QVBoxLayout(settings_group)

        # Выпадающий список с опциями
        action_label = QLabel("Действие при вылете игры:")
        settings_layout.addWidget(action_label)

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "continue_bot - Перезапустить игру и продолжить",
            "activity.running.clear(0) - Закрыть эмулятор",
            "activity.running.clear(1) - Закрыть эмулятор и запустить следующий"
        ])
        settings_layout.addWidget(self.action_combo)

        # Опции для continue_bot
        self.continue_options_group = QGroupBox("Опции для continue_bot")
        continue_layout = QVBoxLayout(self.continue_options_group)

        self.restart_emulator_check = QCheckBox("Перезапустить эмулятор (restart.emulator)")
        self.close_game_check = QCheckBox("Закрыть игру (close.game)")
        self.start_game_check = QCheckBox("Запустить игру (start.game)")
        self.start_game_check.setChecked(True)  # По умолчанию включено

        hbox_restart = QHBoxLayout()
        self.restart_from_line = QSpinBox()
        self.restart_from_line.setRange(1, 999)
        self.restart_from_line.setEnabled(False)
        self.restart_from_check = QCheckBox("Перезапустить со строки:")
        self.restart_from_check.toggled.connect(self.restart_from_line.setEnabled)
        hbox_restart.addWidget(self.restart_from_check)
        hbox_restart.addWidget(self.restart_from_line)

        self.restart_from_last_check = QCheckBox("Перезапустить с последней позиции (restart.from.last)")

        continue_layout.addWidget(self.restart_emulator_check)
        continue_layout.addWidget(self.close_game_check)
        continue_layout.addWidget(self.start_game_check)
        continue_layout.addLayout(hbox_restart)
        continue_layout.addWidget(self.restart_from_last_check)

        settings_layout.addWidget(self.continue_options_group)

        # Обработка выбора действия
        self.action_combo.currentIndexChanged.connect(self.update_ui_based_on_action)

        layout.addWidget(settings_group)

        # Кнопки подтверждения/отмены
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        layout.addLayout(buttons_layout)

        # Инициализация UI согласно начальному выбору
        self.update_ui_based_on_action(0)

    def update_ui_based_on_action(self, index):
        """Обновляет UI в зависимости от выбранного действия"""
        self.continue_options_group.setVisible(index == 0)  # Показываем опции только для continue_bot

    def get_data(self) -> Dict[str, Any]:
        """Возвращает данные, заполненные пользователем"""
        action_index = self.action_combo.currentIndex()
        action_type = ["continue_bot", "activity.running.clear(0)", "activity.running.clear(1)"][action_index]

        data = {
            "type": "activity",
            "enabled": self.enable_check.isChecked(),
            "action": action_type,
        }

        # Добавляем опции для continue_bot
        if action_type == "continue_bot":
            data["options"] = {
                "restart_emulator": self.restart_emulator_check.isChecked(),
                "close_game": self.close_game_check.isChecked(),
                "start_game": self.start_game_check.isChecked(),
                "restart_from_last": self.restart_from_last_check.isChecked(),
            }

            if self.restart_from_check.isChecked():
                data["options"]["restart_from_line"] = self.restart_from_line.value()

        return data