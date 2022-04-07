import pygame

from .Button import Button

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class MenuButton(Button):

    def __init__(self, position: dict, size: dict):
        super().__init__(position, size)

    def draw(self, window):
        pygame.draw.rect(window, Colors.grey,
                         (self.position['x'], self.position['y'],
                          self.size['width'], self.size['height']))

        for line in range(3):
            pygame.draw.line(window, Colors.white,
                             (self.position['x'] + self.size['width'] // 5,
                              self.position['y'] + (self.size['height'] // 4) * (line + 1)),
                             (self.position['x'] + self.size['width'] - (self.size['width'] // 5),
                              self.position['y'] + (self.size['height'] // 4) * (line + 1)),
                             width=self.size['height'] // 10)


class Menu:

    def __init__(self, position: dict, size: dict, button: MenuButton):
        self.position = position
        self.size = size
        self.button = button

        self.visible = self.button.pressed

    def draw(self, window) -> None:
        if self.visible:
            pass
        else:
            self.button.draw(window)
