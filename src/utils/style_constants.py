"""
Модуль содержит константы стилей для всего приложения.
Использует генераторы стилей для уменьшения дублирования кода.
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

# ======== ГЕНЕРАТОРЫ СТИЛЕЙ ========

def generate_button_style(bg_color, text_color, hover_color=None, border_radius=BORDER_RADIUS,
                          padding=PADDING_STANDARD, font_weight="bold", border="none", extra_css=""):
    """Генерирует стиль для кнопки на основе параметров."""
    hover_color = hover_color or bg_color

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: {border};
            border-radius: {border_radius};
            padding: {padding};
            font-weight: {font_weight};
            {extra_css}
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """

def generate_input_style(bg_color=COLOR_BG_DARK_2, text_color=COLOR_TEXT, border_color=COLOR_BORDER,
                         border_radius="3px", padding=PADDING_SMALL, min_height=None, extra_css=""):
    """Генерирует стиль для текстовых полей и других компонентов ввода."""
    height_css = f"min-height: {min_height}; max-height: {min_height};" if min_height else ""

    return f"""
        background-color: {bg_color}; 
        color: {text_color}; 
        padding: {padding};
        border: 1px solid {border_color};
        border-radius: {border_radius};
        {height_css}
        {extra_css}
    """

def generate_container_style(bg_color, border_color=None, border_radius="8px", padding=None,
                             margin=None, extra_css=""):
    """Генерирует стиль для контейнеров (фреймы, группы и т.д.)."""
    border_css = f"border: 1px solid {border_color};" if border_color else ""
    padding_css = f"padding: {padding};" if padding else ""
    margin_css = f"margin: {margin};" if margin else ""

    return f"""
        background-color: {bg_color}; 
        border-radius: {border_radius};
        {border_css}
        {padding_css}
        {margin_css}
        {extra_css}
    """

def generate_group_box_style(title_color=COLOR_PRIMARY, border_color=COLOR_BORDER,
                           border_radius=BORDER_RADIUS, margin_top="8px", title_position="left",
                           title_offset="6px", extra_css=""):
    """Генерирует стиль для группировочных боксов."""
    return f"""
        {FONT_WEIGHT_BOLD}
        color: {title_color};
        border: 1px solid {border_color};
        border-radius: {border_radius};
        margin-top: {margin_top};
        padding-top: 8px;
        {extra_css}
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        {title_position}: {title_offset};
        padding: 0 3px;
    """

def generate_table_style(bg_color=COLOR_BG_DARK_2, text_color=COLOR_TEXT,
                        grid_color=COLOR_BORDER, header_bg=COLOR_BG_DARK_3,
                        header_color=COLOR_PRIMARY, selected_bg=COLOR_PRIMARY,
                        selected_text=COLOR_TEXT, extra_css=""):
    """Генерирует стиль для таблиц."""
    return f"""
        QTableWidget {{
            background-color: {bg_color};
            color: {text_color};
            gridline-color: {grid_color};
            border: none;
            {extra_css}
        }}
        QHeaderView::section {{
            background-color: {header_bg};
            color: {header_color};
            padding: 5px;
            border: 1px solid {grid_color};
        }}
        QTableWidget::item:selected {{
            background-color: {selected_bg};
            color: {selected_text};
        }}
    """

def generate_tool_button_style(bg_color="transparent", text_color=COLOR_TEXT,
                             hover_bg="rgba(255, 255, 255, 0.1)", hover_radius="3px",
                             size=None, extra_css=""):
    """Генерирует стиль для кнопок инструментов."""
    size_css = f"""
        min-width: {size}px;
        max-width: {size}px;
        min-height: {size}px;
        max-height: {size}px;
    """ if size else ""

    return f"""
        QToolButton {{
            background-color: {bg_color};
            border: none;
            color: {text_color};
            {size_css}
            {extra_css}
        }}
        QToolButton:hover {{
            background-color: {hover_bg};
            border-radius: {hover_radius};
        }}
    """

