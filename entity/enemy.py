import pygame as pg
from pygame.math import *
from entity.ability import *
from entity.game_entity import AbilityEntity
from entity.game_entity import Entity


class Enemy(AbilityEntity):
    """
    Generic enemies class that attacks player
    """

    @staticmethod
    def wall_collided(enemy, wall):
        return enemy.wall_hit_box.colliderect(wall.hit_box)

    def __init__(self, group, game_state, pos, ability, speed, health, images):
        super().__init__(group, game_state, pos, images, health, ability=ability)
        # movement speed
        self.speed = speed
        # movement direction
        self.dir = Vector2(0, 0)
        # hit box
        self.hit_box.size = self.game_state.tile_size, self.game_state.tile_size
        # wall hit box for movement
        self.wall_hit_box = pg.Rect(self.hit_box.x, self.hit_box.y + self.hit_box.height / 2,
                                    self.hit_box.width, self.hit_box.height)
        self.facing_right = False

    def update(self):
        self.frame_counter += 1

    def attack(self):
        pass

    def steer(self, new_pos, min_dist=0, max_dist=None):
        """
        Steering behavior for movement towards pathfinding node.
        """
        displacement = (new_pos - self.pos)
        if max_dist is None:
            if min_dist * min_dist < (self.game_state.player.pos - self.pos).magnitude_squared():
                self.dir = displacement.normalize()
        else:
            if min_dist * min_dist < (self.game_state.player.pos - self.pos).magnitude_squared() < max_dist * max_dist:
                self.dir = displacement.normalize()

    def move(self):
        """
        Movement method
        """
        # movement
        if self.dir.magnitude_squared() != 0:
            self.dir = self.dir.normalize()
        self.vel = self.speed * self.dir
        self.pos += self.vel
        self.hit_box.center = self.pos.x, self.pos.y
        self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 2

        # wall collision detection
        if pg.sprite.spritecollideany(self, self.game_state.walls, collided=Enemy.wall_collided) is not None:
            while pg.sprite.spritecollideany(self, self.game_state.walls, collided=Enemy.wall_collided) is not None:
                self.pos -= self.dir
                self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 2
            # algorithm to include sliding along walls
            # 0: left, 1: up, 2: right, 3: down
            adj = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
            x_collision = False
            y_collision = False
            for i, x in enumerate(adj):
                adj_pos = self.pos + self.speed * x
                self.wall_hit_box.center = adj_pos.x, adj_pos.y + self.hit_box.height / 2
                if pg.sprite.spritecollideany(self, self.game_state.walls, collided=Enemy.wall_collided):
                    if i % 2 == 0:
                        x_collision = True
                    else:
                        y_collision = True

            # only allow sliding along walls if this is not a corner collision
            if x_collision and not y_collision:
                self.vel.x = 0
                if self.vel.length_squared() != 0:
                    self.pos += self.speed * self.vel.normalize()
            elif not x_collision and y_collision:
                self.vel.y = 0
                if self.vel.length_squared() != 0:
                    self.pos += self.speed * self.vel.normalize()
            else:
                self.vel = Vector2(0, 0)
            self.wall_hit_box.center = self.pos.x, self.pos.y + self.hit_box.height / 2

        self.hit_box.center = self.pos.x, self.pos.y
        self.dir.update(0, 0)
        self.rect.center = self.pos.x, self.pos.y

    def on_damage(self, source):
        """Behavior when enemy takes damage."""
        self.damaged = True
        self.damage_frame = self.frame_counter
        self.damage_source = source
        self.health -= self.damage_source.damage
        self.damage_source.on_damage(self)


