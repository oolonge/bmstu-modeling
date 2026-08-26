# -*- coding: utf-8 -*-
"""
Точка входа в приложение моделирования информационного центра
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Используем стиль Fusion для лучшего вида

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
