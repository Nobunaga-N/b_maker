# src/gui/modules/script_block_base.py
"""
Базовый класс для диалогов блоков скрипта.
Предоставляет общую функциональность для IF Result, ELIF, IF Not Result.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt


from src.utils.ui_factory import (
    create_button, create_input_field, create_group_box
)
from src.utils.style_constants import (
    SCRIPT_DIALOG_BLUE_STYLE, COLOR_ERROR, COLOR_SUCCESS
)


class ScriptBlockDialog(QDialog):
    """
    Базовый класс для диалогов блоков скрипта.
    """

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(900, 700)  # Увеличиваем размер окна
        self.setStyleSheet(SCRIPT_DIALOG_BLUE_STYLE)  # Используем новый синий стиль
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)

        # Смещаем позицию окна относительно родителя
        if parent:
            from src.utils.ui_factory import position_dialog_with_offset
            position_dialog_with_offset(self, parent, 50, 50)

        # Будет инициализировано в дочерних классах
        self.canvas = None

        self.setup_ui()

    def setup_ui(self):
        """Настраивает базовый интерфейс диалога"""
        self.layout = QVBoxLayout(self)

        # ВАЖНО: этот метод больше не вызывает setup_buttons()
        # Дочерние классы должны сами вызывать этот метод в конце своих setup_ui

    def setup_settings_group(self):
        """Создает группу настроек"""
        settings_group = create_group_box("Настройки")
        settings_layout = QVBoxLayout(settings_group)

        # Сообщение в консоль
        log_layout = QHBoxLayout()
        log_label = QLabel("Сообщение в консоль:")
        self.log_input = create_input_field("Например: Изображение найдено!")
        self.log_input.setText("Изображение найдено!")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_input, 1)
        settings_layout.addLayout(log_layout)

        self.layout.addWidget(settings_group)

        return settings_group, settings_layout

    def setup_canvas(self):
        """
        Создает холст для действий - должен быть реализован в подклассах.
        """
        pass

    def setup_buttons(self):
        """Создает кнопки диалога с выравниванием вправо и новыми цветами"""
        buttons_layout = QHBoxLayout()

        self.cancel_btn = create_button("Отмена", f"""
            QPushButton {{
                background-color: {COLOR_ERROR};
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E55E5E;
            }}
        """)

        self.ok_btn = create_button("Подтвердить", f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5EBF61;
            }}
        """)

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        buttons_layout.addStretch(1)  # Добавляем растяжку слева для выравнивания кнопок вправо
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.ok_btn)

        # Добавляем панель в основной лейаут
        buttons_panel = QFrame()
        buttons_panel.setStyleSheet("""
            QFrame {
                border-top: 1px solid #4C7BD9;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        buttons_panel.setLayout(buttons_layout)

        self.layout.addWidget(buttons_panel)

    def get_data(self):
        """
        Получает данные из диалога.
        Должен быть переопределен в подклассах.
        """
        data = {
            "log_event": self.log_input.text(),
            "actions": self.canvas.get_modules_data() if self.canvas else []
        }
        return data

    def load_data(self, data):
        """
        Загружает данные в диалог.
        Должен быть дополнен в подклассах.
        """
        # Сообщение в консоль
        if "log_event" in data:
            self.log_input.setText(data["log_event"])

        # Загружаем действия в холст
        if "actions" in data and self.canvas:
            self.canvas.load_modules_data(data["actions"])