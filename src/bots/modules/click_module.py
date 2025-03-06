# b_maker/src/bots/modules/click_module.py
from typing import Any


def click(x: int, y: int, description: str = "", sleep: float = 0.0) -> None:
    """
    Выполняет клик по указанным координатам.

    :param x: Координата X.
    :param y: Координата Y.
    :param description: Описание клика.
    :param sleep: Время задержки после клика.
    """
    try:
        print(f"Клик по координатам ({x}, {y}). {description}")
        if sleep:
            import time
            time.sleep(sleep)
    except Exception as e:
        print(f"Ошибка в модуле клика: {e}")
