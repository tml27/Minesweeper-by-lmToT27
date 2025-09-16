import pygame
import random
from tile import Tile
from queue import Queue
from utils import *

#________INIT__________

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 280, 460
ROWS, COLS = 24, 15
TILE_SIZE = 16
WIDTH_OFFSET = (SCREEN_WIDTH - COLS * TILE_SIZE) / 2
HEIGHT_OFFSET = 60

BOMB_AMOUNT = 80
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper by lmToT27")
clock = pygame.time.Clock()

hover_img = pygame.image.load(resource_path("assets/hover.png")).convert()
default_img = pygame.image.load(resource_path("assets/default.png")).convert()
bomb_img = pygame.image.load(resource_path("assets/bomb.png")).convert()
flower_img = pygame.image.load(resource_path("assets/flower.png")).convert()
flag_img = pygame.image.load(resource_path("assets/flag.png")).convert()
revealed_texture = []
for i in range(9):
    revealed_texture.append(pygame.image.load(resource_path("assets/" + str(i) + ".png")).convert())

grid = [[Tile(r, c, TILE_SIZE) for c in range(COLS)] for r in range(ROWS)]

running = True
game_started = False

mouse_held = False
held_button = None

remained_flags = BOMB_AMOUNT
remained_bombs = BOMB_AMOUNT
remained_tiles = ROWS * COLS - BOMB_AMOUNT

timer = 0
pass_1_sec = pygame.USEREVENT + 1

font = pygame.font.Font(resource_path("assets/04B_19.ttf"), 15)
color1 = [33, 255, 33]
color2 = [255, 33, 33]

default_button = pygame.image.load(resource_path("assets/default_button.png")).convert()
scale = 40 / default_button.get_height()
default_button = pygame.transform.scale_by(default_button, scale)
button_rect = default_button.get_rect(center = (SCREEN_WIDTH / 2, HEIGHT_OFFSET / 2))

hovered_button = pygame.image.load(resource_path("assets/hovered_button.png")).convert()
scale = 40 / hovered_button.get_height()
hovered_button = pygame.transform.scale_by(hovered_button, scale)
button_is_hovered = False

bombaed = False
won = False
lost = False

#------------------------

#___________Function____________

def UpdateGrid():
    for rows in grid:
        for tile in rows:
            if tile.revealed == False:
                if tile.flagged:
                    tile.SetTexture(flag_img) 
                elif tile.hovered:
                    tile.SetTexture(hover_img)
                else: 
                    tile.SetTexture(default_img)
            else:
                if tile.is_bomb:
                    tile.SetTexture(bomb_img if won == False else flower_img)
                else:
                    tile.SetTexture(revealed_texture[tile.surround_bombs])

def DrawGrid():
    for rows in grid:
        for tile in rows:
            screen.blit(tile.texture, (WIDTH_OFFSET + tile.col * tile.size, HEIGHT_OFFSET + tile.row * tile.size))

def DrawButton():
    screen.blit(hovered_button if button_is_hovered else default_button, button_rect)

def BFS(i, j):
    global remained_tiles
    q = Queue()
    q.put((i, j))
    grid[i][j].revealed = True
    remained_tiles -= 1
    while not q.empty():
        i, j = q.get()
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0: continue
                u = i + x
                v = j + y
                if 0 <= u < ROWS and 0 <= v < COLS:
                    if grid[u][v].revealed: continue
                    if grid[u][v].is_bomb: continue
                    if grid[u][v].surround_bombs == 0 or grid[i][j].surround_bombs == 0:
                        grid[u][v].revealed = True
                        remained_tiles -= 1
                        if grid[u][v].surround_bombs == 0: q.put((u, v))

def InitGame(i, j):
    ResetGame()
    pygame.time.set_timer(pass_1_sec, 1000)

    lst = [(r, c) for c in range(COLS) for r in range(ROWS)]
    for x in range(-1, 2):
        for y in range(-1, 2):
            u = i + x
            v = j + y
            if 0 <= u < ROWS and 0 <= v < COLS:
                lst.remove((u, v))
    
    bomb_list = random.sample(lst, BOMB_AMOUNT)
    for (x, y) in bomb_list:
        grid[x][y].is_bomb = True
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                u = x + dx
                v = y + dy
                if 0 <= u < ROWS and 0 <= v < COLS:
                    grid[u][v].surround_bombs += 1

    BFS(i, j)

