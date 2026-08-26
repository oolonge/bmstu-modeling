# -*- coding: utf-8 -*-
"""
Элементы системы массового обслуживания: генератор, операторы, компьютеры, очереди
"""

from typing import Optional
from .distributions import UniformDistribution


class ClientGenerator:
    """Генератор клиентов (заявок)"""

    def __init__(self, distribution: UniformDistribution):
        """
        Args:
            distribution: Распределение для времени между прибытиями клиентов
        """
        self.distribution = distribution

    def generate_next_arrival_time(self, current_time: float) -> float:
        """
        Генерация времени прибытия следующего клиента

        Args:
            current_time: Текущее время моделирования

        Returns:
            Время прибытия следующего клиента
        """
        return current_time + self.distribution.generate()


class Operator:
    """Оператор информационного центра"""

    def __init__(self, operator_id: int, distribution: UniformDistribution, target_computer_id: int):
        """
        Args:
            operator_id: Идентификатор оператора
            distribution: Распределение для времени обработки запроса
            target_computer_id: ID компьютера, на который оператор отправляет заявки
        """
        self.operator_id = operator_id
        self.distribution = distribution
        self.target_computer_id = target_computer_id
        self.is_busy = False
        self.finish_time = 0.0

    @property
    def productivity(self) -> float:
        """
        Производительность оператора (количество заявок в единицу времени)
        Чем меньше среднее время обработки, тем выше производительность
        """
        return 1.0 / self.distribution.mean

    def start_processing(self, current_time: float) -> float:
        """
        Начать обработку клиента

        Args:
            current_time: Текущее время

        Returns:
            Время окончания обработки
        """
        self.is_busy = True
        processing_time = self.distribution.generate()
        self.finish_time = current_time + processing_time
        return self.finish_time

    def finish_processing(self):
        """Завершить обработку клиента"""
        self.is_busy = False
        self.finish_time = 0.0


class Computer:
    """Компьютер для обработки запросов"""

    def __init__(self, computer_id: int, processing_time: float):
        """
        Args:
            computer_id: Идентификатор компьютера
            processing_time: Детерминированное время обработки запроса
        """
        self.computer_id = computer_id
        self.processing_time = processing_time
        self.is_busy = False
        self.finish_time = 0.0

    def start_processing(self, current_time: float) -> float:
        """
        Начать обработку запроса

        Args:
            current_time: Текущее время

        Returns:
            Время окончания обработки
        """
        self.is_busy = True
        self.finish_time = current_time + self.processing_time
        return self.finish_time

    def finish_processing(self):
        """Завершить обработку запроса"""
        self.is_busy = False
        self.finish_time = 0.0


class Queue:
    """Очередь (накопитель) для запросов"""

    def __init__(self, queue_id: int):
        """
        Args:
            queue_id: Идентификатор очереди (соответствует ID компьютера)
        """
        self.queue_id = queue_id
        self.size = 0
        self.max_size = 0
        self.total_size_observations = 0
        self.observation_count = 0

    def add_request(self):
        """Добавить запрос в очередь"""
        self.size += 1
        if self.size > self.max_size:
            self.max_size = self.size

    def remove_request(self):
        """Удалить запрос из очереди"""
        if self.size > 0:
            self.size -= 1

    def observe(self):
        """Зафиксировать текущий размер очереди для расчёта среднего"""
        self.total_size_observations += self.size
        self.observation_count += 1

    @property
    def average_size(self) -> float:
        """Средний размер очереди"""
        if self.observation_count == 0:
            return 0.0
        return self.total_size_observations / self.observation_count
