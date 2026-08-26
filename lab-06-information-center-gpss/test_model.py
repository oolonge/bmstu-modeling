# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки событийной модели без GUI
"""

from models.distributions import UniformDistribution
from models.elements import ClientGenerator, Operator, Computer
from models.event_model import simulate_info_center


def test_basic_simulation():
    """Тест базового моделирования с параметрами из задания"""
    print("=== Тест моделирования информационного центра ===\n")

    # Создаём генератор клиентов: 10 ± 2 мин
    generator_dist = UniformDistribution.from_mean_and_deviation(10.0, 2.0)
    generator = ClientGenerator(generator_dist)
    print(f"Генератор: интервал [{generator_dist.a:.1f}, {generator_dist.b:.1f}] мин")

    # Создаём операторов
    operators = []

    # Оператор 1: 20 ± 5 мин -> Компьютер 0
    op1_dist = UniformDistribution.from_mean_and_deviation(20.0, 5.0)
    operators.append(Operator(0, op1_dist, 0))
    print(f"Оператор 1: [{op1_dist.a:.1f}, {op1_dist.b:.1f}] мин, "
          f"производительность={operators[0].productivity:.4f}, компьютер 1")

    # Оператор 2: 40 ± 10 мин -> Компьютер 0
    op2_dist = UniformDistribution.from_mean_and_deviation(40.0, 10.0)
    operators.append(Operator(1, op2_dist, 0))
    print(f"Оператор 2: [{op2_dist.a:.1f}, {op2_dist.b:.1f}] мин, "
          f"производительность={operators[1].productivity:.4f}, компьютер 1")

    # Оператор 3: 40 ± 20 мин -> Компьютер 1
    op3_dist = UniformDistribution.from_mean_and_deviation(40.0, 20.0)
    operators.append(Operator(2, op3_dist, 1))
    print(f"Оператор 3: [{op3_dist.a:.1f}, {op3_dist.b:.1f}] мин, "
          f"производительность={operators[2].productivity:.4f}, компьютер 2")

    # Создаём компьютеры
    computers = [
        Computer(0, 15.0),  # Компьютер 1: 15 мин
        Computer(1, 30.0),  # Компьютер 2: 30 мин
    ]
    print(f"\nКомпьютер 1: {computers[0].processing_time:.1f} мин")
    print(f"Компьютер 2: {computers[1].processing_time:.1f} мин")

    # Запускаем моделирование
    print("\n=== Запуск моделирования (300 клиентов) ===\n")
    results = simulate_info_center(generator, operators, computers, 300)

    # Выводим результаты
    print(f"Всего клиентов: {results.total_clients}")
    print(f"Обработано: {results.processed_clients}")
    print(f"Отклонено: {results.rejected_clients}")
    print(f"\nВероятность отказа: {results.rejection_probability * 100:.2f}%")

    print("\n=== Статистика по накопителям ===")
    for queue_id, (max_size, avg_size) in results.queue_stats.items():
        print(f"Накопитель {queue_id + 1} (к компьютеру {queue_id + 1}):")
        print(f"  Максимальная длина: {max_size}")
        print(f"  Средняя длина: {avg_size:.2f}")

    print("\n=== Тест завершён успешно ===")


if __name__ == '__main__':
    test_basic_simulation()
