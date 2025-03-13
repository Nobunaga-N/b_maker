# src/gui/widgets/context_menu_tree_widget.py
from PyQt6.QtWidgets import QTreeWidget, QMenu, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from typing import Dict, List, Optional, Any, Tuple, Callable


class ContextMenuTreeWidget(QTreeWidget):
    """
    Базовый класс для виджетов с деревом и контекстным меню.
    Предоставляет общую функциональность для создания и обработки контекстных меню.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Настраиваем обработку контекстного меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.current_item = None  # Текущий выбранный элемент для контекстного меню

    def show_context_menu(self, position):
        """
        Показывает контекстное меню.
        Базовый метод, который использует шаблонный метод для создания конкретного меню.

        Args:
            position: Позиция, где было вызвано меню
        """
        # Получаем элемент, на котором было вызвано меню
        item = self.itemAt(position)
        if not item:
            return

        self.current_item = item

        # Определяем тип элемента и создаем соответствующее меню
        menu_items = self.get_menu_items(item)
        if not menu_items:
            return

        # Создаем меню
        menu = QMenu(self)

        # Добавляем элементы меню
        self.build_menu(menu, menu_items)

        # Показываем меню и обрабатываем выбранное действие
        action = menu.exec(self.mapToGlobal(position))
        if action:
            item_id = action.property("item_id")
            # Обрабатываем выбранное действие
            self.handle_menu_action(item, item_id)

    def get_menu_items(self, item: QTreeWidgetItem) -> List[Dict[str, Any]]:
        """
        Возвращает список элементов для меню в зависимости от типа элемента.
        Должен быть переопределен в дочерних классах.

        Args:
            item: Элемент, для которого создается меню

        Returns:
            Список словарей с данными для элементов меню.
            Каждый словарь должен содержать:
            - id: Идентификатор действия
            - text: Текст пункта меню
            - icon_path: Путь к иконке (опционально)
            - separator_before: Добавить разделитель перед пунктом (опционально)
        """
        return []

    def build_menu(self, menu: QMenu, menu_items: List[Dict[str, Any]]):
        """
        Создает меню из списка элементов.

        Args:
            menu: Объект меню для наполнения
            menu_items: Список элементов меню
        """
        for item in menu_items:
            # Проверяем, нужно ли добавить разделитель
            if item.get('separator_before', False):
                menu.addSeparator()

            # Создаем действие
            action = menu.addAction(item['text'])

            # Добавляем иконку, если указана
            if 'icon_path' in item and item['icon_path']:
                action.setIcon(QIcon(item['icon_path']))

            # Сохраняем ID действия для обработки
            action.setProperty("item_id", item['id'])

    def handle_menu_action(self, item: QTreeWidgetItem, action_id: str):
        """
        Обрабатывает выбранное действие меню.
        Должен быть переопределен в дочерних классах.

        Args:
            item: Элемент, для которого было вызвано действие
            action_id: Идентификатор выбранного действия
        """
        pass