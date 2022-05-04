import pygame as pg

class Button(pg.sprite.Sprite):
    # TODO: change to image instead of text
    """Button class with a text image and associated function that is executed on demand."""
    def __init__(self, group, pos, size, color, text, function, font='arialunicode'):
        super().__init__(group)
        self.text = text
        self.pos = pos
        # function to be executed when button is activated
        self.function = function
        # font object of the button
        self.font = pg.font.SysFont(font, size)
        self.image = self.font.render(self.text, False, color)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y

    def update(self):
        self.rect.center = self.pos.x, self.pos.y


class Selector(pg.sprite.Sprite):
    # TODO: add arrow-like image to the selector
    """
    Selector class that can move between different selection positions.
    Used for selecting between multiple options.
    """
    def __init__(self, group, pos, spacing):
        super().__init__(group)
        self.pos = pos
        # spacing relative to the selected position, can be used to offset from selected option
        self.spacing = spacing
        self.image = pg.surface.Surface((30, 30))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y

    def change_selection(self, new_pos):
        """Changes selection to a new position."""
        self.pos = new_pos + self.spacing

    def update(self):
        self.rect.center = self.pos.x, self.pos.y