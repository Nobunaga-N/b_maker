# src/gui/dialogs/bot_settings_dialog.py
"""
Модуль содержит класс диалога настроек бота.
Позволяет настраивать параметры запуска бота: отложенный старт,
количество циклов, время работы, потоки и список эмуляторов.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QFrame, QFormLayout, QPushButton, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime

from src.utils.style_constants import (
    MODULE_DIALOG_STYLE, MODULE_BUTTON_STYLE
)
from src.utils.ui_factory import (
    create_input_field, create_spinbox_without_buttons
)


class BotSettingsDialog(QDialog):
    """
    Диалог для настройки параметров запуска бота.
    Позволяет настроить отложенный старт, циклы, время работы,
    количество потоков и список эмуляторов.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка параметров бота")
        self.setModal(True)
        self.resize(450, 350)
        self.setStyleSheet(MODULE_DIALOG_STYLE)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Создаем форму для полей ввода
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        # Отложенный старт (дата и время)
        self.scheduled_time = QDateTimeEdit()
        self.scheduled_time.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.scheduled_time.setDateTime(QDateTime.currentDateTime())
        self.scheduled_time.setCalendarPopup(True)
        self.scheduled_time.setStyleSheet("""
            QDateTimeEdit {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        form_layout.addRow("Запланирован на:", self.scheduled_time)

        # Количество циклов
        self.cycles_input = create_spinbox_without_buttons(0, 9999, 0)
        self.cycles_input.setToolTip("0 - бесконечное выполнение")
        form_layout.addRow("Количество циклов:", self.cycles_input)

        # Время работы
        self.work_time_input = create_spinbox_without_buttons(0, 1440, 0)
        self.work_time_input.setToolTip("Время работы в минутах (0 - без ограничения)")
        form_layout.addRow("Время работы (мин):", self.work_time_input)

        # Количество потоков
        self.threads_input = create_spinbox_without_buttons(1, 50, 1)
        self.threads_input.setToolTip("Количество одновременно запущенных эмуляторов")
        form_layout.addRow("Количество потоков:", self.threads_input)

        # Список эмуляторов
        self.emulators_input = create_input_field("Например: 0:5,7,9:10")
        self.emulators_input.setToolTip("Формат: 0:5,7,9:10")
        form_layout.addRow("Список эмуляторов:", self.emulators_input)

        # Добавляем информационную подсказку по формату
        info_label = QLabel(
            "Формат списка эмуляторов: одиночные ID через запятую (например: 0,1,2), "
            "диапазоны через двоеточие (например: 0:3 для 0,1,2,3), "
            "или их комбинации (например: 0:2,5,7:9)."
        )
        info_label.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        info_label.setWordWrap(True)
        layout.addLayout(form_layout)
        layout.addWidget(info_label)

        # Добавляем разделительную линию
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #555;")
        layout.addWidget(separator)

        # Кнопки OK и Cancel
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok = QPushButton("ОК")

        self.btn_cancel.setStyleSheet(MODULE_BUTTON_STYLE)
        self.btn_ok.setStyleSheet(MODULE_BUTTON_STYLE)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_ok)

        layout.addLayout(buttons_layout)

    def get_data(self):
        """Возвращает данные, введенные пользователем"""
        return {
            "scheduled_time": self.scheduled_time.dateTime().toString("dd.MM.yyyy HH:mm"),
            "cycles": self.cycles_input.value(),
            "work_time": self.work_time_input.value(),
            "threads": self.threads_input.value(),
            "emulators": self.emulators_input.text()
        }

    def set_data(self, data):
        """
        Устанавливает данные в поля диалога.

        :param data: Словарь с данными
        """
        # Устанавливаем дату и время, если они есть
        if "scheduled_time" in data and data["scheduled_time"]:
            try:
                dt = QDateTime.fromString(data["scheduled_time"], "dd.MM.yyyy HH:mm")
                if dt.isValid():
                    self.scheduled_time.setDateTime(dt)
            except Exception as e:
                print(f"Ошибка при установке даты и времени: {e}")

        # Устанавливаем остальные значения
        if "cycles" in data:
            try:
                self.cycles_input.setValue(data["cycles"])
            except Exception as e:
                print(f"Ошибка при установке циклов: {e}")

        if "work_time" in data:
            try:
                self.work_time_input.setValue(data["work_time"])
            except Exception as e:
                print(f"Ошибка при установке времени работы: {e}")

        if "threads" in data:
            try:
                self.threads_input.setValue(data["threads"])
            except Exception as e:
                print(f"Ошибка при установке количества потоков: {e}")

        if "emulators" in data:
            self.emulators_input.setText(data["emulators"])