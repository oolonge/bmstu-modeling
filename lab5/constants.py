# -*- coding: utf-8 -*-
"""
Константы для приложения моделирования информационного центра
"""

# Размеры окна
MAIN_WINDOW_WIDTH = 800
MAIN_WINDOW_HEIGHT = 600
CONNECTIONS_WINDOW_WIDTH = 900
CONNECTIONS_WINDOW_HEIGHT = 700
RESULTS_WINDOW_WIDTH = 700
RESULTS_WINDOW_HEIGHT = 500

# Размеры шрифтов
FONT_SIZE_TITLE = 14
FONT_SIZE_LABEL = 11
FONT_SIZE_INPUT = 11
FONT_SIZE_BUTTON = 12
FONT_SIZE_RESULT = 12

# Цвета (только белый, черный, зеленый, синий, красный)
COLOR_BACKGROUND = "#F5F5F5"
COLOR_WIDGET_BG = "#FFFFFF"
COLOR_BUTTON = "#2196F3"
COLOR_BUTTON_HOVER = "#1976D2"
COLOR_ERROR = "#F44336"
COLOR_SUCCESS = "#4CAF50"

# Цвета для окна связей
COLOR_OPERATOR = "#2196F3"      # Синий
COLOR_COMPUTER = "#4CAF50"      # Зеленый
COLOR_CONNECTION_LINE = "#000000"  # Черный
COLOR_CONNECTION_POINT = "#000000"  # Черный

# Размеры элементов в окне связей
ELEMENT_WIDTH = 120
ELEMENT_HEIGHT = 50
CONNECTION_POINT_RADIUS = 6
COLUMN_SPACING = 300
ROW_SPACING = 80
MARGIN_TOP = 100
MARGIN_LEFT = 150

# Параметры по умолчанию
DEFAULT_NUM_CLIENTS = 300
DEFAULT_GENERATOR_MEAN = 10.0
DEFAULT_GENERATOR_DEVIATION = 2.0

# Параметры операторов по умолчанию
DEFAULT_OPERATORS = [
    {'mean': 20.0, 'deviation': 5.0, 'computer_id': 0},   # Оператор 1 -> Компьютер 1
    {'mean': 40.0, 'deviation': 10.0, 'computer_id': 0},  # Оператор 2 -> Компьютер 1
    {'mean': 40.0, 'deviation': 20.0, 'computer_id': 1},  # Оператор 3 -> Компьютер 2
]

# Параметры компьютеров по умолчанию
DEFAULT_COMPUTERS = [
    {'processing_time': 15.0},  # Компьютер 1
    {'processing_time': 30.0},  # Компьютер 2
]