def generate_combobox_style(bg_color=COLOR_BG_DARK_2, text_color=COLOR_TEXT,
                          border_color=COLOR_BORDER, popup_bg=COLOR_BG_DARK_2,
                          selection_bg=COLOR_PRIMARY, padding=PADDING_SMALL,
                          border_radius="3px", extra_css=""):
    """Генерирует стиль для выпадающих списков."""
    return f"""
        QComboBox {{
            background-color: {bg_color};
            color: {text_color}; 
            padding: {padding};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            {extra_css}
        }}
        QComboBox QAbstractItemView {{
            background-color: {popup_bg};
            color: {text_color};
            border: 1px solid {border_color};
            selection-background-color: {selection_bg};
        }}
    """

def generate_dialog_style(bg_color=COLOR_BG_DARK_1, text_color=COLOR_TEXT,
                        group_title_color=COLOR_PRIMARY, border_color=COLOR_BORDER,
                        tooltip_bg=COLOR_BG_DARK_2, tooltip_border=COLOR_PRIMARY,
                        extra_css=""):
    """Генерирует стиль для диалогов."""
    return f"""
        QDialog {{
            background-color: {bg_color};
            color: {text_color};
            {extra_css}
        }}
        QLabel {{
            color: {text_color};
        }}
        QGroupBox {{
            {generate_group_box_style(group_title_color, border_color)}
        }}
        QToolTip {{
            background-color: {tooltip_bg};
            color: {text_color};
            border: 1px solid {tooltip_border};
            padding: 2px;
            opacity: 200;
        }}
    """

# ======== БАЗОВЫЕ СТИЛИ КОМПОНЕНТОВ ========

# Общий стиль для оранжевых кнопок
BASE_ORANGE_BUTTON = generate_button_style(COLOR_PRIMARY, "black")

# Общий стиль для темных кнопок
BASE_DARK_BUTTON = generate_button_style(COLOR_BG_DARK_2, COLOR_TEXT, COLOR_BG_DARK_3,
                                         border="1px solid " + COLOR_TEXT, border_radius="3px",
                                         padding="5px 10px", font_weight="normal")

# Общий стиль для полей ввода
BASE_INPUT = generate_input_style()

# Общий стиль для фреймов
BASE_FRAME = generate_container_style(COLOR_BG_DARK_1, COLOR_BORDER)

# Общий стиль для группбоксов
BASE_GROUP_BOX = generate_group_box_style()

# Общий стиль для подсказок
BASE_TOOLTIP = f"""
    background-color: {COLOR_BG_DARK_2};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_PRIMARY};
    padding: 2px;
"""

# Общий стиль для кнопок инструментов
BASE_TOOL_BUTTON = generate_tool_button_style(size=20)

# ======== КОНКРЕТНЫЕ СТИЛИ КОМПОНЕНТОВ ========

# Стили для диалогов
BASE_DIALOG_STYLE = generate_dialog_style()

# Стили для кнопок
BASE_BUTTON_STYLE = BASE_ORANGE_BUTTON

DARK_BUTTON_STYLE = BASE_DARK_BUTTON

DELETE_BUTTON_STYLE = generate_button_style(COLOR_ERROR, COLOR_TEXT, "#FF6666")

# Стили для полей ввода
BASE_INPUT_STYLE = generate_input_style(min_height="22px")

# Стили для спинбоксов
BASE_SPINBOX_STYLE = generate_input_style(min_height="22px")

# Стили для комбобоксов
BASE_COMBOBOX_STYLE = generate_combobox_style()

# Стили для таблиц
BASE_TABLE_STYLE = generate_table_style()

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

SIDEBAR_ICON_STYLE = generate_tool_button_style(hover_bg="rgba(255, 255, 255, 0.2)", hover_radius="4px")

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
TOOL_BUTTON_STYLE = BASE_TOOL_BUTTON

