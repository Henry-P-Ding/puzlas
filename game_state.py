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
        self.background = None

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
        # update GUI sprites
        self.gui_sprites.update()

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
    SCREEN_SHAKE_AMPLITUDE = 8
    SCREEN_SHAKE_ATTACK = 0.1
    SCREEN_SHAKE_RELEASE = 0.7
    SCREEN_SHAKE_PERIOD = 2 * math.pi

    def __init__(self, game, name):
        super().__init__(game, name)
        # pre-shake screen surface for camera shake
        self.shake_screen = pg.Surface([self.game.window_size[0], self.game.window_size[1]])
        self.camera_pos = Vector2(0, 0)
        self.pre_shake_pos = self.camera_pos.copy()
        self.shake_timer = 0
        self.shake_timer_max = None
        # tile dimensions
        self.tile_size = 64
        self.tile_dim = int(self.game.window_size[0] / self.tile_size), int(self.game.window_size[1] / self.tile_size)
        # game background
        background_image = pg.image.load("assets/map/playing_state_map_0.png")
        self.background = pg.transform.scale(background_image,
                                             (background_image.get_width() * 4, background_image.get_height() * 4))
        self.on_camera_background = pg.Surface([self.shake_screen.get_width() + 2 * self.tile_size, self.shake_screen.get_height() + 2 * self.tile_size])
        # void background_color
        self.void_color = (41, 41, 54)
        # level creator
        self.level_creator = LevelCreator(self, Vector2(0, 0))
        # sets all_sprites group to draw by order of y_position
        self.all_sprites = VerticalOrderSprites()
        # map ornaments
        self.map_ornaments = pg.sprite.Group()
        # player
        self.player = Player(self.all_sprites, self)
        # player sprite group
        self.player_group = pg.sprite.Group()
        self.player_group.add(self.player)
        # wall sprites for collision
        self.walls = pg.sprite.Group()
        # movable objects
        self.movables = pg.sprite.Group()
        # enemy sprites
        self.enemies = pg.sprite.Group()
        # particle sprites
        self.particles = pg.sprite.Group()
        # set controls
        self.controls = controls.PlayingControls(self.game)

        # example level
        self.level_creator.create_level(self.level_creator.load_from_file('levels.txt'))
        self.player.ability = MeleeAbility(self.player, 100, [self.enemies], [self.enemies])

        # check if screen has been entirely updated after shaking
        self.post_shake_screen_update = False
    
        # menu gui
        self.ability_indicator = IndicatorBar(self.gui_sprites, Vector2(16, 80), (64, 64), 
                                              [pg.image.load(f"assets/gui/ability_icon/{name}.png") for name in
                                               ["melee",
                                                "shoot_fireball",
                                                "shoot_root",
                                                "shoot_hook"
                                                ]])

    def load(self):
        self.on_camera_background.fill(self.void_color)
        self.on_camera_background.blit(self.background, (0, 0),
                                       (int(self.level_creator.stage.x * self.tile_dim[0] - 1) * self.tile_size,
                                        int(self.level_creator.stage.y * self.tile_dim[1] - 1) * self.tile_size,
                                        (int(self.level_creator.stage.x + 1) * self.tile_dim[0] + 2) * self.tile_size,
                                        (int(self.level_creator.stage.y + 1) * self.tile_dim[1] + 2) * self.tile_size))
        self.shake_screen.fill(self.void_color)
        self.shake_screen.blit(self.on_camera_background, (-self.tile_size, -self.tile_size))
        self.game.screen.fill(self.void_color)
        rect = self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
        pg.display.update(rect)

    def update(self):
        """Updates all game objects based on input."""
        # updates game sprites
        self.all_sprites.update()
        # updates gui sprites
        self.gui_sprites.update()

        if isinstance(self.player.ability, MeleeAbility):
            self.ability_indicator.change_indicator(0)
        elif isinstance(self.player.ability, ShootFireball):
            self.ability_indicator.change_indicator(1)
        elif isinstance(self.player.ability, ShootRoot):
            self.ability_indicator.change_indicator(2)
        elif isinstance(self.player.ability, ShootHook):
            self.ability_indicator.change_indicator(3)
        else:
            raise ValueError("Player ability is not valid.")

        # check if game needs to switch stage
        screen_bound = self.player.check_screen_bounds()
        if screen_bound is not None:
            self.level_creator.stage += screen_bound
            # remove all non-player objects to switch stage
            for sprite in self.all_sprites:
                if not isinstance(sprite, Player):
                    sprite.kill()
            # reset player position
            if screen_bound.x != 0:
                self.player.pos.x = screen_bound.x % self.game.window_size[0]
            elif screen_bound.y != 0:
                self.player.pos.y = screen_bound.y % self.game.window_size[1]
            # populates game with new sprites from the new stage
            self.level_creator.create_level(self.level_creator.level)
            # draws new background
            self.on_camera_background.fill(self.void_color)
            self.on_camera_background.blit(self.background, (0, 0),
                                           (int(self.level_creator.stage.x * self.tile_dim[0] - 1) * self.tile_size,
                                            int(self.level_creator.stage.y * self.tile_dim[1] - 1) * self.tile_size,
                                            (int(self.level_creator.stage.x + 1) * self.tile_dim[0] + 2) * self.tile_size,
                                            (int(self.level_creator.stage.y + 1) * self.tile_dim[1] + 2) * self.tile_size))
            self.shake_screen.blit(self.on_camera_background, (-self.tile_size, -self.tile_size))
            self.game.screen.fill(self.void_color)
            rect = self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
            pg.display.update(rect)

        # reset camera shake
        # TODO: remove hardcoded envelope values
        if self.shake_timer != 0:
            phase_factor = Vector2(math.sin(2 * math.pi / PlayingState.SCREEN_SHAKE_PERIOD * self.shake_timer),
                                   math.sin(2 * math.pi / PlayingState.SCREEN_SHAKE_PERIOD * (self.shake_timer + random.random() * PlayingState.SCREEN_SHAKE_PERIOD)))
            if 0 < self.shake_timer < self.shake_timer_max * PlayingState.SCREEN_SHAKE_ATTACK:
                self.camera_pos = phase_factor * self.shake_timer / (self.shake_timer_max * PlayingState.SCREEN_SHAKE_ATTACK) * PlayingState.SCREEN_SHAKE_AMPLITUDE
            elif self.shake_timer_max * PlayingState.SCREEN_SHAKE_ATTACK <= self.shake_timer < self.shake_timer_max * (1 - PlayingState.SCREEN_SHAKE_RELEASE):
                self.camera_pos = phase_factor * PlayingState.SCREEN_SHAKE_AMPLITUDE
            else:
                self.camera_pos = phase_factor * (1 - (self.shake_timer - self.shake_timer_max * (1 - PlayingState.SCREEN_SHAKE_RELEASE)) / (self.shake_timer_max * PlayingState.SCREEN_SHAKE_RELEASE)) * PlayingState.SCREEN_SHAKE_AMPLITUDE

            self.shake_timer -= 1
        else:
            self.camera_pos = self.pre_shake_pos
            self.post_shake_screen_update = True

    def render(self):
        """Renders all game objects."""
        sprite_clear_background = pg.Surface([self.shake_screen.get_width(), self.shake_screen.get_height()])
        sprite_clear_background.blit(self.on_camera_background, (0, 0), (self.tile_size, self.tile_size, self.shake_screen.get_width(), self.shake_screen.get_height()))
        # clears sprites from the screen
        self.all_sprites.clear(self.shake_screen, sprite_clear_background)
        # pygame rectangles for all sprites to be updated on the game screen
        dirty_rects = self.all_sprites.draw(self.shake_screen)
        # gui updates
        self.gui_sprites.clear(self.shake_screen, sprite_clear_background)
        dirty_rects += self.gui_sprites.draw(self.shake_screen)
        # resets game screen
        self.game.screen.fill(self.void_color)
        if self.camera_pos.x == 0 and self.camera_pos.y == 0 and not self.post_shake_screen_update:
            # updates only areas of the screen that have changed
            offset_dirty_rects = []
            for rect in dirty_rects:
                offset_dirty_rects.append(rect.move(-self.camera_pos.x, -self.camera_pos.y))
            self.game.screen.blit(self.shake_screen, (0, 0))
            pg.display.update(dirty_rects + offset_dirty_rects)
        else:
            self.game.screen.blit(self.on_camera_background, (self.camera_pos.x - self.tile_size, self.camera_pos.y - self.tile_size))
            self.game.screen.blit(self.shake_screen, (self.camera_pos.x, self.camera_pos.y))
            pg.display.update()
            if self.shake_timer == 0:
                self.post_shake_screen_update = False

    def shake_camera(self, time):
        if self.shake_timer == 0:
            self.pre_shake_pos = self.camera_pos.copy()
        self.shake_timer = time
        self.shake_timer_max = time


