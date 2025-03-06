# b_maker/src/adb/adb_controller.py
from ppadb.client import Client as AdbClient
import logging
from typing import Optional

class ADBController:
    """
    Класс для работы с ADB, управления эмуляторами LDP Player 9.
    Использует библиотеку ppadb для взаимодействия с ADB.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 5037, logger: Optional[logging.Logger] = None) -> None:
        """
        Инициализирует ADB клиент.

        :param host: Адрес ADB-сервера.
        :param port: Порт ADB-сервера.
        :param logger: Объект логирования.
        """
        self.logger = logger
        try:
            self.client = AdbClient(host=host, port=port)
            if self.logger:
                self.logger.info("ADB клиент успешно инициализирован")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка инициализации ADB клиента: {e}")
            raise e

    def get_device(self, device_id: str):
        """
        Возвращает устройство по его ID.

        :param device_id: Идентификатор устройства.
        :return: Устройство ADB.
        """
        try:
            device = self.client.device(device_id)
            if not device:
                raise Exception(f"Устройство с ID {device_id} не найдено")
            return device
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка получения устройства {device_id}: {e}")
            raise e

    def send_command(self, device_id: str, command: str) -> str:
        """
        Отправляет ADB-команду на указанное устройство.

        :param device_id: Идентификатор устройства.
        :param command: Команда для отправки.
        :return: Результат выполнения команды.
        """
        try:
            device = self.get_device(device_id)
            output = device.shell(command)
            if self.logger:
                self.logger.info(f"Команда '{command}' отправлена на устройство {device_id}")
            return output
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка отправки команды на устройство {device_id}: {e}")
            raise e
