#!/usr/bin/env python3
"""
Скрипт для автоматического применения изменений цветовой схемы и сворачиваемого меню.
Запустите этот скрипт из корневой директории проекта.
"""

import os
import re
import shutil
from pathlib import Path

# Пути к файлам
STYLE_CONSTANTS_PATH = "src/utils/style_constants.py"
SIDEBAR_PATH = "src/gui/sidebar.py"
DARK_BLUE_QSS_PATH = "assets/styles/dark_blue.qss"
MAIN_PY_PATH = "src/main.py"

# Содержимое новых файлов
STYLE_CONSTANTS_ADDITIONS = """
# Основной цвет для бокового меню (более спокойный темно-синий)
SIDEBAR_COLOR = "#2C3E50"  # Темно-синий

# Цвет акцентов (вместо оранжевого)
ACCENT_COLOR = "#3498DB"  # Синий
ACCENT_COLOR_HOVER = "#2980B9"  # Темно-синий для hover

# Стили для бокового меню
SIDEBAR_STYLE = f\"\"\"
    background-color: {SIDEBAR_COLOR};
\"\"\"

# Стиль кнопок бокового меню
SIDEBAR_BUTTON_STYLE = f\"\"\"
    QPushButton {{
        color: white;
        background: transparent;
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
\"\"\"

# Стиль активной кнопки бокового меню
SIDEBAR_ACTIVE_BUTTON_STYLE = f\"\"\"
    QPushButton {{
        color: white;
        background-color: rgba(0, 0, 0, 0.3);
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: rgba(0, 0, 0, 0.4);
    }}
\"\"\"

# Обновленный стиль акцентных кнопок
ACCENT_BUTTON_STYLE = f\"\"\"
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: white;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_COLOR_HOVER};
    }}
\"\"\"
"""

