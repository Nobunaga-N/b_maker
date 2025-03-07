# src/gui/page_container.py
"""
Модуль содержит класс контейнера страниц с возможностью переключения.
"""

from PyQt6.QtWidgets import QStackedWidget, QWidget


class PageContainer(QStackedWidget):
    """
    Контейнер для страниц с возможностью переключения между ними.
    Простая реализация без анимации для обеспечения стабильности.
    """

    def __init__(self, parent=None):
        """
        Инициализирует контейнер страниц.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

    def change_page(self, index: int) -> bool:
        """
        Переключает страницу на страницу с указанным индексом.

        Args:
            index: Индекс страницы для отображения.

        Returns:
            True, если переключение выполнено успешно, иначе False.
        """
        if index >= 0 and index < self.count():
            self.setCurrentIndex(index)
            return True
        return False