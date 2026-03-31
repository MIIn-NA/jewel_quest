import pygame
from src.button import Button


class Menu:
    def __init__(self, screen_width, screen_height, click_sound=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.click_sound = click_sound
        self.font = pygame.font.Font(None, 56)
        self.small_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 28)

        # Создаём кнопки меню
        button_width = 300
        button_height = 60
        start_x = (screen_width - button_width) // 2

        # Кнопки главного меню
        self.buttons = {
            'start': Button(start_x, 200, button_width, button_height,
                            "Начать игру", (222, 68, 135), (238, 114, 168),
                            click_sound=click_sound),

            'scores': Button(start_x, 280, button_width, button_height,
                             "Таблица рекордов", (238, 114, 168), (238, 147, 187),
                             click_sound=click_sound),

            'help': Button(start_x, 360, button_width, button_height,
                           "Справка", (144, 22, 75), (222, 68, 135),
                           click_sound=click_sound),

            'exit': Button(start_x, 440, button_width, button_height,
                           "Выход", (144, 22, 75), (222, 68, 135),
                           click_sound=click_sound)
        }

        # Кнопка "Назад" для других экранов
        self.back_button = Button(50, screen_height - 80, 150, 50,
                                  "Назад", (144, 22, 75), (222, 68, 135),
                                  click_sound=click_sound)

        # Текущее состояние
        self.current_screen = 'menu'

    def draw_menu(self, screen):
        """Отрисовка главного меню"""
        # Заголовок
        title = self.font.render("JEWEL QUEST", True, (255, 180, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Подзаголовок
        subtitle = self.small_font.render("Три в ряд", True, (255, 180, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 155))
        screen.blit(subtitle, subtitle_rect)

        # Кнопки
        for button in self.buttons.values():
            button.draw(screen)

    def draw_help(self, screen):
        """Отрисовка экрана справки"""
        # Заголовок
        title = self.font.render("СПРАВКА", True, (255, 180, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title, title_rect)

        # Правила игры
        rules = [
            "ПРАВИЛА ИГРЫ:",
            "",
            "1. Соединяйте 3 или более одинаковых кристалла",
            "2. Кристаллы исчезают и начисляются очки",
            "",
            "3. Режимы игры:",
            "   - По времени: наберите очки за 60 секунд",
            "     (результат сохраняется в таблицу рекордов)",
            "   - По очкам: достигните целевого счёта",
            "",
            "4. Управление:",
            "   - Кликните на кристалл для выбора",
            "   - Кликните на соседний для обмена",
            "   - ESC - возврат в меню"
        ]

        y_offset = 120
        for line in rules:
            if line == "":
                y_offset += 15
            else:
                text = self.desc_font.render(line, True, (255, 255, 255))
                screen.blit(text, (80, y_offset))
                y_offset += 32

        # Кнопка назад
        self.back_button.draw(screen)

    def draw_scores(self, screen):
        """Отрисовка таблицы рекордов (только режим времени)"""
        # Заголовок
        title = self.font.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 180, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title, title_rect)

        # Подзаголовок
        subtitle = self.desc_font.render("Режим: По времени", True, (255, 180, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(subtitle, subtitle_rect)

        # Заголовки таблицы
        headers = ["#  Имя", "Очки", "Уровень", "Дата"]
        x_positions = [80, 350, 500, 650]

        for i, header in enumerate(headers):
            text = self.desc_font.render(header, True, (255, 180, 200))
            screen.blit(text, (x_positions[i], 140))

        # Разделительная линия
        pygame.draw.line(screen, (255, 180, 200),
                         (80, 170), (800, 170), 2)

        # Загрузка рекордов
        try:
            from src.highscores import Highscores
            highscores = Highscores()
            scores = highscores.get_top_scores(10)

            if scores:
                y_offset = 190
                for i, record in enumerate(scores):
                    # Номер
                    num_text = self.desc_font.render(f"{i + 1}.", True, (255, 255, 255))
                    screen.blit(num_text, (80, y_offset))

                    # Имя
                    name_text = self.desc_font.render(record['name'], True, (255, 255, 255))
                    screen.blit(name_text, (110, y_offset))

                    # Очки
                    score_text = self.desc_font.render(str(record['score']), True, (255, 180, 200))
                    screen.blit(score_text, (350, y_offset))

                    # Уровень
                    level_text = self.desc_font.render(f"Ур.{record['level']}", True, (255, 255, 255))
                    screen.blit(level_text, (500, y_offset))

                    # Дата
                    date_text = self.desc_font.render(record['date'], True, (255, 255, 255))
                    screen.blit(date_text, (650, y_offset))

                    y_offset += 35
            else:
                text = self.small_font.render("Рекорды пока пусты...",
                                              True, (200, 200, 200))
                text_rect = text.get_rect(center=(self.screen_width // 2, 350))
                screen.blit(text, text_rect)
        except Exception as e:
            print(f"❌ Ошибка отображения рекордов: {e}")
            text = self.small_font.render("Ошибка загрузки рекордов",
                                          True, (255, 100, 100))
            text_rect = text.get_rect(center=(self.screen_width // 2, 350))
            screen.blit(text, text_rect)

        # Кнопка назад
        self.back_button.draw(screen)

    def handle_event(self, event):
        """Обработка событий (клики мыши)"""
        if self.current_screen == 'menu':
            if self.buttons['start'].is_clicked(event):
                return 'start_game'
            elif self.buttons['scores'].is_clicked(event):
                self.current_screen = 'scores'
            elif self.buttons['help'].is_clicked(event):
                self.current_screen = 'help'
            elif self.buttons['exit'].is_clicked(event):
                return 'exit'

        elif self.current_screen in ['help', 'scores']:
            if self.back_button.is_clicked(event):
                self.current_screen = 'menu'

        return None

    def draw(self, screen):
        """Отрисовка текущего экрана"""
        if self.current_screen == 'menu':
            self.draw_menu(screen)
        elif self.current_screen == 'help':
            self.draw_help(screen)
        elif self.current_screen == 'scores':
            self.draw_scores(screen)