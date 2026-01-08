import arcade
import math
import enum


# ---------- Окно и мир ----------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Maincraft"
TILE_SCALING = 0.2

# ---------- Камера ----------
CAMERA_LERP = 0.12
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)

GRAVITY = 0.8


class Side(enum.Enum):
    LEFT = 0
    RIGHT = 1


class Hero(arcade.Sprite):
    def __init__(self, x, y, speed, color=arcade.color.SKY_BLUE):
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
        self.color = color
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
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.is_jumping = False
        self.can_jump = False

    def setup(self):
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

        # Уточняем размеры мира по карте
        self.world_width = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
        self.world_height = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)

        # Делаем игрока
        self.player = Hero(200, 700, 200)
        self.player.scale = 0.4

        self.player_list.append(self.player)

        # Физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.collisions_list,
            gravity_constant=GRAVITY
        )

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

        self.player_list.draw()

        # 2) GUI
        self.gui_camera.use()

        arcade.draw_lrbt_rectangle_outline(
            self.world_camera.position[0] - DEAD_ZONE_W // 2,
            self.world_camera.position[0] + DEAD_ZONE_W // 2,
            self.world_camera.position[1] - DEAD_ZONE_H // 2,
            self.world_camera.position[1] + DEAD_ZONE_H // 2,
            arcade.color.AMBER, 2
        )

    def on_update(self, dt: float):
        self.player_list.update_animation(dt)
        self.player_list.update(dt)

        self.can_jump = self.physics_engine.can_jump()

        if not self.player:
            return
        self.physics_engine.update()

        position = (
            self.player.center_x,
            self.player.center_y
        )

        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            CAMERA_LERP,  # Плавность следования камеры
        )

        # # Камера: мёртвая зона + плавное следование
        # cam_x, cam_y = self.world_camera.position
        # dz_left = cam_x - DEAD_ZONE_W // 2
        # dz_right = cam_x + DEAD_ZONE_W // 2
        # dz_bottom = cam_y - DEAD_ZONE_H // 2
        # dz_top = cam_y + DEAD_ZONE_H // 2
        #
        # px, py = self.player.center_x, self.player.center_y
        # target_x, target_y = cam_x, cam_y
        #
        # if px < dz_left:
        #     target_x = px + DEAD_ZONE_W // 2
        # elif px > dz_right:
        #     target_x = px - DEAD_ZONE_W // 2
        # if py < dz_bottom:
        #     target_y = py + DEAD_ZONE_H // 2
        # elif py > dz_top:
        #     target_y = py - DEAD_ZONE_H // 2
        #
        # # Не показываем «пустоту» за краями карты
        # half_w = self.world_camera.viewport_width / 2
        # half_h = self.world_camera.viewport_height / 2
        # target_x = max(half_w, min(self.world_width - half_w, target_x))
        # target_y = max(half_h, min(self.world_height - half_h, target_y))
        #
        # # Плавно к цели, аналог arcade.math.lerp_2d, но руками
        # smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        # smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        # self.cam_target = (smooth_x, smooth_y)
        #
        #
        # self.world_camera.position = (self.cam_target[0], self.cam_target[1])

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
