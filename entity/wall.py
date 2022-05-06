import pygame as pg
from entity.game_entity import Entity


class Wall(Entity):
    """
    Wall class that serves as barriers to players and enemies in a level.
    """
    def __init__(self, group, game_state, pos):
        super().__init__(group, game_state, pos, [pg.Surface([game_state.tile_size, game_state.tile_size])])
        self.image.fill((50, 50, 50))
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y, self.game_state.tile_size, self.game_state.tile_size)
