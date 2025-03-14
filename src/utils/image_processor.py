# src/utils/image_processor.py
import os
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Union
from PIL import Image
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from src.utils.exceptions import ImageProcessingError


class ImageProcessor:
    """
    Класс для обработки изображений и поиска шаблонов на скриншотах.
    Использует OpenCV для эффективного поиска изображений без сохранения на диск.
    Реализует кэширование, многопоточный поиск и масштабирование шаблонов.
    """

    def __init__(self, max_workers: int = 4, logger: Optional[logging.Logger] = None):
        """
        Инициализирует процессор изображений.

        Args:
            max_workers: Максимальное количество потоков для параллельного поиска.
            logger: Объект логирования.
        """
        self.logger = logger
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Кэш для изображений-шаблонов, чтобы не загружать их каждый раз
        self._template_cache = {}

        # Кэш последних скриншотов для повторного использования
        self._screenshot_cache = {}

    def _log_debug(self, message: str) -> None:
        """Вспомогательный метод для логирования отладочных сообщений."""
        if self.logger:
            self.logger.debug(message)

    def _log_info(self, message: str) -> None:
        """Вспомогательный метод для логирования информационных сообщений."""
        if self.logger:
            self.logger.info(message)

    def _log_error(self, message: str) -> None:
        """Вспомогательный метод для логирования ошибок."""
        if self.logger:
            self.logger.error(message)

    def load_template(self, template_path: str, force_reload: bool = False) -> np.ndarray:
        """
        Загружает изображение-шаблон из файла и преобразует его для использования в OpenCV.

        Args:
            template_path: Путь к файлу шаблона.
            force_reload: Принудительно перезагрузить шаблон, если он уже в кэше.

        Returns:
            Массив NumPy с изображением шаблона в формате BGR.

        Raises:
            ImageProcessingError: Если произошла ошибка при загрузке шаблона.
        """
        try:
            # Проверяем кэш, если не требуется принудительная перезагрузка
            if not force_reload and template_path in self._template_cache:
                self._log_debug(f"Использую кэшированный шаблон: {template_path}")
                return self._template_cache[template_path]

            # Проверяем существование файла
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Файл шаблона не найден: {template_path}")

            # Загружаем изображение через OpenCV напрямую
            template_bgr = cv2.imread(template_path)

            if template_bgr is None:
                raise ValueError(f"Не удалось загрузить изображение: {template_path}")

            # Сохраняем в кэш
            self._template_cache[template_path] = template_bgr

            self._log_debug(f"Шаблон загружен: {template_path}, размер: {template_bgr.shape}")

            return template_bgr

        except Exception as e:
            error_msg = f"Ошибка загрузки шаблона {template_path}: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def convert_pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """
        Конвертирует изображение из формата PIL в формат OpenCV (NumPy array).

        Args:
            pil_image: Изображение в формате PIL.

        Returns:
            Массив NumPy с изображением в формате BGR для OpenCV.

        Raises:
            ImageProcessingError: Если произошла ошибка при конвертации.
        """
        try:
            # Преобразуем из PIL Image в массив NumPy
            numpy_image = np.array(pil_image)

            # Если изображение RGB, преобразуем в BGR (формат OpenCV)
            if len(numpy_image.shape) == 3 and numpy_image.shape[2] == 3:
                opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
            else:
                # Если изображение уже в оттенках серого или RGBA, просто используем его
                opencv_image = numpy_image

            return opencv_image

        except Exception as e:
            error_msg = f"Ошибка конвертации изображения из PIL в OpenCV: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def find_template(self, screen: Union[np.ndarray, Image.Image],
                      template: Union[str, np.ndarray],
                      threshold: float = 0.8,
                      scales: List[float] = None,
                      regions: List[Tuple[int, int, int, int]] = None) -> Optional[Dict]:
        """
        Ищет шаблон на экране с заданным порогом соответствия.

        Args:
            screen: Скриншот экрана как массив NumPy или объект PIL.Image.
            template: Путь к файлу шаблона или уже загруженный шаблон.
            threshold: Порог соответствия (от 0 до 1).
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Словарь с результатами поиска или None, если шаблон не найден.
            Формат словаря: {
                'confidence': float,  # Уверенность найденного совпадения
                'x': int,            # Координата X левого верхнего угла
                'y': int,            # Координата Y левого верхнего угла
                'w': int,            # Ширина шаблона
                'h': int,            # Высота шаблона
                'center_x': int,     # Координата X центра шаблона
                'center_y': int      # Координата Y центра шаблона
            }

        Raises:
            ImageProcessingError: Если произошла ошибка при поиске шаблона.
        """
        try:
            # Устанавливаем значения по умолчанию
            if scales is None:
                scales = [1.0]

            # Подготавливаем скриншот к поиску
            if isinstance(screen, Image.Image):
                screen_bgr = self.convert_pil_to_cv2(screen)
            else:
                screen_bgr = screen

            # Подготавливаем шаблон к поиску
            if isinstance(template, str):
                template_bgr = self.load_template(template)
            else:
                template_bgr = template

            best_result = None
            best_val = -1.0

            # Если регионы не указаны, используем весь экран
            if regions is None:
                regions = [(0, 0, screen_bgr.shape[1], screen_bgr.shape[0])]

            # Для каждого масштаба ищем шаблон
            for scale in scales:
                # Масштабируем шаблон, если масштаб отличается от 1.0
                if scale != 1.0:
                    width = int(template_bgr.shape[1] * scale)
                    height = int(template_bgr.shape[0] * scale)
                    resized_template = cv2.resize(template_bgr, (width, height),
                                                  interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR)
                else:
                    resized_template = template_bgr

                template_width = resized_template.shape[1]
                template_height = resized_template.shape[0]

                # Для каждого региона ищем шаблон
                for region in regions:
                    x, y, width, height = region

                    # Убеждаемся, что регион находится в пределах скриншота
                    if x < 0 or y < 0 or x + width > screen_bgr.shape[1] or y + height > screen_bgr.shape[0]:
                        continue

                    # Вырезаем регион из скриншота
                    region_bgr = screen_bgr[y:y + height, x:x + width]

                    # Ищем шаблон в регионе
                    result = cv2.matchTemplate(region_bgr, resized_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                    # Если нашли лучшее совпадение, сохраняем его
                    if max_val > best_val:
                        best_val = max_val
                        best_result = {
                            'confidence': float(max_val),
                            'x': x + max_loc[0],
                            'y': y + max_loc[1],
                            'w': template_width,
                            'h': template_height,
                            'center_x': x + max_loc[0] + template_width // 2,
                            'center_y': y + max_loc[1] + template_height // 2,
                            'scale': scale
                        }

            # Проверяем, превышает ли найденное совпадение порог
            if best_result and best_result['confidence'] >= threshold:
                self._log_debug(f"Шаблон найден с уверенностью {best_result['confidence']:.2f} на координатах "
                                f"({best_result['x']}, {best_result['y']})")
                return best_result
            else:
                self._log_debug(f"Шаблон не найден (максимальная уверенность: {best_val:.2f})")
                return None

        except Exception as e:
            error_msg = f"Ошибка при поиске шаблона: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def find_all_templates(self, screen: Union[np.ndarray, Image.Image],
                           template: Union[str, np.ndarray],
                           threshold: float = 0.8,
                           max_results: int = 10,
                           scales: List[float] = None,
                           regions: List[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        Ищет все вхождения шаблона на экране с заданным порогом соответствия.

        Args:
            screen: Скриншот экрана как массив NumPy или объект PIL.Image.
            template: Путь к файлу шаблона или уже загруженный шаблон.
            threshold: Порог соответствия (от 0 до 1).
            max_results: Максимальное количество результатов.
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Список словарей с результатами поиска (формат как у find_template).

        Raises:
            ImageProcessingError: Если произошла ошибка при поиске шаблонов.
        """
        try:
            # Устанавливаем значения по умолчанию
            if scales is None:
                scales = [1.0]

            # Подготавливаем скриншот к поиску
            if isinstance(screen, Image.Image):
                screen_bgr = self.convert_pil_to_cv2(screen)
            else:
                screen_bgr = screen

            # Подготавливаем шаблон к поиску
            if isinstance(template, str):
                template_bgr = self.load_template(template)
            else:
                template_bgr = template

            all_results = []

            # Если регионы не указаны, используем весь экран
            if regions is None:
                regions = [(0, 0, screen_bgr.shape[1], screen_bgr.shape[0])]

            # Для каждого масштаба ищем шаблоны
            for scale in scales:
                # Масштабируем шаблон, если масштаб отличается от 1.0
                if scale != 1.0:
                    width = int(template_bgr.shape[1] * scale)
                    height = int(template_bgr.shape[0] * scale)
                    resized_template = cv2.resize(template_bgr, (width, height),
                                                  interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR)
                else:
                    resized_template = template_bgr

                template_width = resized_template.shape[1]
                template_height = resized_template.shape[0]

                # Для каждого региона ищем шаблоны
                for region in regions:
                    x, y, width, height = region

                    # Убеждаемся, что регион находится в пределах скриншота
                    if x < 0 or y < 0 or x + width > screen_bgr.shape[1] or y + height > screen_bgr.shape[0]:
                        continue

                    # Вырезаем регион из скриншота
                    region_bgr = screen_bgr[y:y + height, x:x + width]

                    # Ищем шаблон в регионе
                    result = cv2.matchTemplate(region_bgr, resized_template, cv2.TM_CCOEFF_NORMED)

                    # Находим все точки, превышающие порог
                    locations = np.where(result >= threshold)

                    for pt in zip(*locations[::-1]):  # Переворачиваем, т.к. numpy возвращает (y, x)
                        # Добавляем результат
                        match_val = result[pt[1], pt[0]]
                        match_result = {
                            'confidence': float(match_val),
                            'x': x + pt[0],
                            'y': y + pt[1],
                            'w': template_width,
                            'h': template_height,
                            'center_x': x + pt[0] + template_width // 2,
                            'center_y': y + pt[1] + template_height // 2,
                            'scale': scale
                        }
                        all_results.append(match_result)

            # Сортируем результаты по уверенности (от большей к меньшей)
            all_results.sort(key=lambda r: r['confidence'], reverse=True)

            # Удаляем дубликаты (шаблоны, которые перекрываются)
            filtered_results = []
            for result in all_results:
                # Проверяем, не перекрывается ли этот результат с уже добавленными
                is_duplicate = False
                for filtered in filtered_results:
                    # Если центры шаблонов находятся близко друг к другу, считаем их дубликатами
                    distance = ((result['center_x'] - filtered['center_x']) ** 2 +
                                (result['center_y'] - filtered['center_y']) ** 2) ** 0.5
                    if distance < min(result['w'], result['h']) / 2:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    filtered_results.append(result)

                    # Если достигли максимального количества результатов, выходим из цикла
                    if len(filtered_results) >= max_results:
                        break

            self._log_debug(f"Найдено {len(filtered_results)} шаблонов")
            return filtered_results

        except Exception as e:
            error_msg = f"Ошибка при поиске всех шаблонов: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def find_multiple_templates(self, screen: Union[np.ndarray, Image.Image],
                                templates: List[Union[str, np.ndarray]],
                                threshold: float = 0.8,
                                scales: List[float] = None,
                                regions: List[Tuple[int, int, int, int]] = None) -> Dict[str, Dict]:
        """
        Ищет несколько разных шаблонов на экране и возвращает лучшее совпадение для каждого.

        Args:
            screen: Скриншот экрана как массив NumPy или объект PIL.Image.
            templates: Список путей к файлам шаблонов или уже загруженных шаблонов.
            threshold: Порог соответствия (от 0 до 1).
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Словарь с результатами поиска для каждого шаблона.
            Ключи - имена файлов шаблонов или индексы.
            Значения - словари с результатами поиска (или None, если шаблон не найден).

        Raises:
            ImageProcessingError: Если произошла ошибка при поиске шаблонов.
        """
        try:
            # Подготавливаем скриншот к поиску
            if isinstance(screen, Image.Image):
                screen_bgr = self.convert_pil_to_cv2(screen)
            else:
                screen_bgr = screen

            results = {}

            # Обрабатываем каждый шаблон
            for i, template in enumerate(templates):
                # Генерируем ключ для результата
                if isinstance(template, str):
                    key = os.path.basename(template)
                else:
                    key = f"template_{i}"

                # Ищем шаблон
                result = self.find_template(screen_bgr, template, threshold, scales, regions)
                results[key] = result

            return results

        except Exception as e:
            error_msg = f"Ошибка при поиске нескольких шаблонов: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def find_templates_async(self, screen: Union[np.ndarray, Image.Image],
                             templates: List[Union[str, np.ndarray]],
                             threshold: float = 0.8,
                             scales: List[float] = None,
                             regions: List[Tuple[int, int, int, int]] = None) -> Dict[str, Dict]:
        """
        Асинхронно ищет несколько разных шаблонов на экране, используя многопоточность.

        Args:
            screen: Скриншот экрана как массив NumPy или объект PIL.Image.
            templates: Список путей к файлам шаблонов или уже загруженных шаблонов.
            threshold: Порог соответствия (от 0 до 1).
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Словарь с результатами поиска для каждого шаблона (как у find_multiple_templates).

        Raises:
            ImageProcessingError: Если произошла ошибка при асинхронном поиске шаблонов.
        """
        try:
            # Подготавливаем скриншот к поиску
            if isinstance(screen, Image.Image):
                screen_bgr = self.convert_pil_to_cv2(screen)
            else:
                screen_bgr = screen

            # Создаем задачи для каждого шаблона
            future_to_template = {}
            results = {}

            for i, template in enumerate(templates):
                # Генерируем ключ для результата
                if isinstance(template, str):
                    key = os.path.basename(template)
                else:
                    key = f"template_{i}"

                # Создаем асинхронную задачу
                future = self.executor.submit(
                    self.find_template, screen_bgr, template, threshold, scales, regions
                )
                future_to_template[future] = key

            # Получаем результаты выполнения задач
            for future in future_to_template:
                key = future_to_template[future]
                try:
                    result = future.result()
                    results[key] = result
                except Exception as e:
                    self._log_error(f"Ошибка при асинхронном поиске шаблона {key}: {e}")
                    results[key] = None

            return results

        except Exception as e:
            error_msg = f"Ошибка при асинхронном поиске шаблонов: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def wait_for_template(self, get_screen_func, template: Union[str, np.ndarray],
                          timeout: float = 10.0, interval: float = 0.5,
                          threshold: float = 0.8, scales: List[float] = None,
                          regions: List[Tuple[int, int, int, int]] = None) -> Optional[Dict]:
        """
        Ожидает появления шаблона на экране в течение указанного времени.

        Args:
            get_screen_func: Функция для получения скриншота экрана.
            template: Путь к файлу шаблона или уже загруженный шаблон.
            timeout: Максимальное время ожидания в секундах.
            interval: Интервал между проверками в секундах.
            threshold: Порог соответствия (от 0 до 1).
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Словарь с результатами поиска или None, если шаблон не найден за отведенное время.

        Raises:
            ImageProcessingError: Если произошла ошибка при ожидании шаблона.
        """
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Получаем скриншот
                screen = get_screen_func()

                # Ищем шаблон
                result = self.find_template(screen, template, threshold, scales, regions)

                # Если шаблон найден, возвращаем результат
                if result:
                    return result

                # Ждем указанное время перед следующей попыткой
                time.sleep(interval)

            # Время истекло, шаблон не найден
            self._log_debug(f"Шаблон не найден за отведенное время ({timeout} сек)")
            return None

        except Exception as e:
            error_msg = f"Ошибка при ожидании шаблона: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def wait_for_any_template(self, get_screen_func, templates: List[Union[str, np.ndarray]],
                              timeout: float = 10.0, interval: float = 0.5,
                              threshold: float = 0.8, scales: List[float] = None,
                              regions: List[Tuple[int, int, int, int]] = None) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Ожидает появления любого из указанных шаблонов на экране.

        Args:
            get_screen_func: Функция для получения скриншота экрана.
            templates: Список путей к файлам шаблонов или уже загруженных шаблонов.
            timeout: Максимальное время ожидания в секундах.
            interval: Интервал между проверками в секундах.
            threshold: Порог соответствия (от 0 до 1).
            scales: Список масштабов для поиска шаблона (по умолчанию [1.0]).
            regions: Список регионов для поиска в формате (x, y, width, height).

        Returns:
            Кортеж (имя найденного шаблона, словарь с результатами поиска) или (None, None),
            если ни один шаблон не найден за отведенное время.

        Raises:
            ImageProcessingError: Если произошла ошибка при ожидании шаблонов.
        """
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Получаем скриншот
                screen = get_screen_func()

                # Ищем все шаблоны асинхронно
                results = self.find_templates_async(screen, templates, threshold, scales, regions)

                # Проверяем результаты
                for template_name, result in results.items():
                    if result:
                        # Нашли шаблон
                        self._log_debug(f"Шаблон '{template_name}' найден с уверенностью {result['confidence']:.2f}")
                        return template_name, result

                # Ждем указанное время перед следующей попыткой
                time.sleep(interval)

            # Время истекло, ни один шаблон не найден
            self._log_debug(f"Ни один шаблон не найден за отведенное время ({timeout} сек)")
            return None, None

        except Exception as e:
            error_msg = f"Ошибка при ожидании любого шаблона: {e}"
            self._log_error(error_msg)
            raise ImageProcessingError(error_msg)

    def clear_cache(self, template_path: str = None) -> None:
        """
        Очищает кэш шаблонов и скриншотов.

        Args:
            template_path: Путь к конкретному шаблону для очистки (если None, очищает весь кэш).
        """
        if template_path:
            # Очищаем кэш для конкретного шаблона
            if template_path in self._template_cache:
                del self._template_cache[template_path]
                self._log_debug(f"Кэш очищен для шаблона: {template_path}")
        else:
            # Очищаем весь кэш
            self._template_cache.clear()
            self._screenshot_cache.clear()
            self._log_debug("Весь кэш изображений очищен")

    def __del__(self):
        """
        Освобождает ресурсы при уничтожении объекта.
        """
        # Закрываем пул потоков
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

        # Очищаем кэш
        self.clear_cache()