# src/gui/modules/if_not_result_module.py - оптимизированная версия
"""
Модуль для подмодуля IF Not Result, используемого в модуле поиска изображений.
"""
from PyQt6.QtWidgets import QVBoxLayout, QFrame
from src.utils.ui_factory import create_group_box
from src.gui.modules.if_result_module import IfResultCanvas
from src.gui.modules.script_block_base import ScriptBlockDialog
from src.utils.style_constants import SCRIPT_SUBMODULE_CANVAS_STYLE


class IfNotResultModuleDialog(ScriptBlockDialog):
    """
    Диалог для настройки подмодуля IF Not Result.
    Позволяет настроить сообщение и действия, когда изображения не найдены.
    """

    def __init__(self, parent=None):
        super().__init__("Настройка блока IF Not Result", parent)

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        # Инициализируем базовый layout напрямую
        self.layout = QVBoxLayout(self)

        # --- 1. Настройки основных параметров ---
        settings_group, settings_layout = self.setup_settings_group()

        # Устанавливаем текст по умолчанию
        self.log_input.setText("Изображение не найдено!")

        # --- 2. Холст для дополнительных действий ---
        self.setup_canvas()

        # --- 3. Кнопки диалога (добавляем в конце) ---
        self.setup_buttons()

    def setup_canvas(self):
        """Создает холст для действий"""
        action_group = create_group_box("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)

        self.canvas = IfResultCanvas(self)
        self.canvas.setStyleSheet(SCRIPT_SUBMODULE_CANVAS_STYLE)
        action_layout.addWidget(self.canvas)

        self.layout.addWidget(action_group)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        data = super().get_data()
        data["type"] = "if_not_result"
        return data