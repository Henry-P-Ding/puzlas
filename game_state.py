from player import *
from level_creator import *
from controls import *
from gui import *


class GameStateManager:
    """
    Manages switching between different game states.
    """
    def __init__(self, game):
        self.game = game

    def switch_state(self, new_state):
        self.game.game_state.exit()
        self.game.game_state_pool[self.game.game_state.name] = self.game.game_state
        self.game.game_state = new_state
        self.game.game_state.load()

    def pause(self):
        if self.game.game_state.name == "playing":
            self.switch_state(self.game.game_state_pool["pause_menu"])
        elif self.game.game_state.name == "pause_menu":
            self.switch_state(self.game.game_state_pool["playing"])


class GameState:
    """
    A state of game looping, characterized by unique loop behavior. Used to distinguish between running the game, menus,
    an in-game GUIs.
    """
    def __init__(self, game, name):
        # game object associated with the game state
        self.game = game
        # characteristic string of the game state
        self.name = name
        # all sprites associated with this game state
        self.all_sprites = pg.sprite.RenderUpdates()
        # controls associated with this game state
        self.controls = Controls(self.game).get_controls_by_name(name)

    # TODO: merge this with the constructor?
    def setup(self):
        """Setup game state. Used separately from when game-state is initialized."""
        return self

    def load(self):
        """Behavior when this game state is loaded from pool."""
        pass

    def loop(self):
        """Game state loop, runs input(), update(), and render() steps"""
        self.input()
        self.render()
        self.update()
        self.game.time_delta = self.game.clock.tick(self.game.fps)

    def input(self):
        """Handles user input, and maps input to associated methods using the control class."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.running = False

        # boolean list of key_strokes that are pressed
        key_strokes = pg.key.get_pressed()
        for control in self.controls:
            if key_strokes[control]:
                self.controls[control]()

    def update(self):
        """Update step in game state loop."""
        pass

    def render(self):
        """Renders all game objects."""
        # clears sprites from the screen
        self.all_sprites.clear(self.game.screen, self.background)
        # pygame rectangles for all sprites to be updated on the game screen
        sprite_rects = self.all_sprites.draw(self.game.screen)
        # updates only areas of the screen that have changed
        pg.display.update(sprite_rects)

    def exit(self):
        """Behavior when game state is exited and game switches to a new state."""
        pass


class PlayingState(GameState):
    """
    Default playing game state featuring a player-controlled character.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        # tile dimensions
        self.tile_size = 64
        self.tile_dim = int(self.game.window_size[0] / self.tile_size), int(self.game.window_size[1] / self.tile_size)
        # game background
        self.background = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.background.fill((0, 0, 0))
        # level creator
        self.level_creator = LevelCreator(self, Vector2(0, 0))
        # player
        self.player = Player(self.all_sprites, self)
        # wall sprites for collision
        self.walls = pg.sprite.Group()
        # enemy sprites
        self.enemies = pg.sprite.Group()
        # player object
        self.player = None

    def setup(self):
        # example level
        self.level_creator.create_level(self.level_creator.load_from_file('levels.txt'))
        return self

    def load(self):
        # setup controls to matching with the game state
        self.controls = Controls(self.game).get_controls()

    def update(self):
        """Updates all game objects based on input."""
        # updates game sprites
        self.all_sprites.update()

        # check if need to switch stage
        screen_bound = self.player.check_screen_bounds()
        if screen_bound is not None:
            self.level_creator.stage += screen_bound
            # remove all non-player objects to switch stage
            for sprite in self.all_sprites:
                if not isinstance(sprite, Player):
                    sprite.kill()
            # populates game with new sprites from the new stage
            self.level_creator.create_level(self.level_creator.level)
            # reset player position
            if screen_bound.x != 0:
                self.player.pos.x = screen_bound.x % self.game.window_size[0]
            elif screen_bound.y != 0:
                self.player.pos.y = screen_bound.y % self.game.window_size[1]


class StartMenu(GameState):
    # delay between consecutive key presses on the start menu
    # TODO: make this key-release instead
    BUTTON_DELAY = 15

    def __init__(self, game, name):
        super().__init__(game, name)
        self.controls = None
        # game background
        self.background = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.background.fill((0, 0, 0))
        # sprites
        self.all_sprites = pg.sprite.RenderUpdates()
        self.selector = Selector(self.all_sprites, Vector2(self.game.window_size[0] / 2 + 100, 100), Vector2(100, 0))
        self.buttons = {}
        # selected option out of start options
        self.selection = 0
        self.frame_counter = 0
        self.previous_press = self.frame_counter

    def load(self):
        """Sets up three buttons for starting the game, options menu, and to quit the game."""
        # set controls to the controls associated with the game state.
        self.controls = Controls(self.game).get_controls()
        self.buttons = [
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 100), 30, (200, 200, 200),
                   "start game", lambda: self.game.game_state_manager.switch_state(self.game.game_state_pool["playing"])),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 200), 30, (200, 200, 200),
                   "options", lambda: print("opening options")),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 300), 30, (200, 200, 200),
                   "quit", lambda: self.game.stop())
        ]
        # reset selection to 0
        self.selection = 0

    def update(self):
        """Updates all game objects based on input."""
        # updates game sprites
        self.all_sprites.update()
        # advances frame counter
        self.frame_counter += 1

    def activate_selection(self):
        """Activates selected button's defined function."""
        self.buttons[self.selection].function()

    def update_selection(self, i):
        """Changes selected button based on key presses."""
        # switching delay
        if self.frame_counter - self.previous_press > StartMenu.BUTTON_DELAY:
            self.selection += i
            # ensures selection is within bounds
            if not 0 <= self.selection < len(self.buttons):
                self.selection -= i
                return
            # moves selector sprite
            self.selector.change_selection(self.buttons[self.selection].pos)
            # resets switching frame delay
            self.previous_press = self.frame_counter

    def exit(self):
        """Kills all sprites when exiting start menu, since not many sprites are present."""
        for sprite in self.all_sprites:
            sprite.kill()


# TODO: make pausing/unpausing the same key
class PauseMenu(GameState):
    # intensity of black tint on screen during pause menu
    TINT = 150

    def __init__(self, game, name):
        super().__init__(game, name)
        # tinted overlay during pause menu
        self.overlay = pg.Surface(self.game.window_size, pg.SRCALPHA)
        self.overlay.fill((0, 0, 0, PauseMenu.TINT))
        # check whether overlay is on or off - this avoids issues with overlay resetting from game loop render order
        self.overlay_on = False

    def load(self):
        """Loads controls for the pause menu, and sets overlay to false."""
        self.controls = Controls(self.game).get_controls()
        self.overlay_on = False

    def update(self):
        # TODO: implement pause menu
        pass

    def render(self):
        """Renders pause button and overlay."""
        # adds overlay if overlay is not detected to be on - this is
        if not self.overlay_on:
            self.game.screen.blit(self.overlay, (0, 0))
            pg.display.update()
            # once overlay is turned on, set to True
            self.overlay_on = True
