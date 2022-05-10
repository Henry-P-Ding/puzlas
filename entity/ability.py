import pygame as pg
from pygame.math import *
from entity.game_entity import Entity
import random
import math


class DamageSource(Entity):
    """Base class for all game entities that do damage."""

    def __init__(self, group, game_state, pos, damage, duration, images):
        super().__init__(group, game_state, pos, images)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        # numerical damage value
        self.damage = damage
        # duration that other entities are considered in a damage state
        self.damage_duration = duration

    def on_damage(self, entity):
        """Behavior when sprite first takes damage fromm source"""
        pass

    def damaging(self, entity):
        """Loop behavior when sprite is taking damage from this source"""
        pass


class MeleeAttack(DamageSource):
    """Melee attack damage source - damages entities within a sector"""

    @staticmethod
    def sector_collide(attack, entity):
        """
        Collision logic for this attack's sector and an entity.

        Note: the center of the entity must be in the sector for collision to be detected.
        """
        assert isinstance(attack, MeleeAttack), "sector_collide can only be used with melee attacks"
        rel = entity.pos - attack.pos
        # finds angle relative to horizontal of enemy
        if rel.x == 0:
            angle = math.pi / 2 if rel.y > 0 else -math.pi / 2
        else:
            angle = math.atan(rel.y / rel.x) if rel.x > 0 else math.atan(rel.y / rel.x) + math.pi
        # checks if entity angle is within allowed range
        if attack.angle_min < angle < attack.angle_max:
            # checks entity is within distance
            if rel.magnitude_squared() < attack.range_squared:
                return True

        return False

    def __init__(self, group, game_state, pos, damage, range, dir, spread, duration, kill_list, damage_list):
        super().__init__(group, game_state, pos, damage, duration)
        # melee attack has no image, the player changes to a slashing animation instead
        self.image = pg.Surface((1, 1), pg.SRCALPHA)
        # filled image with a transparent color
        self.image.fill((0, 0, 0, 0))
        # stores range of the melee attack
        self.range_squared = range * range
        # determines angle relative of horizontal of attack
        if dir.x == 0:
            angle = math.pi / 2 if dir.y > 0 else -math.pi / 2
        else:
            angle = math.atan(dir.y / dir.x) if dir.x > 0 else math.atan(dir.y / dir.x) + math.pi
        # min and max angle considered within the angle boundaries based off of the attack angle
        self.angle_min, self.angle_max = angle - spread, angle + spread

        # list of sprites groups that will kill this MeleeAttack object
        self.kill_list = kill_list
        # list of sprite groups this ability will damage to
        self.damage_list = damage_list

    def update(self):
        self.frame_counter += 1
        # collision with other sprites, uses special melee attack collision predicate
        for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False,
                                              collided=MeleeAttack.sector_collide):
            self.collision_behavior(sprite)
        # destroys this melee attack sprite if the duration ha expired
        if self.frame_counter > self.damage_duration:
            self.kill()

    def collision_behavior(self, entity):
        """Behavior when melee attack collides with an entity"""
        for group in entity.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                # makes sure the sprite has this method, which should be inherited in all HealthEntity sprites
                if hasattr(entity, "on_damage"):
                    entity.on_damage(self)

    def on_damage(self, entity):
        # TODO: add red tint for this but only on image
        """Changes entity to a white color when it takes damage"""
        entity.image.fill((255, 255, 255))


class Projectile(DamageSource):
    """
    Projectile damage source, used for flying objects
    """

    def __init__(self, group, game_state, pos, vel, damage, duration, kill_list, damage_list, images):
        super().__init__(group, game_state, pos, damage, duration, images)
        # movement speed
        self.vel = vel
        # image of projectile
        if vel.x == 0:
            self.angle = math.pi / 2 if vel.y > 0 else -math.pi / 2
        else:
            self.angle = math.atan(vel.y / vel.x) if vel.x > 0 else math.atan(vel.y / vel.x) + math.pi
        # pygame rectangle of projectile hit box
        self.kill_list = kill_list
        self.damage_list = damage_list

    def update(self):
        """Update behavior of projectile"""
        # movement update
        self.pos += self.vel
        self.rect.center = self.pos.x, self.pos.y
        self.frame_counter += 1
        self.animate()
        # collision with other sprites
        for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False):
            self.collision_behavior(sprite)
        # out of screen bounds then deleted
        if not (0 < self.pos.x < self.game_state.game.window_size[0] and 0 < self.pos.y <
                self.game_state.game.window_size[1]):
            self.kill()

    def collision_behavior(self, entity):
        """Behavior when melee attack collides with a sprite"""
        for group in entity.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(entity, "on_damage"):
                    entity.on_damage(self)

    def animate(self):
        pass


