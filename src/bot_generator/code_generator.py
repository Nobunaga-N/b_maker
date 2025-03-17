# src/bot_generator/code_generator.py - добавление функции vars()

from typing import List, Dict, Any, Optional
import jinja2
import os
import json
from datetime import datetime


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

        # Добавляем функцию now() в глобальный контекст Jinja2
        self.env.globals['now'] = self.get_current_datetime

        # Добавляем функцию vars() для проверки существования переменных
        self.env.globals['vars'] = lambda: self.template_vars

        # Словарь для хранения переменных шаблона
        self.template_vars = {}

    def get_current_datetime(self):
        """
        Возвращает текущую дату и время в форматированном виде.

        Returns:
            Форматированная строка с текущей датой и временем.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        # Обновляем переменные шаблона
        self.template_vars = {
            'bot_name': bot_name,
            'game': game,
            'modules': modules,
            'module_code_blocks': module_code_blocks
        }

        # Проверим, есть ли activity_actions
        activity_module = None
        for module in modules:
            if module.get("type") == "activity" and module.get("continue_options"):
                activity_module = module
                break

        if activity_module:
            self.template_vars['activity_actions'] = "self.activity_continue_actions(self)"

        # Загружаем основной шаблон
        template = self.env.get_template("bot_template.py.jinja")

        # Генерируем код
        code = template.render(self.template_vars)

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

            try:
                # Определяем метод генерации на основе типа модуля
                block = None
                if module_type == "activity":
                    block = self._generate_activity_module(module, i)
                elif module_type == "click":
                    block = self._generate_click_module(module, i)
                elif module_type == "swipe":
                    block = self._generate_swipe_module(module, i)
                elif module_type == "image_search":
                    block = self._generate_image_search_module(module, i)
                elif module_type == "time_sleep":
                    block = self._generate_time_sleep_module(module, i)
                else:
                    block = f"# Неподдерживаемый тип модуля: {module_type}"

                # Предобработка блока для исправления форматирования
                if block:
                    # Удаляем комментарии о шаблонах
                    lines = block.split('\n')
                    if lines and lines[0].startswith('# Файл '):
                        lines = lines[1:]

                    # Удаляем пустые строки в начале
                    while lines and not lines[0].strip():
                        lines = lines[1:]

                    # Собираем обратно в строку
                    block = '\n'.join(lines)

                blocks.append(block)
            except Exception as e:
                print(f"Ошибка при генерации модуля {module_type}: {str(e)}")
                # Добавляем строку с ошибкой, чтобы не нарушать порядок блоков
                blocks.append(f"# Ошибка при генерации модуля {module_type}: {str(e)}")

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