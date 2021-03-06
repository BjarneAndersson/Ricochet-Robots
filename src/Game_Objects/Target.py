from math import cos
from math import pi
from math import sin
from src.Helpers import Colors
from src.SQL import MySQL, PostgreSQL
import pygame


class TargetDraw:
    def __init__(self, color: tuple, color_name: str, symbol: str, position: dict, position_grid_center: dict,
                 size: dict,
                 is_revealed: bool):
        self.color = color
        self.color_name = color_name
        self.symbol = symbol
        self.position = position
        self.position_grid_center = position_grid_center
        self.size = size
        self.is_revealed = is_revealed

    def set_revealed(self, state: bool) -> None:
        self.is_revealed = state

    def r_draw(self, window, position, size):
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
            star_points: tuple = ((position['x'] + size['width'] // 2, position['y'] + size['height'] // 10),  # top
                                  (position['x'] + size['width'] // 2 + size['width'] // 10,
                                   position['y'] + size['height'] // 2 - size['height'] // 10),  #
                                  (position['x'] + size['width'] - size['width'] // 10,
                                   position['y'] + size['height'] // 2),  # right
                                  (position['x'] + size['width'] // 2 + size['width'] // 10,
                                   position['y'] + size['height'] // 2 + size['height'] // 10),  #
                                  (position['x'] + size['width'] // 2,
                                   position['y'] + size['height'] - size['height'] // 10),  # bottom
                                  (position['x'] + size['width'] // 2 - size['width'] // 10,
                                   position['y'] + size['height'] // 2 + size['height'] // 10),  #
                                  (position['x'] + size['width'] // 10, position['y'] + size['height'] // 2),  # left
                                  (position['x'] + size['width'] // 2 - size['width'] // 10,
                                   position['y'] + size['height'] // 2 - size['height'] // 10))
            pygame.draw.polygon(window, self.color, star_points)

    def draw(self, window) -> None:
        self.r_draw(window, self.position, self.size)

        if self.is_revealed:
            size_for_draw_center = self.size.copy()
            size_for_draw_center['width'] *= 2
            size_for_draw_center['height'] *= 2
            self.draw_to_grid_center(window, size_for_draw_center)

    def draw_to_grid_center(self, window, size):
        self.r_draw(window, {'x': self.position_grid_center['x'] - size['width'] // 2,
                             'y': self.position_grid_center['y'] - size['height'] // 2}, size)


class Target:
    def __init__(self, db: MySQL | PostgreSQL, game_id: int, chip_id: int, node, position_grid_center: dict):
        self.db: MySQL | PostgreSQL = db
        self.chip_id = chip_id
        self.color_name, self.symbol = \
            self.db.execute_query(f"SELECT color_name, symbol FROM chips WHERE chip_id={self.chip_id}")[0]
        self.color: tuple = Colors.target[self.color_name]
        self.node = node
        self.position = self.node.get_position()
        self.size = node.get_size()
        self.position_grid_center = position_grid_center

    def create_obj_for_draw(self):
        is_revealed = bool(self.db.execute_query(f"SELECT revealed FROM chips WHERE chip_id={self.chip_id}")[0][0])

        obj_target_draw = TargetDraw(self.color, self.color_name, self.symbol, self.position, self.position_grid_center,
                                     self.size,
                                     is_revealed)
        return obj_target_draw
