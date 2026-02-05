import arcade
import math
import enum
import time
import pyglet
import json
import os
from typing import Dict, List, Any, Optional
from arcade import Text
from arcade.gui import (UIManager, UIAnchorLayout, UIBoxLayout,
                        UITextureButton, UILabel, UIDropdown, UISlider)
from globals import BLOCKS_DATA, CRAFTING_RECIPES, WEAPON



SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Minecraft"
TILE_SCALING = 0.4

CAMERA_LERP = 0.12

GRAVITY = 1

# Размеры блоков
BLOCK_SIZE = 40
HOTBAR_SLOTS = 10
HOTBAR_HEIGHT = 100

# Цвета
SELECTED_COLOR = (192, 192, 192, 255)
HOTBAR_COLOR = (64, 64, 64, 100)
SLOT_BG_COLOR = (64, 64, 64, 130)
SLOT_BORDER_COLOR = (100, 100, 100, 255)
CRAFTING_BG_COLOR = (40, 40, 40, 220)
CRAFTING_SLOT_COLOR = (70, 70, 70, 200)
CRAFTING_RESULT_COLOR = (80, 80, 100, 200)
CRAFTING_TEXT_COLOR = (220, 220, 220, 255)

# Константы крафта
CRAFTING_GRID_SIZE = 3
CRAFTING_SLOT_SIZE = 50
CRAFTING_RESULT_SIZE = 60
CRAFTING_WINDOW_WIDTH = 400
CRAFTING_WINDOW_HEIGHT = 350


class Side(enum.Enum):
    LEFT = 0
    RIGHT = 1


class InventorySlot:
    """Слот инвентаря"""

    def __init__(self, x: float, y: float, size: int = BLOCK_SIZE, is_crafting_slot=False):
        self.x = x
        self.y = y
        self.size = size
        self.block_name = None
        self.selected = False
        self.count = 0
        self.width, self.height = self.size + 10, self.size + 10
        self.texture = None
        self.is_crafting_slot = is_crafting_slot

        self.score_text = arcade.Text(
            text="0",
            x=self.x + self.size // 2 - 4,
            y=self.y - self.size // 2 + 6,
            color=arcade.color.WHITE,
            font_size=14)

    def update_score(self):
        """Обновляем текст при изменении счета"""
        self.score_text.text = f"{self.count}"

    def update_texture(self):
        """Обновляем текстуру при изменении блока"""
        if self.block_name:
            texture_path = f'minecraft_blocks/{self.block_name}.webp'
            self.texture = arcade.load_texture(texture_path)
        else:
            self.texture = None

    def draw(self):
        """Отрисовка слота"""
        # Фон слота
        slot_color = CRAFTING_SLOT_COLOR if self.is_crafting_slot else SLOT_BG_COLOR
        arcade.draw_lbwh_rectangle_filled(self.x, self.y, self.width, self.height, slot_color)

        # Граница
        if self.is_crafting_slot:
            border_color = arcade.color.YELLOW if self.selected else SLOT_BORDER_COLOR
        else:
            border_color = SELECTED_COLOR if self.selected else SLOT_BORDER_COLOR

        border_width = 5 if self.selected else 3
        arcade.draw_lbwh_rectangle_outline(self.x, self.y, self.width, self.height, border_color, border_width)

        # Блок внутри слота
        if self.block_name and self.texture:
            block_size = self.size - 5
            # Рисуем текстуру напрямую
            arcade.draw_texture_rect(
                self.texture,
                arcade.LBWH(self.x + self.width / 7, self.y + self.height / 7,
                            block_size, block_size))

            # Счетчик
            if self.count > 1 or self.is_crafting_slot:
                self.score_text.draw()


