# b_maker/src/gui/custom_widgets.py
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton


class ClickModuleDialog(QDialog):
    """
    Диалог для настройки модуля клика.
    Позволяет задать координаты, описание и время задержки после клика.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка модуля клика")
        self.setModal(True)
        self.resize(300, 250)

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.description_input = QLineEdit()
        self.console_description_input = QLineEdit()
        self.sleep_input = QLineEdit()  # время задержки после клика

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Координата X:"))
        layout.addWidget(self.x_input)
        layout.addWidget(QLabel("Координата Y:"))
        layout.addWidget(self.y_input)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Описание для консоли:"))
        layout.addWidget(self.console_description_input)
        layout.addWidget(QLabel("Время задержки (сек):"))
        layout.addWidget(self.sleep_input)

        self.btn_confirm = QPushButton("Подтвердить")
        layout.addWidget(self.btn_confirm)
        self.btn_confirm.clicked.connect(self.accept)

    def get_data(self) -> dict:
        """
        Возвращает данные, введенные пользователем.

        :return: Словарь с параметрами модуля клика.
        """
        return {
            "x": self.x_input.text().strip(),
            "y": self.y_input.text().strip(),
            "description": self.description_input.text().strip(),
            "console_description": self.console_description_input.text().strip(),
            "sleep": self.sleep_input.text().strip()
        }
