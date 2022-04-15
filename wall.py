import pygame as pg
from pygame.math import *


class Wall(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.pos = Vector2(0, 0)
        self.dir = Vector2(0, 0)
        self.image = pg.Surface([100, 100])
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()

    def update(self):
        pass



