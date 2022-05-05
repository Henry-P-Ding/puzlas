import controls
from level_creator import *
from entity.player import *
from gui import *


class GameStateManager:
    """
    Manages switching between different game states.
    """
    def __init__(self, game, start_state, pool):
        self.game = game
        # active game states in a stack - top of stack is looping game currently
        self.state_stack = [start_state]
        # inactive game states in a pool
        self.pool = pool

    def exit_state(self):
        self.current_state().exit()
        state = self.state_stack.pop()
        self.pool[state.name] = state

    def enter_state(self, new_state):
        self.state_stack.append(new_state)
        self.current_state().load()

    def enter_state_from_pool(self, name):
        self.enter_state(self.pool[name])

    def switch_state(self, new_state):
        self.exit_state()
        self.enter_state(new_state)

    def switch_state_from_pool(self, name):
        self.switch_state(self.pool[name])

    def current_state(self):
        return self.state_stack[-1]


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
        self.controls = None
        # mouse position
        self.mouse_pos = pg.mouse.get_pos()

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
            else:
                self.controls.process_event(event)

        # updates mouse positoin
        self.mouse_pos = pg.mouse.get_pos()

    def update(self):
        """Update step in game state loop."""
        # updates game sprites
        self.all_sprites.update()

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
        # set controls
        self.controls = controls.PlayingControls(self.game)

        # example level
        self.level_creator.create_level(self.level_creator.load_from_file('levels.txt'))
        self.player.ability = ShootHook(self.player, [self.walls, self.enemies], [self.enemies])

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

    def __init__(self, game, name):
        super().__init__(game, name)
        # game background
        self.background = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.background.fill((0, 0, 0))
        # sprites
        self.all_sprites = pg.sprite.RenderUpdates()
        self.selector = None
        self.buttons = {}
        # selected option out of start options
        self.selection = 0
        # sets controls
        self.controls = controls.StartMenuControls(self.game)

    def load(self):
        self.game.screen.blit(self.background, (0, 0))
        pg.display.update(self.background.get_rect())
        self.buttons = [
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 100), 30, (200, 200, 200),
                   "play game", lambda: self.game.game_state_manager.switch_state_from_pool("playing")),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 200), 30, (200, 200, 200),
                   "options", lambda: print("opening options")),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 300), 30, (200, 200, 200),
                   "quit", lambda: self.game.stop())
        ]
        # reset selection to 0
        self.selector = Selector(self.all_sprites, Vector2(self.game.window_size[0] / 2 + 100, 100), Vector2(100, 0))
        self.selection = 0

    def activate_selection(self):
        """Activates selected button's defined function."""
        self.buttons[self.selection].function()

    def update_selection(self, i):
        """Changes selected button based on key presses."""
        # switching delay
        self.selection += i
        # ensures selection is within bounds
        if not 0 <= self.selection < len(self.buttons):
            self.selection -= i
            return
        # moves selector sprite
        self.selector.change_selection(self.buttons[self.selection].pos)
        # resets switching frame delay

    def exit(self):
        """Kills all sprites when exiting start menu, since not many sprites are present."""
        self.all_sprites.empty()


# TODO: inherit selection game state class for both StartMenu and PauseMenu
class PauseMenu(GameState):
    # intensity of black tint on screen during pause menu
    TINT = 150

    def __init__(self, game, name):
        super().__init__(game, name)
        # set controls
        self.controls = controls.PauseMenuControls(self.game)
        # game background
        self.background = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.background.fill((0, 0, 0))
        # selecting options
        self.selector = None
        self.box = None
        self.buttons = {}
        # selected option out of start options
        self.selection = 0

    def load(self):
        """Loads controls for the pause menu, and sets overlay to false."""
        self.box = Box(self.all_sprites, Vector2(200, 60), Vector2(520, 350), (120, 120, 120))
        self.buttons = [
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 100), 30, (200, 200, 200),
                   "resume game", lambda: self.game.game_state_manager.switch_state_from_pool("playing")),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 200), 30, (200, 200, 200),
                   "options", lambda: print("opening options")),
            Button(self.all_sprites, Vector2(self.game.window_size[0] / 2, 300), 30, (200, 200, 200),
                   "quit to menu", lambda: self.quit_to_menu())
        ]
        self.selector = Selector(self.all_sprites, self.buttons[0].pos + Vector2(130, 0), Vector2(130, 0))
        # reset selection to 0
        self.selection = 0

    def render(self):
        """Renders pause button and overlay."""

        # clears sprites from the screen
        self.all_sprites.clear(self.game.screen, self.background)
        # pygame rectangles for all sprites to be updated on the game screen
        sprite_rects = self.all_sprites.draw(self.game.screen)
        # updates only areas of the screen that have changed
        pg.display.update(sprite_rects)

    def activate_selection(self):
        """Activates selected button's defined function."""
        self.buttons[self.selection].function()

    def update_selection(self, i):
        """Changes selected button based on key presses."""
        # switching delay
        self.selection += i
        # ensures selection is within bounds
        if not 0 <= self.selection < len(self.buttons):
            self.selection -= i
            return
        # moves selector sprite
        self.selector.change_selection(self.buttons[self.selection].pos)
        # resets switching frame delay

    def quit_to_menu(self):
        self.game.game_state_manager.exit_state()
        self.game.game_state_manager.switch_state_from_pool("start_menu")

    def exit(self):
        self.all_sprites.empty()