class Fireball(Projectile):
    """Fireball class"""
    BURN = 120  # time duration of fire damage burning
    ANIMATION_SPEED = 4

    def __init__(self, group, game_state, pos, vel, damage, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, damage, Fireball.BURN, kill_list, damage_list,
                         [pg.transform.scale(image, (48, 48)) for image in
                          [pg.image.load("assets/fireball/tile{0}.png".format(x)) for x in
                           ["000",
                            "001",
                            "002",
                            "003"
                            ]]])
        self.hit_box.size = 16, 16

    def on_damage(self, entity):
        # TODO make this look better with pixel art
        on_damage_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        on_damage_image.blit(entity.image, (0, 0))
        on_damage_image.fill((255, 255, 255, 200)) # flashes sprite white when projectile hits it
        entity.image = on_damage_image

    def damaging(self, entity):
        # TODO: make the enemy light on fire
        damaging_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        damaging_image.blit(entity.image, (0, 0))
        damaging_image.fill((255, 0, 0, 200))  # flashes sprite white when projectile hits it
        entity.image = damaging_image
        if entity.frame_counter % 60 == 0:
            # burns enemy for damage over time
            entity.health -= 2

    def animate(self):
        # TODO: remove hardcoded moduli and offsets and make this inherited from enemy class
        """Animates player sprite."""
        self.switch_image(self.images[(self.frame_counter // Fireball.ANIMATION_SPEED) % 4])
        self.image = pg.transform.rotate(self.image, -self.angle * 180 / math.pi + 90)

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y


class Root(Projectile):
    """Root class"""
    DURATION = 180  # duration that enemy is rooted into place

    def __init__(self, group, game_state, pos, vel, damage, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, damage, Root.DURATION, kill_list, damage_list)
        # TODO: add animations for root
        self.image.fill((255, 255, 255))

    # TODO: add animations for root effect
    def on_damage(self, entity):
        # TODO make this look better with pixel art
        flashing_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        flashing_image.blit(entity.image, (0, 0))
        flashing_image.fill((255, 255, 255, 200))  # flashes sprite white when projectile hits it
        entity.image = flashing_image

    def damaging(self, entity):
        # TODO: make the enemy caged in a root animation
        damaging_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        damaging_image.blit(entity.image, (0, 0))
        damaging_image.fill((255, 255, 0, 40))  # flashes sprite white when projectile hits it
        entity.image = damaging_image
        # all entity movement is stopped when rooted.
        entity.vel = Vector2(0, 0)
        entity.dir = Vector2(0, 0)


class Hook(Projectile):
    """Root class"""
    DURATION = 5  # duration that hooks pulls entity

    def __init__(self, group, game_state, pos, vel, damage, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, damage, Hook.DURATION, kill_list, damage_list)
        # TODO: make an image of a rotate
        self.image.fill((0, 255, 0))

    def on_damage(self, entity):
        # TODO make this look better with pixel art
        flashing_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        flashing_image.blit(entity.image, (0, 0))
        flashing_image.fill((255, 255, 255, 200))  # flashes sprite white when projectile hits it
        entity.image = flashing_image

    def damaging(self, entity):
        # TODO: change animation mode of the sprite to be flailing
        damaging_image = pg.Surface(entity.image.get_size(), pg.SRCALPHA)
        damaging_image.blit(entity.image, (0, 0))
        damaging_image.fill((0, 255, 0, 200))  # flashes sprite white when projectile hits it
        entity.image = damaging_image
        # moves towards the hook source for 6 seconds
        entity.dir = -6 * self.vel.normalize()


class Ability:
    """Base ability class for ability types, creates damage sources"""

    def __init__(self, sprite, cooldown, kill_list, damage_list):
        # sprite that has this ability
        self.sprite = sprite
        # ability cooldown
        self.cooldown = cooldown
        # previous frame of activation
        self.prev_activation = -cooldown
        # list of sprite groups that damage sources will be killed on
        self.kill_list = kill_list
        # list of sprite groups that damage sources will be damaged on
        self.damage_list = damage_list

    def activate(self, dir):
        "Ability is activated, run by game entity"
        pass

    def off_cooldown(self):
        """Determine if ability is off or own, used by an external entity"""
        return self.sprite.frame_counter - self.prev_activation > self.cooldown

    def create_copy(self, entity, kill_list, damage_list):
        """"""
        pass


class ShootFireball(Ability):
    MAX_FIREBALLS = 30  # maximum number of fireballs on the screen at once
    SPRAY_ANGLE = 0.1  # angle in radians of spread when shooting
    FIRE_BALL_SPEED = 8.15  # speed of shooting fireballs
    COOL_DOWN = 32  # ability cool down
    DAMAGE = 10  # frieball damage

    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, ShootFireball.COOL_DOWN, kill_list, damage_list)
        # list of fireball entities
        self.fireballs = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.fireballs) < ShootFireball.MAX_FIREBALLS:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for fire_ball in self.fireballs:
            if len(fire_ball.groups()) == 0:
                self.fireballs.remove(fire_ball)

    def shoot(self, dir):
        spray_angle = random.uniform(-ShootFireball.SPRAY_ANGLE, ShootFireball.SPRAY_ANGLE)
        spray_vector = Vector2(math.cos(spray_angle), math.sin(spray_angle))
        randomized_dir = Vector2(dir.x * spray_vector.x - dir.y * spray_vector.y,
                                 dir.x * spray_vector.y + dir.y * spray_vector.x)
        self.fireballs.append(Fireball(group=self.sprite.game_state.all_sprites,
                                       game_state=self.sprite.game_state,
                                       pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                                       vel=ShootFireball.FIRE_BALL_SPEED * randomized_dir,
                                       damage=ShootFireball.DAMAGE,
                                       kill_list=self.kill_list,
                                       damage_list=self.damage_list))

    def create_copy(self, entity, kill_list, damage_list):
        return ShootFireball(entity, kill_list, damage_list)


class ShootRoot(Ability):
    MAX_ROOTS = 3
    ROOT_SPEED = 3
    COOL_DOWN = 180
    DAMAGE = 0

    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, ShootRoot.COOL_DOWN, kill_list, damage_list)
        self.roots = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.roots) < ShootRoot.MAX_ROOTS:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for root in self.roots:
            if len(root.groups()) == 0:
                self.roots.remove(root)

    def shoot(self, dir):
        self.roots.append(Root(group=self.sprite.game_state.all_sprites,
                               game_state=self.sprite.game_state,
                               pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                               vel=ShootRoot.ROOT_SPEED * dir,
                               damage=ShootRoot.DAMAGE,
                               kill_list=self.kill_list,
                               damage_list=self.damage_list))

    def create_copy(self, sprite, kill_list, damage_list):
        return ShootRoot(sprite, kill_list, damage_list)


