import controls
from level_creator import *
from entity.player import *
from gui import *


class VerticalOrderSprites(pg.sprite.Group):

    @staticmethod
    def get_y(spr):
        return spr.pos.y

    def draw(self, surface):
        """Source: RenderUpdates pygame class"""
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for sprite in sorted(self.sprites(), key=VerticalOrderSprites.get_y):
            old_rect = self.spritedict[sprite]
            new_rect = surface_blit(sprite.image, sprite.rect)
            if old_rect:
                if new_rect.colliderect(old_rect):
                    dirty_append(new_rect.union(old_rect))
                else:
                    dirty_append(new_rect)
                    dirty_append(old_rect)
            else:
                dirty_append(new_rect)
            self.spritedict[sprite] = new_rect
        return dirty


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
        # gui sprites
        self.gui_sprites = pg.sprite.RenderUpdates()
        # controls associated with this game state
        self.controls = None
        # mouse position
        self.mouse_pos = pg.mouse.get_pos()
        # background of the game
        self.background = pg.Surface([self.game.window_size[0], self.game.window_size[1]])

    def load(self):
        """Behavior when this game state is loaded from pool."""
        pass

    def loop(self):
        """Game state loop, runs input(), update(), and render() steps"""
        self.render()
        self.update()
        self.input()
        self.game.time_delta = self.game.clock.tick(self.game.fps)

    def input(self):
        """Handles user input, and maps input to associated methods using the control class."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.running = False
            else:
                self.controls.process_event(event)

        # updates mouse position
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
        dirty_rects = self.all_sprites.draw(self.game.screen)
        # gui updates
        self.gui_sprites.clear(self.game.screen, self.background)
        dirty_rects += self.gui_sprites.draw(self.game.screen)
        # updates only areas of the screen that have changed
        pg.display.update(dirty_rects)

    def exit(self):
        """Behavior when game state is exited and game switches to a new state."""
        pass


class PlayingState(GameState):
    """
    Default playing game state featuring a player-controlled character.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        # pre-shake screen surface for camera shake
        self.shake_screen = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.camera_pos = Vector2(0, 0)
        self.pre_shake_pos = self.camera_pos.copy()
        self.shake_timer = 0
        # tile dimensions
        self.tile_size = 64
        self.tile_dim = int(self.game.window_size[0] / self.tile_size), int(self.game.window_size[1] / self.tile_size)
        # game background
        background_image = pg.image.load("assets/map/map.png")
        self.background = pg.transform.scale(background_image, (background_image.get_width() * 4, background_image.get_height() * 4))
        self.on_camera_background = pg.Surface([self.shake_screen.get_width(), self.shake_screen.get_height()])
        # level creator
        self.level_creator = LevelCreator(self, Vector2(0, 0))
        # sets all_sprites group to draw by order of y_position
        self.all_sprites = VerticalOrderSprites()
        # player
        self.player = Player(self.all_sprites, self)
        # player sprite group
        self.player_group = pg.sprite.Group()
        self.player_group.add(self.player)
        # wall sprites for collision
        self.walls = pg.sprite.Group()
        # enemy sprites
        self.enemies = pg.sprite.Group()
        # set controls
        self.controls = controls.PlayingControls(self.game)

        # example level
        self.level_creator.create_level(self.level_creator.load_from_file('levels.txt'))
        self.player.ability = MeleeAbility(self.player, 100, [self.enemies], [self.enemies])

    def load(self):
        self.on_camera_background.blit(self.background, (0, 0),
                                  (int(self.level_creator.stage.x * self.tile_dim[0]) * self.tile_size,
                                   int(self.level_creator.stage.y * self.tile_dim[1]) * self.tile_size,
                                   int(self.level_creator.stage.x + 1) * self.tile_dim[0] * self.tile_size,
                                   int(self.level_creator.stage.y + 1) * self.tile_dim[1] * self.tile_size))
        self.shake_screen.fill((0, 0, 0))
        self.shake_screen.blit(self.on_camera_background, (0, 0))
        self.game.screen.fill((0, 0, 0))
        rect = self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
        pg.display.update(rect)

    def update(self):
        """Updates all game objects based on input."""
        # updates game sprites
        self.all_sprites.update()
        # updates gui sprites
        self.gui_sprites.update()

        # check if game needs to switch stage
        screen_bound = self.player.check_screen_bounds()
        if screen_bound is not None:
            self.level_creator.stage += screen_bound
            print(self.level_creator.stage)
            print(self.tile_dim)
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
            # draws new background
            self.on_camera_background.fill((0, 0, 0))
            self.on_camera_background.blit(self.background, (0, 0),
                                      (int(self.level_creator.stage.x * self.tile_dim[0]) * self.tile_size,
                                       int(self.level_creator.stage.y * self.tile_dim[1]) * self.tile_size,
                                       int(self.level_creator.stage.x + 1) * self.tile_dim[0] * self.tile_size,
                                       int(self.level_creator.stage.y + 1) * self.tile_dim[1] * self.tile_size))
            self.shake_screen.blit(self.on_camera_background, (0, 0))
            self.game.screen.fill((0, 0, 0))
            rect = self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
            pg.display.update(rect)

        # reset camera shake
        if self.shake_timer != 0:
            self.camera_pos += Vector2(random.randint(-10, 10), random.randint(-10, 10))
            self.shake_timer -= 1
        else:
            self.camera_pos = self.pre_shake_pos

    def render(self):
        """Renders all game objects."""
        # clears sprites from the screen
        self.all_sprites.clear(self.shake_screen, self.on_camera_background)
        # pygame rectangles for all sprites to be updated on the game screen
        dirty_rects = self.all_sprites.draw(self.shake_screen)
        # gui updates
        self.gui_sprites.clear(self.shake_screen, self.on_camera_background)
        dirty_rects += self.gui_sprites.draw(self.shake_screen)
        # updates only areas of the screen that have changed
        offset_dirty_rects = []
        for rect in dirty_rects:
            offset_dirty_rects.append(rect.move(-self.camera_pos.x, -self.camera_pos.y))
        # resets game screen
        self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
        pg.display.update(dirty_rects + offset_dirty_rects)

    def shake_camera(self, time):
        if self.shake_timer == 0:
            self.pre_shake_pos = self.camera_pos.copy()
        self.shake_timer = time


class SelectionMenu(GameState):
    def __init__(self, game, name):
        super().__init__(game, name)
        # game background
        self.background = pg.image.load("assets/map/map.png")
        self.background.fill((0, 0, 0))
        # sprites
        self.selector = None
        self.selection = 0
        self.selections = None

    def load(self):
        pass

    def activate_selection(self):
        """Activates selected button's defined function."""
        self.selections[self.selection].function()

    def update_selection(self, i):
        """Changes selected button based on key presses."""
        # switching delay
        self.selection += i
        # ensures selection is within bounds
        if not 0 <= self.selection < len(self.selections):
            self.selection -= i
            return
        # moves selector sprite
        self.selector.change_selection(self.selections[self.selection].pos)
        # resets switching frame delay

    def exit(self):
        """Kills all sprites when exiting start menu, since not many sprites are present."""
        self.all_sprites.empty()


class StartMenu(SelectionMenu):

    def __init__(self, game, name):
        super().__init__(game, name)
        # sets controls
        self.controls = controls.StartMenuControls(self.game)

    def load(self):
        self.game.screen.blit(self.background, (0, 0))
        pg.display.update(self.background.get_rect())
        self.selections = [
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


# TODO: change this to using GUI sprites
class PauseMenu(SelectionMenu):
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
