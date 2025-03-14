"""
Модуль для обработки изображений и поиска шаблонов на скриншотах.
Предоставляет функции для поиска изображений на экране эмулятора.
"""

import os
import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional, Union


class ImageProcessor:
    """
    Класс для обработки изображений и поиска шаблонов.
    Предоставляет методы для поиска изображений на скриншотах.
    """

    def __init__(self, logger=None):
        """
        Инициализирует процессор изображений.

        Args:
            logger: Объект логгера для записи отладочной информации.
        """
        self.logger = logger or logging.getLogger("ImageProcessor")
        self.templates_cache = {}  # Кэш загруженных шаблонов {путь: изображение}

    def load_template(self, template_path: str) -> np.ndarray:
        """
        Загружает изображение шаблона из файла с кэшированием.

        Args:
            template_path: Путь к файлу шаблона.

        Returns:
            Изображение шаблона как numpy array.

        Raises:
            FileNotFoundError: Если файл не найден.
            ValueError: Если не удалось загрузить изображение.
        """
        # Проверяем кэш
        if template_path in self.templates_cache:
            return self.templates_cache[template_path]

        # Проверяем существование файла
        if not os.path.exists(template_path):
            error_msg = f"Файл шаблона не найден: {template_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Загружаем изображение
        template = cv2.imread(template_path)

        if template is None:
            error_msg = f"Не удалось загрузить изображение шаблона: {template_path}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Сохраняем в кэш
        self.templates_cache[template_path] = template
        self.logger.debug(f"Шаблон загружен и кэширован: {template_path}")

        return template

    def find_template(self, screenshot: np.ndarray, template: np.ndarray,
                      threshold: float = 0.8) -> Tuple[bool, Tuple[int, int]]:
        """
        Ищет шаблон на скриншоте.

        Args:
            screenshot: Изображение скриншота.
            template: Изображение шаблона.
            threshold: Порог совпадения (от 0 до 1).

        Returns:
            Кортеж (найден, (x, y)), где:
            - найден: True, если шаблон найден, иначе False.
            - x, y: Координаты центра найденного шаблона.
        """
        # Проверяем размеры изображений
        if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
            self.logger.error("Шаблон больше скриншота")
            return False, (0, 0)

        # Используем TM_CCOEFF_NORMED для лучшего сопоставления
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

        # Находим наилучшее совпадение
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Логируем результат
        self.logger.debug(f"Поиск шаблона: совпадение {max_val:.4f} (порог {threshold:.4f})")

        # Если совпадение выше порога, считаем шаблон найденным
        if max_val >= threshold:
            # Вычисляем координаты центра шаблона
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            self.logger.info(f"Шаблон найден: ({center_x}, {center_y}) с точностью {max_val:.4f}")
            return True, (center_x, center_y)
        else:
            self.logger.info(f"Шаблон не найден (точность {max_val:.4f} ниже порога {threshold:.4f})")
            return False, (0, 0)

    def find_template_by_path(self, screenshot: np.ndarray, template_path: str,
                              threshold: float = 0.8) -> Tuple[bool, Tuple[int, int]]:
        """
        Ищет шаблон из файла на скриншоте.

        Args:
            screenshot: Изображение скриншота.
            template_path: Путь к файлу шаблона.
            threshold: Порог совпадения (от 0 до 1).

        Returns:
            Кортеж (найден, (x, y)), где:
            - найден: True, если шаблон найден, иначе False.
            - x, y: Координаты центра найденного шаблона.
        """
        try:
            template = self.load_template(template_path)
            return self.find_template(screenshot, template, threshold)
        except Exception as e:
            self.logger.error(f"Ошибка при поиске шаблона {template_path}: {str(e)}")
            return False, (0, 0)

    def find_any_template(self, screenshot: np.ndarray, template_paths: List[str],
                          threshold: float = 0.8) -> Tuple[bool, str, Tuple[int, int]]:
        """
        Ищет любой из указанных шаблонов на скриншоте.

        Args:
            screenshot: Изображение скриншота.
            template_paths: Список путей к файлам шаблонов.
            threshold: Порог совпадения (от 0 до 1).

        Returns:
            Кортеж (найден, путь, (x, y)), где:
            - найден: True, если хотя бы один шаблон найден, иначе False.
            - путь: Путь к найденному шаблону или пустая строка, если ничего не найдено.
            - x, y: Координаты центра найденного шаблона.
        """
        best_match = None
        best_path = ""
        best_val = 0
        best_loc = (0, 0)

        for path in template_paths:
            try:
                template = self.load_template(path)

                # Проверяем размеры изображений
                if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
                    self.logger.error(f"Шаблон {path} больше скриншота")
                    continue

                # Ищем шаблон
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                # Обновляем лучший результат, если найдено лучшее совпадение
                if max_val > best_val:
                    best_val = max_val
                    best_match = template
                    best_path = path
                    best_loc = max_loc

                # Если совпадение достаточно хорошее, можно сразу вернуть результат
                if max_val >= threshold:
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2

                    self.logger.info(
                        f"Шаблон {path} найден первым: ({center_x}, {center_y}) "
                        f"с точностью {max_val:.4f}"
                    )
                    return True, path, (center_x, center_y)

            except Exception as e:
                self.logger.error(f"Ошибка при поиске шаблона {path}: {str(e)}")
                continue

        # Если найдено лучшее совпадение выше порога
        if best_match is not None and best_val >= threshold:
            h, w = best_match.shape[:2]
            center_x = best_loc[0] + w // 2
            center_y = best_loc[1] + h // 2

            self.logger.info(
                f"Шаблон {best_path} найден: ({center_x}, {center_y}) "
                f"с точностью {best_val:.4f}"
            )
            return True, best_path, (center_x, center_y)

        self.logger.info(f"Ни один шаблон не найден (лучшая точность {best_val:.4f})")
        return False, "", (0, 0)

    def clear_cache(self):
        """Очищает кэш шаблонов."""
        self.templates_cache.clear()
        self.logger.debug("Кэш шаблонов очищен")

    def save_debug_image(self, screenshot: np.ndarray, template: np.ndarray,
                         match_loc: Tuple[int, int], output_path: str):
        """
        Сохраняет отладочное изображение с отмеченным найденным шаблоном.

        Args:
            screenshot: Изображение скриншота.
            template: Изображение шаблона.
            match_loc: Координаты левого верхнего угла найденного шаблона.
            output_path: Путь для сохранения отладочного изображения.
        """
        try:
            # Создаем копию скриншота
            debug_img = screenshot.copy()

            # Получаем размеры шаблона
            h, w = template.shape[:2]

            # Рисуем прямоугольник вокруг найденного шаблона
            x, y = match_loc
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Рисуем крестик в центре
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.drawMarker(
                debug_img,
                (center_x, center_y),
                (0, 0, 255),
                markerType=cv2.MARKER_CROSS,
                markerSize=20,
                thickness=2
            )

            # Добавляем подпись с координатами
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"({center_x}, {center_y})"
            cv2.putText(
                debug_img,
                text,
                (center_x + 10, center_y - 10),
                font,
                0.6,
                (0, 255, 255),
                2
            )

            # Сохраняем изображение
            cv2.imwrite(output_path, debug_img)
            self.logger.debug(f"Отладочное изображение сохранено: {output_path}")

        except Exception as e:
            self.logger.error(f"Ошибка при сохранении отладочного изображения: {str(e)}")