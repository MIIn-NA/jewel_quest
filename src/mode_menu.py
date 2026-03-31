import pygame
from src.button import Button


class ModeMenu:
    def __init__(self, screen_width, screen_height, click_sound=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.click_sound = click_sound
        self.font = pygame.font.Font(None, 56)
        self.small_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 30)

        # Размеры кнопок
        self.button_width = 300
        self.button_height = 70

        # Позиции для горизонтального расположения
        gap = 50
        total_width = (self.button_width * 2) + gap
        start_x = (screen_width - total_width) // 2

        left_x = start_x
        right_x = start_x + self.button_width + gap
        button_y = 220

        # Цвета кнопок
        button_color = (255, 180, 200)
        button_hover = (255, 200, 215)

        self.buttons = {
            'time': Button(left_x, button_y, self.button_width, self.button_height,
                           "По времени", button_color, button_hover,
                           text_color=(255, 255, 255),
                           click_sound=click_sound),

            'score': Button(right_x, button_y, self.button_width, self.button_height,
                            "По очкам", button_color, button_hover,
                            text_color=(255, 255, 255),
                            click_sound=click_sound),

            'back': Button(50, screen_height - 80, 150, 50,
                           "Назад", (144, 22, 75), (222, 68, 135),
                           click_sound=click_sound)
        }

        self.descriptions = {
            'time': [
                "Наберите как можно больше очков",
                "за отведённое время!",
                "",
                "Время: 60 секунд",
                "Цель: макс. очков",
                "Сложность: средняя"
            ],
            'score': [
                "Достигните целевого счёта,",
                "чтобы перейти на следующий уровень!",
                "",
                "Цель: 1500 очков",
                "Уровней: 3",
                "Сложность: высокая"
            ]
        }

        self.desc_color = (255, 180, 200)
        self.title_color = (255, 180, 200)

        self.left_x = left_x
        self.right_x = right_x
        self.button_y = button_y

        self.selected_mode = None

    def draw(self, screen, background=None):
        """Отрисовка меню выбора режима"""
        # Рисуем фон только если передан (иначе фон уже нарисован в main.py)
        if background:
            screen.blit(background, (0, 0))
        # Если background=None — не рисуем ничего, фон уже есть

        # Заголовок
        title = self.font.render("ВЫБЕРИТЕ РЕЖИМ ИГРЫ", True, self.title_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Подзаголовок
        subtitle = self.small_font.render("Выберите подходящий вам режим", True, self.title_color)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 160))
        screen.blit(subtitle, subtitle_rect)

        # Кнопки
        for button in self.buttons.values():
            button.draw(screen)

        # Описания под кнопками
        left_center_x = self.left_x + self.button_width // 2
        y_offset = self.button_y + self.button_height + 25
        for line in self.descriptions['time']:
            if line == "":
                y_offset += 15
            else:
                text = self.desc_font.render(line, True, self.desc_color)
                text_rect = text.get_rect(center=(left_center_x, y_offset))
                screen.blit(text, text_rect)
                y_offset += 32

        right_center_x = self.right_x + self.button_width // 2
        y_offset = self.button_y + self.button_height + 25
        for line in self.descriptions['score']:
            if line == "":
                y_offset += 15
            else:
                text = self.desc_font.render(line, True, self.desc_color)
                text_rect = text.get_rect(center=(right_center_x, y_offset))
                screen.blit(text, text_rect)
                y_offset += 32

        # Рамка вокруг кнопок
        left_rect = pygame.Rect(self.left_x - 10, self.button_y - 10,
                                self.button_width + 20, self.button_height + 20)
        right_rect = pygame.Rect(self.right_x - 10, self.button_y - 10,
                                 self.button_width + 20, self.button_height + 20)
        pygame.draw.rect(screen, (255, 180, 200, 100), left_rect, 2, border_radius=15)
        pygame.draw.rect(screen, (255, 180, 200, 100), right_rect, 2, border_radius=15)

    def handle_event(self, event):
        if self.buttons['time'].is_clicked(event):
            self.selected_mode = 'time'
            return 'time'
        elif self.buttons['score'].is_clicked(event):
            self.selected_mode = 'score'
            return 'score'
        elif self.buttons['back'].is_clicked(event):
            return 'back'
        return None

    def get_selected_mode(self):
        return self.selected_mode