# -*- coding: utf-8 -*-
"""
Классы для генерации случайных величин по равномерному распределению
"""

from random import random


class UniformDistribution:
    """Равномерное распределение на интервале [a, b]"""

    def __init__(self, a: float, b: float):
        """
        Args:
            a: Нижняя граница интервала
            b: Верхняя граница интервала
        """
        if a >= b:
            raise ValueError("Параметр 'a' должен быть меньше 'b'")
        self.a = a
        self.b = b

    def generate(self) -> float:
        """
        Генерация интервала времени по равномерному закону
        Формула: t_i = a + (b - a) * R

        Returns:
            Случайное значение из интервала [a, b]
        """
        return self.a + (self.b - self.a) * random()

    @property
    def mean(self) -> float:
        """Математическое ожидание (среднее значение)"""
        return (self.a + self.b) / 2.0

    @staticmethod
    def from_mean_and_deviation(mean: float, deviation: float) -> 'UniformDistribution':
        """
        Создание распределения из среднего значения и отклонения

        Args:
            mean: Среднее значение (μ)
            deviation: Отклонение (δ)

        Returns:
            Объект UniformDistribution для интервала [μ-δ, μ+δ]
        """
        return UniformDistribution(mean - deviation, mean + deviation)