def ResetGame():
    for x in range(ROWS):
        for y in range(COLS):
            grid[x][y].__init__(x, y, TILE_SIZE)
    global remained_flags, remained_bombs, timer, game_started, won, lost, remained_tiles, bombaed
    remained_flags, remained_bombs, timer = BOMB_AMOUNT, BOMB_AMOUNT, 0
    remained_tiles = ROWS * COLS - BOMB_AMOUNT
    game_started = False
    won, lost, bombaed = False, False, False
    pygame.time.set_timer(pass_1_sec, 0)

def PrintTime():
    ratio = min(timer / 240, 1)
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    text = font.render("Time: " + str(timer), True, (r, g, b))
    screen.blit(text, text.get_rect(bottomright = (SCREEN_WIDTH - WIDTH_OFFSET, HEIGHT_OFFSET - 10)))

def PrintRemainedFlags():
    ratio = min(remained_flags / BOMB_AMOUNT, 1)
    r = int(color2[0] * (1 - ratio) + color1[0] * ratio)
    g = int(color2[1] * (1 - ratio) + color1[1] * ratio)
    b = int(color2[2] * (1 - ratio) + color1[2] * ratio)
    text = font.render("Flags: " + str(remained_flags), True, (r, g, b))
    screen.blit(text, text.get_rect(bottomleft = (WIDTH_OFFSET, HEIGHT_OFFSET - 10)))

def Hovering(pos):
    global button_is_hovered
    pos_x, pos_y = pos
    j = (int)((pos_x - WIDTH_OFFSET) // TILE_SIZE)
    i = (int)((pos_y - HEIGHT_OFFSET) // TILE_SIZE)
    if 0 <= i < ROWS and 0 <= j < COLS:
        grid[i][j].hovered = True
    if button_rect.collidepoint(pos):
        button_is_hovered = True

def ResetHovering():
    global button_is_hovered
    for i in range(ROWS):
        for j in range(COLS):
            grid[i][j].hovered = False
    button_is_hovered = False

#---------------------------------

while running:
    delta = clock.tick(144) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        if event.type == pass_1_sec:
            timer += 1
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (1, 3):
                mouse_held = True
                held_button = event.button
                Hovering(event.pos)

        if event.type == pygame.MOUSEMOTION and mouse_held == True:
            ResetHovering()
            Hovering(event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            ResetHovering()
            if held_button != None:
                if held_button == 1:
                    if button_rect.collidepoint(event.pos):
                        ResetGame()
                    pos_x, pos_y = event.pos
                    j = (int)((pos_x - WIDTH_OFFSET) // TILE_SIZE)
                    i = (int)((pos_y - HEIGHT_OFFSET) // TILE_SIZE)
                    if 0 <= i < ROWS and 0 <= j < COLS and not (won or lost):
                        if not game_started:
                            InitGame(i, j)
                            game_started = True
                        else:
                            if not(grid[i][j].revealed or grid[i][j].flagged): 
                                if grid[i][j].is_bomb: bombaed = True
                                else: BFS(i, j)
                elif game_started:
                    pos_x, pos_y = event.pos
                    j = (int)((pos_x - WIDTH_OFFSET) // TILE_SIZE)
                    i = (int)((pos_y - HEIGHT_OFFSET) // TILE_SIZE)
                    if 0 <= i < ROWS and 0 <= j < COLS and not grid[i][j].revealed and not (won or lost):
                        if not grid[i][j].flagged and remained_flags > 0:
                            grid[i][j].flagged = True
                            remained_flags -= 1
                        elif grid[i][j].flagged == True:
                            grid[i][j].flagged = False
                            remained_flags += 1
                held_button = None
            mouse_held = False
    
    if bombaed:
        lost = True
        pygame.time.set_timer(pass_1_sec, 0)
        for x in range(ROWS):
            for y in range(COLS):
                if grid[x][y].is_bomb:
                    grid[x][y].revealed = True

    if remained_tiles == 0:
        won = True
        pygame.time.set_timer(pass_1_sec, 0)
        for i in range(ROWS):
            for j in range(COLS):
                grid[i][j].revealed = True

    UpdateGrid()

    screen.fill("#242424")
    DrawGrid()
    PrintTime()
    PrintRemainedFlags()
    DrawButton()
                

    pygame.display.update()
pygame.quit()