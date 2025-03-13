# src/utils/module_handler.py
"""
Модуль содержит класс ModuleHandler для унификации обработки модулей
и устранения дублирования кода в различных частях приложения.
"""

from typing import Dict, Any, Callable, Optional, Type, List, Tuple
from PyQt6.QtWidgets import QDialog, QMessageBox


class ModuleHandler:
    """
    Базовый класс для работы с модулями в различных контекстах.
    Содержит общие методы для добавления, редактирования и управления модулями.
    """

    @staticmethod
    def format_module_description(module_type: str, data: Dict[str, Any]) -> str:
        """
        Универсальная функция форматирования описаний модулей.

        Args:
            module_type: Тип модуля (Клик, Свайп, Пауза и др.)
            data: Данные модуля

        Returns:
            Отформатированное описание модуля
        """
        if module_type == "Клик":
            description = f"({data['x']}, {data['y']})"
            if data.get('description'):
                description += f" - {data['description']}"
            if data.get('sleep', 0) > 0:
                description += f" с задержкой {data['sleep']} сек"

        elif module_type == "Свайп":
            description = f"({data['x1']}, {data['y1']}) → ({data['x2']}, {data['y2']})"
            if data.get('description'):
                description += f" - {data['description']}"
            if data.get('sleep', 0) > 0:
                description += f" с задержкой {data['sleep']} сек"

        elif module_type == "Пауза":
            description = f"Пауза {data.get('delay', 1.0)} сек"
            if data.get('description'):
                description += f" - {data['description']}"

        elif module_type == "Поиск картинки":
            images_str = ", ".join(data.get("images", []))
            description = f"Поиск: {images_str} (таймаут: {data.get('timeout', 120)} сек)"

            # Добавляем информацию о блоках скрипта
            script_items = data.get("script_items", [])
            if script_items:
                if_result_count = sum(1 for item in script_items if item.get("type") == "if_result")
                elif_count = sum(1 for item in script_items if item.get("type") == "elif")
                if_not_result_count = sum(1 for item in script_items if item.get("type") == "if_not_result")

                blocks_info = []
                if if_result_count:
                    blocks_info.append(f"{if_result_count} IF Result")
                if elif_count:
                    blocks_info.append(f"{elif_count} ELIF")
                if if_not_result_count:
                    blocks_info.append(f"{if_not_result_count} IF Not Result")

                if blocks_info:
                    description += f" | Блоки: {', '.join(blocks_info)}"

        elif module_type == "Activity":
            status = "Включен" if data.get("enabled", False) else "Отключен"
            description = f"Статус: {status}, Действие: {data.get('action', '')}"

        elif module_type == "time.sleep":
            time_value = data.get("time", 1.0)
            description = f"Пауза {time_value} сек (time.sleep)"

        elif module_type == "restart.from":
            line_number = data.get("line", 1)
            description = f"Перезапуск со строки {line_number} (restart.from)"

        elif module_type == "get_coords":
            description = "Клик по координатам найденного изображения"

        elif module_type == "close.game":
            description = "Закрыть игру (close.game)"

        elif module_type == "restart.emulator":
            description = "Перезапустить эмулятор (restart.emulator)"

        elif module_type == "start.game":
            description = "Запустить игру (start.game)"

        elif module_type == "restart.from.last":
            description = "Перезапуск с последней позиции (restart.from.last)"

        elif module_type == "continue":
            description = "Продолжить выполнение скрипта (continue)"

        elif module_type == "running.clear()":
            description = "Остановить выполнение бота (running.clear())"

        else:
            # Обобщенное описание для неизвестных типов модулей
            description = f"Модуль {module_type}"

        return description

    @staticmethod
    def add_module_with_dialog(
            dialog_class: Type[QDialog],
            parent: Optional[object] = None,
            callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Универсальный метод для добавления модуля через диалог.

        Args:
            dialog_class: Класс диалога для создания модуля
            parent: Родительский объект для диалога
            callback: Функция обратного вызова для обработки результата

        Returns:
            Кортеж (успех, данные)
        """
        dialog = dialog_class(parent)

        if dialog.exec():
            try:
                data = dialog.get_data()
                if not data:
                    return False, None

                # Получаем тип модуля из диалога или из класса диалога
                module_type = getattr(dialog, "MODULE_TYPE", dialog.__class__.__name__.replace("Dialog", ""))

                # Форматируем описание
                description = ModuleHandler.format_module_description(module_type, data)

                # Если есть callback, вызываем его
                if callback:
                    callback(module_type, description, data)

                return True, data

            except Exception as e:
                if parent:
                    QMessageBox.warning(parent, "Ошибка", f"Некорректные данные: {str(e)}")
                return False, None

        return False, None

    @staticmethod
    def edit_module_with_dialog(
            dialog_class: Type[QDialog],
            existing_data: Dict[str, Any],
            parent: Optional[object] = None,
            callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Универсальный метод для редактирования модуля через диалог.

        Args:
            dialog_class: Класс диалога для редактирования модуля
            existing_data: Существующие данные модуля
            parent: Родительский объект для диалога
            callback: Функция обратного вызова для обработки результата

        Returns:
            Кортеж (успех, данные)
        """
        dialog = dialog_class(parent)

        # Загружаем данные в диалог
        if hasattr(dialog, "load_data"):
            dialog.load_data(existing_data)

        if dialog.exec():
            try:
                data = dialog.get_data()
                if not data:
                    return False, None

                # Получаем тип модуля из диалога или из класса диалога
                module_type = getattr(dialog, "MODULE_TYPE", dialog.__class__.__name__.replace("Dialog", ""))

                # Форматируем описание
                description = ModuleHandler.format_module_description(module_type, data)

                # Если есть callback, вызываем его
                if callback:
                    callback(module_type, description, data)

                return True, data

            except Exception as e:
                if parent:
                    QMessageBox.warning(parent, "Ошибка", f"Некорректные данные: {str(e)}")
                return False, None

        return False, None