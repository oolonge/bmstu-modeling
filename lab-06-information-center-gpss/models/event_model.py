# -*- coding: utf-8 -*-
"""
Реализация событийного подхода моделирования информационного центра
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
from .elements import ClientGenerator, Operator, Computer, Queue


class EventType(Enum):
    """Типы событий в системе"""
    CLIENT_ARRIVAL = "client_arrival"       # Прибытие клиента
    OPERATOR_FINISH = "operator_finish"     # Окончание обработки оператором
    COMPUTER_FINISH = "computer_finish"     # Окончание обработки компьютером


class Event:
    """Событие в системе"""

    def __init__(self, event_type: EventType, time: float, entity_id: Optional[int] = None):
        """
        Args:
            event_type: Тип события
            time: Время наступления события
            entity_id: ID сущности (оператора/компьютера), если применимо
        """
        self.event_type = event_type
        self.time = time
        self.entity_id = entity_id

    def __lt__(self, other):
        """Сравнение для сортировки по времени"""
        return self.time < other.time

    def __repr__(self):
        return f"Event({self.event_type.value}, t={self.time:.2f}, id={self.entity_id})"


class SimulationResults:
    """Результаты моделирования"""

    def __init__(self):
        self.rejected_clients = 0
        self.processed_clients = 0
        self.total_clients = 0
        self.queue_stats: Dict[int, Tuple[int, float]] = {}  # {queue_id: (max_size, avg_size)}

    @property
    def rejection_probability(self) -> float:
        """Вероятность отказа"""
        if self.total_clients == 0:
            return 0.0
        return self.rejected_clients / self.total_clients


def simulate_info_center(
    generator: ClientGenerator,
    operators: List[Operator],
    computers: List[Computer],
    num_clients: int
) -> SimulationResults:
    """
    Моделирование работы информационного центра

    Args:
        generator: Генератор клиентов
        operators: Список операторов
        computers: Список компьютеров
        num_clients: Количество клиентов для обработки (принятых + отклонённых)

    Returns:
        Результаты моделирования
    """
    results = SimulationResults()

    # Создаём очереди для каждого компьютера
    queues: Dict[int, Queue] = {comp.computer_id: Queue(comp.computer_id) for comp in computers}

    # Индексы для быстрого доступа
    operators_by_id = {op.operator_id: op for op in operators}
    computers_by_id = {comp.computer_id: comp for comp in computers}

    # Очередь событий (отсортированная по времени)
    events: List[Event] = []
    current_time = 0.0

    # Добавление события в очередь с сохранением сортировки
    def add_event(event: Event):
        events.append(event)
        events.sort()

    # Первое событие - прибытие первого клиента
    first_arrival_time = generator.generate_next_arrival_time(current_time)
    add_event(Event(EventType.CLIENT_ARRIVAL, first_arrival_time))

    # Основной цикл моделирования
    while results.total_clients < num_clients:
        if not events:
            break

        # Берём ближайшее событие
        event = events.pop(0)
        current_time = event.time

        # Фиксируем состояние очередей для статистики
        for queue in queues.values():
            queue.observe()

        # Обработка события прибытия клиента
        if event.event_type == EventType.CLIENT_ARRIVAL:
            results.total_clients += 1

            # Ищем свободного оператора с максимальной производительностью
            free_operators = [op for op in operators if not op.is_busy]

            if free_operators:
                # Сортируем по производительности (от большей к меньшей)
                best_operator = max(free_operators, key=lambda op: op.productivity)

                # Оператор начинает обработку
                finish_time = best_operator.start_processing(current_time)
                add_event(Event(EventType.OPERATOR_FINISH, finish_time, best_operator.operator_id))
            else:
                # Все операторы заняты - отказ
                results.rejected_clients += 1

            # Планируем прибытие следующего клиента (если не достигли лимита)
            if results.total_clients < num_clients:
                next_arrival_time = generator.generate_next_arrival_time(current_time)
                add_event(Event(EventType.CLIENT_ARRIVAL, next_arrival_time))

        # Обработка события окончания обработки оператором
        elif event.event_type == EventType.OPERATOR_FINISH:
            operator = operators_by_id[event.entity_id]
            operator.finish_processing()

            # Добавляем запрос в очередь к соответствующему компьютеру
            target_queue = queues[operator.target_computer_id]
            target_queue.add_request()

            # Проверяем, может ли компьютер начать обработку
            target_computer = computers_by_id[operator.target_computer_id]
            if not target_computer.is_busy and target_queue.size > 0:
                target_queue.remove_request()
                finish_time = target_computer.start_processing(current_time)
                add_event(Event(EventType.COMPUTER_FINISH, finish_time, target_computer.computer_id))

        # Обработка события окончания обработки компьютером
        elif event.event_type == EventType.COMPUTER_FINISH:
            computer = computers_by_id[event.entity_id]
            computer.finish_processing()
            results.processed_clients += 1

            # Проверяем, есть ли запросы в очереди
            computer_queue = queues[computer.computer_id]
            if computer_queue.size > 0:
                computer_queue.remove_request()
                finish_time = computer.start_processing(current_time)
                add_event(Event(EventType.COMPUTER_FINISH, finish_time, computer.computer_id))

    # Собираем статистику по очередям
    for queue in queues.values():
        results.queue_stats[queue.queue_id] = (queue.max_size, queue.average_size)

    return results
