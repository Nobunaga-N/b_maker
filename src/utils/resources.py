# src/utils/resources.py
"""
Модуль для работы с ресурсами приложения.
Предоставляет удобные методы для получения путей к различным ресурсам.
"""

import os
from pathlib import Path
from typing import List, Optional


class Resources:
    """Класс для работы с ресурсами приложения."""

    # Базовые пути
    ASSETS_DIR = Path("assets")
    ICONS_DIR = ASSETS_DIR / "icons"
    STYLES_DIR = ASSETS_DIR / "styles"
    BOTS_DIR = Path("bots")
    CONFIG_DIR = Path("config")

    @classmethod
    def get_icon_path(cls, icon_name: str) -> str:
        """
        Возвращает полный путь к иконке.

        Args:
            icon_name: Имя иконки без расширения или с расширением

        Returns:
            Полный путь к файлу иконки
        """
        # Добавляем расширение .svg, если его нет
        if not icon_name.endswith(('.svg', '.png', '.jpg', '.jpeg')):
            icon_name = f"{icon_name}.svg"

        return str(cls.ICONS_DIR / icon_name)

    @classmethod
    def get_style_path(cls, style_name: str) -> str:
        """
        Возвращает полный путь к файлу стиля.

        Args:
            style_name: Имя файла стиля без расширения или с расширением

        Returns:
            Полный путь к файлу стиля
        """
        # Добавляем расширение .qss, если его нет
        if not style_name.endswith('.qss'):
            style_name = f"{style_name}.qss"

        return str(cls.STYLES_DIR / style_name)

    @classmethod
    def get_bot_path(cls, bot_name: str) -> str:
        """
        Возвращает полный путь к папке бота.

        Args:
            bot_name: Имя бота

        Returns:
            Полный путь к папке бота
        """
        return str(cls.BOTS_DIR / bot_name)

    @classmethod
    def get_bot_config_path(cls, bot_name: str) -> str:
        """
        Возвращает полный путь к файлу конфигурации бота.

        Args:
            bot_name: Имя бота

        Returns:
            Полный путь к файлу конфигурации бота
        """
        return str(cls.BOTS_DIR / bot_name / "config.json")

    @classmethod
    def get_bot_images_dir(cls, bot_name: str) -> str:
        """
        Возвращает полный путь к папке с изображениями бота.

        Args:
            bot_name: Имя бота

        Returns:
            Полный путь к папке с изображениями бота
        """
        return str(cls.BOTS_DIR / bot_name / "images")

    @classmethod
    def get_config_path(cls, config_name: str) -> str:
        """
        Возвращает полный путь к файлу конфигурации приложения.

        Args:
            config_name: Имя файла конфигурации без расширения или с расширением

        Returns:
            Полный путь к файлу конфигурации
        """
        # Добавляем расширение .json, если его нет
        if not config_name.endswith('.json'):
            config_name = f"{config_name}.json"

        return str(cls.CONFIG_DIR / config_name)

    @classmethod
    def ensure_dir_exists(cls, dir_path: str) -> bool:
        """
        Проверяет существование директории и создает ее, если она не существует.

        Args:
            dir_path: Путь к директории

        Returns:
            True, если директория существует или была успешно создана, иначе False
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception:
            return False

    @classmethod
    def list_bots(cls) -> List[str]:
        """
        Возвращает список имен всех ботов.

        Returns:
            Список имен ботов
        """
        if not os.path.exists(cls.BOTS_DIR):
            return []

        return [d for d in os.listdir(cls.BOTS_DIR)
                if os.path.isdir(os.path.join(cls.BOTS_DIR, d))]

    @classmethod
    def bot_exists(cls, bot_name: str) -> bool:
        """
        Проверяет существование бота.

        Args:
            bot_name: Имя бота

        Returns:
            True, если бот существует, иначе False
        """
        return os.path.exists(cls.get_bot_path(bot_name))

    @classmethod
    def get_available_games(cls) -> List[str]:
        """
        Возвращает список доступных игр из конфигурации.

        Returns:
            Список названий игр или пустой список, если конфигурация не найдена
        """
        games_config_path = cls.get_config_path("games_activities")

        if not os.path.exists(games_config_path):
            return []

        try:
            import json
            with open(games_config_path, 'r', encoding='utf-8') as f:
                games_data = json.load(f)
                return list(games_data.keys())
        except Exception:
            return []