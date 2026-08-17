"""
RTS Engine - ECS (Entity-Component-System) Core
Архитектурное решение: ECS паттерн для гибкой композиции игровых объектов
"""
from typing import Dict, List, Set, Any, Type
from dataclasses import dataclass, field


@dataclass
class Component:
    """Базовый класс для всех компонентов"""
    entity_id: int = field(default=0, init=False)


@dataclass
class PositionComponent(Component):
    """Компонент позиции в 2D пространстве"""
    x: float = 0.0
    y: float = 0.0
    
    def set(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def move(self, dx: float, dy: float):
        self.x += dx
        self.y += dy


@dataclass
class VelocityComponent(Component):
    """Компонент скорости для движения"""
    vx: float = 0.0
    vy: float = 0.0
    
    def set(self, vx: float, vy: float):
        self.vx = vx
        self.vy = vy


@dataclass
class RenderComponent(Component):
    """Компонент рендеринга (цвет, форма)"""
    color: tuple = field(default_factory=lambda: (255, 255, 255))
    shape: str = "square"  # square, circle
    size: int = 32


@dataclass
class SelectionComponent(Component):
    """Компонент выделения юнита"""
    selected: bool = False


@dataclass
class UnitComponent(Component):
    """Компонент, маркирующий сущность как юнит"""
    unit_type: str = "worker"
    health: int = 100
    max_health: int = 100


class Entity:
    """
    Сущность в ECS системе.
    Контейнер для компонентов, не содержит логики.
    """
    
    _next_id = 0
    
    def __init__(self):
        self.id = Entity._next_id
        Entity._next_id += 1
        self._components: Dict[Type[Component], Component] = {}
    
    def add_component(self, component: Component):
        """Добавление компонента к сущности"""
        component.entity_id = self.id
        self._components[type(component)] = component
        return self
    
    def get_component(self, component_type: Type[Component]) -> Component:
        """Получение компонента по типу"""
        return self._components.get(component_type)
    
    def has_component(self, component_type: Type[Component]) -> bool:
        """Проверка наличия компонента"""
        return component_type in self._components
    
    def remove_component(self, component_type: Type[Component]):
        """Удаление компонента"""
        if component_type in self._components:
            del self._components[component_type]
    
    @property
    def components(self) -> List[Component]:
        """Все компоненты сущности"""
        return list(self._components.values())


class EntityManager:
    """
    Менеджер сущностей.
    Управляет созданием, удалением и хранением сущностей.
    """
    
    def __init__(self):
        self._entities: Dict[int, Entity] = {}
        self._entities_by_components: Dict[Set[Type[Component]], List[Entity]] = {}
    
    def create_entity(self) -> Entity:
        """Создание новой сущности"""
        entity = Entity()
        self._entities[entity.id] = entity
        return entity
    
    def destroy_entity(self, entity_id: int):
        """Удаление сущности"""
        if entity_id in self._entities:
            del self._entities[entity_id]
            # Очистка из индексов по компонентам
            for comp_set in list(self._entities_by_components.keys()):
                self._entities_by_components[comp_set] = [
                    e for e in self._entities_by_components[comp_set] 
                    if e.id != entity_id
                ]
    
    def get_entity(self, entity_id: int) -> Entity:
        """Получение сущности по ID"""
        return self._entities.get(entity_id)
    
    def get_entities_with_components(self, *component_types: Type[Component]) -> List[Entity]:
        """
        Получение всех сущностей, имеющих указанные компоненты.
        Используется системами для обработки групп сущностей.
        """
        comp_set = frozenset(component_types)
        
        if comp_set not in self._entities_by_components:
            # Кэшируем результат запроса
            entities = []
            for entity in self._entities.values():
                if all(entity.has_component(ct) for ct in component_types):
                    entities.append(entity)
            self._entities_by_components[comp_set] = entities
        
        return self._entities_by_components[comp_set]
    
    def clear(self):
        """Очистка всех сущностей (для тестов/рестарта)"""
        self._entities.clear()
        self._entities_by_components.clear()
        Entity._next_id = 0
