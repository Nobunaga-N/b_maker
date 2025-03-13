# src/gui/modules/canvas_module.py
"""
Модуль универсального холста для сборки модулей.
Может быть использован в различных частях приложения.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QToolBar, QToolButton, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from src.utils.style_constants import SCRIPT_SUBMODULE_ITEM_STYLE, CANVAS_MODULE_STYLE


class ModuleItem(QFrame):
    """
    Элемент модуля, который отображается на холсте.
    Представляет собой виджет с заголовком, описанием и кнопками управления.
    """
    editRequested = pyqtSignal(int)  # Сигнал для запроса редактирования (с индексом)
    deleteRequested = pyqtSignal(int)  # Сигнал для запроса удаления (с индексом)
    moveUpRequested = pyqtSignal(int)  # Сигнал для перемещения вверх
    moveDownRequested = pyqtSignal(int)  # Сигнал для перемещения вниз

    def __init__(self, index: int, module_type: str, description: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.module_type = module_type
        self.description = description
        self.data = {}  # Для хранения дополнительных данных
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс элемента модуля"""
        # Устанавливаем стиль рамки
        self.setStyleSheet("""
            ModuleItem {
                background-color: #2C2C2C;
                border: 1px solid #555;
                border-radius: 4px;
                margin: 2px;
            }
            QLabel {
                color: white;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                color: white;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)

        # Основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Верхняя строка с типом модуля и кнопками
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)

        # Тип модуля (жирный текст)
        type_label = QLabel(self.module_type)
        type_label.setStyleSheet("font-weight: bold; color: #FFA500;")
        top_layout.addWidget(type_label)

        top_layout.addStretch(1)  # Растягиваем пространство между типом и кнопками

        # Кнопки управления
        self.edit_btn = QToolButton()
        self.edit_btn.setIcon(QIcon("assets/icons/edit-white.svg"))
        self.edit_btn.setToolTip("Редактировать")
        self.edit_btn.clicked.connect(lambda: self.editRequested.emit(self.index))

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("assets/icons/delete.svg"))
        self.delete_btn.setToolTip("Удалить")
        self.delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self.index))

        self.up_btn = QToolButton()
        self.up_btn.setIcon(QIcon("assets/icons/up.svg"))
        self.up_btn.setToolTip("Переместить вверх")
        self.up_btn.clicked.connect(lambda: self.moveUpRequested.emit(self.index))

        self.down_btn = QToolButton()
        self.down_btn.setIcon(QIcon("assets/icons/down.svg"))
        self.down_btn.setToolTip("Переместить вниз")
        self.down_btn.clicked.connect(lambda: self.moveDownRequested.emit(self.index))

        top_layout.addWidget(self.up_btn)
        top_layout.addWidget(self.down_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(self.delete_btn)

        main_layout.addLayout(top_layout)

        # Описание модуля
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(desc_label)

    def set_data(self, data: dict):
        """Устанавливает дополнительные данные для элемента"""
        self.data = data

    def get_data(self) -> dict:
        """Возвращает данные элемента"""
        return self.data


class CanvasModule(QFrame):
    """
    Универсальный холст для добавления, редактирования и управления модулями.
    Может использоваться в различных частях приложения.
    """
    moduleAdded = pyqtSignal(str, str, dict)  # Сигнал о добавлении модуля (тип, описание, данные)
    moduleEdited = pyqtSignal(int, str, str, dict)  # Сигнал о редактировании модуля (индекс, тип, описание, данные)
    moduleDeleted = pyqtSignal(int)  # Сигнал об удалении модуля (индекс)
    canvasChanged = pyqtSignal()  # Сигнал об изменении холста

    def __init__(self, title: str = "Рабочий холст", parent=None):
        super().__init__(parent)
        self.title = title
        self.modules = []  # Список модулей на холсте
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс холста"""
        self.setStyleSheet(CANVAS_MODULE_STYLE)

        # Основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Заголовок холста
        title_layout = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #FFA500; font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        main_layout.addLayout(title_layout)

        # Скролл-область для холста
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #333;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Содержимое скролл-области
        self.canvas_content = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_content)
        self.canvas_layout.setContentsMargins(5, 5, 5, 5)
        self.canvas_layout.setSpacing(10)
        self.canvas_layout.addStretch(1)  # Добавляем растягивающийся элемент внизу

        scroll_area.setWidget(self.canvas_content)
        main_layout.addWidget(scroll_area, 1)  # Растягиваем скролл-область

        # Панель инструментов для добавления модулей
        tools_layout = QHBoxLayout()
        self.create_tool_buttons(tools_layout)
        main_layout.addLayout(tools_layout)

    def create_tool_buttons(self, layout):
        """
        Создает кнопки для панели инструментов.
        Переопределяется в дочерних классах для добавления специфичных кнопок.
        """
        # Базовые кнопки можно добавить здесь, если нужно
        layout.addStretch(1)  # Растягивающееся пространство

    def add_module(self, module_type: str, description: str, data: dict = None):
        """Добавляет новый модуль на холст подмодуля"""
        index = len(self.modules)
        module_item = ModuleItem(index, module_type, description)
        module_item.setStyleSheet(SCRIPT_SUBMODULE_ITEM_STYLE)

        if data:
            module_item.set_data(data)

        # Подключаем сигналы
        module_item.editRequested.connect(self.edit_module)
        module_item.deleteRequested.connect(self.delete_module)
        module_item.moveUpRequested.connect(self.move_module_up)
        module_item.moveDownRequested.connect(self.move_module_down)

        # Добавляем в список и на холст
        self.modules.append(module_item)

        # Вставляем перед растягивающимся элементом
        self.canvas_layout.insertWidget(self.canvas_layout.count() - 1, module_item)

        # Испускаем сигнал
        self.moduleAdded.emit(module_type, description, data or {})
        self.canvasChanged.emit()

        return index

    def edit_module(self, index: int):
        """
        Метод-заглушка для редактирования модуля.
        Должен быть переопределен в дочерних классах.
        """
        if 0 <= index < len(self.modules):
            module = self.modules[index]
            print(f"Редактирование модуля {module.module_type} с индексом {index}")
            # Логика редактирования будет реализована в дочерних классах

    def delete_module(self, index: int):
        """Удаляет модуль с указанным индексом"""
        if 0 <= index < len(self.modules):
            # Спрашиваем подтверждение
            module = self.modules[index]
            reply = QMessageBox.question(
                self,
                "Удаление модуля",
                f"Вы уверены, что хотите удалить модуль '{module.module_type}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Удаляем из холста и списка
                self.canvas_layout.removeWidget(module)
                module.deleteLater()
                self.modules.pop(index)

                # Обновляем индексы оставшихся модулей
                for i, mod in enumerate(self.modules):
                    mod.index = i

                # Испускаем сигнал
                self.moduleDeleted.emit(index)
                self.canvasChanged.emit()

    def move_module_up(self, index: int):
        """Перемещает модуль вверх по списку"""
        if index > 0 and index < len(self.modules):
            # Меняем местами в списке
            self.modules[index - 1], self.modules[index] = self.modules[index], self.modules[index - 1]

            # Обновляем индексы
            self.modules[index - 1].index = index - 1
            self.modules[index].index = index

            # Перерисовываем на холсте
            self._redraw_modules()

            # Испускаем сигнал
            self.canvasChanged.emit()

    def move_module_down(self, index: int):
        """Перемещает модуль вниз по списку"""
        if index >= 0 and index < len(self.modules) - 1:
            # Меняем местами в списке
            self.modules[index], self.modules[index + 1] = self.modules[index + 1], self.modules[index]

            # Обновляем индексы
            self.modules[index].index = index
            self.modules[index + 1].index = index + 1

            # Перерисовываем на холсте
            self._redraw_modules()

            # Испускаем сигнал
            self.canvasChanged.emit()

    def _redraw_modules(self):
        """Перерисовывает все модули на холсте"""
        # Удаляем все виджеты с холста
        for module in self.modules:
            self.canvas_layout.removeWidget(module)

        # Добавляем виджеты обратно в правильном порядке
        for module in self.modules:
            self.canvas_layout.insertWidget(self.canvas_layout.count() - 1, module)

    def clear(self):
        """Очищает холст"""
        # Удаляем все модули
        for module in self.modules:
            self.canvas_layout.removeWidget(module)
            module.deleteLater()

        self.modules.clear()
        self.canvasChanged.emit()

    def get_modules_data(self) -> list:
        """Возвращает данные всех модулей"""
        data = []
        for module in self.modules:
            module_data = {
                "type": module.module_type,
                "description": module.description,
                "data": module.get_data()
            }
            data.append(module_data)
        return data

    def load_modules_data(self, modules_data: list):
        """Загружает данные модулей на холст"""
        self.clear()
        for module_data in modules_data:
            self.add_module(
                module_data.get("type", ""),
                module_data.get("description", ""),
                module_data.get("data", {})
            )