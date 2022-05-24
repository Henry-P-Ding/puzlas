import pygame as pg
from pygame.math import *
from entity.game_entity import AbilityEntity
from entity.game_entity import Entity
from gui import *
from entity.particle import *
from entity.map_ornament import Movable


class Player(AbilityEntity):
    """
    Player-controlled game object class
    """
    # TODO: create a settings file for constants
    SPEED = 8
    DISPLAY_SIZE = (60, 80)
    WALK_DUST_RATE = 4
    DEATH_ANIMATION_LENGTH = 120
    ANIMATION_SPEED = {
        "standing": 12,
        "moving": 4,
        "slashing": 5
    }

    def __init__(self, group, game_state):
        super().__init__(group=group,
                         game_state=game_state,
                         pos=Vector2(200, 200),
                         images=
                         [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                          [pg.image.load("assets/player/player_{0}.png".format(x)) for x in
                           ["0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7",
                            "8",
                            "9",
                            "10",
                            "11",
                            "12",
                            "13",
                            "14",
                            "15",
                            "16",
                            "17",
                            "18"
                            ]]],
                         health=100)
        # hit box for walls only, allows the "head" of the player to be drawn above walls
        self.wall_hit_box = pg.Rect(self.hit_box.x, self.hit_box.y + self.hit_box.height / 2,
                                    self.hit_box.width, self.hit_box.height / 2)
        # direction of player movement, always a unit vector
        self.dir = Vector2(0, 0)
        self.speed = Player.SPEED
        self.moving = False
        # different walking animations
        self.facing_right = True
        # checks whether ability is active or not
        self.primary_ability_active = False
        self.secondary_ability_active = False
        # melee slash
        self.slashing = False
        self.slash_counter = 0
        self.ability = None
        self.secondary_ability = None

        # player health bar
        self.max_health = 100
        self.health_bar = FractionalBar(group=self.game_state.gui_sprites,
                                        pos=Vector2(16, 40),
                                        size=Vector2(256, 32),
                                        border_width=8,
                                        indicator=self.health,
                                        indicator_max=self.max_health,
                                        bar_color=(255, 0, 0),
                                        background_color=(255, 255, 255, 100),
                                        border_color=(255, 255, 255))

        # death animation counter
        self.death_animation_counter = -1
        self.dead = False

    @staticmethod
    def wall_collided(player, wall):
        return player.wall_hit_box.colliderect(wall.hit_box)

    def update(self):
        # dead
        if self.death_animation_counter > 0:
            self.dead = True
            self.switch_image(
                self.images[2 - int(self.death_animation_counter / Player.DEATH_ANIMATION_LENGTH * 2) + 16])
            self.death_animation_counter -= 1
            return
        elif self.death_animation_counter == 0:
            self.kill()
            self.game_state.game.game_state_manager.switch_state_from_pool("quit_to_menu")

        self.dir = Vector2(self.game_state.controls.key_presses[pg.K_d] - self.game_state.controls.key_presses[pg.K_a],
                           self.game_state.controls.key_presses[pg.K_s] - self.game_state.controls.key_presses[pg.K_w])

        self.animate()
        if self.damaged:
            self.damage_source.damaging(self)
            if self.frame_counter - self.damage_frame >= self.damage_source.damage_duration:
                self.damaged = False
        else:
            self.rooted = False
        self.health_bar.change_indicator(self.health)

        # movement
        if self.dir.magnitude_squared() != 0:
            self.dir = self.dir.normalize()
            self.moving = True
        else:
            self.moving = False
        self.vel = self.speed * self.dir
        self.pos += self.vel

        self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4
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
                adj_pos = self.pos + self.speed * x
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
            if self.vel.magnitude_squared() == 0:
                self.moving = False
            self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4

        collided_movables = pg.sprite.spritecollide(self, self.game_state.movables, False, collided=Player.wall_collided)
        if len(collided_movables) > 0:
            for movable in collided_movables:
                assert isinstance(movable, Movable), "Movable group must only contain Movable objects"
                x_collision = False
                y_collision = False
                collision_direction = Vector2(0, 0)
                while self.wall_hit_box.colliderect(movable.hit_box):
                    self.pos -= self.dir
                    self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 4
                # algorithm to include sliding along walls
                # 0: left, 1: up, 2: right, 3: down
                adj = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
                for i, x in enumerate(adj):
                    adj_pos = self.pos + self.speed * x
                    self.wall_hit_box.center = adj_pos.x, adj_pos.y + self.hit_box.height / 4
                    if self.wall_hit_box.colliderect(movable.hit_box):
                        if i % 2 == 0:
                            x_collision = True
                        else:
                            y_collision = True
                        collision_direction += x

                if movable.moving:
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
                else:
                    movable.collision_direction = collision_direction.copy()
                    movable.start_moving()

        self.hit_box.center = self.pos.x, self.pos.y

        # walking particles
        if self.vel.magnitude_squared() != 0 and self.frame_counter % Player.WALK_DUST_RATE == 0:
            if self.vel.y == 0:
                dust_pos = Vector2(self.pos.x + random.randint(-self.hit_box.width / 5, self.hit_box.width / 5),
                                   self.pos.y + (self.hit_box.height / 2 + 5) + random.randint(0, 2))
            else:
                dust_pos = Vector2(self.pos.x + random.randint(-self.hit_box.width / 5, self.hit_box.width / 5),
                                   self.pos.y - self.vel.y / abs(self.vel.y) * (
                                               self.hit_box.height / 2 + 5) + random.randint(0, 2))

            self.game_state.particles.add(WalkDust(self.game_state.all_sprites, self.game_state, dust_pos))

        # activates player ability
        if self.primary_ability_active:
            self.ability.activate((self.game_state.mouse_pos - self.pos).normalize())
        elif self.secondary_ability_active:
            self.secondary_ability.activate((self.game_state.mouse_pos - self.pos).normalize())

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
        # TODO: remove hardcoded moduli and offsets
        """Animates player sprite."""
        if self.slashing:
            self.facing_right = (self.game_state.mouse_pos - self.pos).x > 0
            if self.slash_counter > 0:
                if self.facing_right:
                    self.switch_image(
                        self.images[((self.slash_counter // Player.ANIMATION_SPEED["slashing"]) % 3) + 12])
                else:
                    self.switch_image(pg.transform.flip(
                        self.images[((self.slash_counter // Player.ANIMATION_SPEED["slashing"]) % 3) + 12], True,
                        False))
                self.slash_counter -= 1
            else:
                self.slashing = False
        elif self.moving:
            if self.facing_right:
                self.switch_image(self.images[((self.frame_counter // Player.ANIMATION_SPEED["moving"]) % 6) + 6])
            else:
                self.switch_image(
                    pg.transform.flip(self.images[((self.frame_counter // Player.ANIMATION_SPEED["moving"]) % 6) + 6],
                                      True, False))
        else:  # staying still animation
            if self.facing_right:
                self.switch_image(self.images[(self.frame_counter // Player.ANIMATION_SPEED["standing"]) % 6])
            elif not self.facing_right:  # storing animation
                self.switch_image(
                    pg.transform.flip(self.images[((self.frame_counter // Player.ANIMATION_SPEED["standing"]) % 6)],
                                      True, False))

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
        # update player damage status
        if not self.dead:
            self.damaged = True
            self.damage_frame = self.frame_counter
            self.damage_source = source
            self.take_damage(source.damage)
            self.damage_source.on_damage(self)
            self.game_state.shake_camera(15)

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        # TODO: remove hardcoded
        self.game_state.shake_camera(15)

    def death_behavior(self):
        self.dead = True
        self.death_animation_counter = Player.DEATH_ANIMATION_LENGTH
