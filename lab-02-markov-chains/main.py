"""
Лабораторная работа №2: Марковский процесс
Определение времени и вероятности пребывания системы в каждом состоянии
при установившемся режиме
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MarkovResult:
    """Результаты расчёта марковского процесса"""
    states: List[str]  # Названия состояний
    probabilities: np.ndarray  # Вероятности состояний
    times: np.ndarray  # Времена пребывания
    is_valid: bool  # Корректность результата
    error_message: Optional[str] = None


class MarkovProcess:
    """Класс для анализа марковского процесса"""
    
    def __init__(self, transition_matrix: np.ndarray):
        """
        Инициализация марковского процесса
        
        Args:
            transition_matrix: матрица интенсивностей переходов λᵢⱼ
                              где λᵢⱼ - интенсивность перехода из i в j
        """
        self.lambda_matrix = np.array(transition_matrix, dtype=float)
        self.n_states = len(self.lambda_matrix)
        
    def validate_input(self) -> Tuple[bool, Optional[str]]:
        """
        Проверка корректности входных данных
        
        Returns:
            (is_valid, error_message)
        """
        # Проверка квадратности матрицы
        if self.lambda_matrix.shape[0] != self.lambda_matrix.shape[1]:
            return False, "Матрица должна быть квадратной"
        
        # Проверка неотрицательности
        if np.any(self.lambda_matrix < 0):
            return False, "Интенсивности переходов не могут быть отрицательными"
        
        # Проверка диагонали
        if not np.allclose(np.diag(self.lambda_matrix), 0):
            return False, "Диагональ матрицы должна содержать только нули"
        
        # Проверка связности графа
        if not self._is_graph_connected():
            return False, "Граф переходов должен быть связным"
        
        return True, None
    
    def _is_graph_connected(self) -> bool:
        """
        Проверка связности графа переходов
        Использует поиск в ширину (BFS)
        """
        n = self.n_states
        # Создаём матрицу смежности (есть ребро, если λᵢⱼ > 0)
        adj_matrix = (self.lambda_matrix > 0).astype(int)
        
        # Делаем граф неориентированным для проверки связности
        adj_matrix = np.logical_or(adj_matrix, adj_matrix.T).astype(int)
        
        # BFS от вершины 0
        visited = [False] * n
        queue = [0]
        visited[0] = True
        
        while queue:
            v = queue.pop(0)
            for u in range(n):
                if adj_matrix[v][u] and not visited[u]:
                    visited[u] = True
                    queue.append(u)
        
        return all(visited)
    
    def _build_linear_system(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Построение системы линейных уравнений для стационарного режима
        
        Система уравнений:
        1. Для каждого состояния i: 0 = -Pᵢ·(Σⱼ λᵢⱼ) + Σₖ(Pₖ·λₖᵢ)
        2. Условие нормировки: Σᵢ Pᵢ = 1
        
        Returns:
            (A, b) где A·P = b
        """
        n = self.n_states
        A = np.zeros((n, n))
        b = np.zeros(n)
        
        # Формируем уравнения Колмогорова для первых (n-1) состояний
        for i in range(n - 1):
            # Коэффициент при Pᵢ: -Σⱼ λᵢⱼ
            A[i, i] = -np.sum(self.lambda_matrix[i, :])
            
            # Коэффициенты при Pₖ для k ≠ i: λₖᵢ
            for k in range(n):
                if k != i:
                    A[i, k] += self.lambda_matrix[k, i]
        
        # Последнее уравнение - условие нормировки: Σᵢ Pᵢ = 1
        A[n - 1, :] = 1
        b[n - 1] = 1
        
        return A, b
    
    def _solve_linear_system(self, A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
        """
        Решение системы линейных уравнений методом Гаусса
        
        Args:
            A: матрица коэффициентов
            b: вектор правой части
            
        Returns:
            Вектор решений или None при ошибке
        """
        try:
            # Используем numpy для решения (более устойчиво численно)
            solution = np.linalg.solve(A, b)
            
            # Проверка корректности: вероятности должны быть неотрицательными
            if np.any(solution < -1e-10):  # Учитываем погрешность
                return None
                
            # Нормализуем на случай численных ошибок
            solution = np.maximum(solution, 0)
            solution = solution / np.sum(solution)
            
            return solution
            
        except np.linalg.LinAlgError:
            return None
    
    def _calculate_residence_times(self, probabilities: np.ndarray) -> np.ndarray:
        """
        Расчёт времени пребывания в каждом состоянии
        
        Формула: tᵢ = Pᵢ / Σⱼ λᵢⱼ
        
        Args:
            probabilities: вероятности состояний
            
        Returns:
            Времена пребывания в состояниях
        """
        times = np.zeros(self.n_states)
        
        for i in range(self.n_states):
            # Суммарная интенсивность выхода из состояния i
            lambda_out = np.sum(self.lambda_matrix[i, :])
            
            if lambda_out > 1e-10:  # Проверка деления на ноль
                times[i] = probabilities[i] / lambda_out
            else:
                # Если из состояния нет выходов (поглощающее состояние)
                times[i] = float('inf')
        
        return times
    
    def solve(self) -> MarkovResult:
        """
        Решение задачи: нахождение вероятностей и времён пребывания
        
        Returns:
            MarkovResult с результатами расчёта
        """
        # Валидация входных данных
        is_valid, error_msg = self.validate_input()
        if not is_valid:
            return MarkovResult(
                states=[],
                probabilities=np.array([]),
                times=np.array([]),
                is_valid=False,
                error_message=error_msg
            )
        
        # Построение и решение СЛАУ
        A, b = self._build_linear_system()
        probabilities = self._solve_linear_system(A, b)
        
        if probabilities is None:
            return MarkovResult(
                states=[],
                probabilities=np.array([]),
                times=np.array([]),
                is_valid=False,
                error_message="Не удалось решить систему уравнений"
            )
        
        # Расчёт времён пребывания
        times = self._calculate_residence_times(probabilities)
        
        # Формирование имён состояний
        states = [f"S{i}" for i in range(self.n_states)]
        
        return MarkovResult(
            states=states,
            probabilities=probabilities,
            times=times,
            is_valid=True
        )


# ============================================================================
# КОНСОЛЬНЫЙ ИНТЕРФЕЙС (легко заменяется на GUI)
# ============================================================================

def print_result(result: MarkovResult) -> None:
    """
    Вывод результатов в консоль
    
    Args:
        result: результаты расчёта
    """
    if not result.is_valid:
        print(f"\n❌ Ошибка: {result.error_message}")
        return
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ РАСЧЁТА МАРКОВСКОГО ПРОЦЕССА")
    print("="*60)
    
    # Таблица результатов
    print(f"\n{'Состояние':<15} {'Время':<20} {'Вероятность':<20}")
    print("-" * 60)
    
    for state, time, prob in zip(result.states, result.times, result.probabilities):
        time_str = f"{time:.6f}" if time != float('inf') else "∞"
        print(f"{state:<15} {time_str:<20} {prob:.6f}")
    
    # Проверка нормировки
    prob_sum = np.sum(result.probabilities)
    print("-" * 60)
    print(f"{'Сумма вероятностей:':<35} {prob_sum:.10f}")
    
    if abs(prob_sum - 1.0) < 1e-6:
        print("✓ Условие нормировки выполнено")
    else:
        print("⚠ Внимание: условие нормировки не выполнено!")
    
    print("="*60 + "\n")


def input_matrix_console() -> Optional[np.ndarray]:
    """
    Ввод матрицы интенсивностей через консоль
    
    Returns:
        Матрица интенсивностей или None при ошибке
    """
    print("\n" + "="*60)
    print("ВВОД МАТРИЦЫ ИНТЕНСИВНОСТЕЙ ПЕРЕХОДОВ")
    print("="*60)
    
    try:
        n = int(input("\nВведите количество состояний (2-10): "))
        
        if n < 2 or n > 10:
            print("❌ Количество состояний должно быть от 2 до 10")
            return None
        
        print(f"\nВведите матрицу {n}x{n} (λᵢⱼ - интенсивность перехода из i в j)")
        print("Диагональ должна содержать нули!")
        print("Каждую строку вводите через пробел.\n")
        
        matrix = []
        for i in range(n):
            while True:
                row_str = input(f"Строка {i} (S{i}): ")
                try:
                    row = list(map(float, row_str.split()))
                    if len(row) != n:
                        print(f"❌ Ожидалось {n} чисел, получено {len(row)}. Повторите ввод.")
                        continue
                    matrix.append(row)
                    break
                except ValueError:
                    print("❌ Ошибка формата. Вводите числа через пробел.")
        
        return np.array(matrix)
        
    except ValueError:
        print("❌ Ошибка ввода")
        return None
    except KeyboardInterrupt:
        print("\n\n❌ Ввод прерван пользователем")
        return None


def run_console_interface():
    """Запуск консольного интерфейса"""
    print("\n" + "="*60)
    print("ЛАБОРАТОРНАЯ РАБОТА №2: МАРКОВСКИЙ ПРОЦЕСС")
    print("="*60)
    print("Определение времени и вероятности пребывания системы")
    print("в каждом состоянии при установившемся режиме")
    
    while True:
        print("\n" + "-"*60)
        print("1. Ввести матрицу вручную")
        print("2. Использовать тестовый пример")
        print("3. Выход")
        print("-"*60)
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == '1':
            matrix = input_matrix_console()
            if matrix is not None:
                process = MarkovProcess(matrix)
                result = process.solve()
                print_result(result)
                
        elif choice == '2':
            # Тестовый пример из лекций
            print("\nТестовый пример: система с 3 состояниями")
            matrix = np.array([
                [0, 2, 0],
                [1, 0, 3],
                [0, 1, 0]
            ])
            print("\nМатрица интенсивностей:")
            print(matrix)
            
            process = MarkovProcess(matrix)
            result = process.solve()
            print_result(result)
            
        elif choice == '3':
            print("\nЗавершение работы программы.")
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


def run_gui_interface():
    """Запуск GUI интерфейса на PyQt5"""
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QHBoxLayout, QLabel, QComboBox, QPushButton, 
                                  QLineEdit, QTableWidget, QTableWidgetItem, 
                                  QGridLayout, QMessageBox, QFileDialog, QSplitter,
                                  QGroupBox, QHeaderView)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QDoubleValidator, QFont
    import sys
    
    class MarkovGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Лабораторная работа №2: Марковский процесс")
            self.setMinimumSize(1200, 700)
            
            # Текущий размер матрицы
            self.current_size = 3
            
            # Хранилище значений матрицы (для сохранения при изменении размера)
            self.matrix_values = {}
            
            self.init_ui()
            
        def init_ui(self):
            """Инициализация интерфейса"""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            main_layout = QVBoxLayout(central_widget)
            
            # Разделитель на две части (левая и правая)
            splitter = QSplitter(Qt.Horizontal)
            
            # ========== ЛЕВАЯ ЧАСТЬ: Ввод матрицы ==========
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            
            # Заголовок
            title_label = QLabel("Матрица интенсивностей переходов")
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(title_label)
            
            # Выбор размера матрицы
            size_layout = QHBoxLayout()
            size_label = QLabel("Количество состояний:")
            self.size_combo = QComboBox()
            self.size_combo.addItems([str(i) for i in range(2, 10)])
            self.size_combo.setCurrentText(str(self.current_size))
            self.size_combo.currentTextChanged.connect(self.on_size_changed)
            
            size_layout.addWidget(size_label)
            size_layout.addWidget(self.size_combo)
            size_layout.addStretch()
            left_layout.addLayout(size_layout)
            
            # Кнопки управления
            buttons_layout = QHBoxLayout()
            
            self.clear_button = QPushButton("Очистить")
            self.clear_button.clicked.connect(self.clear_matrix)
            
            self.load_button = QPushButton("Загрузить")
            self.load_button.clicked.connect(self.load_from_file)
            
            buttons_layout.addWidget(self.clear_button)
            buttons_layout.addWidget(self.load_button)
            buttons_layout.addStretch()
            left_layout.addLayout(buttons_layout)
            
            # Контейнер для матрицы
            self.matrix_container = QWidget()
            self.matrix_layout = QGridLayout(self.matrix_container)
            self.matrix_layout.setSpacing(2)
            left_layout.addWidget(self.matrix_container)
            left_layout.addStretch()
            
            # ========== ПРАВАЯ ЧАСТЬ: Результаты ==========
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            
            # Заголовок
            result_title = QLabel("Результаты расчёта")
            result_title.setFont(title_font)
            result_title.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(result_title)
            
            # Таблица результатов
            self.result_table = QTableWidget()
            self.result_table.setColumnCount(3)
            self.result_table.setHorizontalHeaderLabels(["Состояние", "Время", "Вероятность"])
            self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
            right_layout.addWidget(self.result_table)
            
            # Статус валидации
            self.status_label = QLabel("")
            self.status_label.setAlignment(Qt.AlignCenter)
            self.status_label.setWordWrap(True)
            status_font = QFont()
            status_font.setPointSize(10)
            self.status_label.setFont(status_font)
            right_layout.addWidget(self.status_label)
            
            # ========== Добавление в сплиттер ==========
            splitter.addWidget(left_widget)
            splitter.addWidget(right_widget)
            splitter.setSizes([600, 600])
            
            main_layout.addWidget(splitter)
            
            # ========== КНОПКА ВЫЧИСЛИТЬ (внизу по центру) ==========
            calc_button_layout = QHBoxLayout()
            calc_button_layout.addStretch()
            
            self.calc_button = QPushButton("Вычислить")
            self.calc_button.setMinimumSize(200, 40)
            calc_font = QFont()
            calc_font.setPointSize(11)
            calc_font.setBold(True)
            self.calc_button.setFont(calc_font)
            self.calc_button.clicked.connect(self.calculate)
            
            calc_button_layout.addWidget(self.calc_button)
            calc_button_layout.addStretch()
            
            main_layout.addLayout(calc_button_layout)
            
            # Создаём начальную матрицу
            self.create_matrix_grid(self.current_size)
            
        def create_matrix_grid(self, size):
            """Создание сетки ввода матрицы"""
            # Очистка старой сетки
            for i in reversed(range(self.matrix_layout.count())):
                widget = self.matrix_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Размер ячейки (подбираем оптимальный)
            cell_size = int(max(50, min(70, 600 // (size + 1))) * 0.723)
            
            # Пустая ячейка в левом верхнем углу (для выравнивания)
            corner_spacer = QLabel("")
            corner_spacer.setFixedSize(cell_size, cell_size)
            self.matrix_layout.addWidget(corner_spacer, 0, 0)
            
            # Подписи столбцов (сверху)
            for j in range(size):
                label = QLabel(f"S{j}")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("font-weight: bold;")
                label.setFixedWidth(cell_size)
                self.matrix_layout.addWidget(label, 0, j + 1)
            
            # Подписи строк (слева) + ячейки ввода
            self.matrix_inputs = []
            
            for i in range(size):
                row_inputs = []
                
                # Подпись строки
                label = QLabel(f"S{i}")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("font-weight: bold;")
                label.setFixedSize(cell_size, cell_size)
                self.matrix_layout.addWidget(label, i + 1, 0)
                
                # Ячейки ввода
                for j in range(size):
                    input_field = QLineEdit()
                    input_field.setAlignment(Qt.AlignCenter)
                    input_field.setFixedSize(cell_size, cell_size)
                    
                    # Валидатор: только неотрицательные числа
                    validator = QDoubleValidator(0.0, 999999.0, 6)
                    validator.setNotation(QDoubleValidator.StandardNotation)
                    input_field.setValidator(validator)
                    
                    # Диагональные элементы недоступны
                    if i == j:
                        input_field.setText("0")
                        input_field.setEnabled(False)
                        input_field.setStyleSheet("background-color: #e0e0e0;")
                    else:
                        # Восстанавливаем старое значение или ставим 0
                        old_value = self.matrix_values.get((i, j), "0")
                        input_field.setText(old_value)
                    
                    self.matrix_layout.addWidget(input_field, i + 1, j + 1)
                    row_inputs.append(input_field)
                
                self.matrix_inputs.append(row_inputs)
            
            # Устанавливаем выравнивание сетки по левому верхнему углу
            self.matrix_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        def on_size_changed(self, text):
            """Обработка изменения размера матрицы"""
            # Сохраняем текущие значения
            self.save_matrix_values()
            
            # Обновляем размер
            new_size = int(text)
            self.current_size = new_size
            
            # Пересоздаём сетку
            self.create_matrix_grid(new_size)
            
            # Очищаем результаты
            self.result_table.setRowCount(0)
            self.status_label.setText("")
        
        def save_matrix_values(self):
            """Сохранение текущих значений матрицы"""
            for i in range(len(self.matrix_inputs)):
                for j in range(len(self.matrix_inputs[i])):
                    if i != j:
                        value = self.matrix_inputs[i][j].text().strip()
                        if value:
                            self.matrix_values[(i, j)] = value
        
        def clear_matrix(self):
            """Очистка матрицы"""
            for i in range(len(self.matrix_inputs)):
                for j in range(len(self.matrix_inputs[i])):
                    if i != j:
                        self.matrix_inputs[i][j].setText("0")
            
            self.matrix_values.clear()
            self.result_table.setRowCount(0)
            self.status_label.setText("")
        
        def load_from_file(self):
            """Загрузка матрицы из файла"""
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Загрузить матрицу", 
                "", 
                "Text Files (*.txt);;All Files (*)"
            )
            
            if not file_path:
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Парсим матрицу
                loaded_matrix = []
                for line in lines:
                    line = line.strip()
                    if line:
                        row = []
                        for val in line.split():
                            try:
                                row.append(float(val))
                            except ValueError:
                                pass
                        if row:
                            loaded_matrix.append(row)
                
                if not loaded_matrix:
                    QMessageBox.warning(self, "Ошибка", "Файл не содержит корректных данных")
                    return
                
                # Заполняем текущую матрицу
                size = self.current_size
                for i in range(size):
                    for j in range(size):
                        if i != j:
                            # Берём значение из файла или 0
                            if i < len(loaded_matrix) and j < len(loaded_matrix[i]):
                                value = loaded_matrix[i][j]
                                # Форматируем: если целое - без точки, иначе с точкой
                                if value == int(value):
                                    self.matrix_inputs[i][j].setText(str(int(value)))
                                else:
                                    self.matrix_inputs[i][j].setText(str(value))
                            else:
                                self.matrix_inputs[i][j].setText("0")
                
                QMessageBox.information(self, "Успех", "Матрица успешно загружена")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
        
        def get_matrix(self):
            """Получение матрицы из полей ввода"""
            size = self.current_size
            matrix = np.zeros((size, size))
            
            for i in range(size):
                for j in range(size):
                    if i != j:
                        text = self.matrix_inputs[i][j].text().strip()
                        if text:
                            try:
                                matrix[i][j] = float(text)
                            except ValueError:
                                matrix[i][j] = 0.0
            
            return matrix
        
        def calculate(self):
            """Выполнение расчёта"""
            # Получаем матрицу
            matrix = self.get_matrix()
            
            # Создаём процесс и решаем
            process = MarkovProcess(matrix)
            result = process.solve()
            
            # Отображаем результат
            if not result.is_valid:
                QMessageBox.critical(self, "Ошибка", result.error_message)
                self.result_table.setRowCount(0)
                self.status_label.setText("")
                return
            
            # Заполняем таблицу
            self.result_table.setRowCount(len(result.states))
            
            for idx, (state, time, prob) in enumerate(zip(
                result.states, result.times, result.probabilities
            )):
                # Состояние
                self.result_table.setItem(idx, 0, QTableWidgetItem(state))
                
                # Время
                time_str = f"{time:.6f}" if time != float('inf') else "∞"
                self.result_table.setItem(idx, 1, QTableWidgetItem(time_str))
                
                # Вероятность
                self.result_table.setItem(idx, 2, QTableWidgetItem(f"{prob:.6f}"))
            
            # Статус валидации
            prob_sum = np.sum(result.probabilities)
            status_text = f"Σ P = {prob_sum:.10f}"
            
            if abs(prob_sum - 1.0) < 1e-6:
                status_text += " ✓ (норма выполнена)"
                self.status_label.setStyleSheet("color: green;")
            else:
                status_text += " ⚠ (норма не выполнена)"
                self.status_label.setStyleSheet("color: red;")
            
            self.status_label.setText(status_text)
    
    # Запуск приложения
    app = QApplication(sys.argv)
    window = MarkovGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Выбор интерфейса
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        run_console_interface()
    else:
        run_gui_interface()