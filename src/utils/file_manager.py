# src/utils/file_manager.py
"""
Модуль для работы с файловой системой приложения.
Предоставляет функции для создания, импорта и экспорта ботов.
"""

import os
import json
import shutil
import zipfile
from typing import Dict, Any, Optional, List, Tuple

from src.utils.resources import Resources


def create_bot_environment(bot_name: str) -> bool:
    """
    Создает необходимые директории и файлы для нового бота.

    Args:
        bot_name: Название бота.

    Returns:
        True, если окружение успешно создано, иначе False.

    Raises:
        Exception: Если не удалось создать директории или файлы.
    """
    try:
        # Получаем пути через класс ресурсов
        bot_path = Resources.get_bot_path(bot_name)
        images_path = Resources.get_bot_images_dir(bot_name)
        config_path = Resources.get_bot_config_path(bot_name)

        # Создаем директории
        Resources.ensure_dir_exists(bot_path)
        Resources.ensure_dir_exists(images_path)

        # Создаем базовый конфигурационный файл
        if not os.path.exists(config_path):
            default_config = {
                "name": bot_name,
                "game": "",
                "modules": []
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)

        return True
    except Exception as e:
        raise Exception(f"Ошибка при создании окружения для бота: {e}")


def save_bot_config(bot_name: str, config_data: Dict[str, Any]) -> bool:
    """
    Сохраняет конфигурацию бота в JSON-файл.

    Args:
        bot_name: Название бота.
        config_data: Словарь с конфигурацией бота.

    Returns:
        True, если конфигурация успешно сохранена, иначе False.
    """
    try:
        config_path = Resources.get_bot_config_path(bot_name)

        # Создаем директории, если они не существуют
        bot_path = Resources.get_bot_path(bot_name)
        Resources.ensure_dir_exists(bot_path)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

        return True
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации бота: {e}")
        return False


def load_bot_config(bot_name: str) -> Optional[Dict[str, Any]]:
    """
    Загружает конфигурацию бота из JSON-файла.

    Args:
        bot_name: Название бота.

    Returns:
        Словарь с конфигурацией бота или None, если произошла ошибка.
    """
    try:
        config_path = Resources.get_bot_config_path(bot_name)

        if not os.path.exists(config_path):
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации бота: {e}")
        return None


def export_bot(bot_name: str, target_path: str) -> bool:
    """
    Экспортирует бота в ZIP-архив.

    Args:
        bot_name: Название бота.
        target_path: Путь для сохранения архива.

    Returns:
        True, если бот успешно экспортирован, иначе False.
    """
    try:
        bot_path = Resources.get_bot_path(bot_name)

        if not os.path.exists(bot_path):
            return False

        # Если путь к архиву не указан, создаем его в текущей директории
        if not target_path:
            target_path = f"{bot_name}.zip"

        # Создаем ZIP-архив
        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(bot_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Записываем файл относительно директории бота
                    zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(bot_path)))

        return True
    except Exception as e:
        print(f"Ошибка при экспорте бота: {e}")
        return False


