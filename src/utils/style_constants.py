"""
Модуль содержит константы стилей для всего приложения.
Это позволяет унифицировать внешний вид и уменьшить дублирование кода.
"""

# ======== ОСНОВНЫЕ ЦВЕТА И ПЕРЕМЕННЫЕ ========

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

# ======== ОБЩИЕ ПЕРЕМЕННЫЕ ДЛЯ СТИЛЕЙ ========

BORDER_RADIUS = "4px"
PADDING_STANDARD = "6px 10px"
PADDING_SMALL = "4px"
FONT_WEIGHT_BOLD = "font-weight: bold;"

# ======== БАЗОВЫЕ СТИЛИ КОМПОНЕНТОВ ========

# Общий стиль для оранжевых кнопок
BASE_ORANGE_BUTTON = f"""
    background-color: {COLOR_PRIMARY};
    color: black;
    border-radius: {BORDER_RADIUS};
    padding: {PADDING_STANDARD};
    {FONT_WEIGHT_BOLD}
"""

# Общий стиль для темных кнопок
BASE_DARK_BUTTON = f"""
    background-color: {COLOR_BG_DARK_2};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_TEXT};
    border-radius: 3px;
    padding: 5px 10px;
"""

# Общий стиль для полей ввода
BASE_INPUT = f"""
    background-color: {COLOR_BG_DARK_2}; 
    color: {COLOR_TEXT}; 
    padding: {PADDING_SMALL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
"""

# Общий стиль для фреймов
BASE_FRAME = f"""
    background-color: {COLOR_BG_DARK_1}; 
    border-radius: 8px;
    border: 1px solid {COLOR_BORDER};
"""

# Общий стиль для группбоксов
BASE_GROUP_BOX = f"""
    {FONT_WEIGHT_BOLD}
    color: {COLOR_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: {BORDER_RADIUS};
    margin-top: 8px;
    padding-top: 8px;
"""

# Общий стиль для подсказок
BASE_TOOLTIP = f"""
    background-color: {COLOR_BG_DARK_2};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_PRIMARY};
    padding: 2px;
"""

# Общий стиль для кнопок инструментов
BASE_TOOL_BUTTON = f"""
    background-color: transparent;
    border: none;
    color: {COLOR_TEXT};
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
"""

# ======== КОНКРЕТНЫЕ СТИЛИ КОМПОНЕНТОВ ========

# Стили для диалогов
BASE_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLOR_BG_DARK_1};
        color: {COLOR_TEXT};
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QGroupBox {{
        {BASE_GROUP_BOX}
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
    }}
    QToolTip {{
        {BASE_TOOLTIP}
        opacity: 200;
    }}
"""

# Стили для кнопок
BASE_BUTTON_STYLE = f"""
    QPushButton {{
        {BASE_ORANGE_BUTTON}
    }}
    QPushButton:hover {{
        background-color: {COLOR_WARNING};
    }}
"""

DARK_BUTTON_STYLE = f"""
    QPushButton {{
        {BASE_DARK_BUTTON}
    }}
    QPushButton:hover {{
        background-color: {COLOR_BG_DARK_3};
    }}
"""

DELETE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_ERROR};
        color: {COLOR_TEXT};
        border-radius: {BORDER_RADIUS};
        padding: {PADDING_STANDARD};
    }}
    QPushButton:hover {{
        background-color: #FF6666;
    }}
"""

# Стили для полей ввода
BASE_INPUT_STYLE = f"""
    {BASE_INPUT}
    min-height: 22px;
    max-height: 22px;
"""

# Стили для спинбоксов
BASE_SPINBOX_STYLE = f"""
    {BASE_INPUT}
    min-height: 22px;
    max-height: 22px;
"""

# Стили для комбобоксов
BASE_COMBOBOX_STYLE = f"""
    QComboBox {{
        {BASE_INPUT}
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_PRIMARY};
    }}
"""

# Стили для таблиц
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
MAIN_FRAME_STYLE = BASE_FRAME

# Стиль для подсказок
TOOLTIP_STYLE = f"""
    QToolTip {{
        {BASE_TOOLTIP}
    }}
"""

# ======== СТИЛИ ЭЛЕМЕНТОВ ИНТЕРФЕЙСА ========

# Заголовок
TITLE_STYLE = f"""
    color: {COLOR_PRIMARY};
    font-size: 16px;
    {FONT_WEIGHT_BOLD}
"""

