# -*- coding: utf-8 -*-
"""
Константы для приложения моделирования СМО
"""

# Размеры шрифтов
FONT_SIZE_TITLE = 18          # Заголовки ("Распределение:", "Параметры:")
FONT_SIZE_COMBO = 13          # Выпадающий список распределений
FONT_SIZE_PARAM_LABEL = 13    # Метки параметров (k =, λ =)
FONT_SIZE_PARAM_FIELD = 13    # Поля ввода параметров
FONT_SIZE_ERROR = 13          # Панель ошибок
FONT_SIZE_BUTTON = 14         # Размер шрифта кнопки
FONT_SIZE_RESULT = 13         # Результаты моделирования

# Внутренние отступы виджетов
WIDGET_PADDING = 12

# Цвета
COLOR_BACKGROUND = "#F8F8F8"
COLOR_WIDGET_BG = "white"
COLOR_ERROR_BG = "#FFF5F5"
COLOR_ERROR_BORDER = "#FFC9C9"
COLOR_ERROR_TEXT = "#D32F2F"
COLOR_BUTTON_BG = "#4CAF50"
COLOR_BUTTON_HOVER = "#45a049"
COLOR_BUTTON_PRESSED = "#3d8b40"

# Размеры окна
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 700

# Параметры по умолчанию
DEFAULT_VALUES = {
    'generator_dist': 'Равномерное',
    'generator_params': {'a': 0.0, 'b': 10.0},
    'processor_dist': 'Нормальное',
    'processor_params': {'μ': 5.0, 'σ': 2.0},
    'num_tasks': 1000,
    'return_probability': 10,
    'time_step': 0.01
}