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


class Box(pg.sprite.Sprite):
    def __init__(self, group, pos1, pos2, color):
        super().__init__(group)
        self.pos = (pos1 + pos2) / 2
        self.image = pg.surface.Surface((int((pos2 - pos1).x), int((pos2 - pos1).y)))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y


class FractionalBar(pg.sprite.Sprite):
    def __init__(self, group, pos, size, border_width, indicator, indicator_max, bar_color, background_color, border_color, left_centered=True):
        super().__init__(group)
        # left size of the bar
        self.pos = pos
        self.size = size
        self.indicator = indicator
        self.indicator_max = indicator_max
        # rect object for border around health bar
        self.border_color = border_color
        self.border_width = border_width
        self.border_corners = [(0, 0), (size.x + 2 * self.border_width, 0), (size.x + 2 * self.border_width, size.y + 2 * self.border_width), (0, size.y + 2 * self.border_width)]
        # rect object for health bar
        self.bar_color = bar_color
        self.background_color = background_color
        self.bar_rect = pg.Rect(self.border_width, self.border_width, self.indicator / self.indicator_max * size.x,
                                size.y)
        self.image = pg.Surface((size.x + 2 * self.border_width, size.y + 2 * self.border_width), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        if left_centered:
            self.rect.midleft = self.pos
        else:
            self.rect.midright = self.pos

    def update(self):
        self.bar_rect.width = self.indicator / self.indicator_max * self.size.x
        self.image.fill(self.background_color)
        pg.draw.rect(self.image, self.bar_color, self.bar_rect)
        pg.draw.lines(self.image, self.border_color, True, self.border_corners, 2 * self.border_width + 1)

    def change_indicator(self, value):
        self.indicator = value


class IndicatorBar(pg.sprite.Sprite):
    def __init__(self, group, pos, size, images, left_centered=True, top_centered=True):
        super().__init__(group)
        # left size of the bar
        self.pos = pos
        self.size = size
        self.images = []
        for image in images:
            self.images.append(pg.transform.scale(image, size))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        if left_centered and top_centered:
            self.rect.topleft = self.pos.x, self.pos.y
        elif left_centered and not top_centered:
            self.rect.bottomleft = self.pos.x, self.pos.y
        elif not left_centered and top_centered:
            self.rect.topright = self.pos.x, self.pos.y
        else:
            self.rect.bottomright = self.pos.x, self.pos.y

    def change_indicator(self, index):
        self.image = self.images[index]
