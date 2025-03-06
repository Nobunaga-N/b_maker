# src/gui/sidebar.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import QIcon, QFont


class SideBar(QFrame):
    """
    Боковое меню с анимацией и подсветкой активной страницы.
    Содержит кнопки для навигации между основными разделами приложения.
    """
    # Сигналы для переключения между страницами
    pageChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #FF5722;")
        self.setup_ui()
        self._current_page = "manager"  # По умолчанию активна страница менеджера

    def setup_ui(self):
        """Настройка UI компонентов бокового меню"""
        # Создаем вертикальный layout с отступами
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 20)
        layout.setSpacing(20)

        # Создаем кнопки с иконками
        self.btn_manager = self._create_sidebar_button("Менеджер ботов", "assets/icons/manager.svg")
        self.btn_create = self._create_sidebar_button("Создать бота", "assets/icons/create.svg")
        self.btn_settings = self._create_sidebar_button("Настройки", "assets/icons/settings.svg")

        # Добавляем кнопки в layout
        layout.addWidget(self.btn_manager)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.btn_settings)

        # Добавляем растягивающийся спейсер внизу
        layout.addStretch()

        # Устанавливаем начальное выделение
        self.set_active_page("manager")

        # Подключаем сигналы кнопок
        self.btn_manager.clicked.connect(lambda: self.change_page("manager"))
        self.btn_create.clicked.connect(lambda: self.change_page("create"))
        self.btn_settings.clicked.connect(lambda: self.change_page("settings"))

    def _create_sidebar_button(self, text, icon_path):
        """Создает стилизованную кнопку для бокового меню"""
        btn = QPushButton(text)
        btn.setIcon(QIcon(icon_path))
        btn.setFont(QFont("Segoe UI", 12))
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                text-align: left;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        return btn

    def set_active_page(self, page_name):
        """Устанавливает активную страницу и обновляет стили кнопок"""
        self._current_page = page_name

        # Сброс стилей всех кнопок
        for btn in [self.btn_manager, self.btn_create, self.btn_settings]:
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background: transparent;
                    border: none;
                    text-align: left;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)

        # Устанавливаем стиль активной кнопки
        active_btn_style = """
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: none;
                text-align: left;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.4);
            }
        """

        if page_name == "manager":
            self.btn_manager.setStyleSheet(active_btn_style)
        elif page_name == "create":
            self.btn_create.setStyleSheet(active_btn_style)
        elif page_name == "settings":
            self.btn_settings.setStyleSheet(active_btn_style)

    def change_page(self, page_name):
        """Меняет активную страницу и испускает сигнал для обновления основного окна"""
        if self._current_page != page_name:
            self.set_active_page(page_name)
            self.pageChanged.emit(page_name)