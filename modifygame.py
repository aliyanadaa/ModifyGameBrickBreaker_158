
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


