import pygame as pg
from pygame.math import *


class Player(pg.sprite.Sprite):
    """
    Player-controlled game object class
    """
    # TODO: create a settings file for constants
    SPEED = 5
    DISPLAY_SIZE = (60, 60)

    def __init__(self, group, game):
        super().__init__(group)
        self.pos = Vector2(200, 200)
        # direction of player movement
        self.dir = Vector2(0, 0)
        # different walking animations
        self.images = [pg.transform.scale(pg.image.load("assets/player/tile{0}.png".format(x)), Player.DISPLAY_SIZE) for
                       x in
                       ["000",
                        "001",
                        "002",
                        "003",
                        "004",
                        "005",
                        "006",
                        "007",
                        "008",
                        "009",
                        "010",
                        "011",
                        "012",
                        "013",
                        "014",
                        "015",
                        "024",
                        "025",
                        "026"]]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.game = game
        self.rect.size = (Player.DISPLAY_SIZE[0], Player.DISPLAY_SIZE[1])
        # self.image.
        self.rect.center = self.pos.x, self.pos.y
        self.frametimer = 0
        self.facing_right = True

    def update(self):
        # movement
        if self.dir.length() != 0:
            self.dir = self.dir.normalize()
        self.pos += Player.SPEED * self.dir
        self.rect.center = self.pos.x, self.pos.y

        # wall collision check
        if pg.sprite.spritecollideany(self, self.game.walls) is not None:
            while pg.sprite.spritecollideany(self, self.game.walls) is not None:
                self.pos -= self.dir
                self.rect.center = self.pos.x, self.pos.y
            # algorithm to include sliding along walls
            # 0: left, 1: up, 2: right, 3: down
            adj = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
            x_collision = False
            y_collision = False
            for i, x in enumerate(adj):
                adj_pos = self.pos + Player.SPEED * x
                self.rect.center = adj_pos.x, adj_pos.y
                if pg.sprite.spritecollideany(self, self.game.walls):
                    if i % 2 == 0:
                        x_collision = True
                    else:
                        y_collision = True

            # only allow sliding along walls if this is not a corner collision
            if x_collision and not y_collision:
                self.pos += Player.SPEED * Vector2(0, self.dir.y)
            elif not x_collision and y_collision:
                self.pos += Player.SPEED * Vector2(self.dir.x, 0)
            self.rect.center = self.pos.x, self.pos.y

        # walking animation
        if self.dir.x > 0:  # facing right walking animation
            self.image = self.images[((self.frametimer // 5) % 6) + 6]
            self.facing_right = True
        elif self.dir.x < 0:  # facing left walking animation
            self.image = pg.transform.flip(self.images[((self.frametimer // 5) % 6) + 6], True, False)
            self.facing_right = False
        elif self.dir.x == 0 and self.dir.y == 0:  # staying still animation
            if self.facing_right:
                self.image = self.images[(self.frametimer // 15) % 6]
            elif not self.facing_right:  # storing animation
                self.image = pg.transform.flip(self.images[((self.frametimer // 5) % 6)], True, False)
        elif self.dir.y > 0:  # up and down animation
            if self.facing_right:
                self.image = self.images[((self.frametimer // 15) % 6)+6]
            elif not self.facing_right:  # storing animation
                self.image = pg.transform.flip(self.images[(((self.frametimer // 5) % 6))+6], True, False)
        elif self.dir.y < 0:  # up and down animation
            if self.facing_right:
                self.image = self.images[((self.frametimer // 15) % 6)+6]
            elif not self.facing_right:  # storing animation
                self.image = pg.transform.flip(self.images[(((self.frametimer // 5) % 6))+6], True, False)
        self.frametimer += 1

        # reset direction vector
        self.dir.update(0, 0)

    # adds vector to player direction
    def add_dir(self, v):
        self.dir += v

    # check player colliding with edge of screen
    def check_screen_bounds(self):
        if self.pos.x > self.game.window_size[0]:
            return Vector2(1, 0)
        elif self.pos.x < 0:
            return Vector2(-1, 0)
        elif self.pos.y > self.game.window_size[1]:
            return Vector2(0, 1)
        elif self.pos.y < 0:
            return Vector2(0, -1)

        return
