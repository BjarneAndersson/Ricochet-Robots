import pygame

from .Object import Object
from .Target import Target

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class NodeDraw:
    def __init__(self, color, position, size, neighbors):
        self.color: tuple = color
        self.position: dict = position
        self.size: dict = size
        self.neighbors = neighbors

    def draw(self, window) -> None:
        pygame.draw.rect(window, self.color,
                         (self.position['x'], self.position['y'], self.size['width'], self.size['height']))

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
        self.is_robot: bool = False

    def get_position(self) -> dict:
        return self.position

    def get_size(self) -> dict:
        return self.size

    def reset(self) -> None:
        self.color = Colors.node['default']

    def set_neighbors(self, grid: list) -> None:
        total_rows = 16
        total_columns = 16

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

    def create_obj_for_draw(self) -> NodeDraw:
        # conv_neighbors_to_bool_based  |  {'up': <Node>, 'down': None} -> {'up': True, 'down': False}
        bool_based_neighbors = self.neighbors.copy()
        for k, v in self.neighbors.items():
            if v is None:
                bool_based_neighbors[k] = False
            else:
                bool_based_neighbors[k] = True

        obj_node_draw = NodeDraw(self.color, self.position, self.size, bool_based_neighbors)
        return obj_node_draw