# Содержимое нового файла sidebar.py
SIDEBAR_CONTENT = """# src/gui/sidebar.py
\"\"\"
Модуль содержит класс боковой панели приложения с возможностью сворачивания.
\"\"\"

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QSizePolicy, 
    QHBoxLayout, QLabel, QToolButton
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from src.utils.resources import Resources
from src.utils.style_constants import (
    SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, SIDEBAR_ACTIVE_BUTTON_STYLE
)


class SideBar(QFrame):
    \"\"\"
    Боковое меню с подсветкой активной страницы.
    Содержит кнопки для навигации между основными разделами приложения.
    Имеет возможность сворачивания до иконок.
    \"\"\"
    # Сигналы для переключения между страницами
    pageChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        \"\"\"
        Инициализирует боковую панель.

        Args:
            parent: Родительский виджет.
        \"\"\"
        super().__init__(parent)
        self.setStyleSheet(SIDEBAR_STYLE)

        # Состояние сворачивания и размеры
        self.expanded = True
        self.expanded_width = 200
        self.collapsed_width = 60
        self.setFixedWidth(self.expanded_width)

        self._current_page = "manager"  # По умолчанию активна страница менеджера
        self.setup_ui()

    def setup_ui(self):
        \"\"\"Настройка UI компонентов бокового меню\"\"\"
        # Основной вертикальный layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 20, 10, 20)
        self.main_layout.setSpacing(15)

        # Кнопка сворачивания (бургер)
        self.burger_button = QToolButton()
        self.burger_button.setIcon(QIcon(Resources.get_icon_path("burger")))
        self.burger_button.setIconSize(QSize(24, 24))
        self.burger_button.setStyleSheet(\"\"\"\
            QToolButton {
                background: transparent;
                border: none;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        \"\"\")
        self.burger_button.setToolTip("Свернуть/развернуть меню")
        self.burger_button.clicked.connect(self.toggle_sidebar)

        # Добавляем кнопку в отдельный layout для выравнивания справа
        burger_layout = QHBoxLayout()
        burger_layout.addStretch()
        burger_layout.addWidget(self.burger_button)
        self.main_layout.addLayout(burger_layout)

        # Создаем кнопки с иконками в горизонтальных layout'ах
        self.create_nav_button("manager", "Менеджер ботов", "manager")
        self.create_nav_button("create", "Создать бота", "create")
        self.create_nav_button("settings", "Настройки", "settings")

        # Добавляем растягивающийся спейсер внизу
        self.main_layout.addStretch()

        # Устанавливаем начальное выделение
        self.set_active_page("manager")

    def create_nav_button(self, page_name, text, icon_name):
        \"\"\"
        Создает навигационную кнопку с иконкой и текстом в отдельном layout.

        Args:
            page_name: Имя страницы для перехода.
            text: Текст кнопки.
            icon_name: Имя иконки.
        \"\"\"
        # Создаем layout для кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Создаем иконку
        icon_button = QToolButton()
        icon_button.setIcon(QIcon(Resources.get_icon_path(icon_name)))
        icon_button.setIconSize(QSize(24, 24))
        icon_button.setStyleSheet(\"\"\"\
            QToolButton {
                background: transparent;
                border: none;
            }
        \"\"\")

        # Создаем текстовую часть кнопки
        text_button = QPushButton(text)
        text_button.setFont(QFont("Segoe UI", 12))
        text_button.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        # Сохраняем ссылки на кнопки как атрибуты класса
        setattr(self, f"icon_{page_name}", icon_button)
        setattr(self, f"text_{page_name}", text_button)

        # Добавляем кнопки в layout
        button_layout.addWidget(icon_button)
        button_layout.addWidget(text_button, 1)  # stretch=1

        # Подключаем события клика
        icon_button.clicked.connect(lambda: self.change_page(page_name))
        text_button.clicked.connect(lambda: self.change_page(page_name))

        # Добавляем layout в основной layout
        self.main_layout.addLayout(button_layout)

    def set_active_page(self, page_name):
        \"\"\"
        Устанавливает активную страницу и обновляет стили кнопок.

        Args:
            page_name: Имя активной страницы.
        \"\"\"
        self._current_page = page_name

        # Сброс стилей всех кнопок
        for name in ["manager", "create", "settings"]:
            text_button = getattr(self, f"text_{name}")
            text_button.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        # Устанавливаем стиль активной кнопки
        active_text_button = getattr(self, f"text_{page_name}")
        active_text_button.setStyleSheet(SIDEBAR_ACTIVE_BUTTON_STYLE)

    def change_page(self, page_name):
        \"\"\"
        Меняет активную страницу и испускает сигнал для обновления основного окна.

        Args:
            page_name: Имя страницы для активации.
        \"\"\"
        if self._current_page != page_name:
            self.set_active_page(page_name)
            self.pageChanged.emit(page_name)

    def toggle_sidebar(self):
        \"\"\"Сворачивает или разворачивает боковую панель.\"\"\"
        target_width = self.collapsed_width if self.expanded else self.expanded_width

        # Создаем анимацию изменения ширины
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Запускаем анимацию
        self.animation.start()

        # Изменяем видимость текстовых кнопок
        self.expanded = not self.expanded
        self.update_button_visibility()

    def update_button_visibility(self):
        \"\"\"Обновляет видимость текстовых кнопок в зависимости от состояния сворачивания.\"\"\"
        for name in ["manager", "create", "settings"]:
            text_button = getattr(self, f"text_{name}")
            text_button.setVisible(self.expanded)
"""

# Содержимое нового файла dark_blue.qss
DARK_BLUE_QSS_CONTENT = """/* assets/styles/dark_blue.qss */

/* Общие стили для всего приложения */
QMainWindow {
    background-color: #121212; /* Тёмно-серый фон */
    color: #FFFFFF;            /* Белый цвет текста по умолчанию */
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12pt;
}

/* Стили для QPushButton */
QPushButton {
    background-color: #3498DB; /* Синий цвет кнопки */
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2980B9; /* Более тёмный синий при наведении */
}
QPushButton:pressed {
    background-color: #1F618D; /* Ещё более тёмный синий при клике */
}

/* Стили для QLineEdit, QComboBox и т.п. */
QLineEdit, QComboBox {
    background-color: #1E1E1E;
    color: #FFFFFF;
    border: 1px solid #3498DB;
    border-radius: 4px;
    padding: 4px;
}

/* Стили для QLabel */
QLabel {
    color: #3498DB; /* Синий цвет для текста */
    font-weight: 600;
}

/* Стили для QListWidget */
QListWidget {
    background-color: #1E1E1E;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
}

/* Пример стиля для QScrollBar */
QScrollBar:vertical {
    background-color: #1E1E1E;
    width: 10px;
    margin: 22px 0 22px 0;
}
QScrollBar::handle:vertical {
    background-color: #3498DB;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    border: none;
}

/* Стили для заголовков таблиц */
QHeaderView::section {
    background-color: #2C3E50;
    color: white;
    padding: 4px;
    border: 1px solid #444;
}

/* Стили для выбранных элементов */
QTableView::item:selected, QListView::item:selected, QTreeView::item:selected {
    background-color: #3498DB;
    color: white;
}

/* Стили для TabWidget */
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #2C3E50;
    color: white;
    padding: 6px 10px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #3498DB;
    font-weight: bold;
}
"""


