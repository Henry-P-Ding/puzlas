import pygame as pg


class Controls:
    def __init__(self, game):
        self.controls = None
        self.game = game

    def get_controls(self):
        if self.controls is None:
            self.set_default()
            return self.controls
        return self.controls

    def set_default(self):
        self.controls = {
            pg.K_d: lambda: self.game.player.add_dir(pg.math.Vector2(1, 0)),
            pg.K_a: lambda: self.game.player.add_dir(pg.math.Vector2(-1, 0)),
            pg.K_w: lambda: self.game.player.add_dir(pg.math.Vector2(0, -1)),
            pg.K_s: lambda: self.game.player.add_dir(pg.math.Vector2(0, 1))
        }