def import_bot(source_path: str, new_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Импортирует бота из ZIP-архива.

    Args:
        source_path: Путь к ZIP-архиву с ботом.
        new_name: Новое название для бота (опционально).

    Returns:
        Кортеж (успех, имя_бота), где успех - True если бот успешно импортирован,
        имя_бота - название импортированного бота или сообщение об ошибке.
    """
    try:
        if not os.path.exists(source_path) or not source_path.endswith('.zip'):
            return False, "Указанный файл не существует или не является ZIP-архивом."

        # Создаем временную директорию для распаковки
        temp_dir = os.path.join(os.path.dirname(source_path), "temp_bot_import")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Распаковываем архив
        with zipfile.ZipFile(source_path, 'r') as zipf:
            zipf.extractall(temp_dir)

        # Определяем имя бота
        try:
            # Ищем файл config.json
            config_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file == "config.json":
                        config_files.append(os.path.join(root, file))

            if not config_files:
                shutil.rmtree(temp_dir)
                return False, "В архиве не найден файл конфигурации бота."

            # Берем первый найденный config.json
            with open(config_files[0], 'r', encoding='utf-8') as f:
                bot_config = json.load(f)
                original_name = bot_config.get("name", "")

            if not original_name:
                shutil.rmtree(temp_dir)
                return False, "В файле конфигурации не указано имя бота."

            # Определяем окончательное имя бота
            bot_name = new_name if new_name else original_name

            # Проверяем, существует ли бот с таким именем
            if Resources.bot_exists(bot_name) and not new_name:
                shutil.rmtree(temp_dir)
                return False, f"Бот с именем '{bot_name}' уже существует."

            # Копируем файлы во временной директории в целевую директорию
            bot_dir = Resources.get_bot_path(bot_name)
            if os.path.exists(bot_dir):
                shutil.rmtree(bot_dir)

            # Находим корневую директорию бота в распакованном архиве
            bot_root = os.path.dirname(config_files[0])

            # Копируем содержимое
            shutil.copytree(bot_root, bot_dir)

            # Если имя бота изменилось, обновляем config.json
            if new_name:
                config_path = Resources.get_bot_config_path(bot_name)
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config["name"] = new_name
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)

            # Удаляем временную директорию
            shutil.rmtree(temp_dir)

            return True, bot_name
        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False, f"Ошибка при обработке архива: {e}"

    except Exception as e:
        return False, f"Ошибка при импорте бота: {e}"


def delete_bot(bot_name: str) -> bool:
    """
    Удаляет бота.

    Args:
        bot_name: Название бота.

    Returns:
        True, если бот успешно удален, иначе False.
    """
    try:
        bot_path = Resources.get_bot_path(bot_name)

        if not os.path.exists(bot_path):
            return False

        shutil.rmtree(bot_path)
        return True
    except Exception as e:
        print(f"Ошибка при удалении бота: {e}")
        return False


def rename_bot(old_name: str, new_name: str) -> bool:
    """
    Переименовывает бота.

    Args:
        old_name: Текущее название бота.
        new_name: Новое название бота.

    Returns:
        True, если бот успешно переименован, иначе False.
    """
    try:
        old_path = Resources.get_bot_path(old_name)
        new_path = Resources.get_bot_path(new_name)

        if not os.path.exists(old_path):
            return False

        if os.path.exists(new_path):
            return False

        # Переименовываем директорию
        os.rename(old_path, new_path)

        # Обновляем config.json
        config_path = Resources.get_bot_config_path(new_name)
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config["name"] = new_name
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)

        return True
    except Exception as e:
        print(f"Ошибка при переименовании бота: {e}")
        return False


def copy_bot(source_name: str, target_name: str) -> bool:
    """
    Копирует бота с новым именем.

    Args:
        source_name: Исходное название бота.
        target_name: Новое название для копии бота.

    Returns:
        True, если бот успешно скопирован, иначе False.
    """
    try:
        source_path = Resources.get_bot_path(source_name)
        target_path = Resources.get_bot_path(target_name)

        if not os.path.exists(source_path):
            return False

        if os.path.exists(target_path):
            return False

        # Копируем директорию
        shutil.copytree(source_path, target_path)

        # Обновляем config.json
        config_path = Resources.get_bot_config_path(target_name)
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config["name"] = target_name
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)

        return True
    except Exception as e:
        print(f"Ошибка при копировании бота: {e}")
        return False


def save_image_for_bot(bot_name: str, image_path: str, image_name: Optional[str] = None) -> bool:
    """
    Сохраняет изображение для бота.

    Args:
        bot_name: Название бота.
        image_path: Путь к изображению.
        image_name: Новое название для изображения (опционально).

    Returns:
        True, если изображение успешно сохранено, иначе False.
    """
    try:
        images_dir = Resources.get_bot_images_dir(bot_name)
        Resources.ensure_dir_exists(images_dir)

        # Если имя не указано, используем оригинальное имя файла
        if not image_name:
            image_name = os.path.basename(image_path)

        # Копируем файл
        target_path = os.path.join(images_dir, image_name)
        shutil.copy2(image_path, target_path)

        return True
    except Exception as e:
        print(f"Ошибка при сохранении изображения для бота: {e}")
        return False


def get_bot_images(bot_name: str) -> List[str]:
    """
    Возвращает список изображений бота.

    Args:
        bot_name: Название бота.

    Returns:
        Список имен файлов изображений.
    """
    try:
        images_dir = Resources.get_bot_images_dir(bot_name)

        if not os.path.exists(images_dir):
            return []

        # Получаем только файлы изображений
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        images = []

        for file in os.listdir(images_dir):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                images.append(file)

        return images
    except Exception as e:
        print(f"Ошибка при получении списка изображений бота: {e}")
        return []


# Дополнение к src/utils/file_manager.py

def validate_imported_bot(zip_path: str) -> Tuple[bool, str]:
    """
    Проверяет архив с ботом на корректность перед импортом.

    Args:
        zip_path: Путь к ZIP-архиву

    Returns:
        Кортеж (результат, сообщение)
    """
    try:
        if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
            return False, "Указанный файл не является ZIP-архивом."

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Проверяем наличие config.json
            config_files = [f for f in zipf.namelist() if f.endswith('config.json')]
            if not config_files:
                return False, "В архиве отсутствует файл конфигурации бота."

            # Проверяем содержимое config.json
            with zipf.open(config_files[0]) as config_file:
                try:
                    config = json.load(config_file)
                    if not config.get("name"):
                        return False, "В конфигурации бота отсутствует имя."
                    if not config.get("modules"):
                        return False, "В конфигурации бота отсутствуют модули."
                except json.JSONDecodeError:
                    return False, "Файл конфигурации бота содержит некорректный JSON."

            # Проверяем наличие используемых изображений
            if 'images' in zipf.namelist():
                image_files = [f for f in zipf.namelist() if f.startswith('images/')]

                # Проверяем модули поиска изображений
                for module in config.get("modules", []):
                    if module.get("type") == "image_search":
                        for image in module.get("images", []):
                            image_path = os.path.join('images', image)
                            if image_path not in zipf.namelist():
                                return False, f"В архиве отсутствует изображение {image}, используемое в модуле поиска."

        return True, "Архив прошел проверку."

    except Exception as e:
        return False, f"Ошибка при проверке архива: {str(e)}"