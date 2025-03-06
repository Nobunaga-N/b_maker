# src/gui/page_container.py
from PyQt6.QtWidgets import QStackedWidget

class PageContainer(QStackedWidget):
    """
    Контейнер для страниц с возможностью переключения между ними.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

    def change_page(self, index):
        """Переключает страницу на страницу с указанным индексом"""
        if index >= 0 and index < self.count():
            self.setCurrentIndex(index)
            return True
        return False