class CraftingWindow:
    """Окно крафта"""

    def __init__(self, inventory_system):
        self.inventory = inventory_system
        self.is_visible = False
        self.grid_slots = []
        self.result_slot = None
        self.current_recipe = None
        self.setup_crafting_slots()

    def setup_crafting_slots(self):
        """Настройка слотов крафта"""
        # Позиция окна крафта
        window_x = SCREEN_WIDTH // 2 - CRAFTING_WINDOW_WIDTH // 2
        window_y = SCREEN_HEIGHT // 2 - CRAFTING_WINDOW_HEIGHT // 2

        # Позиция сетки 3x3
        grid_start_x = window_x + 50
        grid_start_y = window_y + CRAFTING_WINDOW_HEIGHT - 150

        # Создаем слоты для сетки крафта
        for row in range(CRAFTING_GRID_SIZE):
            for col in range(CRAFTING_GRID_SIZE):
                x = grid_start_x + col * (CRAFTING_SLOT_SIZE + 10)
                y = grid_start_y - row * (CRAFTING_SLOT_SIZE + 10)
                slot = InventorySlot(x, y, CRAFTING_SLOT_SIZE, is_crafting_slot=True)
                self.grid_slots.append(slot)

        # Создаем слот для результата
        result_x = window_x + CRAFTING_WINDOW_WIDTH - 100
        result_y = window_y + CRAFTING_WINDOW_HEIGHT // 2 - 35
        self.result_slot = InventorySlot(result_x, result_y, CRAFTING_RESULT_SIZE, is_crafting_slot=True)

    def toggle_visibility(self):
        """Переключение видимости окна крафта"""
        self.is_visible = not self.is_visible
        if not self.is_visible:
            # При закрытии возвращаем предметы из сетки крафта в инвентарь
            self.return_items_to_inventory()

    def return_items_to_inventory(self):
        """Возврат предметов из сетки крафта в инвентарь"""
        for slot in self.grid_slots:
            if slot.block_name and slot.count > 0:
                for _ in range(slot.count):
                    self.inventory.add_block(slot.block_name)
                slot.block_name = None
                slot.count = 0
                slot.update_score()
                slot.update_texture()

        self.result_slot.block_name = None
        self.result_slot.count = 0
        self.result_slot.update_score()
        self.result_slot.update_texture()
        self.current_recipe = None

    def add_to_crafting_grid(self, block_name, slot_index):
        """Добавление предмета в сетку крафта"""
        if 0 <= slot_index < len(self.grid_slots):
            slot = self.grid_slots[slot_index]
            if slot.block_name is None:
                slot.block_name = block_name
                slot.count = 1
            elif slot.block_name == block_name:
                slot.count += 1
            else:
                return False

            slot.update_score()
            slot.update_texture()
            self.check_recipes()
            return True
        return False

    def remove_from_crafting_grid(self, slot_index):
        """Удаление предмета из сетки крафта"""
        if 0 <= slot_index < len(self.grid_slots):
            slot = self.grid_slots[slot_index]
            if slot.block_name and slot.count > 0:
                slot.count -= 1
                slot.update_score()

                if slot.count == 0:
                    self.inventory.add_block(slot.block_name)
                    slot.block_name = None
                    slot.update_texture()

                self.check_recipes()
                return True
        return False

    def check_recipes(self):
        """Проверка рецептов крафта"""
        # Создаем матрицу текущего крафта
        crafting_matrix = []
        for i in range(CRAFTING_GRID_SIZE):
            row = []
            for j in range(CRAFTING_GRID_SIZE):
                slot = self.grid_slots[i * CRAFTING_GRID_SIZE + j]
                row.append(slot.block_name if slot.block_name and slot.count > 0 else None)
            crafting_matrix.append(row)

        # Проверяем все рецепты
        self.current_recipe = None
        self.result_slot.block_name = None
        self.result_slot.count = 0

        for recipe_name, recipe in CRAFTING_RECIPES.items():
            if self.matches_recipe(crafting_matrix, recipe["pattern"]):
                self.current_recipe = recipe_name
                self.result_slot.block_name = recipe["result"]
                self.result_slot.count = recipe["result_count"]
                self.result_slot.update_score()
                self.result_slot.update_texture()
                break

        if not self.current_recipe:
            self.result_slot.update_score()
            self.result_slot.update_texture()

    def matches_recipe(self, crafting_matrix, recipe_pattern):
        """Проверяет, соответствует ли матрица рецепту"""
        for i in range(CRAFTING_GRID_SIZE):
            for j in range(CRAFTING_GRID_SIZE):
                if crafting_matrix[i][j] != recipe_pattern[i][j]:
                    return False
        return True

    def craft_item(self):
        """Создание предмета по рецепту"""
        if not self.current_recipe or not self.result_slot.block_name:
            return False

        recipe = CRAFTING_RECIPES[self.current_recipe]

        # Проверяем, есть ли место в инвентаре для результата
        if not self.inventory.has_space_for(recipe["result"]):
            return False

        # Убираем предметы из сетки крафта
        for slot in self.grid_slots:
            if slot.block_name and slot.count > 0:
                slot.count -= 1
                slot.update_score()
                if slot.count == 0:
                    slot.block_name = None
                    slot.update_texture()

        # Добавляем результат в инвентарь
        for _ in range(recipe["result_count"]):
            self.inventory.add_block(recipe["result"])

        # Проверяем рецепты снова
        self.check_recipes()
        return True

    def draw(self):
        """Отрисовка окна крафта"""
        if not self.is_visible:
            return

        window_x = SCREEN_WIDTH // 2 - CRAFTING_WINDOW_WIDTH // 2
        window_y = SCREEN_HEIGHT // 2 - CRAFTING_WINDOW_HEIGHT // 2

        # Заголовок
        title_text = Text(
            text="Крафт",
            x=SCREEN_WIDTH // 2,
            y=window_y + CRAFTING_WINDOW_HEIGHT - 30,
            color=arcade.color.WHITE,
            font_size=24,
            anchor_x="center"
        )
        title_text.draw()

        # Текст сетки
        grid_text = Text(
            text="Сетка крафта:",
            x=window_x + 50,
            y=window_y + CRAFTING_WINDOW_HEIGHT - 80,
            color=arcade.color.WHITE,
            font_size=16
        )
        grid_text.draw()

        # Текст результата
        result_text = Text(
            text="Результат:",
            x=window_x + CRAFTING_WINDOW_WIDTH - 110,
            y=window_y + CRAFTING_WINDOW_HEIGHT // 2 + 55,
            color=arcade.color.WHITE,
            font_size=16
        )
        result_text.draw()

        # Отрисовка сетки крафта
        for slot in self.grid_slots:
            slot.draw()

        # Отрисовка слота результата
        if self.result_slot:
            # Фон для слота результата
            result_bg_x = self.result_slot.x - 10
            result_bg_y = self.result_slot.y - 10
            result_bg_width = self.result_slot.width + 20
            result_bg_height = self.result_slot.height + 20

            arcade.draw_lbwh_rectangle_filled(
                result_bg_x, result_bg_y, result_bg_width, result_bg_height,
                CRAFTING_RESULT_COLOR
            )

            # Стрелка от сетки к результату
            arrow_start_x = window_x + 250
            arrow_end_x = window_x + CRAFTING_WINDOW_WIDTH - 150
            arrow_y = window_y + CRAFTING_WINDOW_HEIGHT // 2

            arcade.draw_line(
                arrow_start_x, arrow_y,
                arrow_end_x, arrow_y,
                arcade.color.YELLOW, 3
            )

            arrow_points = [
                (arrow_end_x - 20, arrow_y - 10),
                (arrow_end_x, arrow_y),
                (arrow_end_x - 20, arrow_y + 10)
            ]
            arcade.draw_polygon_filled(arrow_points, arcade.color.YELLOW)

            self.result_slot.draw()

            # # Подсказка для крафта
            # if self.result_slot.block_name:
            #     arcade.draw_text(
            #         "Нажмите C для крафта",
            #         SCREEN_WIDTH // 2,
            #         window_y + 40,
            #         arcade.color.LIGHT_GREEN,
            #         18,
            #         anchor_x="center"
            #     )

        # Подсказка для закрытия
        help_text = Text(
            text="Нажмите E для закрытия:",
            x=SCREEN_WIDTH // 2,
            y=window_y + 50,
            color=arcade.color.WHITE,
            font_size=14,
            anchor_x="center"
        )
        help_text.draw()


