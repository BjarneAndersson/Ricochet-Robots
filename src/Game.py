import random
from datetime import datetime

from Game_Objects import Board
from Game_Objects import Hourglass
from Game_Objects import Leaderboard
from Game_Objects import Menu
from Game_Objects import MenuButton
from Game_Objects import BestSolution
from Game_Objects import Robot

from SQL import SQL


class Game:
    ROWS: int = 16
    COLUMNS: int = 16
    FIELD_SIZE: int = 50  # pixels

    def __init__(self, db: SQL, game_id: int):
        self.db: SQL = db
        self.game_id: int = game_id
        self.round_id: int = None
        self.ready: bool = False

        # window initialisation
        self.board_offset: dict = {'top': self.FIELD_SIZE // 2,
                                   'bottom': self.FIELD_SIZE // 2 + 3 * self.FIELD_SIZE + self.FIELD_SIZE // 2,
                                   'left': self.FIELD_SIZE // 2 + 1 * self.FIELD_SIZE + self.FIELD_SIZE // 2,
                                   'right': self.FIELD_SIZE // 2 + 5 * self.FIELD_SIZE + self.FIELD_SIZE // 2}

        # initialisation of server game objects
        self.board: Board = None
        self.hourglass: Hourglass = None
        self.best_solution: BestSolution = None
        self.leaderboard: Leaderboard = None
        self.initialize_game_objects_server()
        self.robots: list = self.create_robots()

        # declare position and size of client game objects
        self.menu: dict = None
        self.individual_solution: dict = None
        self.ready_button: dict = None
        self.initialize_game_objects_client()

        self.window_dimensions = (
            self.board_offset['left'] + self.board.rect.width + self.board_offset['right'],
            self.board_offset['top'] + self.board.rect.height + self.board_offset['bottom'])


        # variables needed for rounds
        self.is_round_active: bool = False
        self.round_number: int = 0
        self.active_player_id: int = None
        self.active_player_solution: int = None

        self.overall_player_count: int = 0

        self.control_move_count: int = 0
        self.selected_robot: Robot = None

        self.game_tick_rate = 30
        self.last_creation_of_draw_objects: datetime = datetime.now()

        self.grid_draw = None
        self.robots_draw = None
        self.targets_draw = None
        self.hourglass_draw = None
        self.leaderboard_draw = None
        self.best_solution_draw = None

    def initialize_game_objects_server(self):
        self.board: Board = Board(self.db, self.game_id,
                                  {'x': self.board_offset['left'], 'y': self.board_offset['top']}, self.FIELD_SIZE)

        self.hourglass = Hourglass({'x': self.FIELD_SIZE // 2,
                                    'y': self.FIELD_SIZE // 2 + 1 * self.FIELD_SIZE + 3 * self.FIELD_SIZE},
                                   {'width': self.FIELD_SIZE, 'height': 12 * self.FIELD_SIZE})

        self.leaderboard = Leaderboard(self.db, self.game_id, {
            'x': self.board_offset['left'] + self.board.size['width'] + self.FIELD_SIZE // 2,
            'y': self.board_offset['top']}, {'width': 5 * self.FIELD_SIZE, 'height': 16 * self.FIELD_SIZE},
                                       self.FIELD_SIZE, self.board.targets)

        self.best_solution = BestSolution(self.db, self.game_id,
                                          {'x': self.FIELD_SIZE // 2 + self.hourglass.size[
                                              'width'] + self.FIELD_SIZE // 2 + 5 * self.FIELD_SIZE + self.FIELD_SIZE // 2 + 5 * self.FIELD_SIZE + self.FIELD_SIZE // 2,
                                           'y': self.board_offset['top'] + self.board.size[
                                               'height'] + self.FIELD_SIZE // 2},
                                          {'width': 5 * self.FIELD_SIZE, 'height': 3 * self.FIELD_SIZE})

    def initialize_game_objects_client(self):
        menu_button = {
            'position': {'x': self.FIELD_SIZE // 2, 'y': self.FIELD_SIZE // 2},
            'size': {'width': self.FIELD_SIZE, 'height': self.FIELD_SIZE}
        }
        self.menu = {
            'position': {'x': self.board.position['x'], 'y': self.board.position['y']},
            'size': {'width': 4 * self.FIELD_SIZE, 'height': 4 * self.FIELD_SIZE},
            'button': menu_button
        }
        self.individual_solution = {
            'position': {'x': self.board_offset['left'], 'y': self.board_offset['top'] + self.board.size[
                'height'] + self.FIELD_SIZE // 2},
            'size': {'width': 5 * self.FIELD_SIZE, 'height': 3 * self.FIELD_SIZE}}
        self.ready_button = {
            'position': {
                'x': self.board_offset['left'] + self.individual_solution['size']['width'] + self.FIELD_SIZE // 2,
                'y': self.board_offset['top'] + self.board.size['height'] + self.FIELD_SIZE // 2},
            'size': {'width': 5 * self.FIELD_SIZE, 'height': 3 * self.FIELD_SIZE}}

    def create_robots(self) -> list:
        robots: list = []
        used_positions: list = [{'row': 7, 'column': 7}, {'row': 7, 'column': 8}, {'row': 8, 'column': 7},
                                {'row': 8, 'column': 8}]

        for color_name in ['red', 'green', 'blue', 'yellow']:
            # find an open random position
            robot_position = {'row': random.randint(0, self.ROWS - 1), 'column': random.randint(0, self.COLUMNS - 1)}
            while robot_position in used_positions:
                robot_position = {'row': random.randint(0, self.ROWS - 1),
                                  'column': random.randint(0, self.COLUMNS - 1)}
            used_positions.append(robot_position)

            # insert robot data into db
            self.db.insert('robots',
                           {'game_id': self.game_id, 'color_name': color_name,
                            'position': f"({robot_position['column']}, {robot_position['row']})",
                            'home_position': f"({robot_position['column']}, {robot_position['row']})"})

            # create robot object
            robot_id = self.db.execute_query(
                f"SELECT robot_id FROM robots WHERE game_id={self.game_id} AND color_name={color_name}")[0][0]
            robots.append(
                Robot(self.db, self.game_id, robot_id, self.FIELD_SIZE,
                      self.board.grid[robot_position['row']][robot_position['column']]))
        return robots

    # ------------------------------------------------------------------------------------------------------------------

    def get_is_ready(self) -> bool:
        return self.ready

    # ------------------------------------------------------------------------------------------------------------------

    def check_if_new_draw_objects_should_be_created(self) -> bool:
        current_datetime = datetime.now()
        dif = current_datetime - self.last_creation_of_draw_objects
        dif_micro = dif.seconds * 10 ** 6 + dif.microseconds
        if dif_micro >= 10 ** 6 / self.game_tick_rate:
            self.last_creation_of_draw_objects = datetime.now()
            self.create_new_draw_objects()
            return True
        return False

    def create_new_draw_objects(self) -> None:
        self.grid_draw = [[node.create_obj_for_draw() for node in row] for row in self.board.grid]
        self.robots_draw = [robot.create_obj_for_draw() for robot in self.robots]
        self.targets_draw = [target.create_obj_for_draw() for target in self.board.targets]
        self.hourglass_draw = self.hourglass.create_obj_for_draw()
        self.leaderboard_draw = self.leaderboard.create_obj_for_draw()
        self.best_solution_draw = self.best_solution.create_obj_for_draw()

    # ------------------------------------------------------------------------------------------------------------------

    def select_robot(self, robot):
        self.selected_robot = robot
        self.selected_robot.in_use = True

    def unselect_robot(self):
        if self.selected_robot:
            self.selected_robot.in_use = False
        self.selected_robot = None

    def get_is_round_ready(self) -> bool:
        player_count_ready_for_round_raw = self.db.execute_query(
            f"SELECT player_id FROM players WHERE game_id={self.game_id} AND ready_for_round=1")
        if not player_count_ready_for_round_raw:
            return False
        player_count_ready_for_round = len([player_id_tpl[0] for player_id_tpl in player_count_ready_for_round_raw])
        return self.ready and player_count_ready_for_round >= \
               self.db.execute_query(f"SELECT player_count FROM games WHERE game_id={self.game_id}")[0][0] // 2

    def get_new_round_number(self) -> int:
        self.round_number += 1
        return self.round_number

    def are_chips_without_solution(self) -> bool:
        all_available_chip_ids_raw = self.db.execute_query(
            f"SELECT chip_id FROM chips WHERE game_id={self.game_id} AND obtained_by IS NULL")
        return bool(all_available_chip_ids_raw)

    def choose_rand_chip(self) -> int:  # return chip_id
        if not self.are_chips_without_solution():
            return None

        all_available_chip_ids_raw = self.db.execute_query(
            f"SELECT chip_id FROM chips WHERE game_id={self.game_id} AND obtained_by IS NULL")
        all_available_chip_ids = [chip_id_tpl[0] for chip_id_tpl in all_available_chip_ids_raw]
        return random.choice(all_available_chip_ids)

    def reset_all_player_solutions(self) -> None:
        self.db.execute_query(f"UPDATE players SET solution=Null WHERE game_id={self.game_id}")

    def set_global_ready_button_state(self, state_pressed):
        self.db.execute_query(f"UPDATE players SET ready_for_round={bool(state_pressed)} WHERE game_id={self.game_id}")

    def start_round(self):
        self.is_round_active = True

        # insert round
        self.db.insert('rounds', {'game_id': self.game_id, 'round_number': self.get_new_round_number(),
                                  'chip_id': self.choose_rand_chip()})

        self.round_id = self.db.execute_query(
            f"SELECT round_id FROM rounds WHERE game_id={self.game_id} AND round_number={self.round_number}")[0][0]

        chip_id = self.db.execute_query(f"SELECT chip_id FROM rounds WHERE round_id={self.round_id}")[0][0]
        # update db - reveal chip
        self.db.execute_query(f"UPDATE chips SET revealed=True WHERE chip_id={chip_id}")

        self.set_global_ready_button_state(True)

    def check_robot_on_target(self):
        if self.selected_robot:
            active_chip_id, chip_color_name = \
                self.db.execute_query(
                    f"SELECT chip_id, color_name FROM chips WHERE game_id={self.game_id} AND revealed=True")[0]
            active_chip_position_raw = \
                self.db.execute_query(
                    f"SELECT position FROM chips WHERE chip_id={active_chip_id}")[0]
            active_chip_position = {'column': active_chip_position_raw[0], 'row': active_chip_position_raw[1]}

            robot_color_name = self.db.execute_query(
                f"SELECT color_name FROM robots WHERE robot_id={self.selected_robot.robot_id}")[0][0]
            active_robot_position = self.selected_robot.get_position()

            if active_chip_position == active_robot_position and chip_color_name == robot_color_name:
                return True
        return False

    def get_best_player_id_in_round(self) -> int:
        all_player_ids_and_solutions_in_game: list = self.db.execute_query(
            f"SELECT player_id, solution FROM players WHERE game_id={self.game_id}")  # get all player in game
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
        self.db.execute_query(f"UPDATE players SET solution=Null WHERE player_id={self.active_player_id}")
        self.active_player_id = None
        if self.selected_robot:
            self.unselect_robot()

        # move robots to home
        for robot in self.robots:
            robot_home_position = \
            self.db.execute_query(f"SELECT home_position FROM robots WHERE robot_id={robot.robot_id}")[0][0].split(",")
            robot.set_position({'column': int(robot_home_position[0]), 'row': int(robot_home_position[1])},
                               self.board.grid,
                               is_home=False)

    def finish_round(self):
        self.is_round_active = False
        chip_id = self.db.execute_query(f"SELECT chip_id FROM rounds WHERE round_id={self.round_id}")[0][0]

        if self.active_player_id:  # if solution was found
            self.db.execute_query(
                f"UPDATE chips SET revealed=False AND obtained_by={self.active_player_id} WHERE chip_id={chip_id}")

            # update db - player score
            player_old_score = int(
                self.db.execute_query(f"SELECT score FROM players WHERE player_id={self.active_player_id}")[0][0])
            self.db.execute_query(
                f"UPDATE players SET score={player_old_score + 1} WHERE player_id={self.active_player_id}")

            # set robot home
            for robot in self.robots:
                robot.set_position(robot.get_position(), self.board.grid, is_home=True)

            # update db for round
            self.db.execute_query(
                f"UPDATE rounds SET solution={player_old_score + 1} AND winner={self.active_player_id} WHERE round_id={self.round_id}")
        else:
            self.db.execute_query(
                f"UPDATE chips SET revealed=False WHERE chip_id={chip_id}")

        # move robots to home
        for robot in self.robots:
            robot_home_position = \
            self.db.execute_query(f"SELECT home_position FROM robots WHERE robot_id={robot.robot_id}")[0].split(",")
            robot.set_position({'column': int(robot_home_position[0]), 'row': int(robot_home_position[1])},
                               self.board.grid)

        round_started_at: datetime = \
        self.db.execute_query(f"SELECT started_at FROM rounds WHERE round_id={self.round_id}")[0][0]
        duration = datetime.now() - round_started_at
        duration = duration.seconds
        self.db.execute_query(f"UPDATE rounds SET duration={duration} WHERE round_id={self.round_id}")

        self.active_player_id = None
        self.active_player_solution = None

        if self.selected_robot:
            self.unselect_robot()

        self.hourglass.reset()

        self.reset_all_player_solutions()
        self.set_global_ready_button_state(False)
        self.control_move_count = 0

        if not self.choose_rand_chip():
            self.finish_game()

    def get_best_player_id_in_game(self) -> int:
        all_player_ids_and_scores_in_game: list = self.db.execute_query(
            f"SELECT player_id, score FROM players WHERE game_id={self.game_id}")  # get all player in game

        all_player_ids_and_scores_in_game = list(
            filter(lambda x: x[1] != -1,
                   all_player_ids_and_scores_in_game))  # filter out player with a score of 0
        all_player_ids_and_scores_in_game.sort(key=lambda x: x[1], reverse=True)  # sort after scores
        best_player_id = all_player_ids_and_scores_in_game[0][0]
        return best_player_id