# Стили для боковой панели
SIDEBAR_STYLE = f"""
    background-color: #121212;
    border-right: 2px solid {COLOR_BG_DARK_3};
"""

SIDEBAR_BUTTON_BASE = f"""
    color: {COLOR_TEXT};
    border: none;
    text-align: left;
    padding: 5px 10px;
    border-radius: 5px;
"""

SIDEBAR_BUTTON_STYLE = f"""
    QPushButton {{
        {SIDEBAR_BUTTON_BASE}
        background: transparent;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
"""

SIDEBAR_ACTIVE_BUTTON_STYLE = f"""
    QPushButton {{
        {SIDEBAR_BUTTON_BASE}
        background-color: rgba(255, 255, 255, 0.15);
        {FONT_WEIGHT_BOLD}
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

# Обновленный стиль акцентных кнопок (используем базовый)
ACCENT_BUTTON_STYLE = BASE_BUTTON_STYLE

# Стиль для кнопок в диалогах модулей (используем базовый)
MODULE_BUTTON_STYLE = BASE_BUTTON_STYLE

# Стиль для групп в форме
FORM_GROUP_STYLE = f"""
    QGroupBox {{
        {BASE_GROUP_BOX}
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
        color: {COLOR_PRIMARY};
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
"""

# Стиль для элементов ModuleItem
MODULE_ITEM_STYLE = f"""
    ModuleItem {{
        background-color: {COLOR_BG_DARK_2};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        margin: 2px;
    }}
    ModuleItem:hover {{
        border: 1px solid {COLOR_PRIMARY};
    }}
    QLabel {{
        color: {COLOR_TEXT};
        padding: 2px;
    }}
    QToolButton {{
        {BASE_TOOL_BUTTON}
        icon-size: 16px;
        padding: 1px;
    }}
    QToolButton:hover {{
        background-color: rgba(255, 165, 0, 0.2);
        border-radius: 2px;
    }}
"""

# Стиль для кнопок инструментов
TOOL_BUTTON_STYLE = f"""
    QToolButton {{
        {BASE_TOOL_BUTTON}
    }}
    QToolButton:hover {{
        background-color: rgba(255, 165, 0, 0.2);
        border-radius: 2px;
    }}
"""

# Стиль для холста модулей активности
ACTIVITY_CANVAS_STYLE = f"""
    background-color: #252525;
    border-radius: 4px;
    border: 1px solid {COLOR_BORDER_LIGHT};
"""

# Стиль для диалога активности
ACTIVITY_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QGroupBox {{
        {FONT_WEIGHT_BOLD}
        color: {COLOR_PRIMARY};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 4px;
        margin-top: 15px;
        padding-top: 15px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
    QLineEdit, QSpinBox, QDoubleSpinBox {{
        background-color: #333;
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
    }}
    QComboBox {{
        background-color: #333;
        color: {COLOR_TEXT}; 
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        padding: 4px;
    }}
    QPushButton {{
        {BASE_ORANGE_BUTTON}
    }}
    QPushButton:hover {{
        background-color: {COLOR_WARNING};
    }}
    QCheckBox {{
        color: {COLOR_TEXT};
        spacing: 5px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
    }}
    QToolTip {{
        {BASE_TOOLTIP}
        opacity: 200;
    }}
"""

# Стиль для страницы создания бота
CREATE_BOT_STYLE = f"""
    QWidget#createBotPage {{
        background-color: {COLOR_BG_DARK};
    }}
"""

# Стиль для кнопок в таблице
TABLE_ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: #222222;
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_TEXT};
        border-radius: 2px;
        padding: 4px 8px;
    }}
    QPushButton:hover {{
        background-color: #333333;
    }}
"""

# ======== СТИЛИ ДЛЯ СКРИПТОВ ========

# Стиль для элементов скрипта
SCRIPT_ITEM_STYLE = f"""
    QFrame {{
        background-color: {COLOR_BG_DARK_2};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        margin: 2px;
    }}
    QFrame:hover {{
        border: 1px solid {COLOR_PRIMARY};
    }}
"""

# Стиль для заголовка элемента скрипта
SCRIPT_ITEM_HEADER_STYLE = f"""
    color: {COLOR_PRIMARY}; 
    {FONT_WEIGHT_BOLD}
