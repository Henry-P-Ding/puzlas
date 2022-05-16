import pygame as pg
from entity.game_entity import Entity
from entity.game_entity import DamageSource
from entity.particle import LavaParticle
from pygame.math import *
import random


class Fountain(Entity):
    """
    Ornament class with animated map backgrounds
    """
    ANIMATION_SPEED = 24
    ANIMATION_MODULUS = 3
    PARTICLE_CYCLE = 90
    PARTICLES_PER_CYCLE = 6

    def __init__(self, group, game_state, pos, color):
        self.particle_spawn_frames = [random.randint(0, Fountain.PARTICLE_CYCLE) for x in range(Fountain.PARTICLES_PER_CYCLE)]
        if color == "red":
            super().__init__(group, game_state, pos,
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/fountain/red_fountain/red_fountain_{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2"
                   ]]])
            self.red = True
        else:
            super().__init__(group, game_state, pos,
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/fountain/blue_fountain/blue_fountain_{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2"
                   ]]])
            self.red = False
        self.pos.y -= self.game_state.tile_size
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y + self.game_state.tile_size / 2, self.game_state.tile_size, self.game_state.tile_size)

    def update(self):
        self.frame_counter += 1
        self.animate()
        if self.red and self.frame_counter % Fountain.PARTICLE_CYCLE in self.particle_spawn_frames:
            self.game_state.particles.add(LavaParticle(self.game_state.all_sprites, self.game_state, 
                                                       Vector2(self.pos.x + 5 + random.random() * (self.rect.width - 10), 
                                                               self.pos.y + self.hit_box.height + random.random() * 4 - 2)))

    def animate(self):
        new_image = self.images[((self.frame_counter // Fountain.ANIMATION_SPEED) % Fountain.ANIMATION_MODULUS)]
        self.switch_image(new_image)

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)


class Spike(DamageSource):
    DAMAGE = 10
    DAMAGE_FLASH_TIME = 15
    COOL_DOWN = 180
    CYCLE_SPEED = 180
    ANIMATION_SPEED = 1
    ANIMATION_MODULUS = 4
    DAMAGE_FLASH_COLOR = (255, 255, 255)

    """Spike that pops up from the ground and does damage to entities"""
    def __init__(self, group, game_state, pos, damage, damage_list):
        super().__init__(group, game_state, pos, damage, Spike.COOL_DOWN, [], damage_list,
                         [pg.transform.scale(image, (64, 64)) for image in
                          [pg.image.load("assets/map_ornament/spike/spike_{0}.png".format(x)) for x in
                           ["0",
                            "1",
                            "2",
                            "3"
                            ]]]
                         )
        self.spike_up = False
        self.pos.y -= self.game_state.tile_size
        self.animation_counter = 0
        self.cool_down_counter = 0
        self.rect.update(self.pos.x, self.pos.y + self.game_state.tile_size, self.game_state.tile_size, self.game_state.tile_size)
        self.hit_box = self.rect.copy()

    def update(self):
        """Update behavior of projectile"""
        # movement update
        if self.cool_down_counter > 0:
            self.cool_down_counter -= 1
        if self.frame_counter % Spike.CYCLE_SPEED == 0:
            self.spike_up = not self.spike_up
            self.animation_counter = Spike.ANIMATION_SPEED * (Spike.ANIMATION_MODULUS - 1)
        self.animate()
        self.frame_counter += 1
        # collision with other sprites
        if self.spike_up and self.animation_counter == 0:
            for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False, collided=Entity.collided):
                self.collision_behavior(sprite)

    def collision_behavior(self, entity):
        if self.cool_down_counter == 0:
            for group in entity.groups():
                if group in self.damage_list:
                    if hasattr(entity, "on_damage"):
                        entity.on_damage(self)

    def on_damage(self, entity):
        self.cool_down_counter = 180
        self.damage_flash(entity, Spike.DAMAGE_FLASH_COLOR)
        
    def damaging(self, entity):
        if entity.frame_counter - entity.damage_frame <= Spike.DAMAGE_FLASH_TIME:
            self.damage_flash(entity, Spike.DAMAGE_FLASH_COLOR)

    def animate(self):
        if self.animation_counter > 0:
            self.animation_counter -= 1
            if self.spike_up:
                index = Spike.ANIMATION_MODULUS - ((self.animation_counter // Spike.ANIMATION_SPEED) % Spike.ANIMATION_MODULUS) - 1
            else:
                index = (self.animation_counter // Spike.ANIMATION_SPEED) % Spike.ANIMATION_MODULUS
            self.switch_image(self.images[index])

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y + self.game_state.tile_size, self.game_state.tile_size, self.game_state.tile_size)