# src/gui/widgets/manager_queue_widget.py
"""
Модуль содержит улучшенный класс ManagerQueueWidget - виджет для очереди ботов.
Решает проблемы с перетаскиванием, стилизацией и улучшает пользовательский опыт.
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QAbstractItemView,
    QHeaderView, QPushButton, QHBoxLayout, QWidget, QVBoxLayout,
    QToolButton, QLabel
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QKeyEvent

from src.utils.resources import Resources


class ManagerQueueWidget(QTreeWidget):
    """
    Улучшенный QTreeWidget для очереди ботов с улучшенной видимостью элементов.
    """
    # Сигналы для оповещения родительского виджета
    botStartRequested = pyqtSignal(str)  # Имя бота для запуска
    botStopRequested = pyqtSignal(str)  # Имя бота для остановки
    botDuplicateRequested = pyqtSignal(str)  # Имя бота для дублирования
    botMoveUpRequested = pyqtSignal(int)  # Индекс бота для перемещения вверх
    botMoveDownRequested = pyqtSignal(int)  # Индекс бота для перемещения вниз
    emulatorConsoleRequested = pyqtSignal(int)  # ID эмулятора для консоли
    emulatorStopRequested = pyqtSignal(int)  # ID эмулятора для остановки
    emulatorRestartRequested = pyqtSignal(int)  # ID эмулятора для перезапуска
    emulatorMoveUpRequested = pyqtSignal(int, int)  # ID родительского бота и эмулятора для перемещения вверх
    emulatorMoveDownRequested = pyqtSignal(int, int)  # ID родительского бота и эмулятора для перемещения вниз

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

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

        # Отключаем drag & drop для решения проблем с перетаскиванием
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDragDropMode(QTreeWidget.DragDropMode.NoDragDrop)

        # Разрешаем выбор single
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Улучшаем видимость строк и элементов
        self.setIndentation(20)  # Увеличиваем отступ для дочерних элементов для лучшей видимости

        # Обновлённый стиль для виджета очереди
        self.setStyleSheet("""
            QTreeView {
                background-color: #2D2D30;  /* Более светлый фон, как в редакторе */
                color: white;
                alternate-row-colors: true;
                gridline-color: #444;
                border: none;
            }
            QTreeView::item {
                padding: 6px 0;
                border-bottom: 1px solid #3E3E42;
            }
            /* Стиль для родительских элементов (ботов) */
            QTreeView::item:has-children {
                background-color: #3A3A3D;  /* Немного светлее для ботов */
                font-weight: bold;
                border-bottom: 1px solid #505054;
            }
            /* Стиль для дочерних элементов (эмуляторов) */
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(assets/icons/expand-white.svg);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(assets/icons/collapse-white.svg);
            }
            QTreeView::item:selected {
                background-color: #3A6EA5;
                color: white;
            }
            QTreeView::item:hover {
                background-color: #2C5175;
            }
            /* Исправление стилей подсказок и контекстного меню */
            QToolTip {
                background-color: #2D2D30;
                color: white;
                border: 1px solid #3E3E42;
                padding: 2px;
            }
            QMenu {
                background-color: #2D2D30;
                color: white;
                border: 1px solid #3E3E42;
            }
            QMenu::item {
                padding: 5px 18px 5px 30px;
            }
            QMenu::item:selected {
                background-color: #3A6EA5;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3E3E42;
                margin: 4px 0px;
            }
            /* Стиль для календаря и связанных элементов */
            QCalendarWidget {
                background-color: #2D2D30;
                color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #3A3A3D;
                border: 1px solid #505054;
                border-radius: 3px;
            }
            QCalendarWidget QMenu {
                color: white;
                background-color: #2D2D30;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #3A3A3D;
                selection-background-color: #3A6EA5;
                selection-color: white;
            }
            QCalendarWidget QTableView {
                alternate-background-color: #3E3E42;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                background-color: #2D2D30;
                selection-background-color: #3A6EA5;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #777777;
            }
        """)

        # Включаем двойной клик для открытия консоли эмулятора
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Контекстное меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # После создания строк добавляем кнопки навигации
        self.itemChanged.connect(self.on_item_changed)

    def add_bot_to_queue(self, bot_name, game_name, threads=1, scheduled_time=None):
        """
        Добавляет нового бота в очередь.

        Args:
            bot_name: Имя бота
            game_name: Имя игры
            threads: Количество потоков (по умолчанию 1)
            scheduled_time: Запланированное время запуска (по умолчанию текущее время + 1 час)

        Returns:
            QTreeWidgetItem: Созданный элемент бота
        """
        from PyQt6.QtCore import QDateTime

        # Устанавливаем время запуска (по умолчанию текущее время + 1 час)
        if scheduled_time is None:
            next_hour = QDateTime.currentDateTime().addSecs(3600)
            scheduled_time = next_hour.toString("dd.MM.yyyy HH:mm")

        # Создаем элемент с данными бота
        # [0=№, 1=Бот, 2=Игра, 3=Потоки, 4=Запланирован, 5=Циклы, 6=Время раб.]
        index = self.topLevelItemCount() + 1
        queue_item = QTreeWidgetItem([
            str(index), bot_name, game_name, str(threads),
            scheduled_time, "0", "0"
        ])

        # Устанавливаем белый цвет и увеличенный шрифт
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)  # Bold для ботов
        for col in range(self.columnCount()):
            queue_item.setFont(col, font)
            queue_item.setForeground(col, QBrush(QColor("white")))

        # Устанавливаем цвет фона для бота
        for col in range(self.columnCount()):
            queue_item.setBackground(col, QBrush(QColor("#3A3A3D")))

        # Добавляем элемент в дерево
        self.addTopLevelItem(queue_item)

        # Добавляем кнопки навигации для бота
        self.add_navigation_buttons_to_bot(queue_item)

        # Добавляем контекстное меню
        queue_item.setToolTip(0, "Нажмите правой кнопкой для управления ботом")

        return queue_item

    def add_emulator_to_bot(self, parent_item, emu_id):
        """
        Добавляет эмулятор к боту

        Args:
            parent_item: Родительский элемент бота
            emu_id: ID эмулятора

        Returns:
            QTreeWidgetItem: Созданный элемент эмулятора
        """
        if not parent_item:
            return None

        # Создаем элемент эмулятора
        child = QTreeWidgetItem(["", f"Эмулятор {emu_id}", "off", "", "", "", ""])

        # Устанавливаем обычный (не жирный) шрифт для эмуляторов
        font = QFont("Segoe UI", 11)
        for col in range(self.columnCount()):
            child.setFont(col, font)
            child.setForeground(col, QBrush(QColor("white")))

        # Добавляем эмулятор к боту
        parent_item.addChild(child)

        # Добавляем иконку для эмулятора
        child.setIcon(1, QIcon(Resources.get_icon_path("emulator")))

        # Добавляем данные для идентификации эмулятора при контекстном меню
        child.setData(0, Qt.ItemDataRole.UserRole, emu_id)

        # Добавляем кнопки навигации для эмулятора
        self.add_navigation_buttons_to_emulator(child)

        # Добавляем контекстное меню
        child.setToolTip(1, "Двойной клик для открытия консоли, правый клик для меню управления")

        # Раскрываем родительский элемент
        parent_item.setExpanded(True)

        return child

    def add_navigation_buttons_to_bot(self, item):
        """Добавляет кнопки навигации (вверх/вниз) к элементу бота"""
        if not item or item.parent():  # Проверяем, что это бот (не эмулятор)
            return

        # Получаем индекс элемента
        item_idx = self.indexOfTopLevelItem(item)

        # Создаем виджет с кнопками
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(2, 2, 2, 2)
        nav_layout.setSpacing(2)

        # Кнопка "Вверх"
        btn_up = QToolButton()
        btn_up.setIcon(QIcon(Resources.get_icon_path("up")))
        btn_up.setToolTip("Переместить бота вверх")
        btn_up.setFixedSize(20, 20)
        btn_up.setStyleSheet("""
            QToolButton {
                background-color: #3A6EA5;
                border: none;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #4A7EB5;
            }
            QToolButton:disabled {
                background-color: #555555;
            }
        """)

        # Отключаем кнопку "Вверх" для первого элемента
        btn_up.setEnabled(item_idx > 0)

        # Кнопка "Вниз"
        btn_down = QToolButton()
        btn_down.setIcon(QIcon(Resources.get_icon_path("down")))
        btn_down.setToolTip("Переместить бота вниз")
        btn_down.setFixedSize(20, 20)
        btn_down.setStyleSheet("""
            QToolButton {
                background-color: #3A6EA5;
                border: none;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #4A7EB5;
            }
            QToolButton:disabled {
                background-color: #555555;
            }
        """)

        # Отключаем кнопку "Вниз" для последнего элемента
        btn_down.setEnabled(item_idx < self.topLevelItemCount() - 1)

        # Создаем замыкания для обработчиков событий с актуальным индексом
        def create_move_up_callback(idx):
            return lambda: self.move_bot_up(idx)

        def create_move_down_callback(idx):
            return lambda: self.move_bot_down(idx)

        # Подключаем обработчики
        btn_up.clicked.connect(create_move_up_callback(item_idx))
        btn_down.clicked.connect(create_move_down_callback(item_idx))

        # Добавляем кнопки в layout
        nav_layout.addWidget(btn_up)
        nav_layout.addWidget(btn_down)
        nav_layout.addStretch()

        # Устанавливаем виджет в последний столбец
        self.setItemWidget(item, 6, nav_widget)

    def add_navigation_buttons_to_emulator(self, item):
        """Добавляет кнопки навигации (вверх/вниз) к элементу эмулятора"""
        if not item or not item.parent():  # Проверяем, что это эмулятор (есть родитель)
            return

        parent = item.parent()

        # Получаем индекс элемента среди дочерних элементов родителя
        item_idx = parent.indexOfChild(item)

        # Создаем виджет с кнопками
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(2, 2, 2, 2)
        nav_layout.setSpacing(2)

        # Кнопка "Вверх"
        btn_up = QToolButton()
        btn_up.setIcon(QIcon(Resources.get_icon_path("up")))
        btn_up.setToolTip("Переместить эмулятор вверх")
        btn_up.setFixedSize(20, 20)
        btn_up.setStyleSheet("""
            QToolButton {
                background-color: #3A6EA5;
                border: none;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #4A7EB5;
            }
            QToolButton:disabled {
                background-color: #555555;
            }
        """)

        # Отключаем кнопку "Вверх" для первого элемента
        btn_up.setEnabled(item_idx > 0)

        # Кнопка "Вниз"
        btn_down = QToolButton()
        btn_down.setIcon(QIcon(Resources.get_icon_path("down")))
        btn_down.setToolTip("Переместить эмулятор вниз")
        btn_down.setFixedSize(20, 20)
        btn_down.setStyleSheet("""
            QToolButton {
                background-color: #3A6EA5;
                border: none;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #4A7EB5;
            }
            QToolButton:disabled {
                background-color: #555555;
            }
        """)

        # Отключаем кнопку "Вниз" для последнего элемента
        btn_down.setEnabled(item_idx < parent.childCount() - 1)

        # Получаем индекс родительского элемента
        parent_idx = self.indexOfTopLevelItem(parent)

        # Создаем замыкания для обработчиков событий с актуальными индексами
        def create_move_up_callback(parent_idx, idx):
            return lambda: self.move_emulator_up(parent_idx, idx)

        def create_move_down_callback(parent_idx, idx):
            return lambda: self.move_emulator_down(parent_idx, idx)

        # Подключаем обработчики
        btn_up.clicked.connect(create_move_up_callback(parent_idx, item_idx))
        btn_down.clicked.connect(create_move_down_callback(parent_idx, item_idx))

        # Добавляем кнопки в layout
        nav_layout.addWidget(btn_up)
        nav_layout.addWidget(btn_down)
        nav_layout.addStretch()

        # Устанавливаем виджет в последний столбец
        self.setItemWidget(item, 6, nav_widget)

    def move_bot_up(self, bot_idx):
        """Перемещает бота вверх по списку"""
        if bot_idx <= 0 or bot_idx >= self.topLevelItemCount():
            return

        # Получаем элементы, которые нужно поменять местами
        current_item = self.topLevelItem(bot_idx)
        previous_item = self.topLevelItem(bot_idx - 1)

        if not current_item or not previous_item:
            return

        # Удаляем элементы из дерева (но не удаляем сами объекты)
        current_temp = self.takeTopLevelItem(bot_idx)
        previous_temp = self.takeTopLevelItem(bot_idx - 1)

        # Вставляем элементы обратно в дерево в нужном порядке
        self.insertTopLevelItem(bot_idx - 1, current_temp)
        self.insertTopLevelItem(bot_idx, previous_temp)

        # Обновляем нумерацию и кнопки навигации
        self._renumber_items()
        self._update_navigation_buttons()

        # Выделяем перемещенный элемент
        self.setCurrentItem(current_temp)

        # Испускаем сигнал о перемещении
        self.botMoveUpRequested.emit(bot_idx)

    def move_bot_down(self, bot_idx):
        """Перемещает бота вниз по списку"""
        if bot_idx < 0 or bot_idx >= self.topLevelItemCount() - 1:
            return

        # Получаем элементы, которые нужно поменять местами
        current_item = self.topLevelItem(bot_idx)
        next_item = self.topLevelItem(bot_idx + 1)

        if not current_item or not next_item:
            return

        # Удаляем элементы из дерева (но не удаляем сами объекты)
        next_temp = self.takeTopLevelItem(bot_idx + 1)
        current_temp = self.takeTopLevelItem(bot_idx)

        # Вставляем элементы обратно в дерево в нужном порядке
        self.insertTopLevelItem(bot_idx, next_temp)
        self.insertTopLevelItem(bot_idx + 1, current_temp)

        # Обновляем нумерацию и кнопки навигации
        self._renumber_items()
        self._update_navigation_buttons()

        # Выделяем перемещенный элемент
        self.setCurrentItem(current_temp)

        # Испускаем сигнал о перемещении
        self.botMoveDownRequested.emit(bot_idx)

    def move_emulator_up(self, parent_idx, emu_idx):
        """Перемещает эмулятор вверх в пределах родительского бота"""
        if parent_idx < 0 or parent_idx >= self.topLevelItemCount():
            return

        parent_item = self.topLevelItem(parent_idx)
        if not parent_item:
            return

        if emu_idx <= 0 or emu_idx >= parent_item.childCount():
            return

        # Сохраняем состояние раскрытия родителя
        is_expanded = parent_item.isExpanded()

        # Получаем эмуляторы, которые нужно поменять местами
        current_emu = parent_item.child(emu_idx)
        previous_emu = parent_item.child(emu_idx - 1)

        if not current_emu or not previous_emu:
            return

        # Сохраняем данные эмуляторов
        current_data = []
        previous_data = []

        for col in range(self.columnCount()):
            current_data.append(current_emu.text(col))
            previous_data.append(previous_emu.text(col))

        current_id = current_emu.data(0, Qt.ItemDataRole.UserRole)
        previous_id = previous_emu.data(0, Qt.ItemDataRole.UserRole)

        # Обновляем данные эмуляторов
        for col in range(self.columnCount()):
            current_emu.setText(col, previous_data[col])
            previous_emu.setText(col, current_data[col])

        current_emu.setData(0, Qt.ItemDataRole.UserRole, previous_id)
        previous_emu.setData(0, Qt.ItemDataRole.UserRole, current_id)

        # Обновляем кнопки навигации для всех эмуляторов
        for i in range(parent_item.childCount()):
            self.add_navigation_buttons_to_emulator(parent_item.child(i))

        # Восстанавливаем состояние раскрытия родителя
        parent_item.setExpanded(is_expanded)

        # Испускаем сигнал о перемещении
        emu_id = current_id if current_id is not None else 0
        self.emulatorMoveUpRequested.emit(parent_idx, emu_id)

    def move_emulator_down(self, parent_idx, emu_idx):
        """Перемещает эмулятор вниз в пределах родительского бота"""
        if parent_idx < 0 or parent_idx >= self.topLevelItemCount():
            return

        parent_item = self.topLevelItem(parent_idx)
        if not parent_item:
            return

        if emu_idx < 0 or emu_idx >= parent_item.childCount() - 1:
            return

        # Сохраняем состояние раскрытия родителя
        is_expanded = parent_item.isExpanded()

        # Получаем эмуляторы, которые нужно поменять местами
        current_emu = parent_item.child(emu_idx)
        next_emu = parent_item.child(emu_idx + 1)

        if not current_emu or not next_emu:
            return

        # Сохраняем данные эмуляторов
        current_data = []
        next_data = []

        for col in range(self.columnCount()):
            current_data.append(current_emu.text(col))
            next_data.append(next_emu.text(col))

        current_id = current_emu.data(0, Qt.ItemDataRole.UserRole)
        next_id = next_emu.data(0, Qt.ItemDataRole.UserRole)

        # Обновляем данные эмуляторов
        for col in range(self.columnCount()):
            current_emu.setText(col, next_data[col])
            next_emu.setText(col, current_data[col])

        current_emu.setData(0, Qt.ItemDataRole.UserRole, next_id)
        next_emu.setData(0, Qt.ItemDataRole.UserRole, current_id)

        # Обновляем кнопки навигации для всех эмуляторов
        for i in range(parent_item.childCount()):
            self.add_navigation_buttons_to_emulator(parent_item.child(i))

        # Восстанавливаем состояние раскрытия родителя
        parent_item.setExpanded(is_expanded)

        # Испускаем сигнал о перемещении
        emu_id = current_id if current_id is not None else 0
        self.emulatorMoveDownRequested.emit(parent_idx, emu_id)

    def on_item_changed(self, item, column):
        """Обрабатывает изменение элемента (для добавления кнопок навигации)"""
        # Проверяем, что это элемент верхнего уровня (бот)
        if item.parent() is None:
            self.add_navigation_buttons_to_bot(item)
        else:
            self.add_navigation_buttons_to_emulator(item)

    def _renumber_items(self):
        """
        Перенумеровывает top-level элементы (первый столбец).
        """
        for i in range(self.topLevelItemCount()):
            it = self.topLevelItem(i)
            it.setText(0, str(i + 1))

    def _update_navigation_buttons(self):
        """Обновляет кнопки навигации для всех элементов"""
        # Обновляем кнопки для ботов
        for i in range(self.topLevelItemCount()):
            bot_item = self.topLevelItem(i)
            self.add_navigation_buttons_to_bot(bot_item)

            # Обновляем кнопки для эмуляторов этого бота
            for j in range(bot_item.childCount()):
                emu_item = bot_item.child(j)
                self.add_navigation_buttons_to_emulator(emu_item)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Обрабатывает нажатия клавиш. При нажатии Delete — удаляет выбранного бота.
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
            settings_action.setIcon(QIcon(Resources.get_icon_path("settings")))

            start_action = menu.addAction("Запустить")
            start_action.setIcon(QIcon(Resources.get_icon_path("play")))

            duplicate_action = menu.addAction("Дублировать")
            duplicate_action.setIcon(QIcon(Resources.get_icon_path("copy")))

            menu.addSeparator()

            delete_action = menu.addAction("Удалить")
            delete_action.setIcon(QIcon(Resources.get_icon_path("delete")))
        else:
            # Это эмулятор (child item)
            console_action = menu.addAction("Открыть консоль")
            console_action.setIcon(QIcon(Resources.get_icon_path("console")))

            stop_action = menu.addAction("Остановить")
            stop_action.setIcon(QIcon(Resources.get_icon_path("stop")))

            restart_action = menu.addAction("Перезапустить")
            restart_action.setIcon(QIcon(Resources.get_icon_path("restart")))

        action = menu.exec(self.mapToGlobal(pos))

        if not action:
            return

        if item.parent() is None:
            # Действия для бота
            bot_name = item.text(1)
            if action == delete_action:
                self.selected_item = item
                self.remove_selected_bot()
            elif action == settings_action:
                self.selected_item = item
                if hasattr(self.parent_window, 'show_settings_dialog'):
                    self.parent_window.show_settings_dialog()
            elif action == start_action:
                self.botStartRequested.emit(bot_name)
            elif action == duplicate_action:
                self.botDuplicateRequested.emit(bot_name)
        else:
            # Действия для эмулятора
            emu_id = item.data(0, Qt.ItemDataRole.UserRole)
            if action == console_action:
                self.emulatorConsoleRequested.emit(emu_id)
            elif action == stop_action:
                self.emulatorStopRequested.emit(emu_id)
            elif action == restart_action:
                self.emulatorRestartRequested.emit(emu_id)

    def remove_selected_bot(self):
        """
        Удаляет выбранного бота из очереди.
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
                self._update_navigation_buttons()
                self.botStopRequested.emit(bot_name)
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
                self.emulatorConsoleRequested.emit(emu_id)

    def clear_queue(self):
        """
        Очищает всю очередь ботов.
        """
        confirm = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить всю очередь?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.clear()
            return True
        return False