# src/gui/modules/__init__.py
"""
Пакет содержит модули для использования в графическом интерфейсе.
Модули предоставляют средства для создания и редактирования подмодулей поиска изображений.
"""

# Экспортируем основные классы для удобного импорта
from src.gui.modules.canvas_module import CanvasModule, ModuleItem
from src.gui.modules.if_result_module import IfResultCanvas, IfResultModuleDialog
from src.gui.modules.elif_module import ElifModuleDialog
from src.gui.modules.if_not_result_module import IfNotResultModuleDialog
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog

# Определяем версию пакета
__version__ = "0.1.0"