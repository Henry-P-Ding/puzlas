import pygame as pg
from pygame.math import *
import random
import math


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
    BURN = 120

    def __init__(self, group, game_state, dir, pos, size, speed, damage, kill_list, damage_list):
        super().__init__(group, game_state, dir, pos, size, speed)
        self.image.fill((255, 120, 0))
        # list of sprites that will kill the fireball if collided
        self.kill_list = kill_list
        # list of sprites fireball will do damage to
        self.damage_list = damage_list
        self.damage = damage
        self.damage_duration = FireBall.BURN

    def collision_behavior(self, sprite):
        for group in sprite.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(sprite, "on_damage"):
                    sprite.on_damage(self)

    # TODO: add to projectile parent class
    def on_damage(self, sprite):
        sprite.image.fill((255, 255, 255))

    # TODO: make the enemy light on fire
    def damaging(self, sprite):
        sprite.image.fill((255, 0, 0))
        if sprite.frame_counter % 60 == 0:
            # burns enemy for damage over time
            sprite.health -= 2


class Ability:
    def __init__(self, sprite):
        self.sprite = sprite
        self.can_activate = True

    def activate(self, dir):
        pass


class ShootFireBall(Ability):
    # TODO: create global settings for fire ball ability
    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite)
        self.prev_frame = 0
        self.fireballs = []
        self.kill_list = kill_list
        self.damage_list = damage_list

    def activate(self, dir):
        if self.can_activate and len(self.fireballs) < 15:
            self.shoot(dir)
            self.prev_frame = self.sprite.frame_counter * 1
            self.can_activate = False

        else:
            if self.sprite.frame_counter - self.prev_frame > 5:
                self.can_activate = True

        for fire_ball in self.fireballs:
            if len(fire_ball.groups()) == 0:
                self.fireballs.remove(fire_ball)

    def shoot(self, dir):
        spray_angle = random.uniform(-0.1, 0.1)
        spray_vector = Vector2(math.cos(spray_angle), math.sin(spray_angle))
        randomized_dir = Vector2(dir.x * spray_vector.x - dir.y * spray_vector.y, dir.x * spray_vector.y + dir.y * spray_vector.x)
        self.fireballs.append(FireBall(self.sprite.game_state.all_sprites,
                                       self.sprite.game_state, randomized_dir,
                                       Vector2(self.sprite.pos.x, self.sprite.pos.y),
                                       (10, 10),
                                       10,
                                       10,
                                       self.kill_list,
                                       self.damage_list))
