from game_state import *
import pygame as pg


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
        self.time_delta = self.clock.tick(self.fps)
        # game state: game is running
        self.running = False
        self.game_state_pool = {
            "playing": PlayingState(self, "playing").setup(),
            "pause_menu": PauseMenu(self, "pause_menu").setup()
        }
        self.game_state = StartMenu(self, "start_menu").setup()
        self.game_state_manager = GameStateManager(self)

    def start(self):
        """Initialize the start of the game"""
        self.running = True
        pg.init()
        pg.font.init()
        self.game_state.load()
        self.loop()

    def loop(self):
        """Game loop, runs input(), update(), and render() steps"""
        while self.running:
            self.game_state.loop()

        self.exit()

    def stop(self):
        self.running = False

    def exit(self):
        pass


pg.init()
game = Game((704, 512), 60)
game.start()
