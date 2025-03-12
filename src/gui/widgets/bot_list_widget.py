# src/gui/widgets/bot_list_widget.py
"""
Модуль содержит класс BotListWidget - улучшенный виджет для отображения
и управления списком доступных ботов.
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush

from src.utils.style_constants import TABLE_STYLE
from src.utils.resources import Resources


class BotListWidget(QTreeWidget):
    """
    Улучшенный виджет списка ботов с дополнительными возможностями.
    """
    # Сигналы для взаимодействия с родительским виджетом
    botEditRequested = pyqtSignal(str)  # Имя бота для редактирования
    botAddToManagerRequested = pyqtSignal(str, str)  # Имя бота и игры для добавления в менеджер
    botDeleteRequested = pyqtSignal(str)  # Имя бота для удаления
    botExportRequested = pyqtSignal(str)  # Имя бота для экспорта
    botImportRequested = pyqtSignal()  # Сигнал для импорта бота

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        """Настраивает внешний вид виджета"""
        # Настройка заголовков (Название бота, Игра)
        self.setColumnCount(2)
        self.setHeaderLabels(["Название бота", "Игра"])
        self.setStyleSheet(TABLE_STYLE)

        # Настройка видимости и поведения
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)

        # Настройка отображения столбцов
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Настройка контекстного меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Настройка двойного клика
        self.itemDoubleClicked.connect(self.on_double_click)

    def add_bot(self, bot_name, game_name):
        """Добавляет бота в список"""
        item = QTreeWidgetItem([bot_name, game_name])

        # Устанавливаем цвет и шрифт
        font = QFont("Segoe UI", 11)
        for col in range(self.columnCount()):
            item.setFont(col, font)
            item.setForeground(col, QBrush(QColor("white")))

        # Добавляем в список
        self.addTopLevelItem(item)
        return item

    def load_bots(self, bots_data):
        """Загружает список ботов из данных"""
        self.clear()
        for bot_name, game_name in bots_data:
            self.add_bot(bot_name, game_name)

    def get_selected_bot(self):
        """Возвращает выбранный элемент бота"""
        items = self.selectedItems()
        if items:
            return items[0]
        return None

    def get_selected_bot_data(self):
        """Возвращает данные выбранного бота (имя, игра)"""
        item = self.get_selected_bot()
        if item:
            return item.text(0), item.text(1)
        return None, None

    def on_double_click(self, item):
        """Обрабатывает двойной клик - запрос на редактирование бота"""
        if item:
            self.botEditRequested.emit(item.text(0))

    def show_context_menu(self, position):
        """Показывает контекстное меню для выбранного бота"""
        item = self.itemAt(position)
        if not item:
            return

        # Создаем меню
        menu = QMenu(self)

        # Добавляем действия
        edit_action = menu.addAction("Редактировать")
        edit_action.setIcon(QIcon(Resources.get_icon_path("edit")))

        add_to_manager_action = menu.addAction("Добавить в менеджер")
        add_to_manager_action.setIcon(QIcon(Resources.get_icon_path("add-to-queue")))

        menu.addSeparator()

        export_action = menu.addAction("Экспорт")
        export_action.setIcon(QIcon(Resources.get_icon_path("export")))

        delete_action = menu.addAction("Удалить")
        delete_action.setIcon(QIcon(Resources.get_icon_path("delete")))

        # Выполняем меню
        action = menu.exec(self.mapToGlobal(position))

        # Обрабатываем выбранное действие
        if action == edit_action:
            self.botEditRequested.emit(item.text(0))
        elif action == add_to_manager_action:
            self.botAddToManagerRequested.emit(item.text(0), item.text(1))
        elif action == delete_action:
            self.on_delete_bot(item.text(0))
        elif action == export_action:
            self.botExportRequested.emit(item.text(0))

    def on_delete_bot(self, bot_name):
        """Запрашивает подтверждение удаления бота"""
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить бота '{bot_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.botDeleteRequested.emit(bot_name)

    def handle_bot_deleted(self, bot_name):
        """Удаляет бота из списка после подтверждения удаления"""
        # Находим элемент с указанным именем бота
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.text(0) == bot_name:
                # Удаляем элемент
                self.takeTopLevelItem(i)
                break