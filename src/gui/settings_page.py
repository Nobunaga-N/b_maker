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
        title_label = QLabel("Настройки приложения")
        title_label.setStyleSheet("color: #FFA500;")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        # Раздел игр и активностей
        games_frame = QFrame()
        games_frame.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333; border-radius: 5px;")
        games_layout = QVBoxLayout(games_frame)
        games_layout.setContentsMargins(15, 15, 15, 15)
        games_layout.setSpacing(10)

        # Подзаголовок раздела
        section_title = QLabel("Игры и активности")
        section_title.setStyleSheet("color: #FFA500;")
        section_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        games_layout.addWidget(section_title)

        # Пояснение
        description = QLabel(
            "Здесь вы можете связать названия игр с их активностями (например, com.allstarunion.beastlord)")
        description.setStyleSheet("color: white;")
        description.setWordWrap(True)
        games_layout.addWidget(description)

        # Форма добавления
        form_layout = QHBoxLayout()

        self.game_input = QLineEdit()
        self.game_input.setPlaceholderText("Название игры (например, Beast Lord)")
        self.game_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C; padding: 8px; border-radius: 4px;")

        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Активность (например, com.allstarunion.beastlord)")
        self.activity_input.setStyleSheet(
            "color: #FFFFFF; background-color: #2C2C2C; padding: 8px; border-radius: 4px;")

        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        self.add_button.clicked.connect(self.add_game_activity)

        form_layout.addWidget(self.game_input, stretch=2)
        form_layout.addWidget(self.activity_input, stretch=3)
        form_layout.addWidget(self.add_button)

        games_layout.addLayout(form_layout)

        # Таблица игр и активностей
        self.table = QTableWidget(0, 3)  # 0 строк, 3 столбца (игра, активность, кнопка удаления)
        self.table.setHorizontalHeaderLabels(["Игра", "Активность", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setFixedHeight(30)
        self.table.setColumnWidth(2, 100)  # Ширина столбца с кнопкой
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #444;
                gridline-color: #444;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #FFA500;
                padding: 4px;
                border: 1px solid #444;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #444;
            }
        """)
        games_layout.addWidget(self.table)

        # Кнопка Сохранить
        self.save_button = QPushButton("Сохранить настройки")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
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

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: #FFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_game_activity(row))

        self.table.setCellWidget(row, 2, delete_button)

        # Добавляем в словарь
        self.games_activities[game] = activity

        # Очищаем поля ввода
        self.game_input.clear()
        self.activity_input.clear()

        print(f"Добавлена игра: {game} с активностью: {activity}")

    def delete_game_activity(self, row):
        """Удаляет запись из таблицы и словаря"""
        game = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить игру '{game}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)
            if game in self.games_activities:
                del self.games_activities[game]
            print(f"Удалена игра: {game}")

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
            with open('config/games_activities.json', 'w', encoding='utf-8') as f:
                json.dump(self.games_activities, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")
            print("Настройки игр и активностей сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
            print(f"Ошибка сохранения настроек: {e}")

    def load_games_activities(self):
        """Загружает игры и активности из JSON файла"""
        try:
            if os.path.exists('config/games_activities.json'):
                with open('config/games_activities.json', 'r', encoding='utf-8') as f:
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

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: #FFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_game_activity(row))

        self.table.setCellWidget(row, 2, delete_button)