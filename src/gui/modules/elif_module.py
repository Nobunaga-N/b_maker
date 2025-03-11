# src/gui/modules/elif_module.py - оптимизированная версия
"""
Модуль для подмодуля ELIF, используемого в модуле поиска изображений.
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QMessageBox
from src.utils.ui_factory import create_group_box
from src.gui.modules.if_result_module import IfResultCanvas
from src.gui.modules.script_block_base import ScriptBlockDialog


class ElifModuleDialog(ScriptBlockDialog):
    """
    Диалог для настройки подмодуля ELIF.
    Позволяет выбрать конкретное изображение, настроить сообщение и действия.
    """

    def __init__(self, images_list, parent=None):
        self.images_list = images_list  # Список доступных изображений
        super().__init__("Настройка блока ELIF", parent)

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        super().setup_ui()

        # --- 1. Настройки изображения и основных параметров ---
        settings_group, settings_layout = self.setup_settings_group()

        # Выбор изображения (для ELIF обязательно выбрать конкретное изображение)
        image_layout = QHBoxLayout()
        image_label = QLabel("Изображение для проверки:")
        self.image_combo = QComboBox()
        self.image_combo.addItems(self.images_list)

        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_combo, 1)

        # Вставляем выбор изображения перед сообщением в консоль
        settings_layout.insertLayout(0, image_layout)

        # Устанавливаем текст по умолчанию
        self.log_input.setText("Найдено другое изображение!")

        # --- 2. Холст для дополнительных действий ---
        self.setup_canvas()

    def setup_canvas(self):
        """Создает холст для действий"""
        action_group = create_group_box("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)

        self.canvas = IfResultCanvas(self)
        action_layout.addWidget(self.canvas)

        self.layout.addWidget(action_group)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        # Для ELIF изображение обязательно
        if self.image_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать изображение для блока ELIF")
            return None

        image = self.image_combo.currentText()

        data = super().get_data()
        data.update({
            "type": "elif",
            "image": image
        })

        return data

    def load_data(self, data):
        """Загружает данные для редактирования"""
        super().load_data(data)

        # Изображение
        if data.get("image"):
            index = self.image_combo.findText(data["image"])
            if index >= 0:
                self.image_combo.setCurrentIndex(index)