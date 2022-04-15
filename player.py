import pygame as pg
from pygame.math import *


class Player(pg.sprite.Sprite):
    def __init__(self, group, game):
        super().__init__(group)
        self.pos = Vector2(400, 400)
        self.dir = Vector2(0, 0)
        self.image = pg.Surface([100, 100])
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.game = game
        self.rect.update(self.pos.x, self.pos.y, 100, 100)

    def update(self):
        if self.dir.length() != 0:
            self.dir = self.dir.normalize()
        self.pos += 10 * self.dir
        self.rect.update(self.pos.x, self.pos.y, 100, 100)

        while len(pg.sprite.spritecollide(self, self.game.walls, False)) > 0:
            self.pos -= self.dir
            self.rect.update(self.pos.x, self.pos.y, 100, 100)

        self.dir.update(0, 0)

    def add_dir(self, v):
        self.dir += v
