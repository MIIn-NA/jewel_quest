import pygame
import os
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True

        # Загружаем звуки
        self._load_sounds()

    def _load_sounds(self):
        """Загружает все звуковые эффекты"""
        sound_dir = 'assets/sound/sfx'

        # Звук совпадения (исчезновение кристаллов)
        self._load_sound('match', f'{sound_dir}/match.wav')

        # Звук победы
        self._load_sound('win', f'{sound_dir}/win.wav')

        # Звук поражения
        self._load_sound('lose', f'{sound_dir}/lose.wav')

        # Звук комбо (5+ в ряд)
        self._load_sound('combo', f'{sound_dir}/combo.wav')

        # Звук обмена кристаллов
        self._load_sound('swap', f'{sound_dir}/swap.wav')

        # Звук падения кристаллов
        self._load_sound('drop', f'{sound_dir}/drop.wav')

        print(f"✅ Загружено {len(self.sounds)} звуковых эффектов")

    def _load_sound(self, name, filepath):
        """Загружает один звук"""
        try:
            if os.path.exists(filepath):
                self.sounds[name] = pygame.mixer.Sound(filepath)
                print(f"  ✅ {name}: {filepath}")
            else:
                # Создаём пустой звук если файл не найден
                self.sounds[name] = None
                print(f"  ⚠️ {name}: файл не найден ({filepath})")
        except Exception as e:
            self.sounds[name] = None
            print(f"  ❌ {name}: ошибка ({e})")

    def play(self, name, volume=1.0):
        """Воспроизводит звук по имени"""
        if not self.enabled:
            return

        if name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].set_volume(volume)
                self.sounds[name].play()
            except:
                pass

    def play_match(self, volume=0.4):
        """Звук совпадения кристаллов"""
        self.play('match', volume)

    def play_combo(self, volume=0.5):
        """Звук комбо"""
        self.play('combo', volume)

    def play_win(self, volume=0.5):
        """Звук победы"""
        self.play('win', volume)

    def play_lose(self, volume=0.4):
        """Звук поражения"""
        self.play('lose', volume)

    def play_swap(self, volume=0.3):
        """Звук обмена кристаллов"""
        self.play('swap', volume)

    def play_drop(self, volume=0.2):
        """Звук падения кристаллов"""
        self.play('drop', volume)

    def toggle(self):
        """Включить/выключить звуки"""
        self.enabled = not self.enabled
        return self.enabled