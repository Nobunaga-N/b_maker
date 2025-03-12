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
        # Создаем группу без отступов по бокам
        action_group = create_group_box("Дополнительные действия")
        action_layout = QVBoxLayout(action_group)
        # Уменьшаем отступы группы, чтобы она имела такие же границы, как заголовок
        action_layout.setContentsMargins(0, 16, 0, 0)  # Только верхний отступ для заголовка группы

        self.canvas = IfResultCanvas(self)
        self.canvas.setStyleSheet(SCRIPT_SUBMODULE_CANVAS_STYLE)

        # Настраиваем layout холста, убирая лишние отступы
        self.canvas.setContentsMargins(0, 0, 0, 0)
        action_layout.addWidget(self.canvas)

        # Убираем боковые отступы при добавлении группы в основной layout
        self.layout.setContentsMargins(10, 10, 10, 10)  # Одинаковые отступы для всего диалога
        self.layout.addWidget(action_group)

    def get_data(self):
        """Возвращает данные, настроенные пользователем"""
        data = super().get_data()
        data["type"] = "if_not_result"
        return data