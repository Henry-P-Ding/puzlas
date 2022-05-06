from entity.wall import *
from entity.enemy import *
from entity.ability import *


class LevelCreator:
    """
    Populates the level of a game given an input string.
    """

    def __init__(self, game_state, stage):
        self.game_state = game_state
        self.level = None
        # a specific subsection within the level that the player engages in
        self.stage = stage
        # dict associating string tile key with level creator method to place object in-game
        self.LEVEL_KEY = {
            "#": self.place_wall,
            "P": self.place_player,
            "M": self.place_melee,
            "F": self.place_fire_mage,
        }

    def create_level(self, level_data):
        """
        Arguments
        level_data: 2D python array of level tiles
        """
        for tile_y in range(self.game_state.tile_dim[1]):
            for tile_x in range(self.game_state.tile_dim[0]):
                tile = level_data[int(self.stage.y) * self.game_state.tile_dim[1] + tile_y][int(self.stage.x) *
                                                                                            self.game_state.tile_dim[
                                                                                                0] + tile_x]
                if not self.LEVEL_KEY.get(tile) is None:
                    self.LEVEL_KEY[tile](tile_x, tile_y)
        self.level = level_data

    def load_from_file(self, path):
        """Loads Level Data from a Text-File"""
        with open(path) as m:
            contents = m.read()
            return self.load_from_string(contents)

    @staticmethod
    def load_from_string(level_string):
        """Creates 2D array of characters from single string with newlines."""
        return level_string.split("\n")

    def place_wall(self, tile_x, tile_y):
        """Places a wall object at tile location."""
        self.game_state.walls.add(Wall(group=self.game_state.all_sprites,
                                       game_state=self.game_state,
                                       pos=Vector2(tile_x * self.game_state.tile_size, tile_y * self.game_state.tile_size)))

    def place_player(self, tile_x, tile_y):
        """Places player object at tile location."""
        self.game_state.player.pos = Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                             (2 * tile_y + 1) / 2 * self.game_state.tile_size)

    def place_melee(self, tile_x, tile_y):
        """Places melee enemy at tile location."""
        self.game_state.enemies.add(MeleeAbility(group=self.game_state.all_sprites,
                                                 game_state=self.game_state,
                                                 pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size, (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                                 speed=3,
                                                 health=100,
                                                 melee_range=100))

    def place_fire_mage(self, tile_x, tile_y):
        """Places fire mage enemy at tile location."""
        self.game_state.enemies.add(FireMage(group=self.game_state.all_sprites,
                                             game_state=self.game_state,
                                             pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size, (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                             speed=3,
                                             health=50,
                                             range=200,
                                             attack_list=[self.game_state.walls, self.game_state.player]))
