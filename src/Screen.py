from src.Game_Objects import Menu
from src.Game_Objects import IndividualSolution
from src.Game_Objects import ReadyButton

from src.Game_Objects.BestSolution import BestSolutionDraw
from src.Game_Objects.Hourglass import HourglassDraw
from src.Game_Objects.Leaderboard import LeaderboardDraw
from src.Game_Objects.Node import NodeDraw
from src.Game_Objects.Robot import RobotDraw
from src.Game_Objects.Target import TargetDraw

from Network import Network

import pygame


class Screen:

    def __init__(self, network: Network, player_id: int) -> None:
        self.network: Network = network
        self.player_id: int = player_id
        self.player_name: str = network.send(f"GET user/{player_id}/name")

        self.font = pygame.freetype.SysFont('Comic Sans MS', 0)
        self.colors = network.send('GET colors')

        # initialize window
        self.window = pygame.display.set_mode(network.send("GET game/window_dimensions"))
        pygame.display.set_caption("Ricochet Robots")

        self.menu = Menu(network.send("GET game/menu/position"),
                         network.send("GET game/menu/button"),
                         self.font, network, player_id)

        self.individual_solution = IndividualSolution(network.send("GET game/individual_solution/position"),
                                                      network.send("GET game/individual_solution/size"), self.font,
                                                      network,
                                                      self.player_id, self.player_name)
        self.ready_button = ReadyButton(network.send("GET game/ready_button/position"),
                                        network.send("GET game/ready_button/size"))
        self.ready_button.set_state(network.send("GET game/ready_button/state"))

        self.frame_rate = network.send("GET others/server_tick_rate")

        self.board_offset = self.network.send("GET game/board/offset")
        self.field_size = self.network.send("GET game/field_size")

        self.grid = self.network.send("GET game/board/grid")

        self.targets: list[TargetDraw] = self.network.send("GET game/targets")
        self.active_target: TargetDraw = None

        self.robots: list[RobotDraw] = self.network.send("GET game/robots")

        self.hourglass: HourglassDraw = self.network.send("GET game/hourglass")

        self.best_solution: BestSolutionDraw = self.network.send("GET game/best_solution")

        self.leaderboard: LeaderboardDraw = self.network.send("GET game/leaderboard")

    def get_active_target(self) -> TargetDraw:
        active_target_specifications = self.network.send("GET game/targets/active")

        if active_target_specifications:
            for target in self.targets:
                if target.symbol == active_target_specifications['symbol'] and \
                        target.color_name == active_target_specifications['color']:
                    return target
        else:
            return None

    def set_active_robot(self) -> None:
        active_robot_color = self.network.send("GET game/robots/active")

        for robot in self.robots:
            robot.active = False

        if active_robot_color:
            for robot in self.robots:
                robot.active = robot.color_name == active_robot_color

    def draw_grid(self) -> None:

        for i in range(16 + 1):
            pygame.draw.line(self.window, self.colors.wall,
                             (0 + self.board_offset['left'], i * self.field_size + self.board_offset['top']),
                             (16 * self.field_size + self.board_offset['left'],
                              i * self.field_size + self.board_offset['top']))
            for j in range(16 + 1):
                pygame.draw.line(self.window, self.colors.wall,
                                 (i * self.field_size + self.board_offset['left'], 0 + self.board_offset['top']),
                                 (i * self.field_size + self.board_offset['left'],
                                  16 * self.field_size + self.board_offset['top']))

    def draw(self) -> None:
        self.window.fill(self.colors.background)

        for row in self.grid:
            for node in row:
                node.draw(self.window)

        self.draw_grid()

        self.active_target = self.get_active_target()
        if not self.active_target:
            for target in self.targets:
                target.set_revealed(False)
                target.draw(self.window)
            self.individual_solution.clear()
        else:  # single target
            self.active_target.set_revealed(True)
            self.active_target.draw(self.window)

        self.set_active_robot()
        robot_positions: dict = self.network.send("GET game/robots/positions")
        for robot_color_name, robot_position in robot_positions.items():
            robot = [robot for robot in self.robots if robot.color_name == robot_color_name][0]
            robot.set_position(robot_position)
            robot.draw(self.window)

        self.hourglass.set_percentage_of_fill(float(self.network.send("GET game/hourglass/percentage_of_fill")))
        self.hourglass.draw(self.window)

        self.menu.draw(self.window, self.font)

        self.individual_solution.set_player_name(self.menu.menu_entries['change_name'].input_field.get_player_name())
        self.individual_solution.draw(self.window)

        self.ready_button.set_state(self.network.send(f"GET user/{self.player_id}/ready_button/state"))  # update state
        self.ready_button.draw(self.window)

        best_solution_update = self.network.send("GET game/best_solution/update")
        self.best_solution.set_solution(best_solution_update['solution'])
        self.best_solution.set_player_name(best_solution_update['player_name'])
        self.best_solution.draw(self.window, self.font)

        self.leaderboard.set_entries(self.network.send("GET game/leaderboard/entries"))
        self.leaderboard.draw(self.window, self.font)

        pygame.display.update()
