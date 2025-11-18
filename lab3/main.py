import sys
import numpy as np
from scipy import stats
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QComboBox, QLabel, QLineEdit, QFrame, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io

# ============= КОНСТАНТЫ =============
NUM_POINTS = 1500

# Размеры шрифтов
FONT_SIZE_TITLE = 18          # Заголовки ("Распределение:", "Параметры:")
FONT_SIZE_COMBO = 13         # Выпадающий список распределений
FONT_SIZE_PARAM_LABEL = 13    # Метки параметров (k =, λ =)
FONT_SIZE_PARAM_FIELD = 13    # Поля ввода параметров
FONT_SIZE_ERROR = 13          # Панель ошибок
FONT_SIZE_AXIS_LABEL = 13     # Подписи осей графика
FONT_SIZE_LEGEND = 13         # Легенда графика
FONT_SIZE_TICK = 13           # Метки на осях
FONT_SIZE_BUTTON = 13         # Размер шрифта кнопки

# Размер LaTeX формулы (в render_latex)
LATEX_FONT_SIZE = 24          # Размер символов формулы
LATEX_DPI = 1600               # DPI для рендеринга LaTeX (выше = четче)

# Внутренние отступы виджетов
WIDGET_PADDING = 12           # Отступы внутри виджетов (было 15 для segment1, 20 для segment2)

# ======================================


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Настройка стиля
        self.axes.set_facecolor('white')
        self.axes.grid(True, alpha=0.2, color='gray', linestyle='-', linewidth=0.5)
        self.axes.spines['top'].set_color('#CCCCCC')
        self.axes.spines['right'].set_color('#CCCCCC')
        self.axes.spines['bottom'].set_color('#666666')
        self.axes.spines['left'].set_color('#666666')
        self.axes.tick_params(colors='#666666', labelsize=FONT_SIZE_TICK)
        
        # Ограничение числа меток на оси Y
        self.axes.yaxis.set_major_locator(plt.MaxNLocator(5))


class DistributionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моделирование распределений")
        self.setGeometry(100, 100, 1300, 730)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === ЛЕВАЯ ПАНЕЛЬ (30%) ===
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #F8F8F8;")
        left_panel.setFixedWidth(420)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # Сегмент 1: Выбор распределения и формула
        segment1 = QFrame()
        segment1.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        segment1_layout = QVBoxLayout(segment1)
        segment1_layout.setSpacing(15)
        
        # ComboBox для выбора распределения
        combo_label = QLabel("Распределение:")
        combo_label.setFont(QFont("Arial", FONT_SIZE_TITLE, QFont.Weight.Bold))
        self.combo = QComboBox()
        self.combo.addItems([
            "Равномерное",
            "Пуассоновское", 
            "Экспоненциальное",
            "Нормальное",
            "Эрланга"
        ])
        self.combo.setFont(QFont("Arial", FONT_SIZE_COMBO))
        self.combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: white;
                color: black;
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
                color: black;
                selection-background-color: #E0E0E0;
                selection-color: black;
                border: 1px solid #CCCCCC;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #D0D0D0;
            }
        """)
        self.combo.currentIndexChanged.connect(self.on_distribution_changed)
        
        segment1_layout.addWidget(combo_label)
        segment1_layout.addWidget(self.combo)
        
        # Label для формулы (LaTeX) - фиксированный размер
        self.formula_label = QLabel()
        self.formula_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formula_label.setFixedHeight(100)
        self.formula_label.setScaledContents(True)
        self.formula_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        
        segment1_layout.addWidget(self.formula_label)
        left_layout.addWidget(segment1)
        left_layout.addSpacing(20)
        
        # Сегмент 2: Параметры
        segment2 = QFrame()
        segment2.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        segment2.setMinimumHeight(250)
        segment2_layout = QVBoxLayout(segment2)
        segment2_layout.setSpacing(15)
        
        params_title = QLabel("Параметры:")
        params_title.setFont(QFont("Arial", FONT_SIZE_TITLE, QFont.Weight.Bold))
        segment2_layout.addWidget(params_title)
        
        # Контейнер для параметров
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setSpacing(12)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        segment2_layout.addWidget(self.params_container)
        
        # Кнопка "Построить"
        self.build_button = QPushButton("Построить")
        self.build_button.setFont(QFont("Arial", FONT_SIZE_BUTTON, QFont.Weight.Bold))
        self.build_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.build_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.build_button.clicked.connect(self.on_param_changed)
        segment2_layout.addWidget(self.build_button)
        
        segment2_layout.addStretch()
        
        left_layout.addWidget(segment2)
        left_layout.addSpacing(20)
        
        # Сегмент 3: Панель ошибок
        self.error_panel = QFrame()
        self.error_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #FFF5F5;
                border: 2px solid #FFC9C9;
                border-radius: 8px;
                padding: {WIDGET_PADDING}px;
            }}
        """)
        self.error_panel.setVisible(False)  # Скрыта по умолчанию
        
        error_layout = QVBoxLayout(self.error_panel)
        error_layout.setSpacing(5)
        error_layout.setContentsMargins(0, 0, 0, 0)
        
        error_title = QLabel("⚠ Ошибка ввода:")
        error_title.setFont(QFont("Arial", FONT_SIZE_ERROR, QFont.Weight.Bold))
        error_title.setStyleSheet("color: #D32F2F;")
        
        self.error_text = QLabel()
        self.error_text.setFont(QFont("Arial", FONT_SIZE_ERROR))
        self.error_text.setWordWrap(True)
        self.error_text.setStyleSheet("color: #666666;")
        
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_text)
        
        left_layout.addWidget(self.error_panel)
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        
        # === ПРАВАЯ ПАНЕЛЬ (70%) - График ===
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        # Canvas для графика
        self.canvas = MplCanvas(self, width=10, height=8, dpi=100)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(right_panel)
        
        # Словарь для хранения полей ввода
        self.param_fields = {}
        
        # Параметры распределений с LaTeX формулами
        self.distributions = {
            "Равномерное": {
                "params": [("a", 0.0, "Нижняя граница интервала"), 
                          ("b", 1.0, "Верхняя граница интервала")],
                "latex": r"$f(x) = \frac{1}{b-a}$"
            },
            "Пуассоновское": {
                "params": [("λ", 3.0, "Интенсивность (среднее число событий)")],
                "latex": r"$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$"
            },
            "Экспоненциальное": {
                "params": [("λ", 1.0, "Интенсивность (скорость)")],
                "latex": r"$f(x) = \lambda e^{-\lambda x}$"
            },
            "Нормальное": {
                "params": [("μ", 0.0, "Математическое ожидание (среднее)"),
                          ("σ", 1.0, "Стандартное отклонение")],
                "latex": r"$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$"
            },
            "Эрланга": {
                "params": [("k", 2.0, "Параметр формы (целое число фаз)"),
                          ("λ", 1.0, "Интенсивность (скорость)")],
                "latex": r"$f(x) = \frac{\lambda^k x^{k-1} e^{-\lambda x}}{(k-1)!}$"
            }
        }
        
        # Инициализация
        self.on_distribution_changed()
        
    def render_latex(self, latex_string):
        """Рендеринг LaTeX формулы в QPixmap с улучшенным качеством"""
        try:
            # Создаем временный figure для рендеринга LaTeX
            fig = Figure(figsize=(4.5, 1), dpi=LATEX_DPI, facecolor='#FAFAFA')
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # Используем usetex для более качественного рендеринга
            # Если LaTeX недоступен, matplotlib использует mathtext
            ax.text(0.5, 0.5, latex_string, fontsize=LATEX_FONT_SIZE, ha='center', va='center',
                   transform=ax.transAxes)
            
            # Конвертируем в изображение с высоким разрешением
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', 
                       facecolor='#FAFAFA', edgecolor='none', pad_inches=0.1, 
                       dpi=LATEX_DPI)
            buf.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buf.read())
            plt.close(fig)
            
            # Масштабируем под размер label с сглаживанием
            scaled_pixmap = pixmap.scaled(360, 80, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
            return scaled_pixmap
        except Exception as e:
            print(f"Ошибка рендеринга LaTeX: {e}")
            return None
    
    def on_distribution_changed(self):
        """Обработчик смены распределения"""
        # Очистка старых полей
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.param_fields.clear()
        
        # Получение параметров текущего распределения
        dist_name = self.combo.currentText()
        dist_info = self.distributions[dist_name]
        
        # Обновление формулы через LaTeX
        latex_formula = dist_info["latex"]
        pixmap = self.render_latex(latex_formula)
        if pixmap:
            self.formula_label.setPixmap(pixmap)
        else:
            self.formula_label.setText("Ошибка отображения формулы")
        
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
            field.returnPressed.connect(self.on_param_changed)  # Обновление по Enter
            field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #CCCCCC;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
            
            self.param_fields[param_name] = field
            param_layout.addWidget(label)
            param_layout.addWidget(field, 1)
            
            self.params_layout.addWidget(param_widget)
        
        # Построение графика
        self.update_plot()
    
    def on_param_changed(self):
        """Обработчик изменения параметров (вызывается по Enter или по кнопке)"""
        self.update_plot()
    
    def validate_params(self):
        """Валидация параметров и подсветка некорректных полей"""
        dist_name = self.combo.currentText()
        params = {}
        all_valid = True
        error_messages = []
        
        for param_name, field in self.param_fields.items():
            text = field.text().strip()
            
            # Проверка на пустоту
            if not text:
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: #FFE0E0;
                    }
                """)
                error_messages.append(f"Параметр '{param_name}' не может быть пустым.")
                all_valid = False
                continue
            
            try:
                value = float(text)
                
                # Специальные проверки
                if dist_name == "Равномерное" and param_name == "b":
                    if "a" in self.param_fields:
                        a_text = self.param_fields["a"].text().strip()
                        if a_text:
                            try:
                                a_value = float(a_text)
                                if value <= a_value:
                                    field.setStyleSheet("""
                                        QLineEdit {
                                            padding: 8px;
                                            border: 2px solid #CCCCCC;
                                            border-radius: 4px;
                                            background-color: #FFE0E0;
                                        }
                                    """)
                                    error_messages.append(f"Параметр 'b' должен быть больше 'a' (b > a).")
                                    all_valid = False
                                    continue
                            except ValueError:
                                pass
                        
                if param_name in ["λ", "σ"] and value <= 0:
                    field.setStyleSheet("""
                        QLineEdit {
                            padding: 8px;
                            border: 2px solid #CCCCCC;
                            border-radius: 4px;
                            background-color: #FFE0E0;
                        }
                    """)
                    error_messages.append(f"Параметр '{param_name}' должен быть положительным числом (> 0).")
                    all_valid = False
                    continue
                    
                if param_name == "k":
                    if value <= 0:
                        field.setStyleSheet("""
                            QLineEdit {
                                padding: 8px;
                                border: 2px solid #CCCCCC;
                                border-radius: 4px;
                                background-color: #FFE0E0;
                            }
                        """)
                        error_messages.append(f"Параметр 'k' должен быть положительным целым числом.")
                        all_valid = False
                        continue
                    elif value != int(value):
                        field.setStyleSheet("""
                            QLineEdit {
                                padding: 8px;
                                border: 2px solid #CCCCCC;
                                border-radius: 4px;
                                background-color: #FFE0E0;
                            }
                        """)
                        error_messages.append(f"Параметр 'k' должен быть целым числом (используется в факториале).")
                        all_valid = False
                        continue
                
                # Если все ОК
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: white;
                    }
                """)
                params[param_name] = value
                
            except ValueError:
                field.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: #FFE0E0;
                    }
                """)
                error_messages.append(f"Параметр '{param_name}' должен быть числом (введены некорректные символы).")
                all_valid = False
        
        # Обновление панели ошибок
        if error_messages:
            self.error_text.setText("\n".join(error_messages))
            self.error_panel.setVisible(True)
        else:
            self.error_panel.setVisible(False)
        
        return params if all_valid else None
    
    def update_plot(self):
        """Обновление графика"""
        params = self.validate_params()
        if params is None:
            return
        
        dist_name = self.combo.currentText()
        self.canvas.axes.clear()
        
        # Настройка графика
        self.canvas.axes.set_facecolor('white')
        self.canvas.axes.grid(True, alpha=0.2, color='gray', linestyle='-', linewidth=0.5)
        self.canvas.axes.tick_params(colors='#666666', labelsize=FONT_SIZE_TICK)
        
        try:
            if dist_name == "Равномерное":
                self.plot_uniform(params)
            elif dist_name == "Пуассоновское":
                self.plot_poisson(params)
            elif dist_name == "Экспоненциальное":
                self.plot_exponential(params)
            elif dist_name == "Нормальное":
                self.plot_normal(params)
            elif dist_name == "Эрланга":
                self.plot_erlang(params)
        except Exception as e:
            print(f"Ошибка построения графика: {e}")
        
        self.canvas.draw()
    
    def plot_uniform(self, params):
        a, b = params["a"], params["b"]
        margin = 0.1 * (b - a)
        x = np.linspace(a - margin, b + margin, NUM_POINTS)
        
        # PDF
        pdf = np.where((x >= a) & (x <= b), 1/(b-a), 0)
        self.canvas.axes.plot(x, pdf, 'b-', linewidth=2.5, label='f(x)')
        
        # CDF
        cdf = np.where(x < a, 0, np.where(x > b, 1, (x - a)/(b - a)))
        self.canvas.axes.plot(x, cdf, 'r-', linewidth=2.5, label='F(x)')
        
        self.canvas.axes.set_xlabel('x', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.set_ylabel('Вероятность', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.legend(loc='best', fontsize=FONT_SIZE_LEGEND)
        self.canvas.axes.set_ylim(-0.1, 1.2)
    
    def plot_poisson(self, params):
        lam = params["λ"]
        k_max = int(lam + 4 * np.sqrt(lam))
        k = np.arange(0, k_max + 1)
        
        # PMF (дискретная плотность)
        pmf = stats.poisson.pmf(k, lam)
        markerline, stemlines, baseline = self.canvas.axes.stem(k, pmf, linefmt='b-', 
                                                                  markerfmt='bo', basefmt=' ', 
                                                                  label='Плотность (PMF)')
        plt.setp(stemlines, linewidth=2)
        plt.setp(markerline, markersize=6)
        
        # CDF (ступенчатая)
        cdf = stats.poisson.cdf(k, lam)
        self.canvas.axes.step(k, cdf, 'r-', linewidth=2.5, where='post', label='Распределение (CDF)')
        
        self.canvas.axes.set_xlabel('k', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.set_ylabel('Вероятность', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.legend(loc='best', fontsize=FONT_SIZE_LEGEND)
        self.canvas.axes.set_ylim(-0.05, 1.1)
    
    def plot_exponential(self, params):
        lam = params["λ"]
        x_max = -np.log(0.01) / lam
        x = np.linspace(0, x_max, NUM_POINTS)
        
        # PDF
        pdf = stats.expon.pdf(x, scale=1/lam)
        self.canvas.axes.plot(x, pdf, 'b-', linewidth=2.5, label='Плотность (PDF)')
        
        # CDF
        cdf = stats.expon.cdf(x, scale=1/lam)
        self.canvas.axes.plot(x, cdf, 'r-', linewidth=2.5, label='Распределение (CDF)')
        
        self.canvas.axes.set_xlabel('x', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.set_ylabel('Вероятность', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.legend(loc='best', fontsize=FONT_SIZE_LEGEND)
    
    def plot_normal(self, params):
        mu, sigma = params["μ"], params["σ"]
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, NUM_POINTS)
        
        # PDF
        pdf = stats.norm.pdf(x, mu, sigma)
        self.canvas.axes.plot(x, pdf, 'b-', linewidth=2.5, label='Плотность (PDF)')
        
        # CDF
        cdf = stats.norm.cdf(x, mu, sigma)
        self.canvas.axes.plot(x, cdf, 'r-', linewidth=2.5, label='Распределение (CDF)')
        
        self.canvas.axes.set_xlabel('x', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.set_ylabel('Вероятность', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.legend(loc='best', fontsize=FONT_SIZE_LEGEND)
    
    def plot_erlang(self, params):
        k, lam = int(params["k"]), params["λ"]
        mean = k / lam
        std = np.sqrt(k) / lam
        x_max = mean + 4 * std
        x = np.linspace(0, x_max, NUM_POINTS)
        
        # PDF (Эрланг = Гамма с целым k)
        pdf = stats.gamma.pdf(x, a=k, scale=1/lam)
        self.canvas.axes.plot(x, pdf, 'b-', linewidth=2.5, label='Плотность (PDF)')
        
        # CDF
        cdf = stats.gamma.cdf(x, a=k, scale=1/lam)
        self.canvas.axes.plot(x, cdf, 'r-', linewidth=2.5, label='Распределение (CDF)')
        
        self.canvas.axes.set_xlabel('x', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.set_ylabel('Вероятность', fontsize=FONT_SIZE_AXIS_LABEL, color='#666666')
        self.canvas.axes.legend(loc='best', fontsize=FONT_SIZE_LEGEND)


def main():
    app = QApplication(sys.argv)
    window = DistributionWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()