class SelectionMenu(GameState):
    def __init__(self, game, name):
        super().__init__(game, name)
        # game background
        self.selections = None

    def load(self):
        pass

    def activate_selection(self):
        """Activates selected button's defined function."""
        for selection in self.selections:
            if selection.selected:
                selection.function()

    def exit(self):
        self.all_sprites.empty()
        self.gui_sprites.empty()
        self.selections.clear()
        del self.background


class StartMenu(SelectionMenu):
    SCROLL_FORCE = 0.1

    def __init__(self, game, name):
        super().__init__(game, name)
        self.controls = None
        self.title_box = None
        self.shake_screen = None
        self.camera_pos = None
        self.prev_mouse_pos = None
        self.void_color = (41, 41, 54)
        self.camera_acc = None
        self.camera_vel = None
        # tile dimensions
        self.tile_size = 64
        self.tile_dim = int(self.game.window_size[0] / self.tile_size), int(self.game.window_size[1] / self.tile_size)
        # sets all_sprites group to draw by order of y_position
        self.all_sprites = VerticalOrderSprites()
        # map ornaments
        self.map_ornaments = pg.sprite.Group()
        # wall sprites for collision
        self.walls = pg.sprite.Group()
        # enemy sprites
        self.enemies = pg.sprite.Group()
        # particle sprites
        self.particles = pg.sprite.Group()
        self.player = None
        self.player_group = None
        self.level_creator = None

    def load(self):
        # tile dimensions
        self.tile_dim = int(self.game.window_size[0] / self.tile_size), int(self.game.window_size[1] / self.tile_size)
        self.camera_pos = Vector2(0, 0)
        self.prev_mouse_pos = self.mouse_pos[0], self.mouse_pos[1]
        self.camera_acc = Vector2(0, 0)
        self.camera_vel = Vector2(0, 0)
        self.background = pg.transform.scale(pg.image.load("assets/map/start_menu_map_0.png"), (self.game.window_size[0] * 3, self.game.window_size[1] * 3))
        self.game.screen.blit(self.background, (0, 0), (
            self.game.window_size[0] + self.camera_pos.x,
            self.game.window_size[1] + self.camera_pos.y,
            self.game.window_size[0],
            self.game.window_size[1]
        ))
        pg.display.update(self.background.get_rect())
        self.title_box = Box(self, self.gui_sprites, Vector2(self.game.window_size[0] / 2, self.game.window_size[1] * 1/2),
                       pg.image.load("assets/gui/menu/start_menu/start_menu_base.png"))
        # sets controls
        self.controls = controls.StartMenuControls(self.game)
        self.selections = [
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] * 0.5, self.game.window_size[1] * 4/8), lambda: self.game.game_state_manager.switch_state_from_pool("playing"),
                            [pg.image.load(f"assets/gui/button/play/play_{x}.png") for x in ["0", "1"]]),
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] * 0.5, self.game.window_size[1] * 5/8), lambda: print("opening options"),
                            [pg.image.load(f"assets/gui/button/options/options_{x}.png") for x in ["0", "1"]]),
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] * 0.5, self.game.window_size[1] * 6/8), lambda: self.game.stop(),
                            [pg.image.load(f"assets/gui/button/quit/quit_{x}.png") for x in ["0", "1"]]),
        ]
        self.level_creator = LevelCreator(self, Vector2(1, 1))
        self.level_creator.create_level(self.level_creator.load_from_file('start_menu_level.txt'))

    def update(self):
        """Update step in game state loop."""
        # updates game sprites
        self.all_sprites.update()
        # update GUI sprites
        self.gui_sprites.update()
        self.camera_acc = Vector2(self.mouse_pos[0] - self.prev_mouse_pos[0],
                                  self.mouse_pos[1] - self.prev_mouse_pos[1])
        if self.camera_acc.magnitude_squared() != 0:
            self.camera_acc = self.camera_acc.normalize()
        if self.camera_vel.x != 0:
            self.camera_vel.x += self.camera_acc.x * StartMenu.SCROLL_FORCE - self.camera_vel.x / abs(self.camera_vel.x) * (self.camera_vel.x * self.camera_vel.x) * 0.01
        else:
            self.camera_vel.x += self.camera_acc.x * StartMenu.SCROLL_FORCE
        if self.camera_vel.y != 0:
            self.camera_vel.y += self.camera_acc.y * StartMenu.SCROLL_FORCE - self.camera_vel.y / abs(self.camera_vel.y) * (self.camera_vel.y * self.camera_vel.y) * 0.01
        else:
            self.camera_vel.y += self.camera_acc.y * StartMenu.SCROLL_FORCE
        self.camera_vel = self.camera_vel if self.camera_vel.magnitude_squared() > 0.01 else Vector2(0, 0)
        self.camera_pos += self.camera_vel
        if not(-self.game.window_size[0] < self.camera_pos.x < self.game.window_size[0] and -self.game.window_size[1] < self.camera_pos.y < self.game.window_size[1]):
            self.camera_pos -= self.camera_vel
        for sprite in self.all_sprites.sprites():
            sprite.pos -= self.camera_vel
        self.prev_mouse_pos = self.mouse_pos[0], self.mouse_pos[1]


    def render(self):
        """Renders all game objects."""
        tint = pg.Surface(self.game.window_size, pg.SRCALPHA)
        tint.fill((0, 0, 0))
        tint.set_alpha(100)

        sprite_background = pg.Surface(self.game.window_size)
        sprite_background.fill(self.void_color)
        sprite_background.blit(self.background, (0, 0), (
            self.game.window_size[0] + self.camera_pos.x,
            self.game.window_size[1] + self.camera_pos.y,
            self.game.window_size[0],
            self.game.window_size[1]
        ))
        # clears sprites from the screen
        self.game.screen.fill(self.void_color)
        self.game.screen.blit(self.background, (0, 0), (
            self.game.window_size[0] + self.camera_pos.x,
            self.game.window_size[1] + self.camera_pos.y,
            self.game.window_size[0],
            self.game.window_size[1]
        ))
        self.all_sprites.clear(self.game.screen, sprite_background)
        self.all_sprites.draw(self.game.screen)
        self.game.screen.blit(tint, (0, 0))
        # gui updates
        sprite_background.blit(tint, (0, 0))
        self.gui_sprites.clear(self.game.screen, self.game.screen)
        self.gui_sprites.draw(self.game.screen)
        pg.display.update()


