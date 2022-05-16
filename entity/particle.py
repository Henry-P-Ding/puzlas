import random
import pygame as pg
from entity.game_entity import Entity


class Particle(Entity):
    def __init__(self, group, game_state, pos, images, life_time):
        super().__init__(group, game_state, pos, images)
        self.life_time = life_time


class WalkDust(Particle):
    LIFE_TIME = 10
    RADIUS_MIN, RADIUS_MAX = 2, 8
    COLOR = (255, 255, 255, 120)
    FADE_ATTACK = 0.1
    FADE_RELEASE = 0.3

    def __init__(self, group, game_state, pos):
        super().__init__(group, game_state, pos, [pg.Surface([WalkDust.RADIUS_MAX * 2, WalkDust.RADIUS_MAX * 2], pg.SRCALPHA)], WalkDust.LIFE_TIME)
        self.radius = 0
        self.max_radius = random.randint(WalkDust.RADIUS_MIN, WalkDust.RADIUS_MAX)

    def update(self):
        self.frame_counter += 1
        if self.frame_counter > self.life_time:
            self.kill()
            return
        age = self.frame_counter / self.life_time
        if 0 < age < WalkDust.FADE_ATTACK:
            self.radius = self.max_radius * age / WalkDust.FADE_ATTACK
        elif WalkDust.FADE_ATTACK <= age < 1 - WalkDust.FADE_RELEASE:
            self.radius = self.max_radius
        else:
            self.radius = self.max_radius * (1 - (age - (1 - WalkDust.FADE_RELEASE)) / WalkDust.FADE_RELEASE)
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, WalkDust.COLOR, (WalkDust.RADIUS_MAX, WalkDust.RADIUS_MAX), self.radius)


class FireTrail(Particle):
    LIFE_TIME = 8
    RADIUS_MIN, RADIUS_MAX = 2, 4
    COLORS = [
        (242, 203, 5),
        (242, 159, 5),
        (242, 92, 5),
        (242, 48, 5)
    ]
    FADE_ATTACK = 0.1
    FADE_RELEASE = 0.3

    def __init__(self, group, game_state, pos):
        super().__init__(group, game_state, pos, [pg.Surface([FireTrail.RADIUS_MAX * 2, FireTrail.RADIUS_MAX * 2], pg.SRCALPHA)], FireTrail.LIFE_TIME)
        self.radius = 0
        self.max_radius = random.randint(FireTrail.RADIUS_MIN, FireTrail.RADIUS_MAX)
        self.color = random.choice(FireTrail.COLORS)

    def update(self):
        self.frame_counter += 1
        if self.frame_counter > self.life_time:
            self.kill()
            return
        age = self.frame_counter / self.life_time
        if 0 < age < FireTrail.FADE_ATTACK:
            self.radius = self.max_radius * age / FireTrail.FADE_ATTACK
        elif FireTrail.FADE_ATTACK <= age < 1 - FireTrail.FADE_RELEASE:
            self.radius = self.max_radius
        else:
            self.radius = self.max_radius * (1 - (age - (1 - FireTrail.FADE_RELEASE)) / FireTrail.FADE_RELEASE)
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, self.color, (FireTrail.RADIUS_MAX, FireTrail.RADIUS_MAX), self.radius)


class LavaParticle(Particle):
    LIFE_TIME = 90
    RADIUS_MIN, RADIUS_MAX = 4, 6
    COLORS = [
        (240, 156, 120, 200),
        (242, 163, 120, 200),
        (254, 167, 120, 200),
    ]
    FADE_ATTACK = 0.1
    FADE_RELEASE = 0.9

    def __init__(self, group, game_state, pos):
        super().__init__(group, game_state, pos,
                         [pg.Surface([LavaParticle.RADIUS_MAX * 2, LavaParticle.RADIUS_MAX * 2], pg.SRCALPHA)],
                         LavaParticle.LIFE_TIME)
        self.radius = 0
        self.max_radius = random.randint(LavaParticle.RADIUS_MIN, LavaParticle.RADIUS_MAX)
        self.color = random.choice(LavaParticle.COLORS)

    def update(self):
        self.frame_counter += 1
        if self.frame_counter > self.life_time:
            self.kill()
            return
        age = self.frame_counter / self.life_time
        if 0 < age < LavaParticle.FADE_ATTACK:
            self.radius = self.max_radius * age / LavaParticle.FADE_ATTACK
        elif LavaParticle.FADE_ATTACK <= age < 1 - LavaParticle.FADE_RELEASE:
            self.radius = self.max_radius
        else:
            self.radius = self.max_radius * (1 - (age - (1 - LavaParticle.FADE_RELEASE)) / LavaParticle.FADE_RELEASE)
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, self.color, (LavaParticle.RADIUS_MAX, LavaParticle.RADIUS_MAX), self.radius)