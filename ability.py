import pygame as pg
from pygame.math import *
from player import *
from enemy import *
from wall import *


class Projectile(pg.sprite.Sprite):
    def __init__(self, group, game_state, dir, pos, size, speed):
        super().__init__(group)
        # tuple containing (width, height) of projectile rectangle
        self.size = size
        # movement speed
        self.speed = speed
        # pos
        self.pos = pos
        # direction of movement of projectile
        self.dir = dir
        # image of projectile
        self.image = pg.Surface(list(self.size))
        self.image.fill((255, 255, 255))
        # pygame rectangle of projectile hit box
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        # game object with game state
        self.game_state = game_state

    def update(self):
        """Update behavior of projectile"""
        self.pos += self.dir * self.speed
        self.rect.center = self.pos.x, self.pos.y
        # collision with other sprites
        for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False):
            self.collision_behavior(sprite)

        # out of screen bounds then deleted
        if not (0 < self.pos.x < self.game_state.game.window_size[0] and 0 < self.pos.y < self.game_state.game.window_size[1]):
            self.kill()

    def collision_behavior(self, sprite):
        pass


class FireBall(Projectile):
    """Fireball class"""
    def __init__(self, group, game_state, dir, pos, size, speed):
        super().__init__(group, game_state, dir, pos, size, speed)
        self.image.fill((255, 120, 0))

    def collision_behavior(self, sprite):
        if isinstance(sprite, Wall):
            self.kill()

class Ability:
    def __init__(self, sprite):
        self.sprite = sprite
        self.can_activate = True

    def activate(self, dir):
        pass



class ShootFireBall(Ability):
    def __init__(self, sprite):
        super().__init__(sprite)
        self.prev_frame = 0
        self.fire_balls = []

    def activate(self, dir):
        if self.can_activate and len(self.fire_balls) < 5:
            self.shoot(dir)
            self.prev_frame = self.sprite.frame_counter * 1
            self.can_activate = False

        else:
            if self.sprite.frame_counter - self.prev_frame > 5:
                self.can_activate = True

        for fire_ball in self.fire_balls:
            if len(fire_ball.groups()) == 0:
                self.fire_balls.remove(fire_ball)

    def shoot(self, dir):
        self.fire_balls.append(FireBall(self.sprite.game_state.all_sprites, self.sprite.game_state, dir,
                                        Vector2(self.sprite.pos.x, self.sprite.pos.y), (10, 10), 10))


