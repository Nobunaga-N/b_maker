# src/utils/ui_factory.py
"""
Фабрика для создания стандартных UI-компонентов.
Позволяет унифицировать создание часто используемых элементов интерфейса.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFrame, QTableWidget, QHeaderView, QComboBox,
    QCheckBox
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from src.utils.style_constants import (
    ACCENT_BUTTON_STYLE, DELETE_BUTTON_STYLE,
    TITLE_STYLE, MAIN_FRAME_STYLE
)


def create_title_label(text: str, font_size: int = 16) -> QLabel:
    """Создает заголовок с оранжевым текстом и жирным шрифтом"""
    label = QLabel(text)
    label.setStyleSheet(f"color: #FFA500; font-size: {font_size}px; font-weight: bold;")
    return label


def create_accent_button(text: str, icon_path: str = None) -> QPushButton:
    """
    Создает кнопку с акцентным стилем (оранжевый фон).

    Args:
        text: Текст кнопки
        icon_path: Путь к иконке (опционально)

    Returns:
        QPushButton: Стилизованная кнопка
    """
    from src.utils.style_constants import ACCENT_BUTTON_STYLE
    from PyQt6.QtGui import QIcon

    button = QPushButton(text)
    button.setStyleSheet(ACCENT_BUTTON_STYLE)

    if icon_path:
        button.setIcon(QIcon(icon_path))

    return button


def create_delete_button(text: str = "Удалить") -> QPushButton:
    """Создает красную кнопку удаления"""
    button = QPushButton(text)
    button.setStyleSheet(DELETE_BUTTON_STYLE)
    return button


def create_main_frame() -> QFrame:
    """Создает основной фрейм с темным фоном и рамкой"""
    frame = QFrame()
    frame.setStyleSheet(MAIN_FRAME_STYLE)
    return frame


def create_input_field(placeholder: str = "", default_text: str = "") -> QLineEdit:
    """
    Создает поле ввода с темным фоном, плейсхолдером и дефолтным текстом.

    Args:
        placeholder: Текст-подсказка
        default_text: Начальный текст

    Returns:
        QLineEdit: Стилизованное поле ввода
    """
    field = QLineEdit()
    field.setStyleSheet("""
        background-color: #2A2A2A; 
        color: white; 
        padding: 4px;
        border: 1px solid #444;
        border-radius: 3px;
        min-height: 22px;
        max-height: 22px;
    """)

    if placeholder:
        field.setPlaceholderText(placeholder)
    if default_text:
        field.setText(default_text)

    return field


def create_group_box(title: str, style: str = None) -> QGroupBox:
    """
    Создает группировочный бокс с заголовком и стилем.

    Args:
        title: Заголовок группы
        style: Дополнительный CSS-стиль (если None, используется FORM_GROUP_STYLE)

    Returns:
        QGroupBox: Стилизованный объект QGroupBox
    """
    from src.utils.style_constants import FORM_GROUP_STYLE

    group = QGroupBox(title)
    if style:
        group.setStyleSheet(style)
    else:
        group.setStyleSheet(FORM_GROUP_STYLE)
    return group


# Создайте функцию-обертку для создания спиннеров без кнопок в src/utils/ui_factory.py
def create_spinbox_without_buttons(min_val: int = 0, max_val: int = 100, default: int = 0, suffix: str = None) -> QSpinBox:
    """Создает числовой спиннер без кнопок +/-"""
    spinner = QSpinBox()
    spinner.setRange(min_val, max_val)
    spinner.setValue(default)
    if suffix:
        spinner.setSuffix(suffix)
    spinner.setStyleSheet("""
        background-color: #2C2C2C; 
        color: white; 
        padding: 5px;
        border: 1px solid #444;
        border-radius: 4px;
    """)
    # Отключаем кнопки программно
    spinner.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
    return spinner

def create_double_spinbox_without_buttons(min_val: float = 0.0, max_val: float = 100.0,
                                        default: float = 0.0, decimals: int = 1,
                                        suffix: str = None) -> QDoubleSpinBox:
    """Создает числовой спиннер с плавающей точкой без кнопок +/-"""
    spinner = QDoubleSpinBox()
    spinner.setRange(min_val, max_val)
    spinner.setValue(default)
    spinner.setDecimals(decimals)
    if suffix:
        spinner.setSuffix(suffix)
    spinner.setStyleSheet("""
        background-color: #2C2C2C; 
        color: white; 
        padding: 5px;
        border: 1px solid #444;
        border-radius: 4px;
    """)
    # Отключаем кнопки программно
    spinner.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
    return spinner


def create_tool_button(text, tooltip, callback=None, icon_path=None):
    """
    Создает компактную кнопку инструмента с текстом и подсказкой.

    Args:
        text: Текст кнопки
        tooltip: Подсказка при наведении мыши
        callback: Функция обратного вызова (опционально)
        icon_path: Путь к иконке (опционально)

    Returns:
        QToolButton: Стилизованная кнопка инструмента
    """
    from PyQt6.QtWidgets import QToolButton
    from PyQt6.QtGui import QIcon
    from src.utils.style_constants import TOOL_BUTTON_STYLE

    button = QToolButton()
    button.setText(text)
    button.setToolTip(tooltip)

    if icon_path:
        button.setIcon(QIcon(icon_path))

    if callback:
        button.clicked.connect(callback)

    button.setStyleSheet(TOOL_BUTTON_STYLE)

    return button


def create_text_label(text, style=None):
    """
    Создает текстовую метку с заданным стилем.

    Args:
        text: Текст метки
        style: CSS-стиль (опционально)

    Returns:
        QLabel: Стилизованная метка
    """
    from PyQt6.QtWidgets import QLabel

    label = QLabel(text)

    if style:
        label.setStyleSheet(style)

    return label

def create_command_button(text, tooltip, icon_path=None, callback=None):
    """
    Создает кнопку команды для панелей инструментов.

    Args:
        text: Текст кнопки
        tooltip: Подсказка при наведении мыши
        icon_path: Путь к иконке (опционально)
        callback: Функция обратного вызова (опционально)

    Returns:
        QPushButton: Стилизованная кнопка команды
    """
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtGui import QIcon

    button = QPushButton(text)
    button.setToolTip(tooltip)

    if icon_path:
        button.setIcon(QIcon(icon_path))

    if callback:
        button.clicked.connect(callback)

    button.setStyleSheet("""
        QPushButton {
            background-color: #333;
            color: white;
            border-radius: 3px;
            padding: 3px 6px;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #444;
            border: 1px solid #FFA500;
        }
    """)

    return button