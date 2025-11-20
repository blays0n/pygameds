import pygame
import random
import json
import os
from os import path, remove

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DON'T STOP!!! — Full")
clock = pygame.time.Clock()

# music_path = path.join("C:/Users/student/Documents/ds/assets", "rory.mp3")
# pygame.mixer.music.load(music_path)
# pygame.mixer.music.set_volume(0.4)
# pygame.mixer.music.play(-1)

BG_PATH = "C:/Users/student/Documents/ds/assets/universe.jpg"
PLAYER_PATH = "C:/Users/student/Documents/ds/assets/mario.png"
FIRE_PATH = "C:/Users/student/Documents/ds/assets/fireball.png"
SAVE_FILE = "save.json"

background = pygame.image.load(BG_PATH).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
player_img = pygame.image.load(PLAYER_PATH).convert_alpha()
player_img = pygame.transform.scale(player_img, (100, 100))
fire_orig = pygame.image.load(FIRE_PATH).convert_alpha()

FLOOR_Y = 450
PLAYER_START_X = 500
PLAYER_W, PLAYER_H = 100, 100
DUCK_H = 60
GRAVITY = 1.1
JUMP_V = -22.0
HP_MAX = 100
BASE_SPEED = 7.0
MAX_SPEED = 18.0
SPEED_INCREMENT = 0.5
SPEED_INCREASE_EVERY = 5

SPAWN_EVENT = pygame.USEREVENT + 1
SPAWN_BASE_MS = 1600
SPAWN_MIN_MS = 600

player_rect = pygame.Rect(0, 0, PLAYER_W, PLAYER_H)
player_rect.midbottom = (PLAYER_START_X, FLOOR_Y)
player_vel_y = 0.0
is_ducking = False
flash_red = 0

HP = HP_MAX
score = 0
best_score = 0
obs_speed = BASE_SPEED
spawn_interval = SPAWN_BASE_MS
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
game_over = False
obstacles = []

font_small = pygame.font.SysFont(None, 32)
font_big = pygame.font.SysFont(None, 72)

