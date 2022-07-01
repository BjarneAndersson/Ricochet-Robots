import pygame

from src.SQL import MySQL, PostgreSQL

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class BestSolutionDraw:
    def __init__(self, position, size, solution, player_name):
        self.position = position
        self.size = size
        self.solution = solution
        self.player_name = player_name

    def set_solution(self, solution: int) -> None:
        self.solution = solution

    def set_player_name(self, player_name: int) -> None:
        self.player_name = player_name

    def draw(self, window, font) -> None:
        pygame.draw.rect(window, Colors.individual_solution['fill'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']))
        pygame.draw.rect(window, Colors.individual_solution['border'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']), width=3)
        pygame.draw.line(window, Colors.individual_solution['border'],
                         (self.position['x'],
                          self.position['y'] + 2 * (self.size['height'] // 3) - 1),
                         (self.position['x'] + self.size['width'] - 1,
                          self.position['y'] + 2 * (self.size['height'] // 3) - 1),
                         width=1)

        # player solution
        font_size_solution = 64
        text_rect = font.get_rect(str(self.solution), size=font_size_solution)
        text_rect.center = (self.position['x'] + (self.size['width'] // 2),
                            self.position['y'] + 0.5 * 2 * (self.size['height'] // 3))
        font.render_to(window, text_rect, str(self.solution), (0, 0, 0), size=font_size_solution)

        # render player name
        font_size_name = 26
        text_rect_name = font.get_rect(self.player_name, size=font_size_name)
        text_rect_name.center = (self.position['x'] + (self.size['width'] // 2),
                                 self.position['y'] + 2 * (self.size['height'] // 3) + (self.size['height'] // 6))
        font.render_to(window, text_rect_name, self.player_name, (0, 0, 0), size=font_size_name)


class BestSolution:

    def __init__(self, db: MySQL | PostgreSQL, game_id, position: dict, size: dict):
        self.db: MySQL | PostgreSQL = db
        self.game_id = game_id
        self.position = position
        self.size = size

    def get_solution(self) -> int:
        result = self.db.execute_query(
            f"SELECT solution FROM players WHERE game_id={self.game_id} AND solution IS NOT NULL ORDER BY solution ASC, last_solution_change ASC LIMIT 1")
        return result[0][0] if result else ''

    def get_player_name(self) -> str:
        result = self.db.execute_query(
            f"SELECT name FROM players WHERE game_id={self.game_id} AND solution IS NOT NULL ORDER BY solution ASC, last_solution_change ASC LIMIT 1")
        return result[0][0] if result else ''

    def create_obj_for_draw(self) -> BestSolutionDraw:
        obj_best_solution_draw = BestSolutionDraw(self.position, self.size, self.get_solution(), self.get_player_name())
        return obj_best_solution_draw
