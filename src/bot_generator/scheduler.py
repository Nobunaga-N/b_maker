from datetime import datetime
import time
import threading
import heapq
from typing import List, Dict, Any, Optional, Callable
import logging


class BotScheduler:
    """
    Планировщик для управления очередью ботов и их запуском по расписанию.
    """

    def __init__(self, bot_runner, logger=None):
        """
        Инициализирует планировщик ботов.

        Args:
            bot_runner: Экземпляр BotRunner для запуска ботов.
            logger: Объект логгера.
        """
        self.bot_runner = bot_runner
        self.logger = logger or logging.getLogger("BotScheduler")
        self.queue = []  # heapq для очереди [(timestamp, bot_config), ...]
        self.lock = threading.Lock()
        self.running = False
        self.scheduler_thread = None

    def add_to_queue(self, bot_config: Dict[str, Any], scheduled_time: Optional[datetime] = None) -> str:
        """
        Добавляет бота в очередь.

        Args:
            bot_config: Конфигурация бота для запуска.
            scheduled_time: Время запуска. Если None, бот будет запущен при первой возможности.

        Returns:
            ID задачи в очереди.
        """
        with self.lock:
            # Генерируем ID задачи
            task_id = f"task_{int(time.time())}_{len(self.queue)}"

            # Устанавливаем время запуска
            if scheduled_time is None:
                scheduled_time = datetime.now()

            # Создаем конфигурацию задачи
            task_config = {
                "id": task_id,
                "bot_config": bot_config,
                "scheduled_time": scheduled_time,
                "status": "queued",
                "created_at": datetime.now()
            }

            # Добавляем в очередь (heapq сортирует по первому элементу)
            heapq.heappush(self.queue, (scheduled_time.timestamp(), task_config))

            self.logger.info(f"Бот {bot_config.get('name')} добавлен в очередь с ID {task_id}")

            return task_id

    def remove_from_queue(self, task_id: str) -> bool:
        """
        Удаляет задачу из очереди.

        Args:
            task_id: ID задачи для удаления.

        Returns:
            True, если задача найдена и удалена, иначе False.
        """
        with self.lock:
            # Ищем задачу в очереди
            for i, (_, task_config) in enumerate(self.queue):
                if task_config["id"] == task_id:
                    # Удаляем задачу
                    self.queue.pop(i)

                    # Перестраиваем очередь
                    heapq.heapify(self.queue)

                    self.logger.info(f"Задача {task_id} удалена из очереди")
                    return True

            self.logger.warning(f"Задача {task_id} не найдена в очереди")
            return False

    def get_queue(self) -> List[Dict[str, Any]]:
        """
        Возвращает список задач в очереди.

        Returns:
            Список конфигураций задач.
        """
        with self.lock:
            # Копируем список для безопасного возврата
            return [task_config for _, task_config in sorted(self.queue)]

    def start_scheduler(self):
        """
        Запускает поток планировщика.
        """
        with self.lock:
            if self.running:
                self.logger.warning("Планировщик уже запущен")
                return

            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self.scheduler_thread.start()

            self.logger.info("Планировщик запущен")

    def stop_scheduler(self):
        """
        Останавливает поток планировщика.
        """
        with self.lock:
            if not self.running:
                self.logger.warning("Планировщик не запущен")
                return

            self.running = False

            # Ждем завершения потока
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=10)
                self.scheduler_thread = None

            self.logger.info("Планировщик остановлен")

    def _scheduler_loop(self):
        """
        Основной цикл планировщика.
        Выполняется в отдельном потоке и проверяет задачи для запуска.
        """
        while self.running:
            try:
                now = datetime.now().timestamp()

                with self.lock:
                    # Проверяем, есть ли задачи для запуска
                    if self.queue and self.queue[0][0] <= now:
                        # Получаем задачу с наименьшим временем запуска
                        _, task_config = heapq.heappop(self.queue)

                        # Запускаем задачу в отдельном потоке, чтобы не блокировать планировщик
                        threading.Thread(
                            target=self._execute_task,
                            args=(task_config,),
                            daemon=True
                        ).start()

            except Exception as e:
                self.logger.error(f"Ошибка в цикле планировщика: {str(e)}")

            # Ждем перед следующей проверкой
            time.sleep(1)

    def _execute_task(self, task_config: Dict[str, Any]):
        """
        Выполняет задачу из очереди.

        Args:
            task_config: Конфигурация задачи.
        """
        try:
            bot_config = task_config["bot_config"]
            task_id = task_config["id"]

            self.logger.info(f"Выполнение задачи {task_id} для бота {bot_config.get('name')}")

            # Получаем параметры запуска
            bot_path = bot_config.get("path")
            emulator_id = bot_config.get("emulator_id")
            cycles = bot_config.get("cycles", 0)
            max_work_time = bot_config.get("max_work_time", 0)
            params = bot_config.get("params", {})

            # Запускаем бота
            bot_id = self.bot_runner.start_bot(
                bot_path=bot_path,
                emulator_id=emulator_id,
                cycles=cycles,
                max_work_time=max_work_time,
                params=params
            )

            # Обновляем статус задачи
            task_config["status"] = "running"
            task_config["bot_id"] = bot_id
            task_config["started_at"] = datetime.now()

            self.logger.info(f"Задача {task_id} запущена с ID бота {bot_id}")

        except Exception as e:
            self.logger.error(f"Ошибка при выполнении задачи {task_config.get('id')}: {str(e)}")
            task_config["status"] = "error"
            task_config["error"] = str(e)