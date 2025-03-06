# src/gui/page_container.py
from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QPoint


class PageContainer(QStackedWidget):
    """
    Контейнер для страниц с анимированным переходом между ними.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        self._current_index = 0
        self._next_index = 0
        self._animation_in_progress = False

    def slide_to_index(self, index):
        """Анимированный переход к странице по индексу"""
        if self._animation_in_progress or index == self.currentIndex():
            return

        self._animation_in_progress = True
        self._next_index = index

        # Получаем текущий и следующий виджеты
        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        # Определяем направление анимации
        direction = 1 if index > self.currentIndex() else -1

        # Настраиваем начальное положение виджетов
        offset = self.width()
        next_widget_pos = QPoint(offset * direction, 0)
        current_widget_pos = QPoint(0, 0)

        # Устанавливаем положение следующего виджета
        next_widget.move(next_widget_pos)
        next_widget.show()
        next_widget.raise_()

        # Создаем анимацию для текущего виджета
        current_anim = QPropertyAnimation(current_widget, b"pos")
        current_anim.setDuration(300)
        current_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        current_anim.setStartValue(current_widget_pos)
        current_anim.setEndValue(QPoint(-offset * direction, 0))

        # Создаем анимацию для следующего виджета
        next_anim = QPropertyAnimation(next_widget, b"pos")
        next_anim.setDuration(300)
        next_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        next_anim.setStartValue(next_widget_pos)
        next_anim.setEndValue(QPoint(0, 0))

        # Запускаем анимации
        current_anim.start()
        next_anim.start()

        # Обновляем индекс и статус по завершении анимации
        current_anim.finished.connect(self._animation_finished)

    def _animation_finished(self):
        """Обработчик завершения анимации"""
        self.setCurrentIndex(self._next_index)
        self._animation_in_progress = False
        self._current_index = self._next_index