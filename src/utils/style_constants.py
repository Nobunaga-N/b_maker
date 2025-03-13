"""
Модуль содержит константы стилей для всего приложения.
Это позволяет унифицировать внешний вид и уменьшить дублирование кода.
"""

# Основные цвета
COLOR_PRIMARY = "#FFA500"  # Оранжевый (акцентный цвет)
COLOR_SECONDARY = "#4C7BD9"  # Синий (для синей темы)
COLOR_ERROR = "#FF4444"  # Красный (для ошибок и удаления)
COLOR_SUCCESS = "#44BB44"  # Зеленый (для успеха)
COLOR_WARNING = "#FFB347"  # Светло-оранжевый (для предупреждений)

# Темные фоны
COLOR_BG_DARK = "#000000"  # Основной фон приложения
COLOR_BG_DARK_1 = "#1E1E1E"  # Основной фон фреймов
COLOR_BG_DARK_2 = "#2A2A2A"  # Фон полей ввода и элементов
COLOR_BG_DARK_3 = "#333333"  # Фон заголовков и более светлых областей

# Границы
COLOR_BORDER = "#444444"  # Основные границы
COLOR_BORDER_LIGHT = "#555555"  # Светлые границы

# Текст
COLOR_TEXT = "#FFFFFF"  # Основной текст
COLOR_TEXT_SECONDARY = "#CCCCCC"  # Вторичный текст

# Синяя тема
COLOR_BLUE_BG = "#1E2B3C"  # Фон синей темы
COLOR_BLUE_ACCENT = "#4C7BD9"  # Акцент синей темы
COLOR_BLUE_HIGHLIGHT = "#5E8DE5"  # Подсветка синей темы
COLOR_BLUE_BG_LIGHT = "#283A5A"  # Светлый фон синей темы
COLOR_BLUE_TEXT = "#89B4FF"  # Текст синей темы

# Базовые стили компонентов

# Общие стили для всех диалогов
BASE_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLOR_BG_DARK_1};
        color: {COLOR_TEXT};
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QGroupBox {{
        font-weight: bold;
        color: {COLOR_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
    }}
    QToolTip {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_PRIMARY};
        padding: 2px;
        opacity: 200;
    }}
"""

# Стиль для кнопок
BASE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_PRIMARY};
        color: black;
        border-radius: 4px;
        padding: 6px 10px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLOR_WARNING};
    }}
"""

# Стиль для темных кнопок
DARK_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_TEXT};
        border-radius: 3px;
        padding: 5px 10px;
    }}
    QPushButton:hover {{
        background-color: {COLOR_BG_DARK_3};
    }}
"""

# Стиль для кнопки удаления
DELETE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_ERROR};
        color: {COLOR_TEXT};
        border-radius: 4px;
        padding: 6px 10px;
    }}
    QPushButton:hover {{
        background-color: #FF6666;
    }}
"""

# Стиль для полей ввода
BASE_INPUT_STYLE = f"""
    background-color: {COLOR_BG_DARK_2}; 
    color: {COLOR_TEXT}; 
    padding: 4px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    min-height: 22px;
    max-height: 22px;
"""

# Стиль для спин-боксов
BASE_SPINBOX_STYLE = f"""
    background-color: {COLOR_BG_DARK_2}; 
    color: {COLOR_TEXT}; 
    padding: 4px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    min-height: 22px;
    max-height: 22px;
"""

# Стиль для комбо-боксов
BASE_COMBOBOX_STYLE = f"""
    QComboBox {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT}; 
        padding: 4px;
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_PRIMARY};
    }}
"""

# Стиль для таблиц
BASE_TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        gridline-color: {COLOR_BORDER};
        border: none;
    }}
    QHeaderView::section {{
        background-color: {COLOR_BG_DARK_3};
        color: {COLOR_PRIMARY};
        padding: 5px;
        border: 1px solid {COLOR_BORDER};
    }}
    QTableWidget::item:selected {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_TEXT};
    }}
"""

# Стиль для основных фреймов
MAIN_FRAME_STYLE = f"""
    background-color: {COLOR_BG_DARK_1}; 
    border-radius: 8px;
    border: 1px solid {COLOR_BORDER};
"""

# Остальные специфические стили для совместимости
MODULE_DIALOG_STYLE = BASE_DIALOG_STYLE
TABLE_STYLE = BASE_TABLE_STYLE
SETTINGS_BUTTON_STYLE = BASE_BUTTON_STYLE
TOOLTIP_STYLE = f"""
    QToolTip {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_PRIMARY};
        padding: 2px;
    }}
"""

# Стили для боковой панели
SIDEBAR_STYLE = f"""
    background-color: #121212;
    border-right: 2px solid {COLOR_BG_DARK_3};
