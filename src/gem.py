import pygame
import os


class Gem:
    # Класс-переменные для общих изображений
    images = []
    images_loaded = False
    images_checked = False

    # Специальные кристаллы
    bomb_image = None
    line_image = None
    rainbow_image = None

    def __init__(self, x, y, row, col, color_id, size=60, gem_type='normal'):
        self.row = row
        self.col = col
        self.size = size
        self.color_id = color_id  # 0-5 для разных цветов
        self.gem_type = gem_type  # 'normal', 'bomb', 'line', 'rainbow'
        self.direction = None  # 'h' = горизонтальный, 'v' = вертикальный

        # Позиция на экране
        self.x = x
        self.y = y

        # Для анимации
        self.target_x = x
        self.target_y = y
        self.selected = False
        self.matched = False
        self.scale = 1.0

        # Цвета для 6 типов
        self.colors = [
            (255, 50, 50),  # 0: Красный
            (50, 255, 50),  # 1: Зелёный
            (50, 50, 255),  # 2: Синий
            (255, 255, 50),  # 3: Жёлтый
            (255, 50, 255),  # 4: Фиолетовый
            (50, 255, 255)  # 5: Голубой
        ]

        # Загружаем картинки один раз для всех кристаллов
        if not Gem.images_checked:
            Gem._load_images(size)

    @classmethod
    def _load_images(cls, size):
        """Загружает все изображения кристаллов"""
        cls.images = []
        cls.images_loaded = True

        # Обычные кристаллы (gem_0.png ... gem_5.png)
        for i in range(6):
            img_path = f'assets/img/gems/gem_{i}.png'
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, (size, size))
                    cls.images.append(img)
                except:
                    cls.images.append(None)
                    cls.images_loaded = False
            else:
                cls.images.append(None)
                cls.images_loaded = False

        # 💣 Кристалл-бомба (gem_bomb.png)
        bomb_path = 'assets/img/gems/gem_bomb.png'
        if os.path.exists(bomb_path):
            try:
                cls.bomb_image = pygame.image.load(bomb_path)
                cls.bomb_image = pygame.transform.scale(cls.bomb_image, (size, size))
                print(f"✅ Бомба загружена: {bomb_path}")
            except Exception as e:
                cls.bomb_image = None
                print(f"⚠️ Бомба не загружена: {e}")
        else:
            cls.bomb_image = None
            print(f"⚠️ Бомба не найдена: {bomb_path}")

        # ⚡ Линейный кристалл (gem_line.png)
        line_path = 'assets/img/gems/gem_line.png'
        if os.path.exists(line_path):
            try:
                cls.line_image = pygame.image.load(line_path)
                cls.line_image = pygame.transform.scale(cls.line_image, (size, size))
                print(f"✅ Линейный загружен: {line_path}")
            except Exception as e:
                cls.line_image = None
                print(f"⚠️ Линейный не загружен: {e}")
        else:
            cls.line_image = None
            print(f"⚠️ Линейный не найден: {line_path}")

        # 🌈 Радужный кристалл (gem_rainbow.png)
        rainbow_path = 'assets/img/gems/gem_rainbow.png'
        if os.path.exists(rainbow_path):
            try:
                cls.rainbow_image = pygame.image.load(rainbow_path)
                cls.rainbow_image = pygame.transform.scale(cls.rainbow_image, (size, size))
                print(f"✅ Радужный загружен: {rainbow_path}")
            except Exception as e:
                cls.rainbow_image = None
                print(f"⚠️ Радужный не загружен: {e}")
        else:
            cls.rainbow_image = None
            print(f"⚠️ Радужный не найден: {rainbow_path}")

        cls.images_checked = True

        if cls.images_loaded and cls.bomb_image and cls.line_image and cls.rainbow_image:
            print("✅✅✅ ВСЕ кристаллы загружены (бомба + линейный + радужный)!")
        else:
            print("⚠️⚠️⚠️ Некоторые кристаллы не загружены")

    def draw(self, screen):
        """Рисует кристалл"""
        center_x = int(self.x + self.size // 2)
        center_y = int(self.y + self.size // 2)

        # Если картинки загружены — рисуем изображение
        if Gem.images_loaded:
            image = None

            # 💣 Бомба
            if self.gem_type == 'bomb':
                if Gem.bomb_image:
                    image = Gem.bomb_image

            # ⚡ Линейный кристалл
            elif self.gem_type == 'line':
                if Gem.line_image:
                    image = Gem.line_image

            # 🌈 Радужный кристалл
            elif self.gem_type == 'rainbow':
                if Gem.rainbow_image:
                    image = Gem.rainbow_image

            # Обычный кристалл
            if image is None and self.color_id < len(Gem.images) and Gem.images[self.color_id]:
                image = Gem.images[self.color_id]

            # Рисуем изображение
            if image:
                # Масштабирование для анимации
                if self.scale < 1.0:
                    new_size = int(self.size * self.scale)
                    if new_size > 0:
                        image = pygame.transform.scale(image, (new_size, new_size))

                image_rect = image.get_rect(center=(center_x, center_y))
                screen.blit(image, image_rect)
            else:
                # Рисуем цветной круг если нет картинки
                color = self.colors[self.color_id] if self.color_id < len(self.colors) else (255, 255, 255)
                radius = int(self.size // 2 * self.scale)
                if radius > 0:
                    pygame.draw.circle(screen, color, (center_x, center_y), radius)

            # Рамка если выбран
            if self.selected:
                rect = pygame.Rect(center_x - self.size // 2, center_y - self.size // 2,
                                   self.size, self.size)
                pygame.draw.rect(screen, (255, 180, 200), rect, 4, border_radius=10)
        else:
            # Если нет картинок — рисуем цветной круг
            color = self.colors[self.color_id] if self.color_id < len(self.colors) else (255, 255, 255)

            if self.selected:
                pygame.draw.circle(screen, (255, 180, 200), (center_x, center_y),
                                   self.size // 2 + 5, 4)

            radius = int(self.size // 2 * self.scale)
            if radius > 0:
                pygame.draw.circle(screen, color, (center_x, center_y), radius)

    def update(self):
        """Обновляет позицию и анимацию"""
        # Плавное движение к целевой позиции
        if abs(self.target_x - self.x) > 1:
            self.x += (self.target_x - self.x) * 0.3
        if abs(self.target_y - self.y) > 1:
            self.y += (self.target_y - self.y) * 0.3

        # Анимация исчезновения
        if self.matched:
            self.scale -= 0.1
            if self.scale < 0:
                self.scale = 0

    def is_adjacent(self, other):
        """Проверяет, соседний ли кристалл"""
        return (abs(self.row - other.row) + abs(self.col - other.col)) == 1