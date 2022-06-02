import pygame as pg


class Controls:
    """General control calss that handles mosue and key events"""
    def __init__(self, game):
        self.game = game
        self.event_maps = {
            "mouse_down": {},
            "mouse_up": {},
            "key_down": {},
            "key_up": {}
        }

    def process_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_down(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.mouse_up(event)
        elif event.type == pg.KEYDOWN:
            self.key_down(event)
        elif event.type == pg.KEYUP:
            self.key_up(event)

    def mouse_down(self, event):
        self.event_maps["mouse_down"].get(event.button, lambda: None)()

    def mouse_up(self, event):
        self.event_maps["mouse_up"].get(event.button, lambda: None)()

    def key_down(self, event):
        self.event_maps["key_down"].get(event.key, lambda: None)()

    def key_up(self, event):
        self.event_maps["key_up"].get(event.key, lambda: None)()


class PlayingControls(Controls):
    """Placing menu controls"""
    def __init__(self, game):
        super().__init__(game)
        self.key_presses = {
            pg.K_d: False,
            pg.K_a: False,
            pg.K_w: False,
            pg.K_s: False
        }
        self.event_maps["key_down"] = {
            pg.K_d: lambda: self.set_pressed_map(pg.K_d, True),
            pg.K_a: lambda: self.set_pressed_map(pg.K_a, True),
            pg.K_w: lambda: self.set_pressed_map(pg.K_w, True),
            pg.K_s: lambda: self.set_pressed_map(pg.K_s, True),
            pg.K_SPACE: lambda: self.flip_lever()
        }
        self.event_maps["key_up"] = {
            pg.K_d: lambda: self.set_pressed_map(pg.K_d, False),
            pg.K_a: lambda: self.set_pressed_map(pg.K_a, False),
            pg.K_w: lambda: self.set_pressed_map(pg.K_w, False),
            pg.K_s: lambda: self.set_pressed_map(pg.K_s, False),
            pg.K_ESCAPE: lambda: self.game.game_state_manager.enter_state_from_pool("pause_menu")
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.game.game_state_manager.current_state().player.set_primary_ability_active(True),
            pg.BUTTON_RIGHT: lambda: self.game.game_state_manager.current_state().player.set_secondary_ability_active(True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.game.game_state_manager.current_state().player.set_primary_ability_active(False),
            pg.BUTTON_RIGHT: lambda: self.game.game_state_manager.current_state().player.set_secondary_ability_active(False)
        }

    def flip_lever(self):
        # adds controls for flipping levers
        game_state = self.game.game_state_manager.current_state()
        min_sq_d = game_state.tile_size * game_state.tile_size
        for lever in game_state.levers.sprites():
            if (game_state.player.pos - lever.pos).magnitude_squared() < min_sq_d:
                lever.activated = not lever.activated
                break

    def set_pressed_map(self, key, val):
        # adds key press map
        self.key_presses[key] = val


class StartMenuControls(Controls):
    """Start menu controls."""
    def __init__(self, game):
        super().__init__(game)
        self.mouse_downs = {
            pg.BUTTON_LEFT: False,
            pg.BUTTON_RIGHT: False
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.set_click_map(pg.BUTTON_LEFT, True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.activate_selection(pg.BUTTON_LEFT, False)
        }

    def activate_selection(self, button, value):
        # activates any buttons
        self.set_click_map(button, value)
        self.game.game_state_manager.current_state().activate_selection()

    def set_click_map(self, button, value):
        self.mouse_downs[button] = value


class PauseMenuControls(Controls):
    """Pause menu controls."""
    def __init__(self, game):
        super().__init__(game)
        self.mouse_downs = {
            pg.BUTTON_LEFT: False,
            pg.BUTTON_RIGHT: False
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.set_click_map(pg.BUTTON_LEFT, True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.activate_selection(pg.BUTTON_LEFT, False)
        }

    def activate_selection(self, button, value):
        # activates a button
        self.set_click_map(button, value)
        self.game.game_state_manager.current_state().activate_selection()

    def set_click_map(self, button, value):
        # sets click map
        self.mouse_downs[button] = value


class GameOverMenuControls(Controls):
    """Game over menu controls."""
    def __init__(self, game):
        super().__init__(game)
        self.mouse_downs = {
            pg.BUTTON_LEFT: False,
            pg.BUTTON_RIGHT: False
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.set_click_map(pg.BUTTON_LEFT, True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.activate_selection(pg.BUTTON_LEFT, False)
        }

    def activate_selection(self, button, value):
        self.set_click_map(button, value)
        self.game.game_state_manager.current_state().activate_selection()

    def set_click_map(self, button, value):
        self.mouse_downs[button] = value


class GameWinMenuControls(Controls):
    """Game win menu controls."""
    def __init__(self, game):
        super().__init__(game)
        self.mouse_downs = {
            pg.BUTTON_LEFT: False,
            pg.BUTTON_RIGHT: False
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.set_click_map(pg.BUTTON_LEFT, True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.activate_selection(pg.BUTTON_LEFT, False)
        }

    def activate_selection(self, button, value):
        self.set_click_map(button, value)
        self.game.game_state_manager.current_state().activate_selection()

    def set_click_map(self, button, value):
        self.mouse_downs[button] = value