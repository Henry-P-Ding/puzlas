import pygame as pg
from pygame.math import *
from entity.game_entity import AbilityEntity
from entity.game_entity import Entity
from gui import *


class Player(AbilityEntity):
    """
    Player-controlled game object class
    """
    # TODO: create a settings file for constants
    SPEED = 8
    DISPLAY_SIZE = (60, 80)
    ANIMATION_SPEED = {
        "standing": 12,
        "moving": 4,
        "slashing": 5
    }

    def __init__(self, group, game_state):
        super().__init__(group=group,
                         game_state=game_state,
                         pos=Vector2(200, 200),
                         images=[pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in [pg.image.load("assets/player/tile{0}.png".format(x)) for x in ["000", "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "024", "025", "026"]]],
                         health=100)
        # hit box for walls only, allows the "head" of the player to be drawn above walls
        self.wall_hit_box = pg.Rect(self.hit_box.x, self.hit_box.y + self.hit_box.height / 2,
                                    self.hit_box.width, self.hit_box.height / 2)
        # direction of player movement, always a unit vector
        self.dir = Vector2(0, 0)
        # different walking animations
        self.facing_right = True
        # checks whether ability is active or not
        self.ability_active = False
        # melee slash
        self.slashing = False
        self.slash_counter = 0
        self.ability = None

        # player health bar
        self.max_health = 100
        self.health_bar = IndicatorBar(group=self.game_state.gui_sprites,
                                       pos=Vector2(16, 32),
                                       size=Vector2(256, 32),
                                       border_width=5,
                                       indicator=self.health,
                                       indicator_max=self.max_health,
                                       bar_color=(255, 0, 0),
                                       background_color=(255, 255, 255, 100),
                                       border_color=(255, 255, 255))

    @staticmethod
    def wall_collided(player, wall):
        return player.wall_hit_box.colliderect(wall.hit_box)

    def update(self):
        self.dir = Vector2(self.game_state.controls.key_presses[pg.K_d] - self.game_state.controls.key_presses[pg.K_a],
                           self.game_state.controls.key_presses[pg.K_s] - self.game_state.controls.key_presses[pg.K_w])

        self.animate()
        if self.damaged:
            self.damage_source.damaging(self)
            if self.frame_counter - self.damage_frame >= self.damage_source.damage_duration:
                self.damaged = False
        self.health_bar.change_indicator(self.health)

        # movement
        if self.dir.magnitude_squared() != 0:
            self.dir = self.dir.normalize()
        self.vel = Player.SPEED * self.dir
        self.pos += self.vel

        self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4

        # wall collision check with player hit box specifically
        if pg.sprite.spritecollideany(self, self.game_state.walls, collided=Player.wall_collided) is not None:
            while pg.sprite.spritecollideany(self, self.game_state.walls, collided=Player.wall_collided) is not None:
                self.pos -= self.dir
                self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4
            # algorithm to include sliding along walls
            # 0: left, 1: up, 2: right, 3: down
            adj = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
            x_collision = False
            y_collision = False
            for i, x in enumerate(adj):
                adj_pos = self.pos + Player.SPEED * x
                self.wall_hit_box.center = adj_pos.x, adj_pos.y + self.hit_box.height / 4
                if pg.sprite.spritecollideany(self, self.game_state.walls, collided=Player.wall_collided):
                    if i % 2 == 0:
                        x_collision = True
                    else:
                        y_collision = True

            # only allow sliding along walls if this is not a corner collision
            if x_collision and not y_collision:
                self.vel.x = 0
                self.pos += self.vel
            elif not x_collision and y_collision:
                self.vel.y = 0
                self.pos += self.vel
            else:
                self.vel = Vector2(0, 0)
            self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4
        self.hit_box.center = self.pos.x, self.pos.y

        # activates player ability
        if self.ability_active:
            self.ability.activate((self.game_state.mouse_pos - self.pos).normalize())

        # animate player sprite
        self.frame_counter += 1
        if self.vel.x > 0:
            self.facing_right = True
        elif self.vel.x < 0:
            self.facing_right = False

        self.rect.center = self.pos.x, self.pos.y

        if self.health <= 0:
            self.death_behavior()

    def animate(self):
        # TODO: remove hardcoded moduli
        """Animates player sprite."""
        if self.slashing:
            self.facing_right = (self.game_state.mouse_pos - self.pos).x > 0
            if self.slash_counter > 0:
                if self.facing_right:
                    self.switch_image(self.images[((self.slash_counter // Player.ANIMATION_SPEED["slashing"]) % 3) + 12])
                else:
                    self.switch_image(pg.transform.flip(
                        self.images[((self.slash_counter // Player.ANIMATION_SPEED["slashing"]) % 3) + 12], True, False))
                self.slash_counter -= 1
            else:
                self.slashing = False
        elif self.vel.length_squared() != 0:
            if self.facing_right:
                self.switch_image(self.images[((self.frame_counter // Player.ANIMATION_SPEED["moving"]) % 6) + 6])
            else:
                self.switch_image(pg.transform.flip(self.images[((self.frame_counter // Player.ANIMATION_SPEED["moving"]) % 6) + 6], True, False))
        else:  # staying still animation
            if self.facing_right:
                self.switch_image(self.images[(self.frame_counter // Player.ANIMATION_SPEED["standing"]) % 6])
            elif not self.facing_right:  # storing animation
                self.switch_image(pg.transform.flip(self.images[((self.frame_counter // Player.ANIMATION_SPEED["standing"]) % 6)], True, False))

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y

    def check_screen_bounds(self):
        """manages behavior if player collides with edge of screen"""
        if self.pos.x > self.game_state.game.window_size[0]:
            return Vector2(1, 0)
        elif self.pos.x < 0:
            return Vector2(-1, 0)
        elif self.pos.y > self.game_state.game.window_size[1]:
            return Vector2(0, 1)
        elif self.pos.y < 0:
            return Vector2(0, -1)
        return

    def add_dir(self, v):
        """Adds vector to player direction"""
        self.dir += v

    def on_damage(self, source):
        """Behavior when enemy takes damage."""
        self.damaged = True
        self.damage_frame = self.frame_counter
        self.damage_source = source
        self.health -= self.damage_source.damage
        self.damage_source.on_damage(self)

    def death_behavior(self):
        print('game lost')
        # TODO: make a game over scree
        self.game_state.game.stop()