"""

# Стиль для описания элемента скрипта
SCRIPT_ITEM_DESCRIPTION_STYLE = f"""
    color: {COLOR_TEXT_SECONDARY}; 
    font-size: 11px; 
    margin-left: 24px;
"""

# Стиль для кнопок в элементе скрипта
SCRIPT_ITEM_BUTTON_STYLE = f"""
    QToolButton {{
        {BASE_TOOL_BUTTON}
    }}
    QToolButton:hover {{
        background-color: rgba(255, 165, 0, 0.2);
        border-radius: 2px;
    }}
"""

# Стиль для кнопки удаления в элементе скрипта
SCRIPT_ITEM_DELETE_BUTTON_STYLE = f"""
    QToolButton {{
        {BASE_TOOL_BUTTON}
        color: {COLOR_ERROR};
    }}
    QToolButton:hover {{
        background-color: rgba(255, 68, 68, 0.2);
        border-radius: 2px;
    }}
"""

# Стиль для холста скрипта
SCRIPT_CANVAS_STYLE = f"""
    background-color: #252525; 
    border-radius: 3px; 
    border: 1px solid {COLOR_BORDER_LIGHT};
"""

# Стиль для кнопки отмены (красная)
CANCEL_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_ERROR};
        color: {COLOR_TEXT};
        border-radius: 3px;
        padding: 5px 10px;
        {FONT_WEIGHT_BOLD}
    }}
    QPushButton:hover {{
        background-color: #FF6666;
    }}
"""

# Стиль для кнопки подтверждения (зеленая)
CONFIRM_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_SUCCESS};
        color: {COLOR_TEXT};
        border-radius: 3px;
        padding: 5px 10px;
        {FONT_WEIGHT_BOLD}
    }}
    QPushButton:hover {{
        background-color: #66CC66;
    }}
"""

# Стиль для панели кнопок
BUTTONS_PANEL_STYLE = f"""
    QFrame {{
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 4px;
        padding: 5px;
        margin-top: 10px;
        background-color: {COLOR_BG_DARK_2};
    }}
"""

# Стиль для компактной секции настроек изображений
COMPACT_IMAGE_SETTINGS_STYLE = f"""
    QGroupBox {{
        {FONT_WEIGHT_BOLD}
        color: {COLOR_PRIMARY};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 16px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
        color: {COLOR_PRIMARY};
    }}
    QLabel {{
        color: {COLOR_TEXT};
        margin: 2px;
    }}
    QHBoxLayout {{
        margin: 2px;
        spacing: 4px;
    }}
"""

# ======== СТИЛИ ДЛЯ СИНЕЙ ТЕМЫ ========

# Базовый синий стиль
BASE_BLUE_STYLE = f"""
    background-color: {COLOR_BLUE_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BLUE_ACCENT};
"""

# Базовая синяя кнопка
BASE_BLUE_BUTTON = f"""
    background-color: {COLOR_BLUE_ACCENT};
    color: {COLOR_TEXT};
    border-radius: 4px;
    padding: 8px 16px;
    {FONT_WEIGHT_BOLD}
"""

# Стиль для диалогов скрипт-блоков с синей темой
SCRIPT_DIALOG_BLUE_STYLE = f"""
    QDialog {{
        background-color: {COLOR_BLUE_BG};
        border: 2px solid {COLOR_BLUE_ACCENT};
    }}
    QPushButton {{
        {BASE_BLUE_BUTTON}
    }}
    QPushButton:hover {{
        background-color: {COLOR_BLUE_HIGHLIGHT};
    }}
    QGroupBox {{
        border: 1px solid {COLOR_BLUE_ACCENT};
        color: {COLOR_BLUE_TEXT};
        {FONT_WEIGHT_BOLD}
        margin-top: 15px;
        padding-top: 15px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QLineEdit, QComboBox {{
        background-color: {COLOR_BLUE_BG_LIGHT};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BLUE_ACCENT};
        border-radius: 3px;
        padding: 4px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BLUE_BG_LIGHT};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BLUE_ACCENT};
    }}
    QToolTip {{
        background-color: {COLOR_BLUE_BG_LIGHT};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BLUE_ACCENT};
        padding: 2px;
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: {COLOR_BLUE_BG};
        width: 12px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLOR_BLUE_ACCENT};
        min-height: 20px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLOR_BLUE_HIGHLIGHT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# Стиль для холста подмодуля в синей теме
