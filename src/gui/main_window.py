# src/gui/main_window.py
import sys
import os
import datetime
import logging
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from src.gui.sidebar import SideBar
from src.gui.page_container import PageContainer
from src.gui.settings_page import SettingsPage
from src.gui.create_bot_page import CreateBotPage
from src.gui.manager_page import ManagerPage
from src.utils.resources import Resources
from src.utils.exceptions import BotMakerError
from src.controllers import BotManagerController


class MainWindow(QMainWindow):
    """
    Главное окно приложения:
    - Использует боковую панель SideBar
    - Использует PageContainer для анимированного перехода между страницами
    - Страницы: Менеджер ботов, Создать бота, Настройки
    """

    def __init__(self, logger: Optional[logging.Logger] = None, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("BOT Maker")
        self.setGeometry(100, 100, 1200, 800)

        # Создаем контроллер для управления бизнес-логикой
        self.bot_manager_controller = BotManagerController(logger)

        # --- Центральный виджет и горизонтальный лейаут ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Боковая панель (новая реализация) ===
        self.sidebar = SideBar()
        main_layout.addWidget(self.sidebar)

        # === Контейнер для страниц с анимацией ===
        self.page_container = PageContainer()
        main_layout.addWidget(self.page_container, stretch=1)

        # === Создаем страницы ===
        # 1. Страница менеджера ботов (используем новый класс)
        self.manager_page = ManagerPage(self, self.logger)
        self.manager_page.createBotRequested.connect(self.on_create_bot_requested)
        self.manager_page.editBotRequested.connect(self.on_edit_bot_requested)

        # 2. Страница создания бота
        self.create_page = CreateBotPage()
        self.create_page.botCreated.connect(self.on_bot_created)

        # 3. Страница настроек
        self.settings_page = SettingsPage()

        # Добавляем страницы в контейнер
        self.page_container.addWidget(self.manager_page)
        self.page_container.addWidget(self.create_page)
        self.page_container.addWidget(self.settings_page)

        # Подключаем сигнал изменения страницы от бокового меню
        self.sidebar.pageChanged.connect(self._handle_page_change)

        # Устанавливаем иконку приложения
        self._set_application_icon()

        # Логируем начало работы
        if self.logger:
            self.logger.info("Главное окно инициализировано")

    def _set_application_icon(self):
        """Устанавливает иконку приложения"""
        try:
            app_icon_path = Resources.get_icon_path("app_icon")
            if os.path.exists(app_icon_path):
                self.setWindowIcon(QIcon(app_icon_path))
            else:
                print(f"Иконка приложения не найдена: {app_icon_path}")
        except Exception as e:
            print(f"Ошибка при установке иконки приложения: {e}")

    def _handle_page_change(self, page_name):
        """Обрабатывает сигнал изменения страницы от бокового меню"""
        if page_name == "manager":
            self.page_container.change_page(0)
        elif page_name == "create":
            self.page_container.change_page(1)
        elif page_name == "settings":
            self.page_container.change_page(2)

    def on_create_bot_requested(self, bot_name=None):
        """Обрабатывает запрос на создание нового бота"""
        # Переключаемся на страницу создания бота
        self.page_container.change_page(1)
        self.sidebar.set_active_page("create")

        # Если нужно, можно использовать bot_name для предзаполнения формы
        if bot_name and hasattr(self.create_page, 'set_initial_bot_name'):
            self.create_page.set_initial_bot_name(bot_name)

        if self.logger:
            self.logger.info(f"Запрошено создание нового бота")

    def on_edit_bot_requested(self, bot_name):
        """Обрабатывает запрос на редактирование бота"""
        if self.logger:
            self.logger.info(f"Запрошено редактирование бота '{bot_name}'")

        # Проверяем существование папки бота
        bot_path = Resources.get_bot_path(bot_name)
        if not os.path.exists(bot_path):
            QMessageBox.warning(self, "Ошибка", f"Папка бота '{bot_name}' не найдена.")
            if self.logger:
                self.logger.warning(f"Папка бота '{bot_name}' не найдена при попытке редактирования")
            return

        # Переключаемся на страницу создания/редактирования бота
        self.page_container.change_page(1)
        self.sidebar.set_active_page("create")

        # Загружаем бота в редактор
        if hasattr(self.create_page, 'load_bot'):
            try:
                success = self.create_page.load_bot(bot_path)
                if success:
                    if self.logger:
                        self.logger.info(f"Бот '{bot_name}' успешно загружен для редактирования")
                else:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить бота '{bot_name}'")
                    if self.logger:
                        self.logger.error(f"Не удалось загрузить бота '{bot_name}' для редактирования")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке бота '{bot_name}': {str(e)}")
                if self.logger:
                    self.logger.error(f"Ошибка при загрузке бота '{bot_name}': {str(e)}")
        else:
            QMessageBox.warning(self, "Ошибка", "Функция загрузки бота недоступна в текущей версии.")
            if self.logger:
                self.logger.error("Метод load_bot не найден в create_page")

    def on_bot_created(self, bot_name, game_name):
        """
        Обрабатывает сигнал о создании бота.
        Добавляет нового бота в список ботов на странице менеджера.
        """
        if self.logger:
            self.logger.info(f"Бот '{bot_name}' для игры '{game_name}' успешно создан")

        # Переключаемся на страницу менеджера
        self.page_container.change_page(0)
        self.sidebar.set_active_page("manager")

        # Обновляем список ботов на странице менеджера
        self.manager_page.load_bots()

        # Показываем сообщение об успешном создании бота
        QMessageBox.information(self, "Успех", f"Бот '{bot_name}' успешно создан и добавлен в список!")

    def closeEvent(self, event):
        """Перехватывает событие закрытия окна для корректного завершения работы"""
        if self.logger:
            self.logger.info("Приложение завершает работу")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Настраиваем стиль приложения
    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
    """)

    # Создаем простой логгер для автономного запуска
    logger = logging.getLogger('bot_maker')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Создаем и показываем главное окно
    window = MainWindow(logger)
    window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())