# -*- coding: utf-8 -*-
"""
Окно настройки связей между операторами и компьютерами
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QMessageBox, QWidget, QScrollArea)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
from typing import Dict, List, Optional, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import *


class ConnectionsCanvas(QWidget):
    """Канвас для отрисовки операторов, компьютеров и связей"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_operators = 3
        self.num_computers = 2
        self.connections: Dict[int, int] = {0: 0, 1: 0, 2: 1}  # {operator_id: computer_id}

        self.dragging = False
        self.drag_start_operator: Optional[int] = None
        self.drag_current_pos: Optional[QPoint] = None

        self.update_canvas_size()
        self.setStyleSheet(f"background-color: {COLOR_WIDGET_BG};")

    def update_canvas_size(self):
        """Обновить размер канваса в зависимости от количества элементов"""
        max_elements = max(self.num_operators, self.num_computers)
        required_height = MARGIN_TOP + max_elements * ROW_SPACING + ELEMENT_HEIGHT + 50
        canvas_width = CONNECTIONS_WINDOW_WIDTH - 100
        self.setMinimumSize(canvas_width, max(required_height, CONNECTIONS_WINDOW_HEIGHT - 150))
        self.resize(canvas_width, required_height)

    def get_operator_rect(self, operator_id: int) -> QRect:
        """Получить прямоугольник оператора"""
        y = MARGIN_TOP + operator_id * ROW_SPACING
        # Центрируем операторов в левой половине канваса
        canvas_width = CONNECTIONS_WINDOW_WIDTH - 100
        left_column_center = canvas_width / 4  # Центр левой половины
        x = int(left_column_center - ELEMENT_WIDTH / 2)
        return QRect(x, y, ELEMENT_WIDTH, ELEMENT_HEIGHT)

    def get_computer_rect(self, computer_id: int) -> QRect:
        """Получить прямоугольник компьютера"""
        y = MARGIN_TOP + computer_id * ROW_SPACING
        # Центрируем накопители в правой половине канваса
        canvas_width = CONNECTIONS_WINDOW_WIDTH - 100
        right_column_center = canvas_width * 3 / 4  # Центр правой половины
        x = int(right_column_center - ELEMENT_WIDTH / 2)
        return QRect(x, y, ELEMENT_WIDTH, ELEMENT_HEIGHT)

    def get_operator_connection_point(self, operator_id: int) -> QPoint:
        """Получить точку соединения оператора (справа)"""
        rect = self.get_operator_rect(operator_id)
        return QPoint(rect.right(), rect.center().y())

    def get_computer_connection_point(self, computer_id: int) -> QPoint:
        """Получить точку соединения компьютера (слева)"""
        rect = self.get_computer_rect(computer_id)
        return QPoint(rect.left(), rect.center().y())

    def paintEvent(self, event):
        """Отрисовка элементов"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Отрисовка связей
        self.draw_connections(painter)

        # Отрисовка линии при перетаскивании
        if self.dragging and self.drag_start_operator is not None and self.drag_current_pos:
            pen = QPen(QColor(COLOR_CONNECTION_LINE), 2, Qt.DashLine)
            painter.setPen(pen)
            start_point = self.get_operator_connection_point(self.drag_start_operator)
            painter.drawLine(start_point, self.drag_current_pos)

        # Отрисовка операторов
        for i in range(self.num_operators):
            self.draw_operator(painter, i)

        # Отрисовка компьютеров
        for i in range(self.num_computers):
            self.draw_computer(painter, i)

    def draw_connections(self, painter: QPainter):
        """Отрисовка линий связей"""
        pen = QPen(QColor(COLOR_CONNECTION_LINE), 3)
        painter.setPen(pen)

        for operator_id, computer_id in self.connections.items():
            if operator_id < self.num_operators and computer_id < self.num_computers:
                start = self.get_operator_connection_point(operator_id)
                end = self.get_computer_connection_point(computer_id)
                painter.drawLine(start, end)

    def draw_operator(self, painter: QPainter, operator_id: int):
        """Отрисовка оператора"""
        rect = self.get_operator_rect(operator_id)

        # Прямоугольник оператора
        painter.setBrush(QBrush(QColor(COLOR_OPERATOR)))
        painter.setPen(QPen(QColor("#2C3E50"), 2))
        painter.drawRoundedRect(rect, 5, 5)

        # Текст
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"Оператор {operator_id + 1}")

        # Точка соединения
        connection_point = self.get_operator_connection_point(operator_id)
        painter.setBrush(QBrush(QColor(COLOR_CONNECTION_POINT)))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(connection_point, CONNECTION_POINT_RADIUS, CONNECTION_POINT_RADIUS)

    def draw_computer(self, painter: QPainter, computer_id: int):
        """Отрисовка компьютера"""
        rect = self.get_computer_rect(computer_id)

        # Прямоугольник компьютера
        painter.setBrush(QBrush(QColor(COLOR_COMPUTER)))
        painter.setPen(QPen(QColor("#2C3E50"), 2))
        painter.drawRoundedRect(rect, 5, 5)

        # Текст
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"Накопитель {computer_id + 1}")

        # Точка соединения
        connection_point = self.get_computer_connection_point(computer_id)
        painter.setBrush(QBrush(QColor(COLOR_CONNECTION_POINT)))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(connection_point, CONNECTION_POINT_RADIUS, CONNECTION_POINT_RADIUS)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.LeftButton:
            # Проверяем, нажали ли на точку соединения оператора
            for i in range(self.num_operators):
                point = self.get_operator_connection_point(i)
                if (event.pos() - point).manhattanLength() <= CONNECTION_POINT_RADIUS + 5:
                    self.dragging = True
                    self.drag_start_operator = i
                    self.drag_current_pos = event.pos()
                    return

            # Проверяем, нажали ли на линию связи (для удаления)
            for operator_id, computer_id in list(self.connections.items()):
                if operator_id < self.num_operators and computer_id < self.num_computers:
                    start = self.get_operator_connection_point(operator_id)
                    end = self.get_computer_connection_point(computer_id)
                    if self.is_near_line(event.pos(), start, end, threshold=10):
                        del self.connections[operator_id]
                        self.update()
                        return

    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши"""
        if self.dragging:
            self.drag_current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if self.dragging and self.drag_start_operator is not None:
            # Проверяем, отпустили ли на точке соединения компьютера
            for i in range(self.num_computers):
                point = self.get_computer_connection_point(i)
                if (event.pos() - point).manhattanLength() <= CONNECTION_POINT_RADIUS + 10:
                    self.connections[self.drag_start_operator] = i
                    break

            self.dragging = False
            self.drag_start_operator = None
            self.drag_current_pos = None
            self.update()

    def is_near_line(self, point: QPoint, line_start: QPoint, line_end: QPoint, threshold: int) -> bool:
        """Проверка, находится ли точка рядом с линией"""
        # Расстояние от точки до отрезка
        x0, y0 = point.x(), point.y()
        x1, y1 = line_start.x(), line_start.y()
        x2, y2 = line_end.x(), line_end.y()

        # Параметрическое представление отрезка
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return False

        t = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        distance = ((x0 - nearest_x) ** 2 + (y0 - nearest_y) ** 2) ** 0.5
        return distance <= threshold

    def add_operator(self):
        """Добавить оператора"""
        self.num_operators += 1
        # Соединяем с ближайшим компьютером
        if self.num_computers > 0:
            nearest_computer = min(self.num_operators - 1, self.num_computers - 1)
            self.connections[self.num_operators - 1] = nearest_computer
        self.update_canvas_size()
        self.update()

    def remove_operator(self):
        """Удалить оператора"""
        if self.num_operators > 1:
            self.num_operators -= 1
            # Удаляем связь, если она была
            if self.num_operators in self.connections:
                del self.connections[self.num_operators]
            self.update_canvas_size()
            self.update()

    def add_computer(self):
        """Добавить компьютер"""
        self.num_computers += 1
        self.update_canvas_size()
        self.update()

    def remove_computer(self):
        """Удалить компьютер"""
        if self.num_computers > 1:
            self.num_computers -= 1
            # Удаляем связи с удалённым компьютером
            to_remove = [op_id for op_id, comp_id in self.connections.items()
                         if comp_id >= self.num_computers]
            for op_id in to_remove:
                del self.connections[op_id]
            self.update_canvas_size()
            self.update()

    def validate_connections(self) -> Tuple[bool, str]:
        """Проверка корректности связей"""
        for i in range(self.num_operators):
            if i not in self.connections:
                return False, f"Оператор {i + 1} не соединён ни с одним компьютером!"
        return True, ""


