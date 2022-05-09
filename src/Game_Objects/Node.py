import pygame

from .Object import Object
from .Target import Target

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class Node:
    neighbors: dict
    neighbors_with_wall: list
    target: Target

    def __init__(self, position: dict, size: dict):
        self.position = position
        self.size = size

        self.color = Colors.node['default']
        if (position['row'], position['column']) in [(7, 7), (7, 8), (8, 7), (8, 8)]:
            self.color = Colors.node['barrier']

        self.neighbors = dict()
        self.target = None
        self.robot = None

    def get_position(self) -> dict:
        return self.position

    def reset(self) -> None:
        self.color = Colors.node['default']

    def draw(self, window) -> None:
        pygame.draw.rect(window, self.color,
                         (self.position['x'], self.position['y'], self.size['width'], self.size['height']))

        if self.target:
            self.target.draw(window, self.position, self.size)

        self.draw_walls(window)

    def draw_walls(self, window) -> None:
        if not self.neighbors['top']:
            pygame.draw.line(window, Colors.wall,
                             (self.position['x'], self.position['y'] + 2),
                             (self.position['x'] + self.size['width'], self.position['y'] + 2),
                             width=3)
        if not self.neighbors['bottom']:
            pygame.draw.line(window, Colors.wall,
                             (self.position['x'], self.position['y'] + self.size['height'] - 2),
                             (self.position['x'] + self.size['width'], self.position['y'] + self.size['height'] - 2),
                             width=3)
        if not self.neighbors['left']:
            pygame.draw.line(window, Colors.wall,
                             (self.position['x'] + 2, self.position['y']),
                             (self.position['x'] + 2, self.position['y'] + self.size['height']),
                             width=3)
        if not self.neighbors['right']:
            pygame.draw.line(window, Colors.wall,
                             (self.position['x'] + self.size['width'] - 2, self.position['y']),
                             (self.position['x'] + self.size['width'] - 2, self.position['y'] + self.size['height']),
                             width=3)

    def set_neighbors(self, grid: list):
        total_rows = len(grid)
        total_columns = len(grid[0])

        if self.position['row'] < total_rows - 1:  # bottom
            self.neighbors['bottom'] = grid[self.position['row'] + 1][self.position['column']]
        else:
            self.neighbors['bottom'] = None

        if self.position['row'] > 0:  # top
            self.neighbors['top'] = grid[self.position['row'] - 1][self.position['column']]
        else:
            self.neighbors['top'] = None

        if self.position['column'] < total_columns - 1:  # RIGHT
            self.neighbors['right'] = grid[self.position['row']][self.position['column'] + 1]
        else:
            self.neighbors['right'] = None

        if self.position['column'] > 0:  # LEFT
            self.neighbors['left'] = grid[self.position['row']][self.position['column'] - 1]
        else:
            self.neighbors['left'] = None

    def set_wall(self, direction: str) -> None:
        self.neighbors[direction] = None

    def set_target(self, target) -> None:
        self.target = target
