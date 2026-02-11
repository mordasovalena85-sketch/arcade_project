import os

import arcade

from arcade import Text

from arcade.gui import (UIManager, UIAnchorLayout, UIBoxLayout,
                        UITextureButton, UILabel, UIDropdown, UISlider)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

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
            bold=True
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
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Menu")

        self.music_sound = None
        self.music_player = None
        self.is_playing = False

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

        self.skin = 'Stive'


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

        dropdown_default_style = arcade.gui.UISlider.UIStyle(
            border=arcade.color.GRAY,
            bg=(92, 92, 92)
        )
        dropdown_hover_style = arcade.gui.UISlider.UIStyle(
            border=arcade.color.LIGHT_GRAY,
            bg=(92, 92, 92)
        )
        style_dict = {
            "press": dropdown_default_style,
            "normal": dropdown_default_style,
            "hover": dropdown_hover_style,
            "disabled": dropdown_default_style
        }

        self.dropdown = UIDropdown(options=["Stive", "Alex"], width=200,
                              dropdown_style=style_dict, active_style=style_dict, primary_style=style_dict,
                                   default="Stive")

        self.dropdown.on_change = self.choose_skin
        self.box_layout.add(self.dropdown)

        label = UILabel(text="Громкость:",
                        font_size=15,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        slider_default_style = arcade.gui.UISlider.UIStyle(
            filled_track=arcade.color.GRAY,
            unfilled_track=arcade.color.LIGHT_GRAY,
            border=arcade.color.GRAY,
            bg=(92, 92, 92)
        )
        slider_hover_style = arcade.gui.UISlider.UIStyle(
            filled_track=arcade.color.GRAY,
            unfilled_track=arcade.color.LIGHT_GRAY,
            border=arcade.color.LIGHT_GRAY,
            bg=(92, 92, 92)
        )
        slider_style_dict = {
            "press": slider_default_style,
            "normal": slider_default_style,
            "hover": slider_hover_style,
            "disabled": slider_default_style
        }

        self.slider = UISlider(width=200, height=20, min_value=0, max_value=8, value=1, style=slider_style_dict)
        self.slider.on_change = self.set_volume
        self.box_layout.add(self.slider)

        self.music_sound = arcade.load_sound('music/background_music.wav')
        self.play(self.slider.value)

    def play(self, volume):
        """Запускает музыку на повторе"""
        if self.music_player:
            arcade.stop_sound(self.music_player)
        # Запускаем с текущей громкостью
        self.music_player = arcade.play_sound(
                self.music_sound,
                volume=volume,
                loop=True  # Постоянный повтор
            )

    def set_volume(self, event=None):
        """Устанавливает громкость и перезапускает музыку"""
        # Перезапускаем с новой громкостью
        self.play(event.new_value)


    def choose_skin(self, event=None):
        selected_option = self.dropdown.value
        self.skin = selected_option

    def new_game(self, event=None):
        from main import GameWindow
        super().on_close()
        arcade.stop_sound(self.music_player)
        self.game_window = GameWindow(self.skin, self.slider.value)
        if os.path.exists(self.game_window.save_file):
            os.remove(self.game_window.save_file)
        self.game_window.setup()
        arcade.run()

    def start_game(self, event=None):
        # Закрываем меню и открываем игровое окно
        from main import GameWindow  # Импортируем здесь, чтобы избежать циклического импорта
        super().on_close()
        arcade.stop_sound(self.music_player)
        self.game_window = GameWindow(self.skin, self.slider.value)
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



class PauseScreen:
    """Класс для экрана паузы"""

    def __init__(self, window):
        self.window = window
        self.is_visible = False

        # Позиция и размеры кнопок
        self.button_width = 300
        self.button_height = 50
        self.button_spacing = 70

        # Цвета
        self.background_color = (0, 0, 0, 180)  # Полупрозрачный черный
        self.title_color = arcade.color.GOLD
        self.text_color = arcade.color.WHITE
        self.button_color = (145, 145, 145)
        self.button_hover_color = (200, 200, 200)
        self.button_border_color = (79, 79, 79)

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
            self.window.save_game()
            return True

        if self._is_point_in_button(x, y, center_x, craft_y):
            return True

        if self._is_point_in_button(x, y, center_x, exit_y):
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