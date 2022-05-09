from math import cos
from math import pi
from math import sin
from src.Helpers import Colors
from src.SQL import SQL
import pygame


class TargetSpace:
    def __init__(self, db: SQL, game_id: int, chip_id: int):
        self.position = {
            'column': db.select_where_from_table('chips', ['position_column'], {'chip_id': chip_id, 'game_id': game_id},
                                                 single_result=True),
            'row': db.select_where_from_table('chips', ['position_row'], {'chip_id': chip_id, 'game_id': game_id},
                                              single_result=True)}
        self.size = {'width': 50, 'height': 50}
        self.color: tuple = Colors.target_space[
            db.select_where_from_table('chips', ['color'], {'chip_id': chip_id, 'game_id': game_id},
                                       single_result=True)]
        self.symbol = db.select_where_from_table('chips', ['symbol'], {'chip_id': chip_id, 'game_id': game_id},
                                                 single_result=True)

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