def backup_file(file_path):
    """Создает резервную копию файла, если она еще не существует."""
    backup_path = f"{file_path}.bak"
    if not os.path.exists(backup_path) and os.path.exists(file_path):
        print(f"Создание резервной копии: {backup_path}")
        shutil.copy2(file_path, backup_path)


def update_style_constants():
    """Добавляет новые константы стилей в файл style_constants.py."""
    # Создаем резервную копию
    backup_file(STYLE_CONSTANTS_PATH)

    # Проверяем, существует ли файл
    if not os.path.exists(STYLE_CONSTANTS_PATH):
        print(f"Файл {STYLE_CONSTANTS_PATH} не найден. Пропускаем обновление констант стилей.")
        return

    # Читаем содержимое файла
    with open(STYLE_CONSTANTS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Проверяем, содержит ли файл уже константы SIDEBAR_COLOR и ACCENT_COLOR
    if "SIDEBAR_COLOR" in content and "ACCENT_COLOR" in content:
        print("Константы стилей уже обновлены. Пропускаем.")
        return

    # Добавляем новые константы в конец файла
    with open(STYLE_CONSTANTS_PATH, "a", encoding="utf-8") as f:
        f.write(STYLE_CONSTANTS_ADDITIONS)

    print(f"Файл {STYLE_CONSTANTS_PATH} успешно обновлен.")


def update_sidebar():
    """Заменяет содержимое файла sidebar.py."""
    # Создаем резервную копию
    backup_file(SIDEBAR_PATH)

    # Записываем новое содержимое
    os.makedirs(os.path.dirname(SIDEBAR_PATH), exist_ok=True)
    with open(SIDEBAR_PATH, "w", encoding="utf-8") as f:
        f.write(SIDEBAR_CONTENT)

    print(f"Файл {SIDEBAR_PATH} успешно обновлен.")


def create_dark_blue_qss():
    """Создает файл dark_blue.qss."""
    os.makedirs(os.path.dirname(DARK_BLUE_QSS_PATH), exist_ok=True)
    with open(DARK_BLUE_QSS_PATH, "w", encoding="utf-8") as f:
        f.write(DARK_BLUE_QSS_CONTENT)

    print(f"Файл {DARK_BLUE_QSS_PATH} успешно создан.")


def update_main_py():
    """Обновляет DEFAULT_STYLE в main.py."""
    # Создаем резервную копию
    backup_file(MAIN_PY_PATH)

    # Проверяем, существует ли файл
    if not os.path.exists(MAIN_PY_PATH):
        print(f"Файл {MAIN_PY_PATH} не найден. Пропускаем обновление.")
        return

    # Читаем содержимое файла
    with open(MAIN_PY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Заменяем DEFAULT_STYLE
    updated_content = re.sub(
        r'DEFAULT_STYLE\s*=\s*["\']dark_orange["\']',
        'DEFAULT_STYLE = "dark_blue"',
        content
    )

    # Записываем обновленное содержимое
    with open(MAIN_PY_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Файл {MAIN_PY_PATH} успешно обновлен.")


def main():
    """Основная функция для применения всех изменений."""
    print("Начало применения изменений...")

    # Обновляем константы стилей
    update_style_constants()

    # Обновляем sidebar.py
    update_sidebar()

    # Создаем dark_blue.qss
    create_dark_blue_qss()

    # Обновляем main.py
    update_main_py()

    print("\nВсе изменения успешно применены!")
    print("\nВы можете внести следующие дополнительные изменения вручную:")
    print("1. Обновите все упоминания #FFA500 (оранжевый) на ACCENT_COLOR в main_window.py")
    print("2. Замените все inline-стили кнопок на ACCENT_BUTTON_STYLE")
    print("3. Убедитесь, что иконка 'burger.svg' находится в папке assets/icons/")
    print("\nГотово!")


if __name__ == "__main__":
    main()