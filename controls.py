import pygame as pg


class Controls:
    """
    Controls class that handles the mapping of user inputs to game functions
    """

    def __init__(self, game):
        self.controls = None
        # game containing this controls class
        self.game = game
        self.state_map = {
            "playing": self.set_playing_controls,
            "pause_menu": self.set_pause_menu_controls,
            "start_menu": self.set_start_menu_controls
        }

    def get_controls(self):
        """Returns dict of controls to associated methods"""
        if self.controls is None:
            self.state_map[self.game.game_state.name]()
            return self.controls
        return self.controls

    def get_controls_by_name(self, name):
        self.state_map[name]()
        return self.controls

    def set_playing_controls(self):
        """Default controls when playing the game"""
        self.controls = {
            pg.K_d: lambda: self.game.game_state.player.add_dir(pg.math.Vector2(1, 0)),
            pg.K_a: lambda: self.game.game_state.player.add_dir(pg.math.Vector2(-1, 0)),
            pg.K_w: lambda: self.game.game_state.player.add_dir(pg.math.Vector2(0, -1)),
            pg.K_s: lambda: self.game.game_state.player.add_dir(pg.math.Vector2(0, 1)),
            pg.K_p: lambda: self.game.game_state_manager.pause()
        }
        return self

    def set_pause_menu_controls(self):
        """Controls when paused."""
        self.controls = {
            pg.K_u: lambda: self.game.game_state_manager.pause()
        }
        return self

    def set_start_menu_controls(self):
        """Controls when paused."""
        self.controls = {
            pg.K_DOWN: lambda: self.game.game_state.update_selection(1),
            pg.K_UP: lambda: self.game.game_state.update_selection(-1),
            pg.K_RETURN: lambda: self.game.game_state.activate_selection()
        }
        return self

