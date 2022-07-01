from src.SQL import MySQL, PostgreSQL
import pygame

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class LeaderboardEntryDraw:
    def __init__(self, name, score, obtained_targets):
        self.name = name
        self.score = score
        self.obtained_targets_draw = obtained_targets

    def calc_size(self, field_size):
        if len(self.obtained_targets_draw) > 16:
            count_target_row = 5
        elif len(self.obtained_targets_draw) > 12:
            count_target_row = 4
        elif len(self.obtained_targets_draw) > 8:
            count_target_row = 3
        elif len(self.obtained_targets_draw) > 4:
            count_target_row = 2
        else:
            count_target_row = 1

        size = {'width': 4 * field_size, 'height': 1 * field_size + count_target_row * field_size}
        return size

    def draw(self, window, font, position: dict, field_size: int):
        offset = {
            'top': 0,
            'left': 0
        }

        size = self.calc_size(field_size)
        rect = pygame.Rect(position['x'], position['y'], size['width'], size['height'])
        pygame.draw.rect(window, Colors.leaderboard['background'], rect)
        pygame.draw.rect(window, Colors.leaderboard['border'], rect, width=2)

        # draw name + score
        pygame.draw.line(window, Colors.leaderboard['border'], (position['x'], position['y'] + field_size),
                         (position['x'] + size['width'], position['y'] + field_size))
        pygame.draw.line(window, Colors.leaderboard['border'], (position['x'] + 3 * field_size, position['y']),
                         (position['x'] + 3 * field_size, position['y'] + field_size))

        # render player name
        font_size_name = 26
        text_rect_name = font.get_rect(self.name, size=font_size_name)
        text_rect_name.center = (position['x'] + (size['width'] - field_size) // 2,
                                 position['y'] + field_size // 2)
        font.render_to(window, text_rect_name, self.name, (0, 0, 0), size=font_size_name)

        # render player score
        font_size_score = 26
        text_rect_score = font.get_rect(str(self.score), size=font_size_score)
        text_rect_score.center = (position['x'] + 3 * field_size + field_size // 2, position['y'] + field_size // 2)
        font.render_to(window, text_rect_score, str(self.score), (0, 0, 0), size=font_size_score)

        offset['top'] += 1

        # draw targets
        for target in self.obtained_targets_draw:
            target.r_draw(window, {'x': position['x'] + offset['left'] * field_size,
                                   'y': position['y'] + offset['top'] * field_size},
                          {'width': field_size, 'height': field_size})
            offset['left'] += 1
            if offset['left'] == 4:
                offset['left'] = 0
                offset['top'] += 1


class LeaderboardDraw:
    def __init__(self, position: dict, size: dict, field_size, entries: list):
        self.position: dict = position
        self.size: dict = size
        self.field_size = field_size
        self.entries: list = entries

    def set_entries(self, entries: list[LeaderboardEntryDraw]) -> None:
        self.entries = entries

    def draw(self, window, font):
        offset: dict = {
            'top': 0,
            'left': 0.5
        }

        rect = pygame.Rect(self.position['x'], self.position['y'], self.size['width'], self.size['height'])
        pygame.draw.rect(window, Colors.leaderboard['background'], rect)
        pygame.draw.rect(window, Colors.leaderboard['border'], rect, width=2)

        # draw header
        header = 'Leaderboard'
        font_size_header = 26
        text_rect_header = font.get_rect(header, size=font_size_header)
        text_rect_header.center = (
        self.position['x'] + self.size['width'] // 2, self.position['y'] + self.field_size // 2)
        font.render_to(window, text_rect_header, header, (0, 0, 0), size=font_size_header)

        offset['top'] += 1

        # draw entries
        for entry in self.entries:
            entry.draw(window, font, {'x': self.position['x'] + offset['left'] * self.field_size,
                                      'y': self.position['y'] + offset['top'] * self.field_size}, self.field_size)
            offset['top'] += entry.calc_size(self.field_size)['height'] / self.field_size + 0.5


class Leaderboard:
    def __init__(self, db: MySQL | PostgreSQL, game_id: int, position: dict, size: dict, field_size: int,
                 targets: list):
        self.db: MySQL | PostgreSQL = db
        self.game_id: int = game_id
        self.position: dict = position
        self.size: dict = size
        self.field_size = field_size
        self.targets: list = targets

    def get_all_player_ids_in_game(self):
        raw_query_player_ids = self.db.execute_query(f"SELECT player_id FROM players WHERE game_id={self.game_id}")
        if not raw_query_player_ids:
            return None
        return [int(player_id_tpl[0]) for player_id_tpl in raw_query_player_ids]

    def get_all_players_who_have_scored(self):
        unfiltered_player_ids = self.get_all_player_ids_in_game()
        if not unfiltered_player_ids:
            return

        final_player_ids = []

        for player_id in unfiltered_player_ids:
            player_score = int(self.db.execute_query(f"SELECT score FROM players WHERE player_id={player_id}")[0][0])
            if player_score != 0:
                final_player_ids.append(player_id)

        return final_player_ids

    def get_all_target_ids_which_the_player_has_obtained(self, player_id):
        target_ids = [target_id_tpl[0] for target_id_tpl in
                      self.db.execute_query(f"SELECT chip_id FROM chips WHERE obtained_by={player_id}")]
        return target_ids

    def create_obj_for_draw(self):
        entries: list = []
        scored_player_ids: list = self.get_all_players_who_have_scored()

        if scored_player_ids:
            for player_id in scored_player_ids:

                name, score = self.db.execute_query(f"SELECT name, score FROM players WHERE player_id={player_id}")[0]

                target_ids_obtained_by_player = self.get_all_target_ids_which_the_player_has_obtained(player_id)
                target_draw_objects: list = []
                for target in self.targets:
                    if target.chip_id in target_ids_obtained_by_player:
                        target_draw_objects.append(target.create_obj_for_draw())

                entries.append(LeaderboardEntryDraw(name, score, target_draw_objects))

        obj_leaderboard_draw = LeaderboardDraw(self.position, self.size, self.field_size, entries)
        return obj_leaderboard_draw
