import random
from datetime import datetime

import pygame.freetype

from Game_Objects import Board
from Game_Objects import Hourglass
from Game_Objects import IndividualSolution
from Game_Objects import Menu
from Game_Objects import MenuButton
from Game_Objects import Robot
from Game_Objects import TargetChip
from SQL import SQL


class Game:
    ROWS: int = 16
    COLUMNS: int = 16
    QUBE_SIZE: int = 50  # pixels

    def __init__(self, db, game_id):
        self.db: SQL = db
        self.game_id: int = game_id
        self.round_id: int = self.db.get_next_id('rounds')

        self.robots = []
        self.ready: bool = False

        width_menu_hourglass: int = 1 * self.QUBE_SIZE
        width_leaderboard: int = 4 * self.QUBE_SIZE
        height_start_input: int = 3 * self.QUBE_SIZE

        self.board_offset: dict = {'top': self.QUBE_SIZE // 2,
                                   'bottom': self.QUBE_SIZE // 2 + height_start_input + self.QUBE_SIZE // 2,
                                   'left': self.QUBE_SIZE // 2 + width_menu_hourglass + self.QUBE_SIZE // 2,
                                   'right': self.QUBE_SIZE // 2 + width_leaderboard + self.QUBE_SIZE // 2}

        # object initialisation
        self.board: Board = Board(self.db, self.game_id,
                                  {'x': self.board_offset['left'], 'y': self.board_offset['top']}, self.FIELD_SIZE)

        menu_button = MenuButton({'x': self.QUBE_SIZE // 2, 'y': self.QUBE_SIZE // 2},
                                 {'width': self.QUBE_SIZE, 'height': self.QUBE_SIZE})
        self.menu = Menu({'x': self.board.position['x'], 'y': self.board.position['y']},
                         {'width': self.QUBE_SIZE, 'height': self.QUBE_SIZE}, menu_button)
        self.hourglass = Hourglass({'x': self.QUBE_SIZE // 2,
                                    'y': self.QUBE_SIZE // 2 + self.menu.button.size[
                                        'height'] + 3 * self.QUBE_SIZE},
                                   {'width': self.QUBE_SIZE, 'height': 12 * self.QUBE_SIZE})
        self.individual_solution = IndividualSolution(
            {'x': self.QUBE_SIZE // 2, 'y': self.board_offset['top'] + self.board.size['height'] + self.QUBE_SIZE // 2},
            {'width': 4 * self.QUBE_SIZE, 'height': 3 * self.QUBE_SIZE})
        self.make_robots()

        # window initialisation
        self.window_dimensions = (
            self.board_offset['left'] + self.board.rect.width + self.board_offset['right'],
            self.board_offset['top'] + self.board.rect.height + self.board_offset['bottom'])

        self.active_player_id: int = None

        self.control_move_count: int = 0

    def make_robots(self) -> None:
        used_positions: list = [{'row': 7, 'column': 7}, {'row': 7, 'column': 8}, {'row': 8, 'column': 7},
                                {'row': 8, 'column': 8}]
        for color_name in ['red', 'green', 'blue', 'yellow']:
            current_position = {'row': random.randint(0, self.ROWS - 1), 'column': random.randint(0, self.COLUMNS - 1)}

            while current_position in used_positions:
                current_position = {'row': random.randint(0, self.ROWS - 1),
                                    'column': random.randint(0, self.COLUMNS - 1)}

            used_positions.append(current_position)

            self.db.insert('robots',
                           {'game_id': self.game_id, 'color': color_name, 'position_column': current_position['column'],
                            'position_row': current_position['row']})

    def get_is_ready(self) -> bool:
        return self.ready

    def control_move_count_gt_player_solution(self):
        self.selected_robot.border = False
        self.selected_robot.current_node.robot = None
        self.selected_robot.current_node = self.selected_robot.home_node
        self.selected_robot.current_node.robot = self.selected_robot
        self.selected_robot.position_window = self.selected_robot.current_node.get_position_window()
        self.selected_robot = None

        if len(self.players_guessed) >= 2:
            self.players_guessed.pop(0)
            self.active_player = self.get_best_player_in_round()

            self.control_move_count = 0
        else:
            print('No one found a valid solution!\nSkipping target chip!')

    def start_round(self):
        self.round_id = self.db.get_next_id('rounds')
        self.db.insert_round(str(self.game_id), self.selected_chip)

        for player in self.players:
            player.solution = -1

    def get_best_player_id(self) -> int:  # solution >= 0 => valid | solution < 0 => invalid
        best_player_id = self.db.select_where_from_table('player_id', 'players', 'solution',
                                                         '(SELECT MIN(solution) FROM players)', 'last_solution_change',
                                                         '(SELECT MIN(last_change) FROM players)', 'game_id',
                                                         self.game_id)

        return best_player_id

    def finish_round(self):
        self.selected_chip.is_revealed = False

        # get all player_ids that are in the game
        all_user_ids = self.db.select_where_from_table('player_id', 'players', 'game_id', self.game_id)
        print(all_user_ids)

        duration: int = self.db.select_where_from_table('started_at', 'rounds', 'round_id',
                                                        self.round_id) - datetime.timestamp(datetime.now())

        best_player_id: int = self.get_best_player_id()
        best_solution: int = self.db.select_where_from_table('solution', 'players', 'player_id', best_player_id)

        self.db.update_round(self.round_id, duration, best_solution, best_player_id)

        if best_solution >= 0:

            best_player.target_chips.append(self.selected_chip)
            self.target_chips.remove(self.selected_chip)

            self.selected_robot.border = False
            for robot in self.robots:
                robot.home_node = robot.current_node
        else:
            pass

        self.hourglass.current_time = 0
        self.control_move_count = 0
        self.selected_robot = None
        self.selected_chip = None
        self.active_player = None

        print('\nLeaderboard:')
        for player in self.players:
            print(f"Player: {player.name} | Score: {len(player.target_chips)}")
        print('')
