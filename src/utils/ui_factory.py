"""
Фабрика для создания стандартных UI-компонентов.
Позволяет унифицировать создание часто используемых элементов интерфейса.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFrame, QTableWidget, QHeaderView, QComboBox,
    QCheckBox, QToolButton, QFileDialog
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from src.utils.style_constants import (
    COLOR_PRIMARY, COLOR_BG_DARK_2, COLOR_TEXT, COLOR_BORDER,
    TITLE_STYLE, BASE_BUTTON_STYLE, DARK_BUTTON_STYLE,
    DELETE_BUTTON_STYLE, TOOL_BUTTON_STYLE,
    BASE_INPUT_STYLE, BASE_SPINBOX_STYLE, MAIN_FRAME_STYLE,
    BASE_COMBOBOX_STYLE, BASE_TABLE_STYLE
)
from src.utils.resources import Resources


def create_label(text, style=None, font_size=None, bold=False, color=None):
    """
    Создает метку с заданным стилем.
    """
    label = QLabel(text)

    if style:
        label.setStyleSheet(style)
    elif font_size or bold or color:
        style_parts = []

        if color:
            style_parts.append(f"color: {color};")

        if font_size:
            style_parts.append(f"font-size: {font_size}px;")

        if bold:
            style_parts.append("font-weight: bold;")

        label.setStyleSheet(" ".join(style_parts))

    return label


def create_title_label(text, font_size=16):
    """Создает заголовок с акцентным стилем"""
    return create_label(text, TITLE_STYLE, font_size=font_size, bold=True, color=COLOR_PRIMARY)


def create_button(text, style=None, icon_path=None, callback=None, tooltip=None):
    """
    Создает кнопку с заданным стилем.
    """
    button = QPushButton(text)

    if style:
        button.setStyleSheet(style)

    if icon_path:
        if isinstance(icon_path, str):
            button.setIcon(QIcon(icon_path))
        else:
            button.setIcon(icon_path)  # Если передан уже QIcon

    if callback:
        button.clicked.connect(callback)

    if tooltip:
        button.setToolTip(tooltip)

    return button


def create_accent_button(text, icon_path=None, callback=None, tooltip=None):
    """Создает кнопку с акцентным стилем (оранжевый фон)"""
    return create_button(text, BASE_BUTTON_STYLE, icon_path, callback, tooltip)


def create_dark_button(text, icon_path=None, callback=None, tooltip=None):
    """Создает темную кнопку с белой рамкой"""
    return create_button(text, DARK_BUTTON_STYLE, icon_path, callback, tooltip)


def create_delete_button(text="Удалить", callback=None, tooltip="Удалить элемент"):
    """Создает красную кнопку удаления"""
    return create_button(text, DELETE_BUTTON_STYLE, callback=callback, tooltip=tooltip)


def create_tool_button(text="", tooltip=None, callback=None, icon_path=None):
    """
    Создает кнопку инструмента.
    """
    button = QToolButton()

    if text:
        button.setText(text)

    if tooltip:
        button.setToolTip(tooltip)

    if icon_path:
        if isinstance(icon_path, str):
            button.setIcon(QIcon(icon_path))
        else:
            button.setIcon(icon_path)

    if callback:
        button.clicked.connect(callback)

    button.setStyleSheet(TOOL_BUTTON_STYLE)

    return button


def create_frame(style=None):
    """
    Создает фрейм с заданным стилем.
    """
    frame = QFrame()

    if style:
        frame.setStyleSheet(style)
    else:
        frame.setStyleSheet(MAIN_FRAME_STYLE)

    return frame


def create_main_frame():
    """Создает основной фрейм с темным фоном и рамкой"""
    return create_frame(MAIN_FRAME_STYLE)


def create_input_field(placeholder="", default_text="", style=None):
    """
    Создает поле ввода с темным фоном.
    """
    field = QLineEdit()

    if style:
        field.setStyleSheet(style)
    else:
        field.setStyleSheet(BASE_INPUT_STYLE)

    if placeholder:
        field.setPlaceholderText(placeholder)

    if default_text:
        field.setText(default_text)

    return field


def create_spinbox(min_val=0, max_val=100, default=0, suffix=None, prefix=None,
                   decimals=0, step=1, show_buttons=True, style=None):
    """
    Создает числовой спиннер.
    """
    if decimals > 0:
        spinner = QDoubleSpinBox()
        spinner.setDecimals(decimals)
        spinner.setSingleStep(step if step else 0.1)
    else:
        spinner = QSpinBox()
        spinner.setSingleStep(step if step else 1)

    spinner.setRange(min_val, max_val)
    spinner.setValue(default)

    if suffix:
        spinner.setSuffix(suffix)

    if prefix:
        spinner.setPrefix(prefix)

    if not show_buttons:
        spinner.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    if style:
        spinner.setStyleSheet(style)
    else:
        spinner.setStyleSheet(BASE_SPINBOX_STYLE)

    return spinner


def create_spinbox_without_buttons(min_val=0, max_val=100, default=0, suffix=None):
    """Создает числовой спиннер без кнопок +/-"""
    return create_spinbox(min_val, max_val, default, suffix, show_buttons=False)


def create_double_spinbox_without_buttons(min_val=0.0, max_val=100.0, default=0.0,
                                          decimals=1, suffix=None):
    """Создает числовой спиннер с плавающей точкой без кнопок +/-"""
    return create_spinbox(min_val, max_val, default, suffix,
                          decimals=decimals, show_buttons=False)


def create_group_box(title, style=None):
    """
    Создает группировочный бокс с заголовком и стилем.
    """
    group = QGroupBox(title)

    if style:
        group.setStyleSheet(style)

    return group


def create_combobox(items=None, default_index=0, style=None):
    """
    Создает выпадающий список с заданным стилем.
    """
    combo = QComboBox()

    if style:
        combo.setStyleSheet(style)
    else:
        combo.setStyleSheet(BASE_COMBOBOX_STYLE)

    if items:
        combo.addItems(items)
        if 0 <= default_index < len(items):
            combo.setCurrentIndex(default_index)

    return combo


def create_table(columns=None, style=None):
    """
    Создает таблицу с заданным стилем.
    """
    if columns is None:
        columns = []

    table = QTableWidget(0, len(columns))

    if columns:
        table.setHorizontalHeaderLabels(columns)

    if style:
        table.setStyleSheet(style)
    else:
        table.setStyleSheet(BASE_TABLE_STYLE)

    table.verticalHeader().setVisible(False)

    return table


def create_multiple_file_dialog(title="Выбрать файлы", filter="Изображения (*.png *.jpg *.jpeg)"):
    """
    Открывает диалог выбора нескольких файлов.
    """
    files, _ = QFileDialog.getOpenFileNames(None, title, "", filter)
    return files


def position_dialog_with_offset(dialog, parent, x_offset=50, y_offset=50):
    """
    Позиционирует диалог со смещением относительно родительского окна.
    """
    if parent:
        parent_pos = parent.pos()
        dialog.move(parent_pos.x() + x_offset, parent_pos.y() + y_offset)








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
    from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
    from src.utils.style_constants import (
        SCRIPT_ITEM_STYLE, SCRIPT_ITEM_HEADER_STYLE,
        SCRIPT_ITEM_DESCRIPTION_STYLE
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

