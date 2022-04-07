import pygame

from .Node import Node
from .TargetSpace import TargetSpace
from .Wall import Wall

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class QuarterBoard:
    color: tuple
    field_size: int

    target_spaces: list
    walls: list

    def __init__(self, color: tuple, field_size: int):
        self.color = color
        self.field_size = field_size

        self.target_spaces = []
        self.walls = []


class QuarterBoardYellow(QuarterBoard):

    def __init__(self, field_size: int):
        super().__init__(Colors.board_yellow, field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target spaces
        self.target_spaces.append(
            TargetSpace({'row': 1, 'column': 6}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_blue, 'circle'))
        self.target_spaces.append(
            TargetSpace({'row': 3, 'column': 1}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_yellow,
                        'triangle'))
        self.target_spaces.append(
            TargetSpace({'row': 4, 'column': 5}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_green,
                        'square'))
        self.target_spaces.append(
            TargetSpace({'row': 5, 'column': 2}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_red, 'hexagon'))
        self.target_spaces.append(
            TargetSpace({'row': 5, 'column': 7}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_all, 'spiral'))

        # walls
        # middle barrier
        self.walls.append(
            Wall({'row': 6, 'column': 7}, {'row': 7, 'column': 7}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 7, 'column': 6}, {'row': 7, 'column': 7}, {'node1': 'right', 'node2': 'left'}))
        # blue circle
        self.walls.append(
            Wall({'row': 1, 'column': 6}, {'row': 1, 'column': 5}, {'node1': 'left', 'node2': 'right'}))
        self.walls.append(
            Wall({'row': 1, 'column': 6}, {'row': 2, 'column': 6}, {'node1': 'bottom', 'node2': 'top'}))
        # yellow triangle
        self.walls.append(
            Wall({'row': 3, 'column': 1}, {'row': 2, 'column': 1}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 3, 'column': 1}, {'row': 3, 'column': 2}, {'node1': 'right', 'node2': 'left'}))
        # green square
        self.walls.append(
            Wall({'row': 4, 'column': 5}, {'row': 4, 'column': 4}, {'node1': 'left', 'node2': 'right'}))
        self.walls.append(
            Wall({'row': 4, 'column': 5}, {'row': 3, 'column': 5}, {'node1': 'top', 'node2': 'bottom'}))
        # red hexagon
        self.walls.append(
            Wall({'row': 5, 'column': 2}, {'row': 6, 'column': 2}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 5, 'column': 2}, {'row': 5, 'column': 3}, {'node1': 'right', 'node2': 'left'}))
        # all spiral
        self.walls.append(
            Wall({'row': 5, 'column': 7}, {'row': 6, 'column': 7}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 5, 'column': 7}, {'row': 5, 'column': 8}, {'node1': 'right', 'node2': 'left'}))
        # single walls
        self.walls.append(
            Wall({'row': 0, 'column': 3}, {'row': 0, 'column': 4}, {'node1': 'right', 'node2': 'left'}))
        self.walls.append(
            Wall({'row': 6, 'column': 0}, {'row': 7, 'column': 0}, {'node1': 'bottom', 'node2': 'top'}))


