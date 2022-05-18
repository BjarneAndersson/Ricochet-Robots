import random
from datetime import datetime

import pygame.freetype

from Game_Objects import Board
from Game_Objects import Hourglass
from Game_Objects import IndividualSolution
from Game_Objects import Menu
from Game_Objects import MenuButton
from Game_Objects import ReadyButton
from Game_Objects import BestSolution
from Game_Objects import Robot

from SQL import SQL


class Game:
    ROWS: int = 16
    COLUMNS: int = 16
    FIELD_SIZE: int = 50  # pixels

    def __init__(self, db, game_id):
        self.db: SQL = db
        self.game_id: int = game_id
        self.round_id: int
        self.round_number: int = 0

        self.robots = []
        self.ready: bool = False
        self.is_round_active: bool = False
        self.player_count_ready_for_round = 0

        width_menu_hourglass: int = 1 * self.FIELD_SIZE
        width_leaderboard: int = 4 * self.FIELD_SIZE
        height_start_input: int = 3 * self.FIELD_SIZE

        self.board_offset: dict = {'top': self.FIELD_SIZE // 2,
                                   'bottom': self.FIELD_SIZE // 2 + height_start_input + self.FIELD_SIZE // 2,
                                   'left': self.FIELD_SIZE // 2 + width_menu_hourglass + self.FIELD_SIZE // 2,
                                   'right': self.FIELD_SIZE // 2 + width_leaderboard + self.FIELD_SIZE // 2}

        # object initialisation
        self.board: Board = Board(self.db, self.game_id,
                                  {'x': self.board_offset['left'], 'y': self.board_offset['top']}, self.FIELD_SIZE)

        menu_button = MenuButton({'x': self.FIELD_SIZE // 2, 'y': self.FIELD_SIZE // 2},
                                 {'width': self.FIELD_SIZE, 'height': self.FIELD_SIZE})

        self.menu = Menu({'x': self.board.position['x'], 'y': self.board.position['y']},
                         {'width': self.FIELD_SIZE, 'height': self.FIELD_SIZE}, menu_button)

        self.hourglass = Hourglass({'x': self.FIELD_SIZE // 2,
                                    'y': self.FIELD_SIZE // 2 + self.menu.button.size[
                                        'height'] + 3 * self.FIELD_SIZE},
                                   {'width': self.FIELD_SIZE, 'height': 12 * self.FIELD_SIZE})

        self.individual_solution = {'position': {'x': self.FIELD_SIZE, 'y': self.board_offset['top'] + self.board.size[
            'height'] + self.FIELD_SIZE // 2},
                                    'size': {'width': 5 * self.FIELD_SIZE, 'height': height_start_input}}
        self.ready_button = {
            'position': {
                'x': self.board_offset['left'] + self.individual_solution['size']['width'] + self.FIELD_SIZE // 2,
                'y': self.board_offset['top'] + self.board.size['height'] + self.FIELD_SIZE // 2},
            'size': {'width': 5 * self.FIELD_SIZE, 'height': height_start_input}}

        self.best_solution = BestSolution(self.db, self.game_id,
                                          {'x': self.FIELD_SIZE // 2 + self.hourglass.size[
                                              'width'] + self.FIELD_SIZE // 2 + self.individual_solution['size'][
                                                    'width'] + self.FIELD_SIZE // 2 + self.ready_button['size'][
                                                    'width'] + self.FIELD_SIZE // 2,
                                           'y': self.board_offset['top'] + self.board.size[
                                               'height'] + self.FIELD_SIZE // 2},
                                          self.individual_solution['size'])

        self.create_robots()

        # window initialisation
        self.window_dimensions = (
            self.board_offset['left'] + self.board.rect.width + self.board_offset['right'],
            self.board_offset['top'] + self.board.rect.height + self.board_offset['bottom'])

        self.active_player_id: int = None
        self.active_player_solution: int = None

        self.control_move_count: int = 0
        self.selected_robot: Robot = None

        self.game_tick_rate = 30
        self.last_creation_of_draw_objects: datetime = datetime.now()

        self.grid_draw = None
        self.robots_draw = None
        self.targets_draw = None
        self.hourglass_draw = None
        self.best_solution_draw = None


    def create_robots(self) -> None:
        used_positions: list = [{'row': 7, 'column': 7}, {'row': 7, 'column': 8}, {'row': 8, 'column': 7},
                                {'row': 8, 'column': 8}]
        for color_name in ['red', 'green', 'blue', 'yellow']:
            current_position = {'row': random.randint(0, self.ROWS - 1), 'column': random.randint(0, self.COLUMNS - 1)}

            while current_position in used_positions:
                current_position = {'row': random.randint(0, self.ROWS - 1),
                                    'column': random.randint(0, self.COLUMNS - 1)}

            used_positions.append(current_position)

            self.db.insert('robots',
                           {'game_id': self.game_id, 'color_name': color_name,
                            'home_position_column': current_position['column'],
                            'home_position_row': current_position['row'],
                            'position_column': current_position['column'], 'position_row': current_position['row']})

            robot_id = self.db.select_where_from_table('robots', ['robot_id'],
                                                       {'game_id': self.game_id, 'color_name': color_name,
                                                        'position_column': current_position['column'],
                                                        'position_row': current_position['row']}, single_result=True)

            robot_position = self.db.select_where_from_table('robots', ['position_column', 'position_row'],
                                                             {'game_id': self.game_id, 'robot_id': robot_id})[0]
            robot_position = {'column': robot_position[0], 'row': robot_position[1]}

            self.robots.append(
                Robot(self.db, self.game_id, robot_id, self.FIELD_SIZE,
                      self.board.grid[robot_position['row']][robot_position['column']]))

    def get_is_ready(self) -> bool:
        return self.ready

    def get_is_round_ready(self) -> bool:
        return self.player_count_ready_for_round >= self.db.select_where_from_table('games', ['player_count'],
                                                                                    {'game_id': self.game_id},
                                                                                    single_result=True) // 2

    def get_new_round_number(self):
        self.round_number += 1
        return self.round_number

    def choose_rand_chip(self) -> int:  # return chip_id
        all_available_chip_ids = [chip_id_tpl[0] for chip_id_tpl in
                                  self.db.select_where_from_table('chips', ['chip_id'], {'game_id': self.game_id,
                                                                                         'obtained_by_player_id': 0})]
        return random.choice(all_available_chip_ids)

    def reset_all_player_solutions(self) -> None:
        self.db.update_where_from_table('players', {'solution': -1}, {'game_id': self.game_id})

    def check_if_new_draw_objects_should_be_created(self) -> bool:
        current_datetime = datetime.now()
        dif = current_datetime - self.last_creation_of_draw_objects
        dif_micro = dif.seconds * 10 ** 6 + dif.microseconds
        if dif_micro >= 10 ** 6 / 30:
            self.last_creation_of_draw_objects = datetime.now()
            self.create_new_draw_objects()
            return True
        return False

    def create_new_draw_objects(self):
        self.grid_draw = [[node.create_obj_for_draw() for node in row] for row in self.board.grid]
        self.robots_draw = [robot.create_obj_for_draw() for robot in self.robots]
        self.targets_draw = [target.create_obj_for_draw() for target in self.board.targets]
        self.hourglass_draw = self.hourglass.create_obj_for_draw()
        self.best_solution_draw = self.best_solution.create_obj_for_draw()

    def set_global_ready_button_state(self, state_pressed):
        self.db.update_where_from_table('players', {'ready_for_round': int(state_pressed)}, {'game_id': self.game_id})

    def start_round(self):
        self.is_round_active = True
        self.db.insert('rounds', {'game_id': self.game_id, 'round_number': self.get_new_round_number(),
                                  'chip_id': self.choose_rand_chip()})
        self.round_id = self.db.select_where_from_table('rounds', ['round_id'],
                                                        {'game_id': self.game_id, 'round_number': self.round_number},
                                                        single_result=True)

        self.reset_all_player_solutions()

        chip_id = self.db.select_where_from_table('rounds', ['chip_id'], {'round_id': self.round_id},
                                                  single_result=True)
        self.db.update_where_from_table('chips', {'revealed': 1}, {'chip_id': chip_id})

        self.set_global_ready_button_state(True)

    def solutions_review(self):
        self.active_player_id = self.get_best_player_id_in_round()

        if not self.active_player_id:
            print('No one found a valid solution!\nSkipping target chip!')
            self.finish_round()
        else:
            self.active_player_solution = self.db.select_where_from_table('players', ['solution'],
                                                                          {'player_id': self.active_player_id},
                                                                          single_result=True)
            self.control_move_count = 0

    def check_robot_on_target(self):
        active_chip_id = self.db.select_where_from_table('chips', ['chip_id'], {'game_id': self.game_id, 'revealed': 1},
                                                         single_result=True)
        active_chip_position_raw = \
        self.db.select_where_from_table('chips', ['position_column', 'position_row'], {'chip_id': active_chip_id})[0]
        active_chip_position = {'column': active_chip_position_raw[0], 'row': active_chip_position_raw[1]}
        active_robot_position = self.selected_robot.get_position()

        if active_chip_position == active_robot_position:
            return True
        return False

    def get_best_player_id_in_round(self) -> int:
        all_player_ids_and_solutions_in_game: list = self.db.select_where_from_table('players',
                                                                                     ['player_id', 'solution'], {
                                                                                         'game_id': self.game_id})  # get all player in game
        if all_player_ids_and_solutions_in_game:
            all_player_ids_and_solutions_in_game = list(
                filter(lambda x: x[1] != -1,
                       all_player_ids_and_solutions_in_game))  # filter out player without a solution
            all_player_ids_and_solutions_in_game.sort(key=lambda x: x[1])  # sort after solution
            if len(all_player_ids_and_solutions_in_game) != 0:
                best_player_id = all_player_ids_and_solutions_in_game[0][0]
                return best_player_id
        return None

    def pass_active_status_on_to_next_player_in_solution_list(self):
        self.db.update_where_from_table('players', {'solution': -1}, {'player_id': self.active_player_id})
        self.solutions_review()

    def finish_round(self):
        self.is_round_active = False

        chip_id = self.db.select_where_from_table('rounds', ['chip_id'], {'round_id': self.round_id},
                                                  single_result=True)

        if self.active_player_id:  # if solution was found
            self.db.update_where_from_table('chips', {'revealed': 0, 'obtained_by_player_id': self.active_player_id},
                                            {'chip_id': chip_id})

            # update db for player score
            player_old_score = int(
                self.db.select_where_from_table('players', ['score'], {'player_id': self.active_player_id},
                                                single_result=True))
            self.db.update_where_from_table('players', {'score': player_old_score + 1},
                                            {'player_id': self.active_player_id})

            # set robot home
            for robot in self.robots:
                robot_position = robot.get_position()
                self.db.update_where_from_table('robots', {'home_position_column': robot_position['column'],
                                                           'home_position_row': robot_position['row']},
                                                {'robot_id': robot.robot_id})

            # update db for round
            self.db.update_where_from_table('rounds', {'best_solution': self.active_player_solution,
                                                       'best_player_id': self.active_player_id},
                                            {'round_id': self.round_id})
        else:
            self.db.update_where_from_table('chips', {'revealed': 0}, {'chip_id': chip_id})

        # move robots to home
        for robot in self.robots:
            robot_home_position = \
            self.db.select_where_from_table('robots', ['home_position_column', 'home_position_row'],
                                            {'robot_id': robot.robot_id})[0]
            self.db.update_where_from_table('robots', {'home_position_column': robot_home_position[0],
                                                       'home_position_row': robot_home_position[1]},
                                            {'robot_id': robot.robot_id})

        round_started_at: datetime = self.db.select_where_from_table('rounds', ['started_at'],
                                                                     {'round_id': self.round_id}, single_result=True)
        duration = datetime.now() - round_started_at
        duration = duration.seconds
        self.db.update_where_from_table('rounds', {'duration': duration}, {'round_id': self.round_id})

        self.active_player_id = None
        self.active_player_solution = None

        if self.selected_robot:
            self.db.update_where_from_table('robots', {'in_use': 0}, {'robot_id': self.selected_robot.robot_id})
            self.selected_robot = None

        self.hourglass.reset()

        self.reset_all_player_solutions()
        self.set_global_ready_button_state(False)
        self.player_count_ready_for_round = 0
