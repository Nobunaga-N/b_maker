# src/utils/exceptions.py
"""
Модуль содержит пользовательские классы исключений для приложения.
Это позволяет более точно обрабатывать различные типы ошибок.
"""

class BotMakerError(Exception):
    """Базовый класс для исключений в приложении Bot Maker."""
    pass


class BotError(BotMakerError):
    """Базовый класс для исключений, связанных с ботами."""
    pass


class BotCreationError(BotError):
    """Исключение, связанное с созданием бота."""
    pass


class BotImportError(BotError):
    """Исключение, связанное с импортом бота."""
    pass


class BotExportError(BotError):
    """Исключение, связанное с экспортом бота."""
    pass


class BotDeleteError(BotError):
    """Исключение, связанное с удалением бота."""
    pass


class BotExecutionError(BotError):
    """Исключение, связанное с выполнением бота."""
    pass


class ModuleError(BotMakerError):
    """Базовый класс для исключений, связанных с модулями."""
    pass


class ModuleCreationError(ModuleError):
    """Исключение, связанное с созданием модуля."""
    pass


class ModuleExecutionError(ModuleError):
    """Исключение, связанное с выполнением модуля."""
    pass


class ConfigError(BotMakerError):
    """Базовый класс для исключений, связанных с конфигурацией."""
    pass


class ConfigLoadError(ConfigError):
    """Исключение, связанное с загрузкой конфигурации."""
    pass


class ConfigSaveError(ConfigError):
    """Исключение, связанное с сохранением конфигурации."""
    pass


class ResourceError(BotMakerError):
    """Базовый класс для исключений, связанных с ресурсами."""
    pass


class ResourceNotFoundError(ResourceError):
    """Исключение, связанное с отсутствием ресурса."""
    pass


class ADBError(BotMakerError):
    """Базовый класс для исключений, связанных с ADB."""
    pass


class ADBConnectionError(ADBError):
    """Исключение, связанное с подключением к ADB."""
    pass


class ADBCommandError(ADBError):
    """Исключение, связанное с выполнением команды ADB."""
    pass


class EmulatorError(BotMakerError):
    """Базовый класс для исключений, связанных с эмулятором."""
    pass


class EmulatorStartError(EmulatorError):
    """Исключение, связанное с запуском эмулятора."""
    pass


class EmulatorStopError(EmulatorError):
    """Исключение, связанное с остановкой эмулятора."""
    pass


class ImageProcessingError(BotMakerError):
    """Исключение, связанное с обработкой изображений."""
    pass


class UIError(BotMakerError):
    """Исключение, связанное с пользовательским интерфейсом."""
    pass