SCRIPT_SUBMODULE_CANVAS_STYLE = f"""
    background-color: {COLOR_BLUE_BG_LIGHT};
    border-radius: 4px;
    border: 1px solid {COLOR_BLUE_ACCENT};
    padding: 0;
    margin: 0;
"""

# Стиль для элемента в холсте подмодуля
SCRIPT_SUBMODULE_ITEM_STYLE = f"""
    QFrame {{
        background-color: #354967;
        border: 1px solid {COLOR_BLUE_ACCENT};
        border-radius: 3px;
        margin: 2px;
    }}
    QFrame:hover {{
        border: 1px solid {COLOR_BLUE_TEXT};
    }}
    QLabel {{
        color: {COLOR_TEXT};
        padding: 2px;
    }}
    QToolButton {{
        {BASE_TOOL_BUTTON}
        icon-size: 16px;
        padding: 1px;
    }}
    QToolButton:hover {{
        background-color: rgba(76, 123, 217, 0.3);
        border-radius: 2px;
    }}
"""

# Стиль для кнопок в холсте подмодуля
SCRIPT_SUBMODULE_BUTTON_STYLE = f"""
    QPushButton {{
        {BASE_BLUE_BUTTON}
    }}
    QPushButton:hover {{
        background-color: {COLOR_BLUE_HIGHLIGHT};
    }}
"""

CANVAS_MODULE_STYLE = f"""
    CanvasModule {{
        background-color: {COLOR_BG_DARK_1};
        border: 1px solid {COLOR_BORDER};
        border-radius: 5px;
    }}
"""

SETTINGS_CHECKBOX_STYLE = f"""
    QCheckBox {{
        color: {COLOR_TEXT};
        spacing: 5px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid #888;
        border-radius: 3px;
        background-color: {COLOR_BG_DARK_3};
    }}
    QCheckBox::indicator:unchecked {{
        background-color: {COLOR_BG_DARK_3};
        border: 1px solid {COLOR_PRIMARY};
    }}
"""

SCHEDULE_CONTAINER_STYLE = f"""
    #scheduleContainer {{
        background-color: {COLOR_BG_DARK_3};
        border-radius: 4px;
        padding: 4px;
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
"""

DATETIME_EDIT_STYLE = f"""
    QDateTimeEdit {{
        background-color: {COLOR_BG_DARK_3};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        padding: 4px;
    }}
    /* Стиль для календаря и связанных элементов */
    QCalendarWidget {{
        background-color: #2D2D30;
        color: {COLOR_TEXT};
    }}
    QCalendarWidget QToolButton {{
        color: {COLOR_TEXT};
        background-color: #3A3A3D;
        border: 1px solid #505054;
        border-radius: 3px;
    }}
    QCalendarWidget QMenu {{
        color: {COLOR_TEXT};
        background-color: #2D2D30;
    }}
    QCalendarWidget QSpinBox {{
        color: {COLOR_TEXT};
        background-color: #3A3A3D;
        selection-background-color: #3A6EA5;
        selection-color: {COLOR_TEXT};
    }}
    QCalendarWidget QTableView {{
        alternate-background-color: #3E3E42;
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {COLOR_TEXT};
        background-color: #2D2D30;
        selection-background-color: #3A6EA5;
        selection-color: {COLOR_TEXT};
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: #777777;
    }}
    QCalendarWidget QWidget {{ 
        background-color: #2D2D30;
        color: {COLOR_TEXT};
    }}
"""

