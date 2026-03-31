import pygame
import cv2
import json
import sys
import os

from src.menu import Menu
from src.mode_menu import ModeMenu
from src.level_menu import LevelMenu
from src.result_screen import ResultScreen
from src.highscores import Highscores
from src.board import Board
from src.sound_manager import SoundManager

# ============================================================
# --- ИНИЦИАЛИЗАЦИЯ PYGAME ---
# ============================================================
pygame.init()
pygame.display.init()

# ============================================================
# --- ЗАГРУЗКА КОНФИГУРАЦИИ ---
# ============================================================
try:
    with open('config/settings.json', 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    print("❌ Ошибка: Не найден файл config/settings.json")
    settings = {
        'window_width': 1024,
        'window_height': 768,
        'fps': 60,
        'title': 'Jewel Quest',
        'volume_music': 0.3,
        'volume_sfx': 0.5,
        'video_speed': 2,
        'volume_match': 0.6,
        'volume_win': 0.7,
        'volume_lose': 0.6
    }

# ============================================================
# --- СОЗДАНИЕ ОКНА ---
# ============================================================
print(f"🪟 Создание окна {settings['window_width']}x{settings['window_height']}...")
screen = pygame.display.set_mode((settings['window_width'], settings['window_height']))
pygame.display.set_caption(settings['title'])
clock = pygame.time.Clock()

screen.fill((0, 0, 0))
pygame.display.flip()
print("✅ Окно создано!")

# ============================================================
# --- ЗАГРУЗКА ВИДЕО ---
# ============================================================
video_loaded = False
cap = None
current_frame = None
video_frame_counter = 0
video_speed = settings.get('video_speed', 2)

try:
    cap = cv2.VideoCapture('assets/video/background.mp4')
    if cap.isOpened():
        video_loaded = True
        print("✅ Видео загружено успешно!")
    else:
        print("⚠️ Не удалось открыть видеофайл")
        if cap:
            cap.release()
        cap = None
except Exception as e:
    print(f"⚠️ Ошибка видео: {e}")
    video_loaded = False
    if cap:
        cap.release()
    cap = None

# ============================================================
# --- ЗАГРУЗКА ЗВУКОВ ---
# ============================================================
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    try:
        pygame.mixer.music.load('assets/sound/music.mp3')
        pygame.mixer.music.set_volume(settings.get('volume_music', 0.3))
        pygame.mixer.music.play(-1)
        print("✅ Фоновая музыка играет!")
    except Exception as e:
        print(f"⚠️ Музыка не загружена: {e}")

    click_sound = None
    try:
        click_sound = pygame.mixer.Sound('assets/sound/click.mp3')
        click_sound.set_volume(settings.get('volume_sfx', 0.5))
        print("✅ Звук клика загружен!")
    except:
        try:
            click_sound = pygame.mixer.Sound('assets/sound/click.wav')
            click_sound.set_volume(settings.get('volume_sfx', 0.5))
            print("✅ Звук клика загружен (wav)!")
        except Exception as e:
            print(f"⚠️ Звук клика не загружен: {e}")
            click_sound = None
except Exception as e:
    print(f"⚠️ Микшер не инициализирован: {e}")
    click_sound = None

# ============================================================
# --- МЕНЕДЖЕР ЗВУКОВЫХ ЭФФЕКТОВ ---
# ============================================================
sound_manager = SoundManager()

# ============================================================
# --- ЗАГРУЗКА ФОНА ---
# ============================================================
mode_bg = None
mode_bg_path = 'assets/img/mode_bg.jpg'

if os.path.exists(mode_bg_path):
    try:
        mode_bg = pygame.image.load(mode_bg_path)
        mode_bg = pygame.transform.scale(mode_bg, (settings['window_width'], settings['window_height']))
        print(f"✅ Фон загружен: {mode_bg_path}")
    except Exception as e:
        print(f"❌ Ошибка загрузки фона: {e}")
        mode_bg = pygame.Surface((settings['window_width'], settings['window_height']))
        mode_bg.fill((100, 50, 80))
else:
    mode_bg = pygame.Surface((settings['window_width'], settings['window_height']))
    mode_bg.fill((100, 50, 80))

# ============================================================
# --- СОЗДАНИЕ ОБЪЕКТОВ ---
# ============================================================
menu = Menu(settings['window_width'], settings['window_height'], click_sound)
mode_menu = ModeMenu(settings['window_width'], settings['window_height'], click_sound)
level_menu = None
result_screen = None
board = None
highscores = Highscores()

# Переменные игры
game_state = 'MENU'
selected_mode = None
selected_level = None
score = 0
time_left = 60
target_score = 1500
level = 1
is_game_over = False

# Таймеры
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)
MATCH_CHECK_EVENT = pygame.USEREVENT + 2
BOMB_ACTIVATE_EVENT = pygame.USEREVENT + 3  # 🔥 Для активации специальных кристаллов

