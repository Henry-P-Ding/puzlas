from entity.wall import *
from entity.enemy import *
from entity.ability import *
from entity.map_ornament import *
import copy


class LevelCreator:
    """
    Populates the level of a game given an input string.
    """

    def __init__(self, game_state, stage):
        self.game_state = game_state
        # string containing level data
        self.level = None
        # a specific subsection within the level that the player engages in
        self.stage = stage
        # dict associating string tile key with level creator method to place object in-game
        self.LEVEL_KEY = {
            "#": self.place_wall,
            "P": self.place_player,
            "M": self.place_melee,
            "F": self.place_fire_mage,
            "R": self.place_root_mage,
            "H": self.place_hook_mage,
            "A": self.place_fountain,
            "B": self.place_fountain,
            "S": self.place_spike,
            "V": self.place_movable,
            "L": self.place_lever
        }
        # information for placing doors and levers
        self.stage_function_information = {}

    def create_level(self, level_data):
        """
        Arguments
        level_data: 2D python array of level tiles
        """
        self.level = level_data
        stage_has_player = False
        # loops to game tiles
        while not stage_has_player:
            self.stage.x = 0
            for x in range(int(len(self.level[0]) / self.game_state.tile_dim[0])):
                for tile_y in range(self.game_state.tile_dim[1]):
                    for tile_x in range(self.game_state.tile_dim[0]):
                        # text position
                        text_pos = (int(self.stage.y) * self.game_state.tile_dim[1] + tile_y,
                            int(self.stage.x) * self.game_state.tile_dim[0] + tile_x)
                        tile = self.level[text_pos[0]][text_pos[1]]
                        # set stage to wherever player is in the text file
                        if tile == "P":
                            stage_has_player = True
                            break
                if stage_has_player:
                    break
                # added stage vector to move stages
                self.stage += Vector2(1, 0)
            if stage_has_player:
                break
            # add stage vector to move stages
            self.stage += Vector2(0, 1)

        # whether the game is currenty reading level functions, which appear at end of file
        reading_level_functions = False
        for line in self.level:
            if line[0] == "~":
                reading_level_functions = True
            if reading_level_functions:
                tokens = [""]
                for char in line:
                    if char == ";":
                        tokens.append("")
                    else:
                        tokens[-1] += char

                if tokens[0] == "door":
                    pos1_split, pos2_split = tokens[1].split(","), tokens[2].split(",")
                    pos1, pos2 = Vector2(int(pos1_split[0]), int(pos1_split[1])), Vector2(int(pos2_split[0]), int(pos2_split[1]))
                    # id of whatever condition the door needs to activate
                    activation_condition_id = tokens[3]
                    if len(tokens) > 3:
                        activation_condition = ActivationCondition(activation_condition_id, tokens[4:])
                    else:
                        activation_condition = ActivationCondition(activation_condition_id, tokens[4:])
                    stage = (int(pos1.x / self.game_state.tile_dim[0]), int(pos1.y / self.game_state.tile_dim[1]))
                    if self.stage_function_information.get(stage, None) is None:
                        self.stage_function_information[stage] = []

                    self.stage_function_information[stage].append([
                        "door",
                        pos1.x % self.game_state.tile_dim[0],
                        pos1.y % self.game_state.tile_dim[1],
                        pos2.x % self.game_state.tile_dim[0],
                        pos2.y % self.game_state.tile_dim[1],
                        activation_condition
                    ])
                elif tokens[0] == "gun":
                    pos1_split = tokens[1].split(",")
                    pos1 = Vector2(int(pos1_split[0]), int(pos1_split[1]))
                    assert tokens[2] == "True" or tokens[2] == "False", "constant firing must be True or False"
                    assert tokens[3] == "True" or tokens[3] == "False", "aiming must be True or False"
                    damage = int(tokens[4])
                    speed = int(tokens[5])
                    dir_split = tokens[6].split(",")
                    dir = Vector2(int(dir_split[0]), int(dir_split[1]))
                    activation_condition_id = tokens[7]
                    activation_condition = ActivationCondition(activation_condition_id, tokens[8:])
                    stage = (int(pos1.x / self.game_state.tile_dim[0]), int(pos1.y / self.game_state.tile_dim[1]))
                    if self.stage_function_information.get(stage, None) is None:
                        self.stage_function_information[stage] = []
                    self.stage_function_information[stage].append([
                        "gun",
                        pos1.x % self.game_state.tile_dim[0],
                        pos1.y % self.game_state.tile_dim[1],
                        damage,
                        speed,
                        dir,
                        tokens[2] == "True",
                        tokens[3] == "True",
                        activation_condition
                    ])

        self.load_stage()

    def load_stage(self):
        for tile_y in range(self.game_state.tile_dim[1]):
            for tile_x in range(self.game_state.tile_dim[0]):
                tile = self.level[int(self.stage.y) * self.game_state.tile_dim[1] + tile_y][
                    int(self.stage.x) * self.game_state.tile_dim[0] + tile_x]
                if not self.LEVEL_KEY.get(tile) is None:
                    self.LEVEL_KEY[tile](tile_x, tile_y)

        for f_info in self.stage_function_information.get((int(self.stage.x), int(self.stage.y)), []):
            if f_info[0] == "door":
                self.place_door(f_info[1], f_info[2], f_info[3], f_info[4], f_info[5])
            elif f_info[0] == "gun":
                self.place_arrow_gun(f_info[1], f_info[2], f_info[3], f_info[4], f_info[5], f_info[6], f_info[7], f_info[8])

    def load_from_file(self, path):
        """Loads Level Data from a Text-File"""
        with open(path) as m:
            contents = m.read()
            return self.load_from_string(contents)

    @staticmethod
    def load_from_string(level_string):
        """Creates 2D array of characters from single string with newlines."""
        return [list(row) for row in level_string.split("\n")]

    def place_wall(self, tile_x, tile_y):
        """Places a wall object at tile location."""
        self.game_state.walls.add(Wall(group=self.game_state.all_sprites,
                                       game_state=self.game_state,
                                       pos=Vector2(tile_x * self.game_state.tile_size,
                                                   tile_y * self.game_state.tile_size)))

    def place_fountain(self, tile_x, tile_y):
        """Places fountain"""
        tile = self.level[int(self.stage.y) * self.game_state.tile_dim[1] + tile_y][
            int(self.stage.x) * self.game_state.tile_dim[0] + tile_x]
        fountain = Fountain(group=self.game_state.all_sprites,
                            game_state=self.game_state,
                            pos=Vector2(tile_x * self.game_state.tile_size, tile_y * self.game_state.tile_size),
                            color="red" if tile == "A" else "blue")
        self.game_state.map_ornaments.add(fountain)
        self.game_state.walls.add(fountain)

    def place_spike(self, tile_x, tile_y):
        """Places spike into the game"""
        spike = Spike(group=self.game_state.all_sprites,
                      game_state=self.game_state,
                      pos=Vector2(tile_x * self.game_state.tile_size, tile_y * self.game_state.tile_size),
                      damage=Spike.DAMAGE,
                      damage_list=[self.game_state.enemies, self.game_state.player_group])
        self.game_state.map_ornaments.add(spike)

    def place_movable(self, tile_x, tile_y):
        """Places movable block by player"""
        movable = Movable(group=self.game_state.all_sprites,
                          game_state=self.game_state,
                          pos=Vector2((tile_x + 0.5) * self.game_state.tile_size,
                                      (tile_y + 0.5) * self.game_state.tile_size))
        self.game_state.movables.add(movable)

    def place_movable_with_image(self, tile_x, tile_y, image):
        """Places movable block by player"""
        movable = Movable(group=self.game_state.all_sprites,
                          game_state=self.game_state,
                          pos=Vector2((tile_x + 0.5) * self.game_state.tile_size,
                                      (tile_y + 0.5) * self.game_state.tile_size))
        movable.image = image
        self.game_state.movables.add(movable)

    def place_door(self, tile_x1, tile_y1, tile_x2, tile_y2, activation_condition):
        """Places door"""
        door = Door(group=self.game_state.all_sprites,
                    game_state=self.game_state,
                    pos1=Vector2((tile_x1 + 0.5) * self.game_state.tile_size,
                                 (tile_y1) * self.game_state.tile_size),
                    pos2=Vector2((tile_x2 + 0.5) * self.game_state.tile_size,
                                 (tile_y2) * self.game_state.tile_size),
                    activation_condition=activation_condition)
        self.game_state.doors.add(door)

    def place_arrow_gun(self, tile_x, tile_y, damage, speed, dir, constant_firing, aiming, activation_condition):
        """Places arrow gun"""
        shooter = ArrowGun(group=self.game_state.all_sprites,
                           game_state=self.game_state,
                           pos=Vector2((tile_x + 0.5) * self.game_state.tile_size,
                                       (tile_y + 0.5) * self.game_state.tile_size),
                           damage=damage,
                           speed=speed,
                           dir=dir,
                           constant_firing=constant_firing,
                           aiming=aiming,
                           activation_condition=activation_condition)
        self.game_state.arrow_shooters.add(shooter)

    def place_lever(self, tile_x, tile_y):
        """Places lever"""
        lever = Lever(group=self.game_state.all_sprites,
                      game_state=self.game_state,
                      pos=Vector2((tile_x + 0.5) * self.game_state.tile_size,
                                  (tile_y + 0.5) * self.game_state.tile_size))
        self.game_state.levers.add(lever)

    def place_player(self, tile_x, tile_y):
        """Places player object at tile location."""
        self.game_state.player.pos = Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                             (2 * tile_y + 1) / 2 * self.game_state.tile_size)
        # removes player character after being placed
        self.level[int(self.stage.y) * self.game_state.tile_dim[1] + tile_y][
            int(self.stage.x) * self.game_state.tile_dim[0] + tile_x] = " "

    def place_melee(self, tile_x, tile_y):
        """Places melee enemy at tile location."""
        self.game_state.enemies.add(Melee(group=self.game_state.all_sprites,
                                          game_state=self.game_state,
                                          pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                                      (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                          speed=3,
                                          health=100,
                                          melee_range=100))

    def place_fire_mage(self, tile_x, tile_y):
        """Places fire mage enemy at tile location."""
        self.game_state.enemies.add(FireMage(group=self.game_state.all_sprites,
                                             game_state=self.game_state,
                                             pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                                         (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                             speed=3,
                                             health=50,
                                             range=200,
                                             attack_list=[self.game_state.walls, self.game_state.player_group]))

    def place_root_mage(self, tile_x, tile_y):
        """Places fire mage enemy at tile location."""
        self.game_state.enemies.add(RootMage(group=self.game_state.all_sprites,
                                             game_state=self.game_state,
                                             pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                                         (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                             speed=1.2,
                                             health=50,
                                             range=400,
                                             attack_list=[self.game_state.walls, self.game_state.player_group]))

    def place_hook_mage(self, tile_x, tile_y):
        """Places fire mage enemy at tile location."""
        self.game_state.enemies.add(HookMage(group=self.game_state.all_sprites,
                                             game_state=self.game_state,
                                             pos=Vector2((2 * tile_x + 1) / 2 * self.game_state.tile_size,
                                                         (2 * tile_y + 1) / 2 * self.game_state.tile_size),
                                             speed=3,
                                             health=50,
                                             range=400,
                                             attack_list=[self.game_state.walls, self.game_state.player_group]))
