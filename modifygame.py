
import pygame
import random
import json
import math
import io
import wave
import struct
from pathlib import Path

# ==================================================
# BRICK BREAKER DELUXE
# ==================================================

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker Deluxe")
clock = pygame.time.Clock()

# COLORS
BLACK = (10, 12, 25)
WHITE = (245, 245, 255)
GREEN = (60, 220, 130)
RED = (245, 80, 90)
BLUE = (75, 155, 255)
YELLOW = (255, 220, 75)
PURPLE = (175, 105, 255)
CYAN = (70, 225, 235)
GRAY = (160, 170, 190)
DARK = (25, 30, 55)

FONT = pygame.font.Font(None, 30)
SMALL = pygame.font.Font(None, 23)
BIG = pygame.font.Font(None, 60)
TITLE = pygame.font.Font(None, 80)

# HIGH SCORE
RECORD_FILE = Path(__file__).with_name("highscore.json")


def load_record():
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return {
                "name": data.get("name", "Player"),
                "score": int(data.get("score", 0))
            }
    except (FileNotFoundError, ValueError, TypeError, OSError):
        return {"name": "Belum ada", "score": 0}


def save_record(name, score):
    try:
        with open(RECORD_FILE, "w", encoding="utf-8") as file:
            json.dump(
                {"name": name, "score": score},
                file,
                indent=4
            )
    except OSError:
        print("High score gagal disimpan.")


# ==================================================
# SOUND EFFECT DAN MUSIK
# ==================================================

def create_sound(frequency, duration=0.12, volume=0.18):
    rate = 44100
    frames = bytearray()
    count = int(rate * duration)

    for i in range(count):
        envelope = min(1, i / 300) * min(1, (count-i) / 500)
        value = int(
            32767 * volume * envelope *
            math.sin(2 * math.pi * frequency * i / rate)
        )
        frames.extend(struct.pack("<h", value))

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(frames)

    buffer.seek(0)
    return pygame.mixer.Sound(buffer)


SOUNDS = {}
MUSIC = None

try:
    SOUNDS = {
        "bounce": create_sound(520, 0.07),
        "brick": create_sound(760, 0.10),
        "power": create_sound(980, 0.18),
        "lose": create_sound(180, 0.30),
        "win": create_sound(880, 0.30)
    }

    # Membuat musik arcade sederhana
    rate = 22050
    notes = [262, 330, 392, 330, 294, 349, 440, 349]
    frames = bytearray()

    for frequency in notes * 2:
        count = int(rate * 0.22)

        for i in range(count):
            envelope = min(1, i / 250) * min(1, (count-i) / 350)
            value = int(
                32767 * 0.05 * envelope *
                math.sin(2 * math.pi * frequency * i / rate)
            )
            frames.extend(struct.pack("<h", value))

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(frames)

    buffer.seek(0)
    MUSIC = pygame.mixer.Sound(buffer)

except (pygame.error, OSError):
    SOUNDS = {}
    MUSIC = None


def sound(name):
    if name in SOUNDS:
        SOUNDS[name].play()


def start_music():
    if MUSIC is not None and not pygame.mixer.get_busy():
        MUSIC.play(loops=-1)


def stop_music():
    if pygame.mixer.get_init():
        pygame.mixer.stop()


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)


def button(rect, text, selected=False):
    color = (65, 90, 150) if selected else (40, 50, 85)

    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(
        screen,
        CYAN if selected else GRAY,
        rect,
        2,
        border_radius=10
    )

    draw_text(text, FONT, WHITE, rect.centerx, rect.centery)


# ==================================================
# PLAYER NAME
# ==================================================

