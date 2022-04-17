import pygame as pg
from pygame.math import *
import math


class Player(pg.sprite.Sprite):
    """
    Player-controlled game object class
    """
    # TODO: create a settings file for constants
    SPEED = 2
    SIZE = (64, 64)

    def __init__(self, group, game):
        super().__init__(group)
        self.pos = Vector2(200, 200)
        # direction of player movement
        self.dir = Vector2(0, 0)
        # different walking animations
        self.images = [pg.transform.scale(pg.image.load("assets/player/player_{0}.png".format(x)), Player.SIZE) for x in
                                     ["front",
                                      "up",
                                      "down",
                                      "side_l",
                                      "side_r",
                                      "diag_dl",
                                      "diag_dr",
                                      "diag_ul",
                                      "diag_ur"]]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.game = game
        self.rect.update(0, 0, Player.SIZE[0], Player.SIZE[1])
        self.rect.center = self.pos.x, self.pos.y

    def update(self):
        # movement
        if self.dir.length() != 0:
            self.dir = self.dir.normalize()
        self.pos += Player.SPEED * self.dir
        self.rect.center = self.pos.x, self.pos.y

        # wall collision check
        while not pg.sprite.spritecollideany(self, self.game.walls) is None:
            self.image = None
            self.pos -= self.dir
            self.rect.center = self.pos.x, self.pos.y

        # walking animation
        if self.dir.x > 0 and self.dir.y > 0:
            self.image = self.images[6]
        elif self.dir.x > 0 and self.dir.y < 0:
            self.image = self.images[7]
        elif self.dir.x < 0 and self.dir.y > 0:
            self.image = self.images[5]
        elif self.dir.x < 0 and self.dir.y < 0:
            self.image = self.images[8]
        elif self.dir.x > 0 and self.dir.y == 0:
            self.image = self.images[4]
        elif self.dir.x < 0 and self.dir.y == 0:
            self.image = self.images[3]
        elif self.dir.x == 0 and self.dir.y > 0:
            self.image = self.images[2]
        elif self.dir.x == 0 and self.dir.y < 0:
            self.image = self.images[1]
        else:
            self.image = self.images[0]

        # reset direction vector
        self.dir.update(0, 0)

    # adds vector to player direction
    def add_dir(self, v):
        self.dir += v
