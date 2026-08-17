"""
RTS Engine - Systems (Логика обработки сущностей)
Архитектурное решение: Системы обрабатывают логику, компоненты хранят данные
"""
from typing import List
from ecs.core import (
    EntityManager, Entity, 
    PositionComponent, VelocityComponent, 
    RenderComponent, SelectionComponent, UnitComponent
)
from core.event_bus import EventBus, GameTickEvent, UnitMovedEvent


class BaseSystem:
    """Базовый класс для всех систем"""
    
    def __init__(self, entity_manager: EntityManager, event_bus: EventBus):
        self.entity_manager = entity_manager
        self.event_bus = event_bus
    
    def update(self, delta_time: float):
        """Обновление системы каждый кадр"""
        pass


class MovementSystem(BaseSystem):
    """
    Система движения.
    Обрабатывает все сущности с Position и Velocity компонентами.
    """
    
    def update(self, delta_time: float):
        entities = self.entity_manager.get_entities_with_components(
            PositionComponent, VelocityComponent
        )
        
        for entity in entities:
            pos = entity.get_component(PositionComponent)
            vel = entity.get_component(VelocityComponent)
            
            # Применяем скорость к позиции
            pos.move(vel.vx * delta_time, vel.vy * delta_time)
            
            # Публикуем событие перемещения
            self.event_bus.publish("unit_moved", UnitMovedEvent({
                "entity_id": entity.id,
                "x": pos.x,
                "y": pos.y
            }))


class RenderSystem(BaseSystem):
    """
    Система рендеринга.
    Собирает данные о всех отображаемых объектах для отрисовки.
    В прототипе просто выводит информацию в консоль.
    """
    
    def __init__(self, entity_manager: EntityManager, event_bus: EventBus):
        super().__init__(entity_manager, event_bus)
        self.render_data = []
    
    def update(self, delta_time: float):
        self.render_data = []
        
        entities = self.entity_manager.get_entities_with_components(
            PositionComponent, RenderComponent
        )
        
        for entity in entities:
            pos = entity.get_component(PositionComponent)
            render = entity.get_component(RenderComponent)
            selection = entity.get_component(SelectionComponent)
            
            self.render_data.append({
                "entity_id": entity.id,
                "x": pos.x,
                "y": pos.y,
                "color": render.color,
                "shape": render.shape,
                "size": render.size,
                "selected": selection.selected if selection else False
            })
    
    def get_render_data(self) -> List[dict]:
        """Возвращает данные для отрисовки"""
        return self.render_data


class SelectionSystem(BaseSystem):
    """
    Система выделения юнитов.
    Обрабатывает клики и выделение групп юнитов.
    """
    
    def select_unit(self, entity_id: int):
        """Выделить конкретный юнит"""
        entity = self.entity_manager.get_entity(entity_id)
        if entity and entity.has_component(SelectionComponent):
            # Снимаем выделение со всех
            self.deselect_all()
            # Выделяем нужный
            entity.get_component(SelectionComponent).selected = True
    
    def deselect_all(self):
        """Снять выделение со всех юнитов"""
        entities = self.entity_manager.get_entities_with_components(
            SelectionComponent
        )
        for entity in entities:
            entity.get_component(SelectionComponent).selected = False
    
    def select_in_rect(self, x1: float, y1: float, x2: float, y2: float):
        """Выделить все юниты в прямоугольной области"""
        entities = self.entity_manager.get_entities_with_components(
            PositionComponent, SelectionComponent
        )
        
        # Нормализуем координаты
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        for entity in entities:
            pos = entity.get_component(PositionComponent)
            if min_x <= pos.x <= max_x and min_y <= pos.y <= max_y:
                entity.get_component(SelectionComponent).selected = True
