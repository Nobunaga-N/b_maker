# b_maker/src/bots/script_generator.py
from typing import List, Dict

def generate_script(modules: List[Dict[str, any]]) -> str:
    """
    Генерирует скрипт для бота на основе списка модулей.

    :param modules: Список модулей с параметрами.
    :return: Сгенерированный скрипт в виде строки.
    """
    script_lines = []
    for module in modules:
        module_type = module.get("type")
        if module_type == "click":
            x = module.get("x")
            y = module.get("y")
            desc = module.get("description", "")
            sleep_time = module.get("sleep", "0.0")
            # Формирование строки для модуля клика
            line = f'click(x={x}, y={y}, description="{desc}", sleep={sleep_time})'
            script_lines.append(line)
        # Здесь можно добавить обработку других типов модулей (swipe, image_search, activity и т.д.)
    return "\n".join(script_lines)
