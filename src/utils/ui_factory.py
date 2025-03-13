"""
Фабрика для создания стандартных UI-компонентов.
Использует унифицированный подход с параметрами типа для уменьшения дублирования кода.
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


# ======== УНИФИЦИРОВАННЫЕ ФУНКЦИИ СОЗДАНИЯ ВИДЖЕТОВ ========

def create_label(text, style=None, font_size=None, bold=False, color=None, is_title=False, align=None):
    """
    Универсальная функция для создания меток различных типов.

    Args:
        text: Текст метки
        style: CSS-стиль (опционально)
        font_size: Размер шрифта (опционально)
        bold: Сделать шрифт жирным (опционально)
        color: Цвет текста (опционально)
        is_title: Создать заголовок (опционально)
        align: Выравнивание текста (опционально)

    Returns:
        QLabel: Созданная метка
    """
    label = QLabel(text)

    if is_title:
        # Если это заголовок, используем стиль заголовка
        label.setStyleSheet(TITLE_STYLE)
        if font_size:
            label.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
    elif style:
        label.setStyleSheet(style)
    elif font_size or bold or color:
        # Создаем стиль на основе параметров
        style_parts = []

        if color:
            style_parts.append(f"color: {color};")

        if font_size:
            style_parts.append(f"font-size: {font_size}px;")

        if bold:
            style_parts.append("font-weight: bold;")

        label.setStyleSheet(" ".join(style_parts))

    # Устанавливаем выравнивание, если указано
    if align:
        label.setAlignment(align)

    return label


def create_button(text, style_type=None, style=None, icon_path=None,
                  callback=None, tooltip=None):
    """
    Универсальная функция для создания кнопок различных типов.

    Args:
        text: Текст кнопки
        style_type: Тип стиля ("default", "accent", "dark", "delete")
        style: CSS-стиль (опционально)
        icon_path: Путь к иконке или объект QIcon (опционально)
        callback: Функция обратного вызова (опционально)
        tooltip: Подсказка (опционально)

    Returns:
        QPushButton: Созданная кнопка
    """
    button = QPushButton(text)

    # Выбираем стиль на основе типа
    if style:
        button.setStyleSheet(style)
    elif style_type:
        styles = {
            "default": BASE_BUTTON_STYLE,
            "accent": BASE_BUTTON_STYLE,  # То же самое что и default
            "dark": DARK_BUTTON_STYLE,
            "delete": DELETE_BUTTON_STYLE
        }
        button.setStyleSheet(styles.get(style_type, BASE_BUTTON_STYLE))

    # Добавляем иконку, если указана
    if icon_path:
        if isinstance(icon_path, str):
            button.setIcon(QIcon(icon_path))
        else:
            button.setIcon(icon_path)  # Если передан уже QIcon

    # Подключаем обработчик события, если указан
    if callback:
        button.clicked.connect(callback)

    # Устанавливаем подсказку, если указана
    if tooltip:
        button.setToolTip(tooltip)

    return button


def create_tool_button(text="", tooltip=None, callback=None, icon_path=None, style=None):
    """
    Создает кнопку инструмента.

    Args:
        text: Текст кнопки (опционально)
        tooltip: Подсказка (опционально)
        callback: Функция обратного вызова (опционально)
        icon_path: Путь к иконке или объект QIcon (опционально)
        style: CSS-стиль (опционально)

    Returns:
        QToolButton: Созданная кнопка инструмента
    """
    button = QToolButton()

    # Устанавливаем текст, если указан
    if text:
        button.setText(text)

    # Устанавливаем подсказку, если указана
    if tooltip:
        button.setToolTip(tooltip)

    # Добавляем иконку, если указана
    if icon_path:
        if isinstance(icon_path, str):
            button.setIcon(QIcon(icon_path))
        else:
            button.setIcon(icon_path)  # Если передан уже QIcon

    # Подключаем обработчик события, если указан
    if callback:
        button.clicked.connect(callback)

    # Устанавливаем стиль
    button.setStyleSheet(style or TOOL_BUTTON_STYLE)

    return button


def create_frame(style=None):
    """
    Создает фрейм с заданным стилем.

    Args:
        style: CSS-стиль (опционально)

    Returns:
        QFrame: Созданный фрейм
    """
    frame = QFrame()

    # Устанавливаем стиль
    frame.setStyleSheet(style or MAIN_FRAME_STYLE)

    return frame


def create_input_field(placeholder="", default_text="", style=None, read_only=False):
    """
    Создает поле ввода с указанными параметрами.

    Args:
        placeholder: Текст-подсказка (опционально)
        default_text: Начальный текст (опционально)
        style: CSS-стиль (опционально)
        read_only: Только для чтения (опционально)

    Returns:
        QLineEdit: Созданное поле ввода
    """
    field = QLineEdit()

    # Устанавливаем стиль
    field.setStyleSheet(style or BASE_INPUT_STYLE)

    # Устанавливаем текст-подсказку, если указан
    if placeholder:
        field.setPlaceholderText(placeholder)

    # Устанавливаем начальный текст, если указан
    if default_text:
        field.setText(default_text)

    # Устанавливаем режим только для чтения, если указан
    if read_only:
        field.setReadOnly(True)

    return field


def create_spinbox(min_val=0, max_val=100, default=0, suffix=None, prefix=None,
                   decimals=0, step=None, show_buttons=True, style=None):
    """
    Универсальная функция для создания числовых спиннеров.

    Args:
        min_val: Минимальное значение
        max_val: Максимальное значение
        default: Начальное значение
        suffix: Суффикс (опционально)
        prefix: Префикс (опционально)
        decimals: Количество знаков после запятой
        step: Шаг изменения значения (опционально)
        show_buttons: Показывать кнопки +/- (опционально)
        style: CSS-стиль (опционально)

    Returns:
        QSpinBox или QDoubleSpinBox: Созданный спиннер
    """
    # Выбираем тип спиннера в зависимости от decimals
    if decimals > 0:
        spinner = QDoubleSpinBox()
        spinner.setDecimals(decimals)
        spinner.setSingleStep(step if step else 0.1)
    else:
        spinner = QSpinBox()
        spinner.setSingleStep(step if step else 1)

    # Устанавливаем диапазон значений
    spinner.setRange(min_val, max_val)
    spinner.setValue(default)

    # Устанавливаем суффикс, если указан
    if suffix:
        spinner.setSuffix(suffix)

    # Устанавливаем префикс, если указан
    if prefix:
        spinner.setPrefix(prefix)

    # Скрываем кнопки, если указано
    if not show_buttons:
        spinner.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    # Устанавливаем стиль
    spinner.setStyleSheet(style or BASE_SPINBOX_STYLE)

    return spinner


def create_combobox(items=None, default_index=0, style=None, editable=False):
    """
    Создает выпадающий список с заданными параметрами.

    Args:
        items: Список элементов (опционально)
        default_index: Индекс выбранного по умолчанию элемента (опционально)
        style: CSS-стиль (опционально)
        editable: Разрешить редактирование (опционально)

    Returns:
        QComboBox: Созданный выпадающий список
    """
    combo = QComboBox()

    # Устанавливаем стиль
    combo.setStyleSheet(style or BASE_COMBOBOX_STYLE)

    # Добавляем элементы, если указаны
    if items:
        combo.addItems(items)
        if 0 <= default_index < len(items):
            combo.setCurrentIndex(default_index)

    # Разрешаем редактирование, если указано
    if editable:
        combo.setEditable(True)

    return combo


def create_group_box(title, style=None):
    """
    Создает группировочный бокс с заголовком и стилем.

    Args:
        title: Заголовок группы
        style: CSS-стиль (опционально)

    Returns:
        QGroupBox: Созданный группировочный бокс
    """
    group = QGroupBox(title)

    # Устанавливаем стиль, если указан
    if style:
        group.setStyleSheet(style)

    return group


def create_table(columns=None, style=None, selectable=True, sortable=False, headers_visible=True):
    """
    Создает таблицу с заданными параметрами.

    Args:
        columns: Список заголовков столбцов (опционально)
        style: CSS-стиль (опционально)
        selectable: Разрешить выделение (опционально)
        sortable: Разрешить сортировку (опционально)
        headers_visible: Показывать заголовки (опционально)

    Returns:
        QTableWidget: Созданная таблица
    """
    if columns is None:
        columns = []

    # Создаем таблицу с указанным количеством столбцов
    table = QTableWidget(0, len(columns))

    # Устанавливаем заголовки столбцов, если указаны
    if columns:
        table.setHorizontalHeaderLabels(columns)

    # Устанавливаем стиль
    table.setStyleSheet(style or BASE_TABLE_STYLE)

    # Скрываем заголовки строк
    table.verticalHeader().setVisible(headers_visible)

    # Настраиваем выделение
    if not selectable:
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

    # Настраиваем сортировку
    table.setSortingEnabled(sortable)

    return table


# ======== СПЕЦИАЛИЗИРОВАННЫЕ ФУНКЦИИ (ОБОЛОЧКИ) ========

def create_title_label(text, font_size=16):
    """Создает заголовок с акцентным стилем"""
    return create_label(text, is_title=True, font_size=font_size)


def create_accent_button(text, icon_path=None, callback=None, tooltip=None):
    """Создает кнопку с акцентным стилем (оранжевый фон)"""
    return create_button(text, style_type="accent", icon_path=icon_path, callback=callback, tooltip=tooltip)


def create_dark_button(text, icon_path=None, callback=None, tooltip=None):
    """Создает темную кнопку с белой рамкой"""
    return create_button(text, style_type="dark", icon_path=icon_path, callback=callback, tooltip=tooltip)


def create_delete_button(text="Удалить", callback=None, tooltip="Удалить элемент"):
    """Создает красную кнопку удаления"""
    return create_button(text, style_type="delete", callback=callback, tooltip=tooltip)


def create_spinbox_without_buttons(min_val=0, max_val=100, default=0, suffix=None):
    """Создает числовой спиннер без кнопок +/-"""
    return create_spinbox(min_val, max_val, default, suffix, show_buttons=False)


def create_double_spinbox_without_buttons(min_val=0.0, max_val=100.0, default=0.0,
                                          decimals=1, suffix=None):
    """Создает числовой спиннер с плавающей точкой без кнопок +/-"""
    return create_spinbox(min_val, max_val, default, suffix, decimals=decimals, show_buttons=False)


def create_main_frame():
    """Создает основной фрейм с темным фоном и рамкой"""
    return create_frame(MAIN_FRAME_STYLE)


def create_text_label(text, style=None):
    """Создает текстовую метку с заданным стилем"""
    return create_label(text, style)


def create_command_button(text, tooltip, icon_path=None, callback=None):
    """
    Создает кнопку команды для панелей инструментов.
    """
    custom_style = """
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
    """
    return create_button(text, style=custom_style, icon_path=icon_path, callback=callback, tooltip=tooltip)


def create_script_button(text, tooltip=None, icon_path=None, callback=None):
    """
    Создает кнопку для панели инструментов в скрипте.
    """
    custom_style = """
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

    # Получаем полный путь к иконке, если указан
    if icon_path:
        icon_path = Resources.get_icon_path(icon_path)

    return create_button(text, style=custom_style, icon_path=icon_path, callback=callback, tooltip=tooltip)


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


# ======== ФУНКЦИИ ДЛЯ РАБОТЫ С ЭЛЕМЕНТАМИ СКРИПТА ========

def create_script_item_widget(index, item_type, description, data, parent=None):
    """
    Создает виджет элемента скрипта для использования в холсте скрипта.
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