# src/gui/widgets/bot_list_widget.py
"""
Модуль содержит класс BotListWidget - улучшенный виджет для отображения
и управления списком доступных ботов.
"""

from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush

from src.utils.style_constants import TABLE_STYLE
from src.utils.resources import Resources
from src.gui.widgets.context_menu_tree_widget import ContextMenuTreeWidget


class BotListWidget(ContextMenuTreeWidget):
    """
    Улучшенный виджет списка ботов с дополнительными возможностями.
    Использует базовый класс для обработки контекстных меню.
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

        # Настройка двойного клика
        self.itemDoubleClicked.connect(self.on_double_click)

    # УДАЛИТЬ метод show_context_menu, так как он теперь реализован в базовом классе:
    # def show_context_menu(self, position): ...

    # ДОБАВИТЬ новый метод для определения пунктов меню
    def get_menu_items(self, item):
        """
        Возвращает список элементов для меню ботов.
        """
        return [
            {
                'id': 'edit',
                'text': "Редактировать",
                'icon_path': Resources.get_icon_path("edit")
            },
            {
                'id': 'add_to_manager',
                'text': "Добавить в менеджер",
                'icon_path': Resources.get_icon_path("add-to-queue")
            },
            {
                'id': 'export',
                'text': "Экспорт",
                'icon_path': Resources.get_icon_path("export"),
                'separator_before': True
            },
            {
                'id': 'delete',
                'text': "Удалить",
                'icon_path': Resources.get_icon_path("delete")
            }
        ]

    # ДОБАВИТЬ новый метод для обработки действий меню
    def handle_menu_action(self, item, action_id):
        """
        Обрабатывает выбранное действие меню.
        """
        bot_name = item.text(0)
        game_name = item.text(1)

        if action_id == 'edit':
            self.botEditRequested.emit(bot_name)
        elif action_id == 'add_to_manager':
            self.botAddToManagerRequested.emit(bot_name, game_name)
        elif action_id == 'delete':
            self.on_delete_bot(bot_name)
        elif action_id == 'export':
            self.botExportRequested.emit(bot_name)

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

    # СОХРАНИТЬ этот метод, так как он содержит бизнес-логику, а не только отображение меню
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