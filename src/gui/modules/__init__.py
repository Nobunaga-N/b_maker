# src/gui/modules/__init__.py
"""
Пакет содержит модули для использования в графическом интерфейсе.
Модули предоставляют средства для создания и редактирования подмодулей поиска изображений.
"""

# Экспортируем основные классы для удобного импорта
from src.gui.modules.canvas_module import CanvasModule, ModuleItem
from src.gui.modules.condition_modules import IfResultModuleDialog, ElifModuleDialog, IfNotResultModuleDialog, IfResultCanvas
from src.gui.modules.image_search_module_improved import ImageSearchModuleDialog

# Определяем версию пакета
__version__ = "0.1.0"