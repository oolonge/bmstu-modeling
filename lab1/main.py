import sys
import csv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

# Константы
SEED_TABLE = 12345  # Seed для табличного метода
SEED_LCG = 12345    # Seed для LCG
ROWS_COUNT = 10     # Количество генерируемых чисел

# Параметры LCG (MINSTD)
LCG_M = 2147483647  # 2^31 - 1
LCG_K = 48271
LCG_B = 0

class RandomNumberGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table_data = []
        self.load_table()
        self.init_ui()
        self.generate_numbers()
        
    def load_table(self):
        """Загрузка таблицы из CSV файла"""
        csv_data = """66194,28926,99547,16625,45515,67953,12108,57846
78240,43195,24837,32511,70880,22070,52622,61881
00833,88000,67299,68215,11274,55624,32991,17436
12111,86683,61270,58036,64192,90611,15145,01748
47189,99951,05755,03834,43782,90599,40282,51417
76396,72486,62423,27618,84184,78922,73561,52818
46409,17469,32483,09083,76175,19985,26309,91536
74626,22111,87286,46772,42243,68046,44250,42439
34450,81974,93723,49023,58432,67083,36876,93391
36327,72155,33005,28701,34710,49359,50693,89311
74185,77536,84895,09934,99103,09325,67389,45869
12096,41623,67873,37943,25584,09609,63360,47270
90822,60280,88925,99610,42772,60561,76873,04117
72121,79152,96591,90305,10189,79778,68016,13747
95268,41377,25684,08151,61816,58555,54305,86189
92603,09091,75884,93424,72586,88903,30061,14457
18813,90291,05275,01223,79607,95426,34900,09778
38840,26903,98624,67157,51986,42865,14508,49315
05959,33836,53758,16562,41081,38012,41230,20528
85141,21155,99212,32685,51403,31926,69813,58781
75047,59643,31074,38172,03718,32119,69506,67143
30752,95260,68032,62871,58781,34143,68790,69766
22986,82575,42187,62295,84295,30634,66562,31442
09439,86692,90348,66036,48399,73451,26608,39437
20389,93029,11881,71685,65452,89047,63669,02656
39249,05173,68256,36359,20250,68686,05947,09335
96777,33605,29481,20063,09398,01843,35139,61344
04860,32918,10798,50492,52655,33359,94713,28393
41613,42375,00403,03656,77580,87772,86877,57085
17930,00794,53836,53692,67135,98102,61912,11246
24649,31845,25736,75231,83808,98917,93829,99430
79899,34061,54308,59358,56462,58166,97302,86828
76801,49594,81002,30397,52728,15101,72070,33706"""
        
        for line in csv_data.strip().split('\n'):
            row = line.split(',')
            self.table_data.append(row)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('Лабораторная работа №1')
        self.setGeometry(100, 100, 1100, 600)
        
        # Создаём центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаём таблицу
        self.table = QTableWidget(ROWS_COUNT + 1, 7)
        
        # Заголовки
        headers = ['Таб. 1\n(0-9)', 'Таб. 2\n(10-99)', 'Таб. 3\n(100-999)',
                   'Алг. 1\n(0-9)', 'Алг. 2\n(10-99)', 'Алг. 3\n(100-999)',
                   'Ручной ввод\n(0-9)']
        self.table.setHorizontalHeaderLabels(headers)
        
        # Настройка таблицы
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        # Инициализация ячеек
        for row in range(ROWS_COUNT + 1):
            for col in range(7):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Последняя строка - проценты (нередактируемая)
                if row == ROWS_COUNT:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                # Столбец ручного ввода (редактируемый)
                elif col == 6:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                # Остальные столбцы (нередактируемые)
                else:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                
                self.table.setItem(row, col, item)
        
        # Обработчик изменения ячеек
        self.table.itemChanged.connect(self.on_cell_changed)
        
        layout.addWidget(self.table)
        
    def table_method(self, seed, count, min_val, max_val):
        """Табличный метод генерации"""
        result = []
        current = seed
        
        for _ in range(count):
            # Разбиваем число на координаты
            row_idx = (current // 1000) % 33  # Первые 2 цифры для строки
            col_idx = (current % 1000) % 8    # Последние 3 цифры для столбца
            
            # Получаем число из таблицы
            value = int(self.table_data[row_idx][col_idx])
            
            # Приводим к нужному диапазону
            if max_val == 9:
                value = value % 10
                if value == 0:  # Избегаем 0 для диапазона 0-9
                    value = (value + 1) % 10
            elif max_val == 99:
                value = (value % 90) + 10
            else:  # max_val == 999
                value = (value % 900) + 100
            
            result.append(value)
            current = int(self.table_data[row_idx][col_idx])
            
        return result
    
    def lcg_method(self, seed, count, min_val, max_val):
        """Линейный конгруэнтный метод"""
        result = []
        current = seed
        
        for _ in range(count):
            current = (LCG_K * current + LCG_B) % LCG_M
            
            # Приводим к нужному диапазону
            if max_val == 9:
                value = (current % 10)
                if value == 0:
                    value = (current % 9) + 1
            elif max_val == 99:
                value = (current % 90) + 10
            else:  # max_val == 999
                value = (current % 900) + 100
            
            result.append(value)
            
        return result
    
    def generate_numbers(self):
        """Генерация всех чисел"""
        # Табличный метод
        tab_1 = self.table_method(SEED_TABLE, ROWS_COUNT, 0, 9)
        tab_2 = self.table_method(SEED_TABLE + 1, ROWS_COUNT, 10, 99)
        tab_3 = self.table_method(SEED_TABLE + 2, ROWS_COUNT, 100, 999)
        
        # Алгоритмический метод
        alg_1 = self.lcg_method(SEED_LCG, ROWS_COUNT, 0, 9)
        alg_2 = self.lcg_method(SEED_LCG + 1000, ROWS_COUNT, 10, 99)
        alg_3 = self.lcg_method(SEED_LCG + 2000, ROWS_COUNT, 100, 999)
        
        # Заполняем таблицу
        columns = [tab_1, tab_2, tab_3, alg_1, alg_2, alg_3]
        
        for col_idx, column_data in enumerate(columns):
            for row_idx, value in enumerate(column_data):
                self.table.item(row_idx, col_idx).setText(str(value))
        
        # Рассчитываем проценты для сгенерированных столбцов
        for col in range(6):
            self.calculate_randomness(col)
    
    def calculate_randomness(self, col):
        """Расчёт процента случайности для столбца"""
        numbers = []
        for row in range(ROWS_COUNT):
            text = self.table.item(row, col).text()
            if text:
                try:
                    numbers.append(int(text))
                except ValueError:
                    return
        
        if len(numbers) != ROWS_COUNT:
            self.table.item(ROWS_COUNT, col).setText('')
            self.table.item(ROWS_COUNT, col).setBackground(QColor(255, 255, 255))
            return
        
        # Критерий 1: Отсутствие повторов (35%)
        repeats = sum(1 for i in range(len(numbers) - 1) if numbers[i] == numbers[i + 1])
        no_repeat_score = 1 - (repeats / (len(numbers) - 1))
        
        # Критерий 2: Глобальное распределение χ² (35%)
        unique_count = len(set(numbers))
        expected_freq = len(numbers) / unique_count
        observed_freqs = {}
        for num in numbers:
            observed_freqs[num] = observed_freqs.get(num, 0) + 1
        
        chi_square = sum((observed_freqs.get(num, 0) - expected_freq) ** 2 / expected_freq 
                        for num in set(numbers))
        
        # Нормализация χ² (чем меньше, тем лучше)
        max_value = 9  # или 99, или 999 в зависимости от столбца
        min_value = 0  # или 10, или 100
        range_size = max_value - min_value + 1
        expected_freq = len(numbers) / range_size

        chi_square = 0
        for value in range(min_value, max_value + 1):
            observed = observed_freqs.get(value, 0)
            chi_square += (observed - expected_freq) ** 2 / expected_freq

        # Теперь нормализуем χ² через критические значения
        # Для 9 степеней свободы (10 категорий - 1):
        # χ²_critical ≈ 16.9 (при p=0.05)
        chi_score = max(0, 1 - (chi_square / 16.9))
        
        # Критерий 3: Монотонность concordant/discordant (30%)
        concordant = 0
        discordant = 0
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                if numbers[j] > numbers[i]:
                    concordant += 1
                elif numbers[j] < numbers[i]:
                    discordant += 1
        
        total_pairs = concordant + discordant
        monotonicity_score = 1 - abs(concordant - discordant) / total_pairs if total_pairs > 0 else 0
        # монотонность (баланс возрастающими и убывающими) + отсутсвие повторов + глобальное распределение (хи2)
        # отклонение между наблюдаемыми и теоретическими, где наши теоретические это ожидаемая частота значений, 
        # а наблюдаемые - действительная
        # взвешанная сумма 
        # Итоговая оценка
        final_score = (0.35 * no_repeat_score + 
                      0.35 * chi_score + 
                      0.30 * monotonicity_score)
        
        percentage = int(final_score * 100)
        
        # Отображаем процент
        self.table.item(ROWS_COUNT, col).setText(f'{percentage}%')
        
        # Цветовая индикация
        if percentage >= 75:
            color = QColor(144, 238, 144)  # Светло-зелёный
        elif percentage >= 50:
            color = QColor(255, 255, 153)  # Жёлтый
        else:
            color = QColor(255, 182, 193)  # Светло-красный
        
        self.table.item(ROWS_COUNT, col).setBackground(color)
    
    def on_cell_changed(self, item):
        """Обработчик изменения ячейки"""
        if item.column() != 6 or item.row() == ROWS_COUNT:
            return
        
        text = item.text().strip()
        
        # Валидация: только цифры 0-9
        if text:
            try:
                value = int(text)
                if value < 0 or value > 9:
                    item.setText('')
                    return
            except ValueError:
                item.setText('')
                return
        
        # Пересчитываем процент
        self.calculate_randomness(6)

def main():
    app = QApplication(sys.argv)
    window = RandomNumberGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()