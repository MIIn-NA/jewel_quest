import pygame
from src.button import Button


class ResultScreen:
    def __init__(self, screen_width, screen_height, is_win, score, level, mode, click_sound=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.click_sound = click_sound
        self.is_win = is_win
        self.score = score
        self.level = level
        self.mode = mode

        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 28)

        # Поле для ввода имени
        self.player_name = ""
        self.input_box = pygame.Rect(screen_width // 2 - 150, 320, 300, 40)

        # 🔥 РОЗОВЫЕ ЦВЕТА (явно заданы)
        self.input_color = (255, 180, 200)  # Розовая рамка
        self.input_text_color = (255, 180, 200)  # 🔥 Розовый текст (был белый!)

        # Цвета
        if is_win:
            self.title_color = (100, 255, 100)
            self.button_color = (100, 200, 100)
        else:
            self.title_color = (255, 180, 200)
            self.button_color = (200, 100, 100)

        # Кнопки
        button_width = 250
        button_height = 60
        start_x = (screen_width - button_width) // 2

        # РЕЖИМ ПО ВРЕМЕНИ (время вышло)
        if mode == 'time':
            self.buttons = {
                'save': Button(start_x, 380, button_width, button_height,
                               "Сохранить рекорд", self.button_color, (150, 255, 150),
                               text_color=(255, 255, 255),
                               click_sound=click_sound),
                'retry': Button(start_x, 460, button_width, button_height,
                                "Попробовать снова", (255, 180, 200), (255, 200, 215),
                                text_color=(255, 255, 255),
                                click_sound=click_sound),
                'menu': Button(start_x, 540, button_width, button_height,
                               "В главное меню", (144, 22, 75), (222, 68, 135),
                               text_color=(255, 255, 255),
                               click_sound=click_sound)
            }
        else:
            self.buttons = {
                'next': Button(start_x, 380, button_width, button_height,
                               "Следующий уровень", self.button_color, (150, 255, 150),
                               text_color=(255, 255, 255),
                               click_sound=click_sound),
                'menu': Button(start_x, 460, button_width, button_height,
                               "В главное меню", (144, 22, 75), (222, 68, 135),
                               text_color=(255, 255, 255),
                               click_sound=click_sound)
            }

    def draw(self, screen, background=None):
        """Отрисовка экрана результата"""
        # Фон
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((50, 20, 40))

        # Заголовок
        if self.is_win:
            title = self.font.render("ПОБЕДА!", True, self.title_color)
            subtitle = self.small_font.render("Уровень пройден!", True, (255, 255, 255))
        else:
            title = self.font.render("ВРЕМЯ ВЫШЛО", True, self.title_color)
            subtitle = self.small_font.render("Введи имя для рекорда", True, (255, 255, 255))

        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)

        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 210))
        screen.blit(subtitle, subtitle_rect)

        # Информация
        info_text = self.desc_font.render(f"Уровень {self.level} | Режим: {'Время' if self.mode == 'time' else 'Очки'}",
                                          True, (255, 180, 200))
        info_rect = info_text.get_rect(center=(self.screen_width // 2, 260))
        screen.blit(info_text, info_rect)

        # Счёт
        score_text = self.small_font.render(f"Твой счёт: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 300))
        screen.blit(score_text, score_rect)

        # ПОЛЕ ДЛЯ ВВОДА ИМЕНИ (только для режима времени!)
        if self.mode == 'time':
            # 1. Рисуем рамку поля (розовая)
            pygame.draw.rect(screen, self.input_color, self.input_box, 3, border_radius=10)

            # 2. Рисуем фон поля (чтобы текст был виден)
            pygame.draw.rect(screen, (50, 20, 40), self.input_box, border_radius=10)

            # 3. Получаем текст для отображения
            if self.player_name:
                name_display = self.player_name
            else:
                name_display = "Введи своё имя..."

            # 4. 🔥 Рендерим текст с РОЗОВЫМ ЦВЕТОМ (255, 180, 200)
            name_text = self.desc_font.render(name_display, True, (255, 180, 200))

            # 5. Вычисляем позицию (по центру поля)
            text_rect = name_text.get_rect(midleft=(self.input_box.x + 15, self.input_box.centery))

            # 6. Рисуем текст на экране
            screen.blit(name_text, text_rect)

            # 7. Рисуем курсор (мигающая палочка) - белый
            if self.player_name or name_display != "Введи своё имя...":
                cursor_x = text_rect.right + 3
                pygame.draw.line(screen, (255, 255, 255),
                                 (cursor_x, self.input_box.y + 8),
                                 (cursor_x, self.input_box.bottom - 8), 2)

        # Кнопки
        for button in self.buttons.values():
            button.draw(screen)

    def add_letter(self, char):
        """Добавляет символ в имя"""
        if self.mode == 'time' and len(self.player_name) < 15:
            self.player_name += char

    def remove_letter(self):
        """Удаляет последний символ"""
        if self.mode == 'time':
            self.player_name = self.player_name[:-1]

    def get_player_name(self):
        """Возвращает имя игрока"""
        return self.player_name if self.player_name else "Игрок"

    def check_button_click(self, pos):
        """Проверяет клик по кнопкам"""
        for key, button in self.buttons.items():
            if (button.rect.x <= pos[0] <= button.rect.x + button.rect.width and
                    button.rect.y <= pos[1] <= button.rect.y + button.rect.height):
                return key
        return None