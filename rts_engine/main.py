"""
RTS Engine - Main Game Loop and Integration
Архитектурное решение: Интеграция всех систем в единый игровой цикл
"""
import sys
import os

# Добавляем корень проекта в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import EventBus, UnitCreatedEvent, GameTickEvent
from ecs.core import EntityManager, PositionComponent, VelocityComponent, RenderComponent, SelectionComponent, UnitComponent
from ecs.systems import MovementSystem, RenderSystem, SelectionSystem
from data.manager import DataManager, create_sample_data_files


class RTSGame:
    """
    Главный класс игры.
    Координирует работу всех систем и управляет игровым циклом.
    """
    
    def __init__(self):
        # Инициализация основных систем
        self.event_bus = EventBus()
        self.entity_manager = EntityManager()
        self.data_manager = DataManager()
        
        # Создание систем
        self.movement_system = MovementSystem(self.entity_manager, self.event_bus)
        self.render_system = RenderSystem(self.entity_manager, self.event_bus)
        self.selection_system = SelectionSystem(self.entity_manager, self.event_bus)
        
        # Игровые параметры
        self.running = False
        self.delta_time = 0.0
        
        # Подписка на события
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Настройка обработчиков событий"""
        def on_unit_created(event):
            print(f"Юнит создан: ID={event.data.get('entity_id')}, Type={event.data.get('unit_type')}")
        
        self.event_bus.subscribe("unit_created", on_unit_created)
    
    def create_unit(self, unit_type: str, x: float, y: float):
        """
        Создание юнита на основе данных из JSON конфигурации.
        Демонстрирует подход "данные отдельно от кода".
        """
        try:
            config = self.data_manager.get_unit_config(unit_type)
            if not config:
                print(f"Неизвестный тип юнита: {unit_type}")
                return None
            
            # Создаем сущность с компонентами
            entity = self.entity_manager.create_entity()
            
            # Позиция
            entity.add_component(PositionComponent(x, y))
            
            # Скорость (из конфига)
            speed = config.get("speed", 50)
            entity.add_component(VelocityComponent(0, 0))
            
            # Рендер (из конфига)
            render_config = config.get("render", {})
            color = tuple(render_config.get("color", [255, 255, 255]))
            shape = render_config.get("shape", "square")
            size = render_config.get("size", 32)
            entity.add_component(RenderComponent(color=color, shape=shape, size=size))
            
            # Выделение
            entity.add_component(SelectionComponent())
            
            # Маркер юнита
            entity.add_component(UnitComponent(
                unit_type=unit_type,
                health=config.get("health", 100)
            ))
            
            # Публикуем событие создания
            self.event_bus.publish("unit_created", UnitCreatedEvent({
                "entity_id": entity.id,
                "unit_type": unit_type
            }))
            
            return entity
            
        except Exception as e:
            print(f"Ошибка создания юнита: {e}")
            return None
    
    def update(self, delta_time: float):
        """Обновление всех систем"""
        self.delta_time = delta_time
        
        # Обновляем системы в определенном порядке
        self.movement_system.update(delta_time)
        self.render_system.update(delta_time)
        
        # Публикуем событие игрового тика
        self.event_bus.publish("game_tick", GameTickEvent({
            "delta_time": delta_time
        }))
    
    def render(self):
        """Отрисовка текущего состояния (в консоль для прототипа)"""
        render_data = self.render_system.get_render_data()
        
        if not render_data:
            return
        
        print("\n=== RENDER FRAME ===")
        for obj in render_data:
            marker = "*" if obj["selected"] else " "
            print(f"[{marker}] Entity {obj['entity_id']}: {obj['shape']} at ({obj['x']:.1f}, {obj['y']:.1f}) color={obj['color']}")
    
    def run_demo(self, num_ticks: int = 5):
        """
        Демо-запуск игры без графики.
        Симулирует несколько игровых тиков.
        """
        print("=" * 50)
        print("RTS ENGINE DEMO - Iteration 1")
        print("=" * 50)
        
        # Создаем тестовые данные
        create_sample_data_files("data")
        
        # Создаем несколько юнитов
        print("\n>>> Создаем юнитов...")
        worker = self.create_unit("worker", 100, 100)
        soldier = self.create_unit("soldier", 200, 150)
        tank = self.create_unit("tank", 300, 200)
        
        # Задаем скорость рабочему
        if worker:
            worker.get_component(VelocityComponent).set(10, 5)
        
        # Выделяем солдата
        if soldier:
            self.selection_system.select_unit(soldier.id)
        
        # Игровой цикл
        print("\n>>> Запуск игрового цикла...")
        self.running = True
        
        for tick in range(num_ticks):
            print(f"\n--- TICK {tick + 1} ---")
            
            # Обновление
            self.update(0.016)  # ~60 FPS
            
            # Отрисовка
            self.render()
        
        # Демонстрация выделения по области
        print("\n>>> Тест выделения по области...")
        self.selection_system.select_in_rect(150, 100, 350, 250)
        self.render()
        
        print("\n>>> Демо завершено!")
        self.running = False


def main():
    """Точка входа"""
    game = RTSGame()
    game.run_demo(num_ticks=3)


if __name__ == "__main__":
    main()