class InventorySystem:
    """Система инвентаря"""

    def __init__(self, window):
        self.window = window
        self.slots = []
        self.selected_slot = 0
        self.crafting_window = CraftingWindow(self)
        self.setup_hotbar()

    def setup_hotbar(self):
        """Настройка панели быстрого доступа"""
        start_x = SCREEN_WIDTH // 2 - (HOTBAR_SLOTS * (BLOCK_SIZE + 17)) // 2
        y = HOTBAR_HEIGHT // 2 - 23

        for i in range(HOTBAR_SLOTS):
            x = start_x + i * (BLOCK_SIZE + 17)
            slot = InventorySlot(x, y, BLOCK_SIZE)
            self.slots.append(slot)

        # Выбираем первый слот
        self.select_slot(0)

    def select_slot(self, index: int):
        """Выбор слота"""
        if 0 <= index < len(self.slots):
            self.slots[self.selected_slot].selected = False
            self.selected_slot = index
            self.slots[self.selected_slot].selected = True

    def scroll_slot(self, direction: int):
        """Прокрутка слотов колесиком мыши"""
        new_index = (self.selected_slot + direction) % len(self.slots)
        self.select_slot(new_index)

    def draw(self):
        """Отрисовка инвентаря"""
        # Отрисовка слотов
        for slot in self.slots:
            slot.draw()

        # Отрисовка окна крафта
        self.crafting_window.draw()

    def add_block(self, name_block):
        """Добавление блока в инвентарь"""
        # Сначала ищем слот с таким же блоком, где можно добавить
        for slot in self.slots:
            if slot.block_name and slot.block_name == name_block and slot.count < 64:
                slot.count += 1
                slot.update_score()
                return True

        # Ищем пустой слот
        for slot in self.slots:
            if slot.block_name is None:
                slot.block_name = name_block
                slot.count += 1
                slot.update_score()
                slot.update_texture()  # Загружаем текстуру
                return True

        # Все слоты заняты
        return False

    def has_space_for(self, block_name):
        """Проверяет, есть ли место в инвентаре для блока"""
        # Проверяем слоты с таким же блоком
        for slot in self.slots:
            if slot.block_name == block_name and slot.count < 64:
                return True

        # Проверяем пустые слоты
        for slot in self.slots:
            if slot.block_name is None:
                return True

        return False

    def get_selected_block(self):
        """Получение выбранного блока"""
        slot = self.slots[self.selected_slot]
        return slot.block_name if slot else None

    def remove_block(self, x, y, game_window=None):
        """Удаление блока из слота и его установка в мире"""
        slot = self.slots[self.selected_slot]

        if slot.block_name and slot.count > 0 and slot.block_name in BLOCKS_DATA.keys():
            # Если передан game_window, пытаемся поставить блок
            if game_window:
                # Проверяем, есть ли блоки рядом (чтобы нельзя было ставить блоки в воздухе)
                nearby_blocks = arcade.get_sprites_at_point(
                    (x, y - 64),  # Проверяем блок снизу
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x + 64, y),  # Проверяем блок справа
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x - 64, y),  # Проверяем блок слева
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x, y + 64),  # Проверяем блок сверху
                    game_window.all_blocks
                )
                if nearby_blocks:
                    if game_window.create_block_at_position(slot.block_name, x, y):
                        # Если блок успешно поставлен, уменьшаем количество
                        slot.count -= 1
                        slot.update_score()

                        # Если блоков не осталось, очищаем слот
                        if slot.count == 0:
                            slot.block_name = None
                            slot.update_texture()
                        return True

        return False

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш для инвентаря и крафта"""
        if key == arcade.key.E:
            # Открытие/закрытие окна крафта
            self.crafting_window.toggle_visibility()
            return True

        if self.crafting_window.is_visible and key == arcade.key.C:
            # Крафт предмета
            if self.crafting_window.craft_item():
                # Звук успешного крафта
                if hasattr(self.window, 'craft_sound'):
                    arcade.play_sound(self.window.craft_sound)
            return True

        return False

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатий мыши для крафта"""
        if not self.crafting_window.is_visible:
            return False

        # Проверяем, был ли клик по сетке крафта
        for i, slot in enumerate(self.crafting_window.grid_slots):
            if (slot.x <= x <= slot.x + slot.width and
                    slot.y <= y <= slot.y + slot.height):

                selected_block = self.get_selected_block()
                if button == arcade.MOUSE_BUTTON_LEFT and selected_block:
                    # Добавляем предмет из выбранного слота в сетку крафта
                    slot_to_use = self.slots[self.selected_slot]
                    if slot_to_use.block_name and slot_to_use.count > 0:
                        if self.crafting_window.add_to_crafting_grid(selected_block, i):
                            slot_to_use.count -= 1
                            slot_to_use.update_score()
                            if slot_to_use.count == 0:
                                slot_to_use.block_name = None
                                slot_to_use.update_texture()

                elif button == arcade.MOUSE_BUTTON_RIGHT:
                    # Возвращаем предмет из сетки крафта в инвентарь
                    if self.crafting_window.remove_from_crafting_grid(i):
                        returned_block = slot.block_name
                        if returned_block:
                            self.add_block(returned_block)

                return True

        # Проверяем, был ли клик по результату крафта
        if self.crafting_window.result_slot:
            result_slot = self.crafting_window.result_slot
            if (result_slot.x <= x <= result_slot.x + result_slot.width and
                    result_slot.y <= y <= result_slot.y + result_slot.height):

                if button == arcade.MOUSE_BUTTON_LEFT and result_slot.block_name:
                    # Крафт предмета по клику на результат
                    if self.crafting_window.craft_item():
                        if hasattr(self.window, 'craft_sound'):
                            arcade.play_sound(self.window.craft_sound)

                return True

        return False

