import pygame as pg
from pygame.math import *


class Player(pg.sprite.Sprite):
    """
    Player-controlled game object class
    """
    # TODO: create a settings file for constants
    SPEED = 5
    DISPLAY_SIZE = (60, 60)

    def __init__(self, group, game_state):
        super().__init__(group)
        self.pos = Vector2(200, 200)
        # direction of player movement
        self.dir = Vector2(0, 0)
        # different walking animations
        self.images = [pg.transform.scale(pg.image.load("assets/player/player_{0}.png".format(x)), Player.DISPLAY_SIZE) for x in
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
        self.game_state = game_state
        self.rect.size = (Player.DISPLAY_SIZE[0], Player.DISPLAY_SIZE[1])
        self.rect.center = self.pos.x, self.pos.y

    def update(self):
        # movement
        if self.dir.length() != 0:
            self.dir = self.dir.normalize()
        self.pos += Player.SPEED * self.dir
        self.rect.center = self.pos.x, self.pos.y

        # wall collision check
        if pg.sprite.spritecollideany(self, self.game_state.walls) is not None:
            while pg.sprite.spritecollideany(self, self.game_state.walls) is not None:
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
                if pg.sprite.spritecollideany(self, self.game_state.walls):
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

    # check player colliding with edge of screen
    def check_screen_bounds(self):
        if self.pos.x > self.game_state.game.window_size[0]:
            return Vector2(1, 0)
        elif self.pos.x < 0:
            return Vector2(-1, 0)
        elif self.pos.y > self.game_state.game.window_size[1]:
            return Vector2(0, 1)
        elif self.pos.y < 0:
            return Vector2(0, -1)

        return
