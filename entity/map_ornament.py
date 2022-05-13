import pygame as pg
from entity.game_entity import Entity


class Fountain(Entity):
    """
    Ornament class with animated map backgrounds
    """
    ANIMATION_SPEED = 3
    ANIMATION_MODULUS = 3

    def __init__(self, group, game_state, pos, color):
        if color == "red":
            super().__init__(group, game_state, pos, [
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/red_fountain/red_fountain_{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2",
                   "_basin_0",
                   "_basin_1",
                   "_basin_2",
                   ]]]])
        else:
            super().__init__(group, game_state, pos, [
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/blue_fountain/blue_fountain{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2",
                   "_basin_0",
                   "_basin_1",
                   "_basin_2",
                   ]]]])
        self.image = pg.Surface[]
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y, self.game_state.tile_size, self.game_state.tile_size)

    def update(self):
        self.frame_counter += 1
        self.animate()

    def animate(self):
        new_image = self.images[((self.frame_counter // Fountain.ANIMATION_SPEED) % Fountain.ANIMATION_MODULUS)]
        self.switch_image(new_image)
