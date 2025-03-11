# src/utils/style_constants.py
"""
Модуль содержит константы стилей для всего приложения.
Это позволяет унифицировать внешний вид и уменьшить дублирование кода.
"""

# Основной стиль для диалогов
DIALOG_STYLE = """
    QDialog {
        background-color: #2C2C2C;
        color: white;
    }
    QLabel {
        color: white;
        font-weight: bold;
    }
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #3A3A3A;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
    }
    QPushButton {
        background-color: #FFA500;
        color: black;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }
    QPushButton:hover {
        background-color: #FFB347;
    }
    QGroupBox {
        color: #FFA500;
        font-weight: bold;
        border: 1px solid #555;
        border-radius: 4px;
        margin-top: 15px;
        padding-top: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
"""

# Стиль для чекбоксов
CHECKBOX_STYLE = """
    QCheckBox {
        color: white;
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
    }
    QCheckBox::indicator:unchecked {
        border: 1px solid #555;
        background-color: #2C2C2C;
    }
    QCheckBox::indicator:checked {
        border: 1px solid #555;
        background-color: #FFA500;
    }
"""

# Стиль для табов и таблиц
TAB_AND_TABLE_STYLE = """
    QTabWidget::pane {
        border: 1px solid #555;
        border-radius: 4px;
        background-color: #2C2C2C;
    }
    QTabBar::tab {
        background-color: #3A3A3A;
        color: white;
        border: 1px solid #555;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 8ex;
        padding: 6px;
    }
    QTabBar::tab:selected {
        background-color: #FFA500;
    }
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    QTableWidget {
        background-color: #3A3A3A;
        color: white;
        gridline-color: #555;
    }
    QHeaderView::section {
        background-color: #3a3a3a;
        color: white;
        padding: 4px;
        border: 1px solid #555;
    }
"""

# Стиль для скролл-баров
SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        border: none;
        background-color: #3A3A3A;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #FFA500;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background-color: #3A3A3A;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: #FFA500;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""

# Стиль для выпадающих списков
COMBOBOX_STYLE = """
    QComboBox {
        background-color: #3A3A3A;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
        min-width: 6em;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: #555;
        border-left-style: solid;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #555;
        selection-background-color: #FFA500;
        background-color: #2C2C2C;
        color: white;
    }
"""

# Стиль для кнопки удаления
DELETE_BUTTON_STYLE = """
    QPushButton {
        background-color: #FF4444;
        color: #FFF;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #FF6666;
    }
"""

# Стиль для заголовков
TITLE_STYLE = """
    color: #FFA500;
    font-size: 16px;
    font-weight: bold;
"""

# Стиль для основных фреймов
MAIN_FRAME_STYLE = """
    background-color: #1E1E1E; 
    border-radius: 8px;
    border: 1px solid #444;
"""

# В файле src/utils/style_constants.py добавьте или измените эти константы



# Цвет акцентов (вместо оранжевого)
ACCENT_COLOR = "#F0C14B"  # для совместимости со старым кодом
ACCENT_COLOR_HOVER = "#DDAF37"  # для совместимости со старым кодом
PRIMARY_COLOR = "#F0C14B"  # темно оранжевый
PRIMARY_COLOR_HOVER = "#DDAF37"  # темно оранжевый с небольшим засветлением


# Обновленный стиль акцентных кнопок
ACCENT_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: black;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_COLOR_HOVER};
    }}
"""
# Цвет фона для бокового меню (темный, почти черный)
SIDEBAR_COLOR = "#121212"  # Глубокий черный

# Стили для бокового меню с окантовкой
SIDEBAR_STYLE = f"""
    background-color: {SIDEBAR_COLOR};
    border-right: 2px solid #333333;
"""

# Стиль кнопок бокового меню (белый текст)
SIDEBAR_BUTTON_STYLE = """
    QPushButton {
        color: white;
        background: transparent;
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
"""

# Стиль активной кнопки бокового меню
SIDEBAR_ACTIVE_BUTTON_STYLE = """
    QPushButton {
        color: white;
        background-color: rgba(255, 255, 255, 0.15);
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.25);
    }
"""

# Стиль иконки бургера и других иконок в меню
SIDEBAR_ICON_STYLE = """
    QToolButton {
        background: transparent;
        border: none;
        color: white;
    }
    QToolButton:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
