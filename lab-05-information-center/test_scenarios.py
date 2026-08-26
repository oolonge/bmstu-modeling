# -*- coding: utf-8 -*-
"""
Тестирование различных сценариев работы системы
"""

from models.distributions import UniformDistribution
from models.elements import ClientGenerator, Operator, Computer
from models.event_model import simulate_info_center


def test_scenario_1():
    """Сценарий 1: Стандартная конфигурация из задания"""
    print("=" * 60)
    print("СЦЕНАРИЙ 1: Стандартная конфигурация (3 оператора, 2 компьютера)")
    print("=" * 60)

    generator_dist = UniformDistribution.from_mean_and_deviation(10.0, 2.0)
    generator = ClientGenerator(generator_dist)

    operators = [
        Operator(0, UniformDistribution.from_mean_and_deviation(20.0, 5.0), 0),
        Operator(1, UniformDistribution.from_mean_and_deviation(40.0, 10.0), 0),
        Operator(2, UniformDistribution.from_mean_and_deviation(40.0, 20.0), 1),
    ]

    computers = [
        Computer(0, 15.0),
        Computer(1, 30.0),
    ]

    results = simulate_info_center(generator, operators, computers, 300)

    print(f"Результаты:")
    print(f"  Всего клиентов: {results.total_clients}")
    print(f"  Обработано: {results.processed_clients}")
    print(f"  Отклонено: {results.rejected_clients}")
    print(f"  Вероятность отказа: {results.rejection_probability * 100:.2f}%")
    for queue_id, (max_size, avg_size) in results.queue_stats.items():
        print(f"  Накопитель {queue_id + 1}: макс={max_size}, среднее={avg_size:.2f}")
    print()


def test_scenario_2():
    """Сценарий 2: Увеличенная нагрузка (клиенты приходят чаще)"""
    print("=" * 60)
    print("СЦЕНАРИЙ 2: Увеличенная нагрузка (клиенты каждые 5±1 мин)")
    print("=" * 60)

    # Клиенты приходят вдвое чаще
    generator_dist = UniformDistribution.from_mean_and_deviation(5.0, 1.0)
    generator = ClientGenerator(generator_dist)

    operators = [
        Operator(0, UniformDistribution.from_mean_and_deviation(20.0, 5.0), 0),
        Operator(1, UniformDistribution.from_mean_and_deviation(40.0, 10.0), 0),
        Operator(2, UniformDistribution.from_mean_and_deviation(40.0, 20.0), 1),
    ]

    computers = [
        Computer(0, 15.0),
        Computer(1, 30.0),
    ]

    results = simulate_info_center(generator, operators, computers, 300)

    print(f"Результаты:")
    print(f"  Всего клиентов: {results.total_clients}")
    print(f"  Обработано: {results.processed_clients}")
    print(f"  Отклонено: {results.rejected_clients}")
    print(f"  Вероятность отказа: {results.rejection_probability * 100:.2f}%")
    for queue_id, (max_size, avg_size) in results.queue_stats.items():
        print(f"  Накопитель {queue_id + 1}: макс={max_size}, среднее={avg_size:.2f}")
    print()


def test_scenario_3():
    """Сценарий 3: Все операторы одинаковой производительности"""
    print("=" * 60)
    print("СЦЕНАРИЙ 3: Все операторы одинаковой производительности")
    print("=" * 60)

    generator_dist = UniformDistribution.from_mean_and_deviation(10.0, 2.0)
    generator = ClientGenerator(generator_dist)

    # Все операторы: 30 ± 5 мин
    operators = [
        Operator(0, UniformDistribution.from_mean_and_deviation(30.0, 5.0), 0),
        Operator(1, UniformDistribution.from_mean_and_deviation(30.0, 5.0), 0),
        Operator(2, UniformDistribution.from_mean_and_deviation(30.0, 5.0), 1),
    ]

    computers = [
        Computer(0, 15.0),
        Computer(1, 30.0),
    ]

    results = simulate_info_center(generator, operators, computers, 300)

    print(f"Результаты:")
    print(f"  Всего клиентов: {results.total_clients}")
    print(f"  Обработано: {results.processed_clients}")
    print(f"  Отклонено: {results.rejected_clients}")
    print(f"  Вероятность отказа: {results.rejection_probability * 100:.2f}%")
    for queue_id, (max_size, avg_size) in results.queue_stats.items():
        print(f"  Накопитель {queue_id + 1}: макс={max_size}, среднее={avg_size:.2f}")
    print()


def test_scenario_4():
    """Сценарий 4: Больше операторов (5 операторов, 3 компьютера)"""
    print("=" * 60)
    print("СЦЕНАРИЙ 4: Расширенная система (5 операторов, 3 компьютера)")
    print("=" * 60)

    generator_dist = UniformDistribution.from_mean_and_deviation(10.0, 2.0)
    generator = ClientGenerator(generator_dist)

    operators = [
        Operator(0, UniformDistribution.from_mean_and_deviation(20.0, 5.0), 0),
        Operator(1, UniformDistribution.from_mean_and_deviation(25.0, 5.0), 0),
        Operator(2, UniformDistribution.from_mean_and_deviation(30.0, 5.0), 1),
        Operator(3, UniformDistribution.from_mean_and_deviation(35.0, 5.0), 1),
        Operator(4, UniformDistribution.from_mean_and_deviation(40.0, 5.0), 2),
    ]

    computers = [
        Computer(0, 15.0),
        Computer(1, 20.0),
        Computer(2, 25.0),
    ]

    results = simulate_info_center(generator, operators, computers, 300)

    print(f"Результаты:")
    print(f"  Всего клиентов: {results.total_clients}")
    print(f"  Обработано: {results.processed_clients}")
    print(f"  Отклонено: {results.rejected_clients}")
    print(f"  Вероятность отказа: {results.rejection_probability * 100:.2f}%")
    for queue_id, (max_size, avg_size) in results.queue_stats.items():
        print(f"  Накопитель {queue_id + 1}: макс={max_size}, среднее={avg_size:.2f}")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ РАЗЛИЧНЫХ СЦЕНАРИЕВ")
    print("=" * 60 + "\n")

    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
    test_scenario_4()

    print("=" * 60)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО")
    print("=" * 60)
