# src/gui/main_window.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QSpinBox, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QIcon, QBrush, QColor, QKeyEvent
from src.gui.sidebar import SideBar
from src.gui.page_container import PageContainer
from src.gui.settings_page import SettingsPage
from src.gui.editor import BotEditor
import logging


# ------------------ КАСТОМНЫЙ QWIDGET ДЛЯ БОТА (КНОПКА START) ------------------ #
class BotWidget(QWidget):
    """
    Небольшой виджет с кнопкой "Start" для бота.
    """

    def __init__(self, bot_id: str, parent=None):
        super().__init__(parent)
        self.bot_id = bot_id  # можно использовать для логики
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        self.btn_start.clicked.connect(self.on_start)
        layout.addWidget(self.btn_start)

    def on_start(self):
        """
        Логика запуска бота (заглушка).
        """
        print(f"Запуск бота {self.bot_id}...")


# ------------------ КАСТОМНЫЙ QWIDGET ДЛЯ ЭМУЛЯТОРА (КНОПКИ CONSOLE + STOP) ------------------ #
class EmulatorWidget(QWidget):
    """
    Небольшой виджет с кнопками "Console" и "Stop" для эмулятора.
    """

    def __init__(self, emulator_id: int, parent=None):
        super().__init__(parent)
        self.emulator_id = emulator_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.btn_console = QPushButton("Console")
        self.btn_console.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        self.btn_console.clicked.connect(self.on_console)
        layout.addWidget(self.btn_console)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: #FFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        self.btn_stop.clicked.connect(self.on_stop)
        layout.addWidget(self.btn_stop)

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


# ------------------ КАСТОМНЫЙ QTreeWidget ДЛЯ ОЧЕРЕДИ ------------------ #
class ManagerQueueWidget(QTreeWidget):
    """
    QTreeWidget для очереди ботов:
    - 8 столбцов: №, Бот, Игра, Потоки, Отл. старт, Циклы, Время раб., (Кнопки)
    - Запрещаем вложение одного бота в другого (flatten после dropEvent).
    - Удаляем бота по клавише Delete и контекстному меню.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(8)
        self.setHeaderLabels([
            "№", "Бот", "Игра", "Потоки",
            "Отл. старт", "Циклы", "Время раб.", ""
        ])

        # Стилизуем заголовки
        self.header().setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;
                color: #FFA500;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        # Разрешаем Drag & Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        # Разрешаем выбор single
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

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
        Контекстное меню по правому клику.
        """
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить бота")
        action = menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            self.remove_selected_bot()

    def remove_selected_bot(self):
        """
        Удаляем выбранного бота.
        """
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


