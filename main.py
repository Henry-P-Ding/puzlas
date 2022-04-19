from player import *
from controls import *
from level_creator import *


class Game:
    """Main game class containing all game-related objects"""
    def __init__(self, window_size, fps):
        # tuple for window size
        self.window_size = window_size
        # pygame surface for display window
        self.screen = pg.display.set_mode(self.window_size)
        self.fps = fps
        # pygame clock for fixed FPS
        self.clock = pg.time.Clock()

        # control class to store game controls and associated actions
        self.controls = Controls(self).get_controls()
        self.level_creator = LevelCreator(self)
        self.tile_size = 64

        # game state: game is running
        self.running = False

        # all sprites to be rendered
        self.all_sprites = pg.sprite.RenderUpdates()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = Player(self.all_sprites, self)

        # game background
        self.background = pg.Surface([window_size[0], window_size[1]])
        self.background.fill((0, 0, 0))

    def start(self):
        """Initialize the start of the game"""
        self.running = True
        pg.init()
        # example level
        self.level_creator.create_level(self.level_creator.load_from_string(
"""############
#M#   #    #
# # # # #  #
# # # # #  #
# # # # #  #
# # # # #  #
# # # # #  #
# # # # #  #
#   #   # P#
############"""))
        self.loop()

    def loop(self):
        """Game loop, runs input(), update(), and render() steps"""
        while self.running:
            self.input()
            self.update()
            self.render()
            self.clock.tick(self.fps)

        self.stop()

    def input(self):
        """Handles user input, and maps input to associated methods using the control class."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

        # boolean list of key_strokes that are pressed
        key_strokes = pg.key.get_pressed()
        for control in self.controls:
            if key_strokes[control]:
                self.controls[control]()

    def update(self):
        """Updates all game objects based on input."""
        self.all_sprites.update()

    def render(self):
        """Renders all game objects."""
        self.all_sprites.clear(self.screen, self.background)
        # pygame rectangles for all sprites to be updated on the game screen
        sprite_rects = self.all_sprites.draw(self.screen)
        # updates only areas of the screen that have changed
        pg.display.update(sprite_rects)

    def stop(self):
        """Behavior for the end of the game."""
        pass


game = Game((768, 640), 60)
game.start()
