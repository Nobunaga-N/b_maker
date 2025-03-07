# src/gui/sidebar.py
"""
Модуль содержит класс боковой панели приложения с возможностью сворачивания.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QSizePolicy,
    QHBoxLayout, QToolButton
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from src.utils.resources import Resources
from src.utils.style_constants import (
    SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, SIDEBAR_ACTIVE_BUTTON_STYLE, SIDEBAR_ICON_STYLE
)


class SideBar(QFrame):
    """
    Боковое меню с подсветкой активной страницы.
    Содержит кнопки для навигации между основными разделами приложения.
    Имеет возможность сворачивания до иконок.
    """
    # Сигналы для переключения между страницами
    pageChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Инициализирует боковую панель.

        Args:
            parent: Родительский виджет.
        """
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
        """Настройка UI компонентов бокового меню"""
        # Основной вертикальный layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 20, 10, 20)
        self.main_layout.setSpacing(15)

        # Создаем кнопку бургера точно так же, как создаем навигационные кнопки
        # Но используем специальный метод, чтобы подключить другую логику
        self.create_burger_button()

        # Создаем обычные навигационные кнопки
        self.create_nav_button("manager", "Менеджер Бота", "manager")
        self.create_nav_button("create", "Создать бота", "create")
        self.create_nav_button("settings", "Настройки", "settings")

        # Добавляем растягивающийся спейсер внизу
        self.main_layout.addStretch()

        # Устанавливаем начальное выделение
        self.set_active_page("manager")

    def create_burger_button(self):
        """Создает кнопку бургера по тому же принципу, что и навигационные кнопки"""
        # Создаем layout для кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Создаем иконку
        self.burger_button = QToolButton()
        self.burger_button.setIcon(QIcon(Resources.get_icon_path("burger")))
        self.burger_button.setIconSize(QSize(24, 24))
        self.burger_button.setStyleSheet(SIDEBAR_ICON_STYLE)
        self.burger_button.setToolTip("Свернуть/развернуть меню")

        # Создаем фиктивную текстовую часть кнопки для сохранения структуры
        self.burger_text = QPushButton("")
        self.burger_text.setFont(QFont("Segoe UI", 12))
        self.burger_text.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        # Добавляем кнопки в layout
        button_layout.addWidget(self.burger_button)
        button_layout.addWidget(self.burger_text, 1)  # stretch=1

        # Подключаем события клика
        self.burger_button.clicked.connect(self.toggle_sidebar)
        self.burger_text.clicked.connect(self.toggle_sidebar)

        # Добавляем layout в основной layout
        self.main_layout.addLayout(button_layout)

    def create_nav_button(self, page_name, text, icon_name):
        """
        Создает навигационную кнопку с иконкой и текстом в отдельном layout.

        Args:
            page_name: Имя страницы для перехода.
            text: Текст кнопки.
            icon_name: Имя иконки.
        """
        # Создаем layout для кнопки
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
        button_layout.setSpacing(10)

        # Создаем иконку
        icon_button = QToolButton()
        icon_button.setIcon(QIcon(Resources.get_icon_path(icon_name)))
        icon_button.setIconSize(QSize(24, 24))
        icon_button.setStyleSheet(SIDEBAR_ICON_STYLE)
        icon_button.setFixedWidth(24)  # Фиксируем ширину кнопки, как у бургера

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
        """
        Устанавливает активную страницу и обновляет стили кнопок.

        Args:
            page_name: Имя активной страницы.
        """
        self._current_page = page_name

        # Сброс стилей всех кнопок
        for name in ["manager", "create", "settings"]:
            text_button = getattr(self, f"text_{name}")
            text_button.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        # Устанавливаем стиль активной кнопки
        active_text_button = getattr(self, f"text_{page_name}")
        active_text_button.setStyleSheet(SIDEBAR_ACTIVE_BUTTON_STYLE)

    def change_page(self, page_name):
        """
        Меняет активную страницу и испускает сигнал для обновления основного окна.

        Args:
            page_name: Имя страницы для активации.
        """
        if self._current_page != page_name:
            self.set_active_page(page_name)
            self.pageChanged.emit(page_name)

    def toggle_sidebar(self):
        """Сворачивает или разворачивает боковую панель."""
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
        """Обновляет видимость текстовых кнопок в зависимости от состояния сворачивания."""
        # Обновляем видимость текстовой части кнопки бургера
        self.burger_text.setVisible(self.expanded)

        # Обновляем видимость текстовых частей навигационных кнопок
        for name in ["manager", "create", "settings"]:
            text_button = getattr(self, f"text_{name}")
            text_button.setVisible(self.expanded)