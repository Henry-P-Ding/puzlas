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
        self.rect.center = self.pos.x, self.pos.y
        self.hit_box = self.rect.copy()
        self.frame_counter = 0

    def update(self):
        pass

    def animate(self):
        pass

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y


class HealthEntity(Entity):
    def __init__(self, group, game_state, pos, images, health):
        super().__init__(group, game_state, pos, images)
        self.health = health
        self.damaged = False
        self.damage_source = None
        self.damage_frame = self.frame_counter

    def on_damage(self, source):
        pass

    def death_behavior(self):
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

    def death_behavior(self):
        new_ability = self.ability.create_copy(self.game_state.player, [self.game_state.enemies, self.game_state.walls],
                                               [self.game_state.enemies])
        self.game_state.player.ability = new_ability
        self.kill()


class DamageSource(Entity):
    """Base class for all game entities that do damage."""
    DAMAGE_FLASH_ALPHA = 200

    def __init__(self, group, game_state, pos, damage, duration, kill_list, damage_list, images):
        super().__init__(group, game_state, pos, images)
        # numerical damage value
        self.damage = damage
        # duration that other entities are considered in damage state
        self.damage_duration = duration
        self.kill_list = kill_list
        self.damage_list = damage_list

    def on_damage(self, entity):
        """Behavior when sprite first takes damage fromm source"""
        pass

    def damaging(self, entity):
        """Loop behavior when sprite is taking damage from this source"""
        pass

    def damage_flash(self, entity, color):
        """Flashes the entity white to indicate damage"""
        entity_mask = pg.mask.from_surface(entity.image)
        damage_mask = entity_mask.to_surface(setcolor=color)
        damage_mask.set_colorkey((0, 0, 0))
        damage_mask.set_alpha(DamageSource.DAMAGE_FLASH_ALPHA)
        entity.image = entity.image.copy()
        entity.image.blit(damage_mask, (0, 0))
