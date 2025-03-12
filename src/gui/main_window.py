# src/gui/main_window.py
import sys
import os
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QSpinBox, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QAbstractItemView, QDialog,
    QDateTimeEdit, QFormLayout, QToolButton, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt, QPoint, QDateTime, QSize
from PyQt6.QtGui import QFont, QIcon, QBrush, QColor, QKeyEvent
from src.gui.sidebar import SideBar
from src.gui.page_container import PageContainer
from src.gui.settings_page import SettingsPage
from src.gui.create_bot_page import CreateBotPage
from src.utils.style_constants import (
    ACCENT_BUTTON_STYLE, ACCENT_COLOR, MAIN_FRAME_STYLE,
    TABLE_STYLE, COMPACT_BUTTON_STYLE
)
from src.utils.ui_factory import (
    create_title_label, create_accent_button, create_input_field,
    create_tool_button, create_text_label, create_spinbox_without_buttons
)

import logging


# ------------------ УЛУЧШЕННЫЙ QWIDGET ДЛЯ БОТА (КОМПАКТНЫЕ КНОПКИ) ------------------ #
class BotWidget(QWidget):
    """
    Компактный виджет с кнопкой "Start" для бота.
    Оптимизирован для экономии пространства в интерфейсе.
    """

    def __init__(self, bot_id: str, parent=None):
        super().__init__(parent)
        self.bot_id = bot_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Создаем компактную кнопку с иконкой вместо текста
        # Создаем более заметную кнопку Start
        self.btn_start = QPushButton("Start")
        self.btn_start.setIcon(QIcon("assets/icons/play.svg"))
        self.btn_start.setToolTip("Запустить бота")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        self.btn_start.clicked.connect(self.on_start)

        layout.addWidget(self.btn_start)
        layout.addStretch(1)  # Добавляем гибкий элемент для выравнивания по левому краю

    def on_start(self):
        """
        Логика запуска бота (заглушка).
        """
        print(f"Запуск бота {self.bot_id}...")


# ------------------ УЛУЧШЕННЫЙ QWIDGET ДЛЯ ЭМУЛЯТОРА (КОМПАКТНЫЕ КНОПКИ) ------------------ #
class EmulatorWidget(QWidget):
    """
    Компактный виджет с кнопками "Console" и "Stop" для эмулятора.
    Оптимизирован для экономии пространства в интерфейсе.
    """

    def __init__(self, emulator_id: int, parent=None):
        super().__init__(parent)
        self.emulator_id = emulator_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Создаем кнопку Console с текстом и иконкой
        self.btn_console = QPushButton("Console")
        self.btn_console.setIcon(QIcon("assets/icons/console.svg"))
        self.btn_console.setToolTip("Открыть консоль")
        self.btn_console.setStyleSheet("""
            QPushButton {
                background-color: #4477FF;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5588FF;
            }
        """)
        self.btn_console.clicked.connect(self.on_console)

        # Создаем кнопку Stop с текстом и иконкой
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setIcon(QIcon("assets/icons/stop.svg"))
        self.btn_stop.setToolTip("Остановить эмулятор")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)

        layout.addWidget(self.btn_console)
        layout.addWidget(self.btn_stop)
        layout.addStretch(1)  # Добавляем гибкий элемент для выравнивания по левому краю

    def on_console(self):
        """
        Открывает консоль для эмулятора (заглушка).
        """
        print(f"Открываем консоль для эмулятора {self.emulator_id}...")

    def on_stop(self):
        """
        Останавливает эмулятор (заглушка).
        """
        print(f"Остановка эмулятора {self.emulator_id}...")


