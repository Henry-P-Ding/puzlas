import pygame as pg
from pygame.math import *


class Enemy(pg.sprite.Sprite):
    """
    Generic enemies class that attacks player
    """
    def __init__(self, group, game, pos, size, steering_rate, speed):
        super().__init__(group)
        # tuple containing (width, height) of the enemies
        self.size = size
        # rate of turing towards the player
        self.steering_rate = steering_rate
        # movement speed
        self.speed = speed
        # game position
        self.pos = pos
        # movement direction
        self.dir = Vector2(0, 0)
        # image of enemies
        self.image = pg.Surface([self.size[0], self.size[1]])
        self.image.fill((100, 100, 100))
        # pygame rectangle object of enemies
        self.rect = self.image.get_rect()
        self.rect.update(0, 0, self.size[0], self.size[1])
        self.rect.center = self.pos.x, self.pos.y
        # game object containing the enemies
        self.game = game
        # positions that object is pathing to
        self.pathing_nodes = []
        # tile distances
        self.tile_dist = []

    def update(self):
        pass

    def attack(self):
        pass

    def steer(self, new_pos, min_dist=0, max_dist=None):
        """
        Steering behavior for movement towards player.
        """
        displacement = (new_pos - self.pos)
        if max_dist is None:
            if min_dist * min_dist < displacement.magnitude_squared():
                self.dir = displacement.normalize()
        else:
            if min_dist * min_dist < displacement.magnitude_squared() < max_dist * max_dist:
                self.dir = displacement.normalize()

    def path_find_to_player(self, min_dist=0, max_dist=None):
        """Pathfinding towards player with BFS"""
        # get positions of player and enemy in tile format
        pos_tile = self.pos // self.game.tile_size
        player_tile = self.game.player.pos // self.game.tile_size
        # TODO: note that all levels have to be rectangular
        # dimensions of the level
        level_size = (len(self.game.level_creator.level[0]), len(self.game.level_creator.level))

        # bfs algorithm to pathfinding
        visited = [[False for x in range(level_size[0])] for y in range(level_size[1])]
        self.tile_dist = [[-1 for x in range(level_size[0])] for y in range(level_size[1])]
        moves = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
        queue = [pos_tile]
        visited[int(pos_tile.y)][int(pos_tile.x)] = True
        self.tile_dist[int(pos_tile.y)][int(pos_tile.x)] = 0
        while len(queue) > 0:
            v = queue.pop(0)
            for move in moves:
                u = v + move

                # check if is in boundary
                if self.game.level_creator.level[int(u.y)][int(u.x)] == "#":
                    continue

                if 0 < u.x < level_size[0] and 0 < u.y < level_size[1] and not visited[int(u.y)][int(u.x)] and self.tile_dist[int(u.y)][int(u.x)] == -1:
                    queue.append(u)
                    visited[int(u.y)][int(u.x)] = True
                    self.tile_dist[int(u.y)][int(u.x)] = self.tile_dist[int(v.y)][int(v.x)] + 1

        # reset pathfinding nodes for every updated BFS iteration
        self.pathing_nodes = []
        v = player_tile
        self.pathing_nodes.insert(0, v)
        while self.tile_dist[int(v.y)][int(v.x)] > 1:
            for move in moves:
                u = v + move
                if self.game.level_creator.level[int(u.y)][int(u.x)] == "#":
                    continue

                if self.tile_dist[int(u.y)][int(u.x)] == self.tile_dist[int(v.y)][int(v.x)] - 1:
                    self.pathing_nodes.insert(0, u)
                    v = u
                    break

    def move(self):
        """
        Movement method to move towards player.
        """
        # stop moving if colliding with player
        if not pg.sprite.collide_rect(self, self.game.player):
            self.pos += self.speed * self.dir
            self.rect.center = self.pos.x, self.pos.y

        # wall collision detection
        while not pg.sprite.spritecollideany(self, self.game.walls) is None:
            self.pos -= self.speed * self.dir
            self.rect.center = self.pos.x, self.pos.y
            # algorithm to include sliding along walls
            # 0: left, 1: up, 2: right, 3: down
            adj = [Vector2(-1, 0), Vector2(0, -1), Vector2(1, 0), Vector2(0, 1)]
            collision_side = -1
            for i, x in enumerate(adj):
                adj_pos = self.pos + self.speed * x
                self.rect.center = adj_pos.x, adj_pos.y
                if pg.sprite.spritecollideany(self, self.game.walls):
                    collision_side = i

            if collision_side % 2 == 0:
                # allow movement at normal speed by normalizing vectors
                self.pos += self.speed * Vector2(0, self.dir.y).normalize()
            else:
                self.pos += self.speed * Vector2(self.dir.x, 0).normalize()
            self.rect.center = self.pos.x, self.pos.y

        self.dir.update(0, 0)


class Melee(Enemy):
    def __init__(self, group, game, pos, size, steering_rate, speed, range):
        super().__init__(group, game, pos, size, steering_rate, speed)
        self.range = range

    def update(self):
        self.path_find_to_player()
        if len(self.pathing_nodes) > 0:
            self.steer(self.pathing_nodes[0] * self.game.tile_size + Vector2(self.game.tile_size / 2, self.game.tile_size / 2))
        self.move()
        self.attack()

    def attack(self):
        if (self.pos - self.game.player.pos).magnitude_squared() < self.range * self.range:
            print("melee attack!")