class Hero(arcade.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.is_walking = False
        self.current_side = Side.RIGHT
        self.texture_idle = arcade.load_texture(
            "skin/resized-Stive_1.png")
        self.texture = self.texture_idle
        self.walk_animation = []
        for i in range(2, 8):
            self.walk_animation.append(
                arcade.load_texture(f"skin/resized-Stive_{i}.png"))
        self.animation_update_speed = 0.15
        self.animation_counter = 0
        self.cur_texture_index = 0
        self.speed = speed
        self.dx = 0
        self.dy = 0
        self.mining_target = None
        self.max_health = 100
        self.health = self.max_health
        self.is_alive = True

    def update(self, delta_time):
        current_speed = self.speed
        if self.dx != 0 and self.dy != 0:
            current_speed /= math.sqrt(2)
        self.center_x += self.dx * current_speed * delta_time
        self.center_y += self.dy * current_speed * delta_time

    def update_animation(self, delta_time: float = 1 / 60):
        self.animation_counter += delta_time
        if self.animation_counter >= self.animation_update_speed:
            self.cur_texture_index += 1
            self.cur_texture_index %= len(self.walk_animation)
            self.animation_counter = 0
        if self.is_walking:
            self.texture = self.walk_animation[self.cur_texture_index] if self.current_side == Side.LEFT else \
                self.walk_animation[self.cur_texture_index].flip_horizontally()
        else:
            self.texture = self.texture_idle


class Crack(arcade.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.texture_idle = arcade.load_texture(
            "cracks/crack_0.png")
        self.texture = self.texture_idle
        self.cracking_animation = []
        for i in range(1, 9):
            self.cracking_animation.append(
                arcade.load_texture(f"cracks/crack_{i}.png"))
        self.texture_change_time = 0
        self.texture_change_delay = speed
        self.current_texture = 0
        self.scale = 4
        self.is_breaking_block = True

    def update_animation(self, delta_time: float = 1 / 60):
        """Обновление анимации трещины"""
        self.texture_change_time += delta_time
        if self.is_breaking_block:
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture == len(self.cracking_animation) - 1:
                    self.is_breaking_block = False
                self.texture = self.cracking_animation[self.current_texture]


class Monster(arcade.Sprite):
    def __init__(self, x, y, speed, damage):
        super().__init__()

        self.center_x = x
        self.center_y = y

        self.texture_idle = arcade.load_texture(
            "skin/resized-zombie_1.png"
        )
        self.texture = self.texture_idle

        self.walk_animation = []
        for i in range(2, 8):
            self.walk_animation.append(
                arcade.load_texture(
                    f"skin/resized-zombie_{i}.png"
                )
            )

        self.animation_update_speed = 0.15
        self.animation_counter = 0
        self.cur_texture_index = 0

        self.speed = speed
        self.damage = damage

        self.dx = 0
        self.dy = 0

        self.last_attack_time = 0
        self.attack_delay = 1

        self.physics_engine = None

        self.current_side = Side.RIGHT

    def setup_physics(self, collision_list):
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self,
            collision_list,
            gravity_constant=GRAVITY
        )

    def update(self, delta_time, player):
        # Ходим к игроку по X
        if player.center_x < self.center_x:
            self.dx = -1
            self.current_side = Side.RIGHT
        else:
            self.dx = 1
            self.current_side = Side.LEFT

        self.center_x += self.dx * self.speed * delta_time

        # Ходим к игроку по Y
        if player.center_y - self.center_y >= 62:
            self.dy = 12
        else:
            self.dy = 0

        self.center_y += self.dy * self.speed * delta_time

        # Физика (гравитация, пол)
        if self.physics_engine:
            self.physics_engine.update()

        # Урон при касании
        if arcade.check_for_collision(self, player):
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attack_delay:
                if hasattr(player, "health"):
                    player.health -= self.damage
                self.last_attack_time = current_time

    def update_animation(self, delta_time: float = 1 / 60):
        self.animation_counter += delta_time
        if self.animation_counter >= self.animation_update_speed:
            self.cur_texture_index += 1
            self.cur_texture_index %= len(self.walk_animation)
            self.animation_counter = 0
        self.texture = self.walk_animation[self.cur_texture_index] if self.current_side == Side.LEFT else \
            self.walk_animation[self.cur_texture_index].flip_horizontally()


class GridGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, antialiasing=True)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Камеры: мир и GUI
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Данные уровня
        self.tile_map = None
        self.player_list = arcade.SpriteList()
        self.player = None
        self.world_width = None
        self.world_height = None

        self.is_jumping = False
        self.can_jump = False
        self.player_list = None
        self.first_blocks_hit_list = arcade.SpriteList()
        self.sprite_lists = {}
        self.all_blocks = arcade.SpriteList()
        self.is_breaking_block = False
        self.hold_duration = 10

        # Система инвентаря
        self.inventory = InventorySystem(self)

        # Экран респавна
        self.respawn_screen = RespawnScreen(self)

        # Экран паузы
        self.pause_screen = PauseScreen(self)

        # Файл сохранения
        self.save_file = "game_save.json"

        self.sound_player = None


    def setup(self):
        # СОЗДАЕМ И СОХРАНЯЕМ ВСЕ СПРАЙТ-ЛИСТЫ
        self.create_sprite_lists()

        # СОЗДАЕМ ИГРОКА
        self.player_start_x = 200
        self.player_start_y = 1400
        self.player = Hero(self.player_start_x, self.player_start_y, 200)
        self.player.scale = 0.24
        self.player_list.append(self.player)

        # Пытаемся загрузить сохраненную игру
        if not self.load_game():
            # Если не удалось загрузить, создаем нового монстра
            monster = Monster(400, 700, speed=60, damage=10)
            monster.setup_physics(self.sprite_lists['collisions'])
            monster.scale = 0.32
            self.monster_list.append(monster)

        # Уточняем размеры мира по карте
        self.world_width = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
        self.world_height = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)

        # Физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.sprite_lists['collisions'],
            gravity_constant=GRAVITY
        )

        # Загрузка музыки
        self.grass_sound = arcade.load_sound("music/grass.mp3")
        self.grass2_sound = arcade.load_sound("music/grass2.mp3")
        self.wood_sound = arcade.load_sound("music/wood.mp3")
        self.stone_sound = arcade.load_sound("music/stone.mp3")
        self.craft_sound = arcade.load_sound("music/stone.mp3")

    def create_sprite_lists(self):
        """Создание всех спрайт-листов"""
        # Создаем каждый спрайт-лист отдельно
        # Загружаем уровень из TMX-файла
        self.tile_map = arcade.load_tilemap("test_map_minecraft.tmx", scaling=TILE_SCALING)

        self.player_list = arcade.SpriteList()
        self.cracks_list = arcade.SpriteList()
        self.monster_list = arcade.SpriteList()

        for block_name in ['earth', 'stone', 'coal', 'iron', 'gold',
                           'diamonds', 'wood', 'flowers', 'foliage', 'collisions']:
            if block_name not in self.sprite_lists:
                self.sprite_lists[block_name] = self.tile_map.sprite_lists[block_name]

        for sprite_list in self.sprite_lists.values():
            self.all_blocks.extend(sprite_list)

    def on_draw(self):
        """Отрисовка экрана."""
        self.clear()

        # 1) Мир
        self.world_camera.use()
        for name, sprite_list in self.sprite_lists.items():
            if name != 'collisions':
                sprite_list.draw()

        self.cracks_list.draw()
        self.player_list.draw()
        self.monster_list.draw()

        # 2) GUI
        self.gui_camera.use()

        if self.player and self.player.is_alive:
            bar_width = 200
            bar_height = 20

            health_ratio = max(0, self.player.health / self.player.max_health)
            health_width = int(bar_width * health_ratio)

            x = 20
            y = SCREEN_HEIGHT - 40

            # Фон
            bg_rect = arcade.rect.XYWH(x + bar_width // 2, y, bar_width, bar_height)
            arcade.draw_rect_filled(bg_rect, arcade.color.DARK_RED)

            # Текущее здоровье
            hp_rect = arcade.rect.XYWH(x + health_width // 2, y, health_width, bar_height)
            arcade.draw_rect_filled(hp_rect, arcade.color.GREEN)

            # Рамка
            frame_rect = arcade.rect.XYWH(x + bar_width // 2, y, bar_width, bar_height)
            arcade.draw_rect_outline(frame_rect, arcade.color.BLACK, 2)

        # Отрисовка экрана респавна
        self.respawn_screen.draw()

        # Отрисовка экрана паузы
        self.pause_screen.draw()

        # Отрисовка инвентаря и окна крафта (если игрок жив и не на экране респавна)
        if (self.player and self.player.is_alive and
                not self.respawn_screen.is_visible and
                not self.pause_screen.is_visible):
            self.inventory.draw()

            # Подсказка для открытия крафта
            if not self.inventory.crafting_window.is_visible:
                help_text = Text(
                    text="Нажмите E для открытия крафта:",
                    x=SCREEN_WIDTH // 2,
                    y=85,
                    color=arcade.color.LIGHT_GRAY,
                    font_size=16,
                    anchor_x="center"
                )
                help_text.draw()


    def on_update(self, dt: float):
        # Если игра на паузе, не обновляем игровую логику
        if self.pause_screen.is_visible:
            return
        self.physics_engine.update()

        # Анимация игрока
        self.player_list.update_animation(dt)
        self.player_list.update(dt)

        # Обновление трещины
        if self.is_breaking_block:
            release_time = time.time()
            self.hold_duration = release_time - self.press_time
            if self.hold_duration > self.time_digging:
                self.remove_blocks_and_cracks()
            else:
                for crack in self.cracks_list:
                    crack.update_animation(dt)
        else:
            for crack in self.cracks_list:
                crack.remove_from_sprite_lists()

        if not self.player:
            return

        if self.player.health <= 0 and self.player.is_alive:
            self.player.is_alive = False
            self.player.remove_from_sprite_lists()
            self.respawn_screen.show()  # Показываем экран респавна

        # Если виден экран респавна, не обновляем остальную игру
        if self.respawn_screen.is_visible:
            return

        # Движение камеры
        cam_x, cam_y = self.world_camera.position

        # Не показываем «пустоту» за краями карты
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.world_width - half_w, self.player.center_x))
        target_y = max(half_h, min(self.world_height - half_h, self.player.center_y))

        # Плавное перемещение
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y

        self.world_camera.position = (smooth_x, smooth_y)

        self.monster_list.update_animation(dt)

        for monster in self.monster_list:
            monster.update(dt, self.player)

    def save_game(self):
        """Сохраняет текущее состояние игры в JSON файл"""
        try:
            save_data = {
                "player": {
                    "position": {
                        "x": self.player.center_x,
                        "y": self.player.center_y
                    },
                    "health": self.player.health,
                    "max_health": self.player.max_health,
                    "is_alive": self.player.is_alive
                },
                "inventory": {
                    "slots": [],
                    "selected_slot": self.inventory.selected_slot
                },
                "blocks": {},
                "monsters": [],
                "cracks": []
            }

            # Сохраняем инвентарь
            for slot in self.inventory.slots:
                slot_data = {
                    "block_name": slot.block_name,
                    "count": slot.count
                }
                save_data["inventory"]["slots"].append(slot_data)

            # Сохраняем сетку крафта
            save_data["crafting_grid"] = []
            for slot in self.inventory.crafting_window.grid_slots:
                slot_data = {
                    "block_name": slot.block_name,
                    "count": slot.count
                }
                save_data["crafting_grid"].append(slot_data)

            # Сохраняем результат крафта
            save_data["crafting_result"] = {
                "block_name": self.inventory.crafting_window.result_slot.block_name,
                "count": self.inventory.crafting_window.result_slot.count
            }

            # Сохраняем позиции блоков по типам
            for block_name, sprite_list in self.sprite_lists.items():
                if block_name != 'collisions':  # Не сохраняем коллизионные блоки отдельно
                    block_positions = []
                    for block in sprite_list:
                        block_positions.append({
                            "x": block.center_x,
                            "y": block.center_y
                        })
                    if block_positions:  # Сохраняем только если есть блоки этого типа
                        save_data["blocks"][block_name] = block_positions

            # Сохраняем монстров
            for monster in self.monster_list:
                monster_data = {
                    "position": {
                        "x": monster.center_x,
                        "y": monster.center_y
                    },
                    "health": monster.health if hasattr(monster, 'health') else None
                }
                save_data["monsters"].append(monster_data)

            # Сохраняем трещины (если есть)
            for crack in self.cracks_list:
                crack_data = {
                    "position": {
                        "x": crack.center_x,
                        "y": crack.center_y
                    },
                    "current_texture": crack.current_texture,
                    "is_breaking_block": crack.is_breaking_block
                }
                save_data["cracks"].append(crack_data)

            # Записываем в файл
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)

            print(f"Игра сохранена в {self.save_file}")
            return True

        except Exception as e:
            print(f"Ошибка сохранения игры: {e}")
            return False

    def load_game(self):
        """Загружает сохраненное состояние игры из JSON файла"""
        if not os.path.exists(self.save_file):
            print("Сохранение не найдено, начинаем новую игру")
            return False

        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Загружаем игрока
            player_data = save_data.get("player", {})
            if player_data:
                self.player.center_x = player_data.get("position", {}).get("x", self.player_start_x)
                self.player.center_y = player_data.get("position", {}).get("y", self.player_start_y)
                self.player.health = player_data.get("health", self.player.max_health)
                self.player.max_health = player_data.get("max_health", 100)
                self.player.is_alive = player_data.get("is_alive", True)

            # Загружаем инвентарь
            inventory_data = save_data.get("inventory", {})
            if inventory_data:
                self.inventory.selected_slot = inventory_data.get("selected_slot", 0)
                slots_data = inventory_data.get("slots", [])

                for i, slot_data in enumerate(slots_data):
                    if i < len(self.inventory.slots):
                        slot = self.inventory.slots[i]
                        slot.block_name = slot_data.get("block_name")
                        slot.count = slot_data.get("count", 0)
                        slot.update_score()
                        slot.update_texture()

            # Загружаем сетку крафта
            crafting_grid_data = save_data.get("crafting_grid", [])
            if crafting_grid_data and len(crafting_grid_data) == len(self.inventory.crafting_window.grid_slots):
                for i, slot_data in enumerate(crafting_grid_data):
                    slot = self.inventory.crafting_window.grid_slots[i]
                    slot.block_name = slot_data.get("block_name")
                    slot.count = slot_data.get("count", 0)
                    slot.update_score()
                    slot.update_texture()

            # Загружаем результат крафта
            crafting_result_data = save_data.get("crafting_result", {})
            if crafting_result_data:
                result_slot = self.inventory.crafting_window.result_slot
                result_slot.block_name = crafting_result_data.get("block_name")
                result_slot.count = crafting_result_data.get("count", 0)
                result_slot.update_score()
                result_slot.update_texture()
                self.inventory.crafting_window.current_recipe = None  # Сброс рецепта

            # Загружаем блоки
            blocks_data = save_data.get("blocks", {})
            if blocks_data:
                # Очищаем существующие блоки (кроме коллизий и игрока)
                for block_name, sprite_list in self.sprite_lists.items():
                    if block_name not in ['collisions']:
                        sprite_list.clear()

                # Загружаем сохраненные блоки
                for block_name, positions in blocks_data.items():
                    if block_name not in self.sprite_lists:
                        self.sprite_lists[block_name] = arcade.SpriteList()

                    for pos in positions:
                        block = arcade.Sprite(
                            f"minecraft_blocks/{block_name}.webp",
                            scale=TILE_SCALING
                        )
                        block.center_x = pos.get("x", 0)
                        block.center_y = pos.get("y", 0)
                        self.sprite_lists[block_name].append(block)

                        # Если это блок с коллизией, создаем коллизионный блок
                        if block_name in ['earth', 'stone', 'wood', 'foliage', 'wooden_planks',
                                          'oven', 'oven2', 'stone_bricks', 'glass']:
                            collision_block = arcade.Sprite(
                                f"minecraft_blocks/Border_29_EE1.webp",
                                scale=TILE_SCALING
                            )
                            collision_block.center_x = block.center_x
                            collision_block.height = block.height
                            self.sprite_lists['collisions'].append(collision_block)

            # Загружаем монстров
            monsters_data = save_data.get("monsters", [])
            if monsters_data:
                self.monster_list.clear()
                for monster_data in monsters_data:
                    pos = monster_data.get("position", {})
                    monster = Monster(
                        pos.get("x", 400),
                        pos.get("y", 700),
                        speed=60,
                        damage=10
                    )
                    monster.setup_physics(self.sprite_lists['collisions'])
                    monster.scale = 0.32
                    if hasattr(monster, 'health'):
                        monster.health = monster_data.get("health", 100)
                    self.monster_list.append(monster)

            # Загружаем трещины
            cracks_data = save_data.get("cracks", [])
            if cracks_data:
                self.cracks_list.clear()
                for crack_data in cracks_data:
                    pos = crack_data.get("position", {})
                    crack = Crack(pos.get("x", 0), pos.get("y", 0), speed=0.5)
                    crack.current_texture = crack_data.get("current_texture", 0)
                    crack.is_breaking_block = crack_data.get("is_breaking_block", False)

                    if crack.current_texture < len(crack.cracking_animation):
                        crack.texture = crack.cracking_animation[crack.current_texture]

                    self.cracks_list.append(crack)

            # Обновляем общий список всех блоков
            self.update_all_blocks_list()

            print(f"Игра загружена из {self.save_file}")
            return True

        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")
            return False

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        # Обновляем позицию мыши для экрана респавна
        self.respawn_screen.update_mouse_position(x, y)

        # Обновляем позицию мыши для экрана паузы
        self.pause_screen.update_mouse_position(x, y)

        # Проверяем клик по кнопке респавна
        if self.respawn_screen.check_button_click(x, y):
            self.respawn_player()
            return

        # Проверяем клик по кнопкам паузы
        if self.pause_screen.check_button_click(x, y):
            return


        # Обработка кликов в остальной игре только если игрок жив
        if not self.player or not self.player.is_alive:
            return

        # Проверяем клики в окне крафта
        if self.inventory.crafting_window.is_visible:
            if self.inventory.on_mouse_press(x, y, button, modifiers):
                return

        # изменение координат с учётом движения камеры
        x, y = self.world_camera.unproject((x, y))[0], self.world_camera.unproject((x, y))[1]
        if button == arcade.MOUSE_BUTTON_LEFT:
            # проверка на близость к игроку
            if (self.player.center_x - 100 <= x <= self.player.center_x + 100 and
                    self.player.center_y - 100 <= y <= self.player.center_y + 100):
                # добавляем в список все нажатые блоки
                self.first_blocks_hit_list = arcade.get_sprites_at_point((x, y), self.all_blocks)
                for block in self.first_blocks_hit_list:
                    for name, list in self.sprite_lists.items():
                        # по имени находим информацию о блоке
                        if block in list and name != 'collisions':
                            self.name = name

                            if not self.sound_player:
                                music = BLOCKS_DATA[self.name][1]
                                self.sound_player = arcade.play_sound(
                                    eval(f'self.{music}_sound'),
                                    loop=True)
                            selected_block_name = self.inventory.get_selected_block()
                            coef = 1
                            if selected_block_name:
                                if selected_block_name in WEAPON.keys():
                                    if self.name in WEAPON[selected_block_name]['object']:
                                        coef = WEAPON[selected_block_name]['damage']
                            self.time_digging = BLOCKS_DATA[self.name][0] / coef
                            speed_animation_digging = BLOCKS_DATA[self.name][2]

                            # создаём трещину
                            crack = Crack(block.center_x, block.center_y,
                                          self.time_digging / speed_animation_digging)
                            self.is_breaking_block = True
                            self.cracks_list.append(crack)
                            self.press_time = time.time()

        if button == arcade.MOUSE_BUTTON_RIGHT:
            if (self.player.center_x - 140 <= x <= self.player.center_x + 140 and
                    self.player.center_y - 140 <= y <= self.player.center_y + 140):
                self.inventory.remove_block(x, y, self)

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        # Обновляем позицию мыши для экрана респавна
        self.respawn_screen.update_mouse_position(x, y)

        # Обновляем позицию мыши для экрана паузы (добавил)
        self.pause_screen.update_mouse_position(x, y)

        if self.is_breaking_block:
            x, y = self.world_camera.unproject((x, y))[0], self.world_camera.unproject((x, y))[1]
            blocks_hit_list = arcade.get_sprites_at_point((x, y), self.all_blocks)
            # смотрим, не сместился ли курсор с блока
            for block in blocks_hit_list:
                if block not in self.first_blocks_hit_list:
                    self.remove_blocks_and_cracks()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.is_breaking_block:
            self.remove_blocks_and_cracks()

    def remove_blocks_and_cracks(self):
        """Останавливает копание блока.
        Удаляет его и трещины, если прошло достаточно времени"""
        release_time = time.time()
        self.hold_duration = release_time - self.press_time
        self.is_breaking_block = False
        if self.sound_player:
            arcade.stop_sound(self.sound_player)
        self.sound_player = None

        if self.hold_duration > self.time_digging:
            self.hold_duration = 10
            for crack in self.cracks_list:
                crack.remove_from_sprite_lists()
            for block in self.first_blocks_hit_list:
                if block not in self.sprite_lists['collisions']:
                    if self.name in ['coal', 'iron', 'gold', 'diamonds']:
                        self.name += '2'
                    self.inventory.add_block(self.name)
                block.remove_from_sprite_lists()

        # удаляем только трещины, если прошло меньше нужного времени
        for crack in self.cracks_list:
            crack.remove_from_sprite_lists()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Обработка прокрутки колеса мыши"""
        if scroll_y > 0:  # Прокрутка вверх
            self.inventory.scroll_slot(-1)
        elif scroll_y < 0:  # Прокрутка вниз
            self.inventory.scroll_slot(1)

    def on_key_press(self, key, modifiers):
        # Обработка клавиш для экрана респавна
        if self.respawn_screen.on_key_press(key, modifiers):
            self.respawn_player()
            return

        # Обработка клавиш для экрана паузы
        if self.pause_screen.on_key_press(key, modifiers):
            return

        # Проверяем обработку клавиш инвентарем (крафт)
        if self.inventory.on_key_press(key, modifiers):
            return

        # Обработка игровых клавиш только если игрок жив и игра не на паузе
        if (not self.player or not self.player.is_alive or
                    self.pause_screen.is_visible):
            return

        # прыжок
        if key in (arcade.key.W, arcade.key.UP):
            if self.physics_engine.can_jump():
                self.player.dy = 6

        # движение
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.dx = -1
            self.player.is_walking = True
            self.player.current_side = Side.LEFT
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.player.dx = 1
            self.player.is_walking = True
            self.player.current_side = Side.RIGHT

        if key == arcade.key.ESCAPE:
            if not self.pause_screen.is_visible:
                self.pause_screen.show()
            else:
                self.pause_screen.hide()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.player.dy = 0
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.dx = 0
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.player.dy = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.player.dx = 0
        if self.player.dx == 0 and self.player.dy == 0:
            self.player.is_walking = False

        if not self.player.is_alive:
            return

    def create_block_at_position(self, block_name, x, y):
        """Создает блок в указанной позиции"""
        # Преобразуем координаты в координаты сетки
        actual_tile_size = self.tile_map.tile_width * TILE_SCALING
        grid_x1 = round(x / actual_tile_size) * actual_tile_size + 32
        grid_x2 = round(x / actual_tile_size) * actual_tile_size - 32
        grid_x = grid_x1 if abs(x - grid_x1) < abs(x - grid_x2) else grid_x2
        grid_y1 = round(y / actual_tile_size) * actual_tile_size + 32
        grid_y2 = round(y / actual_tile_size) * actual_tile_size - 32
        grid_y = grid_y1 if abs(y - grid_y1) < abs(y - grid_y2) else grid_y2

        # Проверяем, нет ли уже блока в этой позиции
        point = (grid_x, grid_y)
        existing_blocks = arcade.get_sprites_at_point(point, self.all_blocks)

        if existing_blocks:
            return False  # Место занято

        # Проверяем, чтобы блок не ставился внутри игрока
        player_rect = arcade.LRBT(
            self.player.left - 5,
            self.player.right + 5,
            self.player.bottom - 5,
            self.player.top + 5
        )

        if player_rect.left <= grid_x <= player_rect.right and player_rect.bottom <= grid_y <= player_rect.top:
            return False  # Нельзя ставить блок внутри игрока

        # Создаем блок в зависимости от типа
        block = arcade.Sprite(
            f"minecraft_blocks/{block_name}.webp",
            scale=TILE_SCALING
        )

        block.center_x = grid_x
        block.center_y = grid_y

        # Добавляем блок только если это блок с коллизией
        if block_name in ['earth', 'stone', 'wood', 'foliage', 'wooden_planks',
                          'oven', 'oven2', 'stone_bricks', 'glass']:
            collision_block = arcade.Sprite(
                f"minecraft_blocks/Border_29_EE1.webp",
                scale=TILE_SCALING
            )
            collision_block.center_x = grid_x
            collision_block.center_y = grid_y
            self.sprite_lists['collisions'].append(collision_block)

        # Для новых предметов крафта
        if block_name not in self.sprite_lists:
            self.sprite_lists[block_name] = arcade.SpriteList()
        self.sprite_lists[block_name].append(block)

        # Обновляем общий список всех блоков
        self.update_all_blocks_list()

        return True

    def update_all_blocks_list(self):
        """Обновляет общий список всех блоков"""
        self.all_blocks.clear()
        for sprite_list in self.sprite_lists.values():
            self.all_blocks.extend(sprite_list)

    def respawn_player(self):
        """Перерождение игрока"""
        self.player = Hero(self.player_start_x, self.player_start_y, 200)
        self.player.scale = 0.24
        self.player_list.append(self.player)
        self.player.health = self.player.max_health
        self.player.is_alive = True

        # Скрываем экран респавна
        self.respawn_screen.hide()

        # Пересоздаём физику
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.sprite_lists['collisions'],
            gravity_constant=GRAVITY
        )

    def on_close(self):
        """Вызывается при закрытии окна"""
        # Сохраняем игру перед закрытием
        self.save_game()

        try:
            super().on_close()
            menu = MenuWindow()
            arcade.run()
        except pyglet.gl.lib.GLException:
            pass

class RespawnScreen:
    """Класс для экрана респавна в конце игры"""

    def __init__(self, window):
        self.window = window
        self.is_visible = False

        # Позиция и размеры кнопки респавна
        self.respawn_button_x = SCREEN_WIDTH // 2
        self.respawn_button_y = SCREEN_HEIGHT // 2 - 60
        self.respawn_button_width = 200
        self.respawn_button_height = 50

        # Цвета
        self.background_color = (0, 0, 0, 180)  # Полупрозрачный черный
        self.title_color = arcade.color.RED
        self.text_color = arcade.color.WHITE
        self.button_color = arcade.color.BLUE_GRAY
        self.button_hover_color = arcade.color.LIGHT_BLUE
        self.button_border_color = arcade.color.BLACK

        # Состояние кнопки
        self.is_button_hovered = False

    def show(self):
        """Показать экран респавна"""
        self.is_visible = True

    def hide(self):
        """Скрыть экран респавна"""
        self.is_visible = False
        self.is_button_hovered = False

    def update_mouse_position(self, x, y):
        """Обновить позицию мыши для определения наведения на кнопку"""
        if not self.is_visible:
            return

        # Проверяем, находится ли курсор над кнопкой
        left = self.respawn_button_x - self.respawn_button_width / 2
        right = self.respawn_button_x + self.respawn_button_width / 2
        bottom = self.respawn_button_y - self.respawn_button_height / 2
        top = self.respawn_button_y + self.respawn_button_height / 2

        self.is_button_hovered = (left <= x <= right and bottom <= y <= top)

    def check_button_click(self, x, y):
        """Проверить, была ли нажата кнопка респавна"""
        if not self.is_visible:
            return False

        left = self.respawn_button_x - self.respawn_button_width / 2
        right = self.respawn_button_x + self.respawn_button_width / 2
        bottom = self.respawn_button_y - self.respawn_button_height / 2
        top = self.respawn_button_y + self.respawn_button_height / 2

        if left <= x <= right and bottom <= y <= top:
            self.hide()
            return True

        return False

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if not self.is_visible:
            return False

        if key == arcade.key.R:
            # Респавн по клавише R
            self.hide()
            return True

        return False

    def draw(self):
        """Отрисовка экрана респавна"""
        if not self.is_visible:
            return

        # Используем камеру GUI
        self.window.gui_camera.use()

        # Полупрозрачный фон
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            self.background_color
        )

        # Текст смерти
        death_text = Text(
            text="Вы умерли",
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 + 30,
            color=self.title_color,
            font_size=40,
            anchor_x="center",
            bold=True
        )
        death_text.draw()


        death_text2 = Text(
            text="Нажмите кнопку, чтобы переродиться",
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2,
            color=self.text_color,
            font_size=20,
            anchor_x="center"
        )
        death_text2.draw()

        # Определяем цвет кнопки (при наведении меняется)
        button_color = self.button_hover_color if self.is_button_hovered else self.button_color

        # Кнопка респавна
        rect = arcade.rect.XYWH(
            self.respawn_button_x,
            self.respawn_button_y,
            self.respawn_button_width,
            self.respawn_button_height
        )

        # Фон кнопки
        arcade.draw_rect_filled(rect, button_color)

        # Рамка кнопки
        arcade.draw_rect_outline(
            rect,
            self.button_border_color,
            border_width=2
        )

        # Текст на кнопке
        text_on_button = Text(
            text="Переродиться",
            x=self.respawn_button_x,
            y=self.respawn_button_y,
            color=self.text_color,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold = True
        )
        text_on_button.draw()

        # Подсказка про клавишу R
        help_text = Text(
            text="Или нажмите клавишу R",
            x=self.respawn_button_x,
            y=self.respawn_button_y - 70,
            color=arcade.color.LIGHT_GRAY,
            font_size=16,
            anchor_x="center"
        )
        help_text.draw()


class MenuWindow(arcade.Window):
    def __init__(self):
        # Инициализируем окно
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Меню игры")

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

        self.background_texture = arcade.load_texture("menu/background.jpg")

        # Для переключения на игровое окно
        self.game_window = None

    def setup_widgets(self):
        overlay_texture = arcade.load_texture("menu/title.png")
        overlay_widget = arcade.gui.UITextureButton(
            width=585, height=150,
            texture=overlay_texture
        )
        self.box_layout.add(overlay_widget)

        texture_normal = arcade.load_texture("menu/button_normal.jpg")
        texture_hovered = arcade.load_texture("menu/button_hover.jpg")
        texture_pressed = arcade.load_texture("menu/button_press.jpg")

        old_game_button = UITextureButton(texture=texture_normal,
                                          texture_hovered=texture_hovered,
                                          texture_pressed=texture_pressed,
                                          scale=0.2,
                                          text="Продолжить")
        old_game_button.on_click = self.start_game
        self.box_layout.add(old_game_button)

        new_game_button = UITextureButton(texture=texture_normal,
                                          texture_hovered=texture_hovered,
                                          texture_pressed=texture_pressed,
                                          scale=0.2,
                                          text="Новая игра")
        new_game_button.on_click = self.new_game
        self.box_layout.add(new_game_button)

        label = UILabel(text="Выбери скин:",
                        font_size=15,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        dropdown = UIDropdown(options=["Стив", "Алекс"], width=200)
        dropdown.on_change = lambda value: print(f"Выбрано: {value}")
        self.box_layout.add(dropdown)

        label = UILabel(text="Громкость:",
                        font_size=15,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        slider = UISlider(width=200, height=20, min_value=0, max_value=100, value=50)
        slider.on_change = lambda value: print(f"Слайдер: {value}")
        self.box_layout.add(slider)

    def new_game(self, event=None):
        super().on_close()

        self.game_window = GridGame()
        print(self.game_window.save_file)
        if os.path.exists(self.game_window.save_file):
            os.remove(self.game_window.save_file)
        self.game_window.setup()
        arcade.run()
    def start_game(self, event=None):
        # Закрываем меню и открываем игровое окно
        # from game_window import GameWindow  # Импортируем здесь, чтобы избежать циклического импорта
        super().on_close()
        self.game_window = GridGame()
        self.game_window.setup()
        arcade.run()  # Запускаем игровое окно

    def on_draw(self):
        self.clear()

        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.LBWH(0, 0,
                            self.width, self.height))

        self.manager.draw()  # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает

    def on_update(self, delta_time):
        """Обновление логики"""
        pass

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        pass


class PauseScreen:
    """Класс для экрана паузы"""

    def __init__(self, window):
        self.window = window
        self.is_visible = False

        # Позиция и размеры кнопок
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 70

        # Цвета
        self.background_color = (0, 0, 0, 180)  # Полупрозрачный черный
        self.title_color = arcade.color.GOLD
        self.text_color = arcade.color.WHITE
        self.button_color = arcade.color.BLUE_GRAY
        self.button_hover_color = arcade.color.LIGHT_BLUE
        self.button_border_color = arcade.color.BLACK

        # Состояния кнопок
        self.continue_button_hovered = False
        self.save_button_hovered = False
        self.exit_button_hovered = False
        self.craft_button_hovered = False

    def show(self):
        """Показать экран паузы"""
        self.is_visible = True

    def hide(self):
        """Скрыть экран паузы"""
        self.is_visible = False
        self.continue_button_hovered = False
        self.save_button_hovered = False
        self.exit_button_hovered = False
        self.craft_button_hovered = False

    def update_mouse_position(self, x, y):
        """Обновить позицию мыши для определения наведения на кнопки"""
        if not self.is_visible:
            return

        # Центр экрана
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Позиции кнопок
        continue_y = center_y + 30
        save_y = center_y - 40
        craft_y = center_y - 110
        exit_y = center_y - 180

        # Проверяем наведение на каждую кнопку
        self.continue_button_hovered = self._is_point_in_button(x, y, center_x, continue_y)
        self.save_button_hovered = self._is_point_in_button(x, y, center_x, save_y)
        self.craft_button_hovered = self._is_point_in_button(x, y, center_x, craft_y)
        self.exit_button_hovered = self._is_point_in_button(x, y, center_x, exit_y)

    def _is_point_in_button(self, x, y, button_x, button_y):
        """Проверяет, находится ли точка внутри кнопки"""
        left = button_x - self.button_width / 2
        right = button_x + self.button_width / 2
        bottom = button_y - self.button_height / 2
        top = button_y + self.button_height / 2

        return left <= x <= right and bottom <= y <= top

    def check_button_click(self, x, y):
        """Проверить, была ли нажата какая-либо кнопка"""
        if not self.is_visible:
            return False

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Позиции кнопок
        continue_y = center_y + 30
        save_y = center_y - 40
        craft_y = center_y - 110
        exit_y = center_y - 180

        # Проверяем клик по каждой кнопке
        if self._is_point_in_button(x, y, center_x, continue_y):
            self.hide()
            return True

        if self._is_point_in_button(x, y, center_x, save_y):
            print("Сохранение игры...")
            self.window.save_game()  # Добавьте эту строку
            return True

        if self._is_point_in_button(x, y, center_x, craft_y):
            print("Открытие инструкции по крафту...")
            return True

        if self._is_point_in_button(x, y, center_x, exit_y):
            print("Выход в меню...")
            self.window.save_game()  # Сохраняем перед выходом
            self.window.on_close()
            return True

        return False

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if not self.is_visible:
            return False

        if key == arcade.key.ESCAPE:
            # ESC для продолжения игры
            self.hide()
            return True

        return False

    def draw(self):
        """Отрисовка экрана паузы"""
        if not self.is_visible:
            return

        # Используем камеру GUI
        self.window.gui_camera.use()

        # Полупрозрачный фон
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            self.background_color
        )

        # Заголовок
        title_text = Text(
            text="ИГРА НА ПАУЗЕ",
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 + 100,
            color=self.title_color,
            font_size=40,
            anchor_x="center",
            bold=True
        )
        title_text.draw()

        # Центр экрана для кнопок
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Кнопка "Продолжить"
        self._draw_button(
            center_x, center_y + 30,
            "Продолжить",
            self.continue_button_hovered
        )

        # Кнопка "Сохранить"
        self._draw_button(
            center_x, center_y - 40,
            "Сохранить",
            self.save_button_hovered
        )

        # Кнопка "Инструкция по крафту"
        self._draw_button(
            center_x, center_y - 110,
            "Инструкция по крафту",
            self.craft_button_hovered
        )

        # Кнопка "Выйти"
        self._draw_button(
            center_x, center_y - 180,
            "Выйти",
            self.exit_button_hovered
        )

        # Подсказка про клавишу ESC
        help_text = Text(
            text="Нажмите ESC для продолжения",
            x=SCREEN_WIDTH // 2,
            y=50,
            color=arcade.color.LIGHT_GRAY,
            font_size=16,
            anchor_x="center"
        )
        help_text.draw()

    def _draw_button(self, x, y, text, is_hovered):
        """Рисует одну кнопку"""
        # Определяем цвет кнопки
        button_color = self.button_hover_color if is_hovered else self.button_color

        # Кнопка
        rect = arcade.rect.XYWH(
            x,
            y,
            self.button_width,
            self.button_height
        )

        # Фон кнопки
        arcade.draw_rect_filled(rect, button_color)

        # Рамка кнопки
        arcade.draw_rect_outline(
            rect,
            self.button_border_color,
            border_width=2
        )

        # Текст на кнопке
        button_text = Text(
            text=text,
            x=x,
            y=y,
            color=self.text_color,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        button_text.draw()

def main():
    # Создаем и запускаем игру
    menu = MenuWindow()
    arcade.run()


if __name__ == "__main__":
    main()
