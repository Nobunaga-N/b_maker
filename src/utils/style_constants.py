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
        background-color: #FF5722;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }
    QPushButton:hover {
        background-color: #FF7043;
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
        background-color: #FF5722;
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
        background-color: #FF5722;
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
        background-color: #FF5722;
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
        background-color: #FF5722;
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
        background-color: #FF5722;
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
        selection-background-color: #FF5722;
        background-color: #2C2C2C;
        color: white;
    }
"""

# Стиль для акцентных кнопок
ACCENT_BUTTON_STYLE = """
    QPushButton {
        background-color: #FFA500;
        color: #000;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FFB347;
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

# Полный стиль для диалогов (комбинация стилей)
FULL_DIALOG_STYLE = DIALOG_STYLE + CHECKBOX_STYLE + TAB_AND_TABLE_STYLE + SCROLLBAR_STYLE + COMBOBOX_STYLE