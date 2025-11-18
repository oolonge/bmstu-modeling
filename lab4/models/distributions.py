# -*- coding: utf-8 -*-
"""
Классы для генерации случайных величин по различным распределениям
Используются формулы из лекций (Таблица 9.1)
"""

from random import random
from math import log, sqrt


class UniformDistribution:
    """Равномерное распределение на интервале [a, b]"""
    
    def __init__(self, a: float, b: float):
        if a >= b:
            raise ValueError("Параметр 'a' должен быть меньше 'b'")
        self.a = a
        self.b = b
    
    def generate(self) -> float:
        """
        Генерация интервала времени по равномерному закону
        Формула: t_i = a + (b - a) * R
        """
        return self.a + (self.b - self.a) * random()


class ExponentialDistribution:
    """Экспоненциальное распределение с параметром λ"""
    
    def __init__(self, lambda_param: float):
        if lambda_param <= 0:
            raise ValueError("Параметр 'λ' должен быть положительным")
        self.lambda_param = lambda_param
    
    def generate(self) -> float:
        """
        Генерация интервала времени по экспоненциальному закону
        Формула: t_i = (1/λ) * ln(1 - R)
        Используем abs для избежания отрицательных значений
        """
        return -(1.0 / self.lambda_param) * log(1 - random())


class NormalDistribution:
    """Нормальное распределение с параметрами M (среднее) и σ (СКО)"""
    
    def __init__(self, m: float, sigma: float):
        if sigma <= 0:
            raise ValueError("Параметр 'σ' должен быть положительным")
        self.m = m
        self.sigma = sigma
    
    def generate(self) -> float:
        """
        Генерация интервала времени по нормальному закону
        Формула: t_i = σ * sqrt(12/n) * (Σ R_i - n/2) + M
        При n=12: t_i = σ * (Σ R_i - 6) + M
        """
        n = 12
        sum_random = sum(random() for _ in range(n))
        return self.sigma * sqrt(12.0 / n) * (sum_random - n / 2.0) + self.m


class ErlangDistribution:
    """Распределение Эрланга с параметрами k (форма) и λ (интенсивность)"""
    
    def __init__(self, k: int, lambda_param: float):
        if k <= 0 or k != int(k):
            raise ValueError("Параметр 'k' должен быть положительным целым числом")
        if lambda_param <= 0:
            raise ValueError("Параметр 'λ' должен быть положительным")
        self.k = int(k)
        self.lambda_param = lambda_param
    
    def generate(self) -> float:
        """
        Генерация интервала времени по распределению Эрланга
        Формула: t_i = -(1/(k*λ)) * Σ ln(1 - R_i)
        """
        sum_log = sum(log(1 - random()) for _ in range(self.k))
        return -(1.0 / (self.k * self.lambda_param)) * sum_log


# Словарь для маппинга названий распределений на классы
DISTRIBUTION_CLASSES = {
    'Равномерное': UniformDistribution,
    'Экспоненциальное': ExponentialDistribution,
    'Нормальное': NormalDistribution,
    'Эрланга': ErlangDistribution
}


def create_distribution(dist_name: str, params: dict):
    """
    Фабричная функция для создания объекта распределения
    
    Args:
        dist_name: Название распределения
        params: Словарь с параметрами
    
    Returns:
        Объект распределения
    """
    if dist_name not in DISTRIBUTION_CLASSES:
        raise ValueError(f"Неизвестное распределение: {dist_name}")
    
    dist_class = DISTRIBUTION_CLASSES[dist_name]
    
    if dist_name == 'Равномерное':
        return dist_class(params['a'], params['b'])
    elif dist_name == 'Экспоненциальное':
        return dist_class(params['λ'])
    elif dist_name == 'Нормальное':
        return dist_class(params['μ'], params['σ'])
    elif dist_name == 'Эрланга':
        return dist_class(params['k'], params['λ'])