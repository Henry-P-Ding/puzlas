import pygame as pg
from entity.game_entity import Entity


class Fountain(Entity):
    """
    Ornament class with animated map backgrounds
    """
    ANIMATION_SPEED = 24
    ANIMATION_MODULUS = 3

    def __init__(self, group, game_state, pos, color):
        if color == "red":
            super().__init__(group, game_state, pos,
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/fountain/red_fountain/red_fountain_{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2"
                   ]]])
        else:
            super().__init__(group, game_state, pos,
                [pg.transform.scale(image, (image.get_width() * 4, image.get_height() * 4)) for image in
                 [pg.image.load("assets/map_ornament/fountain/blue_fountain/blue_fountain{0}.png".format(x)) for x in
                  ["0",
                   "1",
                   "2"
                   ]]])
        self.pos.y -= self.game_state.tile_size
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)
        self.hit_box.update(self.pos.x, self.pos.y + self.game_state.tile_size / 2, self.game_state.tile_size, self.game_state.tile_size)

    def update(self):
        self.frame_counter += 1
        self.animate()

    def animate(self):
        new_image = self.images[((self.frame_counter // Fountain.ANIMATION_SPEED) % Fountain.ANIMATION_MODULUS)]
        self.switch_image(new_image)

    def switch_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.update(self.pos.x, self.pos.y, self.game_state.tile_size, 2 * self.game_state.tile_size)
