import pygame

from .Node import Node
from src.SQL import MySQL, PostgreSQL

try:
    from src.Helpers import Colors, Converters
except ModuleNotFoundError:
    from Helpers import Colors


class Robot:
    def __init__(self, db: MySQL | PostgreSQL, game_id, robot_id, field_size, current_node):
        self.db: MySQL | PostgreSQL = db
        self.game_id = game_id
        self.robot_id = robot_id
        self.field_size = field_size
        self.color_name = db.execute_query(f"SELECT color_name FROM robots WHERE robot_id={robot_id}")[0][0]
        self.current_node = current_node
        self.current_node.is_robot = True
        self.in_use: bool = False

    def move(self, direction: str) -> bool:  # return True if the robot moved
        old_node = self.current_node
        if direction == 'up':
            while self.current_node.neighbors['top'] and not self.current_node.neighbors['top'].is_robot:
                self.current_node = self.current_node.neighbors['top']
        elif direction == 'down':
            while self.current_node.neighbors['bottom'] and not self.current_node.neighbors['bottom'].is_robot:
                self.current_node = self.current_node.neighbors['bottom']
        elif direction == 'left':
            while self.current_node.neighbors['left'] and not self.current_node.neighbors['left'].is_robot:
                self.current_node = self.current_node.neighbors['left']
        elif direction == 'right':
            while self.current_node.neighbors['right'] and not self.current_node.neighbors['right'].is_robot:
                self.current_node = self.current_node.neighbors['right']

        old_node.is_robot = False
        self.current_node.is_robot = True

        self.db.execute_query(
            f"UPDATE robots SET position='({self.current_node.get_position()['column']},{self.current_node.get_position()['row']})' WHERE robot_id={self.robot_id}")

        if old_node == self.current_node:
            return False
        return True

    def get_position(self) -> dict:
        position = Converters.db_position_to_position(
            self.db.execute_query(f"SELECT position FROM robots WHERE robot_id={self.robot_id}")[
                0][0])
        position['x'] = self.current_node.get_position()['x']
        position['y'] = self.current_node.get_position()['y']
        return position

    def set_position(self, _position: dict, grid, is_home=False) -> None:

        if not is_home:
            key = "position"
        else:
            key = "home_position"

        self.db.execute_query(
            f"UPDATE robots SET {key}='({_position['column']},{_position['row']})' WHERE robot_id={self.robot_id}")

        self.current_node = grid[_position['row']][_position['column']]

    def create_obj_for_draw(self):
        color = Colors.robot[self.db.execute_query(
            f"SELECT color_name FROM robots WHERE game_id={self.game_id} AND robot_id={self.robot_id}")[0][0]]
        position = self.current_node.get_position()
        obj_robot_draw = RobotDraw(color, self.color_name, position,
                                   {'width': self.field_size, 'height': self.field_size}, self.in_use)
        return obj_robot_draw


class RobotDraw:
    def __init__(self, color, color_name, position, size, active):
        self.color: tuple = color
        self.color_name: str = color_name
        self.position: dict = position
        self.size: dict = size
        self.active: bool = active

    def set_position(self, position: dict) -> None:
        self.position = position

    def draw(self, window) -> None:
        pygame.draw.circle(window, self.color,
                           (
                               self.position['x'] + self.size['width'] // 2,
                               self.position['y'] + self.size['height'] // 2),
                           self.size['width'] // 2 - 3)
        if self.active:
            pygame.draw.circle(window, Colors.white,
                               (self.position['x'] + self.size['width'] // 2,
                                self.position['y'] + self.size['height'] // 2),
                               self.size['width'] // 2 - 3,
                               width=3)