"""

SIDEBAR_BUTTON_STYLE = f"""
    QPushButton {{
        color: {COLOR_TEXT};
        background: transparent;
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
"""

SIDEBAR_ACTIVE_BUTTON_STYLE = f"""
    QPushButton {{
        color: {COLOR_TEXT};
        background-color: rgba(255, 255, 255, 0.15);
        border: none;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.25);
    }}
"""

SIDEBAR_ICON_STYLE = f"""
    QToolButton {{
        background: transparent;
        border: none;
        color: {COLOR_TEXT};
    }}
    QToolButton:hover {{
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }}
"""

# Заголовок
TITLE_STYLE = f"""
    color: {COLOR_PRIMARY};
    font-size: 16px;
    font-weight: bold;
"""


# Обновленный стиль акцентных кнопок
ACCENT_BUTTON_STYLE = """
    QPushButton {
        background-color: #FFA500;
        color: black;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FFB347;
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

# Стиль для кнопок в таблице
TABLE_ACTION_BUTTON_STYLE = """
    QPushButton {
        background-color: #222222;
        color: white;
        border: 1px solid white;
        border-radius: 2px;
        padding: 4px 8px;
    }
    QPushButton:hover {
        background-color: #333333;
    }
"""

# Стиль для элементов скрипта
SCRIPT_ITEM_STYLE = """
    QFrame {
        background-color: #2A2A2A;
        border: 1px solid #444;
        border-radius: 3px;
        margin: 2px;
    }
    QFrame:hover {
        border: 1px solid #FFA500;
    }
"""

# Стиль для заголовка элемента скрипта
SCRIPT_ITEM_HEADER_STYLE = """
    color: #FFA500; 
    font-weight: bold;
"""

# Стиль для описания элемента скрипта
SCRIPT_ITEM_DESCRIPTION_STYLE = """
    color: #CCCCCC; 
    font-size: 11px; 
    margin-left: 24px;
"""

# Стиль для кнопок в элементе скрипта
SCRIPT_ITEM_BUTTON_STYLE = """
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

# Стиль для кнопки удаления в элементе скрипта
SCRIPT_ITEM_DELETE_BUTTON_STYLE = """
    QToolButton {
        background-color: transparent;
        border: none;
        color: #FF4444;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
    }
    QToolButton:hover {
        background-color: rgba(255, 68, 68, 0.2);
        border-radius: 2px;
    }
"""

# Стиль для холста скрипта
SCRIPT_CANVAS_STYLE = """
    background-color: #252525; 
    border-radius: 3px; 
    border: 1px solid #444;
"""

# Стиль для кнопки отмены (красная)
CANCEL_BUTTON_STYLE = """
    QPushButton {
        background-color: #FF4444;
        color: white;
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FF6666;
    }
"""

# Стиль для кнопки подтверждения (зеленая)
CONFIRM_BUTTON_STYLE = """
    QPushButton {
        background-color: #44BB44;
        color: white;
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #66CC66;
    }
"""

# Стиль для панели кнопок
BUTTONS_PANEL_STYLE = """
    QFrame {
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
        margin-top: 10px;
        background-color: #2A2A2A;
    }
"""

# Стиль для компактной секции настроек изображений
COMPACT_IMAGE_SETTINGS_STYLE = """
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
        margin: 2px;
    }
    QHBoxLayout {
        margin: 2px;
        spacing: 4px;
    }
"""

# Стиль для диалогов скрипт-блоков с синей темой
SCRIPT_DIALOG_BLUE_STYLE = """
    QDialog {
        background-color: #1E2B3C;
        border: 2px solid #4C7BD9;
    }
    QPushButton {
        background-color: #4C7BD9;
        color: white;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5E8DE5;
    }
    QGroupBox {
        border: 1px solid #4C7BD9;
        color: #89B4FF;
        font-weight: bold;
        margin-top: 15px;
        padding-top: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QLabel {
        color: white;
    }
    QLineEdit, QComboBox {
        background-color: #283A5A;
        color: white;
        border: 1px solid #4C7BD9;
        border-radius: 3px;
        padding: 4px;
    }
    QComboBox QAbstractItemView {
        background-color: #283A5A;
        color: white;
        border: 1px solid #4C7BD9;
    }
    QToolTip {
        background-color: #283A5A;
        color: white;
        border: 1px solid #4C7BD9;
        padding: 2px;
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background-color: #1E2B3C;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #4C7BD9;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #5E8DE5;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# Стиль для холста подмодуля в синей теме
SCRIPT_SUBMODULE_CANVAS_STYLE = """
    background-color: #283A5A;
    border-radius: 4px;
    border: 1px solid #4C7BD9;
    padding: 0;  /* Убираем внутренние отступы */
    margin: 0;   /* Убираем внешние отступы */
"""

# Стиль для элемента в холсте подмодуля
SCRIPT_SUBMODULE_ITEM_STYLE = """
    QFrame {
        background-color: #354967;
        border: 1px solid #4C7BD9;
        border-radius: 3px;
        margin: 2px;
    }
    QFrame:hover {
        border: 1px solid #89B4FF;
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
        background-color: rgba(76, 123, 217, 0.3);
        border-radius: 2px;
    }
"""

# Стиль для кнопок в холсте подмодуля
SCRIPT_SUBMODULE_BUTTON_STYLE = """
    QPushButton {
        background-color: #4C7BD9;
        color: white;
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5E8DE5;
    }
"""

# Стиль для заголовка модуля активности
ACTIVITY_MODULE_TITLE_STYLE = "color: #FFA500; font-size: 14px; font-weight: bold; margin-bottom: 8px;"