class ConnectionsWindow(QDialog):
    """Окно настройки связей"""

    def __init__(self, num_operators: int, num_computers: int,
                 connections: Dict[int, int], parent=None):
        super().__init__(parent)
        self.canvas = ConnectionsCanvas(self)
        self.canvas.num_operators = num_operators
        self.canvas.num_computers = num_computers
        self.canvas.connections = connections.copy()

        self.init_ui()
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Настройка связей")
        self.setFixedSize(CONNECTIONS_WINDOW_WIDTH, CONNECTIONS_WINDOW_HEIGHT)
        self.setModal(True)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Заголовок
        title = QLabel("Настройка связей: Операторы → Накопители")
        title_font = QFont()
        title_font.setPointSize(FONT_SIZE_TITLE)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Инструкция
        instruction = QLabel("Перетащите точки от операторов к компьютерам. Кликните по линии для удаления связи.")
        instruction.setFont(QFont("Arial", 10))
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setWordWrap(True)
        main_layout.addWidget(instruction)

        # Контрол-панель - центрированная над столбиками
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Вычисляем позиции для точного выравнивания
        canvas_width = CONNECTIONS_WINDOW_WIDTH - 100
        left_column_center = canvas_width / 4
        right_column_center = canvas_width * 3 / 4

        # Левый отступ до операторов
        control_layout.addSpacing(int(left_column_center - 80))

        # Операторы
        op_label = QLabel("Операторы:")
        op_label.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        control_layout.addWidget(op_label)

        add_op_btn = QPushButton("+")
        add_op_btn.setFixedSize(30, 30)
        add_op_btn.setStyleSheet(self._get_control_button_style())
        add_op_btn.clicked.connect(self.canvas.add_operator)
        control_layout.addWidget(add_op_btn)

        remove_op_btn = QPushButton("−")
        remove_op_btn.setFixedSize(30, 30)
        remove_op_btn.setStyleSheet(self._get_control_button_style())
        remove_op_btn.clicked.connect(self.canvas.remove_operator)
        control_layout.addWidget(remove_op_btn)

        # Отступ между колонками
        spacing_between = int(right_column_center - left_column_center - 160)
        control_layout.addSpacing(spacing_between)

        # Накопители
        comp_label = QLabel("Накопители:")
        comp_label.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        control_layout.addWidget(comp_label)

        add_comp_btn = QPushButton("+")
        add_comp_btn.setFixedSize(30, 30)
        add_comp_btn.setStyleSheet(self._get_control_button_style())
        add_comp_btn.clicked.connect(self.canvas.add_computer)
        control_layout.addWidget(add_comp_btn)

        remove_comp_btn = QPushButton("−")
        remove_comp_btn.setFixedSize(30, 30)
        remove_comp_btn.setStyleSheet(self._get_control_button_style())
        remove_comp_btn.clicked.connect(self.canvas.remove_computer)
        control_layout.addWidget(remove_comp_btn)

        # Правый отступ
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        # Канвас в скролл-области
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"background-color: {COLOR_WIDGET_BG};")
        main_layout.addWidget(scroll_area)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Сохранить")
        save_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #388E3C;
            }}
        """)
        save_button.clicked.connect(self.save_connections)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _get_control_button_style(self) -> str:
        """Стиль кнопок управления"""
        return """
            QPushButton {
                background-color: #ECF0F1;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D5DBDB;
            }
        """

    def save_connections(self):
        """Сохранить связи"""
        is_valid, error_msg = self.canvas.validate_connections()
        if not is_valid:
            QMessageBox.warning(self, "Ошибка", error_msg)
            return

        self.accept()

    def get_configuration(self) -> Tuple[int, int, Dict[int, int]]:
        """Получить конфигурацию"""
        return (self.canvas.num_operators,
                self.canvas.num_computers,
                self.canvas.connections.copy())