class QuarterBoardRed(QuarterBoard):

    def __init__(self, field_size: int):
        super().__init__(Colors.board_red, field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        self.target_spaces.append(
            TargetSpace({'row': 1, 'column': 14}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_red, 'triangle'))
        self.target_spaces.append(
            TargetSpace({'row': 2, 'column': 11}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_blue, 'hexagon'))
        self.target_spaces.append(
            TargetSpace({'row': 6, 'column': 13}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_green, 'circle'))
        self.target_spaces.append(
            TargetSpace({'row': 7, 'column': 10}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_yellow, 'square'))

        # walls
        # middle barrier
        self.walls.append(
            Wall({'row': 7, 'column': 8}, {'row': 6, 'column': 8}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 7, 'column': 8}, {'row': 7, 'column': 9}, {'node1': 'right', 'node2': 'left'}))
        # red triangle
        self.walls.append(
            Wall({'row': 1, 'column': 14}, {'row': 0, 'column': 14}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 1, 'column': 14}, {'row': 1, 'column': 13}, {'node1': 'left', 'node2': 'right'}))
        # blue hexagon
        self.walls.append(
            Wall({'row': 2, 'column': 11}, {'row': 3, 'column': 11}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 2, 'column': 11}, {'row': 2, 'column': 10}, {'node1': 'left', 'node2': 'right'}))
        # green circle
        self.walls.append(
            Wall({'row': 6, 'column': 13}, {'row': 7, 'column': 13}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 6, 'column': 13}, {'row': 6, 'column': 14}, {'node1': 'right', 'node2': 'left'}))
        # yellow square
        self.walls.append(
            Wall({'row': 7, 'column': 10}, {'row': 6, 'column': 10}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 7, 'column': 10}, {'row': 7, 'column': 11}, {'node1': 'right', 'node2': 'left'}))
        # single walls
        self.walls.append(
            Wall({'row': 0, 'column': 9}, {'row': 0, 'column': 10}, {'node1': 'right', 'node2': 'left'}))
        self.walls.append(
            Wall({'row': 3, 'column': 15}, {'row': 4, 'column': 15}, {'node1': 'bottom', 'node2': 'top'}))


class QuarterBoardGreen(QuarterBoard):

    def __init__(self, field_size: int):
        super().__init__(Colors.board_green, field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        self.target_spaces.append(
            TargetSpace({'row': 9, 'column': 3}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_yellow, 'hexagon'))
        self.target_spaces.append(
            TargetSpace({'row': 11, 'column': 1}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_red, 'circle'))
        self.target_spaces.append(
            TargetSpace({'row': 12, 'column': 6}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_blue, 'square'))
        self.target_spaces.append(
            TargetSpace({'row': 14, 'column': 2}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_green, 'triangle'))

        # walls
        # middle barrier
        self.walls.append(
            Wall({'row': 8, 'column': 7}, {'row': 9, 'column': 7}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 8, 'column': 7}, {'row': 8, 'column': 6}, {'node1': 'left', 'node2': 'right'}))
        # yellow hexagon
        self.walls.append(
            Wall({'row': 9, 'column': 3}, {'row': 8, 'column': 3}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 9, 'column': 3}, {'row': 9, 'column': 4}, {'node1': 'left', 'node2': 'right'}))
        # red circle
        self.walls.append(
            Wall({'row': 11, 'column': 1}, {'row': 12, 'column': 1}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 11, 'column': 1}, {'row': 11, 'column': 0}, {'node1': 'left', 'node2': 'right'}))
        # blue square
        self.walls.append(
            Wall({'row': 12, 'column': 6}, {'row': 13, 'column': 6}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 12, 'column': 6}, {'row': 12, 'column': 7}, {'node1': 'right', 'node2': 'left'}))
        # green triangle
        self.walls.append(
            Wall({'row': 14, 'column': 2}, {'row': 13, 'column': 2}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 14, 'column': 2}, {'row': 14, 'column': 1}, {'node1': 'left', 'node2': 'right'}))
        # single walls
        self.walls.append(
            Wall({'row': 13, 'column': 0}, {'row': 14, 'column': 0}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 15, 'column': 5}, {'row': 15, 'column': 6}, {'node1': 'right', 'node2': 'left'}))


