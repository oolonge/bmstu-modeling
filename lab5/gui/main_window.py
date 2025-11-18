# -*- coding: utf-8 -*-
"""
Главное окно приложения
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
                              QComboBox, QGroupBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict, List
import sys
import os

# Добавляем путь к родительской директории для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import *
from models.distributions import UniformDistribution
from models.elements import ClientGenerator, Operator, Computer
from models.event_model import simulate_info_center
from gui.connections_window import ConnectionsWindow
from gui.results_window import ResultsWindow


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        # Конфигурация системы
        self.num_operators = len(DEFAULT_OPERATORS)
        self.num_computers = len(DEFAULT_COMPUTERS)
        self.connections: Dict[int, int] = {i: op['computer_id']
                                             for i, op in enumerate(DEFAULT_OPERATORS)}

        # Параметры по умолчанию
        self.operator_params = [
            {'mean': op['mean'], 'deviation': op['deviation']}
            for op in DEFAULT_OPERATORS
        ]
        self.computer_params = [
            {'processing_time': comp['processing_time']}
            for comp in DEFAULT_COMPUTERS
        ]

        self.init_ui()
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Моделирование информационного центра")
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("Моделирование информационного центра")
        title_font = QFont()
        title_font.setPointSize(FONT_SIZE_TITLE + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Параметры моделирования
        sim_params_group = self._create_simulation_params_group()
        main_layout.addWidget(sim_params_group)

        # Параметры генератора
        generator_group = self._create_generator_params_group()
        main_layout.addWidget(generator_group)

        # Параметры операторов
        operators_group = self._create_operators_params_group()
        main_layout.addWidget(operators_group)

        # Параметры компьютеров
        computers_group = self._create_computers_params_group()
        main_layout.addWidget(computers_group)

        main_layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        connections_button = QPushButton("Настроить связи")
        connections_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        connections_button.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
        """)
        connections_button.clicked.connect(self.open_connections_window)
        buttons_layout.addWidget(connections_button)

        run_button = QPushButton("Запустить моделирование")
        run_button.setFont(QFont("Arial", FONT_SIZE_BUTTON))
        run_button.setStyleSheet(f"""
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
        run_button.clicked.connect(self.run_simulation)
        buttons_layout.addWidget(run_button)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        central_widget.setLayout(main_layout)

    def _create_simulation_params_group(self) -> QGroupBox:
        """Создание группы параметров моделирования"""
        group = QGroupBox("Параметры моделирования")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(self._get_group_style())

        layout = QHBoxLayout()

        label = QLabel("Количество клиентов:")
        label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        layout.addWidget(label)

        self.num_clients_spinbox = QSpinBox()
        self.num_clients_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.num_clients_spinbox.setRange(10, 10000)
        self.num_clients_spinbox.setValue(DEFAULT_NUM_CLIENTS)
        self.num_clients_spinbox.setSingleStep(10)
        layout.addWidget(self.num_clients_spinbox)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_generator_params_group(self) -> QGroupBox:
        """Создание группы параметров генератора"""
        group = QGroupBox("Генератор клиентов (равномерное распределение)")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(self._get_group_style())

        layout = QHBoxLayout()

        # Среднее
        mean_label = QLabel("Среднее (мин):")
        mean_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        layout.addWidget(mean_label)

        self.generator_mean_spinbox = QDoubleSpinBox()
        self.generator_mean_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.generator_mean_spinbox.setRange(0.1, 1000.0)
        self.generator_mean_spinbox.setValue(DEFAULT_GENERATOR_MEAN)
        self.generator_mean_spinbox.setSingleStep(0.5)
        self.generator_mean_spinbox.setDecimals(1)
        layout.addWidget(self.generator_mean_spinbox)

        layout.addSpacing(20)

        # Погрешность
        deviation_label = QLabel("± (мин):")
        deviation_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        layout.addWidget(deviation_label)

        self.generator_deviation_spinbox = QDoubleSpinBox()
        self.generator_deviation_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.generator_deviation_spinbox.setRange(0.1, 100.0)
        self.generator_deviation_spinbox.setValue(DEFAULT_GENERATOR_DEVIATION)
        self.generator_deviation_spinbox.setSingleStep(0.5)
        self.generator_deviation_spinbox.setDecimals(1)
        layout.addWidget(self.generator_deviation_spinbox)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_operators_params_group(self) -> QGroupBox:
        """Создание группы параметров операторов"""
        group = QGroupBox("Параметры операторов")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(self._get_group_style())

        layout = QVBoxLayout()

        # Выбор оператора
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Оператор:")
        selector_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        selector_layout.addWidget(selector_label)

        self.operator_selector = QComboBox()
        self.operator_selector.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self._update_operator_selector()
        self.operator_selector.currentIndexChanged.connect(self._on_operator_changed)
        selector_layout.addWidget(self.operator_selector)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Параметры (среднее ± погрешность)
        params_layout = QHBoxLayout()

        mean_label = QLabel("Среднее (мин):")
        mean_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        params_layout.addWidget(mean_label)

        self.operator_mean_spinbox = QDoubleSpinBox()
        self.operator_mean_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.operator_mean_spinbox.setRange(0.1, 1000.0)
        self.operator_mean_spinbox.setSingleStep(0.5)
        self.operator_mean_spinbox.setDecimals(1)
        self.operator_mean_spinbox.valueChanged.connect(self._on_operator_param_changed)
        params_layout.addWidget(self.operator_mean_spinbox)

        params_layout.addSpacing(20)

        deviation_label = QLabel("± (мин):")
        deviation_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        params_layout.addWidget(deviation_label)

        self.operator_deviation_spinbox = QDoubleSpinBox()
        self.operator_deviation_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.operator_deviation_spinbox.setRange(0.1, 100.0)
        self.operator_deviation_spinbox.setSingleStep(0.5)
        self.operator_deviation_spinbox.setDecimals(1)
        self.operator_deviation_spinbox.valueChanged.connect(self._on_operator_param_changed)
        params_layout.addWidget(self.operator_deviation_spinbox)

        params_layout.addStretch()
        layout.addLayout(params_layout)

        self._load_operator_params(0)

        group.setLayout(layout)
        return group

    def _create_computers_params_group(self) -> QGroupBox:
        """Создание группы параметров компьютеров"""
        group = QGroupBox("Параметры компьютеров")
        group.setFont(QFont("Arial", FONT_SIZE_LABEL, QFont.Bold))
        group.setStyleSheet(self._get_group_style())

        layout = QVBoxLayout()

        # Выбор компьютера
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Компьютер:")
        selector_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        selector_layout.addWidget(selector_label)

        self.computer_selector = QComboBox()
        self.computer_selector.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self._update_computer_selector()
        self.computer_selector.currentIndexChanged.connect(self._on_computer_changed)
        selector_layout.addWidget(self.computer_selector)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Параметры
        params_layout = QHBoxLayout()

        time_label = QLabel("Время обработки (мин):")
        time_label.setFont(QFont("Arial", FONT_SIZE_LABEL))
        params_layout.addWidget(time_label)

        self.computer_time_spinbox = QDoubleSpinBox()
        self.computer_time_spinbox.setFont(QFont("Arial", FONT_SIZE_INPUT))
        self.computer_time_spinbox.setRange(0.1, 1000.0)
        self.computer_time_spinbox.setSingleStep(0.5)
        self.computer_time_spinbox.setDecimals(1)
        self.computer_time_spinbox.valueChanged.connect(self._on_computer_param_changed)
        params_layout.addWidget(self.computer_time_spinbox)

        params_layout.addStretch()
        layout.addLayout(params_layout)

        self._load_computer_params(0)

        group.setLayout(layout)
        return group

    def _get_group_style(self) -> str:
        """Получить стиль группы"""
        return f"""
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
        """

    def _update_operator_selector(self):
        """Обновить список операторов"""
        current_index = self.operator_selector.currentIndex()
        self.operator_selector.clear()
        for i in range(self.num_operators):
            self.operator_selector.addItem(f"Оператор {i + 1}", i)
        if current_index >= 0 and current_index < self.num_operators:
            self.operator_selector.setCurrentIndex(current_index)

    def _update_computer_selector(self):
        """Обновить список компьютеров"""
        current_index = self.computer_selector.currentIndex()
        self.computer_selector.clear()
        for i in range(self.num_computers):
            self.computer_selector.addItem(f"Компьютер {i + 1}", i)
        if current_index >= 0 and current_index < self.num_computers:
            self.computer_selector.setCurrentIndex(current_index)

    def _on_operator_changed(self, index):
        """Обработка изменения выбранного оператора"""
        operator_id = self.operator_selector.currentData()
        if operator_id is not None:
            self._load_operator_params(operator_id)

    def _on_computer_changed(self, index):
        """Обработка изменения выбранного компьютера"""
        computer_id = self.computer_selector.currentData()
        if computer_id is not None:
            self._load_computer_params(computer_id)

    def _load_operator_params(self, operator_id: int):
        """Загрузить параметры оператора"""
        if operator_id < len(self.operator_params):
            params = self.operator_params[operator_id]
            self.operator_mean_spinbox.setValue(params['mean'])
            self.operator_deviation_spinbox.setValue(params['deviation'])

    def _load_computer_params(self, computer_id: int):
        """Загрузить параметры компьютера"""
        if computer_id < len(self.computer_params):
            params = self.computer_params[computer_id]
            self.computer_time_spinbox.setValue(params['processing_time'])

    def _on_operator_param_changed(self):
        """Обработка изменения параметров оператора"""
        operator_id = self.operator_selector.currentData()
        if operator_id is not None and operator_id < len(self.operator_params):
            self.operator_params[operator_id]['mean'] = self.operator_mean_spinbox.value()
            self.operator_params[operator_id]['deviation'] = self.operator_deviation_spinbox.value()

    def _on_computer_param_changed(self):
        """Обработка изменения параметров компьютера"""
        computer_id = self.computer_selector.currentData()
        if computer_id is not None and computer_id < len(self.computer_params):
            self.computer_params[computer_id]['processing_time'] = self.computer_time_spinbox.value()

    def open_connections_window(self):
        """Открыть окно настройки связей"""
        dialog = ConnectionsWindow(self.num_operators, self.num_computers,
                                    self.connections, self)
        if dialog.exec_():
            new_num_operators, new_num_computers, new_connections = dialog.get_configuration()

            # Обновляем количество элементов
            old_num_operators = self.num_operators
            old_num_computers = self.num_computers
            self.num_operators = new_num_operators
            self.num_computers = new_num_computers
            self.connections = new_connections

            # Обновляем параметры операторов
            if new_num_operators > old_num_operators:
                for i in range(old_num_operators, new_num_operators):
                    self.operator_params.append({'mean': 30.0, 'deviation': 5.0})
            elif new_num_operators < old_num_operators:
                self.operator_params = self.operator_params[:new_num_operators]

            # Обновляем параметры компьютеров
            if new_num_computers > old_num_computers:
                for i in range(old_num_computers, new_num_computers):
                    self.computer_params.append({'processing_time': 20.0})
            elif new_num_computers < old_num_computers:
                self.computer_params = self.computer_params[:new_num_computers]

            # Обновляем селекторы
            self._update_operator_selector()
            self._update_computer_selector()

    def run_simulation(self):
        """Запустить моделирование"""
        try:
            # Создаём генератор
            generator_mean = self.generator_mean_spinbox.value()
            generator_deviation = self.generator_deviation_spinbox.value()
            generator_dist = UniformDistribution.from_mean_and_deviation(
                generator_mean, generator_deviation
            )
            generator = ClientGenerator(generator_dist)

            # Создаём операторов
            operators = []
            for i in range(self.num_operators):
                params = self.operator_params[i]
                operator_dist = UniformDistribution.from_mean_and_deviation(
                    params['mean'], params['deviation']
                )
                target_computer = self.connections[i]
                operator = Operator(i, operator_dist, target_computer)
                operators.append(operator)

            # Создаём компьютеры
            computers = []
            for i in range(self.num_computers):
                params = self.computer_params[i]
                computer = Computer(i, params['processing_time'])
                computers.append(computer)

            # Запускаем моделирование
            num_clients = self.num_clients_spinbox.value()
            results = simulate_info_center(generator, operators, computers, num_clients)

            # Показываем результаты
            results_window = ResultsWindow(
                results.rejection_probability,
                results.queue_stats,
                results.total_clients,
                results.rejected_clients,
                self
            )
            results_window.repeat_simulation.connect(self.run_simulation)
            results_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при моделировании:\n{str(e)}")
