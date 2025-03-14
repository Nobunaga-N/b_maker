# src/utils/bot_image_processor.py - расширение ImageProcessor для ботов

from typing import List, Tuple, Optional, Dict, Callable
from src.utils.image_processor import ImageProcessor


class BotImageProcessor(ImageProcessor):
    """
    Расширение ImageProcessor с функциями, специфичными для ботов.
    """

    def find_and_execute_action(self, get_screen_func, templates: List[str],
                                action_callback: Callable[[str, Dict], None],
                                timeout: float = 10.0, threshold: float = 0.8) -> bool:
        """
        Находит шаблон на экране и выполняет действие при его обнаружении.

        Args:
            get_screen_func: Функция для получения скриншота
            templates: Список путей к шаблонам
            action_callback: Функция обратного вызова, получает имя найденного шаблона и результат
            timeout: Время ожидания в секундах
            threshold: Порог совпадения

        Returns:
            True, если шаблон найден и действие выполнено
        """
        template_name, result = self.wait_for_any_template(
            get_screen_func, templates, timeout, threshold=threshold
        )

        if template_name and result:
            # Вызываем колбэк с именем найденного шаблона и результатом
            action_callback(template_name, result)
            return True

        return False