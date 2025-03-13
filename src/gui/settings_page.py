# src/gui/settings_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import json
import os

from src.utils.style_constants import (
    TITLE_STYLE, MAIN_FRAME_STYLE, BASE_TABLE_STYLE, SETTINGS_BUTTON_STYLE
)
from src.utils.ui_factory import (
    create_title_label, create_accent_button, create_input_field,
    create_delete_button, create_table, create_frame
)
from src.utils.resources import Resources


class SettingsPage(QWidget):
    """
    Страница настроек приложения.
    Позволяет пользователю управлять связями между играми и их активностями.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        self.games_activities = {}  # Словарь {название_игры: активность}
        self.setup_ui()
        self.load_games_activities()

    def setup_ui(self):
        """Настройка интерфейса страницы настроек"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = create_title_label("Настройки приложения", 18)
        main_layout.addWidget(title_label)

        # Раздел игр и активностей
        games_frame = create_frame()
        games_layout = QVBoxLayout(games_frame)
        games_layout.setContentsMargins(15, 15, 15, 15)
        games_layout.setSpacing(10)

        # Подзаголовок раздела
        section_title = create_title_label("Игры и активности", 14)
        games_layout.addWidget(section_title)

        # Пояснение
        description = QLabel(
            "Здесь вы можете связать названия игр с их активностями (например, com.allstarunion.beastlord)")
        description.setStyleSheet("color: white;")
        description.setWordWrap(True)
        games_layout.addWidget(description)

        # Форма добавления
        form_layout = QHBoxLayout()

        self.game_input = create_input_field("Название игры (например, Beast Lord)")
        self.activity_input = create_input_field("Активность (например, com.allstarunion.beastlord)")
        self.add_button = create_accent_button("Добавить")
        self.add_button.clicked.connect(self.add_game_activity)

        form_layout.addWidget(self.game_input, stretch=2)
        form_layout.addWidget(self.activity_input, stretch=3)
        form_layout.addWidget(self.add_button)

        games_layout.addLayout(form_layout)

        # Таблица игр и активностей
        self.table = create_table(["Игра", "Активность", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setFixedHeight(30)
        self.table.setColumnWidth(2, 100)  # Ширина столбца с кнопкой
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)

        games_layout.addWidget(self.table)

        # Кнопка Сохранить
        self.save_button = create_accent_button("Сохранить настройки")
        self.save_button.setStyleSheet(SETTINGS_BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_games_activities)
        games_layout.addWidget(self.save_button)

        main_layout.addWidget(games_frame)
        main_layout.addStretch()

    def add_game_activity(self):
        """Добавляет новую пару игра-активность в таблицу"""
        game = self.game_input.text().strip()
        activity = self.activity_input.text().strip()

        if not game or not activity:
            QMessageBox.warning(self, "Внимание", "Необходимо заполнить оба поля.")
            return

        # Проверка на дублирование
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).text() == game:
                reply = QMessageBox.question(
                    self, "Игра уже существует",
                    f"Игра '{game}' уже существует. Обновить активность?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.table.item(i, 1).setText(activity)
                    self.games_activities[game] = activity
                self.game_input.clear()
                self.activity_input.clear()
                return

        # Добавление новой записи
        row = self.table.rowCount()
        self.table.insertRow(row)

        game_item = QTableWidgetItem(game)
        activity_item = QTableWidgetItem(activity)

        self.table.setItem(row, 0, game_item)
        self.table.setItem(row, 1, activity_item)

        # Создаем кнопку удаления
        self.add_delete_button_to_row(row)

        # Добавляем в словарь
        self.games_activities[game] = activity

        # Очищаем поля ввода
        self.game_input.clear()
        self.activity_input.clear()

        print(f"Добавлена игра: {game} с активностью: {activity}")

    def add_delete_button_to_row(self, row):
        """
        Создает и добавляет кнопку удаления в указанную строку таблицы.
        Использует замыкание для правильного захвата переменной row.
        """
        # Создаем виджет-контейнер для кнопки
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Создаем кнопку удаления
        delete_button = create_delete_button("Удалить")

        # Важно: используем замыкание, чтобы сохранить текущий row для callback
        def create_delete_callback(r):
            return lambda: self.delete_game_activity(r)

        # Создаем callback, который захватывает текущее значение row
        delete_callback = create_delete_callback(row)
        delete_button.clicked.connect(delete_callback)

        # Добавляем кнопку в контейнер
        button_layout.addWidget(delete_button)

        # Добавляем контейнер в ячейку таблицы
        self.table.setCellWidget(row, 2, button_container)

    def delete_game_activity(self, row):
        """Удаляет запись из таблицы и словаря по индексу строки"""
        # Проверяем, существует ли такая строка
        if row < 0 or row >= self.table.rowCount():
            print(f"Ошибка: строка {row} не существует")
            return

        # Получаем название игры для удаления из словаря
        game = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить игру '{game}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем строку из таблицы
            self.table.removeRow(row)

            # Удаляем из словаря
            if game in self.games_activities:
                del self.games_activities[game]

            # Обновляем индексы колбэков для всех кнопок удаления
            self.update_delete_buttons()

            print(f"Удалена игра: {game}")

    def update_delete_buttons(self):
        """
        Обновляет индексы для всех кнопок удаления.
        Вызывается после удаления строки из таблицы.
        """
        # Для каждой строки в таблице
        for i in range(self.table.rowCount()):
            # Создаем новую кнопку удаления с правильным индексом
            self.add_delete_button_to_row(i)

    def save_games_activities(self):
        """Сохраняет игры и активности в JSON файл"""
        try:
            # Обновляем словарь из таблицы (на случай ручных изменений)
            self.games_activities = {}
            for row in range(self.table.rowCount()):
                game = self.table.item(row, 0).text()
                activity = self.table.item(row, 1).text()
                self.games_activities[game] = activity

            # Создаем директорию config, если не существует
            os.makedirs('config', exist_ok=True)

            # Сохраняем в JSON
            config_path = Resources.get_config_path("games_activities")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.games_activities, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")
            print("Настройки игр и активностей сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
            print(f"Ошибка сохранения настроек: {e}")

    def load_games_activities(self):
        """Загружает игры и активности из JSON файла"""
        try:
            config_path = Resources.get_config_path("games_activities")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.games_activities = json.load(f)

                # Заполняем таблицу
                self.table.setRowCount(0)  # Очищаем таблицу
                for game, activity in self.games_activities.items():
                    self.add_game_to_table(game, activity)

                print("Настройки игр и активностей загружены")
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def add_game_to_table(self, game, activity):
        """Добавляет игру и активность в таблицу"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        game_item = QTableWidgetItem(game)
        activity_item = QTableWidgetItem(activity)

        self.table.setItem(row, 0, game_item)
        self.table.setItem(row, 1, activity_item)

        # Используем общий метод для добавления кнопки удаления
        self.add_delete_button_to_row(row)