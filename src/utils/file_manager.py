# b_maker/src/utils/file_manager.py
import os
from pathlib import Path

def create_bot_environment(bot_name: str) -> None:
    """
    Создает необходимые директории для нового бота.

    :param bot_name: Название бота.
    :raises Exception: Если не удалось создать директории.
    """
    try:
        base_path = Path("bots") / bot_name
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / "images").mkdir(exist_ok=True)
        # Дополнительно можно создать файлы конфигурации, логику сохранения сценария и т.п.
    except Exception as e:
        raise Exception(f"Ошибка при создании окружения для бота: {e}")
