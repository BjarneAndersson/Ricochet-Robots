from math import cos
from math import pi
from math import sin
from src.Helpers import Colors
from src.SQL import SQL
import pygame


class Target:
    def __init__(self, db: SQL, game_id: int, chip_id: int, position_grid_center: dict):
        self.chip_id = chip_id
        self.color_name = db.select_where_from_table('chips', ['color_name'], {'chip_id': chip_id, 'game_id': game_id},
                                                     single_result=True)
        self.color: tuple = Colors.target[self.color_name]
        self.symbol = db.select_where_from_table('chips', ['symbol'], {'chip_id': chip_id, 'game_id': game_id},
                                                 single_result=True)
        self.position_grid_center = position_grid_center

    def draw(self, window, position, size) -> None:
        if self.symbol == 'circle':
            pygame.draw.circle(window, self.color,
                               (position['x'] + size['width'] // 2,
                                position['y'] + size['height'] // 2),
                               size['width'] // 4)
        elif self.symbol == 'square':
            pygame.draw.rect(window, self.color,
                             (position['x'] + size['width'] // 4,
                              position['y'] + size['height'] // 4,
                              size['width'] // 2, size['height'] // 2))
        elif self.symbol == 'triangle':
            pygame.draw.polygon(window, self.color,
                                ((position['x'] + size['width'] // 4,
                                  position['y'] + size['height'] - size['height'] // 4),
                                 (position['x'] + size['width'] // 2,
                                  position['y'] + size['height'] // 4),
                                 (position['x'] + size['width'] - size['width'] // 4,
                                  position['y'] + size['height'] - size['height'] // 4)))
        elif self.symbol == 'hexagon':
            pts = []
            for i in range(6):
                x = (position['x'] + size['width'] // 2) + (size['width'] // 4) * cos(pi * 2 * i / 6)
                y = (position['y'] + size['height'] // 2) + (size['height'] // 4) * sin(pi * 2 * i / 6)
                pts.append([int(x), int(y)])
            pygame.draw.polygon(window, self.color, pts)

        elif self.symbol == 'spiral':
            pygame.draw.line(window, self.color,
                             (position['x'], position['y']),
                             (position['x'] + size['width'], position['y'] + size['height']),
                             width=3)
            pygame.draw.line(window, self.color,
                             (position['x'] + size['width'], position['y']),
                             (position['x'], position['y'] + size['height']),
                             width=3)

    def draw_to_grid_center(self, window, size):
        self.draw(window, {'x': self.position_grid_center['x'] - size['width'] // 2,
                           'y': self.position_grid_center['y'] - size['height'] // 2}, size)
