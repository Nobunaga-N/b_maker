# src/gui/widgets/manager_queue_widget.py
"""
Модуль содержит улучшенный класс ManagerQueueWidget - виджет для очереди ботов.
Использует базовый класс для обработки контекстных меню.
"""

from PyQt6.QtWidgets import QTreeWidgetItem, QHeaderView, QMessageBox, QAbstractItemView, QTreeWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QKeyEvent

from src.utils.resources import Resources
from src.utils.style_constants import (
    DARK_BUTTON_STYLE, COLOR_ERROR, COLOR_TEXT, MANAGER_QUEUE_WIDGET_STYLE
)
from src.utils.ui_factory import create_dark_button, create_delete_button
from src.gui.widgets.context_menu_tree_widget import ContextMenuTreeWidget


class ManagerQueueWidget(ContextMenuTreeWidget):
    """
    Улучшенный QTreeWidget для очереди ботов с улучшенной видимостью элементов.
    Использует базовый класс для обработки контекстных меню.
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
        self.selected_item = None

        # Устанавливаем количество столбцов и заголовки
        self.setColumnCount(7)
        self.setHeaderLabels([
            "№", "Бот", "Игра", "Потоки",
            "Запланирован на", "Циклы", "Время раб."
        ])

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
        self.setStyleSheet(MANAGER_QUEUE_WIDGET_STYLE)

        # Включаем двойной клик для открытия консоли эмулятора
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    # УДАЛИТЬ метод show_context_menu, так как он теперь реализован в базовом классе:
    # def show_context_menu(self, position): ...

    # ДОБАВИТЬ новый метод для определения пунктов меню
    def get_menu_items(self, item):
        """
        Возвращает список элементов для меню в зависимости от типа элемента.
        """
        if item.parent() is None:
            # Это бот (top-level item)
            return [
                {
                    'id': 'settings',
                    'text': "Настройки",
                    'icon_path': Resources.get_icon_path("settings")
                },
                {
                    'id': 'start',
                    'text': "Запустить",
                    'icon_path': Resources.get_icon_path("play")
                },
                {
                    'id': 'duplicate',
                    'text': "Дублировать",
                    'icon_path': Resources.get_icon_path("copy")
                },
                {
                    'id': 'delete',
                    'text': "Удалить",
                    'icon_path': Resources.get_icon_path("delete"),
                    'separator_before': True
                }
            ]
        else:
            # Это эмулятор (child item)
            return [
                {
                    'id': 'console',
                    'text': "Открыть консоль",
                    'icon_path': Resources.get_icon_path("console")
                },
                {
                    'id': 'stop',
                    'text': "Остановить",
                    'icon_path': Resources.get_icon_path("stop")
                },
                {
                    'id': 'restart',
                    'text': "Перезапустить",
                    'icon_path': Resources.get_icon_path("restart")
                }
            ]

    # ДОБАВИТЬ новый метод для обработки действий меню
    def handle_menu_action(self, item, action_id):
        """
        Обрабатывает выбранное действие меню.
        """
        if item.parent() is None:
            # Действия для бота
            bot_name = item.text(1)
            if action_id == 'delete':
                self.selected_item = item
                self.remove_selected_bot()
            elif action_id == 'settings':
                self.selected_item = item
                if hasattr(self.parent_window, 'show_settings_dialog'):
                    self.parent_window.show_settings_dialog()
            elif action_id == 'start':
                self.botStartRequested.emit(bot_name)
            elif action_id == 'duplicate':
                self.botDuplicateRequested.emit(bot_name)
        else:
            # Действия для эмулятора
            emu_id = item.data(0, Qt.ItemDataRole.UserRole)
            if action_id == 'console':
                self.emulatorConsoleRequested.emit(emu_id)
            elif action_id == 'stop':
                self.emulatorStopRequested.emit(emu_id)
            elif action_id == 'restart':
                self.emulatorRestartRequested.emit(emu_id)

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