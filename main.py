import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Shooter")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (30, 30, 30)
GREEN = (0, 200, 0) # Трохи темніший зелений для кнопки
BRIGHT_GREEN = (0, 255, 0) # Яскравіший для наведення (опціонально)

# --- Розміри об'єктів ---
PLAYER_SIZE = (40, 40)
ENEMY_SIZE = (35, 35)
ICON_SIZE = (25, 25)
BULLET_SIZE = (5, 10)

# --- Завантаження ресурсів (з обробкою помилок) ---
try:
    player_img_orig = pygame.image.load("player.png").convert_alpha()
    enemy_img_orig = pygame.image.load("enemy.png").convert_alpha()
    heart_img_orig = pygame.image.load("heart.png").convert_alpha()
    skull_img_orig = pygame.image.load("skull.png").convert_alpha()

    player_img = pygame.transform.scale(player_img_orig, PLAYER_SIZE)
    enemy_img = pygame.transform.scale(enemy_img_orig, ENEMY_SIZE)
    heart_img = pygame.transform.scale(heart_img_orig, ICON_SIZE)
    skull_img = pygame.transform.scale(skull_img_orig, ICON_SIZE)

except pygame.error as e:
    print(f"Помилка завантаження зображення: {e}")
    print("Буду використані стандартні кольорові квадрати.")
    player_img = pygame.Surface(PLAYER_SIZE)
    player_img.fill(BLUE)
    enemy_img = pygame.Surface(ENEMY_SIZE)
    enemy_img.fill(RED)
    heart_img = pygame.Surface(ICON_SIZE)
    heart_img.fill(RED)
    skull_img = pygame.Surface(ICON_SIZE)
    skull_img.fill(WHITE)

bullet_img = pygame.Surface(BULLET_SIZE)
bullet_img.fill(WHITE)

# --- Шрифти ---
try:
    font_info = pygame.font.SysFont(None, 30)
    font_game_over = pygame.font.SysFont(None, 75)
    font_restart = pygame.font.SysFont(None, 50)
except Exception as e: # Ловимо ширший спектр помилок шрифтів
    print(f"Помилка завантаження системного шрифта: {e}. Використовується стандартний.")
    try:
        font_info = pygame.font.Font(None, 30)
        font_game_over = pygame.font.Font(None, 75)
        font_restart = pygame.font.Font(None, 50)
    except Exception as e_fallback:
        print(f"ПОМИЛКА: Не вдалося завантажити навіть стандартний шрифт: {e_fallback}")
        # Аварійний вихід, бо без шрифтів гра не працюватиме коректно
        pygame.quit()
        sys.exit()


class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.bottom = HEIGHT - 20
        self.rect.centerx = WIDTH // 2
        self.speed = 5
        self.bullets = []
        self.lives = 3
        self.score = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = pygame.Rect(self.rect.centerx - BULLET_SIZE[0] // 2, self.rect.top, BULLET_SIZE[0], BULLET_SIZE[1])
        self.bullets.append(bullet)

    def update_bullets(self, enemies):
        for bullet in self.bullets[:]:
            bullet.y -= 10
            if bullet.bottom < 0:
                self.bullets.remove(bullet)
            else:
                enemies_hit = []
                for enemy in enemies[:]:
                    if bullet.colliderect(enemy.rect):
                        enemies_hit.append(enemy)

                if enemies_hit:
                    if bullet in self.bullets:
                         try:
                             self.bullets.remove(bullet)
                         except ValueError: pass # Якщо кулю вже видалено іншим процесом
                    for enemy in enemies_hit:
                         if enemy in enemies:
                            try:
                                enemies.remove(enemy)
                                enemies.append(Enemy())
                                self.score += 1
                            except ValueError: pass # Якщо ворога вже видалено

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            screen.blit(bullet_img, bullet)

class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 1

    def move(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def draw_info(screen, lives, score):
    heart_width = heart_img.get_width()
    for i in range(lives):
        screen.blit(heart_img, (10 + i * (heart_width + 5), 10))

    skull_rect = skull_img.get_rect(topleft=(10, 10 + heart_img.get_height() + 10))
    screen.blit(skull_img, skull_rect)
    text = font_info.render(f': {score}', True, WHITE)
    text_rect = text.get_rect(midleft=(skull_rect.right + 5, skull_rect.centery))
    screen.blit(text, text_rect)

def show_game_over_screen(screen, score):
    screen.fill(BLACK)
    # --- Текст "Game Over" ---
    game_over_text = font_game_over.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)) # Трохи вище
    screen.blit(game_over_text, game_over_rect)

    # --- Текст зі статистикою ---
    score_text = font_info.render(f"Ворогів знищено: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, game_over_rect.bottom + 40)) # Збільшено відступ
    screen.blit(score_text, score_rect)

    # --- Кнопка "Грати знову" ---
    # Визначаємо текст і його розмір
    restart_text_content = "Грати знову"
    restart_text = font_restart.render(restart_text_content, True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, score_rect.bottom + 60)) # Ще відступ

    # Визначаємо розмір кнопки з відступами
    button_padding = 15
    button_rect = pygame.Rect(restart_rect.left - button_padding,
                              restart_rect.top - button_padding,
                              restart_rect.width + 2 * button_padding,
                              restart_rect.height + 2 * button_padding)

    # Перевіряємо, чи курсор над кнопкою (для зміни кольору)
    mouse_pos = pygame.mouse.get_pos()
    button_color = GREEN
    if button_rect.collidepoint(mouse_pos):
        button_color = BRIGHT_GREEN # Яскравіший колір при наведенні

    # Малюємо кнопку та текст
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10) # Обводка
    screen.blit(restart_text, restart_rect) # Малюємо текст поверх кнопки

    return button_rect # Повертаємо область кнопки для перевірки кліку

