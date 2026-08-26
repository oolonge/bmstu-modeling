# -*- coding: utf-8 -*-
"""
Реализация событийного подхода моделирования СМО
"""

from random import randint


def event_model(generator, processor, num_tasks: int, return_probability: int) -> int:
    """
    Моделирование СМО с использованием событийного подхода
    
    Args:
        generator: Объект генератора (распределение для появления заявок)
        processor: Объект обслуживающего аппарата (распределение для обработки)
        num_tasks: Количество заявок для обработки
        return_probability: Вероятность возврата заявки в очередь (0-100)
    
    Returns:
        Максимальная длина очереди
    """
    tasks_done = 0  # Количество обработанных заявок
    current_queue_length = 0  # Текущая длина очереди
    max_queue_length = 0      # Максимальная длина очереди
    
    is_processor_free = True  # Флаг: свободен ли обслуживающий аппарат
    should_process = False    # Флаг: нужно ли обработать заявку
    
    # Список будущих событий: [время, тип]
    # Тип события: "g" - генерация заявки, "p" - окончание обработки
    events = [[generator.generate(), "g"]]
    
    while tasks_done < num_tasks:
        # Берем ближайшее событие
        event = events.pop(0)
        event_time = event[0]
        event_type = event[1]
        
        # Обработка события генерации заявки
        if event_type == "g":
            current_queue_length += 1
            
            if current_queue_length > max_queue_length:
                max_queue_length = current_queue_length
            
            # Добавляем следующее событие генерации
            add_event(events, [event_time + generator.generate(), "g"])
            
            # Если процессор свободен, можно начать обработку
            if is_processor_free:
                should_process = True
        
        # Обработка события окончания обработки заявки
        elif event_type == "p":
            tasks_done += 1
            
            # Проверка возврата заявки в очередь
            if randint(1, 100) <= return_probability:
                current_queue_length += 1
            
            should_process = True
        
        # Если нужно начать обработку новой заявки
        if should_process:
            if current_queue_length > 0:
                # Берем заявку из очереди
                current_queue_length -= 1
                
                # Планируем событие окончания обработки
                add_event(events, [event_time + processor.generate(), "p"])
                
                is_processor_free = False
            else:
                # Очередь пуста, процессор освобождается
                is_processor_free = True
            
            should_process = False
    
    return max_queue_length


def add_event(events: list, new_event: list):
    """
    Добавление события в список будущих событий с сохранением сортировки по времени
    
    Args:
        events: Список событий
        new_event: Новое событие [время, тип]
    """
    i = 0
    # Ищем позицию для вставки (список отсортирован по времени)
    while i < len(events) and events[i][0] < new_event[0]:
        i += 1
    
    # Вставляем событие в нужную позицию
    if 0 < i < len(events):
        events.insert(i - 1, new_event)
    else:
        events.insert(i, new_event)