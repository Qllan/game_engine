"""
RTS Engine - Core Event Bus System
Архитектурное решение: Event Bus для слабой связности между компонентами
"""
from collections import defaultdict
from typing import Callable, Dict, List, Any


class Event:
    """Базовый класс для всех событий в движке"""
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}


class EventBus:
    """
    Система событий для декуплинга компонентов.
    Позволяет объектам общаться без прямых ссылок друг на друга.
    Критично для будущей сетевой архитектуры и модификаций.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners: Dict[str, List[Callable]] = defaultdict(list)
        return cls._instance
    
    def subscribe(self, event_type: str, callback: Callable):
        """Подписка на событие определенного типа"""
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписка от события"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
    
    def publish(self, event_type: str, event: Event = None):
        """Публикация события всем подписчикам"""
        if event is None:
            event = Event()
        
        for callback in self._listeners.get(event_type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def clear(self):
        """Очистка всех подписчиков (для тестов)"""
        self._listeners.clear()


# Предопределенные типы событий для RTS
class UnitCreatedEvent(Event):
    """Событие создания юнита"""
    pass


class UnitMovedEvent(Event):
    """Событие перемещения юнита"""
    pass


class GameTickEvent(Event):
    """Событие каждого кадра игры"""
    pass
