import arcade
import math
import enum
import time
import csv

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Maincraft"
TILE_SCALING = 0.2

CAMERA_LERP = 0.12
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)

GRAVITY = 0.8

BLOCKS_DATA = {
    'earth': [0.8, 'grass', 16],
    'stone': [4, 'stone', 8],
    'coal': [6, 'stone', 3],
'iron': [12, 'stone', 1],
    'gold': [18, 'stone', 0.5],
'diamonds': [25, 'stone', 0.2],
    'wood': [3, 'wood', 10],
'flowers': [0.5, 'grass', 21],
    'foliage': [0.2, 'grass2', 25],
}


class Side(enum.Enum):
    LEFT = 0
    RIGHT = 1


class Crack(arcade.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.texture_idle = arcade.load_texture(
            "cracks/crack_6.png")
        self.texture = self.texture_idle
        self.cracking_animation = []
        for i in range(5, 0, -1):
            self.cracking_animation.append(
                arcade.load_texture(f"cracks/crack_{i}.png"))
        self.texture_change_time = 0
        self.texture_change_delay = speed
        self.current_texture = 0
        self.scale = 0.032
        self.is_breaking_block = True

    def update_animation(self, delta_time: float = 1 / 60):
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
        self.mining_target = None

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

        self.hold_duration = 10
        self.time_digging = 1
        self.speed_animation_digging = 16

    def setup(self):

        # 2. СОЗДАЕМ И СОХРАНЯЕМ ВСЕ СПРАЙТ-ЛИСТЫ
        self.create_sprite_lists()

        # 3. СОЗДАЕМ ИГРОКА
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

        self.grass_sound = arcade.load_sound("music/grass.mp3")
        self.grass2_sound = arcade.load_sound("music/grass2.mp3")
        self.wood_sound = arcade.load_sound("music/wood.mp3")
        self.stone_sound = arcade.load_sound("music/stone.mp3")

    def create_sprite_lists(self):
        """Создание всех спрайт-листов"""
        # Создаем каждый спрайт-лист отдельно
        # Загружаем уровень из TMX-файла
        self.tile_map = arcade.load_tilemap("test_map_maincraft.tmx", scaling=TILE_SCALING)
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

    def on_update(self, dt: float):
        self.player_list.update_animation(dt)
        self.player_list.update(dt)

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

        self.can_jump = self.physics_engine.can_jump()

        if not self.player:
            return
        self.physics_engine.update()

        cam_x, cam_y = self.world_camera.position

        # Не показываем «пустоту» за краями карты
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.world_width - half_w, self.player.center_x))
        target_y = max(half_h, min(self.world_height - half_h, self.player.center_y))

        # Плавно к цели, аналог arcade.math.lerp_2d, но руками
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (smooth_x, smooth_y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            x, y = self.world_camera.unproject((x, y))[0], self.world_camera.unproject((x, y))[1]
            if (self.player.center_x - 50 <= x <= self.player.center_x + 50 and
                    self.player.center_y - 50 <= y <= self.player.center_y + 50):
                self.first_blocks_hit_list = arcade.get_sprites_at_point((x, y), self.all_blocks)[:2]

                for block in self.first_blocks_hit_list:
                    for name in self.name_blocks:
                        if block in eval(name):
                            name = name[5:-5]
                            music = BLOCKS_DATA[name][1]
                            self.sound_player = arcade.play_sound(
                                eval(f'self.{music}_sound'),
                                loop=True)
                            self.time_digging = BLOCKS_DATA[name][0]
                            speed_animation_digging = BLOCKS_DATA[name][2]

                            crack = Crack(block.center_x, block.center_y,
                                          self.time_digging / speed_animation_digging)
                            self.is_breaking_block = True
                            self.cracks_list.append(crack)
                            self.press_time = time.time()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.is_breaking_block:
            x, y = self.world_camera.unproject((x, y))[0], self.world_camera.unproject((x, y))[1]
            blocks_hit_list = arcade.get_sprites_at_point((x, y), self.all_blocks)
            for block in blocks_hit_list:
                if block not in self.first_blocks_hit_list:
                    self.remove_blocks_and_cracks()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.is_breaking_block:
            self.remove_blocks_and_cracks()

    def remove_blocks_and_cracks(self):
        release_time = time.time()
        self.hold_duration = release_time - self.press_time
        self.is_breaking_block = False
        arcade.stop_sound(self.sound_player)

        if self.hold_duration > self.time_digging:
            self.hold_duration = 10
            for crack in self.cracks_list:
                crack.remove_from_sprite_lists()
            for block in self.first_blocks_hit_list:
                block.remove_from_sprite_lists()

        for crack in self.cracks_list:
            crack.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            if self.can_jump:
                self.player.dy = 4
                self.is_jumping = True

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


def main():
    game = GridGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
