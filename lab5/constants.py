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

# Цвета
COLOR_BACKGROUND = "#F5F5F5"
COLOR_WIDGET_BG = "#FFFFFF"
COLOR_BUTTON = "#4A90E2"
COLOR_BUTTON_HOVER = "#357ABD"
COLOR_ERROR = "#E74C3C"
COLOR_SUCCESS = "#27AE60"

# Цвета для окна связей
COLOR_OPERATOR = "#3498DB"
COLOR_COMPUTER = "#E67E22"
COLOR_CONNECTION_LINE = "#2C3E50"
COLOR_CONNECTION_POINT = "#34495E"

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
