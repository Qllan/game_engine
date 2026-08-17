"""
RTS Engine - Data Layer (Загрузка данных из JSON)
Архитектурное решение: Отделение данных от кода для поддержки модификаций
"""
import json
from typing import Dict, Any, List
from pathlib import Path


class DataManager:
    """
    Менеджер данных игры.
    Загружает конфигурации юнитов, зданий и других объектов из JSON файлов.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, Any] = {}
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Загрузка JSON файла с кэшированием"""
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._cache[filename] = data
        return data
    
    def get_unit_config(self, unit_type: str) -> Dict[str, Any]:
        """Получение конфигурации конкретного типа юнита"""
        units_data = self.load_json("units.json")
        return units_data.get(unit_type, {})
    
    def get_all_units(self) -> Dict[str, Any]:
        """Получение всех конфигураций юнитов"""
        return self.load_json("units.json")
    
    def clear_cache(self):
        """Очистка кэша (для горячей перезагрузки модов)"""
        self._cache.clear()


def create_sample_data_files(data_dir: str = "data"):
    """Создание примеров файлов данных для демонстрации"""
    import os
    os.makedirs(data_dir, exist_ok=True)
    
    # Пример конфигурации юнитов
    units_config = {
        "worker": {
            "name": "Рабочий",
            "health": 100,
            "speed": 50,
            "damage": 5,
            "cost": {
                "minerals": 50,
                "gas": 0
            },
            "build_time": 10,
            "render": {
                "color": [0, 255, 0],
                "shape": "square",
                "size": 20
            }
        },
        "soldier": {
            "name": "Солдат",
            "health": 150,
            "speed": 40,
            "damage": 15,
            "cost": {
                "minerals": 100,
                "gas": 25
            },
            "build_time": 20,
            "render": {
                "color": [255, 0, 0],
                "shape": "circle",
                "size": 25
            }
        },
        "tank": {
            "name": "Танк",
            "health": 300,
            "speed": 30,
            "damage": 40,
            "cost": {
                "minerals": 200,
                "gas": 100
            },
            "build_time": 45,
            "render": {
                "color": [0, 128, 255],
                "shape": "square",
                "size": 40
            }
        }
    }
    
    with open(os.path.join(data_dir, "units.json"), 'w', encoding='utf-8') as f:
        json.dump(units_config, f, indent=2, ensure_ascii=False)
    
    print(f"Created sample data files in {data_dir}/")
    return units_config
