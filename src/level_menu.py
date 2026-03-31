import pygame
from src.button import Button


class LevelMenu:
    def __init__(self, screen_width, screen_height, game_mode, click_sound=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_mode = game_mode
        self.click_sound = click_sound
        self.font = pygame.font.Font(None, 56)
        self.small_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 30)

        if game_mode == 'time':
            self.title_text = "ВЫБЕРИТЕ УРОВЕНЬ (ВРЕМЯ)"
            self.mode_description = "Наберите максимум очков за отведённое время"
        else:
            self.title_text = "ВЫБЕРИТЕ УРОВЕНЬ (ОЧКИ)"
            self.mode_description = "Достигните целевого счёта уровня"

        self.title_color = (255, 180, 200)
        self.button_color = (255, 180, 200)
        self.button_hover = (255, 200, 215)
        self.desc_color = (255, 180, 200)

        # Кнопки уровней (2 ряда: 3 + 2)
        self.buttons = {}
        button_width = 150
        button_height = 60
        gap = 30

        # Первый ряд (уровни 1-3)
        row1_y = 250
        total_width_row1 = (button_width * 3) + (gap * 2)
        start_x_row1 = (screen_width - total_width_row1) // 2

        for i in range(3):
            level_num = i + 1
            x = start_x_row1 + i * (button_width + gap)
            self.buttons[level_num] = Button(
                x, row1_y, button_width, button_height,
                f"Уровень {level_num}",
                self.button_color, self.button_hover,
                text_color=(255, 255, 255),
                click_sound=click_sound
            )

        # Второй ряд (уровни 4-5)
        row2_y = 340
        total_width_row2 = (button_width * 2) + gap
        start_x_row2 = (screen_width - total_width_row2) // 2

        for i in range(2):
            level_num = i + 4
            x = start_x_row2 + i * (button_width + gap)
            self.buttons[level_num] = Button(
                x, row2_y, button_width, button_height,
                f"Уровень {level_num}",
                self.button_color, self.button_hover,
                text_color=(255, 255, 255),
                click_sound=click_sound
            )

        self.back_button = Button(50, screen_height - 80, 150, 50,
                                  "Назад", (144, 22, 75), (222, 68, 135),
                                  click_sound=click_sound)

        self.level_params = {
            1: {'time': 60, 'target': 1000},
            2: {'time': 90, 'target': 2000},
            3: {'time': 120, 'target': 3500},
            4: {'time': 150, 'target': 5000},
            5: {'time': 180, 'target': 7500}
        }

        self.selected_level = None

    def draw(self, screen, background=None):
        """Отрисовка меню выбора уровней"""
        # Рисуем фон только если передан (иначе фон уже нарисован в main.py)
        if background:
            screen.blit(background, (0, 0))
        # Если background=None — не рисуем ничего, фон уже есть

        # Заголовок
        title = self.font.render(self.title_text, True, self.title_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        # Подзаголовок
        subtitle = self.small_font.render(self.mode_description, True, self.title_color)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 130))
        screen.blit(subtitle, subtitle_rect)

        # Кнопки уровней
        for button in self.buttons.values():
            button.draw(screen)

        # Описание параметров под уровнями
        for i in range(3):
            level_num = i + 1
            button = self.buttons[level_num]
            center_x = button.rect.centerx
            y_offset = button.rect.bottom + 15

            params = self.level_params[level_num]
            if self.game_mode == 'time':
                desc = f"{params['time']} сек"
            else:
                desc = f"{params['target']} очков"

            text = self.desc_font.render(desc, True, self.desc_color)
            text_rect = text.get_rect(center=(center_x, y_offset))
            screen.blit(text, text_rect)

        for i in range(2):
            level_num = i + 4
            button = self.buttons[level_num]
            center_x = button.rect.centerx
            y_offset = button.rect.bottom + 15

            params = self.level_params[level_num]
            if self.game_mode == 'time':
                desc = f"{params['time']} сек"
            else:
                desc = f"{params['target']} очков"

            text = self.desc_font.render(desc, True, self.desc_color)
            text_rect = text.get_rect(center=(center_x, y_offset))
            screen.blit(text, text_rect)

        # Кнопка назад
        self.back_button.draw(screen)

    def handle_event(self, event):
        for level_num, button in self.buttons.items():
            if button.is_clicked(event):
                self.selected_level = level_num
                return level_num

        if self.back_button.is_clicked(event):
            return 'back'

        return None

    def get_level_params(self, level):
        if level in self.level_params:
            params = self.level_params[level]
            if self.game_mode == 'time':
                return {'time': params['time'], 'target': None}
            else:
                return {'time': None, 'target': params['target']}
        return None