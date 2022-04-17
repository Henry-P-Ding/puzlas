import pygame as pg
from pygame.math import *


class Enemy(pg.sprite.Sprite):
    """
    Generic enemies class that attacks player
    """
    def __init__(self, group, game, pos, size, steering_rate, speed):
        super().__init__(group)
        # tuple containing (width, height) of the enemies
        self.size = size
        # rate of turing towards the player
        self.steering_rate = steering_rate
        self.speed = speed
        self.pos = pos
        self.dir = Vector2(0, 0)
        # image of enemies
        self.image = pg.Surface([self.size[0], self.size[1]])
        self.image.fill((100, 100, 100))
        # pygame rectangle object of enemies
        self.rect = self.image.get_rect()
        # game object containing the enemies
        self.game = game
        self.rect.update(0, 0, self.size[0], self.size[1])
        self.rect.center = self.pos.x, self.pos.y

    def update(self):
        pass

    def attack(self):
        pass

    def steer(self, min_dist=0, max_dist=None):
        """
        Steering behavior for movement towards player.
        """
        displacement = (self.game.player.pos - self.pos)
        if max_dist is None:
            if min_dist * min_dist < displacement.magnitude_squared():
                self.dir = displacement.normalize()
        else:
            if min_dist * min_dist < displacement.magnitude_squared() < max_dist * max_dist:
                self.dir = displacement.normalize()

    def move(self):
        """
        Movement method to move towards player.
        """
        prev_pos = self.pos.copy()
        if not pg.sprite.collide_rect(self, self.game.player):
            self.pos += self.speed * self.dir
            self.rect.center = self.pos.x, self.pos.y

        while not pg.sprite.spritecollideany(self, self.game.walls) is None:
            self.pos -= self.dir
            self.rect.center = self.pos.x, self.pos.y

        self.dir.update(0, 0)


class Melee(Enemy):
    def __init__(self, group, game, pos, size, steering_rate, speed, range):
        super().__init__(group, game, pos, size, steering_rate, speed)
        self.range = range

    def update(self):
        self.steer(min_dist=self.range)
        self.move()
        self.attack()

    def attack(self):
        if (self.pos - self.game.player.pos).magnitude_squared() < self.range * self.range:
            print("melee attack!")
