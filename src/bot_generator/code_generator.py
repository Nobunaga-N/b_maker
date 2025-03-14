from typing import List, Dict, Any, Optional
import jinja2
import os
import json


class BotCodeGenerator:
    """
    Генератор Python-кода для ботов на основе настроек пользователя.
    Преобразует конфигурацию модулей в исполняемый скрипт Python.
    """

    def __init__(self, templates_dir: str = "templates"):
        """
        Инициализирует генератор кода.

        Args:
            templates_dir: Путь к директории с шаблонами.
        """
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_bot_code(self, bot_config: Dict[str, Any]) -> str:
        """
        Генерирует код бота на основе конфигурации.

        Args:
            bot_config: Словарь с конфигурацией бота.

        Returns:
            Строка с сгенерированным Python-кодом.
        """
        # Получаем основные настройки
        bot_name = bot_config.get("name", "unknown_bot")
        game = bot_config.get("game", "")
        modules = bot_config.get("modules", [])

        # Преобразуем модули в код
        module_code_blocks = self._generate_module_blocks(modules)

        # Загружаем основной шаблон
        template = self.env.get_template("bot_template.py.jinja")

        # Генерируем код
        code = template.render(
            bot_name=bot_name,
            game=game,
            modules=modules,
            module_code_blocks=module_code_blocks
        )

        return code

    def _generate_module_blocks(self, modules: List[Dict[str, Any]]) -> List[str]:
        """
        Генерирует блоки кода для каждого модуля.

        Args:
            modules: Список модулей из конфигурации.

        Returns:
            Список строк с кодом для каждого модуля.
        """
        blocks = []

        for i, module in enumerate(modules):
            module_type = module.get("type")

            # Определяем метод генерации на основе типа модуля
            if module_type == "activity":
                blocks.append(self._generate_activity_module(module, i))
            elif module_type == "click":
                blocks.append(self._generate_click_module(module, i))
            elif module_type == "swipe":
                blocks.append(self._generate_swipe_module(module, i))
            elif module_type == "image_search":
                blocks.append(self._generate_image_search_module(module, i))
            elif module_type == "time_sleep":
                blocks.append(self._generate_time_sleep_module(module, i))
            else:
                blocks.append(f"# Неподдерживаемый тип модуля: {module_type}")

        return blocks

    def _generate_activity_module(self, module: Dict[str, Any], index: int) -> str:
        """Генерирует код для модуля Activity."""
        template = self.env.get_template("activity_module.py.jinja")
        return template.render(module=module, index=index)

    def _generate_click_module(self, module: Dict[str, Any], index: int) -> str:
        """Генерирует код для модуля клика."""
        template = self.env.get_template("click_module.py.jinja")
        return template.render(module=module, index=index)

    def _generate_swipe_module(self, module: Dict[str, Any], index: int) -> str:
        """Генерирует код для модуля свайпа."""
        template = self.env.get_template("swipe_module.py.jinja")
        return template.render(module=module, index=index)

    def _generate_image_search_module(self, module: Dict[str, Any], index: int) -> str:
        """Генерирует код для модуля поиска изображений."""
        template = self.env.get_template("image_search_module.py.jinja")
        return template.render(module=module, index=index)

    def _generate_time_sleep_module(self, module: Dict[str, Any], index: int) -> str:
        """Генерирует код для модуля паузы."""
        template = self.env.get_template("time_sleep_module.py.jinja")
        return template.render(module=module, index=index)

    def save_generated_code(self, bot_name: str, code: str) -> str:
        """
        Сохраняет сгенерированный код в файл.

        Args:
            bot_name: Имя бота.
            code: Строка с кодом.

        Returns:
            Путь к сохраненному файлу.
        """
        # Создаем директорию для сгенерированного кода
        bot_dir = os.path.join("bots", bot_name)
        generated_dir = os.path.join(bot_dir, "generated")
        os.makedirs(generated_dir, exist_ok=True)

        # Сохраняем код в файл
        file_path = os.path.join(generated_dir, f"{bot_name}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        return file_path