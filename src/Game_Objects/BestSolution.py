import pygame

from src.SQL import SQL

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

    def __init__(self, db, game_id, position: dict, size: dict):
        self.db: SQL = db
        self.game_id = game_id
        self.position = position
        self.size = size

    def create_obj_for_draw(self) -> BestSolutionDraw:
        all_player_ids_and_solutions_in_game: list = self.db.select_where_from_table('players',
                                                                                     ['player_id', 'solution'], {
                                                                                         'game_id': self.game_id})  # get all player in game
        all_player_ids_and_solutions_in_game = list(
            filter(lambda x: x[1] != -1, all_player_ids_and_solutions_in_game))  # filter out player without a solution
        all_player_ids_and_solutions_in_game.sort(key=lambda x: x[1])  # sort after solution
        if len(all_player_ids_and_solutions_in_game) != 0:
            best_player_id = all_player_ids_and_solutions_in_game[0][0]
            name, solution = \
            self.db.select_where_from_table('players', ['name', 'solution'], {'player_id': best_player_id})[0]
        else:
            solution = ''
            name = ''

        obj_best_solution_draw = BestSolutionDraw(self.position, self.size, solution, name)
        return obj_best_solution_draw
