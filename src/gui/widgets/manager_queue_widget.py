# src/gui/widgets/manager_queue_widget.py
"""
Модуль содержит класс ManagerQueueWidget - улучшенный виджет для очереди ботов.
Обеспечивает более удобное управление ботами в очереди через контекстное меню.
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QKeyEvent

from src.utils.style_constants import TABLE_STYLE
from src.utils.resources import Resources


class ManagerQueueWidget(QTreeWidget):
    """
    QTreeWidget для очереди ботов с улучшенной функциональностью.
    Содержит методы для добавления, удаления и управления ботами.
    Поддерживает перетаскивание, контекстное меню и обработку событий клавиатуры.
    """
    # Сигналы для оповещения родительского виджета
    botStartRequested = pyqtSignal(str)  # Имя бота для запуска
    botStopRequested = pyqtSignal(str)  # Имя бота для остановки
    botDuplicateRequested = pyqtSignal(str)  # Имя бота для дублирования
    emulatorConsoleRequested = pyqtSignal(int)  # ID эмулятора для консоли
    emulatorStopRequested = pyqtSignal(int)  # ID эмулятора для остановки
    emulatorRestartRequested = pyqtSignal(int)  # ID эмулятора для перезапуска

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
        font = QFont("Segoe UI", 11)
        for col in range(self.columnCount()):
            queue_item.setFont(col, font)
            queue_item.setForeground(col, QBrush(QColor("white")))

        # Добавляем элемент в дерево
        self.addTopLevelItem(queue_item)

        # Добавляем контекстное меню вместо кнопок
        queue_item.setFlags(queue_item.flags() | Qt.ItemFlag.ItemIsEditable)
        queue_item.setToolTip(0, "Нажмите правой кнопкой для управления ботом")

        return queue_item

    def dropEvent(self, event):
        """Обрабатывает событие перетаскивания (drop) элементов в дереве."""
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
                    to_lift.append((parent_item, child_item))

        for parent, item in to_lift:
            # Создаем новый элемент с теми же данными
            new_item = QTreeWidgetItem([item.text(k) for k in range(self.columnCount())])

            # Копируем шрифт/цвет и другие свойства
            for col in range(self.columnCount()):
                new_item.setFont(col, item.font(col))
                new_item.setForeground(col, item.foreground(col))
                if item.data(col, Qt.ItemDataRole.UserRole):
                    new_item.setData(col, Qt.ItemDataRole.UserRole, item.data(col, Qt.ItemDataRole.UserRole))

            # Добавляем на верхний уровень
            self.addTopLevelItem(new_item)

            # Удаляем старый элемент
            parent.removeChild(item)

        # Обновляем нумерацию
        self._renumber_items()

    def _renumber_items(self):
        """
        Перенумеровывает top-level элементы (первый столбец).
        """
        for i in range(self.topLevelItemCount()):
            it = self.topLevelItem(i)
            it.setText(0, str(i + 1))

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
            if action == delete_action:
                self.selected_item = item
                self.remove_selected_bot()
            elif action == settings_action:
                self.selected_item = item
                if hasattr(self.parent_window, 'show_settings_dialog'):
                    self.parent_window.show_settings_dialog()
            elif action == start_action:
                bot_name = item.text(1)
                self.botStartRequested.emit(bot_name)
            elif action == duplicate_action:
                bot_name = item.text(1)
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