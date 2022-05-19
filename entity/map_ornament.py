from entity.game_entity import DamageSource
from entity.particle import LavaParticle
from entity.ability import *
from entity.wall import *
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
        self.particle_spawn_frames = [random.randint(0, Fountain.PARTICLE_CYCLE) for x in
                                      range(Fountain.PARTICLES_PER_CYCLE)]
        if color == "red":
            super().__init__(group, game_state, pos,
                             [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                              [pg.image.load("assets/map_ornament/fountain/red_fountain/red_fountain_{0}.png".format(x))
                               for x in
                               ["0",
                                "1",
                                "2"
                                ]]])
            self.red = True
        else:
            super().__init__(group, game_state, pos,
                             [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                              [pg.image.load(
                                  "assets/map_ornament/fountain/blue_fountain/blue_fountain_{0}.png".format(x)) for x in
                               ["0",
                                "1",
                                "2"
                                ]]])
            self.red = False
        self.pos.y -= self.game_state.tile_size
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y + self.game_state.tile_size / 2, self.game_state.tile_size,
                            self.game_state.tile_size)

    def update(self):
        self.frame_counter += 1
        self.animate()
        if self.red and self.frame_counter % Fountain.PARTICLE_CYCLE in self.particle_spawn_frames:
            self.game_state.particles.add(LavaParticle(self.game_state.all_sprites, self.game_state,
                                                       Vector2(
                                                           self.pos.x + 5 + random.random() * (self.rect.width - 10),
                                                           self.pos.y + self.hit_box.height + random.random() * 4 - 2)))
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y + self.game_state.tile_size / 2, self.game_state.tile_size,
                            self.game_state.tile_size)

    def animate(self):
        new_image = self.images[((self.frame_counter // Fountain.ANIMATION_SPEED) % Fountain.ANIMATION_MODULUS)]
        self.switch_image(new_image)

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)


class Movable(Entity):
    SPEED = 1

    def __init__(self, group, game_state, pos):
        super().__init__(group, game_state, pos, [pg.Surface([game_state.tile_size, game_state.tile_size])])
        self.image.fill((255, 255, 0))
        self.moving = False
        self.moving_timer = 0
        self.collision_direction = Vector2(0, 0)
        self.speed = Movable.SPEED
        self.moving_time = self.game_state.tile_size / self.speed

    def update(self):
        if self.moving_timer > 0:
            self.vel = self.collision_direction.copy() * self.speed
            self.moving_timer -= 1
        else:
            self.moving = False
            self.vel = Vector2(0, 0)

        self.pos += self.vel
        self.hit_box.center = self.pos.x, self.pos.y
        if pg.sprite.spritecollideany(self, self.game_state.walls, collided=Entity.collided) is not None:
            while pg.sprite.spritecollideany(self, self.game_state.walls, collided=Entity.collided) is not None:
                if self.vel.magnitude_squared() != 0:
                    self.pos -= self.vel.normalize()
                self.hit_box.center = self.pos.x, self.pos.y
        self.rect.center = self.pos.x, self.pos.y

    def start_moving(self):
        assert not self.moving, "Movable can not start moving while already moving"
        self.moving = True
        self.moving_timer = self.moving_time


class Door(Entity):
    ANIMATION_LENGTH = 30

    def __init__(self, group, game_state, pos1, pos2, size):
        super().__init__(group, game_state, (pos1+pos2)/2, [pg.Surface([game_state.tile_size, game_state.tile_size], pg.SRCALPHA), pg.Surface([1, 1], pg.SRCALPHA)])
        self.open = False
        self.image.fill((255, 255, 0, 255))
        self.interacting = False
        self.interact_timer = 0
        self.hit_box.size = pos2.x - pos1.x + self.game_state.tile_size, pos2.y - pos1.y + self.game_state.tile_size

    def update(self):
        if self.interact_timer > 0:
            self.animate()
            self.interact_timer -= 1
        else:
            self.interacting = False

        if self.open:
            self.game_state.walls.remove(self)
        else:
            self.game_state.walls.add(self)

        self.hit_box.center = self.pos.x, self.pos.y
        self.rect.center = self.pos.x, self.pos.y

    def interact(self):
        if not self.interacting:
            self.open = not self.open
            if self.hit_box.colliderect(self.game_state.player.wall_hit_box):
                bounds = pg.Rect(
                    self.game_state.level_creator.stage.x * self.game_state.tile_dim[0],
                    self.game_state.level_creator.stage.y * self.game_state.tile_dim[1],
                    self.game_state.tile_dim[0],
                    self.game_state.tile_dim[1]
                )

                possible_moves = Vector2(0, 0)
                for v in [Vector2(1, 0), Vector2(0, 1), Vector2(0, -1), Vector2(-1, 0)]:
                    tile_pos = Vector2(int(self.pos.x / self.game_state.tile_size), int(self.pos.y / self.game_state.tile_size))
                    coord = self.game_state.level_creator.stage.elementwise() * Vector2(self.game_state.tile_dim[0], self.game_state.tile_dim[1]) + tile_pos + v
                    if not bounds.collidepoint(coord.x, coord.y):
                        continue
                    tile = self.game_state.level_creator.level[int(coord.y)][int(coord.x)]
                    if tile == " ":
                        possible_moves = v
                        break

                assert possible_moves != Vector2(0, 0), "Must need a possible move for the player"

                while self.hit_box.colliderect(self.game_state.player.wall_hit_box):
                    self.game_state.player.pos -= possible_moves
                    self.game_state.player.wall_hit_box.center = self.game_state.player.pos.x, self.game_state.player.pos.y + self.game_state.player.hit_box.height / 4

            self.interact_timer = Door.ANIMATION_LENGTH

    def animate(self):
        if self.interact_timer > 0:
            if self.open:
                self.switch_image(self.images[1])
            else:
                self.switch_image(self.images[0])


class ArrowGun(Entity):

    def __init__(self, group, game_state, pos, damage, dir, firing_delay=60, constant_firing=False, aiming=False):
        super().__init__(group, game_state, pos, [pg.Surface([1, 1])])
        self.image.fill((0, 0, 0, 0))
        self.ability = ShootRoot(self, [self.game_state.walls, self.game_state.enemies, self.game_state.player_group], [self.game_state.enemies, self.game_state.player_group])
        self.ability.damage = damage
        self.firing_delay = firing_delay
        self.dir = dir.normalize()
        self.constant_firing = constant_firing
        self.aiming = aiming

    def update(self):
        self.frame_counter += 1
        if self.constant_firing and self.frame_counter % self.firing_delay == 0:
            if self.aiming:
                min_dist = self.game_state.game.window_size[0] * self.game_state.game.window_size[0] + self.game_state.game.window_size[1] * self.game_state.game.window_size[1]
                nearest_enemy = None
                for group in self.ability.damage_list:
                    for sprite in group:
                        dist = (sprite.pos - self.pos).length_squared()
                        if dist <= min_dist:
                            min_dist = dist
                            nearest_enemy = sprite
                dir = (nearest_enemy.pos - self.pos).normalize()
                self.fire(dir)
            else:
                self.fire(self.dir)

        self.hit_box.center = self.pos.x, self.pos.y
        self.rect.center = self.pos.x, self.pos.y

    def fire(self, dir):
        self.ability.activate(dir)


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
        self.rect.update(self.pos.x, self.pos.y + self.game_state.tile_size, self.game_state.tile_size,
                         self.game_state.tile_size)
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
                index = Spike.ANIMATION_MODULUS - (
                            (self.animation_counter // Spike.ANIMATION_SPEED) % Spike.ANIMATION_MODULUS) - 1
            else:
                index = (self.animation_counter // Spike.ANIMATION_SPEED) % Spike.ANIMATION_MODULUS
            self.switch_image(self.images[index])

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y + self.game_state.tile_size, self.game_state.tile_size,
                         self.game_state.tile_size)
