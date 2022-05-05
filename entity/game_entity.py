import pygame as pg
from pygame.math import *


class Entity(pg.sprite.Sprite):

    @staticmethod
    def collided(entity1, entity2):
        return entity1.hit_box.colliderect(entity2.hit_box)

    def __init__(self, group, game_state, pos, images):
        super().__init__(group)
        self.game_state = game_state
        self.pos = pos
        self.vel = Vector2(0, 0)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.hit_box = self.rect.copy()
        # offset between sprite rectangle center and pos/hit box center
        # TODO: add dict between sprite frames and offsets
        self.offset = Vector2(0, 0)
        self.rect.center = self.pos.x + self.offset.x, self.pos.y + self.offset.y
        self.hit_box = self.rect.copy()
        self.frame_counter = 0

    def update(self):
        pass

    def animate(self):
        pass


class HealthEntity(Entity):
    def __init__(self, group, game_state, pos, images, health):
        super().__init__(group, game_state, pos, images)
        self.health = health

    def death_behavior(self):
        print(f'{self} died')
        self.kill()


class AbilityEntity(HealthEntity):
    def __init__(self, group, game_state, pos, images, health, ability=None):
        super().__init__(group, game_state, pos, images, health)
        self.ability = ability
        self.ability_active = False
        self.ability_activate_frame = None

    def set_ability_active(self, val):
        assert isinstance(val, bool), "Must change ability_active to only bool"
        self.ability_active = val
