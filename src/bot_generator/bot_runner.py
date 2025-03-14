# 2. Менеджер запуска ботов - управляет запуском и выполнением ботов
import subprocess
import logging
import threading
import time
from datetime import datetime
import signal
from typing import Dict, List, Optional, Tuple, Any
import os


class BotRunner:
    """
    Управляет запуском и выполнением скриптов ботов.
    """

    def __init__(self, logger=None):
        """
        Инициализирует менеджер запуска ботов.

        Args:
            logger: Объект логгера.
        """
        self.logger = logger or logging.getLogger("BotRunner")
        self.running_bots = {}  # {bot_id: {"process": process, "start_time": time, ...}}
        self.lock = threading.Lock()

    def start_bot(self, bot_path: str, emulator_id: str, cycles: int = 0,
                  max_work_time: int = 0, params: Dict[str, Any] = None) -> str:
        """
        Запускает бота асинхронно.

        Args:
            bot_path: Путь к скрипту бота.
            emulator_id: ID эмулятора.
            cycles: Количество циклов выполнения (0 = бесконечно).
            max_work_time: Максимальное время работы в минутах (0 = неограниченно).
            params: Дополнительные параметры для передачи боту.

        Returns:
            ID запущенного бота.
        """
        with self.lock:
            # Генерируем уникальный ID для бота
            bot_id = f"{os.path.basename(bot_path)}_{emulator_id}_{int(time.time())}"

            try:
                # Подготавливаем аргументы командной строки
                cmd = [
                    "python",
                    bot_path,
                    "--emulator", emulator_id
                ]

                if cycles > 0:
                    cmd.extend(["--cycles", str(cycles)])

                if max_work_time > 0:
                    cmd.extend(["--max-work-time", str(max_work_time)])

                # Добавляем дополнительные параметры, если они есть
                if params:
                    for key, value in params.items():
                        cmd.extend([f"--{key}", str(value)])

                # Создаем директорию для логов, если она не существует
                log_dir = "logs/bots"
                os.makedirs(log_dir, exist_ok=True)

                # Создаем файлы для логов
                log_file = os.path.join(log_dir, f"{bot_id}.log")
                err_file = os.path.join(log_dir, f"{bot_id}_error.log")

                # Запускаем бота в отдельном процессе
                with open(log_file, "w") as log_out, open(err_file, "w") as log_err:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log_out,
                        stderr=log_err,
                        universal_newlines=True,
                        # Отсоединяем процесс от родителя
                        start_new_session=True
                    )

                # Сохраняем информацию о запущенном боте
                self.running_bots[bot_id] = {
                    "process": process,
                    "start_time": datetime.now(),
                    "bot_path": bot_path,
                    "emulator_id": emulator_id,
                    "cycles": cycles,
                    "max_work_time": max_work_time,
                    "log_file": log_file,
                    "err_file": err_file,
                    "status": "running"
                }

                self.logger.info(f"Бот {bot_id} запущен на эмуляторе {emulator_id}")

                # Запускаем поток для мониторинга бота
                threading.Thread(
                    target=self._monitor_bot,
                    args=(bot_id,),
                    daemon=True
                ).start()

                return bot_id

            except Exception as e:
                self.logger.error(f"Ошибка запуска бота {bot_id}: {str(e)}")
                raise RuntimeError(f"Не удалось запустить бота: {str(e)}")

    def _monitor_bot(self, bot_id: str):
        """
        Мониторит состояние бота в отдельном потоке.

        Args:
            bot_id: ID бота.
        """
        with self.lock:
            if bot_id not in self.running_bots:
                return

            bot_info = self.running_bots[bot_id]
            process = bot_info["process"]
            max_work_time = bot_info["max_work_time"]

        # Цикл мониторинга
        while True:
            # Проверяем, работает ли процесс
            if process.poll() is not None:
                with self.lock:
                    if bot_id in self.running_bots:
                        # Обновляем статус бота
                        self.running_bots[bot_id]["status"] = "finished"
                        self.running_bots[bot_id]["end_time"] = datetime.now()
                        self.logger.info(f"Бот {bot_id} завершил работу с кодом {process.returncode}")
                break

            # Проверяем время выполнения
            if max_work_time > 0:
                with self.lock:
                    if bot_id in self.running_bots:
                        start_time = self.running_bots[bot_id]["start_time"]
                        elapsed_time = (datetime.now() - start_time).total_seconds() / 60

                        if elapsed_time >= max_work_time:
                            self.logger.info(f"Бот {bot_id} превысил максимальное время работы ({max_work_time} мин)")
                            self.stop_bot(bot_id)
                            break

            # Ждем перед следующей проверкой
            time.sleep(5)

    def stop_bot(self, bot_id: str) -> bool:
        """
        Останавливает работу бота.

        Args:
            bot_id: ID бота.

        Returns:
            True, если бот успешно остановлен, иначе False.
        """
        with self.lock:
            if bot_id not in self.running_bots:
                self.logger.warning(f"Бот {bot_id} не найден")
                return False

            bot_info = self.running_bots[bot_id]
            process = bot_info["process"]

            try:
                # Пытаемся мягко завершить процесс
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                    # Ждем немного для мягкого завершения
                    for _ in range(10):
                        if process.poll() is not None:
                            break
                        time.sleep(0.1)

                    # Если процесс все еще работает, завершаем принудительно
                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)

                # Обновляем статус бота
                self.running_bots[bot_id]["status"] = "stopped"
                self.running_bots[bot_id]["end_time"] = datetime.now()

                self.logger.info(f"Бот {bot_id} остановлен")
                return True

            except Exception as e:
                self.logger.error(f"Ошибка при остановке бота {bot_id}: {str(e)}")
                return False

    def get_bot_status(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает статус бота.

        Args:
            bot_id: ID бота.

        Returns:
            Словарь с информацией о боте или None, если бот не найден.
        """
        with self.lock:
            if bot_id not in self.running_bots:
                return None

            bot_info = self.running_bots[bot_id].copy()

            # Удаляем объект процесса перед возвратом
            if "process" in bot_info:
                process = bot_info["process"]
                del bot_info["process"]

                # Добавляем текущий статус процесса
                if process.poll() is None:
                    bot_info["process_status"] = "running"
                else:
                    bot_info["process_status"] = f"finished ({process.returncode})"

            # Добавляем время выполнения
            start_time = bot_info.get("start_time")
            end_time = bot_info.get("end_time", datetime.now())

            if start_time:
                elapsed_seconds = (end_time - start_time).total_seconds()
                bot_info["elapsed_time"] = {
                    "seconds": elapsed_seconds,
                    "formatted": self._format_elapsed_time(elapsed_seconds)
                }

            return bot_info

    def get_all_bots_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает статусы всех ботов.

        Returns:
            Словарь {bot_id: status_info}
        """
        result = {}

        with self.lock:
            for bot_id in list(self.running_bots.keys()):
                status = self.get_bot_status(bot_id)
                if status:
                    result[bot_id] = status

        return result

    def cleanup_finished_bots(self, max_age_minutes: int = 60) -> int:
        """
        Очищает информацию о завершенных ботах.

        Args:
            max_age_minutes: Максимальное время хранения информации в минутах.

        Returns:
            Количество удаленных записей.
        """
        now = datetime.now()
        count = 0

        with self.lock:
            for bot_id in list(self.running_bots.keys()):
                bot_info = self.running_bots[bot_id]

                # Проверяем, завершен ли бот
                if bot_info.get("status") in ["finished", "stopped"]:
                    # Проверяем время завершения
                    end_time = bot_info.get("end_time")
                    if end_time and (now - end_time).total_seconds() / 60 > max_age_minutes:
                        del self.running_bots[bot_id]
                        count += 1

        return count

    def _format_elapsed_time(self, seconds: float) -> str:
        """
        Форматирует время выполнения в читаемый вид.

        Args:
            seconds: Время в секундах.

        Returns:
            Отформатированная строка.
        """
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}ч {minutes}м {seconds}с"
        elif minutes > 0:
            return f"{minutes}м {seconds}с"
        else:
            return f"{seconds}с"