class Pathfinder(Enemy):
    def __init__(self, group, game_state, pos, ability, speed, health, images):
        super().__init__(group, game_state, pos, ability, speed, health, images)
        # positions that object is pathing to
        self.pathing_nodes = []
        # tile distances for pathfinding
        self.tile_dist = []

    def path_find_to_player(self):
        """Path finds to player"""
        if self.game_state.player is not None:
            self.path_find_to(self.game_state.player)

    def path_find_to(self, entity):
        if not (0 < self.pos.x < self.game_state.game.window_size[0] and 0 < self.pos.y <
                self.game_state.game.window_size[1]):
            return
        """Pathfinding towards target sprite with BFS"""
        # get positions of player and enemy in tile format
        pos_tile = self.pos // self.game_state.tile_size
        sprite_tile = Vector2(entity.pos.x % self.game_state.game.window_size[0],
                              entity.pos.y % self.game_state.game.window_size[1]) // self.game_state.tile_size
        # dimensions of the level
        level_size = self.game_state.tile_dim
        # bfs algorithm to pathfinding
        visited = [[False for _ in range(level_size[0])] for _ in range(level_size[1])]
        self.tile_dist = [[-1 for _ in range(level_size[0])] for _ in range(level_size[1])]
        moves = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
        queue = [pos_tile]
        visited[int(pos_tile.y)][int(pos_tile.x)] = True
        self.tile_dist[int(pos_tile.y)][int(pos_tile.x)] = 0
        while len(queue) > 0:
            v = queue.pop(0)
            for move in moves:
                u = v + move

                # check if is in boundary
                tile = self.game_state.level_creator.level[int(self.game_state.level_creator.stage.y * self.game_state.tile_dim[1] + u.y)][int(self.game_state.level_creator.stage.x * self.game_state.tile_dim[0] + u.x)]
                if tile == "#" or tile == "S":
                    continue

                if 0 < u.x < level_size[0] and 0 < u.y < level_size[1] and not visited[int(u.y)][int(u.x)] and \
                        self.tile_dist[int(u.y)][int(u.x)] == -1:
                    queue.append(u)
                    visited[int(u.y)][int(u.x)] = True
                    self.tile_dist[int(u.y)][int(u.x)] = self.tile_dist[int(v.y)][int(v.x)] + 1

        # reset pathfinding nodes for every updated BFS iteration
        self.pathing_nodes = []
        v = sprite_tile
        self.pathing_nodes.insert(0, v)
        while self.tile_dist[int(v.y)][int(v.x)] > 1:
            for move in moves:
                u = v + move
                if self.game_state.level_creator.level[
                    int(self.game_state.level_creator.stage.y * self.game_state.tile_dim[1] + u.y)][
                    int(self.game_state.level_creator.stage.x * self.game_state.tile_dim[0] + u.x)] == "#":
                    continue

                if self.tile_dist[int(u.y)][int(u.x)] == self.tile_dist[int(v.y)][int(v.x)] - 1:
                    self.pathing_nodes.insert(0, u)
                    v = u
                    break


class ProjectileEnemy(Pathfinder):
    """
    General projectile enemy class that has a projectile ability.
    """
    def __init__(self, group, game_state, pos, speed, health, range, ability, cooldown, images):
        super().__init__(group, game_state, pos, ability, speed, health, images)
        self.ability.cooldown = cooldown
        self.range = range
        self.firing = False

    def update(self):
        # path finds to the player
        self.path_find_to_player()
        # steer towards the nearest node if it can path to the player
        if len(self.pathing_nodes) > 0:
            self.steer(self.pathing_nodes[0] * self.game_state.tile_size +
                       Vector2(self.game_state.tile_size / 2, self.game_state.tile_size / 2), min_dist=self.range)
        self.animate()
        if self.damaged:
            self.damage_source.damaging(self)
            if self.frame_counter - self.damage_frame >= self.damage_source.damage_duration:
                self.damaged = False
        else:
            self.rooted = False

        self.move()
        self.firing = False
        self.attack()
        self.frame_counter += 1
        if self.vel.x > 0:
            self.facing_right = True
        elif self.vel.x < 0:
            self.facing_right = False
        if self.health <= 0:
            self.death_behavior()

    def activate_ability(self):
        self.ability.activate((self.game_state.player.pos - self.pos).normalize())

    def attack(self):
        """Attacks player within a certain range."""
        if not self.game_state.player is None and not self.game_state.player.dead and (self.pos - self.game_state.player.pos).magnitude_squared() < self.range * self.range:
            self.activate_ability()
            self.firing = True