# ============================================================
# --- ГЛАВНЫЙ ЦИКЛ ---
# ============================================================
running = True
print("🎮 Запуск главного цикла...")

pygame.time.wait(100)

while running:
    clock.tick(settings['fps'])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ====================================================
        # ОБРАБОТКА КЛАВИАТУРЫ ДЛЯ ВВОДА ИМЕНИ (РЕЖИМ ВРЕМЕНИ)
        # ====================================================
        if game_state == 'RESULT' and result_screen and result_screen.mode == 'time':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    result_screen.remove_letter()
                elif event.key == pygame.K_SPACE:
                    result_screen.add_letter(' ')
                elif event.key == pygame.K_RETURN:
                    pass
                elif event.unicode and event.unicode.isalnum():
                    result_screen.add_letter(event.unicode)

        # ESC для навигации
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == 'GAME':
                    game_state = 'LEVEL_SELECT'
                    board = None
                elif game_state == 'LEVEL_SELECT':
                    game_state = 'MODE_SELECT'
                elif game_state == 'MODE_SELECT':
                    game_state = 'MENU'
                elif game_state == 'MENU':
                    running = False

        # ГЛАВНОЕ МЕНЮ
        if game_state == 'MENU':
            result = menu.handle_event(event)
            if result == 'start_game':
                game_state = 'MODE_SELECT'
            elif result == 'exit':
                running = False

        # ВЫБОР РЕЖИМА
        elif game_state == 'MODE_SELECT':
            result = mode_menu.handle_event(event)
            if result == 'time' or result == 'score':
                selected_mode = result
                level_menu = LevelMenu(settings['window_width'], settings['window_height'],
                                       selected_mode, click_sound)
                game_state = 'LEVEL_SELECT'
            elif result == 'back':
                game_state = 'MENU'

        # ВЫБОР УРОВНЯ
        elif game_state == 'LEVEL_SELECT':
            result = level_menu.handle_event(event)
            if result and isinstance(result, int):
                selected_level = result
                params = level_menu.get_level_params(selected_level)

                game_state = 'GAME'
                score = 0
                level = selected_level
                is_game_over = False

                if selected_mode == 'time':
                    time_left = params['time']
                    target_score = None
                else:
                    target_score = params['target']
                    time_left = None

                board = Board(rows=8, cols=8, gem_size=60,
                              screen_width=settings['window_width'],
                              screen_height=settings['window_height'])
                print(f"🎮 Уровень {selected_level} запущен!")

            elif result == 'back':
                game_state = 'MODE_SELECT'

        # ИГРА
        elif game_state == 'GAME':
            if not is_game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if board:
                            result = board.handle_click(event.pos[0], event.pos[1])
                            if result and result.get('swapped'):
                                print(f"💎 Обмен: {result['gem1'].color_id} ↔ {result['gem2'].color_id}")
                                # 🔊 Звук обмена
                                sound_manager.play_swap(settings.get('volume_sfx', 0.3))

                # 🔥 АКТИВАЦИЯ ОТЛОЖЕННЫХ СПЕЦИАЛЬНЫХ КРИСТАЛЛОВ
                if event.type == BOMB_ACTIVATE_EVENT:
                    if board:
                        board.activate_pending_special(sound_manager)  # ✅ Исправлено!

                if event.type == MATCH_CHECK_EVENT:
                    if board:
                        board.process_matches(sound_manager)

                # Проверка условий
                if board:
                    # РЕЖИМ ПО ОЧКАМ: победа при достижении цели
                    if selected_mode == 'score' and target_score and board.get_score() >= target_score:
                        print("🏆 ПОБЕДА! Цель достигнута!")
                        is_game_over = True
                        result_screen = ResultScreen(settings['window_width'],
                                                     settings['window_height'],
                                                     is_win=True,
                                                     score=board.get_score(),
                                                     level=selected_level,
                                                     mode=selected_mode,
                                                     click_sound=click_sound)
                        game_state = 'RESULT'
                        # 🔊 Звук победы
                        sound_manager.play_win(settings.get('volume_win', 0.7))

                    # РЕЖИМ ПО ВРЕМЕНИ: когда время вышло
                    elif selected_mode == 'time' and time_left is not None and time_left <= 0:
                        print("⏰ Время вышло! Введи имя для рекорда...")
                        is_game_over = True
                        result_screen = ResultScreen(settings['window_width'],
                                                     settings['window_height'],
                                                     is_win=False,
                                                     score=board.get_score(),
                                                     level=selected_level,
                                                     mode=selected_mode,
                                                     click_sound=click_sound)
                        game_state = 'RESULT'
                        # 🔊 Звук поражения
                        sound_manager.play_lose(settings.get('volume_lose', 0.6))

        # ЭКРАН РЕЗУЛЬТАТА
        elif game_state == 'RESULT':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    button_result = result_screen.check_button_click(event.pos)

                    if button_result == 'save':
                        if result_screen.mode == 'time':
                            player_name = result_screen.get_player_name()
                            highscores.add_score(player_name, board.get_score(), selected_level, 'time')
                            print(f"📊 Рекорд сохранён: {player_name} - {board.get_score()} очков")
                        game_state = 'MENU'

                    elif button_result == 'next':
                        if selected_level < 5:
                            selected_level += 1
                            level_menu = LevelMenu(settings['window_width'], settings['window_height'],
                                                   selected_mode, click_sound)
                            game_state = 'LEVEL_SELECT'
                        else:
                            print("🎉 Все уровни пройдены!")
                            game_state = 'MENU'

                    elif button_result == 'retry':
                        params = level_menu.get_level_params(selected_level) if level_menu else None
                        if params:
                            game_state = 'GAME'
                            score = 0
                            is_game_over = False

                            if selected_mode == 'time':
                                time_left = params['time']
                                target_score = None
                            else:
                                target_score = params['target']
                                time_left = None

                            board = Board(rows=8, cols=8, gem_size=60,
                                          screen_width=settings['window_width'],
                                          screen_height=settings['window_height'])

                    elif button_result == 'menu':
                        if result_screen.mode == 'time':
                            player_name = result_screen.get_player_name()
                            highscores.add_score(player_name, board.get_score(), selected_level, 'time')
                            print(f"📊 Рекорд сохранён: {player_name} - {board.get_score()} очков")
                        game_state = 'MENU'

        # Таймер
        if event.type == TIMER_EVENT:
            if game_state == 'GAME' and selected_mode == 'time' and time_left is not None and not is_game_over:
                time_left -= 1
                if time_left <= 0:
                    print("⏰ Время вышло!")

    # ========================================================
    # --- ОТРИСОВКА ФОНА ---
    # ========================================================
    screen.fill((0, 0, 0))

    if game_state == 'MENU' and video_loaded and cap:
        video_frame_counter += 1
        if video_frame_counter >= video_speed:
            video_frame_counter = 0
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                frame = pygame.transform.scale(frame, (settings['window_width'], settings['window_height']))
                current_frame = frame
        if current_frame:
            screen.blit(current_frame, (0, 0))

    elif game_state in ['MODE_SELECT', 'LEVEL_SELECT', 'GAME', 'RESULT']:
        if mode_bg:
            screen.blit(mode_bg, (0, 0))

    # ========================================================
    # --- ОТРИСОВКА ИНТЕРФЕЙСА ---
    # ========================================================
    if game_state == 'MENU':
        menu.draw(screen)
    elif game_state == 'MODE_SELECT':
        mode_menu.draw(screen, None)
    elif game_state == 'LEVEL_SELECT':
        level_menu.draw(screen, None)
    elif game_state == 'GAME':
        if board:
            board.update()
            board.draw(screen)

        font = pygame.font.Font(None, 36)

        score_text = font.render(f"Очки: {board.get_score()}", True, (255, 180, 200))
        screen.blit(score_text, (20, 20))

        level_text = font.render(f"Уровень: {level}", True, (255, 180, 200))
        screen.blit(level_text, (20, 60))

        if selected_mode == 'time' and time_left is not None:
            time_text = font.render(f"Время: {time_left}", True, (255, 180, 200))
            screen.blit(time_text, (20, 100))
        elif selected_mode == 'score' and target_score is not None:
            target_text = font.render(f"Цель: {target_score}", True, (255, 180, 200))
            screen.blit(target_text, (20, 100))

        small_font = pygame.font.Font(None, 28)
        hint = small_font.render("ESC - назад", True, (200, 200, 200))
        screen.blit(hint, (settings['window_width'] - 150, 20))

    elif game_state == 'RESULT':
        if result_screen:
            result_screen.draw(screen, mode_bg)

    # ========================================================
    # --- ОБНОВЛЕНИЕ ЭКРАНА ---
    # ========================================================
    pygame.display.flip()

# ============================================================
# --- ОЧИСТКА РЕСУРСОВ ---
# ============================================================
print("🧹 Очистка ресурсов...")
if cap:
    cap.release()
pygame.quit()
sys.exit()