# Стиль для холста модулей активности
ACTIVITY_CANVAS_STYLE = generate_container_style("#252525", COLOR_BORDER_LIGHT, "4px")

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
TABLE_ACTION_BUTTON_STYLE = generate_button_style("#222222", COLOR_TEXT, "#333333",
                                                border="1px solid " + COLOR_TEXT,
                                                border_radius="2px", padding="4px 8px",
                                                font_weight="normal")

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
SCRIPT_ITEM_BUTTON_STYLE = generate_tool_button_style(hover_bg="rgba(255, 165, 0, 0.2)", hover_radius="2px")

# Стиль для кнопки удаления в элементе скрипта
SCRIPT_ITEM_DELETE_BUTTON_STYLE = generate_tool_button_style(text_color=COLOR_ERROR,
                                                           hover_bg="rgba(255, 68, 68, 0.2)",
                                                           hover_radius="2px")

# Стиль для холста скрипта
SCRIPT_CANVAS_STYLE = generate_container_style("#252525", COLOR_BORDER_LIGHT, "3px")

# Стиль для кнопки отмены (красная)
CANCEL_BUTTON_STYLE = generate_button_style(COLOR_ERROR, COLOR_TEXT, "#FF6666", "3px", "5px 10px")

# Стиль для кнопки подтверждения (зеленая)
CONFIRM_BUTTON_STYLE = generate_button_style(COLOR_SUCCESS, COLOR_TEXT, "#66CC66", "3px", "5px 10px")

# Стиль для панели кнопок
BUTTONS_PANEL_STYLE = generate_container_style(COLOR_BG_DARK_2, COLOR_BORDER_LIGHT, "4px", "5px", "10px 0 0 0")

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
BASE_BLUE_STYLE = generate_container_style(COLOR_BLUE_BG, COLOR_BLUE_ACCENT, extra_css=f"color: {COLOR_TEXT};")

# Базовая синяя кнопка
BASE_BLUE_BUTTON = generate_button_style(COLOR_BLUE_ACCENT, COLOR_TEXT, COLOR_BLUE_HIGHLIGHT, "4px", "8px 16px")

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
        background-color: transparent;
        border: none;
        color: {COLOR_TEXT};
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
        background-color: {COLOR_BLUE_ACCENT};
        color: {COLOR_TEXT};
        border-radius: 3px;
        padding: 5px 10px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLOR_BLUE_HIGHLIGHT};
    }}
"""

CANVAS_MODULE_STYLE = generate_container_style(COLOR_BG_DARK_1, COLOR_BORDER, "5px")

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

SCHEDULE_CONTAINER_STYLE = generate_container_style(COLOR_BG_DARK_3, border_radius="4px", padding="4px",
                                                 extra_css=f"#scheduleContainer {{ }} QLabel {{ color: {COLOR_TEXT}; }}")

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

BLUE_SPINNER_STYLE = generate_input_style(COLOR_BLUE_BG_LIGHT, COLOR_TEXT, COLOR_BLUE_ACCENT)

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

# Дополнительные стили для manager_page.py
MANAGER_TABLE_HEADER_STYLE = """
    QHeaderView::section {
        background-color: #333333;
        color: #FFA500;
        font-weight: bold;
        font-size: 12px;
        padding: 4px;
    }
"""

MANAGER_QUEUE_STYLE = """
    background-color: #2D2D30;
    alternate-row-colors: true;
    gridline-color: #444444;
"""

MANAGER_NAV_PANEL_STYLE = """
    background-color: #252525;
    border-top: 1px solid #444;
    border-radius: 4px;
    margin-top: 5px;
"""

# Стиль для заголовка модуля активности
ACTIVITY_MODULE_TITLE_STYLE = f"color: {COLOR_PRIMARY}; font-size: 14px; {FONT_WEIGHT_BOLD} margin-bottom: 8px;"

# Обратная совместимость для старых имен
MODULE_DIALOG_STYLE = BASE_DIALOG_STYLE
TABLE_STYLE = BASE_TABLE_STYLE
SETTINGS_BUTTON_STYLE = BASE_BUTTON_STYLE