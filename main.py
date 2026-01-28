from codecs import xmlcharrefreplace_errors

import arcade
import math
import enum
import time
import csv

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Minecraft"
TILE_SCALING = 0.2

CAMERA_LERP = 0.12

GRAVITY = 1

BLOCKS_DATA = {
    'earth': [0.8, 'grass', 16],
    'stone': [4, 'stone', 8],
    'coal': [6, 'stone', 6],
    'iron': [12, 'stone', 1],
    'gold': [18, 'stone', 0.5],
    'diamonds': [25, 'stone', 0.2],
    'wood': [3, 'wood', 10],
    'flowers': [0.5, 'grass', 21],
    'foliage': [0.2, 'grass2', 25]
}

# Размеры блоков
BLOCK_SIZE = 40
HOTBAR_SLOTS = 10
HOTBAR_HEIGHT = 100

# Цвета
SELECTED_COLOR = (192, 192, 192, 255)
HOTBAR_COLOR = (64, 64, 64, 100)
SLOT_BG_COLOR = (64, 64, 64, 130)
SLOT_BORDER_COLOR = (100, 100, 100, 255)


class Side(enum.Enum):
    LEFT = 0
    RIGHT = 1


class InventorySlot:
    """Слот инвентаря"""

    def __init__(self, x: float, y: float, size: int = BLOCK_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.block_name = None
        self.selected = False
        self.count = 0
        self.width, self.height = self.size + 10, self.size + 10
        self.texture = None

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
        arcade.draw_lbwh_rectangle_filled(self.x, self.y, self.width, self.height, SLOT_BG_COLOR)

        # Граница
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
            self.score_text.draw()


class InventorySystem:
    """Система инвентаря"""

    def __init__(self, window):
        self.window = window
        self.slots = []
        self.selected_slot = 0
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

    def add_block(self, name_block):
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

    def get_selected_block(self):
        """Получение выбранного блока"""
        slot = self.slots[self.selected_slot]
        return slot.block_name if slot else None

    def remove_block(self, x, y, game_window=None):
        """Удаление блока из слота и его установка в мире"""
        slot = self.slots[self.selected_slot]

        if slot.block_name and slot.count > 0:
            # Если передан game_window, пытаемся поставить блок
            if game_window:
                # Проверяем, есть ли блоки рядом (чтобы нельзя было ставить блоки в воздухе)
                nearby_blocks = arcade.get_sprites_at_point(
                    (x, y - 32),  # Проверяем блок снизу
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x + 32, y),  # Проверяем блок справа
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x - 32, y),  # Проверяем блок слева
                    game_window.all_blocks
                ) or arcade.get_sprites_at_point(
                    (x, y + 32),  # Проверяем блок сверху
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
        self.scale = 2
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


class Hero(arcade.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.is_walking = False
        self.current_side = Side.RIGHT
        self.texture_idle = arcade.load_texture(
            ":resources:/images/animated_characters/male_person/malePerson_idle.png")
        self.texture = self.texture_idle
        self.walk_animation = []
        for i in range(0, 8):
            self.walk_animation.append(
                arcade.load_texture(f":resources:/images/animated_characters/male_person/malePerson_walk{i}.png"))
        self.animation_update_speed = 0.15
        self.animation_counter = 0
        self.cur_texture_index = 0
        self.speed = speed
        self.dx = 0
        self.dy = 0

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
            self.texture = self.walk_animation[self.cur_texture_index] if self.current_side == Side.RIGHT else \
                self.walk_animation[self.cur_texture_index].flip_horizontally()
        else:
            self.texture = self.texture_idle


class GridGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, antialiasing=True)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Камеры: мир и GUI
        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()  # Камера для объектов интерфейса

        # Данные уровня
        self.tile_map = None

        # Слои с нашими спрайтами
        self.player_list = arcade.SpriteList()

        # Игрок
        self.player = None

        # Границы мира (по карте)
        self.world_width = None
        self.world_height = None

        self.is_jumping = False
        self.can_jump = False

        # Ссылки на спрайт-листы
        self.earth_list = None
        self.stone_list = None
        self.coal_list = None
        self.iron_list = None
        self.gold_list = None
        self.diamonds_list = None
        self.wood_list = None
        self.flowers_list = None
        self.foliage_list = None
        self.collisions_list = None
        self.player_list = None
        self.first_blocks_hit_list = arcade.SpriteList()

        self.all_blocks = arcade.SpriteList()

        self.is_breaking_block = False

        # Продолжительность удержания
        self.hold_duration = 10

        # Система инвентаря
        self.inventory = InventorySystem(self)

        self.sound_player = None

    def setup(self):

        # СОЗДАЕМ И СОХРАНЯЕМ ВСЕ СПРАЙТ-ЛИСТЫ
        self.create_sprite_lists()

        # СОЗДАЕМ ИГРОКА
        self.player = Hero(200, 700, 200)
        self.player.scale = 0.4
        self.player_list.append(self.player)

        # Уточняем размеры мира по карте
        self.world_width = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
        self.world_height = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)

        # Физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.collisions_list,
            gravity_constant=GRAVITY
        )

        # Загрузка музыки
        self.grass_sound = arcade.load_sound("music/grass.mp3")
        self.grass2_sound = arcade.load_sound("music/grass2.mp3")
        self.wood_sound = arcade.load_sound("music/wood.mp3")
        self.stone_sound = arcade.load_sound("music/stone.mp3")

    def create_sprite_lists(self):
        """Создание всех спрайт-листов"""
        # Создаем каждый спрайт-лист отдельно
        # Загружаем уровень из TMX-файла
        self.tile_map = arcade.load_tilemap("test_map_minecraft.tmx", scaling=TILE_SCALING)
        self.earth_list = self.tile_map.sprite_lists["earth"]
        self.stone_list = self.tile_map.sprite_lists["stone"]
        self.coal_list = self.tile_map.sprite_lists["coal"]
        self.iron_list = self.tile_map.sprite_lists["iron"]
        self.gold_list = self.tile_map.sprite_lists["gold"]
        self.diamonds_list = self.tile_map.sprite_lists["diamonds"]
        self.wood_list = self.tile_map.sprite_lists["wood"]
        self.flowers_list = self.tile_map.sprite_lists["flowers"]
        self.foliage_list = self.tile_map.sprite_lists["foliage"]
        self.collisions_list = self.tile_map.sprite_lists["collisions"]
        self.player_list = arcade.SpriteList()
        self.cracks_list = arcade.SpriteList()

        self.all_blocks.extend(
            [*self.earth_list, *self.stone_list, *self.coal_list,
             *self.iron_list, *self.gold_list,
             *self.collisions_list, *self.wood_list, *self.flowers_list, *self.foliage_list,
             *self.diamonds_list])

        self.name_blocks = ['self.earth_list', 'self.stone_list', 'self.coal_list', 'self.iron_list',
                            'self.gold_list', 'self.diamonds_list', 'self.wood_list',
                            'self.flowers_list', 'self.foliage_list']

        # self.update_all_blocks_list()

    def on_draw(self):
        """Отрисовка экрана."""
        self.clear()

        # 1) Мир
        self.world_camera.use()
        self.earth_list.draw()
        self.stone_list.draw()
        self.coal_list.draw()
        self.iron_list.draw()
        self.gold_list.draw()
        self.diamonds_list.draw()
        self.wood_list.draw()
        self.flowers_list.draw()
        self.foliage_list.draw()
        self.cracks_list.draw()

        self.player_list.draw()

        # 2) GUI
        self.gui_camera.use()

        # Отрисовка инвентаря
        self.inventory.draw()

    def on_update(self, dt: float):
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
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (smooth_x, smooth_y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        # изменение координат с учётом движения камеры
        x, y = self.world_camera.unproject((x, y))[0], self.world_camera.unproject((x, y))[1]
        if button == arcade.MOUSE_BUTTON_LEFT:
            # проверка на близость к игроку
            if (self.player.center_x - 50 <= x <= self.player.center_x + 50 and
                    self.player.center_y - 50 <= y <= self.player.center_y + 50):
                # добавляем в список все нажатые блоки
                self.first_blocks_hit_list = arcade.get_sprites_at_point((x, y), self.all_blocks)

                for block in self.first_blocks_hit_list:
                    for name in self.name_blocks:
                        # по имени находим информацию о блоке
                        if block in eval(name):
                            self.name = name[5:-5]

                            if not self.sound_player:
                                music = BLOCKS_DATA[self.name][1]
                                self.sound_player = arcade.play_sound(
                                    eval(f'self.{music}_sound'),
                                    loop=True)
                            self.time_digging = BLOCKS_DATA[self.name][0]
                            speed_animation_digging = BLOCKS_DATA[self.name][2]

                            # создаём трещину
                            crack = Crack(block.center_x, block.center_y,
                                          self.time_digging / speed_animation_digging)
                            self.is_breaking_block = True
                            self.cracks_list.append(crack)
                            self.press_time = time.time()
        if button == arcade.MOUSE_BUTTON_RIGHT:
            if (self.player.center_x - 70 <= x <= self.player.center_x + 70 and
                    self.player.center_y - 70 <= y <= self.player.center_y + 70):
                self.inventory.remove_block(x, y, self)

    def on_mouse_motion(self, x, y, dx, dy):
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
        arcade.stop_sound(self.sound_player)
        self.sound_player = None

        if self.hold_duration > self.time_digging:
            self.hold_duration = 10
            for crack in self.cracks_list:
                crack.remove_from_sprite_lists()
            for block in self.first_blocks_hit_list:
                if block not in self.collisions_list:
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

        # прыжок
        if key in (arcade.key.W, arcade.key.UP):
            if self.physics_engine.can_jump():
                self.player.dy = 4

        # движение
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.dx = -1
            self.player.is_walking = True
            self.player.current_side = Side.LEFT
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.player.dx = 1
            self.player.is_walking = True
            self.player.current_side = Side.RIGHT

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

    def create_block_at_position(self, block_name, x, y):
        """Создает блок в указанной позиции"""
        # Преобразуем координаты в координаты сетки
        actual_tile_size = self.tile_map.tile_width * TILE_SCALING
        grid_x1 = round(x / actual_tile_size) * actual_tile_size + 16
        grid_x2 = round(x / actual_tile_size) * actual_tile_size - 16
        grid_x = grid_x1 if abs(x - grid_x1) < abs(x - grid_x2) else grid_x2
        grid_y1 = round(y / actual_tile_size) * actual_tile_size + 16
        grid_y2 = round(y / actual_tile_size) * actual_tile_size - 16
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

        collision_block = arcade.Sprite(
            f"minecraft_blocks/Border_29_EE1.webp",
            scale=TILE_SCALING
        )
        collision_block.center_x = grid_x
        collision_block.center_y = grid_y

        # Добавляем блок в соответствующий список
        if block_name == 'earth':
            self.earth_list.append(block)
            self.collisions_list.append(collision_block)
        elif block_name == 'stone':
            self.stone_list.append(block)
            self.collisions_list.append(collision_block)
            self.collisions_list.append(collision_block)
        # elif block_name == 'coal':
        #     self.coal_list.append(block)
        # elif block_name == 'iron':
        #     self.iron_list.append(block)
        # elif block_name == 'gold':
        #     self.gold_list.append(block)
        # elif block_name == 'diamonds':
        #     self.diamonds_list.append(block)
        elif block_name == 'wood':
            self.wood_list.append(block)
            self.collisions_list.append(collision_block)
        elif block_name == 'flowers':
            self.flowers_list.append(block)
        elif block_name == 'foliage':
            self.foliage_list.append(block)

        # Обновляем общий список всех блоков
        self.update_all_blocks_list()

        return True

    def update_all_blocks_list(self):
        """Обновляет общий список всех блоков"""
        self.all_blocks.clear()
        self.all_blocks.extend(
            [*self.earth_list, *self.stone_list, *self.coal_list,
             *self.iron_list, *self.gold_list,
             *self.collisions_list, *self.wood_list, *self.flowers_list, *self.foliage_list,
             *self.diamonds_list])


def main():
    game = GridGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
