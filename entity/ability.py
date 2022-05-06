import pygame as pg
from pygame.math import *
from entity.game_entity import Entity
import random
import math


class DamageSource(Entity):
    def __init__(self, group, game_state, pos, damage, duration):
        super().__init__(group, game_state, pos, [pg.Surface((10, 10))])
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.damage = damage
        self.damage_duration = duration

    def on_damage(self, sprite):
        pass

    def damaging(self, sprite):
        pass


class MeleeAttack(DamageSource):
    @staticmethod
    def sector_collide(attack, entity):
        assert isinstance(attack, MeleeAttack), "sector_collide can only be used with melee attacks"
        rel = entity.pos - attack.pos
        if rel.x == 0:
            angle = math.pi/2 if rel.y > 0 else -math.pi/2
        else:
            angle = math.atan(rel.y/rel.x) if rel.x > 0 else math.atan(rel.y/rel.x) + math.pi
        if attack.angle_min < angle < attack.angle_max:
            if rel.magnitude_squared() < attack.range_squared:
                return True

        return False

    def __init__(self, group, game_state, pos, damage, range, dir, spread, duration, kill_list, damage_list):
        super().__init__(group, game_state, pos, damage, duration)
        self.image = pg.Surface((1, 1), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.range_squared = range * range
        angle = math.atan(dir.y/dir.x) if dir.x > 0 else math.atan(dir.y/dir.x) + math.pi
        self.angle_min, self.angle_max = angle - spread, angle + spread
        self.kill_list = kill_list
        self.damage_list = damage_list

    def update(self):
        self.frame_counter += 1
        # collision with other sprites
        for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False, collided=MeleeAttack.sector_collide):
            self.collision_behavior(sprite)
        if self.frame_counter > self.damage_duration:
            self.kill()

    def collision_behavior(self, sprite):
        for group in sprite.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(sprite, "on_damage"):
                    sprite.on_damage(self)

    def on_damage(self, sprite):
        sprite.image.fill((255, 255, 255))
        print(f"Damaged {sprite}")


class Projectile(DamageSource):
    def __init__(self, group, game_state, pos, vel, damage, duration, kill_list, damage_list):
        super().__init__(group, game_state, pos, damage, duration)
        # movement speed
        self.vel = vel
        # image of projectile
        self.image.fill((255, 255, 255))
        # pygame rectangle of projectile hit box
        self.kill_list = kill_list
        self.damage_list = damage_list

    def update(self):
        """Update behavior of projectile"""
        self.pos += self.vel
        self.rect.center = self.pos.x, self.pos.y
        # collision with other sprites
        for sprite in pg.sprite.spritecollide(self, self.game_state.all_sprites, False):
            self.collision_behavior(sprite)

        # out of screen bounds then deleted
        if not (0 < self.pos.x < self.game_state.game.window_size[0] and 0 < self.pos.y <
                self.game_state.game.window_size[1]):
            self.kill()

    def collision_behavior(self, sprite):
        pass


class FireBall(Projectile):
    """Fireball class"""
    BURN = 120

    def __init__(self, group, game_state, pos, vel, damage, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, damage, FireBall.BURN, kill_list, damage_list)
        self.image.fill((255, 120, 0))

    def collision_behavior(self, sprite):
        for group in sprite.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(sprite, "on_damage"):
                    sprite.on_damage(self)

    def on_damage(self, sprite):
        sprite.image.fill((255, 255, 255))

    # TODO: make the enemy light on fire
    def damaging(self, sprite):
        sprite.image.fill((255, 0, 0))
        if sprite.frame_counter % 60 == 0:
            # burns enemy for damage over time
            sprite.health -= 2


class Root(Projectile):
    """Root class"""
    DURATION = 180

    def __init__(self, group, game_state, pos, vel, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, 0, Root.DURATION, kill_list, damage_list)
        self.image.fill((255, 255, 255))

    def collision_behavior(self, sprite):
        for group in sprite.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(sprite, "on_damage"):
                    sprite.on_damage(self)

    def on_damage(self, sprite):
        sprite.image.fill((255, 255, 255))

    # TODO: make the enemy light on fire
    def damaging(self, sprite):
        sprite.image.fill((255, 255, 0))
        sprite.vel = Vector2(0, 0)
        sprite.dir = Vector2(0, 0)


