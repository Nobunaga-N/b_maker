# src/gui/dialogs/bot_settings_dialog.py

"""
Модуль содержит класс диалога настроек бота.
Позволяет настраивать параметры запуска бота: отложенный старт,
количество циклов, время работы, потоки и список эмуляторов.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QDateTimeEdit,
    QCheckBox, QGroupBox, QWidget, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QDateTime

from src.utils.style_constants import (
    COLOR_PRIMARY, COLOR_BG_DARK_3, COLOR_TEXT, BASE_BUTTON_STYLE, BASE_DIALOG_STYLE,
    SETTINGS_CHECKBOX_STYLE, SCHEDULE_CONTAINER_STYLE, DATETIME_EDIT_STYLE,
    SETTINGS_FORM_STYLE, SETTINGS_GROUP_STYLE, SETTINGS_SEPARATOR_STYLE
)
from src.utils.ui_factory import (
    create_input_field, create_spinbox_without_buttons,
    create_button, create_group_box, create_label, create_text_label
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
        self.resize(450, 400)
        self.setStyleSheet(BASE_DIALOG_STYLE)
        self.setup_ui()

        # Устанавливаем начальный стиль для чекбокса
        self.enable_schedule.setStyleSheet(SETTINGS_CHECKBOX_STYLE)

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Создаем контейнер для формы
        form_container = QWidget()
        form_container.setStyleSheet(SETTINGS_FORM_STYLE)

        # Создаем форму внутри контейнера
        form_layout = QFormLayout(form_container)
        form_layout.setVerticalSpacing(10)

        # Добавляем контейнер в основной макет
        layout.addWidget(form_container)

        # Группа планирования запуска с улучшенным стилем
        schedule_group = create_group_box("Планирование запуска")
        schedule_group.setStyleSheet(SETTINGS_GROUP_STYLE)
        schedule_layout = QVBoxLayout(schedule_group)

        # Добавляем небольшую верхнюю прокладку для чекбокса
        schedule_layout.setContentsMargins(8, 16, 8, 8)
        schedule_layout.setSpacing(8)

        # Включение/выключение планирования с улучшенной видимостью
        self.enable_schedule = QCheckBox("Использовать отложенный запуск")
        self.enable_schedule.setChecked(False)
        self.enable_schedule.toggled.connect(self.toggle_schedule)
        schedule_layout.addWidget(self.enable_schedule)

        # Контейнер для даты/времени
        self.schedule_container = QWidget()
        self.schedule_container.setObjectName("scheduleContainer")
        schedule_container_layout = QFormLayout(self.schedule_container)
        schedule_container_layout.setVerticalSpacing(8)

        # Улучшенный внешний вид контейнера для даты/времени
        self.schedule_container.setStyleSheet(SCHEDULE_CONTAINER_STYLE)

        # Отложенный старт (дата и время)
        self.scheduled_time = QDateTimeEdit()
        self.scheduled_time.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.scheduled_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # По умолчанию +1 час
        self.scheduled_time.setCalendarPopup(True)
        self.scheduled_time.setStyleSheet(DATETIME_EDIT_STYLE)

        # Улучшенный и более понятный текст метки
        start_time_label = create_label("Запланирован на:", style="color: white; font-weight: bold;")
        schedule_container_layout.addRow(start_time_label, self.scheduled_time)

        # Добавляем контейнер в группу планирования
        schedule_layout.addWidget(self.schedule_container)

        # По умолчанию контейнер с датой/временем скрыт
        self.schedule_container.setVisible(False)

        # Добавляем группу планирования
        layout.addWidget(schedule_group)

        # Группа выполнения
        execution_group = create_group_box("Параметры выполнения")
        execution_group.setStyleSheet(SETTINGS_GROUP_STYLE)
        execution_layout = QFormLayout(execution_group)

        # Количество циклов
        self.cycles_input = create_spinbox_without_buttons(0, 9999, 0)
        self.cycles_input.setToolTip("0 - бесконечное выполнение")
        execution_layout.addRow("Количество циклов:", self.cycles_input)

        # Время работы
        self.work_time_input = create_spinbox_without_buttons(0, 1440, 0)
        self.work_time_input.setToolTip("Время работы в минутах (0 - без ограничения)")
        execution_layout.addRow("Время работы (мин):", self.work_time_input)

        # Добавляем группу выполнения
        layout.addWidget(execution_group)

        # Группа эмуляторов
        emulators_group = create_group_box("Настройки эмуляторов")
        emulators_group.setStyleSheet(SETTINGS_GROUP_STYLE)
        emulators_layout = QFormLayout(emulators_group)

        # Количество потоков
        self.threads_input = create_spinbox_without_buttons(1, 50, 1)
        self.threads_input.setToolTip("Количество одновременно запущенных эмуляторов")
        emulators_layout.addRow("Количество потоков:", self.threads_input)

        # Список эмуляторов
        self.emulators_input = create_input_field("Например: 0:5,7,9:10")
        self.emulators_input.setToolTip("Формат: 0:5,7,9:10")
        emulators_layout.addRow("Список эмуляторов:", self.emulators_input)

        # Добавляем группу эмуляторов
        layout.addWidget(emulators_group)

        # Добавляем информационную подсказку по формату
        info_label = create_text_label(
            "Формат списка эмуляторов: одиночные ID через запятую (например: 0,1,2), "
            "диапазоны через двоеточие (например: 0:3 для 0,1,2,3), "
            "или их комбинации (например: 0:2,5,7:9).",
            "color: #aaaaaa; font-size: 10px;"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Добавляем разделительную линию
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(SETTINGS_SEPARATOR_STYLE)
        layout.addWidget(separator)

        # Кнопки OK и Cancel
        buttons_layout = QHBoxLayout()
        self.btn_cancel = create_button("Отмена", BASE_BUTTON_STYLE)
        self.btn_ok = create_button("ОК", BASE_BUTTON_STYLE)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_ok)

        layout.addLayout(buttons_layout)

    def toggle_schedule(self, enabled):
        """Включает или выключает панель планирования"""
        self.schedule_container.setVisible(enabled)

        # Обеспечиваем видимость чекбокса - изменяем его стилизацию
        # Это решает проблему, когда чекбокс становится невидимым на черном фоне
        self.enable_schedule.setStyleSheet(SETTINGS_CHECKBOX_STYLE)

        # Если панель стала видимой, обновляем время на текущее + 1 час
        if enabled:
            self.scheduled_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        # Подгоняем размер диалога под содержимое
        self.adjustSize()

    def get_data(self):
        """Возвращает данные, введенные пользователем"""
        # Если планирование отключено, используем текущее время
        if not self.enable_schedule.isChecked():
            scheduled_time = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        else:
            scheduled_time = self.scheduled_time.dateTime().toString("dd.MM.yyyy HH:mm")

        return {
            "scheduled_time": scheduled_time,
            "use_schedule": self.enable_schedule.isChecked(),
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
        # Устанавливаем статус включения планирования (по умолчанию выключено)
        use_schedule = data.get("use_schedule", False)
        self.enable_schedule.setChecked(use_schedule)
        self.schedule_container.setVisible(use_schedule)
        self.toggle_schedule(use_schedule)  # Это важно для применения правильного стиля чекбокса

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