# ------------------ УЛУЧШЕННЫЙ QTreeWidget ДЛЯ ОЧЕРЕДИ ------------------ #
class ManagerQueueWidget(QTreeWidget):
    """
    QTreeWidget для очереди ботов с улучшенной видимостью элементов управления.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Устанавливаем количество столбцов и заголовки
        self.setColumnCount(7)
        self.setHeaderLabels([
            "№", "Бот", "Игра", "Потоки",
            "Запланирован на", "Циклы", "Время раб."
        ])

        # Сохраняем ссылку на текущий элемент для контекстного меню
        self.selected_item = None

        # Стилизуем заголовки
        self.header().setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;
                color: #FFA500;
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }
        """)

        # Настройка размеров столбцов
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # №
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Бот
        self.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Игра
        self.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Потоки
        self.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Запланирован
        self.header().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Циклы
        self.header().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Время работы
        self.setColumnWidth(0, 30)  # №
        self.setColumnWidth(3, 60)  # Потоки
        self.setColumnWidth(4, 160)  # Запланирован
        self.setColumnWidth(5, 60)  # Циклы
        self.setColumnWidth(6, 80)  # Время работы

        # Разрешаем Drag & Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        # Разрешаем выбор single
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Улучшаем видимость строк и элементов
        self.setIndentation(10)  # Уменьшаем отступ для дочерних элементов
        self.setStyleSheet(TABLE_STYLE + """
            QTreeView::item {
                padding: 6px 0;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(assets/icons/expand.svg);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(assets/icons/collapse.svg);
            }
            QTreeView::item:selected {
                background-color: #3A6EA5;
                color: white;
            }
            QTreeView::item:hover {
                background-color: #2C5175;
            }
        """)

        # Включаем двойной клик для открытия консоли эмулятора
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Контекстное меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def dropEvent(self, event):
        super().dropEvent(event)
        self._flatten_top_level()

    def _flatten_top_level(self):
        """
        Если бот вдруг стал child другого, возвращаем его на верхний уровень.
        """
        to_lift = []
        top_count = self.topLevelItemCount()
        for i in range(top_count):
            parent_item = self.topLevelItem(i)
            c_count = parent_item.childCount()
            for c in range(c_count):
                child_item = parent_item.child(c)
                # Если child_item - это тоже "бот" (не "Эмулятор ..."), поднимаем
                if not child_item.text(1).startswith("Эмулятор "):
                    to_lift.append(child_item)

        for item in to_lift:
            parent = item.parent()
            new_item = QTreeWidgetItem([item.text(k) for k in range(self.columnCount())])
            # Копируем шрифт/цвет
            for col in range(self.columnCount()):
                new_item.setFont(col, item.font(col))
                new_item.setForeground(col, item.foreground(col))
            self.addTopLevelItem(new_item)
            parent.removeChild(item)

        self._renumber_items()

    def _renumber_items(self):
        """
        Перенумеровывает top-level items (первый столбец).
        """
        for i in range(self.topLevelItemCount()):
            it = self.topLevelItem(i)
            it.setText(0, str(i + 1))

    def keyPressEvent(self, event: QKeyEvent):
        """
        При нажатии Delete — удаляем выбранного бота (top-level).
        """
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected_bot()
        else:
            super().keyPressEvent(event)

    def show_context_menu(self, pos: QPoint):
        """
        Контекстное меню по правому клику с различными действиями
        в зависимости от выбранного элемента.
        """
        item = self.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        if item.parent() is None:
            # Это бот (top-level item)
            settings_action = menu.addAction("Настройки")
            settings_action.setIcon(QIcon("assets/icons/settings.svg"))

            start_action = menu.addAction("Запустить")
            start_action.setIcon(QIcon("assets/icons/play.svg"))

            duplicate_action = menu.addAction("Дублировать")
            duplicate_action.setIcon(QIcon("assets/icons/copy.svg"))

            menu.addSeparator()

            delete_action = menu.addAction("Удалить")
            delete_action.setIcon(QIcon("assets/icons/delete.svg"))
        else:
            # Это эмулятор (child item)
            console_action = menu.addAction("Открыть консоль")
            console_action.setIcon(QIcon("assets/icons/console.svg"))

            stop_action = menu.addAction("Остановить")
            stop_action.setIcon(QIcon("assets/icons/stop.svg"))

            restart_action = menu.addAction("Перезапустить")
            restart_action.setIcon(QIcon("assets/icons/restart.svg"))

        action = menu.exec(self.mapToGlobal(pos))

        if not action:
            return

        if item.parent() is None:
            # Действия для бота
            if action == delete_action:
                self.remove_selected_bot()
            elif action == settings_action:
                self.selected_item = item
                self.parent().show_settings_dialog()
            elif action == start_action:
                bot_name = item.text(1)
                print(f"Запуск бота {bot_name}...")
            elif action == duplicate_action:
                bot_name = item.text(1)
                print(f"Дублирование бота {bot_name}...")
        else:
            # Действия для эмулятора
            emu_id = item.data(0, Qt.ItemDataRole.UserRole)
            if action == console_action:
                print(f"Открытие консоли для эмулятора {emu_id}...")
            elif action == stop_action:
                print(f"Остановка эмулятора {emu_id}...")
            elif action == restart_action:
                print(f"Перезапуск эмулятора {emu_id}...")

    def remove_selected_bot(self):
        """
        Удаляем выбранного бота.
        """
        item = self.selected_item
        if not item:
            item = self.currentItem()

        if not item or item.parent() is not None:
            QMessageBox.warning(self, "Внимание", "Выберите бота (top-level) для удаления.")
            return
        bot_name = item.text(1)
        reply = QMessageBox.question(
            self, "Подтверждение", f"Удалить бота '{bot_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            idx = self.indexOfTopLevelItem(item)
            if idx >= 0:
                self.takeTopLevelItem(idx)
                self._renumber_items()
                print(f"Бот {bot_name} удалён из очереди.")

    def on_item_double_clicked(self, item):
        """
        Обрабатывает двойной клик по элементу.
        Для эмуляторов открывает консоль.
        """
        if item.parent() is not None:
            # Это эмулятор (child item)
            emu_id = item.data(0, Qt.ItemDataRole.UserRole)
            if emu_id:
                print(f"Открытие консоли для эмулятора {emu_id}...")


# ------------------ ДИАЛОГ НАСТРОЙКИ ПАРАМЕТРОВ БОТА ------------------ #
class BotSettingsDialog(QDialog):
    """
    Диалог для настройки параметров запуска бота.
    Позволяет настроить отложенный старт, циклы, время работы,
    количество потоков и список эмуляторов.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка параметров бота")
        self.setModal(True)
        self.resize(400, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: #2C2C2C;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                color: #FFA500;
                font-weight: bold;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Создаем форму для полей ввода
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        # Отложенный старт (дата и время)
        self.scheduled_time = QDateTimeEdit()
        self.scheduled_time.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.scheduled_time.setDateTime(QDateTime.currentDateTime())
        self.scheduled_time.setCalendarPopup(True)
        self.scheduled_time.setStyleSheet("""
            QDateTimeEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Запланирован на:", self.scheduled_time)

        # Количество циклов
        self.cycles_input = QSpinBox()
        self.cycles_input.setRange(0, 9999)
        self.cycles_input.setValue(0)
        self.cycles_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.cycles_input.setToolTip("0 - бесконечное выполнение")
        self.cycles_input.setStyleSheet("""
            QSpinBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Количество циклов:", self.cycles_input)

        # Время работы
        self.work_time_input = QSpinBox()
        self.work_time_input.setRange(0, 1440)
        self.work_time_input.setValue(0)
        self.work_time_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.work_time_input.setToolTip("Время работы в минутах (0 - без ограничения)")
        self.work_time_input.setStyleSheet("""
            QSpinBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Время работы (мин):", self.work_time_input)

        # Количество потоков
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 50)
        self.threads_input.setValue(1)
        self.threads_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.threads_input.setToolTip("Количество одновременно запущенных эмуляторов")
        self.threads_input.setStyleSheet("""
            QSpinBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Количество потоков:", self.threads_input)

        # Список эмуляторов
        self.emulators_input = QLineEdit()
        self.emulators_input.setText("")
        self.emulators_input.setPlaceholderText("Например: 0:5,7,9:10")
        self.emulators_input.setToolTip("Формат: 0:5,7,9:10")
        self.emulators_input.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Список эмуляторов:", self.emulators_input)

        layout.addLayout(form_layout)

        # Добавляем разделительную линию
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #555;")
        layout.addWidget(separator)

        # Кнопки OK и Cancel
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok = QPushButton("ОК")

        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 3px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 3px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_ok)

        layout.addLayout(buttons_layout)

    def get_data(self):
        """Возвращает данные, введенные пользователем"""
        return {
            "scheduled_time": self.scheduled_time.dateTime().toString("dd.MM.yyyy HH:mm"),
            "cycles": self.cycles_input.value(),
            "work_time": self.work_time_input.value(),
            "threads": self.threads_input.value(),
            "emulators": self.emulators_input.text()
        }

    def set_data(self, data):
        """
        Устанавливает данные в поля диалога.

        :param data: Словарь с данными
        """
        # Устанавливаем дату и время, если они есть
        if "scheduled_time" in data and data["scheduled_time"]:
            try:
                dt = QDateTime.fromString(data["scheduled_time"], "dd.MM.yyyy HH:mm")
                if dt.isValid():
                    self.scheduled_time.setDateTime(dt)
            except Exception as e:
                print(f"Ошибка при установке даты и времени: {e}")

        # Устанавливаем остальные значения
        if "cycles" in data:
            try:
                self.cycles_input.setValue(data["cycles"])
            except Exception as e:
                print(f"Ошибка при установке циклов: {e}")

        if "work_time" in data:
            try:
                self.work_time_input.setValue(data["work_time"])
            except Exception as e:
                print(f"Ошибка при установке времени работы: {e}")

        if "threads" in data:
            try:
                self.threads_input.setValue(data["threads"])
            except Exception as e:
                print(f"Ошибка при установке количества потоков: {e}")

        if "emulators" in data:
            self.emulators_input.setText(data["emulators"])


class MainWindow(QMainWindow):
    """
    Главное окно приложения:
    - Использует боковую панель SideBar
    - Использует PageContainer для анимированного перехода между страницами
    - Страницы: Менеджер ботов, Создать бота, Настройки
    """

    def __init__(self, logger=None, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("BOT Maker")
        self.setGeometry(100, 100, 1200, 800)

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
        # 1. Страница менеджера ботов
        self.manager_page = QWidget()
        self.manager_page.setStyleSheet("background-color: #000000;")
        manager_layout = QHBoxLayout(self.manager_page)
        manager_layout.setContentsMargins(20, 20, 20, 20)
        manager_layout.setSpacing(15)

        # Создаем разделитель для возможности изменения размеров областей
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Добавляем менеджер и список ботов на разделитель
        self.manager_frame = self._create_manager_frame()
        self.bots_frame = self._create_bots_frame()
        splitter.addWidget(self.manager_frame)
        splitter.addWidget(self.bots_frame)

        # Устанавливаем начальные размеры
        splitter.setSizes([800, 350])

        # Добавляем разделитель на страницу
        manager_layout.addWidget(splitter)

        # 2. Страница создания бота (используем заглушку)
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

        # Инициализируем данные (список ботов)
        self.load_bots()

    def _handle_page_change(self, page_name):
        """Обрабатывает сигнал изменения страницы от бокового меню"""
        if page_name == "manager":
            self.page_container.change_page(0)
        elif page_name == "create":
            self.page_container.change_page(1)
        elif page_name == "settings":
            self.page_container.change_page(2)

    def _create_manager_frame(self):
        """
        Создает фрейм с менеджером ботов.
        Оптимизирован для экономии пространства и улучшения UX.
        """
        manager_frame = QFrame()
        manager_frame.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333;")
        manager_layout = QVBoxLayout(manager_frame)
        manager_layout.setContentsMargins(15, 15, 15, 15)
        manager_layout.setSpacing(10)

        # Заголовок с кнопками управления
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Заголовок
        manager_title = create_title_label("Менеджер ботов", 18)
        header_layout.addWidget(manager_title)

        header_layout.addStretch(1)  # Растягиваем пространство между заголовком и кнопками

        # Кнопки управления с улучшенной видимостью
        self.btn_settings = QPushButton("Настройки")
        self.btn_settings.setIcon(QIcon("assets/icons/settings.svg"))
        self.btn_settings.setToolTip("Настройки параметров")
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: black;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        self.btn_settings.clicked.connect(lambda: self.show_settings_dialog())

        self.btn_start_queue = QPushButton("Запустить")
        self.btn_start_queue.setIcon(QIcon("assets/icons/play-all.svg"))
        self.btn_start_queue.setToolTip("Запустить очередь")
        self.btn_start_queue.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        self.btn_start_queue.clicked.connect(lambda: self.start_queue())

        self.btn_clear_queue = QPushButton("Очистить")
        self.btn_clear_queue.setIcon(QIcon("assets/icons/clear-all.svg"))
        self.btn_clear_queue.setToolTip("Очистить очередь")
        self.btn_clear_queue.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF5350;
            }
        """)
        self.btn_clear_queue.clicked.connect(lambda: self.clear_queue())

        header_layout.addWidget(self.btn_settings)
        header_layout.addWidget(self.btn_start_queue)
        header_layout.addWidget(self.btn_clear_queue)

        manager_layout.addLayout(header_layout)

        # Добавляем разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #333;")
        manager_layout.addWidget(separator)

        # Очередь ботов (занимает основную часть пространства)
        queue_section = QVBoxLayout()
        queue_section.setSpacing(5)

        queue_label = create_text_label("Очередь ботов:", "color: #FFA500; font-weight: bold;")
        queue_section.addWidget(queue_label)

        # Улучшенная очередь ботов
        self.queue_tree = ManagerQueueWidget()
        queue_section.addWidget(self.queue_tree, 1)  # Растягиваем по вертикали

        manager_layout.addLayout(queue_section, 1)  # Растягиваем по вертикали

        return manager_frame

    def _create_bots_frame(self):
        """Создает фрейм со списком ботов"""
        bots_frame = QFrame()
        bots_frame.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333;")
        bots_layout = QVBoxLayout(bots_frame)
        bots_layout.setContentsMargins(15, 15, 15, 15)
        bots_layout.setSpacing(10)

        bots_title = create_title_label("Список ботов", 16)
        bots_layout.addWidget(bots_title)

        self.bot_list = QTreeWidget()
        # Два столбца: Название бота, Игра
        self.bot_list.setColumnCount(2)
        self.bot_list.setHeaderLabels(["Название бота", "Игра"])
        self.bot_list.setStyleSheet("""
            background-color: #2C2C2C; 
            color: #FFFFFF; 
            border: 1px solid #444;
        """)

        # Настройка отображения столбцов
        self.bot_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.bot_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        bots_layout.addWidget(self.bot_list, 1)  # Растягиваем по вертикали

        # Кнопки управления ботами (в горизонтальном ряду)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        # Создаем компактные кнопки с иконками
        self.btn_edit_bot = create_tool_button("", "Редактировать бота",
                                               self.edit_selected_bot,
                                               "assets/icons/edit.svg")
        self.btn_add_to_manager = create_tool_button("", "Добавить в менеджер",
                                                     self.add_selected_bot_to_manager,
                                                     "assets/icons/add-to-queue.svg")
        self.btn_delete_bot = create_tool_button("", "Удалить бота",
                                                 self.delete_selected_bot,
                                                 "assets/icons/delete.svg")
        self.btn_export_bot = create_tool_button("", "Экспорт бота",
                                                 self.export_selected_bot,
                                                 "assets/icons/export.svg")
        self.btn_import_bot = create_tool_button("", "Импорт бота",
                                                 self.import_bot,
                                                 "assets/icons/import.svg")

        buttons_layout.addWidget(self.btn_edit_bot)
        buttons_layout.addWidget(self.btn_add_to_manager)
        buttons_layout.addWidget(self.btn_delete_bot)
        buttons_layout.addWidget(self.btn_export_bot)
        buttons_layout.addWidget(self.btn_import_bot)
        buttons_layout.addStretch(1)  # Добавляем гибкий элемент для выравнивания

        bots_layout.addLayout(buttons_layout)

        # Добавляем текстовые подписи под кнопками
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(5)

        edit_label = QLabel("Изменить")
        add_label = QLabel("Добавить")
        delete_label = QLabel("Удалить")
        export_label = QLabel("Экспорт")
        import_label = QLabel("Импорт")

        # Стиль для подписей
        label_style = "color: white; font-size: 10px; qproperty-alignment: AlignCenter;"
        edit_label.setStyleSheet(label_style)
        add_label.setStyleSheet(label_style)
        delete_label.setStyleSheet(label_style)
        export_label.setStyleSheet(label_style)
        import_label.setStyleSheet(label_style)

        # Устанавливаем фиксированную ширину, соответствующую ширине кнопок
        edit_label.setFixedWidth(self.btn_edit_bot.width())
        add_label.setFixedWidth(self.btn_add_to_manager.width())
        delete_label.setFixedWidth(self.btn_delete_bot.width())
        export_label.setFixedWidth(self.btn_export_bot.width())
        import_label.setFixedWidth(self.btn_import_bot.width())

        labels_layout.addWidget(edit_label)
        labels_layout.addWidget(add_label)
        labels_layout.addWidget(delete_label)
        labels_layout.addWidget(export_label)
        labels_layout.addWidget(import_label)
        labels_layout.addStretch(1)  # Добавляем гибкий элемент для выравнивания

        bots_layout.addLayout(labels_layout)

        return bots_frame

    # ---------------- Методы загрузки/управления списком ботов ----------------
    def load_bots(self) -> None:
        self.bot_list.clear()
        bots_data = [
            ("Bot_1", "Game_1"),
            ("Bot_2", "Game_2"),
            ("Bot_3", "Game_3")
        ]
        for bot_name, game_name in bots_data:
            item = QTreeWidgetItem([bot_name, game_name])
            self.bot_list.addTopLevelItem(item)

    def edit_selected_bot(self):
        """
        Редактирует выбранного бота.
        Открывает выбранного бота в редакторе.
        """
        item = self.bot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите бота для редактирования.")
            return

        bot_name = item.text(0)
        bot_path = os.path.join("bots", bot_name)

        # Проверяем существование папки бота
        if not os.path.exists(bot_path):
            QMessageBox.warning(self, "Ошибка", f"Папка бота '{bot_name}' не найдена.")
            return

        # Переключаемся на страницу создания/редактирования бота
        self.page_container.change_page(1)
        self.sidebar.set_active_page("create")

        # Загружаем бота в редактор
        if hasattr(self.create_page, 'load_bot'):
            success = self.create_page.load_bot(bot_path)
            if success:
                print(f"Бот {bot_name} загружен для редактирования")
            else:
                print(f"Не удалось загрузить бота {bot_name}")
        else:
            print("Метод load_bot не найден в create_page")

    def add_selected_bot_to_manager(self):
        """
        Добавляет выбранного бота (из списка справа) в очередь.
        """
        item = self.bot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите бота для добавления в менеджер.")
            return
        bot_name = item.text(0)
        game_name = item.text(1)

        # Создаём итем с 8 столбцами
        index = self.queue_tree.topLevelItemCount() + 1

        # Текущее время + 1 час для отложенного старта по умолчанию
        next_hour = QDateTime.currentDateTime().addSecs(3600)
        scheduled_time = next_hour.toString("dd.MM.yyyy HH:mm")

        # [0=№, 1=Бот, 2=Игра, 3=Потоки, 4=Запланирован, 5=Циклы, 6=Время раб.]
        queue_item = QTreeWidgetItem([
            str(index), bot_name, game_name, "1",  # первые 4
            scheduled_time, "0", "0"  # ещё 3
        ])

        # Устанавливаем белый цвет и увеличенный шрифт
        font = QFont("Segoe UI", 11)
        for col in range(self.queue_tree.columnCount()):
            queue_item.setFont(col, font)
            queue_item.setForeground(col, QBrush(QColor("white")))

        self.queue_tree.addTopLevelItem(queue_item)
        print(f"Бот {bot_name} добавлен в очередь.")

        # Добавляем контекстное меню вместо кнопок
        queue_item.setFlags(queue_item.flags() | Qt.ItemFlag.ItemIsEditable)
        queue_item.setToolTip(0, "Нажмите правой кнопкой для управления ботом")

    def delete_selected_bot(self):
        item = self.bot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите бота для удаления.")
            return
        bot_name = item.text(0)
        reply = QMessageBox.question(
            self, "Подтверждение", f"Удалить бота '{bot_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.bot_list.indexOfTopLevelItem(item)
                self.bot_list.takeTopLevelItem(index)
            print(f"Бот {bot_name} удалён из списка.")

    def export_selected_bot(self):
        item = self.bot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите бота для экспорта.")
            return
        bot_name = item.text(0)
        print(f"Экспорт бота {bot_name} (заглушка).")

    def import_bot(self):
        print("Импорт бота (заглушка).")

    # ---------------- Методы менеджера очереди ----------------
    def start_queue(self):
        """
        Запуск всей очереди (заглушка).
        """
        print("Запуск очереди ботов (заглушка).")
        top_count = self.queue_tree.topLevelItemCount()
        for i in range(top_count):
            top_item = self.queue_tree.topLevelItem(i)
            child_count = top_item.childCount()
            for j in range(child_count):
                child_item = top_item.child(j)
                # Меняем статус
                child_item.setText(2, "on")

    def clear_queue(self):
        """
        Очистка очереди ботов.
        """
        confirm = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить всю очередь?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.queue_tree.clear()
            print("Очередь ботов очищена.")

    def show_settings_dialog(self):
        """
        Показывает диалог настроек параметров для выбранного бота.
        """
        # Получаем выбранный элемент напрямую из очереди
        item = self.queue_tree.currentItem()

        if not item or item.parent() is not None:
            QMessageBox.warning(self, "Внимание", "Выберите бота (top-level) в очереди для настройки параметров.")
            return

        # Создаем диалог настроек
        dialog = BotSettingsDialog(self)

        # Загружаем текущие параметры в диалог
        current_data = {
            "scheduled_time": item.text(4),
            "cycles": int(item.text(5)) if item.text(5).isdigit() else 0,
            "work_time": int(item.text(6)) if item.text(6).isdigit() else 0,
            "threads": item.text(3) if item.text(3).isdigit() else "1",
            "emulators": ""  # Это нужно будет извлечь из дочерних элементов
        }

        # Получаем список эмуляторов из дочерних элементов
        emu_ids = []
        for i in range(item.childCount()):
            child = item.child(i)
            if child.text(1).startswith("Эмулятор "):
                try:
                    emu_id = int(child.text(1).replace("Эмулятор ", ""))
                    emu_ids.append(emu_id)
                except ValueError:
                    pass

        # Формируем строку эмуляторов
        if emu_ids:
            # Сортируем ID эмуляторов
            emu_ids.sort()

            # Группируем последовательные ID
            ranges = []
            start = emu_ids[0]
            end = emu_ids[0]

            for i in range(1, len(emu_ids)):
                if emu_ids[i] == end + 1:
                    end = emu_ids[i]
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}:{end}")
                    start = end = emu_ids[i]

            # Добавляем последний диапазон
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}:{end}")

            current_data["emulators"] = ",".join(ranges)

        # Обработка данных для корректной передачи в диалог
        current_data["threads"] = int(current_data["threads"]) if current_data["threads"].isdigit() else 1
        current_data["cycles"] = int(current_data["cycles"]) if current_data["cycles"].isdigit() else 0
        current_data["work_time"] = int(current_data["work_time"]) if current_data["work_time"].isdigit() else 0

        dialog.set_data(current_data)

        # Если пользователь подтвердил изменения
        if dialog.exec():
            new_data = dialog.get_data()

            # Обновляем основные параметры в дереве
            item.setText(3, str(new_data["threads"]))
            item.setText(4, new_data["scheduled_time"])
            item.setText(5, str(new_data["cycles"]))
            item.setText(6, str(new_data["work_time"]))

            # Обновляем список эмуляторов (сначала удаляем старые)
            while item.childCount() > 0:
                item.removeChild(item.child(0))

            # Парсим новый список эмуляторов
            emu_list = self._parse_emulators_string(new_data["emulators"])

            # Создаём child-элементы (эмуляторы)
            font = QFont("Segoe UI", 11)
            for emu_id in emu_list:
                # [0="", 1="Эмулятор X", 2="off", 3="", 4="", 5="", 6=""]
                child = QTreeWidgetItem(["", f"Эмулятор {emu_id}", "off", "", "", "", ""])
                for col in range(self.queue_tree.columnCount()):
                    child.setFont(col, font)
                    child.setForeground(col, QBrush(QColor("white")))

                # Добавляем иконку для эмулятора
                child.setIcon(1, QIcon("assets/icons/emulator.svg"))

                item.addChild(child)

                # Добавляем обработчик двойного клика для открытия консоли
                child.setToolTip(1, "Двойной клик для открытия консоли, правый клик для меню управления")
                # Добавляем данные для идентификации эмулятора при контекстном меню
                child.setData(0, Qt.ItemDataRole.UserRole, emu_id)

            # Раскрываем узел для показа дочерних элементов
            item.setExpanded(True)

            print(f"Параметры применены к боту №{item.text(0)} ({item.text(1)}): "
                  f"scheduled={new_data['scheduled_time']}, cycles={new_data['cycles']}, "
                  f"work_time={new_data['work_time']}, threads={new_data['threads']}, "
                  f"emulators={emu_list}")

    def _parse_emulators_string(self, emulators_str: str) -> list:
        """
        Парсит строку с указанием эмуляторов и возвращает список их ID.

        :param emulators_str: Строка вида "0:5,7,9:10"
        :return: Список ID эмуляторов
        """
        emu_list = []
        try:
            if not emulators_str.strip():
                return []

            raw_parts = emulators_str.strip().split(",")
            for part in raw_parts:
                if ":" in part:
                    start, end = part.split(":")
                    try:
                        start_i = int(start)
                        end_i = int(end)
                        if start_i <= end_i:
                            for e in range(start_i, end_i + 1):
                                emu_list.append(e)
                    except:
                        pass
                else:
                    try:
                        emu_list.append(int(part))
                    except:
                        pass
        except Exception as e:
            print(f"Ошибка при парсинге строки эмуляторов: {e}")

        return emu_list

    def on_bot_created(self, bot_name, game_name):
        """
        Обрабатывает сигнал о создании бота.
        Добавляет нового бота в список ботов.
        """
        # Добавляем бота в список ботов
        item = QTreeWidgetItem([bot_name, game_name])
        self.bot_list.addTopLevelItem(item)

        # Переключаемся на страницу менеджера
        self.page_container.change_page(0)
        self.sidebar.set_active_page("manager")

        # Выделяем нового бота в списке
        for i in range(self.bot_list.topLevelItemCount()):
            if self.bot_list.topLevelItem(i).text(0) == bot_name:
                self.bot_list.setCurrentItem(self.bot_list.topLevelItem(i))
                break

        # Показываем сообщение об успешном создании бота
        QMessageBox.information(self, "Успех", f"Бот '{bot_name}' успешно создан и добавлен в список!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
    """)

    # Добавляем стиль для компактных кнопок в QToolButton
    if "COMPACT_BUTTON_STYLE" not in globals():
        app.setStyleSheet(app.styleSheet() + """
            QToolButton {
                background-color: #FFA500;
                border-radius: 4px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: #FFB347;
            }
        """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())