def save_game():
    data = {
        "hp": HP,
        "score": score,
        "best_score": best_score,
        "speed": obs_speed,
        "spawn": spawn_interval
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_game():
    global HP, score, best_score, obs_speed, spawn_interval
    if not path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return False
    HP = data.get("hp", HP_MAX)
    score = data.get("score", 0)
    best_score = data.get("best_score", 0)
    obs_speed = data.get("speed", BASE_SPEED)
    spawn_interval = data.get("spawn", SPAWN_BASE_MS)
    pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
    return True

def delete_save():
    try:
        if path.exists(SAVE_FILE):
            remove(SAVE_FILE)
    except Exception:
        pass

if path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            _d = json.load(f)
            best_score = _d.get("best_score", 0)
    except Exception:
        best_score = 0

def player_hitbox():
    h = DUCK_H if (is_ducking and player_vel_y == 0) else PLAYER_H
    return pygame.Rect(player_rect.x, player_rect.bottom - h, PLAYER_W, h)

def make_group(num_items):
    sizes = [36, 48, 60, 72]
    gap = 14
    parts = []
    x = WIDTH + 40
    for _ in range(num_items):
        sz = random.choice(sizes)
        img = pygame.transform.smoothscale(fire_orig, (sz, sz))
        r = img.get_rect()
        r.midbottom = (x + sz // 2, FLOOR_Y)
        parts.append({"img": img, "rect": r})
        x += sz + gap
    left = parts[0]["rect"].left
    right = parts[-1]["rect"].right
    top = parts[0]["rect"].top
    width = right - left if right - left > 0 else 1
    group_rect = pygame.Rect(left, top, width, parts[0]["rect"].height)
    return {"parts": parts, "rect": group_rect, "passed": False}

def spawn_group():
    r = random.random()
    if r < 0.55:
        n = 1
    elif r < 0.88:
        n = 2
    else:
        n = 3
    obstacles.append(make_group(n))

def draw_group(g):
    for p in g["parts"]:
        screen.blit(p["img"], p["rect"])

def draw_hp():
    bar_w = 200
    cur_w = int(bar_w * (HP / HP_MAX))
    if HP > 75:
        color = (0, 200, 0)
    elif HP > 50:
        color = (255, 165, 0)
    else:
        color = (255, 60, 60)
    pygame.draw.rect(screen, (30,30,30), (20,20,bar_w,28))
    pygame.draw.rect(screen, color, (20,20,cur_w,28))
    pygame.draw.rect(screen, (255,255,255), (20,20,bar_w,28), 2)
    txt = font_small.render(f"HP: {HP}", True, (255,255,255))
    screen.blit(txt, (20 + bar_w + 12, 20))

def main_menu():
    options = ["Start New Game", "Continue", "Quit"]
    selected = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if e.key == pygame.K_RETURN:
                    if options[selected] == "Quit":
                        pygame.quit()
                        exit()
                    return options[selected]
        screen.fill((0, 0, 0))
        screen.blit(font_big.render("DON'T STOP!!!", True, (255, 255, 255)), (WIDTH // 2 - 200, 150))
        best_txt = font_small.render(f"Best Score: {best_score}", True, (255, 215, 0))
        screen.blit(best_txt, (WIDTH // 2 - 130, 250))

        for i, op in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            if op == "Continue" and not path.exists(SAVE_FILE):
                color = (80, 80, 80)
            t = font_small.render(op, True, color)
            screen.blit(t, (WIDTH // 2 - 130, 330 + i * 60))
        pygame.display.flip()
        clock.tick(30)

def pause_menu():
    options = ["Continue", "Main Menu", "Quit"]
    selected = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                if e.key == pygame.K_RETURN:
                    if options[selected] == "Quit":
                        pygame.quit()
                        exit()
                    return options[selected]
        screen.fill((15, 15, 15))
        screen.blit(font_big.render("PAUSED", True, (255, 255, 255)), (WIDTH // 2 - 130, 160))
        for i, op in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            t = font_small.render(op, True, color)
            screen.blit(t, (WIDTH // 2 - 100, 300 + i * 60))
        pygame.display.flip()
        clock.tick(30)

def game_over_screen():
    delete_save()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_m:
                    return "menu"
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    exit()
        screen.fill((10, 10, 10))
        screen.blit(font_big.render("GAME OVER", True, (255, 50, 50)), (WIDTH // 2 - 190, HEIGHT // 2 - 100))
        t = font_small.render("R - Restart   M - Menu   ESC/Q - Quit", True, (255, 255, 255))
        screen.blit(t, (WIDTH // 2 - 250, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(30)

mode = main_menu()
if mode == "Continue":
    if not load_game():
        mode = "Start New Game"

if mode == "Start New Game":
    HP = HP_MAX
    score = 0
    obs_speed = BASE_SPEED
    spawn_interval = SPAWN_BASE_MS
    pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
    obstacles.clear()
    player_rect.midbottom = (PLAYER_START_X, FLOOR_Y)
    player_vel_y = 0.0
    game_over = False

if mode == "Quit":
    pygame.quit()
    exit()

while True:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            pygame.quit()
            exit()

        if game_over:
            continue

        if event.type == SPAWN_EVENT:
            if not obstacles or obstacles[-1]["parts"][-1]["rect"].right < WIDTH - 150:
                spawn_group()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_game()
                choice = pause_menu()
                if choice == "Continue":
                    pass
                elif choice == "Main Menu":
                    save_game()
                    m = main_menu()
                    if m == "Continue":
                        load_game()
                    elif m == "Start New Game":
                        HP = HP_MAX
                        score = 0
                        obs_speed = BASE_SPEED
                        spawn_interval = SPAWN_BASE_MS
                        obstacles.clear()
                        player_rect.midbottom = (PLAYER_START_X, FLOOR_Y)
                        player_vel_y = 0.0
                        pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
                else:
                    save_game()
                    pygame.quit()
                    exit()

            if event.key == pygame.K_UP:
                if player_rect.bottom >= FLOOR_Y - 1:
                    player_vel_y = JUMP_V
            if event.key == pygame.K_DOWN:
                is_ducking = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                is_ducking = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= 6
    if keys[pygame.K_RIGHT]:
        player_rect.x += 6

    if not game_over:
        player_vel_y += GRAVITY
        player_rect.y += player_vel_y
        if player_rect.bottom >= FLOOR_Y:
            player_rect.bottom = FLOOR_Y
            player_vel_y = 0

        for g in obstacles:
            for p in g["parts"]:
                p["rect"].x -= int(obs_speed)
            g_left = g["parts"][0]["rect"].left
            g_right = g["parts"][-1]["rect"].right
            g["rect"].left = g_left
            g["rect"].width = max(1, g_right - g_left)

        obstacles[:] = [g for g in obstacles if g["parts"][-1]["rect"].right > 0]

    if not game_over:
        phb = player_hitbox()
        for g in obstacles[:]:
            if (not g.get("passed", False)) and (g["rect"].right < player_rect.left):
                g["passed"] = True
                score += 1
                if score > best_score:
                    best_score = score
                save_game()
                if score % SPEED_INCREASE_EVERY == 0:
                    obs_speed = min(MAX_SPEED, obs_speed + SPEED_INCREMENT)
                    spawn_interval = max(SPAWN_MIN_MS, spawn_interval - 60)
                    pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
                    save_game()

            if phb.colliderect(g["rect"]):
                flash_red = 12
                try:
                    obstacles.remove(g)
                except ValueError:
                    pass
                HP -= 25
                save_game()
                if HP <= 0:
                    HP = 0
                    game_over = True
                break

    screen.blit(background, (0, 0))

    if flash_red > 0:
        flash_red -= 1
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((255, 0, 0, 90))
        screen.blit(s, (0, 0))

    if is_ducking and player_vel_y == 0:
        duck_img = pygame.transform.smoothscale(player_img, (PLAYER_W, DUCK_H))
        dr = duck_img.get_rect(midbottom=(player_rect.centerx, player_rect.bottom))
        screen.blit(duck_img, dr)
    else:
        pr = player_img.get_rect(midbottom=(player_rect.centerx, player_rect.bottom))
        screen.blit(player_img, pr)

    for g in obstacles:
        draw_group(g)

    draw_hp()
    score_txt = font_small.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_txt, (WIDTH - 160, 20))
    best_txt = font_small.render(f"Best: {best_score}", True, (255, 215, 0))
    screen.blit(best_txt, (WIDTH - 160, 50))

    pygame.display.flip()

    if game_over:
        save_game()
        action = game_over_screen()
        if action == "restart":
            HP = HP_MAX
            score = 0
            obs_speed = BASE_SPEED
            spawn_interval = SPAWN_BASE_MS
            obstacles.clear()
            player_rect.midbottom = (PLAYER_START_X, FLOOR_Y)
            player_vel_y = 0.0
            pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
            game_over = False
        elif action == "menu":
            m = main_menu()
            if m == "Continue":
                load_game()
            elif m == "Start New Game":
                HP = HP_MAX
                score = 0
                best_score = 0
                obs_speed = BASE_SPEED
                spawn_interval = SPAWN_BASE_MS
                obstacles.clear()
                player_rect.midbottom = (PLAYER_START_X, FLOOR_Y)
                player_vel_y = 0.0
                pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
                game_over = False
            else:
                pygame.quit()
                exit()