class CreateBotWindow(QMainWindow):
    """
    Окно для создания или редактирования бота (без изменений).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create or Edit Bot")
        self.setGeometry(300, 300, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        label = QLabel("Здесь будет логика создания/редактирования бота.")
        label.setStyleSheet("color: white;")
        layout.addWidget(label)

        self.setStyleSheet("background-color: #2C2C2C;")


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

        # Добавляем менеджер и список ботов на страницу менеджера
        self.manager_frame = self._create_manager_frame()
        self.bots_frame = self._create_bots_frame()
        manager_layout.addWidget(self.manager_frame, stretch=3)
        manager_layout.addWidget(self.bots_frame, stretch=1)

        # 2. Страница создания бота (используем заглушку)
        self.create_page = QWidget()
        self.create_page.setStyleSheet("background-color: #000000;")
        create_layout = QVBoxLayout(self.create_page)
        create_label = QLabel("Редактор ботов")
        create_label.setStyleSheet("color: #FFA500; font-size: 18pt;")
        create_layout.addWidget(create_label)

        # В будущем здесь будет полноценный редактор ботов
        # self.create_page = BotEditor(self.logger)

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
            self.page_container.slide_to_index(0)
        elif page_name == "create":
            self.page_container.slide_to_index(1)
        elif page_name == "settings":
            self.page_container.slide_to_index(2)

    def _create_manager_frame(self):
        """Создает фрейм с менеджером ботов"""
        manager_frame = QFrame()
        manager_frame.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333;")
        manager_layout = QVBoxLayout(manager_frame)
        manager_layout.setContentsMargins(15, 15, 15, 15)
        manager_layout.setSpacing(10)

        manager_title = QLabel("Менеджер ботов")
        manager_title.setStyleSheet("color: #FFA500;")  # оранжевый текст
        manager_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        manager_layout.addWidget(manager_title)

        # Поля для настройки
        self.delay_start_label = QLabel("Отложенный старт (мин):")
        self.delay_start_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.delay_start_label)

        self.delay_start_input = QLineEdit()
        self.delay_start_input.setPlaceholderText("Например, 10")
        self.delay_start_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C;")
        manager_layout.addWidget(self.delay_start_input)

        self.cycles_label = QLabel("Количество циклов (0 - бесконечно):")
        self.cycles_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.cycles_label)

        self.cycles_input = QSpinBox()
        self.cycles_input.setRange(0, 9999)
        self.cycles_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C;")
        manager_layout.addWidget(self.cycles_input)

        self.work_time_label = QLabel("Время работы (минуты, 0 - отключено):")
        self.work_time_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.work_time_label)

        self.work_time_input = QSpinBox()
        self.work_time_input.setRange(0, 1440)
        self.work_time_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C;")
        manager_layout.addWidget(self.work_time_input)

        self.threads_label = QLabel("Количество потоков (эмуляторов одновременно):")
        self.threads_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.threads_label)

        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 50)
        self.threads_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C;")
        manager_layout.addWidget(self.threads_input)

        self.emulators_label = QLabel("Список эмуляторов (пример: 0:5,7,9:10):")
        self.emulators_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.emulators_label)

        self.emulators_input = QLineEdit()
        self.emulators_input.setPlaceholderText("0:5,7,9:10")
        self.emulators_input.setStyleSheet("color: #FFFFFF; background-color: #2C2C2C;")
        manager_layout.addWidget(self.emulators_input)

        # Кнопка "Применить параметры"
        self.btn_apply_params = QPushButton("Применить параметры")
        self.btn_apply_params.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 5px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        manager_layout.addWidget(self.btn_apply_params)

        # Кнопка "Запустить очередь"
        self.btn_start_queue = QPushButton("Запустить очередь")
        self.btn_start_queue.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 5px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        manager_layout.addWidget(self.btn_start_queue)

        # Кнопка "Очистить очередь"
        self.btn_clear_queue = QPushButton("Очистить очередь")
        self.btn_clear_queue.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: #000;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FFB347;
            }
        """)
        manager_layout.addWidget(self.btn_clear_queue)

        # Заголовок для очереди
        self.queue_label = QLabel("Очередь ботов:")
        self.queue_label.setStyleSheet("color: white;")
        manager_layout.addWidget(self.queue_label)

        # Используем наш кастомный QTreeWidget (8 столбцов)
        self.queue_tree = ManagerQueueWidget()
        manager_layout.addWidget(self.queue_tree)

        # Подключаем сигналы
        self.btn_apply_params.clicked.connect(self.apply_params_to_selected)
        self.btn_start_queue.clicked.connect(self.start_queue)
        self.btn_clear_queue.clicked.connect(self.clear_queue)

        return manager_frame

    def _create_bots_frame(self):
        """Создает фрейм со списком ботов"""
        bots_frame = QFrame()
        bots_frame.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333;")
        bots_layout = QVBoxLayout(bots_frame)
        bots_layout.setContentsMargins(15, 15, 15, 15)
        bots_layout.setSpacing(10)

        bots_title = QLabel("Список ботов")
        bots_title.setStyleSheet("color: #FFA500;")
        bots_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        bots_layout.addWidget(bots_title)

        self.bot_list = QTreeWidget()
        # Два столбца: Название бота, Игра
        self.bot_list.setColumnCount(2)
        self.bot_list.setHeaderLabels(["Название бота", "Игра"])
        self.bot_list.setStyleSheet("background-color: #2C2C2C; color: #FFFFFF; border: 1px solid #444;")
        bots_layout.addWidget(self.bot_list)

        # Кнопки
        self.btn_edit_bot = QPushButton("Редактировать бота")
        self.btn_add_to_manager = QPushButton("Добавить в менеджер")
        self.btn_delete_bot = QPushButton("Удалить бота")
        self.btn_export_bot = QPushButton("Экспорт бота")
        self.btn_import_bot = QPushButton("Импорт бота")

        self.btn_edit_bot.setIcon(QIcon("assets/icons/edit.svg"))
        self.btn_add_to_manager.setIcon(QIcon("assets/icons/manager.svg"))
        self.btn_delete_bot.setIcon(QIcon("assets/icons/delete.svg"))
        self.btn_export_bot.setIcon(QIcon("assets/icons/export.svg"))
        self.btn_import_bot.setIcon(QIcon("assets/icons/import.svg"))

        for btn in [self.btn_edit_bot, self.btn_add_to_manager, self.btn_delete_bot,
                    self.btn_export_bot, self.btn_import_bot]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500;
                    color: #000;
                    border-radius: 5px;
                    margin-bottom: 5px;
                }
                QPushButton:hover {
                    background-color: #FFB347;
                }
            """)
            bots_layout.addWidget(btn)

        # Подключаем сигналы
        self.btn_edit_bot.clicked.connect(self.edit_selected_bot)
        self.btn_add_to_manager.clicked.connect(self.add_selected_bot_to_manager)
        self.btn_delete_bot.clicked.connect(self.delete_selected_bot)
        self.btn_export_bot.clicked.connect(self.export_selected_bot)
        self.btn_import_bot.clicked.connect(self.import_bot)

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
        item = self.bot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите бота для редактирования.")
            return
        bot_name = item.text(0)
        print(f"Редактируем бота: {bot_name}")
        self.edit_window = CreateBotWindow(self)
        self.edit_window.setWindowTitle(f"Редактирование бота: {bot_name}")
        self.edit_window.show()

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
        # [0=№, 1=Бот, 2=Игра, 3=Потоки, 4=Отл. старт, 5=Циклы, 6=Время раб., 7=кнопки]
        queue_item = QTreeWidgetItem([
            str(index), bot_name, game_name, "",  # первые 4
            "", "", "", ""  # ещё 4
        ])

        # Устанавливаем белый цвет и увеличенный шрифт
        font = QFont("Segoe UI", 12)
        for col in range(self.queue_tree.columnCount()):
            queue_item.setFont(col, font)
            queue_item.setForeground(col, QBrush(QColor("white")))

        self.queue_tree.addTopLevelItem(queue_item)
        print(f"Бот {bot_name} добавлен в очередь.")

        # Добавляем кнопку "Start" в последний столбец (7)
        widget = BotWidget(bot_name, parent=self.queue_tree)
        self.queue_tree.setItemWidget(queue_item, 7, widget)

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
        self.queue_tree.clear()
        print("Очередь ботов очищена.")

    def apply_params_to_selected(self):
        """
        Применяет параметры к выбранному боту (top-level).
        Заполняет столбцы "Отл. старт" (4), "Циклы" (5), "Время раб." (6),
        и создаёт эмуляторы (child) с кнопками "Console" и "Stop" в столбце (7).
        """
        item = self.queue_tree.currentItem()
        if not item or item.parent() is not None:
            QMessageBox.warning(self, "Внимание", "Выберите бота (top-level) в очереди, чтобы применить параметры.")
            return

        delay_start = self.delay_start_input.text().strip() or ""
        cycles = str(self.cycles_input.value())
        work_time = str(self.work_time_input.value())
        threads = str(self.threads_input.value())
        emulators = self.emulators_input.text().strip()

        # Заполняем нужные столбцы
        # [0=№, 1=Бот, 2=Игра, 3=Потоки, 4=Отл. старт, 5=Циклы, 6=Время раб., 7=кнопка]
        item.setText(3, threads)
        item.setText(4, delay_start)
        item.setText(5, cycles)
        item.setText(6, work_time)

        # Удаляем старые child (эмуляторы)
        while item.childCount() > 0:
            item.removeChild(item.child(0))

        # Парсим список эмуляторов
        emu_list = []
        raw_parts = emulators.split(",")
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

        # Создаём child-элементы (эмуляторы)
        font = QFont("Segoe UI", 12)
        for emu_id in emu_list:
            # [0="", 1="Эмулятор X", 2="off", 3="", 4="", 5="", 6="", 7="кнопки"]
            child = QTreeWidgetItem(["", f"Эмулятор {emu_id}", "off", "", "", "", "", ""])
            for col in range(self.queue_tree.columnCount()):
                child.setFont(col, font)
                child.setForeground(col, QBrush(QColor("white")))

            item.addChild(child)

            # Добавляем виджет с кнопками "Console" и "Stop" в столбец 7
            widget = EmulatorWidget(emulator_id=emu_id, parent=self.queue_tree)
            self.queue_tree.setItemWidget(child, 7, widget)
        print(f"Параметры применены к боту №{item.text(0)} ({item.text(1)}): "
              f"delay={delay_start}, cycles={cycles}, work_time={work_time}, threads={threads}, emulators={emu_list}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Дополнительная стилизация (общий hover-эффект для кнопок)
    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
        QPushButton:hover {
            background-color: #FFB347;
        }
        QTreeWidget::item:selected {
            background-color: #333333;
            color: #FFFFFF;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())