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
from src.utils.resources import Resources


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


def create_script_button(text, tooltip=None, icon_path=None, callback=None):
    """
    Создает кнопку для панели инструментов в скрипте.

    Args:
        text: Текст кнопки
        tooltip: Подсказка при наведении мыши (опционально)
        icon_path: Путь к иконке (опционально)
        callback: Функция обратного вызова (опционально)

    Returns:
        QPushButton: Стилизованная кнопка для скрипта
    """
    button = QPushButton(text)

    if tooltip:
        button.setToolTip(tooltip)

    if icon_path:
        button.setIcon(QIcon(Resources.get_icon_path(icon_path)))

    if callback:
        button.clicked.connect(callback)

    button.setStyleSheet("""
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
    """)

    return button


def create_script_item_widget(index, item_type, description, data, parent=None):
    """
    Создает виджет элемента скрипта для использования в холсте скрипта.

    Args:
        index: Индекс элемента
        item_type: Тип элемента
        description: Описание элемента
        data: Данные элемента
        parent: Родительский виджет (опционально)

    Returns:
        QFrame: Стилизованный фрейм элемента скрипта
    """
    from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QToolButton
    from src.utils.style_constants import (
        SCRIPT_ITEM_STYLE, SCRIPT_ITEM_HEADER_STYLE,
        SCRIPT_ITEM_DESCRIPTION_STYLE, SCRIPT_ITEM_BUTTON_STYLE,
        SCRIPT_ITEM_DELETE_BUTTON_STYLE
    )

    # Основной фрейм элемента
    item_frame = QFrame(parent)
    item_frame.setObjectName(f"script_item_{index}")
    item_frame.setStyleSheet(SCRIPT_ITEM_STYLE)

    # Устанавливаем данные как атрибуты
    item_frame.item_type = item_type
    item_frame.item_description = description
    item_frame.item_data = data
    item_frame.item_index = index

    # Основной лейаут
    main_layout = QVBoxLayout(item_frame)
    main_layout.setContentsMargins(6, 6, 6, 6)
    main_layout.setSpacing(4)

    # Верхняя строка с типом и кнопками
    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(4)

    # Индекс элемента
    index_label = QLabel(f"{index + 1}.")
    index_label.setStyleSheet(SCRIPT_ITEM_HEADER_STYLE)
    header_layout.addWidget(index_label)

    # Тип элемента
    type_label = QLabel(item_type)
    type_label.setStyleSheet(SCRIPT_ITEM_HEADER_STYLE)
    header_layout.addWidget(type_label)

    header_layout.addStretch(1)  # Растягиваем между типом и кнопками

    # Сохраняем ссылку на метки для будущего обновления
    item_frame.index_label = index_label

    # Кнопки вернём отдельно, чтобы не усложнять интерфейс функции
    main_layout.addLayout(header_layout)

    # Описание элемента
    desc_label = QLabel(description)
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet(SCRIPT_ITEM_DESCRIPTION_STYLE)
    main_layout.addWidget(desc_label)

    # Сохраняем ссылку на метку описания
    item_frame.desc_label = desc_label

    return item_frame


def add_script_item_buttons(item_frame, edit_callback=None, delete_callback=None,
                            move_up_callback=None, move_down_callback=None):
    """
    Добавляет кнопки управления к элементу скрипта.

    Args:
        item_frame: Фрейм элемента скрипта
        edit_callback: Функция редактирования (опционально)
        delete_callback: Функция удаления (опционально)
        move_up_callback: Функция перемещения вверх (опционально)
        move_down_callback: Функция перемещения вниз (опционально)

    Returns:
        tuple: Кортеж из созданных кнопок (edit_btn, delete_btn, move_up_btn, move_down_btn)
    """
    from PyQt6.QtWidgets import QToolButton
    from src.utils.style_constants import SCRIPT_ITEM_BUTTON_STYLE, SCRIPT_ITEM_DELETE_BUTTON_STYLE

    # Получаем header_layout из первого элемента основного лейаута
    header_layout = item_frame.layout().itemAt(0).layout()

    # Кнопки управления
    move_up_btn = QToolButton()
    move_up_btn.setText("↑")
    move_up_btn.setToolTip("Переместить вверх")
    move_up_btn.setStyleSheet(SCRIPT_ITEM_BUTTON_STYLE)
    if move_up_callback:
        move_up_btn.clicked.connect(move_up_callback)

    move_down_btn = QToolButton()
    move_down_btn.setText("↓")
    move_down_btn.setToolTip("Переместить вниз")
    move_down_btn.setStyleSheet(SCRIPT_ITEM_BUTTON_STYLE)
    if move_down_callback:
        move_down_btn.clicked.connect(move_down_callback)

    edit_btn = QToolButton()
    edit_btn.setText("🖉")
    edit_btn.setToolTip("Редактировать")
    edit_btn.setStyleSheet(SCRIPT_ITEM_BUTTON_STYLE)
    if edit_callback:
        edit_btn.clicked.connect(edit_callback)

    delete_btn = QToolButton()
    delete_btn.setText("✕")
    delete_btn.setToolTip("Удалить")
    delete_btn.setStyleSheet(SCRIPT_ITEM_DELETE_BUTTON_STYLE)
    if delete_callback:
        delete_btn.clicked.connect(delete_callback)

    # Добавляем кнопки в лейаут
    header_layout.addWidget(move_up_btn)
    header_layout.addWidget(move_down_btn)
    header_layout.addWidget(edit_btn)
    header_layout.addWidget(delete_btn)

    return edit_btn, delete_btn, move_up_btn, move_down_btn


def create_action_buttons_panel():
    """
    Создает панель с кнопками "Отмена" и "Подтвердить"
    с правильным стилем и выравниванием вправо.

    Returns:
        Tuple[QFrame, QPushButton, QPushButton]: (панель, кнопка отмены, кнопка подтверждения)
    """
    from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton
    from src.utils.style_constants import CANCEL_BUTTON_STYLE, CONFIRM_BUTTON_STYLE, BUTTONS_PANEL_STYLE

    panel = QFrame()
    panel.setStyleSheet(BUTTONS_PANEL_STYLE)
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(5, 5, 5, 5)

    # Добавляем растяжку слева для выравнивания кнопок вправо
    layout.addStretch(1)

    # Создаем кнопки
    cancel_btn = QPushButton("Отмена")
    cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLE)

    confirm_btn = QPushButton("Подтвердить")
    confirm_btn.setStyleSheet(CONFIRM_BUTTON_STYLE)

    # Добавляем кнопки
    layout.addWidget(cancel_btn)
    layout.addWidget(confirm_btn)

    return panel, cancel_btn, confirm_btn
