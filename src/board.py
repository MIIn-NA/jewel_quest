import pygame
import random
from src.gem import Gem


class Board:
    def __init__(self, rows=8, cols=8, gem_size=60, screen_width=1024, screen_height=768):
        self.rows = rows
        self.cols = cols
        self.gem_size = gem_size

        # Центрирование сетки
        board_width = cols * gem_size
        board_height = rows * gem_size
        self.offset_x = (screen_width - board_width) // 2
        self.offset_y = (screen_height - board_height) // 2

        # Двумерный массив кристаллов
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

        # Для обмена
        self.selected_gem = None
        self.is_swapping = False
        self.is_processing = False

        # Для подсчёта очков
        self.score = 0

        # Для специальных кристаллов
        self.pending_bomb_gem = None
        self.pending_line_gem = None
        self.pending_rainbow_gem = None
        self.rainbow_target_color = None  # 🌈 Цвет для активации радуги

        # Заполняем поле
        self.fill_board()

    def fill_board(self):
        """Заполняет поле кристаллами без начальных совпадений"""
        for row in range(self.rows):
            for col in range(self.cols):
                color_id = random.randint(0, 5)

                while self.would_match(row, col, color_id):
                    color_id = random.randint(0, 5)

                x = self.offset_x + col * self.gem_size
                y = self.offset_y + row * self.gem_size

                self.grid[row][col] = Gem(x, y, row, col, color_id, self.gem_size)

    def would_match(self, row, col, color_id):
        """Проверяет, создаст ли этот цвет совпадение"""
        if col >= 2:
            if (self.grid[row][col - 1] and self.grid[row][col - 1].color_id == color_id and
                    self.grid[row][col - 2] and self.grid[row][col - 2].color_id == color_id):
                return True

        if row >= 2:
            if (self.grid[row - 1][col] and self.grid[row - 1][col].color_id == color_id and
                    self.grid[row - 2][col] and self.grid[row - 2][col].color_id == color_id):
                return True

        return False

    def find_matches(self):
        """Ищет все совпадения 3+ в ряд"""
        matches = set()

        # Проверка по горизонтали
        for row in range(self.rows):
            for col in range(self.cols - 2):
                gem = self.grid[row][col]
                if gem and not gem.matched:
                    if (self.grid[row][col + 1] and gem.color_id == self.grid[row][col + 1].color_id and
                            self.grid[row][col + 2] and gem.color_id == self.grid[row][col + 2].color_id):
                        matches.add((row, col))
                        matches.add((row, col + 1))
                        matches.add((row, col + 2))

                        for k in range(col + 3, self.cols):
                            if self.grid[row][k] and gem.color_id == self.grid[row][k].color_id:
                                matches.add((row, k))
                            else:
                                break

        # Проверка по вертикали
        for col in range(self.cols):
            for row in range(self.rows - 2):
                gem = self.grid[row][col]
                if gem and not gem.matched:
                    if (self.grid[row + 1][col] and gem.color_id == self.grid[row + 1][col].color_id and
                            self.grid[row + 2][col] and gem.color_id == self.grid[row + 2][col].color_id):
                        matches.add((row, col))
                        matches.add((row + 1, col))
                        matches.add((row + 2, col))

                        for k in range(row + 3, self.rows):
                            if self.grid[k][col] and gem.color_id == self.grid[k][col].color_id:
                                matches.add((k, col))
                            else:
                                break

        return list(matches)

    def create_bomb_gem(self, row, col, color_id):
        """Создаёт кристалл-бомбу"""
        bomb = Gem(self.offset_x + col * self.gem_size,
                   self.offset_y + row * self.gem_size,
                   row, col, color_id, self.gem_size, 'bomb')
        return bomb

    def create_line_gem(self, row, col, color_id, direction):
        """Создаёт линейный кристалл"""
        line = Gem(self.offset_x + col * self.gem_size,
                   self.offset_y + row * self.gem_size,
                   row, col, color_id, self.gem_size, 'line')
        line.direction = direction
        return line

    def create_rainbow_gem(self, row, col, color_id):
        """Создаёт радужный кристалл"""
        rainbow = Gem(self.offset_x + col * self.gem_size,
                      self.offset_y + row * self.gem_size,
                      row, col, color_id, self.gem_size, 'rainbow')
        print(f"🌈 Радужный создан на ({row}, {col})!")
        return rainbow

    def activate_bomb(self, bomb_gem, sound_manager=None):
        """💣 Активирует бомбу — взрывает 3×3 вокруг"""
        exploded = 0
        row = bomb_gem.row
        col = bomb_gem.col

        print(f"💥💥💥 АКТИВАЦИЯ БОМБЫ на ({row}, {col})!")

        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.grid[r][c]:
                    self.grid[r][c].matched = True
                    exploded += 1

        print(f"💣 Бомба взорвалась! Уничтожено кристаллов: {exploded}")

        if sound_manager:
            sound_manager.play_match(0.6)

        return exploded

    def activate_line(self, line_gem, sound_manager=None):
        """⚡ Активирует линейный кристалл"""
        destroyed = 0
        row = line_gem.row
        col = line_gem.col
        direction = getattr(line_gem, 'direction', 'h')

        print(f"⚡⚡⚡ АКТИВАЦИЯ ЛИНЕЙНОГО на ({row}, {col}) направление: {direction}")

        if direction == 'h':
            for c in range(self.cols):
                if self.grid[row][c]:
                    self.grid[row][c].matched = True
                    destroyed += 1
        else:
            for r in range(self.rows):
                if self.grid[r][col]:
                    self.grid[r][col].matched = True
                    destroyed += 1

        print(f"⚡ Линейный активирован! Уничтожено кристаллов: {destroyed}")

        if sound_manager:
            sound_manager.play_combo(0.6)

        return destroyed

    def activate_rainbow(self, target_color, sound_manager=None):
        """🌈 Активирует радужный — удаляет ВСЕ кристаллы ЦЕЛЕВОГО ЦВЕТА"""
        destroyed = 0

        print(f"🌈🌈🌈 АКТИВАЦИЯ РАДУЖНОГО! Удаляем все кристаллы цвета {target_color}!")

        for row in range(self.rows):
            for col in range(self.cols):
                gem = self.grid[row][col]
                if gem and gem.color_id == target_color:
                    gem.matched = True
                    destroyed += 1
                    print(f"  🌈 Удалён кристалл цвета {target_color} на ({row}, {col})")

        print(f"🌈 Радужный активирован! Уничтожено кристаллов: {destroyed}")

        if sound_manager:
            sound_manager.play_win(0.8)

        return destroyed

    def check_and_activate_special_in_matches(self, matches, sound_manager=None):
        """🔥 Проверяет и активирует специальные кристаллы в совпадениях"""
        bombs_activated = 0
        lines_activated = 0
        rainbows_activated = 0
        points = 0

        for row, col in matches:
            gem = self.grid[row][col]
            if gem:
                if gem.gem_type == 'bomb':
                    bombs_activated += 1
                    points += self.activate_bomb(gem, sound_manager)
                elif gem.gem_type == 'line':
                    lines_activated += 1
                    points += self.activate_line(gem, sound_manager)
                elif gem.gem_type == 'rainbow':
                    rainbows_activated += 1
                    # 🌈 Для радуги используем сохранённый цвет
                    if self.rainbow_target_color is not None:
                        points += self.activate_rainbow(self.rainbow_target_color, sound_manager)
                    else:
                        points += self.activate_rainbow(gem.color_id, sound_manager)

        return bombs_activated, lines_activated, rainbows_activated, points

    def remove_matches(self, matches, sound_manager=None):
        """Удаляет совпадения и создаёт специальные кристаллы"""
        points = 0
        special_created = None
        special_pos = None

        # 🔥 Сначала активируем специальные кристаллы в совпадениях
        bombs_activated, lines_activated, rainbows_activated, special_points = self.check_and_activate_special_in_matches(
            matches, sound_manager)
        points += special_points

        # Помечаем обычные кристаллы как matched
        for row, col in matches:
            gem = self.grid[row][col]
            if gem and gem.gem_type not in ['bomb', 'line', 'rainbow']:
                gem.matched = True
                points += 10

        # 🔥 ПРАВИЛА СОЗДАНИЯ СПЕЦИАЛЬНЫХ:
        if len(matches) >= 4:
            avg_row = sum(r for r, c in matches) // len(matches)
            avg_col = sum(c for r, c in matches) // len(matches)
            color_id = self.grid[avg_row][avg_col].color_id if self.grid[avg_row][avg_col] else 0

            rows_in_match = len(set(r for r, c in matches))
            cols_in_match = len(set(c for r, c in matches))

            # 🌈 5+ в ряд = РАДУЖНЫЙ
            if len(matches) >= 5:
                special_created = 'rainbow'
                special_pos = (avg_row, avg_col, color_id, None)
                print(f"🌈 5+ в ряд! Создаётся РАДУЖНЫЙ!")
            # 4 в ряд — проверяем направление
            elif len(matches) == 4:
                if cols_in_match > rows_in_match:
                    special_created = 'bomb'
                    special_pos = (avg_row, avg_col, color_id, None)
                    print(f"💣 4 ГОРИЗОНТАЛЬНО! Создаётся БОМБА!")
                else:
                    special_created = 'line'
                    special_pos = (avg_row, avg_col, color_id, 'v')
                    print(f"⚡ 4 ВЕРТИКАЛЬНО! Создаётся ЛИНЕЙНЫЙ!")

        # Бонус за больше 3 в ряд
        if len(matches) > 3:
            points += (len(matches) - 3) * 5

        self.score += points

        # Создаём специальный кристалл
        if special_created and special_pos and bombs_activated == 0 and lines_activated == 0 and rainbows_activated == 0:
            row, col, color_id, direction = special_pos

            if special_created == 'bomb':
                bomb_gem = self.create_bomb_gem(row, col, color_id)
                self.grid[row][col] = bomb_gem
                print(f"💣 БОМБА создана на позиции ({row}, {col})!")
            elif special_created == 'line':
                line_gem = self.create_line_gem(row, col, color_id, direction)
                self.grid[row][col] = line_gem
                print(f"⚡ ЛИНЕЙНЫЙ создан на позиции ({row}, {col})!")
            elif special_created == 'rainbow':
                rainbow_gem = self.create_rainbow_gem(row, col, color_id)
                self.grid[row][col] = rainbow_gem
                print(f"🌈 РАДУЖНЫЙ создан на позиции ({row}, {col})!")

        # Звуки
        if len(matches) >= 5:
            if sound_manager:
                sound_manager.play_win(0.7)
        elif len(matches) >= 4:
            if sound_manager:
                sound_manager.play_combo(0.5)
        else:
            if sound_manager:
                sound_manager.play_match(0.4)

        print(f"✅ Совпадений: {len(matches)}, Очки: +{points}, Всего: {self.score}")

        return points

    def drop_gems(self, sound_manager=None):
        """Опускает кристаллы вниз и создаёт новые"""
        gems_dropped = False

        for col in range(self.cols):
            empty_spaces = 0

            for row in range(self.rows - 1, -1, -1):
                gem = self.grid[row][col]

                if gem is None or gem.matched:
                    empty_spaces += 1
                    self.grid[row][col] = None
                    gems_dropped = True
                elif empty_spaces > 0:
                    new_row = row + empty_spaces
                    self.grid[new_row][col] = gem
                    self.grid[row][col] = None
                    gem.row = new_row
                    gem.target_y = self.offset_y + gem.row * self.gem_size
                    gems_dropped = True

            for i in range(empty_spaces):
                row = i
                color_id = random.randint(0, 5)
                x = self.offset_x + col * self.gem_size
                y = self.offset_y + row * self.gem_size - (empty_spaces * self.gem_size)

                gem = Gem(x, y, row, col, color_id, self.gem_size)
                gem.target_y = self.offset_y + row * self.gem_size
                self.grid[row][col] = gem
                gems_dropped = True

        if gems_dropped and sound_manager:
            sound_manager.play_drop(0.2)

        return gems_dropped

    def draw(self, screen):
        """Рисует всё поле"""
        board_rect = pygame.Rect(
            self.offset_x - 10,
            self.offset_y - 10,
            self.cols * self.gem_size + 20,
            self.rows * self.gem_size + 20
        )
        pygame.draw.rect(screen, (255, 255, 255), board_rect, border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), board_rect, 3, border_radius=15)

        for i in range(self.rows + 1):
            y = self.offset_y + i * self.gem_size
            pygame.draw.line(screen, (220, 220, 220),
                             (self.offset_x, y),
                             (self.offset_x + self.cols * self.gem_size, y), 2)

        for i in range(self.cols + 1):
            x = self.offset_x + i * self.gem_size
            pygame.draw.line(screen, (220, 220, 220),
                             (x, self.offset_y),
                             (x, self.offset_y + self.rows * self.gem_size), 2)

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    self.grid[row][col].draw(screen)

    def update(self):
        """Обновляет все кристаллы"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    self.grid[row][col].update()

        if self.is_swapping:
            animation_done = True
            for row in range(self.rows):
                for col in range(self.cols):
                    gem = self.grid[row][col]
                    if gem:
                        if abs(gem.target_x - gem.x) > 1 or abs(gem.target_y - gem.y) > 1:
                            animation_done = False
                            break
                if not animation_done:
                    break

            if animation_done:
                self.is_swapping = False

        if self.is_processing:
            all_done = True
            for row in range(self.rows):
                for col in range(self.cols):
                    gem = self.grid[row][col]
                    if gem:
                        if abs(gem.target_x - gem.x) > 1 or abs(gem.target_y - gem.y) > 1:
                            all_done = False
                            break
                if not all_done:
                    break

            if all_done:
                matches = self.find_matches()
                if matches:
                    self.remove_matches(matches, None)
                    self.drop_gems(None)
                else:
                    self.is_processing = False

    def get_gem_at(self, x, y):
        """Возвращает кристалл по координатам мыши"""
        for row in range(self.rows):
            for col in range(self.cols):
                gem = self.grid[row][col]
                if gem and gem.x <= x <= gem.x + gem.size and gem.y <= y <= gem.y + gem.size:
                    return gem
        return None

    def handle_click(self, x, y):
        """Обработка клика мыши"""
        if self.is_swapping or self.is_processing:
            return None

        clicked_gem = self.get_gem_at(x, y)

        if clicked_gem is None:
            if self.selected_gem:
                self.selected_gem.selected = False
                self.selected_gem = None
            return None

        if self.selected_gem is None:
            self.selected_gem = clicked_gem
            clicked_gem.selected = True
            return None
        else:
            if clicked_gem == self.selected_gem:
                clicked_gem.selected = False
                self.selected_gem = None
                return None
            elif self.selected_gem.is_adjacent(clicked_gem):
                result = self.swap_gems(self.selected_gem, clicked_gem)
                self.selected_gem.selected = False
                self.selected_gem = None
                return result
            else:
                self.selected_gem.selected = False
                self.selected_gem = clicked_gem
                clicked_gem.selected = True
                return None

    def swap_gems(self, gem1, gem2):
        """Меняет кристаллы местами"""
        self.is_swapping = True

        row1, col1 = gem1.row, gem1.col
        row2, col2 = gem2.row, gem2.col

        special_gem = None
        other_gem = None

        # 🔥 Определяем какой кристалл специальный, а какой обычный
        if gem1.gem_type in ['bomb', 'line', 'rainbow']:
            special_gem = gem1
            other_gem = gem2
        elif gem2.gem_type in ['bomb', 'line', 'rainbow']:
            special_gem = gem2
            other_gem = gem1

        # Меняем в сетке
        self.grid[row1][col1], self.grid[row2][col2] = gem2, gem1

        # Меняем позиции в кристаллах
        gem1.row, gem1.col = row2, col2
        gem2.row, gem2.col = row1, col1

        # Обновляем позицию специального кристалла
        if special_gem:
            special_gem.row = gem1.row if special_gem == gem1 else gem2.row
            special_gem.col = gem1.col if special_gem == gem1 else gem2.col

        # Целевые позиции для анимации
        gem1.target_x = self.offset_x + gem1.col * self.gem_size
        gem1.target_y = self.offset_y + gem1.row * self.gem_size
        gem2.target_x = self.offset_x + gem2.col * self.gem_size
        gem2.target_y = self.offset_y + gem2.row * self.gem_size

        # 🔥 Активируем специальный кристалл
        if special_gem:
            pygame.time.set_timer(pygame.USEREVENT + 3, 200)

            if special_gem.gem_type == 'bomb':
                self.pending_bomb_gem = special_gem
            elif special_gem.gem_type == 'line':
                self.pending_line_gem = special_gem
            elif special_gem.gem_type == 'rainbow':
                # 🌈 Сохраняем ЦВЕТ ДРУГОГО кристалла для активации радуги!
                self.pending_rainbow_gem = special_gem
                self.rainbow_target_color = other_gem.color_id
                print(f"🌈 Радуга будет активирована с цветом {other_gem.color_id}!")

            print(f"💣⚡🌈 Специальный кристалл будет активирован!")

        self.check_matches_after_swap()

        return {'swapped': True, 'gem1': gem1, 'gem2': gem2}

    def check_matches_after_swap(self):
        """Проверяет совпадения после обмена"""
        pygame.time.set_timer(pygame.USEREVENT + 2, 300)

    def activate_pending_special(self, sound_manager=None):
        """Активирует отложенные специальные кристаллы"""
        activated = False

        if self.pending_bomb_gem:
            print(f"💣 Активация бомбы!")
            self.activate_bomb(self.pending_bomb_gem, sound_manager)
            self.pending_bomb_gem = None
            activated = True

        if self.pending_line_gem:
            print(f"⚡ Активация линейного!")
            self.activate_line(self.pending_line_gem, sound_manager)
            self.pending_line_gem = None
            activated = True

        if self.pending_rainbow_gem:
            print(f"🌈 Активация радужного!")
            # 🌈 Используем сохранённый цвет для активации
            if self.rainbow_target_color is not None:
                self.activate_rainbow(self.rainbow_target_color, sound_manager)
                self.rainbow_target_color = None
            self.pending_rainbow_gem = None
            activated = True

        if activated:
            print(f"🔥 Вызов drop_gems() для очистки...")
            self.drop_gems(sound_manager)
            self.is_processing = True
            print(f"✅ Специальные кристаллы активированы!")

    def process_matches(self, sound_manager=None):
        """Запускает обработку совпадений"""
        matches = self.find_matches()
        if matches:
            self.is_processing = True
            self.remove_matches(matches, sound_manager)
            self.drop_gems(sound_manager)
        else:
            self.is_processing = False

    def get_score(self):
        """Возвращает текущий счёт"""
        return self.score

    def check_win_condition(self, target_score):
        """Проверяет условие победы"""
        if target_score and self.score >= target_score:
            return True
        return False

    def check_lose_condition(self, time_left):
        """Проверяет условие поражения"""
        if time_left is not None and time_left <= 0:
            return True
        return False