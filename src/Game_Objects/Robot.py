import pygame

from .Node import Node
from src.SQL import SQL

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class Robot:
    def __init__(self, db, game_id, robot_id, field_size, current_node):
        self.db: SQL = db
        self.game_id = game_id
        self.robot_id = robot_id
        self.field_size = field_size
        self.current_node = current_node
        self.current_node.is_robot = True

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

        self.db.update_where_from_table('robots', {'position_column': self.current_node.get_position()['column']},
                                        {'robot_id': self.robot_id})
        self.db.update_where_from_table('robots', {'position_row': self.current_node.get_position()['row']},
                                        {'robot_id': self.robot_id})

        if old_node == self.current_node:
            return False
        return True

    def get_position(self) -> dict:
        column, row = \
            self.db.select_where_from_table('robots', ['position_column', 'position_row'], {'robot_id': self.robot_id})[
                0]
        return {'column': int(column), 'row': int(row)}

    def set_position(self, _position: dict, grid, is_home=False) -> None:
        key_column = 'position_column'
        key_row = 'position_row'

        if is_home:
            key_column = 'home_' + key_column
            key_row = 'home_' + key_row

        self.db.update_where_from_table('robots', {key_column: _position['column'],
                                                   key_row: _position['row']},
                                        {'robot_id': self.robot_id})

        self.current_node = grid[_position['row']][_position['column']]

    def create_obj_for_draw(self):
        color = Colors.robot[self.db.select_where_from_table('robots', ['color_name'],
                                                             {'game_id': self.game_id, 'robot_id': self.robot_id},
                                                             single_result=True)]
        position = self.current_node.get_position()
        is_in_use = bool(
            self.db.select_where_from_table('robots', ['in_use'], {'game_id': self.game_id, 'robot_id': self.robot_id},
                                            single_result=True))
        obj_robot_draw = RobotDraw(color, position, {'width': self.field_size, 'height': self.field_size}, is_in_use)
        return obj_robot_draw


class RobotDraw:
    def __init__(self, color, position, size, active):
        self.color: tuple = color
        self.position: dict = position
        self.size: dict = size
        self.active: bool = active

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
