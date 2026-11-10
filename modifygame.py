
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