def enter_name(current_name):
    name = current_name

    while True:
        screen.fill(BLACK)

        draw_text(
            "ENTER PLAYER NAME",
            BIG, CYAN, WIDTH//2, 190
        )

        rect = pygame.Rect(WIDTH//2-170, 260, 340, 55)

        pygame.draw.rect(screen, DARK, rect, border_radius=8)
        pygame.draw.rect(screen, CYAN, rect, 2, border_radius=8)

        draw_text(name + "|", FONT, WHITE, WIDTH//2, 287)

        draw_text(
            "ENTER = Save | ESC = Cancel",
            SMALL, GRAY, WIDTH//2, 350
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return name.strip()[:12] or "Player"

                elif event.key == pygame.K_ESCAPE:
                    return current_name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                elif event.unicode.isprintable() and len(name) < 12:
                    name += event.unicode

        clock.tick(FPS)


# ==================================================
# MAIN MENU
# ==================================================

def high_score_screen(record):
    while True:
        screen.fill(BLACK)

        draw_text("HIGH SCORE", BIG, YELLOW, WIDTH//2, 190)
        draw_text(record["name"], FONT, CYAN, WIDTH//2, 270)
        draw_text(str(record["score"]), BIG, WHITE, WIDTH//2, 330)

        draw_text(
            "ENTER / ESC = Back",
            SMALL, GRAY, WIDTH//2, 420
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return True

        clock.tick(FPS)


def main_menu(record, player_name):

    start_button = pygame.Rect(WIDTH//2-125, 270, 250, 52)
    score_button = pygame.Rect(WIDTH//2-125, 340, 250, 52)
    exit_button = pygame.Rect(WIDTH//2-125, 410, 250, 52)

    while True:
        screen.fill(BLACK)

        draw_text(
            "BRICK BREAKER",
            TITLE, CYAN, WIDTH//2, 120
        )

        draw_text(
            "DELUXE EDITION",
            FONT, WHITE, WIDTH//2, 180
        )

        draw_text(
            "Player: " + player_name,
            SMALL, GRAY, WIDTH//2, 225
        )

        draw_text(
            "Press N to change player name",
            SMALL, GRAY, WIDTH//2, 245
        )

        mouse = pygame.mouse.get_pos()

        button(start_button, "START GAME",
               start_button.collidepoint(mouse))

        button(score_button, "HIGH SCORE",
               score_button.collidepoint(mouse))

        button(exit_button, "EXIT",
               exit_button.collidepoint(mouse))

        draw_text(
            "Use LEFT and RIGHT arrow keys to move",
            SMALL, GRAY, WIDTH//2, 520
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "exit", player_name

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return "exit", player_name

                if event.key == pygame.K_RETURN:
                    return "start", player_name

                if event.key == pygame.K_n:
                    new_name = enter_name(player_name)

                    if new_name is None:
                        return "exit", player_name

                    player_name = new_name

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if start_button.collidepoint(event.pos):
                        return "start", player_name

                    if score_button.collidepoint(event.pos):
                        if not high_score_screen(record):
                            return "exit", player_name

                    if exit_button.collidepoint(event.pos):
                        return "exit", player_name

        clock.tick(FPS)


# ==================================================
# PADDLE CLASS
# ==================================================

class Paddle:

    def __init__(self):
        self.width = 110
        self.height = 16
        self.speed = 8

        self.x = (WIDTH-self.width)/2
        self.y = HEIGHT-55

        self.rect = pygame.Rect(
            round(self.x), self.y,
            self.width, self.height
        )

        self.big_timer = 0

    def update(self, direction):
        self.x += direction*self.speed

        self.x = max(
            0,
            min(self.x, WIDTH-self.width)
        )

        self.rect.x = round(self.x)

        if self.big_timer > 0:
            self.big_timer -= 1

            if self.big_timer == 0:
                self.normal_size()

    def big_size(self):
        center = self.rect.centerx

        self.width = 165
        self.x = max(
            0,
            min(center-self.width/2, WIDTH-self.width)
        )

        self.rect.width = self.width
        self.rect.x = round(self.x)

        self.big_timer = FPS*8

    def normal_size(self):
        center = self.rect.centerx

        self.width = 110
        self.x = max(
            0,
            min(center-self.width/2, WIDTH-self.width)
        )

        self.rect.width = self.width
        self.rect.x = round(self.x)

    def draw(self):
        pygame.draw.rect(
            screen, CYAN, self.rect,
            border_radius=8
        )


# ==================================================
# BALL CLASS
# ==================================================

class Ball:

    def __init__(self, speed):
        self.radius = 9
        self.base_speed = speed
        self.reset()

    @property
    def speed(self):
        if self.slow_timer > 0:
            return self.base_speed*0.65

        return self.base_speed

    def update_rect(self):
        self.rect = pygame.Rect(
            round(self.x-self.radius),
            round(self.y-self.radius),
            self.radius*2,
            self.radius*2
        )

    def reset(self):
        self.x = WIDTH/2
        self.y = HEIGHT-78

        self.dx = random.choice([-0.65, 0.65])
        self.dy = -0.76

        self.slow_timer = 0
        self.update_rect()

    def update(self):

        if self.slow_timer > 0:
            self.slow_timer -= 1

        self.x += self.dx*self.speed
        self.y += self.dy*self.speed

        # Wall collision
        if self.x-self.radius <= 0:
            self.x = self.radius
            self.dx = abs(self.dx)
            sound("bounce")

        elif self.x+self.radius >= WIDTH:
            self.x = WIDTH-self.radius
            self.dx = -abs(self.dx)
            sound("bounce")

        # Top collision
        if self.y-self.radius <= 48:
            self.y = 48+self.radius
            self.dy = abs(self.dy)
            sound("bounce")

        self.update_rect()

        return self.y-self.radius > HEIGHT

    def bounce_paddle(self, paddle):

        offset = (
            self.x-paddle.rect.centerx
        )/(paddle.width/2)

        self.dx = max(-0.9, min(0.9, offset))

        if abs(self.dx) < 0.18:
            self.dx = random.choice([-0.18, 0.18])

        self.dy = -math.sqrt(
            max(0.2, 1-self.dx*self.dx)
        )

        self.y = paddle.rect.top-self.radius-1

        self.update_rect()
        sound("bounce")

    def bounce_brick(self, brick):

        left = self.rect.right-brick.rect.left
        right = brick.rect.right-self.rect.left
        top = self.rect.bottom-brick.rect.top
        bottom = brick.rect.bottom-self.rect.top

        smallest = min(left, right, top, bottom)

        if smallest in (left, right):
            self.dx *= -1
        else:
            self.dy *= -1

        self.update_rect()

    def draw(self):
        pygame.draw.circle(
            screen, YELLOW,
            (round(self.x), round(self.y)),
            self.radius
        )


# ==================================================
# BRICK CLASS
# ==================================================

class Brick:

    def __init__(self, x, y, width, height, color, hits=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hits = hits

    def hit(self):
        self.hits -= 1

        if self.hits == 1:
            self.color = WHITE

        return self.hits <= 0

    def draw(self):
        pygame.draw.rect(
            screen, self.color,
            self.rect, border_radius=4
        )

        pygame.draw.rect(
            screen, BLACK,
            self.rect, 1, border_radius=4
        )


def create_bricks(level):

    bricks = []

    colors = [RED, GREEN, BLUE, PURPLE, CYAN]

    columns = 12
    rows = 4+level

    width = 52
    height = 19

    gap_x = 10
    gap_y = 9

    total_width = columns*width+(columns-1)*gap_x
    start_x = (WIDTH-total_width)//2

    for row in range(rows):

        for col in range(columns):

            x = start_x+col*(width+gap_x)
            y = 75+row*(height+gap_y)

            hits = 2 if level >= 2 and (row+col)%4 == 0 else 1

            color = WHITE if hits == 2 else colors[row%5]

            bricks.append(
                Brick(x, y, width, height, color, hits)
            )

    return bricks


# ==================================================
# POWER-UP CLASS
# ==================================================

class PowerUp:

    def __init__(self, x, y, kind):
        self.kind = kind
        self.y = float(y)

        self.rect = pygame.Rect(
            x-12, y-10, 24, 20
        )

    def update(self):
        self.y += 3
        self.rect.y = round(self.y-10)

    def draw(self):

        colors = {
            "wide": CYAN,
            "slow": BLUE,
            "life": RED
        }

        labels = {
            "wide": "W",
            "slow": "S",
            "life": "+"
        }

        pygame.draw.rect(
            screen,
            colors[self.kind],
            self.rect,
            border_radius=5
        )

        draw_text(
            labels[self.kind],
            SMALL, BLACK,
            self.rect.centerx,
            self.rect.centery
        )


# ==================================================
# PAUSE SCREEN
# ==================================================

def pause_screen():

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))

    screen.blit(overlay, (0, 0))

    draw_text(
        "PAUSED",
        BIG, YELLOW,
        WIDTH//2, HEIGHT//2-35
    )

    draw_text(
        "P / SPACE = RESUME",
        FONT, WHITE,
        WIDTH//2, HEIGHT//2+20
    )

    draw_text(
        "ESC = MAIN MENU",
        SMALL, GRAY,
        WIDTH//2, HEIGHT//2+60
    )


# ==================================================
# GAME SCREEN
# ==================================================

def draw_game(paddle, ball, bricks, powerups,
              score, lives, level, paused):

    screen.fill(BLACK)

    pygame.draw.line(
        screen, DARK,
        (0, 48), (WIDTH, 48), 2
    )

    draw_text(
        f"Score: {score}",
        SMALL, WHITE, 15, 14, False
    )

    draw_text(
        f"Lives: {lives}",
        SMALL, WHITE, 190, 14, False
    )

    draw_text(
        f"Level: {level}/3",
        SMALL, WHITE, 330, 14, False
    )

    draw_text(
        "P: Pause",
        SMALL, GRAY, WIDTH-110, 14, False
    )

    for brick in bricks:
        brick.draw()

    for powerup in powerups:
        powerup.draw()

    paddle.draw()
    ball.draw()

    if paused:
        pause_screen()

    pygame.display.flip()


# ==================================================
# GAME OVER / WIN SCREEN
# ==================================================

def end_screen(message, score, record, new_record):

    while True:

        screen.fill(BLACK)

        draw_text(
            message, BIG, YELLOW,
            WIDTH//2, 145
        )

        draw_text(
            f"Your Score: {score}",
            FONT, WHITE,
            WIDTH//2, 225
        )

        draw_text(
            f"High Score: {record['score']}",
            FONT, GREEN,
            WIDTH//2, 275
        )

        draw_text(
            f"Record Holder: {record['name']}",
            SMALL, CYAN,
            WIDTH//2, 315
        )

        if new_record:
            draw_text(
                "NEW HIGH SCORE!",
                FONT, YELLOW,
                WIDTH//2, 355
            )

        draw_text(
            "R / ENTER = PLAY AGAIN",
            SMALL, WHITE,
            WIDTH//2, 420
        )

        draw_text(
            "M = MAIN MENU | ESC = EXIT",
            SMALL, GRAY,
            WIDTH//2, 460
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_r, pygame.K_RETURN):
                    return "restart"

                if event.key == pygame.K_m:
                    return "menu"

                if event.key == pygame.K_ESCAPE:
                    return "exit"

        clock.tick(FPS)


# ==================================================
# GAME ENGINE
# ==================================================

def play_game():

    start_music()

    score = 0
    lives = 3
    level = 1

    direction = 0
    paused = False

    paddle = Paddle()
    ball = Ball(5.2)

    bricks = create_bricks(level)
    powerups = []

    while True:

        clock.tick(FPS)

        # EVENT HANDLING
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop_music()
                return "exit", score

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return "menu", score

                if event.key == pygame.K_p:
                    paused = not paused
                    direction = 0

                elif event.key == pygame.K_SPACE and paused:
                    paused = False
                    direction = 0

                if not paused:

                    if event.key == pygame.K_LEFT:
                        direction = -1

                    elif event.key == pygame.K_RIGHT:
                        direction = 1

            if event.type == pygame.KEYUP:

                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT
                ):
                    direction = 0

        # GAME UPDATE
        if not paused:

            paddle.update(direction)
            life_lost = ball.update()

            # PADDLE COLLISION
            if (
                ball.dy > 0
                and ball.rect.colliderect(paddle.rect)
            ):
                ball.bounce_paddle(paddle)

            # BRICK COLLISION
            for brick in bricks[:]:

                if ball.rect.colliderect(brick.rect):

                    ball.bounce_brick(brick)

                    destroyed = brick.hit()

                    if destroyed:
                        bricks.remove(brick)
                        score += 10
                        sound("brick")

                        # Chance mendapatkan power-up
                        if random.random() < 0.18:

                            kind = random.choice([
                                "wide", "slow", "life"
                            ])

                            powerups.append(
                                PowerUp(
                                    brick.rect.centerx,
                                    brick.rect.centery,
                                    kind
                                )
                            )
                    else:
                        sound("bounce")

                    break

            # POWER-UP UPDATE
            for powerup in powerups[:]:

                powerup.update()

                if powerup.rect.colliderect(paddle.rect):

                    if powerup.kind == "wide":
                        paddle.big_size()

                    elif powerup.kind == "slow":
                        ball.slow_timer = FPS*7

                    elif powerup.kind == "life":
                        lives = min(5, lives+1)

                    powerups.remove(powerup)
                    sound("power")

                elif powerup.y > HEIGHT:
                    powerups.remove(powerup)

            # BALL FALLS
            if life_lost:

                lives -= 1
                sound("lose")

                if lives <= 0:
                    stop_music()
                    return "gameover", score

                ball.reset()
                paddle = Paddle()
                powerups.clear()
                direction = 0

                pygame.time.delay(400)

            # LEVEL COMPLETED
            if not bricks:

                if level >= 3:
                    sound("win")
                    stop_music()
                    return "win", score

                level += 1

                bricks = create_bricks(level)
                powerups.clear()

                ball = Ball(5.2+(level-1)*0.8)
                paddle = Paddle()

                direction = 0

                pygame.time.delay(600)

        # DRAW SCREEN
        draw_game(
            paddle,
            ball,
            bricks,
            powerups,
            score,
            lives,
            level,
            paused
        )


# ==================================================
# MAIN PROGRAM
# ==================================================

def main():

    record = load_record()
    player_name = "Player"

    while True:

        choice, player_name = main_menu(
            record,
            player_name
        )

        if choice == "exit":
            break

        result, score = play_game()

        if result == "exit":
            break

        if result == "menu":
            continue

        # UPDATE HIGH SCORE
        new_record = score > record["score"]

        if new_record:

            record = {
                "name": player_name,
                "score": score
            }

            save_record(player_name, score)

        # END SCREEN
        action = end_screen(
            "GAME OVER" if result == "gameover" else "YOU WIN!",
            score,
            record,
            new_record
        )

        if action == "exit":
            break

        elif action == "restart":
            # Kembali ke menu untuk memulai sesi baru.
            # High score tetap tersimpan.
            continue

        elif action == "menu":
            continue

    stop_music()
    pygame.quit()


# ==================================================
# RUN GAME
# ==================================================

if __name__ == "__main__":
    main()
