# src/gui/widgets/manager_queue_widget.py
"""
Модуль содержит улучшенный класс ManagerQueueWidget - виджет для очереди ботов.
Решает проблемы с перетаскиванием, стилизацией и улучшает пользовательский опыт.
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QAbstractItemView,
    QHeaderView, QPushButton, QHBoxLayout, QWidget, QVBoxLayout,
    QToolButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QKeyEvent

from src.utils.resources import Resources
from src.utils.style_constants import DARK_BUTTON_STYLE


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

        # Добавляем навигационную панель внизу
        self.setup_navigation_panel()

    def setup_navigation_panel(self):
        """
        Создает и настраивает навигационную панель с кнопками перемещения вверх/вниз.
        Эта панель размещается внизу виджета.
        """
        # Родительский виджет ManagerQueueWidget использует QTreeWidget,
        # который не поддерживает прямое добавление других виджетов
        # Поэтому мы должны создать панель отдельно и добавить ее через родительский лейаут
        if self.parent_window:
            # Создаем рамку для навигационной панели
            self.nav_panel = QFrame(self.parent_window)
            self.nav_panel.setFrameShape(QFrame.Shape.StyledPanel)
            self.nav_panel.setStyleSheet("""
                QFrame {
                    background-color: #252525;
                    border-top: 1px solid #444;
                    border-radius: 4px;
                    margin-top: 5px;
                }
            """)

            # Создаем лейаут для навигационной панели
            nav_layout = QHBoxLayout(self.nav_panel)
            nav_layout.setContentsMargins(5, 5, 5, 5)
            nav_layout.setSpacing(5)

            # Создаем метку с подсказкой
            nav_label = QLabel("Перемещение выбранного элемента:")
            nav_label.setStyleSheet("color: white;")
            nav_layout.addWidget(nav_label)

            # Создаем кнопки перемещения
            self.btn_move_up = QPushButton("Вверх")
            self.btn_move_up.setIcon(QIcon(Resources.get_icon_path("up")))
            self.btn_move_up.setToolTip("Переместить выбранный элемент вверх")
            self.btn_move_up.setStyleSheet(DARK_BUTTON_STYLE)
            self.btn_move_up.clicked.connect(self.move_selected_item_up)

            self.btn_move_down = QPushButton("Вниз")
            self.btn_move_down.setIcon(QIcon(Resources.get_icon_path("down")))
            self.btn_move_down.setToolTip("Переместить выбранный элемент вниз")
            self.btn_move_down.setStyleSheet(DARK_BUTTON_STYLE)
            self.btn_move_down.clicked.connect(self.move_selected_item_down)

            # Добавляем кнопки в лейаут
            nav_layout.addWidget(self.btn_move_up)
            nav_layout.addWidget(self.btn_move_down)
            nav_layout.addStretch(1)  # Добавляем растяжку справа

            # Находим родительский лейаут QTreeWidget и добавляем навигационную панель
            if isinstance(self.parent_window.layout(), QVBoxLayout):
                # Ищем индекс текущего виджета в родительском лейауте
                for i in range(self.parent_window.layout().count()):
                    if self.parent_window.layout().itemAt(i).widget() == self:
                        # Добавляем навигационную панель после текущего виджета
                        self.parent_window.layout().insertWidget(i + 1, self.nav_panel)
                        break

    def move_selected_item_up(self):
        """Перемещает выбранный элемент вверх"""
        item = self.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите элемент для перемещения")
            return

        # Определяем, является ли элемент ботом или эмулятором
        if item.parent() is None:
            # Это бот (top-level item)
            bot_idx = self.indexOfTopLevelItem(item)
            if bot_idx > 0:  # Проверяем, не первый ли элемент
                self.move_bot_up(bot_idx)
        else:
            # Это эмулятор (child item)
            parent = item.parent()
            emu_idx = parent.indexOfChild(item)
            parent_idx = self.indexOfTopLevelItem(parent)

            if emu_idx > 0:  # Проверяем, не первый ли эмулятор
                self.move_emulator_up(parent_idx, emu_idx)

    def move_selected_item_down(self):
        """Перемещает выбранный элемент вниз"""
        item = self.currentItem()
        if not item:
            QMessageBox.warning(self, "Внимание", "Выберите элемент для перемещения")
            return

        # Определяем, является ли элемент ботом или эмулятором
        if item.parent() is None:
            # Это бот (top-level item)
            bot_idx = self.indexOfTopLevelItem(item)
            if bot_idx < self.topLevelItemCount() - 1:  # Проверяем, не последний ли элемент
                self.move_bot_down(bot_idx)
        else:
            # Это эмулятор (child item)
            parent = item.parent()
            emu_idx = parent.indexOfChild(item)
            parent_idx = self.indexOfTopLevelItem(parent)

            if emu_idx < parent.childCount() - 1:  # Проверяем, не последний ли эмулятор
                self.move_emulator_down(parent_idx, emu_idx)

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

        # Добавляем контекстное меню
        child.setToolTip(1, "Двойной клик для открытия консоли, правый клик для меню управления")

        # Раскрываем родительский элемент
        parent_item.setExpanded(True)

        return child

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

        # Восстанавливаем состояние раскрытия родителя
        parent_item.setExpanded(is_expanded)

        # Испускаем сигнал о перемещении
        emu_id = current_id if current_id is not None else 0
        self.emulatorMoveDownRequested.emit(parent_idx, emu_id)

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

        # Добавляем контекстное меню
        queue_item.setToolTip(0, "Нажмите правой кнопкой для управления ботом")

        return queue_item

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

        # Обновляем нумерацию
        self._renumber_items()

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

        # Обновляем нумерацию
        self._renumber_items()

        # Выделяем перемещенный элемент
        self.setCurrentItem(current_temp)

        # Испускаем сигнал о перемещении
        self.botMoveDownRequested.emit(bot_idx)

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