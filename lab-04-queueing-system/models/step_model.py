# -*- coding: utf-8 -*-
"""
Реализация пошагового (Δt) подхода моделирования СМО
"""

from random import randint


def step_model(generator, processor, num_tasks: int, return_probability: int, time_step: float) -> int:
    """
    Моделирование СМО с использованием пошагового подхода (принцип Δt)
    
    Args:
        generator: Объект генератора (распределение для появления заявок)
        processor: Объект обслуживающего аппарата (распределение для обработки)
        num_tasks: Количество заявок для обработки
        return_probability: Вероятность возврата заявки в очередь (0-100)
        time_step: Шаг времени Δt
    
    Returns:
        Максимальная длина очереди
    """
    tasks_done = 0  # Количество обработанных заявок
    current_time = time_step  # Текущее модельное время
    
    # Время следующего появления заявки
    time_next_generated = generator.generate()
    time_prev_generated = 0  # Время предыдущей генерации
    
    # Время окончания обработки текущей заявки
    time_processing_done = 0
    
    current_queue_length = 0  # Текущая длина очереди
    max_queue_length = 0      # Максимальная длина очереди
    
    is_processor_free = True  # Флаг: свободен ли обслуживающий аппарат
    
    while tasks_done < num_tasks:
        # Проверяем генератор: появилась ли новая заявка?
        if current_time > time_next_generated:
            current_queue_length += 1
            
            if current_queue_length > max_queue_length:
                max_queue_length = current_queue_length
            
            time_prev_generated = time_next_generated
            time_next_generated += generator.generate()
        
        # Проверяем обработчик: закончилась ли обработка?
        if current_time > time_processing_done:
            if current_queue_length > 0:
                was_free = is_processor_free
                
                if is_processor_free:
                    # Процессор был свободен, начинаем обработку
                    is_processor_free = False
                else:
                    # Процессор закончил обработку
                    tasks_done += 1
                    current_queue_length -= 1
                    
                    # Проверка возврата заявки в очередь
                    if randint(1, 100) <= return_probability:
                        current_queue_length += 1
                
                # Вычисляем время окончания обработки
                if was_free:
                    time_processing_done = time_prev_generated + processor.generate()
                else:
                    time_processing_done += processor.generate()
            else:
                # Очередь пуста, процессор свободен
                is_processor_free = True
        
        # Продвигаем модельное время на шаг
        current_time += time_step
    
    return max_queue_length