MANAGER_QUEUE_WIDGET_STYLE = f"""
    QTreeView {{
        background-color: #2D2D30;
        color: {COLOR_TEXT};
        alternate-row-colors: true;
        gridline-color: {COLOR_BORDER};
        border: none;
    }}
    QTreeView::item {{
        padding: 6px 0;
        border-bottom: 1px solid #3E3E42;
    }}
    /* Стиль для родительских элементов (ботов) */
    QTreeView::item:has-children {{
        background-color: #3A3A3D;
        font-weight: bold;
        border-bottom: 1px solid #505054;
    }}
    /* Стиль для дочерних элементов (эмуляторов) */
    QTreeView::branch:has-children:!has-siblings:closed,
    QTreeView::branch:closed:has-children:has-siblings {{
        border-image: none;
        image: url(assets/icons/expand-white.svg);
    }}
    QTreeView::branch:open:has-children:!has-siblings,
    QTreeView::branch:open:has-children:has-siblings {{
        border-image: none;
        image: url(assets/icons/collapse-white.svg);
    }}
    QTreeView::item:selected {{
        background-color: #3A6EA5;
        color: {COLOR_TEXT};
    }}
    QTreeView::item:hover {{
        background-color: #2C5175;
    }}
    /* Исправление стилей подсказок и контекстного меню */
    QToolTip {{
        background-color: #2D2D30;
        color: {COLOR_TEXT};
        border: 1px solid #3E3E42;
        padding: 2px;
    }}
    QMenu {{
        background-color: #2D2D30;
        color: {COLOR_TEXT};
        border: 1px solid #3E3E42;
    }}
    QMenu::item {{
        padding: 5px 18px 5px 30px;
    }}
    QMenu::item:selected {{
        background-color: #3A6EA5;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: #3E3E42;
        margin: 4px 0px;
    }}
    /* Стиль для календаря и связанных элементов */
    QCalendarWidget {{
        background-color: #2D2D30;
        color: {COLOR_TEXT};
    }}
    QCalendarWidget QToolButton {{
        color: {COLOR_TEXT};
        background-color: #3A3A3D;
        border: 1px solid #505054;
        border-radius: 3px;
    }}
    QCalendarWidget QMenu {{
        color: {COLOR_TEXT};
        background-color: #2D2D30;
    }}
    QCalendarWidget QSpinBox {{
        color: {COLOR_TEXT};
        background-color: #3A3A3D;
        selection-background-color: #3A6EA5;
        selection-color: {COLOR_TEXT};
    }}
    QCalendarWidget QTableView {{
        alternate-background-color: #3E3E42;
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {COLOR_TEXT};
        background-color: #2D2D30;
        selection-background-color: #3A6EA5;
        selection-color: {COLOR_TEXT};
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: #777777;
    }}
"""

BLUE_SPINNER_STYLE = f"""
    background-color: {COLOR_BLUE_BG_LIGHT};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BLUE_ACCENT};
"""

BLUE_BUTTON_PANEL_STYLE = f"""
    QFrame {{
        border-top: 1px solid {COLOR_BLUE_ACCENT};
        margin-top: 10px;
        padding-top: 10px;
    }}
"""

IMAGE_SEARCH_DIALOG_STYLE = f"""
    QDialog {{
        background-color: #202020;
        color: {COLOR_TEXT};
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QGroupBox {{
        font-weight: bold;
        color: {COLOR_PRIMARY};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 6px;
        padding: 0 3px;
    }}
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        padding: 4px;
        selection-background-color: {COLOR_PRIMARY};
    }}
    QComboBox {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 3px;
        padding: 4px;
        selection-background-color: {COLOR_PRIMARY};
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        selection-background-color: {COLOR_PRIMARY};
    }}
    QPushButton {{
        background-color: {COLOR_PRIMARY};
        color: black;
        border-radius: 3px;
        padding: 4px 8px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLOR_WARNING};
    }}
    QTableWidget {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        gridline-color: {COLOR_BORDER_LIGHT};
        border: none;
    }}
    QHeaderView::section {{
        background-color: #333;
        color: {COLOR_PRIMARY};
        padding: 4px;
        border: 1px solid {COLOR_BORDER_LIGHT};
    }}
    QToolTip {{
        background-color: {COLOR_BG_DARK_2};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_PRIMARY};
        padding: 2px;
        opacity: 200;
    }}
    /* Для ScrollArea */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: {COLOR_BG_DARK_2};
        width: 12px;
        margin: 0px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background-color: #555;
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLOR_PRIMARY};
    }}
    QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
        height: 0px;
    }}
"""

MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {COLOR_BG_DARK};
    }}
"""

# Стиль для заголовка модуля активности
ACTIVITY_MODULE_TITLE_STYLE = f"color: {COLOR_PRIMARY}; font-size: 14px; {FONT_WEIGHT_BOLD} margin-bottom: 8px;"

# Обратная совместимость для старых имен
MODULE_DIALOG_STYLE = BASE_DIALOG_STYLE
TABLE_STYLE = BASE_TABLE_STYLE
SETTINGS_BUTTON_STYLE = BASE_BUTTON_STYLE