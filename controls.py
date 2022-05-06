import pygame as pg


class Controls:
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
    def __init__(self, game):
        super().__init__(game)
        self.event_maps["key_down"] = {
            pg.K_d: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(1, 0)),
            pg.K_a: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(-1, 0)),
            pg.K_w: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(0, -1)),
            pg.K_s: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(0, 1)),
            pg.K_v: lambda: self.game.game_state_manager.current_state().player.get_damage(200) #BROPKLEN
        }
        self.event_maps["key_up"] = {
            pg.K_d: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(-1, 0)),
            pg.K_a: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(1, 0)),
            pg.K_w: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(0, 1)),
            pg.K_s: lambda: self.game.game_state_manager.current_state().player.add_dir(pg.math.Vector2(0, -1)),
            pg.K_ESCAPE: lambda: self.game.game_state_manager.enter_state_from_pool("pause_menu")
        }
        self.event_maps["mouse_down"] = {
            pg.BUTTON_LEFT: lambda: self.game.game_state_manager.current_state().player.set_ability_active(True)
        }
        self.event_maps["mouse_up"] = {
            pg.BUTTON_LEFT: lambda: self.game.game_state_manager.current_state().player.set_ability_active(False)
        }


class StartMenuControls(Controls):
    def __init__(self, game):
        super().__init__(game)
        self.event_maps["key_down"] = {
            pg.K_RETURN: lambda: self.game.game_state_manager.current_state().activate_selection(),
            pg.K_DOWN: lambda: self.game.game_state_manager.current_state().update_selection(1),
            pg.K_UP: lambda: self.game.game_state_manager.current_state().update_selection(-1)
        }


class PauseMenuControls(Controls):
    def __init__(self, game):
        super().__init__(game)
        self.event_maps["key_down"] = {
            pg.K_RETURN: lambda: self.game.game_state_manager.current_state().activate_selection(),
            pg.K_DOWN: lambda: self.game.game_state_manager.current_state().update_selection(1),
            pg.K_UP: lambda: self.game.game_state_manager.current_state().update_selection(-1)
        }

        self.event_maps["key_up"] = {
            pg.K_ESCAPE: lambda: self.game.game_state_manager.exit_state()
        }
