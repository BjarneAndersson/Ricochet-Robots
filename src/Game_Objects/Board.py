import pygame

from .Node import Node
from .Target import Target
from .Wall import Wall

from src.SQL import MySQL, PostgreSQL

try:
    from src.Helpers import Colors, Converters
except ModuleNotFoundError:
    from Helpers import Colors

db: MySQL | PostgreSQL
game_id: int


class QuarterBoard:
    color: tuple
    field_size: int

    walls: list

    def __init__(self, color: tuple, field_size: int):
        self.color = color
        self.field_size = field_size

        self.walls = []


class QuarterBoardYellow(QuarterBoard):

    def __init__(self, field_size: int):
        super().__init__(Colors.board['yellow'], field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target spaces
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'blue','circle','(6,1)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'yellow','triangle','(1,3)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'green','square','(5,4)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'red','hexagon','(2,5)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'all','spiral','(7,5)') RETURNING chip_id;")

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
        super().__init__(Colors.board['red'], field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'red','triangle','(14,1)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'blue','hexagon','(11,2)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'green','circle','(13,6)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'yellow','square','(10,7)') RETURNING chip_id;")

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
        super().__init__(Colors.board['green'], field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'yellow','hexagon','(3,9)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'red','circle','(1,11)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'blue','square','(6,12)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'green','triangle','(2,14)') RETURNING chip_id;")

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
            Wall({'row': 9, 'column': 3}, {'row': 9, 'column': 4}, {'node1': 'right', 'node2': 'left'}))
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
        super().__init__(Colors.board['blue'], field_size)

        self.create_quarter_board()

    def create_quarter_board(self):
        # target chips
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'blue','triangle','(13,9)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'yellow','circle','(9,11)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'red','square','(14,13)') RETURNING chip_id;")
        db.execute_query(
            f"INSERT INTO chips (game_id, color_name, symbol, position) VALUES ({game_id},'green','hexagon','(10,14)') RETURNING chip_id;")

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

    def __init__(self, _db, _game_id, position, field_size):
        global db, game_id
        db = _db
        game_id = _game_id

        self.grid = None
        self.total_rows = 16
        self.total_columns = 16
        self.field_size = field_size

        self.board = dict()
        self.position: dict = position
        self.size = {'width': self.total_rows * self.field_size, 'height': self.total_columns * self.field_size}
        self.rect = pygame.rect.Rect(self.position['x'], self.position['y'], self.size['width'], self.size['height'])

        self.targets = []

        self.create_board()
        self.create_grid()

    def create_board(self) -> dict:
        self.board = {'yellow': QuarterBoardYellow(self.field_size),
                      'red': QuarterBoardRed(self.field_size),
                      'green': QuarterBoardGreen(self.field_size),
                      'blue': QuarterBoardBlue(self.field_size)}
        return self.board

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
        self.create_targets()
        return self.grid

    def add_walls_to_grid(self) -> None:
        for quarter_board in self.board.values():
            for wall in quarter_board.walls:
                self.grid[wall.position_node1['row']][wall.position_node1['column']].set_wall(wall.direction_node1)
                self.grid[wall.position_node2['row']][wall.position_node2['column']].set_wall(wall.direction_node2)

    def create_targets(self) -> None:
        chip_ids = db.execute_query(f"SELECT chip_id FROM chips WHERE game_id={game_id}")
        chip_ids = [chip_id[0] for chip_id in chip_ids]
        for chip_id in chip_ids:
            target_position = Converters.db_position_to_position(
                db.execute_query(f"SELECT position FROM chips WHERE chip_id={chip_id}")[0][0])
            node = self.grid[target_position['row']][target_position['column']]
            self.targets.append(Target(db, game_id, chip_id, node, self.get_position_grid_center()))

    def get_node(self, position: dict) -> Node:
        x, y = position['x'], position['y']
        x -= self.position['x']
        y -= self.position['y']

        row = y // self.field_size
        column = x // self.field_size

        return self.grid[row][column]

    def get_position_grid_center(self) -> dict:
        return {'x': self.rect.centerx, 'y': self.rect.centery}