class QuarterBoardBlue(QuarterBoard):

    def __init__(self, field_size: int):
        super().__init__(Colors.board_blue, field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        self.target_spaces.append(
            TargetSpace({'row': 9, 'column': 13}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_blue, 'triangle'))
        self.target_spaces.append(
            TargetSpace({'row': 11, 'column': 9}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_yellow, 'circle'))
        self.target_spaces.append(
            TargetSpace({'row': 13, 'column': 14}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_red, 'square'))
        self.target_spaces.append(
            TargetSpace({'row': 14, 'column': 10}, {'width': self.field_size, 'height': self.field_size},
                        Colors.target_space_green, 'hexagon'))

        # walls
        # middle barrier
        self.walls.append(
            Wall({'row': 8, 'column': 8}, {'row': 9, 'column': 8}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 8, 'column': 8}, {'row': 8, 'column': 9}, {'node1': 'right', 'node2': 'left'}))
        # blue triangle
        self.walls.append(
            Wall({'row': 9, 'column': 13}, {'row': 10, 'column': 13}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 9, 'column': 13}, {'row': 9, 'column': 12}, {'node1': 'left', 'node2': 'right'}))
        # yellow circle
        self.walls.append(
            Wall({'row': 11, 'column': 9}, {'row': 12, 'column': 9}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 11, 'column': 9}, {'row': 11, 'column': 10}, {'node1': 'right', 'node2': 'left'}))
        # red square
        self.walls.append(
            Wall({'row': 13, 'column': 14}, {'row': 12, 'column': 14}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 13, 'column': 14}, {'row': 13, 'column': 15}, {'node1': 'right', 'node2': 'left'}))
        # green hexagon
        self.walls.append(
            Wall({'row': 14, 'column': 10}, {'row': 13, 'column': 10}, {'node1': 'top', 'node2': 'bottom'}))
        self.walls.append(
            Wall({'row': 14, 'column': 10}, {'row': 14, 'column': 9}, {'node1': 'left', 'node2': 'right'}))
        # single walls
        self.walls.append(
            Wall({'row': 11, 'column': 15}, {'row': 12, 'column': 15}, {'node1': 'bottom', 'node2': 'top'}))
        self.walls.append(
            Wall({'row': 15, 'column': 11}, {'row': 15, 'column': 12}, {'node1': 'right', 'node2': 'left'}))


class Board:
    field_size: int

    board: dict

    def __init__(self, total_rows, total_columns, position, qube_size):
        self.grid = None
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.field_size = qube_size

        self.board = dict()
        self.position: dict = position
        self.size = {'width': self.total_rows * self.field_size, 'height': self.total_columns * self.field_size}
        self.rect = pygame.rect.Rect(self.position['x'], self.position['y'], self.size['width'], self.size['height'])

        self.create_board()
        self.create_grid()

    def create_grid(self) -> list:
        self.grid = [[Node(
            {'row': count_row, 'column': count_column,
             'x': self.position['x'] + count_column * self.field_size,
             'y': self.position['y'] + count_row * self.field_size},
            {'width': self.field_size, 'height': self.field_size})
            for count_column in range(self.total_columns)]
            for count_row in range(self.total_rows)]

        for row in self.grid:
            for node in row:
                node.set_neighbors(self.grid)

        self.add_walls_to_grid()
        self.add_target_spaces_to_grid()
        return self.grid

    def add_walls_to_grid(self) -> None:
        for quarter_board in self.board.values():
            for wall in quarter_board.walls:
                self.grid[wall.position_node1['row']][wall.position_node1['column']].set_wall(wall.direction_node1)
                self.grid[wall.position_node2['row']][wall.position_node2['column']].set_wall(wall.direction_node2)

    def add_target_spaces_to_grid(self) -> None:
        for quarter_board in self.board.values():
            for target_space in quarter_board.target_spaces:
                self.grid[target_space.position['row']][target_space.position['column']].set_target_space(target_space)

    def create_board(self) -> dict:
        self.board = {'yellow': QuarterBoardYellow(self.field_size),
                      'red': QuarterBoardRed(self.field_size),
                      'green': QuarterBoardGreen(self.field_size),
                      'blue': QuarterBoardBlue(self.field_size)}
        return self.board

    def get_node(self, position: dict) -> Node:
        x, y = position['x'], position['y']
        x -= self.position['x']
        y -= self.position['y']

        row = y // self.field_size
        column = x // self.field_size

        return self.grid[row][column]
