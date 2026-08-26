# -*- coding: utf-8 -*-
"""
Окно отображения результатов моделирования
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QComboBox, QGroupBox, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Dict, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import *


class ResultsWindow(QDialog):
    """Окно результатов моделирования"""

    repeat_simulation = pyqtSignal()  # Сигнал для повтора эксперимента

    def __init__(self, rejection_prob: float, queue_stats: Dict[int, Tuple[int, float]],
                 total_clients: int, rejected_clients: int, parent=None):
        """
        Args:
            rejection_prob: Вероятность отказа
            queue_stats: Статистика по очередям {queue_id: (max_size, avg_size)}
            total_clients: Общее количество клиентов
            rejected_clients: Количество отклонённых клиентов
            parent: Родительское окно
        """
        super().__init__(parent)
        self.rejection_prob = rejection_prob
        self.queue_stats = queue_stats
        self.total_clients = total_clients
        self.rejected_clients = rejected_clients
        self.current_queue_id = 0

        self.init_ui()
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Результаты моделирования")
        self.setFixedSize(RESULTS_WINDOW_WIDTH, RESULTS_WINDOW_HEIGHT)
        self.setModal(True)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("Результаты моделирования")
        title_font = QFont()
        title_font.setPointSize(FONT_SIZE_TITLE + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Общая статистика
        general_stats_group = self._create_general_stats_group()
        main_layout.addWidget(general_stats_group)

        # Статистика по накопителям
        queue_stats_group = self._create_queue_stats_group()
        main_layout.addWidget(queue_stats_group)

        main_layout.addStretch()

        # Кнопка повтора эксперимента
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        repeat_button = QPushButton("Повторить эксперимент")
        repeat_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        repeat_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BUTTON};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
        """)
        repeat_button.clicked.connect(self.on_repeat)
        button_layout.addWidget(repeat_button)

        close_button = QPushButton("Закрыть")
        close_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        close_button.setStyleSheet("""
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
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_general_stats_group(self) -> QGroupBox:
        """Создание группы с общей статистикой"""
        group = QGroupBox("Общая статистика")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLOR_WIDGET_BG};
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        layout = QVBoxLayout()

        # Таблица с результатами
        table = QTableWidget(3, 2)
        table.setFont(QFont("Arial", FONT_SIZE_RESULT))
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setMaximumHeight(120)

        # Вероятность отказа
        table.setItem(0, 0, QTableWidgetItem("Вероятность отказа:"))
        prob_text = f"{self.rejection_prob * 100:.2f}%"
        prob_item = QTableWidgetItem(prob_text)
        prob_item.setForeground(Qt.red if self.rejection_prob > 0.1 else Qt.darkGreen)
        prob_item.setFont(QFont("Arial", FONT_SIZE_RESULT, QFont.Bold))
        table.setItem(0, 1, prob_item)

        # Всего клиентов
        table.setItem(1, 0, QTableWidgetItem("Всего клиентов:"))
        table.setItem(1, 1, QTableWidgetItem(str(self.total_clients)))

        # Отклонено
        table.setItem(2, 0, QTableWidgetItem("Отклонено:"))
        rejected_item = QTableWidgetItem(str(self.rejected_clients))
        rejected_item.setForeground(Qt.red)
        table.setItem(2, 1, rejected_item)

        layout.addWidget(table)
        group.setLayout(layout)
        return group

    def _create_queue_stats_group(self) -> QGroupBox:
        """Создание группы со статистикой по накопителям"""
        group = QGroupBox("Статистика по накопителям")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLOR_WIDGET_BG};
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        layout = QVBoxLayout()

        # Выбор накопителя
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Накопитель:")
        selector_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        selector_layout.addWidget(selector_label)

        self.queue_selector = QComboBox()
        self.queue_selector.setFont(QFont("Arial", FONT_SIZE_LABEL))
        for queue_id in sorted(self.queue_stats.keys()):
            self.queue_selector.addItem(f"Накопитель {queue_id + 1}", queue_id)
        self.queue_selector.currentIndexChanged.connect(self.on_queue_changed)
        selector_layout.addWidget(self.queue_selector)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Таблица статистики очереди
        self.queue_table = QTableWidget(2, 2)
        self.queue_table.setFont(QFont("Arial", FONT_SIZE_RESULT))
        self.queue_table.horizontalHeader().setVisible(False)
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.queue_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.queue_table.setSelectionMode(QTableWidget.NoSelection)
        self.queue_table.setMaximumHeight(80)

        self.update_queue_table()

        layout.addWidget(self.queue_table)
        group.setLayout(layout)
        return group

    def update_queue_table(self):
        """Обновление таблицы статистики очереди"""
        queue_id = self.queue_selector.currentData()
        if queue_id is None:
            return

        max_size, avg_size = self.queue_stats[queue_id]

        self.queue_table.setItem(0, 0, QTableWidgetItem("Максимальная длина:"))
        self.queue_table.setItem(0, 1, QTableWidgetItem(str(max_size)))

        self.queue_table.setItem(1, 0, QTableWidgetItem("Средняя длина:"))
        self.queue_table.setItem(1, 1, QTableWidgetItem(f"{avg_size:.2f}"))

    def on_queue_changed(self, index):
        """Обработка изменения выбранной очереди"""
        self.update_queue_table()

    def on_repeat(self):
        """Обработка нажатия кнопки повтора эксперимента"""
        self.repeat_simulation.emit()
        self.accept()
