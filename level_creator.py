from wall import *
from enemy import *

class LevelCreator:
    """
    Populates the level of a game given an input string.
    """
    def __init__(self, game):
        self.game = game
        # dict associating string tile key with level creator method to place object in-game
        self.LEVEL_KEY = {
            "#": self.place_wall,
            "P": self.place_player,
            "M": self.place_melee
        }

    def create_level(self, level_data):
        """
        Arguments
        level_data: 2D python array of level tiles
        """
        for tile_y in range(len(level_data)):
            for tile_x in range(len(level_data[tile_y])):
                tile = level_data[tile_y][tile_x]
                if not self.LEVEL_KEY.get(tile) is None:
                    self.LEVEL_KEY[level_data[tile_y][tile_x]](tile_x, tile_y)

    def load_from_file(self, path):
        #TODO: implement file saving
        """Loads Level Data from a Text-File"""
        pass

    def load_from_string(self, level_string):
        """Creates 2D array of characters from single string with newlines."""
        return level_string.split("\n")

    def place_wall(self, tile_x, tile_y):
        """Places a wall object at tile location."""
        self.game.walls.add(Wall(self.game.all_sprites, self.game,
                                 Vector2(tile_x * self.game.tile_size, tile_y * self.game.tile_size)))

    def place_player(self, tile_x, tile_y):
        """Places player object at tile location."""
        self.game.player.pos = Vector2((2 * tile_x + 1) / 2 * self.game.tile_size, (2 * tile_y + 1) / 2 * self.game.tile_size)

    def place_melee(self, tile_x, tile_y):
        """Places enemies object at tile locatin."""
        self.game.enemies.add(Melee(self.game.all_sprites, self.game,
                                    Vector2((2 * tile_x + 1) / 2 * self.game.tile_size, (2 * tile_y + 1) / 2 * self.game.tile_size), (48, 64), 10, 1, 100))
