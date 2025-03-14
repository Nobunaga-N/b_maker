import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Callable, Union, Any
from PIL import Image

from src.utils.image_processor import ImageProcessor
from src.utils.exceptions import ImageProcessingError


class BotImageProcessor(ImageProcessor):
    """
    Расширенный класс для обработки изображений, специфичный для ботов.
    Добавляет функциональность для поиска изображений, распознавания объектов
    и выполнения действий при обнаружении.

    Наследует базовую функциональность от ImageProcessor и оптимизирован для
    использования в ботах, включая кэширование результатов и анализ регионов интереса.
    """

    def __init__(self, max_workers: int = 4, logger=None):
        """
        Инициализирует процессор изображений для ботов.

        Args:
            max_workers: Максимальное количество потоков для параллельного поиска.
            logger: Объект логирования.
        """
        super().__init__(max_workers, logger)

        # Дополнительные настройки для ботов
        self.last_found_coordinates = None  # Для функции get_coords
        self.roi_history = {}  # Для отслеживания регионов интереса
        self.search_stats = {
            'searches': 0,
            'found': 0,
            'not_found': 0,
            'total_time': 0,
        }

    def find_and_click(self, get_screen_func, templates: List[str],
                       adb_controller, device_id: str,
                       timeout: float = 10.0, threshold: float = 0.8,
                       click_offset_x: int = 0, click_offset_y: int = 0,
                       post_click_delay: float = 0.5) -> bool:
        """
        Находит изображение на экране и выполняет клик по его координатам.

        Args:
            get_screen_func: Функция для получения скриншота.
            templates: Список путей к шаблонам.
            adb_controller: Контроллер ADB для выполнения клика.
            device_id: ID устройства.
            timeout: Максимальное время ожидания (секунды).
            threshold: Порог соответствия (0.0-1.0).
            click_offset_x: Смещение клика по X относительно центра найденного изображения.
            click_offset_y: Смещение клика по Y относительно центра найденного изображения.
            post_click_delay: Задержка после клика (секунды).

        Returns:
            True, если изображение найдено и клик выполнен, иначе False.
        """
        start_time = time.time()
        self.search_stats['searches'] += 1

        try:
            # Поиск изображения
            template_name, result = self.wait_for_any_template(
                get_screen_func, templates, timeout, threshold=threshold
            )

            if template_name and result:
                # Сохраняем найденные координаты для использования в get_coords
                self.last_found_coordinates = (
                    result['center_x'] + click_offset_x,
                    result['center_y'] + click_offset_y
                )

                # Выполняем клик
                adb_controller.tap(device_id,
                                   self.last_found_coordinates[0],
                                   self.last_found_coordinates[1])

                # Логируем успех
                self._log_info(f"Найдено изображение {template_name}, выполнен клик по координатам "
                               f"({self.last_found_coordinates[0]}, {self.last_found_coordinates[1]})")

                # Обновляем статистику
                self.search_stats['found'] += 1
                self.search_stats['total_time'] += time.time() - start_time

                # Ждем после клика
                if post_click_delay > 0:
                    time.sleep(post_click_delay)

                return True

            # Обновляем статистику при неудаче
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

        except Exception as e:
            self._log_error(f"Ошибка при поиске и клике по изображению: {e}")
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

    def find_and_swipe(self, get_screen_func, templates: List[str],
                       adb_controller, device_id: str,
                       swipe_direction: str = "up", swipe_distance: int = 200,
                       timeout: float = 10.0, threshold: float = 0.8,
                       post_swipe_delay: float = 0.5) -> bool:
        """
        Находит изображение на экране и выполняет свайп от его координат.

        Args:
            get_screen_func: Функция для получения скриншота.
            templates: Список путей к шаблонам.
            adb_controller: Контроллер ADB для выполнения свайпа.
            device_id: ID устройства.
            swipe_direction: Направление свайпа ("up", "down", "left", "right").
            swipe_distance: Расстояние свайпа в пикселях.
            timeout: Максимальное время ожидания (секунды).
            threshold: Порог соответствия (0.0-1.0).
            post_swipe_delay: Задержка после свайпа (секунды).

        Returns:
            True, если изображение найдено и свайп выполнен, иначе False.
        """
        start_time = time.time()
        self.search_stats['searches'] += 1

        try:
            # Поиск изображения
            template_name, result = self.wait_for_any_template(
                get_screen_func, templates, timeout, threshold=threshold
            )

            if template_name and result:
                # Сохраняем найденные координаты
                x1, y1 = result['center_x'], result['center_y']
                x2, y2 = x1, y1

                # Определяем координаты конца свайпа в зависимости от направления
                if swipe_direction == "up":
                    y2 = y1 - swipe_distance
                elif swipe_direction == "down":
                    y2 = y1 + swipe_distance
                elif swipe_direction == "left":
                    x2 = x1 - swipe_distance
                elif swipe_direction == "right":
                    x2 = x1 + swipe_distance

                # Ограничиваем координаты границами экрана
                # Получаем скриншот для определения размеров экрана
                screen = get_screen_func()
                if isinstance(screen, Image.Image):
                    screen_width, screen_height = screen.size
                else:  # numpy array
                    screen_height, screen_width = screen.shape[:2]

                x2 = max(0, min(x2, screen_width - 1))
                y2 = max(0, min(y2, screen_height - 1))

                # Выполняем свайп
                adb_controller.swipe(device_id, x1, y1, x2, y2)

                # Логируем успех
                self._log_info(f"Найдено изображение {template_name}, выполнен свайп "
                               f"от ({x1}, {y1}) к ({x2}, {y2})")

                # Обновляем статистику
                self.search_stats['found'] += 1
                self.search_stats['total_time'] += time.time() - start_time

                # Ждем после свайпа
                if post_swipe_delay > 0:
                    time.sleep(post_swipe_delay)

                return True

            # Обновляем статистику при неудаче
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

        except Exception as e:
            self._log_error(f"Ошибка при поиске и свайпе от изображения: {e}")
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

    def find_and_execute_action(self, get_screen_func, templates: List[str],
                                action_callback: Callable[[str, Dict], None],
                                timeout: float = 10.0, threshold: float = 0.8,
                                regions: List[Tuple[int, int, int, int]] = None) -> bool:
        """
        Находит шаблон на экране и выполняет действие при его обнаружении.

        Args:
            get_screen_func: Функция для получения скриншота.
            templates: Список путей к шаблонам.
            action_callback: Функция обратного вызова, которая получает имя найденного
                            шаблона и результат поиска в качестве аргументов.
            timeout: Максимальное время ожидания (секунды).
            threshold: Порог соответствия (0.0-1.0).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            True, если шаблон найден и действие выполнено, иначе False.
        """
        start_time = time.time()
        self.search_stats['searches'] += 1

        try:
            # Поиск изображения
            template_name, result = self.wait_for_any_template(
                get_screen_func, templates, timeout, threshold=threshold, regions=regions
            )

            if template_name and result:
                # Сохраняем найденные координаты
                self.last_found_coordinates = (result['center_x'], result['center_y'])

                # Сохраняем регион интереса для оптимизации последующих поисков
                if regions is None:
                    # Если регионы не указаны, создаем регион вокруг найденного изображения
                    x, y, w, h = result['x'], result['y'], result['w'], result['h']
                    # Расширяем регион на 20% для учета небольших перемещений
                    expand_w, expand_h = int(w * 0.2), int(h * 0.2)
                    roi = (
                        max(0, x - expand_w),
                        max(0, y - expand_h),
                        w + 2 * expand_w,
                        h + 2 * expand_h
                    )
                    # Сохраняем регион по имени шаблона
                    self.roi_history[template_name] = roi

                # Вызываем callback с результатом
                action_callback(template_name, result)

                # Обновляем статистику
                self.search_stats['found'] += 1
                self.search_stats['total_time'] += time.time() - start_time

                return True

            # Обновляем статистику при неудаче
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

        except Exception as e:
            self._log_error(f"Ошибка при поиске и выполнении действия: {e}")
            self.search_stats['not_found'] += 1
            self.search_stats['total_time'] += time.time() - start_time

            return False

    def get_last_found_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Возвращает координаты последнего найденного изображения.

        Returns:
            Координаты (x, y) или None, если изображение не было найдено.
        """
        return self.last_found_coordinates

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику поиска изображений.

        Returns:
            Словарь со статистической информацией.
        """
        stats = self.search_stats.copy()

        # Добавляем вычисляемые значения
        if stats['searches'] > 0:
            stats['success_rate'] = stats['found'] / stats['searches'] * 100
            stats['avg_search_time'] = stats['total_time'] / stats['searches']
        else:
            stats['success_rate'] = 0
            stats['avg_search_time'] = 0

        return stats

    def reset_search_stats(self) -> None:
        """
        Сбрасывает статистику поиска изображений.
        """
        self.search_stats = {
            'searches': 0,
            'found': 0,
            'not_found': 0,
            'total_time': 0,
        }

    def propose_regions_of_interest(self, template_names: List[str]) -> List[Tuple[int, int, int, int]]:
        """
        Предлагает регионы интереса на основе истории поиска заданных шаблонов.
        Это оптимизирует поиск, ограничивая его областями, где изображения уже находились ранее.

        Args:
            template_names: Список имен шаблонов для поиска регионов.

        Returns:
            Список регионов интереса.
        """
        regions = []

        for name in template_names:
            if name in self.roi_history:
                regions.append(self.roi_history[name])

        return regions if regions else None