"""

# Добавьте эти константы в src/utils/style_constants.py

# Улучшенный стиль для диалогов модулей
MODULE_DIALOG_STYLE = """
    QDialog {
        background-color: #202020;
        color: white;
    }
    QLabel {
        color: white;
    }
    QGroupBox {
        font-weight: bold;
        color: #FFA500;
        border: 1px solid #444;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
    }
    QSpinBox, QDoubleSpinBox {
        background-color: #2A2A2A;
        color: white;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 3px;
        min-height: 22px;
        max-height: 22px;
    }
    QLineEdit {
        background-color: #2A2A2A;
        color: white;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 3px;
        min-height: 22px;
        max-height: 22px;
    }
    QToolTip {
        background-color: #2A2A2A;
        color: white;
        border: 1px solid #FFA500;
        padding: 2px;
        opacity: 200;
    }
"""

# Стиль для кнопок в диалогах модулей (с оранжевым цветом #FFA500)
MODULE_BUTTON_STYLE = """
    QPushButton {
        background-color: #FFA500;
        color: black;
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FFB347;
    }
"""

# Стиль для групп в форме
FORM_GROUP_STYLE = """
    QGroupBox {
        font-weight: bold;
        color: #FFA500;
        border: 1px solid #444;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 16px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
        color: #FFA500;
    }
    QLabel {
        color: white;
    }
"""

# Добавьте эти константы в src/utils/style_constants.py

# Стиль для элементов ModuleItem
MODULE_ITEM_STYLE = """
    ModuleItem {
        background-color: #2A2A2A;
        border: 1px solid #444;
        border-radius: 3px;
        margin: 2px;
    }
    ModuleItem:hover {
        border: 1px solid #FFA500;
    }
    QLabel {
        color: white;
        padding: 2px;
    }
    QToolButton {
        background-color: transparent;
        border: none;
        color: white;
        icon-size: 16px;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
        padding: 1px;
    }
    QToolButton:hover {
        background-color: rgba(255, 165, 0, 0.2);
        border-radius: 2px;
    }
"""

# Стиль для кнопок инструментов
TOOL_BUTTON_STYLE = """
    QToolButton {
        background-color: transparent;
        border: none;
        color: white;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
    }
    QToolButton:hover {
        background-color: rgba(255, 165, 0, 0.2);
        border-radius: 2px;
    }
"""

# Стиль для холста модулей
CANVAS_MODULE_STYLE = """
    background-color: #252525;
    border-radius: 3px;
    border: 1px solid #444;
"""

# Стиль для холста модулей активности
ACTIVITY_CANVAS_STYLE = """
    background-color: #252525;
    border-radius: 4px;
    border: 1px solid #444;
"""

# Стиль для диалога активности
ACTIVITY_DIALOG_STYLE = """
    QDialog {
        background-color: #2A2A2A;
        color: white;
    }
    QLabel {
        color: white;
    }
    QGroupBox {
        font-weight: bold;
        color: #FFA500;
        border: 1px solid #555;
        border-radius: 4px;
        margin-top: 15px;
        padding-top: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QLineEdit, QSpinBox, QDoubleSpinBox {
        background-color: #333;
        color: white;
        border: 1px solid #555;
        border-radius: 3px;
    }
    QComboBox {
        background-color: #333;
        color: white; 
        border: 1px solid #555;
        border-radius: 3px;
        padding: 4px;
    }
    QPushButton {
        background-color: #FFA500;
        color: black;
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FFB347;
    }
    QCheckBox {
        color: white;
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
    }
    QToolTip {
        background-color: #2A2A2A;
        color: white;
        border: 1px solid #FFA500;
        padding: 2px;
        opacity: 200;
    }
"""

# Стиль для страницы создания бота
CREATE_BOT_STYLE = """
    QWidget#createBotPage {
        background-color: #000000;
    }
"""

# Стиль для таблицы (холста) модулей
TABLE_STYLE = """
    QTableWidget {
        background-color: #2C2C2C;
        color: white;
        gridline-color: #444;
        border: none;
    }
    QHeaderView::section {
        background-color: #3A3A3A;
        color: #FFA500;
        padding: 5px;
        border: 1px solid #444;
    }
    QTableWidget::item:selected {
        background-color: #FFA500;
        color: white;
    }
"""

# Стиль для кнопки сохранения в настройках
SETTINGS_BUTTON_STYLE = """
    QPushButton {
        background-color: #FFA500;
        color: #000;
        border-radius: 4px;
        padding: 10px;
        font-weight: bold;
        margin-top: 10px;
    }
    QPushButton:hover {
        background-color: #FFB347;
    }
"""

# Стиль для заголовка модуля активности
ACTIVITY_MODULE_TITLE_STYLE = "color: #FFA500; font-size: 14px; font-weight: bold; margin-bottom: 8px;"

# Полный стиль для диалогов (комбинация стилей)
FULL_DIALOG_STYLE = DIALOG_STYLE + CHECKBOX_STYLE + TAB_AND_TABLE_STYLE + SCROLLBAR_STYLE + COMBOBOX_STYLE