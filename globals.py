BLOCKS_DATA = {
    'earth': [0.8, 'grass', 16],
    'grass': [0.8, 'grass', 16],
    'stone': [4, 'stone', 8],
    'stone2': [4, 'stone', 8],
    'coal': [6, 'stone', 6.5],
    'iron': [12, 'stone', 5],
    'gold': [18, 'stone', 3],
    'diamonds': [25, 'stone', 2],
    'wood': [3, 'wood', 10],
    'flowers': [0.5, 'grass', 21],
    'foliage': [0.2, 'grass2', 25],
    'wooden_planks': [3.5, 'wood', 9],
    'oven': [4, 'stone', 8],
    'oven2': [4, 'stone', 8],
    'stone_bricks': [4, 'stone', 8],
    'glass': [0.2, 'stone', 25],
    'torch': [0.1, 'wood', 25]

}

# Рецепты крафта (матрица 3x3)
CRAFTING_RECIPES = {
    # Верстак
    "workbench": {
        "pattern": [
            ["wood", "wood", None],
            ["wood", "wood", None],
            [None, None, None]
        ],
        "result": "workbench",
        "result_count": 1
    },
    # Деревянные доски
    "wooden_planks": {
        "pattern": [
            ["wood", None, None],
            [None, None, None],
            [None, None, None]
        ],
        "result": "wooden_planks",
        "result_count": 4
    },
    # Палки
    "sticks": {
        "pattern": [
            [None, "wooden_planks", None],
            [None, "wooden_planks", None],
            [None, None, None]
        ],
        "result": "sticks",
        "result_count": 4
    },
    # Факелы
    "torch": {
        "pattern": [
            [None, "coal2", None],
            [None, "sticks", None],
            [None, None, None]
        ],
        "result": "torch",
        "result_count": 4
    },
    # Деревянный меч
    "wooden_sword": {
        "pattern": [
            [None, "wooden_planks", None],
            [None, "wooden_planks", None],
            [None, "sticks", None]
        ],
        "result": "wooden_sword",
        "result_count": 1
    },
    # Каменный меч
    "stone_sword": {
        "pattern": [
            [None, "stone2", None],
            [None, "stone2", None],
            [None, "sticks", None]
        ],
        "result": "stone_sword",
        "result_count": 1
    },
    # Печка
    "oven": {
        "pattern": [
            ["stone2", "stone2", "stone2"],
            ["stone2", None, "stone2"],
            ["stone2", "stone2", "stone2"]
        ],
        "result": "oven",
        "result_count": 1
    },
    # Красивый камень
    "stone_bricks": {
        "pattern": [
            ["stone2", "stone2", None],
            ["stone2", "stone2", None],
            [None, None, None]
        ],
        "result": "stone_bricks",
        "result_count": 4
    },
    # Железный меч
    "iron_sword": {
        "pattern": [
            [None, "iron_ingot", None],
            [None, "iron_ingot", None],
            [None, "sticks", None]
        ],
        "result": "iron_sword",
        "result_count": 1
    },
    # Золотой меч
    "golden_sword": {
        "pattern": [
            [None, "golden_ingot", None],
            [None, "golden_ingot", None],
            [None, "sticks", None]
        ],
        "result": "golden_sword",
        "result_count": 1
    },
    # Алмазный меч
    "diamond_sword": {
        "pattern": [
            [None, "diamonds2", None],
            [None, "diamonds2", None],
            [None, "sticks", None]
        ],
        "result": "diamond_sword",
        "result_count": 1
    },

    # Деревянный топор
    "wooden_axe": {
        "pattern": [
            ['wooden_planks', "wooden_planks", None],
            ['wooden_planks', "sticks", None],
            [None, "sticks", None]
        ],
        "result": "wooden_axe",
        "result_count": 1
    },
    # Каменный топор
    "stone_axe": {
        "pattern": [
            ['stone2', "stone2", None],
            ['stone2', "sticks", None],
            [None, "sticks", None]
        ],
        "result": "stone_axe",
        "result_count": 1
    },
    # Железный топор
    "iron_axe": {
        "pattern": [
            ['iron_ingot', "iron_ingot", None],
            ['iron_ingot', "sticks", None],
            [None, "sticks", None]
        ],
        "result": "iron_axe",
        "result_count": 1
    },
    # Золотой топор
    "golden_axe": {
        "pattern": [
            ['golden_ingot', "golden_ingot", None],
            ['golden_ingot', "sticks", None],
            [None, "sticks", None]
        ],
        "result": "golden_axe",
        "result_count": 1
    },
    # Алмазный топор
    "diamond_axe": {
        "pattern": [
            ['diamonds2', "diamonds2", None],
            ['diamonds2', "sticks", None],
            [None, "sticks", None]
        ],
        "result": "diamond_axe",
        "result_count": 1
    },

    # Деревянная кирка
    "wooden_pickaxe": {
        "pattern": [
            ['wooden_planks', "wooden_planks", 'wooden_planks'],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "wooden_pickaxe",
        "result_count": 1
    },
    # Каменная кирка
    "stone_pickaxe": {
        "pattern": [
            ['stone2', "stone2", 'stone2'],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "stone_pickaxe",
        "result_count": 1
    },
    # Железная кирка
    "iron_pickaxe": {
        "pattern": [
            ['iron_ingot', "iron_ingot", 'iron_ingot'],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "iron_pickaxe",
        "result_count": 1
    },
    # Золотая кирка
    "golden_pickaxe": {
        "pattern": [
            ['golden_ingot', "golden_ingot", 'golden_ingot'],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "golden_pickaxe",
        "result_count": 1
    },
    # Алмазная кирка
    "diamond_pickaxe": {
        "pattern": [
            ['diamonds2', "diamonds2", 'diamonds2'],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "diamond_pickaxe",
        "result_count": 1
    },

    # Деревянная лопата
    "wooden_shovel": {
        "pattern": [
            [None, "wooden_planks", None],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "wooden_shovel",
        "result_count": 1
    },
    # Каменная лопата
    "stone_shovel": {
        "pattern": [
            [None, "stone2", None],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "stone_shovel",
        "result_count": 1
    },
    # Железная лопата
    "iron_shovel": {
        "pattern": [
            [None, "iron_ingot", None],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "iron_shovel",
        "result_count": 1
    },
    # Золотая лопата
    "golden_shovel": {
        "pattern": [
            [None, "golden_ingot", None],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "golden_shovel",
        "result_count": 1
    },
    # Алмазная лопата
    "diamond_shovel": {
        "pattern": [
            [None, "diamonds2", None],
            [None, "sticks", None],
            [None, "sticks", None]
        ],
        "result": "diamond_shovel",
        "result_count": 1
    },

    # Слиток железа
    "iron_ingot": {
        "pattern": [
            ["iron2", None, None],
            ["coal2", None, None],
            [None, None, None]
        ],
        "result": "iron_ingot",
        "result_count": 1
    },

    # Слиток золота
    "golden_ingot": {
        "pattern": [
            ["gold2", None, None],
            ["coal2", None, None],
            [None, None, None]
        ],
        "result": "golden_ingot",
        "result_count": 1
    }
}

WEAPON = {
    "wooden_sword": {
        "damage": 1.5,
        "object": ["monster"]
    },
    "stone_sword": {
        "damage": 2,
        "object": ["monster"]
    },
    "iron_sword": {
        "damage": 2.5,
        "object": ["monster"]
    },
    "golden_sword": {
        "damage": 3,
        "object": ["monster"]
    },
    "diamond_sword": {
        "damage": 3.5,
        "object": ["monster"]
    },
    "wooden_axe": {
        "damage": 1.5,
        "object": ["wood", "wooden_planks"]
    },
    "stone_axe": {
        "damage": 2,
        "object": ["wood", "wooden_planks"]
    },
    "iron_axe": {
        "damage": 3,
        "object": ["wood", "wooden_planks"]
    },
    "golden_axe": {
        "damage": 4,
        "object": ["wood", "wooden_planks"]
    },
    "diamond_axe": {
        "damage": 6,
        "object": ["wood", "wooden_planks"]
    },
    "wooden_pickaxe": {
        "damage": 1.5,
        "object": ["stone", "coal", "oven", "oven2", "stone_bricks"]
    },
    "stone_pickaxe": {
        "damage": 2,
        "object": ["stone", "coal", "iron", "oven", "oven2", "stone_bricks"]
    },
    "iron_pickaxe": {
        "damage": 3,
        "object": ["stone", "coal", "iron", "gold", "diamonds", "oven", "oven2", "stone_bricks"]
    },
    "golden_pickaxe": {
        "damage": 4,
        "object": ["stone", "coal", "iron", "gold", "diamonds", "oven", "oven2", "stone_bricks"]
    },
    "diamond_pickaxe": {
        "damage": 6,
        "object": ["stone", "coal", "iron", "gold", "diamonds", "oven", "oven2", "stone_bricks"]
    },

    "wooden_shovel": {
        "damage": 1.5,
        "object": ["earth", 'grass']
    },
    "stone_shovel": {
        "damage": 2,
        "object": ["earth", 'grass']
    },
    "iron_shovel": {
        "damage": 3,
        "object": ["earth", 'grass']
    },
    "golden_shovel": {
        "damage": 4,
        "object": ["earth", 'grass']
    },
    "diamond_shovel": {
        "damage": 6,
        "object": ["earth", 'grass']
    }

}
