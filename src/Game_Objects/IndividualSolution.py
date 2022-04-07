import pygame

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class IndividualSolution:

    def __init__(self, position: dict, size: dict):
        self.position = position
        self.size = size

    def draw(self, window, network, user_id, font, is_input_field_active) -> None:
        pygame.draw.rect(window, Colors.grey,
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']))
        pygame.draw.rect(window, Colors.white,
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'] - 1, self.size['height'] - 1),
                         width=2)
        pygame.draw.line(window, Colors.white,
                         (self.position['x'],
                          self.position['y'] + 2 * (self.size['height'] // 3)),
                         (self.position['x'] + self.size['width'] - 1,
                          self.position['y'] + 2 * (self.size['height'] // 3)),
                         width=1)

        # player solution
        player_solution = int(network.send(f"GET user/{user_id}/solution"))
        if player_solution == -1 or is_input_field_active:
            pygame.draw.rect(window, Colors.grey,
                             (self.position['x'] + 2,
                              self.position['y'] + 2,
                              self.size['width'] - 4, self.size['height'] - (self.size['width'] // 3)))
        else:
            text_rect = font.get_rect(str(player_solution), size=64)
            text_rect.center = (self.position['x'] + 2 * (self.size['width'] // 4),
                                self.position['y'] + 0.75 * (self.size['width'] // 3))
            font.render_to(window, text_rect, str(player_solution), (0, 0, 0), size=64)

        # player name
        font.render_to(window, (self.position['x'] + (self.size['height'] // 4) * 0.5,
                                self.position['y'] + 2 * (self.size['height'] // 3) + (
                                        self.size['height'] // 3) * 0.25),
                       network.send(f"GET user/{user_id}/name"), (0, 0, 0), size=26)
