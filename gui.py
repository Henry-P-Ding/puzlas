import pygame as pg


class Button(pg.sprite.Sprite):
    """Button class with a text image and associated function that is executed on demand."""
    def __init__(self, group, game_state, pos, function, images):
        super().__init__(group)
        self.game_state = game_state
        self.pos = pos
        # function to be executed when button is activated
        self.function = function
        # font object of the button
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.selected = False


class TextButton(Button):
    """Button class with a text image and associated function that is executed on demand."""
    def __init__(self, group, game_state, pos, function, size, color, text, font='arialunicode'):
        self.size = size
        self.font = pg.font.SysFont(font, self.size)
        self.text = text
        super().__init__(group, game_state, pos, function, [self.font.render(self.text, False, color)])


class ClickableButton(Button):
    HOVER_ALPHA = 50

    def __init__(self, group, game_state, pos, function, images, default_index=0, selected_index=1,):
        super().__init__(group, game_state, pos, function, images)
        self.default_index = default_index
        self.selected_index = selected_index
        self.rect.midtop = self.pos.x, self.pos.y
        self.prev_selected = self.selected

    def update(self):
        mouse_pos = self.game_state.mouse_pos
        if self.rect.left < mouse_pos[0] < self.rect.right and self.rect.top < mouse_pos[1] < self.rect.bottom:
            if self.game_state.controls.mouse_downs[pg.BUTTON_LEFT]:
                self.selected = True
                self.image = self.images[self.selected_index]
            else:
                self.selected = False
                self.image = self.images[self.default_index]
            self.hover_mask((255, 255, 255))
        elif not self.selected:
            self.selected = False
            self.image = self.images[self.default_index]

    def hover_mask(self, color):
        """Masks the entity a color to indicate hovering"""
        button_mask = pg.mask.from_surface(self.image)
        damage_mask = button_mask.to_surface(setcolor=color)
        damage_mask.set_colorkey((0, 0, 0))
        damage_mask.set_alpha(ClickableButton.HOVER_ALPHA)
        self.image = self.image.copy()
        self.image.blit(damage_mask, (0, 0))


class Box(pg.sprite.Sprite):
    def __init__(self, game_state, group, pos, image):
        super().__init__(group)
        self.game_state = game_state
        self.pos = pos
        self.image = image
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
