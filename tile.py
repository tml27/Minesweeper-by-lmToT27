import pygame

class Tile:
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size
        self.is_bomb = False
        self.surround_bombs = 0
        self.revealed = False
        self.flagged = False
        self.hovered = False
    
    def SetTexture(self, texture):
        self.texture = pygame.transform.scale(texture, (self.size, self.size))