class FireMage(ProjectileEnemy):
    """
    Fire mage enemy class that can attack the player at range with a fireball ability.
    """
    ABILITY_COOLDOWN = 32
    ANIMATION_SPEED = {
        "standing": 20,
        "moving": 4,
        "firing": int(ABILITY_COOLDOWN / 4)
    }
    ANIMATION_MODULI = {
        "standing": 4,
        "moving": 4,
        "firing": 4
    }
    ANIMATION_OFFSETS = {
        "standing": 0,
        "moving": 4,
        "firing": 0
    }

    def __init__(self, group, game_state, pos, speed, health, range, attack_list):
        super().__init__(group, game_state, pos, speed, health, range, ShootFireball(self, attack_list, attack_list),
                         FireMage.ABILITY_COOLDOWN,
                         [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                          [pg.image.load("assets/enemy/fire_mage/fire_mage_{0}.png".format(x)) for x in
                           ["0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7"
                            ]]])

    def animate(self):
        """Animates player sprite."""
        if self.firing:
            new_image = self.images[((self.frame_counter // FireMage.ANIMATION_SPEED["firing"]) %
                                     FireMage.ANIMATION_MODULI["firing"])]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        elif self.vel.length_squared() != 0:
            new_image = self.images[((self.frame_counter // FireMage.ANIMATION_SPEED["moving"]) %
                                     FireMage.ANIMATION_MODULI["moving"]) + FireMage.ANIMATION_OFFSETS["moving"]]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        else:  # staying still animation
            new_image = self.images[(self.frame_counter // FireMage.ANIMATION_SPEED["standing"]) %
                                    FireMage.ANIMATION_MODULI["standing"]]
            if self.facing_right:
                self.switch_image(new_image)
            elif not self.facing_right:  # storing animation
                self.switch_image(pg.transform.flip(new_image, True, False))


class RootMage(ProjectileEnemy):
    """
    Root mage enemy class that can attack the player at range with a root ability.
    """
    ANIMATION_SPEED = {
        "standing": 20,
        "moving": 4,
        "firing": int(ShootRoot.COOL_DOWN / 4)
    }
    ANIMATION_MODULI = {
        "standing": 4,
        "moving": 4,
        "firing": 4
    }
    ANIMATION_OFFSETS = {
        "standing": 0,
        "moving": 4,
        "firing": 0
    }
    ABILITY_COOLDOWN = 240

    def __init__(self, group, game_state, pos, speed, health, range, attack_list):
        super().__init__(group, game_state, pos, speed, health, range, ShootRoot(self, attack_list, attack_list), RootMage.ABILITY_COOLDOWN,
                         [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                          [pg.image.load("assets/enemy/root_mage/root_mage_{0}.png".format(x)) for x in
                           ["0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7"
                            ]]])

    def animate(self):
        """Animates player sprite."""
        if self.firing:
            new_image = self.images[((self.frame_counter // RootMage.ANIMATION_SPEED["firing"]) %
                                     RootMage.ANIMATION_MODULI["firing"])]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        elif self.vel.length_squared() != 0:
            new_image = self.images[((self.frame_counter // RootMage.ANIMATION_SPEED["moving"]) %
                                     RootMage.ANIMATION_MODULI["moving"]) + RootMage.ANIMATION_OFFSETS["moving"]]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        else:  # staying still animation
            new_image = self.images[(self.frame_counter // RootMage.ANIMATION_SPEED["standing"]) %
                                    RootMage.ANIMATION_MODULI["standing"]]
            if self.facing_right:
                self.switch_image(new_image)
            elif not self.facing_right:  # storing animation
                self.switch_image(pg.transform.flip(new_image, True, False))


class HookMage(ProjectileEnemy):
    """
    Hook mage enemy class that can attack the player at range with a hook ability.
    """
    ANIMATION_SPEED = {
        "standing": 20,
        "moving": 4,
        "firing": int(ShootRoot.COOL_DOWN / 4)
    }
    ANIMATION_MODULI = {
        "standing": 4,
        "moving": 4,
        "firing": 4
    }
    ANIMATION_OFFSETS = {
        "standing": 0,
        "moving": 4,
        "firing": 0
    }
    ABILITY_COOLDOWN = ShootHook.COOL_DOWN

    def __init__(self, group, game_state, pos, speed, health, range, attack_list):
        super().__init__(group, game_state, pos, speed, health, range, ShootHook(self, attack_list, attack_list), HookMage.ABILITY_COOLDOWN,
                         [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                          [pg.image.load("assets/enemy/hook_mage/hook_mage_{0}.png".format(x)) for x in
                           ["0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7"
                            ]]])

    def animate(self):
        """Animates player sprite."""
        if self.firing:
            new_image = self.images[((self.frame_counter // HookMage.ANIMATION_SPEED["firing"]) %
                                     HookMage.ANIMATION_MODULI["firing"])]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        elif self.vel.length_squared() != 0:
            new_image = self.images[((self.frame_counter // HookMage.ANIMATION_SPEED["moving"]) %
                                     HookMage.ANIMATION_MODULI["moving"]) + HookMage.ANIMATION_OFFSETS["moving"]]
            if self.facing_right:
                self.switch_image(new_image)
            else:
                self.switch_image(pg.transform.flip(new_image, True, False))
        else:  # staying still animation
            new_image = self.images[(self.frame_counter // HookMage.ANIMATION_SPEED["standing"]) %
                                    HookMage.ANIMATION_MODULI["standing"]]
            if self.facing_right:
                self.switch_image(new_image)
            elif not self.facing_right:  # storing animation
                self.switch_image(pg.transform.flip(new_image, True, False))
