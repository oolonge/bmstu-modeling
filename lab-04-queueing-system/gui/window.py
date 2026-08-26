# -*- coding: utf-8 -*-
"""
Главное окно приложения для моделирования СМО
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QComboBox, QLabel, QLineEdit, 
                              QFrame, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Импорты из наших модулей
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import *
from models.distributions import create_distribution
from models.step_model import step_model
from models.event_model import event_model


class SMOWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моделирование СМО")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Левая панель
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Правая панель
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        # Словари для хранения полей ввода
        self.generator_param_fields = {}
        self.processor_param_fields = {}
        
        # Определение параметров распределений
        self.distributions_info = {
            "Равномерное": {
                "params": [("a", 0.0, "Нижняя граница интервала"),
                          ("b", 1.0, "Верхняя граница интервала")]
            },
            "Экспоненциальное": {
                "params": [("λ", 1.0, "Интенсивность (скорость)")]
            },
            "Нормальное": {
                "params": [("μ", 0.0, "Математическое ожидание (среднее)"),
                          ("σ", 1.0, "Стандартное отклонение")]
            },
            "Эрланга": {
                "params": [("k", 2.0, "Параметр формы (целое число фаз)"),
                          ("λ", 1.0, "Интенсивность (скорость)")]
            }
        }
        
        # Инициализация интерфейса со значениями по умолчанию
        self.on_generator_distribution_changed()
        self.on_processor_distribution_changed()
        
        # Установка значений по умолчанию
        self.set_default_values()
    
    def create_left_panel(self):
        """Создание левой панели с выбором распределений"""
        left_panel = QWidget()
        left_panel.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
        left_panel.setFixedWidth(420)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # === ГЕНЕРАТОР ===
        generator_segment = self.create_distribution_segment(
            "ГЕНЕРАТОР", 
            is_generator=True
        )
        left_layout.addWidget(generator_segment)
        
        # === ОБСЛУЖИВАЮЩИЙ АППАРАТ ===
        processor_segment = self.create_distribution_segment(
            "ОБСЛУЖИВАЮЩИЙ АППАРАТ", 
            is_generator=False
        )
        left_layout.addWidget(processor_segment)
        
        # === ПАНЕЛЬ ОШИБОК ===
        self.error_panel = self.create_error_panel()
        left_layout.addWidget(self.error_panel)
        
        left_layout.addStretch()
        
        return left_panel
    
    def create_distribution_segment(self, title: str, is_generator: bool):
        """Создание сегмента для выбора распределения"""
        segment = QFrame()
        segment.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WIDGET_BG};
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        
        layout = QVBoxLayout(segment)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", FONT_SIZE_TITLE, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # ComboBox для выбора распределения
        combo = QComboBox()
        combo.addItems(["Равномерное", "Экспоненциальное", "Нормальное", "Эрланга"])
        combo.setFont(QFont("Arial", FONT_SIZE_COMBO))
        combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
            }
        """)
        
        if is_generator:
            self.generator_combo = combo
            combo.currentIndexChanged.connect(self.on_generator_distribution_changed)
        else:
            self.processor_combo = combo
            combo.currentIndexChanged.connect(self.on_processor_distribution_changed)
        
        layout.addWidget(combo)
        
        # Контейнер для параметров
        params_container = QWidget()
        params_layout = QVBoxLayout(params_container)
        params_layout.setSpacing(12)
        params_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_generator:
            self.generator_params_container = params_container
            self.generator_params_layout = params_layout
        else:
            self.processor_params_container = params_container
            self.processor_params_layout = params_layout
        
        layout.addWidget(params_container)
        
        return segment
    
    def create_error_panel(self):
        """Создание панели для отображения ошибок"""
        error_panel = QFrame()
        error_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_ERROR_BG};
                border: 2px solid {COLOR_ERROR_BORDER};
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        error_panel.setVisible(False)
        
        error_layout = QVBoxLayout(error_panel)
        error_layout.setSpacing(5)
        error_layout.setContentsMargins(0, 0, 0, 0)
        
        error_title = QLabel("⚠ Ошибка ввода:")
        error_title.setFont(QFont("Arial", FONT_SIZE_ERROR, QFont.Weight.Bold))
        error_title.setStyleSheet(f"color: {COLOR_ERROR_TEXT};")
        
        self.error_text = QLabel()
        self.error_text.setFont(QFont("Arial", FONT_SIZE_ERROR))
        self.error_text.setWordWrap(True)
        self.error_text.setStyleSheet("color: #666666;")
        
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_text)
        
        return error_panel
    
    def create_right_panel(self):
        """Создание правой панели с параметрами моделирования"""
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)
        
        # === ПАРАМЕТРЫ МОДЕЛИРОВАНИЯ ===
        params_segment = QFrame()
        params_segment.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WIDGET_BG};
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        
        params_layout = QVBoxLayout(params_segment)
        params_layout.setSpacing(15)
        
        title = QLabel("ПАРАМЕТРЫ МОДЕЛИРОВАНИЯ")
        title.setFont(QFont("Arial", FONT_SIZE_TITLE, QFont.Weight.Bold))
        params_layout.addWidget(title)
        
        # Поля ввода параметров
        self.num_tasks_field = self.create_param_field("Количество заявок:", params_layout)
        self.return_prob_field = self.create_param_field("Вероятность возврата (%):", params_layout)
        self.time_step_field = self.create_param_field("Временной шаг:", params_layout)
        
        right_layout.addWidget(params_segment)
        
        # === КНОПКА "РЕШИТЬ" ===
        solve_button = QPushButton("Решить")
        solve_button.setFont(QFont("Arial", FONT_SIZE_BUTTON, QFont.Weight.Bold))
        solve_button.setCursor(Qt.CursorShape.PointingHandCursor)
        solve_button.setFixedHeight(50)
        solve_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BUTTON_PRESSED};
            }}
        """)
        solve_button.clicked.connect(self.solve)
        right_layout.addWidget(solve_button)
        
        # === РЕЗУЛЬТАТЫ ===
        results_segment = QFrame()
        results_segment.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WIDGET_BG};
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        
        results_layout = QVBoxLayout(results_segment)
        results_layout.setSpacing(15)
        
        result_title = QLabel("РЕЗУЛЬТАТ")
        result_title.setFont(QFont("Arial", FONT_SIZE_TITLE, QFont.Weight.Bold))
        results_layout.addWidget(result_title)
        
        subtitle = QLabel("Максимальная длина очереди:")
        subtitle.setFont(QFont("Arial", FONT_SIZE_RESULT + 1))
        results_layout.addWidget(subtitle)
        
        # Поля для результатов
        self.step_result_field = self.create_result_field("Пошаговый подход:", results_layout)
        self.event_result_field = self.create_result_field("Событийный подход:", results_layout)
        
        right_layout.addWidget(results_segment)
        right_layout.addStretch()
        
        return right_panel
    
    def create_param_field(self, label_text: str, layout):
        """Создание поля для ввода параметра"""
        param_widget = QWidget()
        param_layout = QHBoxLayout(param_widget)
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.setSpacing(10)
        
        label = QLabel(label_text)
        label.setFont(QFont("Arial", FONT_SIZE_PARAM_LABEL))
        label.setFixedWidth(200)
        
        field = QLineEdit()
        field.setFont(QFont("Arial", FONT_SIZE_PARAM_FIELD))
        field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #CCCCCC;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        param_layout.addWidget(label)
        param_layout.addWidget(field, 1)
        
        layout.addWidget(param_widget)
        
        return field
    
    def create_result_field(self, label_text: str, layout):
        """Создание поля для отображения результата"""
        result_widget = QWidget()
        result_layout = QHBoxLayout(result_widget)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(10)
        
        label = QLabel(label_text)
        label.setFont(QFont("Arial", FONT_SIZE_RESULT))
        label.setFixedWidth(200)
        
        field = QLineEdit()
        field.setFont(QFont("Arial", FONT_SIZE_RESULT, QFont.Weight.Bold))
        field.setReadOnly(True)
        field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                background-color: #F0F8F0;
                color: #2E7D32;
            }
        """)
        
        result_layout.addWidget(label)
        result_layout.addWidget(field, 1)
        
        layout.addWidget(result_widget)
        
        return field
    
    def update_params_layout(self, params_layout, param_fields, dist_name):
        """Обновление полей параметров для выбранного распределения"""
        # Очистка старых полей
        while params_layout.count():
            child = params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        param_fields.clear()
        
        # Получение параметров текущего распределения
        dist_info = self.distributions_info[dist_name]
        
        # Создание полей для параметров
        for param_name, default_value, tooltip in dist_info["params"]:
            param_widget = QWidget()
            param_layout = QHBoxLayout(param_widget)
            param_layout.setContentsMargins(0, 0, 0, 0)
            param_layout.setSpacing(10)
            
            label = QLabel(f"{param_name} =")
            label.setFont(QFont("Arial", FONT_SIZE_PARAM_LABEL))
            label.setToolTip(tooltip)
            label.setFixedWidth(50)
            label.setStyleSheet("background-color: transparent;")
            
            field = QLineEdit()
            field.setText(str(default_value))
            field.setFont(QFont("Arial", FONT_SIZE_PARAM_FIELD))
            field.setToolTip(tooltip)
            field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
            
            param_fields[param_name] = field
            param_layout.addWidget(label)
            param_layout.addWidget(field, 1)
            
            params_layout.addWidget(param_widget)
    
    def on_generator_distribution_changed(self):
        """Обработчик смены распределения генератора"""
        dist_name = self.generator_combo.currentText()
        self.update_params_layout(
            self.generator_params_layout,
            self.generator_param_fields,
            dist_name
        )
    
    def on_processor_distribution_changed(self):
        """Обработчик смены распределения обслуживающего аппарата"""
        dist_name = self.processor_combo.currentText()
        self.update_params_layout(
            self.processor_params_layout,
            self.processor_param_fields,
            dist_name
        )
    
    def set_default_values(self):
        """Установка значений по умолчанию"""
        # Генератор
        self.generator_combo.setCurrentText(DEFAULT_VALUES['generator_dist'])
        for param, value in DEFAULT_VALUES['generator_params'].items():
            if param in self.generator_param_fields:
                self.generator_param_fields[param].setText(str(value))
        
        # Процессор
        self.processor_combo.setCurrentText(DEFAULT_VALUES['processor_dist'])
        for param, value in DEFAULT_VALUES['processor_params'].items():
            if param in self.processor_param_fields:
                self.processor_param_fields[param].setText(str(value))
        
        # Параметры моделирования
        self.num_tasks_field.setText(str(DEFAULT_VALUES['num_tasks']))
        self.return_prob_field.setText(str(DEFAULT_VALUES['return_probability']))
        self.time_step_field.setText(str(DEFAULT_VALUES['time_step']))
    
    def validate_and_get_params(self):
        """Валидация и получение всех параметров"""
        errors = []
        
        # Валидация параметров генератора
        generator_params = {}
        dist_name = self.generator_combo.currentText()
        
        for param_name, field in self.generator_param_fields.items():
            try:
                value = float(field.text().strip())
                generator_params[param_name] = value
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: white;
                    }
                """)
            except ValueError:
                errors.append(f"Генератор: параметр '{param_name}' должен быть числом")
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: #FFE0E0;
                    }
                """)
        
        # Дополнительная валидация для конкретных распределений
        if not errors:
            if dist_name == "Равномерное" and 'a' in generator_params and 'b' in generator_params:
                if generator_params['a'] >= generator_params['b']:
                    errors.append("Генератор: параметр 'b' должен быть больше 'a'")
            if 'λ' in generator_params and generator_params['λ'] <= 0:
                errors.append("Генератор: параметр 'λ' должен быть положительным")
            if 'σ' in generator_params and generator_params['σ'] <= 0:
                errors.append("Генератор: параметр 'σ' должен быть положительным")
            if 'k' in generator_params:
                if generator_params['k'] <= 0:
                    errors.append("Генератор: параметр 'k' должен быть положительным")
                elif generator_params['k'] != int(generator_params['k']):
                    errors.append("Генератор: параметр 'k' должен быть целым числом")
        
        # Валидация параметров процессора
        processor_params = {}
        proc_dist_name = self.processor_combo.currentText()
        
        for param_name, field in self.processor_param_fields.items():
            try:
                value = float(field.text().strip())
                processor_params[param_name] = value
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: white;
                    }
                """)
            except ValueError:
                errors.append(f"Обслуживающий аппарат: параметр '{param_name}' должен быть числом")
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: #FFE0E0;
                    }
                """)
        
        # Дополнительная валидация для процессора
        if not errors:
            if proc_dist_name == "Равномерное" and 'a' in processor_params and 'b' in processor_params:
                if processor_params['a'] >= processor_params['b']:
                    errors.append("Обслуживающий аппарат: параметр 'b' должен быть больше 'a'")
            if 'λ' in processor_params and processor_params['λ'] <= 0:
                errors.append("Обслуживающий аппарат: параметр 'λ' должен быть положительным")
            if 'σ' in processor_params and processor_params['σ'] <= 0:
                errors.append("Обслуживающий аппарат: параметр 'σ' должен быть положительным")
            if 'k' in processor_params:
                if processor_params['k'] <= 0:
                    errors.append("Обслуживающий аппарат: параметр 'k' должен быть положительным")
                elif processor_params['k'] != int(processor_params['k']):
                    errors.append("Обслуживающий аппарат: параметр 'k' должен быть целым числом")
        
        # Валидация параметров моделирования
        try:
            num_tasks = int(self.num_tasks_field.text().strip())
            if num_tasks <= 0:
                errors.append("Количество заявок должно быть положительным")
            self.num_tasks_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
        except ValueError:
            errors.append("Количество заявок должно быть целым числом")
            num_tasks = None
            self.num_tasks_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: #FFE0E0;
                }
            """)
        
        try:
            return_prob = int(self.return_prob_field.text().strip())
            if return_prob < 0 or return_prob > 100:
                errors.append("Вероятность возврата должна быть в диапазоне 0-100")
            self.return_prob_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
        except ValueError:
            errors.append("Вероятность возврата должна быть целым числом")
            return_prob = None
            self.return_prob_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: #FFE0E0;
                }
            """)
        
        try:
            time_step = float(self.time_step_field.text().strip())
            if time_step <= 0:
                errors.append("Временной шаг должен быть положительным")
            self.time_step_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
        except ValueError:
            errors.append("Временной шаг должен быть числом")
            time_step = None
            self.time_step_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: #FFE0E0;
                }
            """)
        
        # Отображение ошибок
        if errors:
            self.error_text.setText("\n".join(errors))
            self.error_panel.setVisible(True)
            return None
        else:
            self.error_panel.setVisible(False)
            return {
                'generator_dist': dist_name,
                'generator_params': generator_params,
                'processor_dist': proc_dist_name,
                'processor_params': processor_params,
                'num_tasks': num_tasks,
                'return_prob': return_prob,
                'time_step': time_step
            }
    
    def solve(self):
        """Запуск моделирования"""
        # Валидация параметров
        params = self.validate_and_get_params()
        if params is None:
            return
        
        try:
            # Создание объектов распределений
            generator = create_distribution(
                params['generator_dist'],
                params['generator_params']
            )
            
            processor = create_distribution(
                params['processor_dist'],
                params['processor_params']
            )
            
            # Запуск событийного моделирования
            event_result = event_model(
                generator,
                processor,
                params['num_tasks'],
                params['return_prob']
            )
            
            # Запуск пошагового моделирования
            step_result = step_model(
                generator,
                processor,
                params['num_tasks'],
                params['return_prob'],
                params['time_step']
            )
            
            # Отображение результатов
            self.step_result_field.setText(str(step_result))
            self.event_result_field.setText(str(event_result))
            
        except Exception as e:
            self.error_text.setText(f"Ошибка моделирования: {str(e)}")
            self.error_panel.setVisible(True)


def main():
    app = QApplication(sys.argv)
    window = SMOWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()