class PauseMenu(SelectionMenu):
    # intensity of black tint on screen during pause menu
    TINT = 150

    def __init__(self, game, name):
        super().__init__(game, name)
        self.box = None

    def load(self):
        """Loads controls for the pause menu, and sets overlay to false."""
        # set controls
        self.background = pg.Surface(self.game.window_size, pg.SRCALPHA)
        self.background.blit(self.game.screen, (0, 0))
        tint = pg.Surface(self.game.window_size, pg.SRCALPHA)
        tint.fill((0, 0, 0))
        tint.set_alpha(200)
        self.background.blit(tint, (0, 0))
        self.controls = controls.PauseMenuControls(self.game)
        self.box = Box(self, self.gui_sprites, Vector2(self.game.window_size[0] / 2, self.game.window_size[1] / 2),
                       pg.image.load("assets/gui/menu/pause_menu/pause_menu_base.png"))
        self.selections = [
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] / 2, 220),
                            lambda: self.game.game_state_manager.switch_state_from_pool("playing"),
                            [pg.image.load(f"assets/gui/button/resume_game/resume_game_{x}.png") for x in ["0", "1"]]),
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] / 2, 316),
                            lambda: print("opening options"),
                            [pg.image.load(f"assets/gui/button/options/options_{x}.png") for x in ["0", "1"]]),
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] / 2, 412),
                            lambda: self.quit_to_menu(),
                            [pg.image.load(f"assets/gui/button/quit/quit_{x}.png") for x in ["0", "1"]]),
        ]

    def quit_to_menu(self):
        self.game.game_state_manager.exit_state()
        self.game.game_state_manager.switch_state_from_pool("start_menu")


