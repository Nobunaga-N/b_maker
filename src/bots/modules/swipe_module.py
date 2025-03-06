# b_maker/src/bots/modules/swipe_module.py
from typing import Any

def swipe(x1: int, y1: int, x2: int, y2: int, description: str = "", sleep: float = 0.0) -> None:
    """
    Выполняет свайп с начальных координат (x1, y1) к конечным (x2, y2).

    :param x1: Начальная координата X.
    :param y1: Начальная координата Y.
    :param x2: Конечная координата X.
    :param y2: Конечная координата Y.
    :param description: Описание свайпа.
    :param sleep: Время задержки после свайпа.
    """
    try:
        print(f"Свайп с ({x1}, {y1}) на ({x2}, {y2}). {description}")
        if sleep:
            import time
            time.sleep(sleep)
    except Exception as e:
        print(f"Ошибка в модуле свайпа: {e}")
