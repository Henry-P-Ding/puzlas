from game_state import *


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

        # game states
        self.game_state_manager = GameStateManager(self, StartMenu(self, "start_menu"), {
            "playing": PlayingState(self, "playing"),
            "pause_menu": PauseMenu(self, "pause_menu")
        })

    def start(self):
        """Initialize the start of the game"""
        self.running = True
        pg.init()
        pg.font.init()
        self.game_state_manager.state_stack[-1].load()
        self.loop()

    def loop(self):
        """Game loop, runs input(), update(), and render() steps"""
        while self.running:
            self.game_state_manager.state_stack[-1].loop()

        self.exit()

    def stop(self):
        self.running = False

    def exit(self):
        pass


pg.init()
game = Game((704, 512), 60)
game.start()