class Hook(Projectile):
    """Root class"""
    DURATION = 5

    def __init__(self, group, game_state, pos, vel, kill_list, damage_list):
        super().__init__(group, game_state, pos, vel, 0, Hook.DURATION, kill_list, damage_list)
        self.image.fill((0, 255, 0))

    def collision_behavior(self, sprite):
        for group in sprite.groups():
            if group in self.kill_list:
                self.kill()
            if group in self.damage_list:
                if hasattr(sprite, "on_damage"):
                    sprite.on_damage(self)

    def on_damage(self, sprite):
        sprite.image.fill((255, 255, 255))

    # TODO: make the enemy light on fire
    def damaging(self, sprite):
        sprite.image.fill((255, 255, 0))
        sprite.dir = -6 * self.vel.normalize()
        print(self.vel)


class Ability:
    def __init__(self, sprite, cooldown, kill_list, damage_list):
        self.sprite = sprite
        self.cooldown = cooldown
        self.prev_activation = -cooldown
        self.kill_list = kill_list
        self.damage_list = damage_list

    def activate(self, dir):
        pass

    def off_cooldown(self):
        return self.sprite.frame_counter - self.prev_activation > self.cooldown


class ShootFireBall(Ability):
    # TODO: create global settings for fire ball ability
    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, 10, kill_list, damage_list)
        self.fireballs = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.fireballs) < 15:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for fire_ball in self.fireballs:
            if len(fire_ball.groups()) == 0:
                self.fireballs.remove(fire_ball)

    def shoot(self, dir):
        spray_angle = random.uniform(-0.1, 0.1)
        spray_vector = Vector2(math.cos(spray_angle), math.sin(spray_angle))
        randomized_dir = Vector2(dir.x * spray_vector.x - dir.y * spray_vector.y,
                                 dir.x * spray_vector.y + dir.y * spray_vector.x)
        self.fireballs.append(FireBall(group=self.sprite.game_state.all_sprites,
                                       game_state=self.sprite.game_state,
                                       pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                                       vel=10 * randomized_dir,
                                       damage=10,
                                       kill_list=self.kill_list,
                                       damage_list=self.damage_list))


class ShootRoot(Ability):
    # TODO: create global settings for root ability
    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, 180, kill_list, damage_list)
        self.roots = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.roots) < 3:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for root in self.roots:
            if len(root.groups()) == 0:
                self.roots.remove(root)

    def shoot(self, dir):
        self.roots.append(Root(group=self.sprite.game_state.all_sprites,
                               game_state=self.sprite.game_state,
                               pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                               vel=3 * dir,
                               kill_list=self.kill_list,
                               damage_list=self.damage_list))


class ShootHook(Ability):
    # TODO: create global settings for root ability
    def __init__(self, sprite, kill_list, damage_list):
        super().__init__(sprite, 180, kill_list, damage_list)
        self.hooks = []

    def activate(self, dir):
        if self.off_cooldown() and len(self.hooks) < 1:
            self.shoot(dir)
            self.prev_activation = int(self.sprite.frame_counter)

        for root in self.hooks:
            if len(root.groups()) == 0:
                self.hooks.remove(root)

    def shoot(self, dir):
        self.hooks.append(Hook(group=self.sprite.game_state.all_sprites,
                               game_state=self.sprite.game_state,
                               pos=Vector2(self.sprite.pos.x, self.sprite.pos.y),
                               vel=15 * dir,
                               kill_list=self.kill_list,
                               damage_list=self.damage_list))


class MeleeAbility(Ability):
    def __init__(self, sprite, range, kill_list, damage_list):
        super().__init__(sprite, 25, kill_list, damage_list)
        self.attack = None
        self.range = range

    def activate(self, dir):
        if self.off_cooldown():
            self.hit_enemies(dir)
            self.sprite.slashing = True
            self.sprite.slash_counter = 15
            self.prev_activation = int(self.sprite.frame_counter)

    def hit_enemies(self, dir):
        self.attack = MeleeAttack(group=self.sprite.game_state.all_sprites,
                                  game_state=self.sprite.game_state,
                                  pos=self.sprite.pos,
                                  damage=10,
                                  range=self.range,
                                  dir=dir,
                                  spread=0.3,
                                  duration=30,
                                  kill_list=self.kill_list,
                                  damage_list=self.damage_list)
