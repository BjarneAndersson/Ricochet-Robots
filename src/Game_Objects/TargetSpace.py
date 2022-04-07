from math import cos
from math import pi
from math import sin

import pygame


class TargetSpace:
    symbol: str

    def __init__(self, position: dict, size: dict, color: tuple, symbol: str):
        self.position = position
        self.size = size
        self.color = color
        self.symbol = symbol

    def draw(self, window) -> None:
        if self.symbol == 'circle':
            pygame.draw.circle(window, self.color,
                               (self.position['x'] + self.size['width'] // 2,
                                self.position['y'] + self.size['height'] // 2),
                               self.size['width'] // 4)
        elif self.symbol == 'square':
            pygame.draw.rect(window, self.color,
                             (self.position['x'] + self.size['width'] // 4,
                              self.position['y'] + self.size['height'] // 4,
                              self.size['width'] // 2, self.size['height'] // 2))
        elif self.symbol == 'triangle':
            pygame.draw.polygon(window, self.color,
                                ((self.position['x'] + self.size['width'] // 4,
                                  self.position['y'] + self.size['height'] - self.size['height'] // 4),
                                 (self.position['x'] + self.size['width'] // 2,
                                  self.position['y'] + self.size['height'] // 4),
                                 (self.position['x'] + self.size['width'] - self.size['width'] // 4,
                                  self.position['y'] + self.size['height'] - self.size['height'] // 4)))
        elif self.symbol == 'hexagon':
            pts = []
            for i in range(6):
                x = (self.position['x'] + self.size['width'] // 2) + (self.size['width'] // 4) * cos(pi * 2 * i / 6)
                y = (self.position['y'] + self.size['height'] // 2) + (self.size['height'] // 4) * sin(pi * 2 * i / 6)
                pts.append([int(x), int(y)])
            pygame.draw.polygon(window, self.color, pts)

        elif self.symbol == 'spiral':
            pygame.draw.line(window, self.color,
                             (self.position['x'], self.position['y']),
                             (self.position['x'] + self.size['width'], self.position['y'] + self.size['height']),
                             width=3)
            pygame.draw.line(window, self.color,
                             (self.position['x'] + self.size['width'], self.position['y']),
                             (self.position['x'], self.position['y'] + self.size['height']),
                             width=3)
