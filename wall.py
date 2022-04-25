import pygame as pg


class Wall(pg.sprite.Sprite):
    """
    Wall class that serves as barriers to players and enemies in a level.
    """
    def __init__(self, group, game, pos):
        super().__init__(group)
        # position of wall on screen
        self.pos = pos
        # game object that contains wall object
        self.game = game
        # display image of wall
        self.image = pg.Surface([self.game.tile_size, self.game.tile_size])
        self.image.fill((255, 0, 255))
        # pygame rect object that encompasses the wall
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y, self.game.tile_size, self.game.tile_size)

    def update(self):
        pass