# --- Ініціалізація гри ---
player = Player()
enemies = []
button_rect_game_over = None # Змінна для зберігання Rect кнопки

def reset_game():
    global enemies, button_rect_game_over
    player.reset()
    enemies = [Enemy() for _ in range(6)] # Трохи збільшимо початкову кількість ворогів
    button_rect_game_over = None # Скидаємо Rect кнопки при перезапуску

reset_game()

clock = pygame.time.Clock()
running = True
game_state = "PLAYING"

# --- Головний цикл гри ---
while running:

    # --- Обробка подій ---
    events = pygame.event.get() # Отримуємо всі події один раз за кадр
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # --- Обробка подій в стані гри ---
        if game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Обробка подій в стані Game Over ---
        elif game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE: # Вихід по Escape працює завжди
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Перевіряємо клік лівою кнопкою миші (button 1)
                if event.button == 1 and button_rect_game_over is not None:
                    if button_rect_game_over.collidepoint(event.pos):
                        reset_game()
                        game_state = "PLAYING"
                        # Важливо: вийти з циклу обробки подій після зміни стану
                        break # Виходимо з for event in events

    # --- Логіка гри (тільки якщо гра активна) ---
    if game_state == "PLAYING":
        keys = pygame.key.get_pressed() # Отримуємо натиснуті клавіші для руху
        player.move(keys)
        player.update_bullets(enemies)

        # --- Оновлення ворогів та перевірка зіткнень ---
        for enemy in enemies[:]:
            enemy.move()
            # Ворог вийшов за межі екрану
            if enemy.rect.top > HEIGHT:
                try:
                    enemies.remove(enemy)
                    enemies.append(Enemy())
                    player.lives -= 1
                    if player.lives <= 0:
                        game_state = "GAME_OVER"
                        # Не потрібно break, цикл ворогів завершиться природно
                except ValueError: pass

            # Зіткнення гравця з ворогом
            elif player.rect.colliderect(enemy.rect):
                 try:
                    if enemy in enemies:
                        enemies.remove(enemy)
                        enemies.append(Enemy())
                        player.lives -= 1
                        if player.lives <= 0:
                             game_state = "GAME_OVER"
                 except ValueError: pass

        # --- Малювання ігрового стану ---
        screen.fill(BLACK)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        draw_info(screen, player.lives, player.score)

    # --- Логіка та малювання екрану Game Over ---
    elif game_state == "GAME_OVER":
        # Малюємо екран Game Over і отримуємо область кнопки
        # Це потрібно робити кожен кадр, щоб кнопка реагувала на наведення миші
        button_rect_game_over = show_game_over_screen(screen, player.score)

    # --- Оновлення дисплею (завжди в кінці циклу) ---
    pygame.display.flip()

    # --- Контроль FPS ---
    clock.tick(60)

# --- Завершення гри ---
pygame.quit()
sys.exit()
