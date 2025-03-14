# 4. Модуль обработки изображений - для поиска шаблонов на экране
import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional, Union
import os
import hashlib
import logging


class ImageProcessor:
    """
    Модуль для обработки изображений и поиска шаблонов на скриншоте.
    """

    def __init__(self, cache_size: int = 100, threshold: float = 0.8, logger=None):
        """
        Инициализирует обработчик изображений.

        Args:
            cache_size: Размер кэша шаблонов изображений.
            threshold: Порог совпадения по умолчанию (0.0 - 1.0).
            logger: Объект логгера.
        """
        self.logger = logger or logging.getLogger("ImageProcessor")
        self.templates_cache = {}  # {template_path: template_image}
        self.cache_size = cache_size
        self.default_threshold = threshold

    def find_template(self, screenshot: np.ndarray, template_path: str,
                      threshold: Optional[float] = None) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Ищет шаблон на скриншоте.

        Args:
            screenshot: Скриншот в формате numpy array.
            template_path: Путь к изображению шаблона.
            threshold: Порог совпадения (0.0 - 1.0). Если None, используется порог по умолчанию.

        Returns:
            Кортеж (найдено, координаты, достоверность).
            Если шаблон не найден, координаты будут None.
        """
        if threshold is None:
            threshold = self.default_threshold

        try:
            # Загружаем шаблон
            template = self._load_template(template_path)

            if template is None:
                self.logger.error(f"Не удалось загрузить шаблон: {template_path}")
                return False, None, 0.0

            # Выполняем сопоставление шаблонов
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Находим максимальное значение и его позицию
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Проверяем, превышает ли максимальное значение порог
            if max_val >= threshold:
                # Вычисляем центр найденного шаблона
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                self.logger.debug(
                    f"Шаблон {os.path.basename(template_path)} найден с достоверностью {max_val:.2f} в позиции ({center_x}, {center_y})")
                return True, (center_x, center_y), max_val
            else:
                self.logger.debug(
                    f"Шаблон {os.path.basename(template_path)} не найден (max_val={max_val:.2f} < threshold={threshold:.2f})")
                return False, None, max_val

        except Exception as e:
            self.logger.error(f"Ошибка при поиске шаблона {template_path}: {str(e)}")
            return False, None, 0.0

    def find_multiple_templates(self, screenshot: np.ndarray, template_paths: List[str],
                                threshold: Optional[float] = None) -> Dict[
        str, Tuple[bool, Optional[Tuple[int, int]], float]]:
        """
        Ищет несколько шаблонов на скриншоте.

        Args:
            screenshot: Скриншот в формате numpy array.
            template_paths: Список путей к изображениям шаблонов.
            threshold: Порог совпадения (0.0 - 1.0). Если None, используется порог по умолчанию.

        Returns:
            Словарь {template_path: (найдено, координаты, достоверность)}.
        """
        results = {}

        for template_path in template_paths:
            results[template_path] = self.find_template(screenshot, template_path, threshold)

        return results

    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """
        Загружает шаблон из файла или кэша.

        Args:
            template_path: Путь к изображению шаблона.

        Returns:
            Шаблон в формате numpy array или None в случае ошибки.
        """
        # Проверяем кэш
        if template_path in self.templates_cache:
            return self.templates_cache[template_path]

        try:
            # Загружаем шаблон из файла
            template = cv2.imread(template_path)

            if template is None:
                return None

            # Добавляем в кэш
            if len(self.templates_cache) >= self.cache_size:
                # Удаляем случайный элемент, если кэш переполнен
                self.templates_cache.pop(next(iter(self.templates_cache)))

            self.templates_cache[template_path] = template

            return template

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке шаблона {template_path}: {str(e)}")
            return None

    def clear_cache(self):
        """Очищает кэш шаблонов."""
        self.templates_cache.clear()