class ShootHook(Ability):
    MAX_HOOKS = 1
    HOOK_SPEED = 15
    COOL_DOWN = 180
    DAMAGE = 0

    # TODO: create global settings for hook ability
    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, ShootHook.COOL_DOWN, kill_list, damage_list)
        self.hooks = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.hooks) < ShootHook.MAX_HOOKS:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for root in self.hooks:
            if len(root.groups()) == 0:
                self.hooks.remove(root)

    def shoot(self, dir):
        self.hooks.append(Hook(group=self.sprite.game_state.all_sprites,
                               game_state=self.sprite.game_state,
                               pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                               vel=ShootHook.HOOK_SPEED * dir,
                               damage=ShootRoot.DAMAGE,
                               kill_list=self.kill_list,
                               damage_list=self.damage_list))

    def create_copy(self, sprite, kill_list, damage_list):
        return ShootHook(sprite, kill_list, damage_list)


class MeleeAbility(Ability):
    MAX_FIRE_BALLS = 15
    SPREAD = 1
    DURATION = 30
    COOL_DOWN = 25
    SLASH_ANIMATION_LENGTH = 15
    DAMAGE = 10

    def __init__(self, sprite, range, kill_list, damage_list):
        super().__init__(sprite, MeleeAbility.COOL_DOWN, kill_list, damage_list)
        self.attack = None
        self.range = range

    def activate(self, dir):
        if self.off_cooldown():
            self.hit_enemies(dir)
            self.sprite.slashing = True
            self.sprite.slash_counter = MeleeAbility.SLASH_ANIMATION_LENGTH
            self.prev_activation = int(self.sprite.frame_counter)

    def hit_enemies(self, dir):
        self.attack = MeleeAttack(group=self.sprite.game_state.all_sprites,
                                  game_state=self.sprite.game_state,
                                  pos=self.sprite.pos,
                                  damage=MeleeAbility.DAMAGE,
                                  range=self.range,
                                  dir=dir,
                                  spread=MeleeAbility.SPREAD,
                                  duration=MeleeAbility.DURATION,
                                  kill_list=self.kill_list,
                                  damage_list=self.damage_list)
