# src/gui/manager_page.py
"""
Модуль содержит класс страницы менеджера ботов.
Эта страница позволяет управлять ботами: запускать, останавливать, настраивать.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSplitter,
    QMessageBox, QFileDialog, QPushButton, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush

from src.utils.resources import Resources
from src.utils.style_constants import MAIN_FRAME_STYLE
from src.utils.ui_factory import create_title_label, create_accent_button
from src.gui.widgets import ManagerQueueWidget, BotListWidget
from src.gui.dialogs import BotSettingsDialog
from src.controllers import BotManagerController


class ManagerPage(QWidget):
    """
    Страница менеджера ботов.
    Содержит менеджер очереди ботов и список доступных ботов.
    """
    # Сигналы для оповещения о смене страницы
    createBotRequested = pyqtSignal(str)  # Запрос на создание бота
    editBotRequested = pyqtSignal(str)  # Запрос на редактирование бота (имя бота)

    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger
        self.controller = BotManagerController(logger)
        self.setup_ui()
        self.setup_connections()
        self.load_bots()

    def setup_ui(self):
        """Настраивает пользовательский интерфейс страницы"""
        self.setStyleSheet("background-color: #000000;")

        # Основной layout страницы
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Создаем разделитель для возможности изменения размеров областей
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Создаем фреймы для менеджера и списка ботов
        self.manager_frame = self._create_manager_frame()
        self.bots_frame = self._create_bots_frame()

        # Добавляем фреймы на разделитель
        self.splitter.addWidget(self.manager_frame)
        self.splitter.addWidget(self.bots_frame)

        # Устанавливаем начальные размеры
        self.splitter.setSizes([800, 350])

        # Добавляем разделитель на страницу
        main_layout.addWidget(self.splitter)

    def _create_manager_frame(self):
        """
        Создает фрейм с менеджером ботов.
        Оптимизирован для экономии пространства и улучшения UX.
        """
        manager_frame = QFrame()
        manager_frame.setStyleSheet(MAIN_FRAME_STYLE)
        manager_layout = QVBoxLayout(manager_frame)
        manager_layout.setContentsMargins(15, 15, 15, 15)
        manager_layout.setSpacing(10)

        # Заголовок с кнопками управления
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Заголовок
        manager_title = create_title_label("Менеджер ботов", 18)
        header_layout.addWidget(manager_title)

        header_layout.addStretch(1)  # Растягиваем пространство между заголовком и кнопками

        # Кнопки управления
        self.btn_settings = create_accent_button("Настройки", Resources.get_icon_path("settings"))
        self.btn_settings.setToolTip("Настройки параметров выбранного бота")

        self.btn_start_queue = create_accent_button("Запустить", Resources.get_icon_path("play-all"))
        self.btn_start_queue.setToolTip("Запустить очередь ботов")

        self.btn_clear_queue = create_accent_button("Очистить", Resources.get_icon_path("clear-all"))
        self.btn_clear_queue.setToolTip("Очистить очередь ботов")

        header_layout.addWidget(self.btn_settings)
        header_layout.addWidget(self.btn_start_queue)
        header_layout.addWidget(self.btn_clear_queue)

        manager_layout.addLayout(header_layout)

        # Добавляем разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #333;")
        manager_layout.addWidget(separator)

        # Очередь ботов (занимает основную часть пространства)
        queue_section = QVBoxLayout()
        queue_section.setSpacing(5)

        queue_label = create_title_label("Очередь ботов:", 14)
        queue_section.addWidget(queue_label)

        # Создаем виджет очереди менеджера
        self.queue_tree = ManagerQueueWidget(self)
        queue_section.addWidget(self.queue_tree, 1)  # Растягиваем по вертикали

        manager_layout.addLayout(queue_section, 1)  # Растягиваем по вертикали

        return manager_frame

    def _create_bots_frame(self):
        """Создает фрейм со списком ботов"""
        bots_frame = QFrame()
        bots_frame.setStyleSheet(MAIN_FRAME_STYLE)
        bots_layout = QVBoxLayout(bots_frame)
        bots_layout.setContentsMargins(15, 15, 15, 15)
        bots_layout.setSpacing(10)

        # Заголовок с кнопками управления
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        bots_title = create_title_label("Список ботов", 16)
        header_layout.addWidget(bots_title)

        header_layout.addStretch(1)  # Растягиваем пространство между заголовком и кнопками

        # Кнопка создания нового бота
        self.btn_create_bot = create_accent_button("Создать бота", Resources.get_icon_path("add"))
        self.btn_create_bot.setToolTip("Создать нового бота")
        header_layout.addWidget(self.btn_create_bot)

        bots_layout.addLayout(header_layout)

        # Список ботов
        self.bot_list = BotListWidget(self)
        bots_layout.addWidget(self.bot_list, 1)  # Растягиваем по вертикали

        # Кнопки управления ботами (в горизонтальном ряду)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        # Создаем кнопки для управления списком ботов
        self.btn_edit_bot = QPushButton("Редактировать")
        self.btn_edit_bot.setIcon(QIcon(Resources.get_icon_path("edit")))
        self.btn_edit_bot.setToolTip("Редактировать выбранного бота")

        self.btn_add_to_manager = QPushButton("В менеджер")
        self.btn_add_to_manager.setIcon(QIcon(Resources.get_icon_path("add-to-queue")))
        self.btn_add_to_manager.setToolTip("Добавить выбранного бота в менеджер")

        self.btn_delete_bot = QPushButton("Удалить")
        self.btn_delete_bot.setIcon(QIcon(Resources.get_icon_path("delete")))
        self.btn_delete_bot.setToolTip("Удалить выбранного бота")

        self.btn_export_bot = QPushButton("Экспорт")
        self.btn_export_bot.setIcon(QIcon(Resources.get_icon_path("export")))
        self.btn_export_bot.setToolTip("Экспортировать выбранного бота")

        self.btn_import_bot = QPushButton("Импорт")
        self.btn_import_bot.setIcon(QIcon(Resources.get_icon_path("import")))
        self.btn_import_bot.setToolTip("Импортировать бота")

        buttons_layout.addWidget(self.btn_edit_bot)
        buttons_layout.addWidget(self.btn_add_to_manager)
        buttons_layout.addWidget(self.btn_delete_bot)
        buttons_layout.addWidget(self.btn_export_bot)
        buttons_layout.addWidget(self.btn_import_bot)
        buttons_layout.addStretch(1)  # Добавляем гибкий элемент для выравнивания

        bots_layout.addLayout(buttons_layout)

        return bots_frame

    def setup_connections(self):
        """Настраивает соединения сигналов и слотов"""
        # Соединения для контроллера
        self.controller.botsLoaded.connect(self.on_bots_loaded)
        self.controller.botDeleted.connect(self.on_bot_deleted)
        self.controller.botImported.connect(self.on_bot_imported)

        # Соединения для кнопок на панели менеджера
        self.btn_settings.clicked.connect(self.show_settings_dialog)
        self.btn_start_queue.clicked.connect(self.start_queue)
        self.btn_clear_queue.clicked.connect(self.clear_queue)

        # Соединения для кнопок на панели списка ботов
        self.btn_create_bot.clicked.connect(lambda: self.createBotRequested.emit(""))
        self.btn_edit_bot.clicked.connect(self.edit_selected_bot)
        self.btn_add_to_manager.clicked.connect(self.add_selected_bot_to_manager)
        self.btn_delete_bot.clicked.connect(self.delete_selected_bot)
        self.btn_export_bot.clicked.connect(self.export_selected_bot)
        self.btn_import_bot.clicked.connect(self.import_bot)

        # Соединения для виджета списка ботов
        self.bot_list.botEditRequested.connect(self.on_bot_edit_requested)
        self.bot_list.botAddToManagerRequested.connect(self.on_bot_add_to_manager_requested)
        self.bot_list.botDeleteRequested.connect(self.on_bot_delete_requested)
        self.bot_list.botExportRequested.connect(self.on_bot_export_requested)
        self.bot_list.botImportRequested.connect(self.import_bot)

        # Соединения для виджета очереди
        self.queue_tree.botStartRequested.connect(self.on_bot_start_requested)
        self.queue_tree.botStopRequested.connect(self.on_bot_stop_requested)
        self.queue_tree.botDuplicateRequested.connect(self.on_bot_duplicate_requested)
        self.queue_tree.emulatorConsoleRequested.connect(self.on_emulator_console_requested)
        self.queue_tree.emulatorStopRequested.connect(self.on_emulator_stop_requested)
        self.queue_tree.emulatorRestartRequested.connect(self.on_emulator_restart_requested)

    # ======== Методы обработки событий от контроллера ========
    def on_bots_loaded(self, bots_data):
        """Обрабатывает загрузку списка ботов"""
        self.bot_list.load_bots(bots_data)

    def on_bot_deleted(self, bot_name):
        """Обрабатывает удаление бота"""
        self.bot_list.handle_bot_deleted(bot_name)

    def on_bot_imported(self, bot_name, game_name):
        """Обрабатывает импорт бота"""
        self.bot_list.add_bot(bot_name, game_name)

    # ======== Методы обработки событий от виджета списка ботов ========
    def on_bot_edit_requested(self, bot_name):
        """Обрабатывает запрос на редактирование бота"""
        self.edit_bot(bot_name)

    def on_bot_add_to_manager_requested(self, bot_name, game_name):
        """Обрабатывает запрос на добавление бота в менеджер"""
        self.add_bot_to_manager(bot_name, game_name)

    def on_bot_delete_requested(self, bot_name):
        """Обрабатывает запрос на удаление бота"""
        self.delete_bot(bot_name)

    def on_bot_export_requested(self, bot_name):
        """Обрабатывает запрос на экспорт бота"""
        self.export_bot(bot_name)

    # ======== Методы обработки событий от виджета очереди ========
    def on_bot_start_requested(self, bot_name):
        """Обрабатывает запрос на запуск бота"""
        self.controller.start_bot(bot_name)

    def on_bot_stop_requested(self, bot_name):
        """Обрабатывает запрос на остановку бота"""
        self.controller.stop_bot(bot_name)

    def on_bot_duplicate_requested(self, bot_name):
        """Обрабатывает запрос на дублирование бота"""
        # Здесь должна быть реализация дублирования бота
        print(f"Дублирование бота {bot_name} (заглушка)")

    def on_emulator_console_requested(self, emu_id):
        """Обрабатывает запрос на открытие консоли эмулятора"""
        print(f"Открытие консоли для эмулятора {emu_id} (заглушка)")

    def on_emulator_stop_requested(self, emu_id):
        """Обрабатывает запрос на остановку эмулятора"""
        print(f"Остановка эмулятора {emu_id} (заглушка)")

    def on_emulator_restart_requested(self, emu_id):
        """Обрабатывает запрос на перезапуск эмулятора"""
        print(f"Перезапуск эмулятора {emu_id} (заглушка)")

    # ======== Методы для кнопок и действий пользователя ========
    def load_bots(self):
        """Загружает список ботов"""
        self.controller.load_all_bots()

    def edit_bot(self, bot_name):
        """Редактирует бота с указанным именем"""
        # Проверяем существование бота
        if not Resources.bot_exists(bot_name):
            QMessageBox.warning(self, "Внимание", f"Бот '{bot_name}' не найден.")
            return

        # Испускаем сигнал для перехода на страницу редактирования
        self.editBotRequested.emit(bot_name)

    def edit_selected_bot(self):
        """Редактирует выбранного бота из списка"""
        bot_name, _ = self.bot_list.get_selected_bot_data()
        if not bot_name:
            QMessageBox.warning(self, "Внимание", "Выберите бота для редактирования.")
            return

        self.edit_bot(bot_name)

    def add_bot_to_manager(self, bot_name, game_name):
        """Добавляет бота в очередь менеджера"""
        self.queue_tree.add_bot_to_queue(bot_name, game_name)

    def add_selected_bot_to_manager(self):
        """Добавляет выбранного бота в очередь менеджера"""
        bot_name, game_name = self.bot_list.get_selected_bot_data()
        if not bot_name:
            QMessageBox.warning(self, "Внимание", "Выберите бота для добавления в менеджер.")
            return

        self.add_bot_to_manager(bot_name, game_name)

    def delete_bot(self, bot_name):
        """Удаляет бота с указанным именем"""
        self.controller.delete_bot(bot_name)

    def delete_selected_bot(self):
        """Удаляет выбранного бота из списка"""
        bot_name, _ = self.bot_list.get_selected_bot_data()
        if not bot_name:
            QMessageBox.warning(self, "Внимание", "Выберите бота для удаления.")
            return

        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self, "Подтверждение", f"Удалить бота '{bot_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_bot(bot_name)

    def export_bot(self, bot_name):
        """Экспортирует бота с указанным именем"""
        # Открываем диалог выбора файла для сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт бота", f"{bot_name}.zip", "Zip Files (*.zip)"
        )

        if not file_path:
            return

        # Экспортируем бота
        if self.controller.export_bot(bot_name, file_path):
            QMessageBox.information(self, "Успех", f"Бот '{bot_name}' успешно экспортирован в '{file_path}'")
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать бота '{bot_name}'")

    def export_selected_bot(self):
        """Экспортирует выбранного бота из списка"""
        bot_name, _ = self.bot_list.get_selected_bot_data()
        if not bot_name:
            QMessageBox.warning(self, "Внимание", "Выберите бота для экспорта.")
            return

        self.export_bot(bot_name)

    def import_bot(self):
        """Импортирует бота из файла"""
        # Открываем диалог выбора файла для импорта
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт бота", "", "Zip Files (*.zip)"
        )

        if not file_path:
            return

        # Спрашиваем новое имя для бота
        # TODO: Реализовать диалог для ввода нового имени

        # Импортируем бота
        if self.controller.import_bot(file_path):
            # Успешный импорт обрабатывается через сигнал botImported
            pass
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось импортировать бота")

    def start_queue(self):
        """Запускает очередь ботов"""
        # Получаем всех ботов из очереди
        total_bots = self.queue_tree.topLevelItemCount()
        if total_bots == 0:
            QMessageBox.warning(self, "Внимание", "В очереди нет ботов для запуска.")
            return

        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self, "Запуск очереди",
            f"Запустить очередь из {total_bots} ботов?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Здесь должна быть реализация запуска очереди
            print(f"Запуск очереди из {total_bots} ботов (заглушка)")

    def clear_queue(self):
        """Очищает очередь ботов"""
        self.queue_tree.clear_queue()

    def show_settings_dialog(self):
        """
        Показывает диалог настроек параметров для выбранного бота.
        """
        try:
            # Получаем выбранный элемент напрямую из очереди
            item = self.queue_tree.currentItem()

            if not item or item.parent() is not None:
                QMessageBox.warning(self, "Внимание", "Выберите бота (top-level) в очереди для настройки параметров.")
                return

            # Создаем диалог настроек
            dialog = BotSettingsDialog(self)

            # Загружаем текущие параметры в диалог
            current_data = {
                "scheduled_time": item.text(4),
                "cycles": int(item.text(5)) if item.text(5).isdigit() else 0,
                "work_time": int(item.text(6)) if item.text(6).isdigit() else 0,
                "threads": int(item.text(3)) if item.text(3).isdigit() else 1,
                "emulators": self._get_emulators_string_from_item(item)
            }

            dialog.set_data(current_data)

            # Если пользователь подтвердил изменения
            if dialog.exec():
                new_data = dialog.get_data()

                # Обновляем основные параметры в дереве
                item.setText(3, str(new_data["threads"]))
                item.setText(4, new_data["scheduled_time"])
                item.setText(5, str(new_data["cycles"]))
                item.setText(6, str(new_data["work_time"]))

                # Обновляем список эмуляторов (сначала удаляем старые)
                while item.childCount() > 0:
                    item.removeChild(item.child(0))

                # Парсим новый список эмуляторов
                emu_list = self.controller.parse_emulators_string(new_data["emulators"])

                # Создаём child-элементы (эмуляторы)
                font = QFont("Segoe UI", 11)
                for emu_id in emu_list:
                    # [0="", 1="Эмулятор X", 2="off", 3="", 4="", 5="", 6=""]
                    child = QTreeWidgetItem(["", f"Эмулятор {emu_id}", "off", "", "", "", ""])
                    for col in range(self.queue_tree.columnCount()):
                        child.setFont(col, font)
                        child.setForeground(col, QBrush(QColor("white")))

                    # Добавляем иконку для эмулятора
                    child.setIcon(1, QIcon(Resources.get_icon_path("emulator")))

                    item.addChild(child)

                    # Добавляем данные для идентификации эмулятора при контекстном меню
                    child.setData(0, Qt.ItemDataRole.UserRole, emu_id)

                # Раскрываем узел для показа дочерних элементов
                item.setExpanded(True)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог настроек: {str(e)}")
            if self.logger:
                self.logger.error(f"Ошибка при открытии диалога настроек: {str(e)}")
            else:
                print(f"Ошибка при открытии диалога настроек: {str(e)}")

    def _get_emulators_string_from_item(self, item):
        """
        Получает строку с эмуляторами из дочерних элементов item.
        Преобразует список ID эмуляторов в компактную строку формата "0:5,7,9:10".
        """
        try:
            emu_ids = []
            for i in range(item.childCount()):
                child = item.child(i)
                if child.text(1).startswith("Эмулятор "):
                    try:
                        emu_id = int(child.text(1).replace("Эмулятор ", ""))
                        emu_ids.append(emu_id)
                    except ValueError:
                        pass

            # Если список пуст, возвращаем пустую строку
            if not emu_ids:
                return ""

            # Сортируем ID эмуляторов
            emu_ids.sort()

            # Группируем последовательные ID
            ranges = []
            start = emu_ids[0]
            end = emu_ids[0]

            for i in range(1, len(emu_ids)):
                if emu_ids[i] == end + 1:
                    end = emu_ids[i]
                else:
                    # Записываем предыдущий диапазон
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}:{end}")
                    # Начинаем новый диапазон
                    start = end = emu_ids[i]

            # Добавляем последний диапазон
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}:{end}")

            return ",".join(ranges)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при получении строки эмуляторов: {str(e)}")
            return ""