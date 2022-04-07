import pygame

from .Node import Node

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class Robot:
    home_node: Node
    current_node: Node
    border: bool

    def __init__(self, grid, position: dict, size: dict, name: str):
        self.position = position
        self.size = size
        self.name = name
        self.color = self.get_color()

        self.home_node = grid[self.position['row']][self.position['column']]
        self.current_node = self.home_node

        self.current_node.robot = self

        self.border = False

    def get_color(self) -> tuple:
        if self.name.lower() == 'yellow':
            return Colors.yellow
        elif self.name.lower() == 'red':
            return Colors.red
        elif self.name.lower() == 'green':
            return Colors.green
        elif self.name.lower() == 'blue':
            return Colors.blue

    def move(self, direction: str) -> None:
        self.current_node.robot = None

        if direction == 'up':
            while self.current_node.neighbors['up'] and not self.current_node.neighbors['up'].is_robot():
                self.current_node = self.current_node.neighbors['up']
        elif direction == 'down':
            while self.current_node.neighbors['down'] and not self.current_node.neighbors['down'].is_robot():
                self.current_node = self.current_node.neighbors['down']
        elif direction == 'left':
            while self.current_node.neighbors['left'] and not self.current_node.neighbors['left'].is_robot():
                self.current_node = self.current_node.neighbors['left']
        elif direction == 'right':
            while self.current_node.neighbors['right'] and not self.current_node.neighbors['right'].is_robot():
                self.current_node = self.current_node.neighbors['right']

        self.current_node.robot = self

        self.position = self.current_node.get_position()

    def draw(self, window) -> None:
        pygame.draw.circle(window, self.color,
                           (
                               self.position['x'] + self.size['width'] // 2,
                               self.position['y'] + self.size['height'] // 2),
                           self.size['width'] // 2 - 3)
        if self.border:
            pygame.draw.circle(window, Colors.white,
                               (self.position['x'] + self.size['width'] // 2,
                                self.position['y'] + self.size['height'] // 2),
                               self.size['width'] // 2 - 3,
                               width=3)