class GameOverMenu(SelectionMenu):

    def __init__(self, game, name):
        super().__init__(game, name)
        # sets controls
        self.controls = None
        self.box = None

    def load(self):
        self.controls = controls.GameOverMenuControls(self.game)
        self.background = pg.Surface(self.game.window_size, pg.SRCALPHA)
        self.background.blit(self.game.screen, (0, 0))
        tint = pg.Surface(self.game.window_size, pg.SRCALPHA)
        tint.fill((0, 0, 0))
        tint.set_alpha(200)
        self.background.blit(tint, (0, 0))
        self.box = Box(self, self.gui_sprites, Vector2(self.game.window_size[0] / 2, self.game.window_size[1] / 2),
                       pg.transform.scale(pg.image.load(f"assets/gui/menu/game_over_menu/game_over_menu.png"), (720, 384)))
        self.game.screen.blit(self.background, (0, 0))
        pg.display.update(self.background.get_rect())
        self.selections = [
            ClickableButton(self.gui_sprites, self, Vector2(self.game.window_size[0] / 2, self.game.window_size[1] / 2), lambda: self.reset_game(),
                            [pg.transform.scale(image, (528, 96)) for image in
                             [pg.image.load(f"assets/gui/button/quit_to_menu/quit_to_menu_{x}.png") for x in
                              ["0",
                               "1"
                               ]]])
        ]

    def reset_game(self):
        self.game.game_state_manager.exit_state()
        del self.game.game_state_manager.pool["playing"]
        self.game.game_state_manager.pool["playing"] = PlayingState(self.game, "playing")
        self.game.game_state_manager.enter_state_from_pool("start_menu")
